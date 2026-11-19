//! Robinhood Chain I/O: the Pons V2 curve ABI (from its bytecode and real transactions, Nov 18:
//! buy(uint256 quoteIn, uint256 minTokensOut, address recipient) payable with value = quoteIn exactly;
//! sell(uint256 tokensIn, uint256 minQuoteOut, address recipient) after the token's approve(curve);
//! quoteReserve() / tokenReserve() / realQuoteReserve() / graduated()), JSON-RPC over HTTP, EIP-1559 signing.
use crate::engine::Trade;
use alloy_consensus::{SignableTransaction, TxEip1559, TxEnvelope};
use alloy_eips::eip2718::Encodable2718;
use alloy_primitives::{keccak256, Address, Bytes, TxKind, U256};
use alloy_signer::SignerSync;
use alloy_signer_local::PrivateKeySigner;
use serde_json::{json, Value};
use std::str::FromStr;

pub fn topic(sig: &str) -> String { format!("0x{}", hex(&keccak256(sig.as_bytes()).0)) }
pub fn selector(sig: &str) -> String { hex(&keccak256(sig.as_bytes()).0[..4]) }
pub fn hex(b: &[u8]) -> String { b.iter().map(|x| format!("{x:02x}")).collect() }
pub fn topic_buy() -> String { topic("CurveBuy(address,address,uint256,uint256,uint256,uint256)") }
pub fn topic_sell() -> String { topic("CurveSell(address,address,uint256,uint256,uint256,uint256)") }
fn word_u(x: u128) -> String { format!("{x:064x}") }
fn word_a(a: &str) -> String { format!("{:0>64}", a.trim_start_matches("0x").to_lowercase()) }
pub fn wei(eth: f64) -> u128 { (eth.max(0.0) * 1e18) as u128 }
pub fn tok_units(t: f64) -> u128 { (t.max(0.0) * 1e18) as u128 }

pub fn buy_data(quote_wei: u128, min_tokens: u128, to: &str) -> String { format!("0x{}{}{}{}", selector("buy(uint256,uint256,address)"), word_u(quote_wei), word_u(min_tokens), word_a(to)) }
pub fn sell_data(tokens: u128, min_quote: u128, to: &str) -> String { format!("0x{}{}{}{}", selector("sell(uint256,uint256,address)"), word_u(tokens), word_u(min_quote), word_a(to)) }
pub fn allowance_data(owner: &str, spender: &str) -> String { format!("0x{}{}{}", selector("allowance(address,address)"), word_a(owner), word_a(spender)) }
pub fn approve_data(spender: &str) -> String { format!("0x{}{}{}", selector("approve(address,uint256)"), word_a(spender), "f".repeat(64)) }

fn words(data: &str) -> Vec<u128> {
    let d = data.trim_start_matches("0x");
    (0..d.len() / 64).map(|i| u128::from_str_radix(&d[64 * i + 32..64 * (i + 1)], 16).unwrap_or(u128::MAX)).collect()
}
/// A CurveBuy / CurveSell log (as eth_getLogs, eth_subscribe and receipts give it) -> Trade.
pub fn decode_trade(log: &Value, t_ms: u64) -> Option<Trade> {
    let t: Vec<&str> = log["topics"].as_array()?.iter().filter_map(|x| x.as_str()).collect();
    if t.len() < 3 { return None }
    let buy = if t[0] == topic_buy() { true } else if t[0] == topic_sell() { false } else { return None };
    let w = words(log["data"].as_str()?); if w.len() < 2 { return None }
    let user = format!("0x{}", &t[if buy { 2 } else { 1 }][26..]).to_lowercase();
    // data: (quoteIn, tokensOut, fee, tax) for a buy, (tokensIn, quoteOut, fee, tax) for a sale; the fee and the tax come
    // out of the quote, so the curve's reserve moves by quoteIn - fee - tax, or quoteOut + fee + tax (measured Nov 18)
    let (fee, tax) = (w.get(2).copied().unwrap_or(0), w.get(3).copied().unwrap_or(0));
    let (quote, tokens) = if buy { (w[0], w[1]) } else { (w[1], w[0]) };
    let net_q = if buy { quote.saturating_sub(fee).saturating_sub(tax) } else { quote.saturating_add(fee).saturating_add(tax) };
    Some(Trade { curve: log["address"].as_str()?.to_lowercase(), buy, user, quote: quote as f64 / 1e18, net_q: net_q as f64 / 1e18, tokens: tokens as f64 / 1e18,
        block: u64::from_str_radix(log["blockNumber"].as_str().unwrap_or("0x0").trim_start_matches("0x"), 16).unwrap_or(0), t_ms })
}

pub struct Rpc { pub url: String, pub send_urls: Vec<String>, http: reqwest::Client }
impl Rpc {
    pub fn new(url: &str, send_urls: &[String]) -> Self {
        let mut s: Vec<String> = send_urls.to_vec(); if s.is_empty() { s.push(url.to_string()) }
        Rpc { url: url.to_string(), send_urls: s, http: reqwest::Client::builder().timeout(std::time::Duration::from_secs(15)).build().expect("http client") }
    }
    pub async fn call_at(&self, url: &str, method: &str, params: Value) -> Result<Value, String> {
        for i in 0..6 {
            let r = self.http.post(url).json(&json!({"jsonrpc": "2.0", "id": 1, "method": method, "params": params})).send().await;
            match r {
                Ok(r) => {
                    let v: Value = r.json().await.map_err(|e| e.to_string())?;
                    if let Some(e) = v.get("error") {
                        if e["code"].as_i64() == Some(429) { tokio::time::sleep(std::time::Duration::from_millis(300 * (i + 1))).await; continue }
                        return Err(format!("{method}: {e}"));
                    }
                    return Ok(v["result"].clone());
                }
                Err(e) => { if i == 5 { return Err(format!("{method}: {e}")) } tokio::time::sleep(std::time::Duration::from_millis(300 * (i + 1))).await }
            }
        }
        Err(format!("{method}: rate-limited"))
    }
    pub async fn call(&self, method: &str, params: Value) -> Result<Value, String> { self.call_at(&self.url, method, params).await }
    async fn view_u(&self, to: &str, sig: &str, at: &str) -> Result<u128, String> {
        let r = self.call("eth_call", json!([{"to": to, "data": format!("0x{}", selector(sig))}, at])).await?;
        let s = r.as_str().unwrap_or("0x0").trim_start_matches("0x"); let s = if s.len() > 32 { &s[s.len() - 32..] } else { s };
        u128::from_str_radix(if s.is_empty() { "0" } else { s }, 16).map_err(|e| e.to_string())
    }
    /// (virtual quote reserve ETH, virtual token reserve, real quote ETH)
    pub async fn reserves(&self, curve: &str) -> Result<(f64, f64, f64), String> { self.reserves_at(curve, None).await }
    /// the same at the end of `block` (None = latest)
    pub async fn reserves_at(&self, curve: &str, block: Option<u64>) -> Result<(f64, f64, f64), String> {
        let at = block.map_or("latest".to_string(), |b| format!("0x{b:x}"));
        let (q, t, r) = tokio::join!(self.view_u(curve, "quoteReserve()", &at), self.view_u(curve, "tokenReserve()", &at), self.view_u(curve, "realQuoteReserve()", &at));
        Ok((q? as f64 / 1e18, t? as f64 / 1e18, r? as f64 / 1e18))
    }
    pub async fn token_of(&self, curve: &str) -> Result<String, String> {
        let r = self.call("eth_call", json!([{"to": curve, "data": format!("0x{}", selector("token()"))}, "latest"])).await?;
        Ok(format!("0x{}", &r.as_str().unwrap_or("")[26..]).to_lowercase())
    }
    /// a token's balance (raw units) of `owner`
    pub async fn balance_of(&self, token: &str, owner: &str) -> Result<u128, String> {
        let r = self.call("eth_call", json!([{"to": token, "data": format!("0x{}{}", selector("balanceOf(address)"), word_a(owner))}, "latest"])).await?;
        let s = r.as_str().unwrap_or("0x0").trim_start_matches("0x"); let s = if s.len() > 32 { &s[s.len() - 32..] } else { s };
        u128::from_str_radix(if s.is_empty() { "0" } else { s }, 16).map_err(|e| e.to_string())
    }
    /// what `owner` lets `spender` move of `token` (0: never approved; the sale reverts)
    pub async fn allowance(&self, token: &str, owner: &str, spender: &str) -> Result<u128, String> {
        let r = self.call("eth_call", json!([{"to": token, "data": allowance_data(owner, spender)}, "latest"])).await?;
        let s = r.as_str().unwrap_or("0x0").trim_start_matches("0x"); let s = if s.len() > 32 { &s[s.len() - 32..] } else { s };
        u128::from_str_radix(if s.is_empty() { "0" } else { s }, 16).map_err(|e| e.to_string())
    }
    /// CurveBuy / CurveSell logs of one curve over [from, to] (30,000 blocks a request on the official RPC)
    pub async fn curve_logs(&self, curve: &str, from: u64, to: u64) -> Result<Vec<Value>, String> {
        let mut out = vec![]; let mut a = from;
        while a <= to {
            let b = (a + 29_999).min(to);
            let r = self.call("eth_getLogs", json!([{"address": curve, "fromBlock": format!("0x{a:x}"), "toBlock": format!("0x{b:x}"), "topics": [[topic_buy(), topic_sell()]]}])).await?;
            out.extend(r.as_array().cloned().unwrap_or_default()); a = b + 1;
        }
        Ok(out)
    }
    pub async fn block_time(&self, n: u64) -> Result<u64, String> {
        let r = self.call("eth_getBlockByNumber", json!([format!("0x{n:x}"), false])).await?;
        u64::from_str_radix(r["timestamp"].as_str().unwrap_or("0x0").trim_start_matches("0x"), 16).map_err(|e| e.to_string())
    }
    pub async fn u64_of(&self, method: &str, params: Value) -> Result<u128, String> {
        let r = self.call(method, params).await?; u128::from_str_radix(r.as_str().unwrap_or("0x0").trim_start_matches("0x"), 16).map_err(|e| e.to_string())
    }
    /// sends to every send url at once; returns the hash from the first that accepts it, and each url's answer time
    /// ("host ms" or "host ms refused"), to see which node is slow
    pub async fn send_raw(&self, raw: &str) -> (Result<String, String>, String) {
        let futs = self.send_urls.iter().map(|u| async move {
            // one try, 4 s at most: the transaction goes to every node at once, so a slow node must not hold the send
            // (Nov 19 08:33: the official node took 5-33 s, PublicNode answered "failed to call backend endpoint", and
            // the transaction had landed all the same)
            let t = std::time::Instant::now();
            let r = match tokio::time::timeout(std::time::Duration::from_secs(4), self.http.post(u.as_str())
                .json(&json!({"jsonrpc": "2.0", "id": 1, "method": "eth_sendRawTransaction", "params": [raw]})).send()).await {
                Ok(Ok(resp)) => match resp.json::<Value>().await {
                    Ok(v) => match v.get("error") { Some(e) => Err(format!("eth_sendRawTransaction: {e}")), None => Ok(v["result"].clone()) },
                    Err(e) => Err(e.to_string()) },
                Ok(Err(e)) => Err(e.to_string()),
                Err(_) => Err("timed out after 4 s".to_string()),
            };
            (u, t.elapsed().as_millis(), r)
        });
        let rs = futures_util::future::join_all(futs).await; let (mut ok, mut err, mut times) = (None, String::new(), vec![]);
        for (u, ms, r) in rs {
            let host = u.trim_start_matches("https://").trim_start_matches("http://").split('/').next().unwrap_or("").to_string();
            match r { Ok(h) => { times.push(format!("{host} {ms} ms")); ok.get_or_insert(h.as_str().unwrap_or("").to_string()); }
                      Err(e) => { let why: String = e.split("\"message\":").nth(1).unwrap_or(&e).chars().take(60).collect();
                                  times.push(format!("{host} {ms} ms refused: {}", why.trim_matches(|ch: char| ch == '"' || ch == '}' || ch == ' '))); err = e } }
        }
        (ok.ok_or(err), times.join(", "))
    }
    /// waits up to `secs` for the receipt, asking the read node and every send node in turn (one slow or lagging node
    /// must not make a landed transaction look lost: Nov 19 08:33, a sale landed and the bot did not see it); None when
    /// it has not landed
    pub async fn receipt(&self, hash: &str, secs: u64) -> Option<Value> {
        let t0 = std::time::Instant::now(); let mut urls = vec![self.url.clone()];
        for u in &self.send_urls { if !urls.contains(u) { urls.push(u.clone()) } }
        let mut i = 0usize;
        while t0.elapsed().as_secs() < secs {
            let u = &urls[i % urls.len()]; i += 1;
            let r = tokio::time::timeout(std::time::Duration::from_secs(3), self.call_at(u, "eth_getTransactionReceipt", json!([hash]))).await;
            if let Ok(Ok(r)) = r { if !r.is_null() { return Some(r) } }
            tokio::time::sleep(std::time::Duration::from_millis(120)).await;
        }
        None
    }
    /// our own sale on a curve since `from` (eth_getLogs: CurveSell with us as the seller): its quoteOut, ETH
    pub async fn my_sale(&self, curve: &str, me: &str, from: u64) -> Result<Option<f64>, String> {
        let tip = self.u64_of("eth_blockNumber", json!([])).await? as u64; let mut a = from; let me32 = format!("0x{:0>64}", me.trim_start_matches("0x").to_lowercase());
        while a <= tip {
            let b = (a + 29_999).min(tip);
            let r = self.call("eth_getLogs", json!([{"address": curve, "fromBlock": format!("0x{a:x}"), "toBlock": format!("0x{b:x}"), "topics": [topic_sell(), me32]}])).await?;
            if let Some(t) = r.as_array().into_iter().flatten().filter_map(|l| decode_trade(l, 0)).last() { return Ok(Some(t.quote)) }
            a = b + 1;
        }
        Ok(None)
    }
}

pub struct Wallet { pub signer: PrivateKeySigner, pub address: String }
impl Wallet {
    /// the key file: one line, the 0x hex private key (root-only, never printed)
    pub fn load(path: &str) -> Result<Self, String> {
        let mut s = std::fs::read_to_string(path).map_err(|e| format!("{path}: {e}"))?;
        let key = s.trim().trim_matches('"').to_string(); zeroize::Zeroize::zeroize(&mut s);
        let signer = PrivateKeySigner::from_str(key.trim_start_matches("0x")).map_err(|_| format!("{path}: not a private key"))?;
        let address = format!("{:#x}", signer.address()); Ok(Wallet { signer, address })
    }
    pub fn sign(&self, chain_id: u64, nonce: u64, to: &str, value_wei: u128, data: &str, gas: u64, max_fee: u128) -> Result<String, String> {
        let input = Bytes::from(decode_hex(data.trim_start_matches("0x"))?);
        let tx = TxEip1559 { chain_id, nonce, gas_limit: gas, max_fee_per_gas: max_fee, max_priority_fee_per_gas: 0,
            to: TxKind::Call(Address::from_str(to).map_err(|e| e.to_string())?), value: U256::from(value_wei), access_list: Default::default(), input };
        let sig = self.signer.sign_hash_sync(&tx.signature_hash()).map_err(|e| e.to_string())?;
        let env: TxEnvelope = tx.into_signed(sig).into();
        Ok(format!("0x{}", hex(&env.encoded_2718())))
    }
}
/// a signed transaction's hash (keccak of its raw bytes), known before any node answers
pub fn tx_hash(raw: &str) -> String { format!("0x{}", hex(&keccak256(decode_hex(raw.trim_start_matches("0x")).unwrap_or_default()).0)) }
pub fn decode_hex(s: &str) -> Result<Vec<u8>, String> {
    if s.len() % 2 != 0 { return Err("odd hex".into()) }
    (0..s.len()).step_by(2).map(|i| u8::from_str_radix(&s[i..i + 2], 16).map_err(|e| e.to_string())).collect()
}
/// a new key, written root-only; prints only the address
pub fn keygen(path: &str) -> Result<String, String> {
    if std::path::Path::new(path).exists() { return Err(format!("{path} exists: not overwritten")) }
    let s = PrivateKeySigner::random(); let key = format!("0x{}", hex(&s.to_bytes().0));
    std::fs::write(path, key).map_err(|e| e.to_string())?;
    #[cfg(unix)] { use std::os::unix::fs::PermissionsExt; std::fs::set_permissions(path, std::fs::Permissions::from_mode(0o400)).map_err(|e| e.to_string())?; }
    Ok(format!("{:#x}", s.address()))
}
