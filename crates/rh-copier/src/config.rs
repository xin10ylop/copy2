//! /etc/rugsnipe/rh-copier.toml (config/rh-copier.example.toml has every key with its reason).
use serde::Deserialize;

#[derive(Deserialize, Clone, Debug)]
pub struct Leader {
    pub address: String,
    /// its buy, ETH: smaller buys are not copied
    #[serde(default = "d_min_its")] pub min_its_eth: f64,
    /// the coin type: skip when the curve already held this much ETH before its buy (0 = any)
    #[serde(default)] pub max_curve_eth: f64,
    /// the price limit: our buy reverts when it would fill above this many times its price (0 = none; 3x bounds it)
    #[serde(default)] pub max_premium: f64,
    /// take profit, price over its price (0 = none)
    #[serde(default)] pub take_profit: f64,
    /// sold this many seconds after its buy at the latest
    #[serde(default = "d_hold")] pub hold_s: u64,
    /// [n, w, from]: out when the other traders' sales outnumber their buys by n over the last w s, from `from` s
    #[serde(default)] pub sell_pressure: Vec<u64>,
    /// out when the price has made no new high for this many seconds, once at its price (0 = off)
    #[serde(default)] pub stall_s: u64,
    /// its sale: "never", "early" (30-290 s after its buy, under 1.5x) or "always"
    #[serde(default = "d_its")] pub its_sale: String,
}

#[derive(Deserialize, Clone, Debug)]
pub struct Config {
    /// "on" = real transactions; "log" = decisions only, nothing sent
    #[serde(default = "d_mode")] pub mode: String,
    pub ws_url: String,
    /// reads, receipts, nonces: the freshest node (PublicNode ran 7-10 blocks ahead of the official RPC on Nov 18)
    pub rpc_url: String,
    /// history (eth_getLogs over old blocks, for status): the official RPC keeps it, PublicNode's free tier does not
    #[serde(default = "d_logs")] pub logs_url: String,
    /// eth_sendRawTransaction goes to every one of these (the first to land wins)
    #[serde(default)] pub send_urls: Vec<String>,
    #[serde(default = "d_chain")] pub chain_id: u64,
    pub wallet_file: String,
    #[serde(default = "d_state")] pub state_dir: String,
    #[serde(default = "d_stake")] pub stake_eth: f64,
    #[serde(default = "d_max_open")] pub max_open: usize,
    #[serde(default)] pub daily_stop_eth: f64,
    /// a buy's minimum tokens without a price limit: the expected amount less this share
    #[serde(default = "d_slip")] pub slippage: f64,
    /// a sale's minimum ETH: the expected amount less this share
    #[serde(default = "d_sell_slip")] pub sell_slippage: f64,
    /// sell (and do not buy) once the curve holds this much ETH: the coin graduates at 4.2 into a Uniswap v4 pool
    /// the bot does not trade
    #[serde(default = "d_grad")] pub grad_guard_eth: f64,
    #[serde(default = "d_gas_buy")] pub gas_buy: u64,
    #[serde(default = "d_gas_sell")] pub gas_sell: u64,
    #[serde(default = "d_gas_approve")] pub gas_approve: u64,
    /// the fee cap: this many times the chain's gas price
    #[serde(default = "d_fee_mult")] pub fee_mult: f64,
    pub leaders: Vec<Leader>,
}

fn d_min_its() -> f64 { 0.03 }
fn d_logs() -> String { "https://rpc.mainnet.chain.robinhood.com".into() }
fn d_hold() -> u64 { 600 }
fn d_its() -> String { "never".into() }
fn d_mode() -> String { "log".into() }
fn d_chain() -> u64 { 4663 }
fn d_state() -> String { "/var/lib/rh-copier".into() }
fn d_stake() -> f64 { 0.02 }
fn d_max_open() -> usize { 4 }
fn d_slip() -> f64 { 0.25 }
fn d_sell_slip() -> f64 { 0.30 }
fn d_grad() -> f64 { 3.8 }
fn d_gas_buy() -> u64 { 450_000 }
fn d_gas_sell() -> u64 { 350_000 }
fn d_gas_approve() -> u64 { 80_000 }
fn d_fee_mult() -> f64 { 3.0 }

impl Config {
    pub fn load(path: &str) -> Result<Self, String> {
        let s = std::fs::read_to_string(path).map_err(|e| format!("{path}: {e}"))?;
        let c: Config = toml::from_str(&s).map_err(|e| format!("{path}: {e}"))?;
        c.check()?; Ok(c)
    }
    pub fn check(&self) -> Result<(), String> {
        if !(0.0..=1.0).contains(&self.stake_eth) { return Err("stake_eth must be in [0, 1]".into()) }
        if self.mode != "on" && self.mode != "log" { return Err("mode must be on or log".into()) }
        for l in &self.leaders {
            if !(l.address.starts_with("0x") && l.address.len() == 42) { return Err(format!("leader {}: not a 0x address", l.address)) }
            if !["never", "early", "always"].contains(&l.its_sale.as_str()) { return Err(format!("leader {}: its_sale is never, early or always", l.address)) }
            if !(l.sell_pressure.is_empty() || l.sell_pressure.len() == 3) { return Err(format!("leader {}: sell_pressure is [] or [n, w, from]", l.address)) }
        }
        Ok(())
    }
}
