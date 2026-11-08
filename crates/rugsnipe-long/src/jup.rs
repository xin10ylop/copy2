//! Jupiter (lite API): quotes, ready swap transactions and prices, for the
//! copier's coins that pump's own route cannot reach: other exchanges
//! (Meteora DBC and DAMM v2, Raydium LaunchLab and CPMM ...) and pump curves
//! priced in a token without a canonical pump pool (PUMP, CARDS, USDC,
//! xStocks ...). Checked on Nov 1 2026: Jupiter quoted SOL into a coin of
//! each of those venues, and into PUMP- and WXMR-quoted pump curves.
//!
//! The swap transaction comes built and unsigned (v0, our wallet the only
//! signer); [`sign_one`] signs it in place. A Jito tip, when asked for, is a
//! transfer Jupiter adds itself, so the copy goes to the Jito sender and to
//! our RPC (the other senders want a tip to their own accounts).

use crate::chain::Rpc;
use pump_codec::constants as c;
use pump_codec::Pubkey;
use serde_json::{json, Value};

/// Swap API v1 (lite: no key).
pub const SWAP: &str = "https://lite-api.jup.ag/swap/v1";
/// Price API v3.
pub const PRICE: &str = "https://lite-api.jup.ag/price/v3";

/// One quote: what goes in and comes out (raw units), the route's labels,
/// and the body the swap call wants back.
#[derive(Debug, Clone, PartialEq)]
pub struct Quote {
    pub in_amount: u64,
    pub out_amount: u64,
    /// `otherAmountThreshold`: the least the swap accepts (exact-in).
    pub min_out: u64,
    pub impact_pct: f64,
    /// The route, e.g. `Dynamic Bonding Curve` or `TesseraV > Whirlpool > Pump.fun`.
    pub route: String,
    /// `contextSlot`: the slot of the chain state the quote was priced on.
    pub slot: u64,
    pub raw: Value,
}

fn num(v: &Value) -> Option<u64> {
    match v {
        Value::String(s) => s.parse().ok(),
        Value::Number(n) => n.as_u64(),
        _ => None,
    }
}

/// A quote from the API body (`error` or no amounts: `Err`).
pub fn parse_quote(v: Value) -> Result<Quote, String> {
    if let Some(e) = v.get("error").or_else(|| v.get("errorCode")) {
        return Err(format!("jupiter quote: {e}"));
    }
    let in_amount = num(&v["inAmount"]).ok_or("jupiter quote: no inAmount")?;
    let out_amount = num(&v["outAmount"]).ok_or("jupiter quote: no outAmount")?;
    if out_amount == 0 {
        return Err("jupiter quote: zero out".into());
    }
    let min_out = num(&v["otherAmountThreshold"]).unwrap_or(0);
    let impact_pct = match &v["priceImpactPct"] {
        Value::String(s) => s.parse().unwrap_or(0.0),
        Value::Number(n) => n.as_f64().unwrap_or(0.0),
        _ => 0.0,
    };
    let route = v["routePlan"]
        .as_array()
        .map(|a| {
            a.iter()
                .map(|p| p["swapInfo"]["label"].as_str().unwrap_or("?"))
                .collect::<Vec<_>>()
                .join(" > ")
        })
        .unwrap_or_default();
    let slot = v["contextSlot"].as_u64().unwrap_or(0);
    Ok(Quote {
        in_amount,
        out_amount,
        min_out,
        impact_pct,
        route,
        slot,
        raw: v,
    })
}

/// The lite API refuses bursts (HTTP 429, Nov 1 2026: about a dozen calls in
/// 30 s). One gate for the whole process spaces the calls; after a 429 the
/// optional ones (valuing an open position) stand down for [`COOL_MS`] while
/// buys and sales wait and retry.
struct Gate {
    next_ms: u64,
    cool_until_ms: u64,
}
static GATE: std::sync::Mutex<Gate> = std::sync::Mutex::new(Gate {
    next_ms: 0,
    cool_until_ms: 0,
});
static GAP_MS: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(350);
pub const COOL_MS: u64 = 10_000;

/// Minimum spacing between two Jupiter calls (config `jupiter_gap_ms`).
pub fn set_gap_ms(ms: u64) {
    GAP_MS.store(ms, std::sync::atomic::Ordering::Relaxed);
}

/// Wait for a turn; `false` (optional calls only) while cooling down.
fn turn(optional: bool) -> bool {
    let now = crate::oracle::now_ms();
    let wait = {
        let Ok(mut g) = GATE.lock() else { return true };
        if optional && now < g.cool_until_ms {
            return false;
        }
        let at = g.next_ms.max(now);
        g.next_ms = at + GAP_MS.load(std::sync::atomic::Ordering::Relaxed);
        at - now
    };
    if wait > 0 {
        std::thread::sleep(std::time::Duration::from_millis(wait));
    }
    true
}

/// A call made now, without waiting for the gap (a swap right behind its own quote: Nov 4, 23 of 23 such swaps went
/// through, 0.17 s + 0.18 s); the next call still waits the gap after it.
fn mark() {
    let now = crate::oracle::now_ms();
    if let Ok(mut g) = GATE.lock() {
        g.next_ms = g.next_ms.max(now + GAP_MS.load(std::sync::atomic::Ordering::Relaxed));
    }
}

fn refused() {
    let now = crate::oracle::now_ms();
    if let Ok(mut g) = GATE.lock() {
        g.cool_until_ms = now + COOL_MS;
        g.next_ms = g.next_ms.max(now + 1_500);
    }
}

/// A GET through the gate: an optional call gives up on a 429, a needed one
/// retries (3 times, the gate's back-off between).
fn get(rpc: &Rpc, url: &str, optional: bool) -> Result<Value, String> {
    for i in 0..4 {
        if !turn(optional) {
            return Err("jupiter: cooling down after a 429".into());
        }
        match rpc.rpc.get_json(url) {
            Err(e) if e.contains("429") => {
                refused();
                if optional || i == 3 {
                    return Err(e);
                }
            }
            r => return r,
        }
    }
    Err("jupiter: refused".into())
}

/// Exact-in quote of `amount` raw units of `input` into `output` (a buy or
/// a sale: retried on a 429).
pub fn quote(
    rpc: &Rpc,
    base: &str,
    input: &Pubkey,
    output: &Pubkey,
    amount: u64,
    slippage_bps: u32,
) -> Result<Quote, String> {
    let v = get(rpc, &quote_url(base, input, output, amount, slippage_bps), false)?;
    parse_quote(v)
}

/// The same, optional (valuing a position): no retry, nothing while the gate
/// cools down.
pub fn quote_soft(
    rpc: &Rpc,
    base: &str,
    input: &Pubkey,
    output: &Pubkey,
    amount: u64,
    slippage_bps: u32,
) -> Result<Quote, String> {
    let v = get(rpc, &quote_url(base, input, output, amount, slippage_bps), true)?;
    parse_quote(v)
}

fn quote_url(base: &str, input: &Pubkey, output: &Pubkey, amount: u64, slippage_bps: u32) -> String {
    format!("{base}/quote?inputMint={input}&outputMint={output}&amount={amount}&slippageBps={slippage_bps}")
}

/// The swap API's request body for `q`, paid and signed by `user`.
/// `jito_tip > 0`: Jupiter adds a transfer of that much to a Jito tip
/// account; otherwise a priority fee capped at `max_priority` lamports.
pub fn swap_body(q: &Quote, user: &Pubkey, jito_tip: u64, max_priority: u64) -> Value {
    let fee = if jito_tip > 0 {
        json!({ "jitoTipLamports": jito_tip })
    } else {
        json!({ "priorityLevelWithMaxLamports": { "maxLamports": max_priority, "priorityLevel": "veryHigh" } })
    };
    json!({
        "quoteResponse": q.raw,
        "userPublicKey": user.to_string(),
        "wrapAndUnwrapSol": true,
        "dynamicComputeUnitLimit": true,
        "prioritizationFeeLamports": fee,
    })
}

/// The unsigned swap transaction (wire bytes) for `q`, and the last block
/// height its blockhash is good for (0 when Jupiter does not say).
pub fn swap_tx(
    rpc: &Rpc,
    base: &str,
    q: &Quote,
    user: &Pubkey,
    jito_tip: u64,
    max_priority: u64,
) -> Result<(Vec<u8>, u64), String> {
    let body = swap_body(q, user, jito_tip, max_priority).to_string();
    let mut tries = 0;
    let (st, text) = loop {
        if tries > 0 {
            turn(false);
        } else {
            mark();
        }
        let (st, text) =
            rpc.rpc
                .post_raw(&format!("{base}/swap"), "application/json", body.as_bytes())?;
        if st == 429 && tries < 3 {
            refused();
            tries += 1;
            continue;
        }
        break (st, text);
    };
    if st != 200 {
        return Err(format!(
            "jupiter swap: HTTP {st}: {}",
            text.chars().take(200).collect::<String>()
        ));
    }
    let v: Value = serde_json::from_str(&text).map_err(|e| format!("jupiter swap: {e}"))?;
    // Jupiter simulated it (dynamicComputeUnitLimit): a swap that fails there is not sent
    if !v["simulationError"].is_null() {
        return Err(format!(
            "jupiter swap: simulation failed: {}",
            v["simulationError"].to_string().chars().take(200).collect::<String>()
        ));
    }
    let b64 = v["swapTransaction"]
        .as_str()
        .ok_or("jupiter swap: no swapTransaction")?;
    let tx = base64::Engine::decode(&base64::engine::general_purpose::STANDARD, b64)
        .map_err(|e| format!("jupiter swap: {e}"))?;
    // we sign only a transaction we pay for
    if fee_payer(&tx) != Some(user.to_bytes()) {
        return Err("jupiter swap: the transaction's fee payer is not our wallet".into());
    }
    Ok((tx, v["lastValidBlockHeight"].as_u64().unwrap_or(0)))
}

/// The fee payer (first account key) of a wire transaction, legacy or v0.
pub fn fee_payer(tx: &[u8]) -> Option<[u8; 32]> {
    let nsig = *tx.first()? as usize;
    if nsig == 0 || nsig >= 0x80 {
        return None;
    }
    let mut i = 1 + 64 * nsig;
    if tx.get(i)? & 0x80 != 0 {
        i += 1; // the version prefix
    }
    i += 3; // the header
    let nkeys = *tx.get(i)? as usize;
    if nkeys == 0 {
        return None;
    }
    i += if nkeys >= 0x80 { 2 } else { 1 };
    tx.get(i..i + 32)?.try_into().ok()
}

/// Sign a one-signer wire transaction in place: `[1][sig 64][message]`.
/// Returns the signature.
pub fn sign_one(tx: &mut [u8], sign: impl FnOnce(&[u8]) -> [u8; 64]) -> Result<[u8; 64], String> {
    if tx.len() < 66 || tx[0] != 1 {
        return Err("jupiter swap: expected exactly one signer".into());
    }
    let sig = sign(&tx[65..]);
    tx[1..65].copy_from_slice(&sig);
    Ok(sig)
}

/// Lamports per raw unit of `mint` from the price API body
/// (`{mint: {usdPrice, decimals}}`, SOL's price included).
pub fn lamports_per_unit(body: &Value, mint: &Pubkey) -> Option<f64> {
    if *mint == c::WSOL_MINT {
        return Some(1.0);
    }
    let sol = body[c::WSOL_MINT.to_string()]["usdPrice"]
        .as_f64()
        .filter(|p| *p > 0.0)?;
    let m = &body[mint.to_string()];
    let usd = m["usdPrice"].as_f64().filter(|p| *p > 0.0)?;
    let dec = m["decimals"].as_u64()? as i32;
    Some(usd / sol * 1e9 / 10f64.powi(dec))
}

/// One price read (lamports per raw unit), `None` when unknown.
pub fn price(rpc: &Rpc, api: &str, mint: &Pubkey) -> Option<f64> {
    if *mint == c::WSOL_MINT {
        return Some(1.0);
    }
    let v = get(rpc, &format!("{api}?ids={mint},{}", c::WSOL_MINT), false).ok()?;
    lamports_per_unit(&v, mint)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_quote_reads_its_amounts_and_route() {
        let v = json!({
            "inAmount": "100000000", "outAmount": "3656623529995", "otherAmountThreshold": "3546924823695",
            "priceImpactPct": "0.0077",
            "routePlan": [{"swapInfo": {"label": "Dynamic Bonding Curve"}}]
        });
        let q = parse_quote(v).unwrap();
        assert_eq!((q.in_amount, q.out_amount, q.min_out), (100_000_000, 3_656_623_529_995, 3_546_924_823_695));
        assert_eq!(q.route, "Dynamic Bonding Curve");
        assert!((q.impact_pct - 0.0077).abs() < 1e-9);
    }

    #[test]
    fn an_error_or_an_empty_route_is_not_a_quote() {
        assert!(parse_quote(json!({"error": "No routes found"})).is_err());
        assert!(parse_quote(json!({"inAmount": "1", "outAmount": "0"})).is_err());
    }

    #[test]
    fn a_jito_tip_replaces_the_priority_fee() {
        let q = parse_quote(json!({"inAmount": "1", "outAmount": "2"})).unwrap();
        let u = c::WSOL_MINT;
        let b = swap_body(&q, &u, 1_000_000, 0);
        assert_eq!(b["prioritizationFeeLamports"]["jitoTipLamports"], 1_000_000);
        let b = swap_body(&q, &u, 0, 500_000);
        assert_eq!(
            b["prioritizationFeeLamports"]["priorityLevelWithMaxLamports"]["maxLamports"],
            500_000
        );
        assert_eq!(b["wrapAndUnwrapSol"], true);
    }

    #[test]
    fn signing_fills_the_one_signature_slot() {
        let mut tx = vec![1u8];
        tx.extend([0u8; 64]);
        tx.extend([7u8; 10]);
        let sig = sign_one(&mut tx, |m| {
            assert_eq!(m, &[7u8; 10]);
            [9u8; 64]
        })
        .unwrap();
        assert_eq!(sig, [9u8; 64]);
        assert_eq!(&tx[1..65], &[9u8; 64]);
        let mut two = vec![2u8; 140];
        assert!(sign_one(&mut two, |_| [0u8; 64]).is_err());
    }

    #[test]
    fn the_fee_payer_is_read_from_legacy_and_v0_transactions() {
        let payer = [7u8; 32];
        let other = [9u8; 32];
        // [1 sig][64 sig bytes][0x80 v0][header 3][2 keys][payer][other]...
        let mut v0 = vec![1u8];
        v0.extend([0u8; 64]);
        v0.extend([0x80, 1, 0, 1, 2]);
        v0.extend(payer);
        v0.extend(other);
        assert_eq!(fee_payer(&v0), Some(payer));
        let mut legacy = vec![1u8];
        legacy.extend([0u8; 64]);
        legacy.extend([1, 0, 1, 2]);
        legacy.extend(other);
        legacy.extend(payer);
        assert_eq!(fee_payer(&legacy), Some(other));
        assert_eq!(fee_payer(&[0u8; 10]), None);
        assert_eq!(fee_payer(&v0[..80]), None);
    }

    #[test]
    fn a_token_price_converts_to_lamports_per_raw_unit() {
        let pump: Pubkey = "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn".parse().unwrap();
        let body = json!({
            c::WSOL_MINT.to_string(): {"usdPrice": 200.0, "decimals": 9},
            pump.to_string(): {"usdPrice": 0.004, "decimals": 6}
        });
        // 0.004 USD = 0.00002 SOL a token = 20,000 lamports a token = 0.02 a raw unit
        let p = lamports_per_unit(&body, &pump).unwrap();
        assert!((p - 0.02).abs() < 1e-12);
        assert_eq!(lamports_per_unit(&body, &c::WSOL_MINT), Some(1.0));
    }
}
