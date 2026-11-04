//! The copier (docs/21): copies several wallets' buys on any venue through
//! Jupiter, beside the long copy. A SOL-coin wallet's coins sit on Meteora
//! DBC and DAMM v2, Raydium LaunchLab and CPMM and the pump curve; wallet 4's
//! part B are pump curves priced in a token pump's own route cannot reach
//! (PUMP, CARDS, USDC, xStocks ...). Neither can go through the long copy's
//! `multi_hop_swap`; Jupiter quotes all of them (checked Nov 1 2026).
//!
//! * **Detection** from the copied wallet's own balance changes, so no
//!   venue decoder is needed: its pump trade events decide on pump coins;
//!   elsewhere one coin up while SOL (or a stable) goes down is a buy, a
//!   coin down is a sale. Its buy is valued like the backtests valued it:
//!   its whole SOL change, fees included, plus the tokens it paid with at
//!   their price.
//! * **Exits**, first one wins: `max_hold_s` after our buy; right behind its
//!   own first sale of the coin (`follow_sell`); a take profit or stop on our
//!   position's value, read from a Jupiter sell quote every `poll_ms`.
//! * **Execution** ([`Exec`]): paper ([`PaperExec`], mode `log`) fills at a
//!   live Jupiter quote and charges each side `paper_side_cost_lamports`;
//!   real ([`LiveExec`], mode `on`) sends Jupiter's swap transaction with a
//!   Jito tip to our RPC and the Jito sender, waits until it lands or its
//!   blockhash expires, and books the chain's own SOL and token changes.
//! * **Book**: every event is a JSON line in `journal`; the open positions
//!   and today's closed ones are in `state`, so a restart picks them up.

use crate::chain::Rpc;
use crate::config::Mode;
use crate::jup;
use crate::txlite::TxLite;
use pump_codec::constants as c;
use pump_codec::{pda, Pubkey};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::io::Write;

/// Wrapped BTC: a float of the long copy, and an anchor of pump routes.
pub const WBTC: Pubkey = Pubkey::from_str_const("3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh");
/// USDT.
pub const USDT: Pubkey = Pubkey::from_str_const("Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB");

/// A mint a wallet pays with rather than buys (SOL and the stables).
pub fn quote_like(m: &Pubkey) -> bool {
    *m == c::WSOL_MINT || *m == c::USDC_MINT || *m == USDT
}

// ---------------------------------------------------------------- config

/// Which of a wallet's coins are copied.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize, Default)]
#[serde(rename_all = "snake_case")]
pub enum Coins {
    /// Any coin it buys, on any venue.
    #[default]
    Any,
    /// Only pump curves priced in a token that pump's own route cannot
    /// reach (wallet 4's part B; its part A stays with the long copy).
    PumpUnroutable,
}

/// What a take profit and a stop are multiples of.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize, Default)]
#[serde(rename_all = "snake_case")]
pub enum Basis {
    /// Its buy price (its SOL over its tokens): how the long copy and the
    /// backtests set them (copy2 strategy A: 2.0x / 0.8x of its price).
    #[default]
    Its,
    /// What we paid.
    Ours,
}

/// One copied wallet and its rule.
#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields, default)]
pub struct TargetCfg {
    pub name: String,
    pub wallet: String,
    pub coins: Coins,
    /// Its buy, valued in SOL, of at least this much ...
    pub min_sol: f64,
    /// ... and at most this much (0 = no ceiling).
    pub max_sol: f64,
    /// Our buy in SOL; or, when `stake_frac` is above 0, that share of its
    /// buy ...
    pub stake_sol: f64,
    pub stake_frac: f64,
    /// ... capped here (0 = no cap).
    pub stake_cap_sol: f64,
    /// Sell when our position's value (a Jupiter sell quote) reaches this
    /// multiple of `exit_basis` (0 = off) ...
    pub take_profit: f64,
    /// ... or falls to this multiple (0 = off) ...
    pub stop: f64,
    /// Multiples of its buy price (default) or of what we paid.
    pub exit_basis: Basis,
    /// No buy when Jupiter's quote prices the coin more than this over its
    /// buy price (0.3 = 30% over; 0 = off): a fill far above it starts at or
    /// past the take profit, or far above the stop.
    pub max_premium: f64,
    /// ... or this long after our buy ...
    pub max_hold_s: u64,
    /// ... or right behind its own first sale of the coin.
    pub follow_sell: bool,
    /// Open positions of this wallet at once.
    pub max_open: usize,
    /// Quote mints never copied (`pump_unroutable`).
    pub quotes_deny: Vec<String>,
}

impl Default for TargetCfg {
    fn default() -> Self {
        Self {
            name: String::new(),
            wallet: String::new(),
            coins: Coins::Any,
            min_sol: 0.0,
            max_sol: 0.0,
            stake_sol: 0.1,
            stake_frac: 0.0,
            stake_cap_sol: 0.0,
            take_profit: 0.0,
            stop: 0.0,
            exit_basis: Basis::Its,
            max_premium: 0.0,
            max_hold_s: 300,
            follow_sell: true,
            max_open: 3,
            quotes_deny: vec![],
        }
    }
}

impl TargetCfg {
    /// Our stake (lamports) for its buy of `its` lamports.
    pub fn stake(&self, its: u64) -> u64 {
        let mut s = if self.stake_frac > 0.0 {
            its as f64 * self.stake_frac
        } else {
            self.stake_sol * 1e9
        };
        if self.stake_cap_sol > 0.0 {
            s = s.min(self.stake_cap_sol * 1e9);
        }
        s.max(0.0) as u64
    }

    fn denies(&self, q: &Pubkey) -> bool {
        self.quotes_deny.iter().any(|d| d.parse::<Pubkey>().ok() == Some(*q))
    }
}

/// `/etc/rugsnipe/copier.toml`.
#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields, default)]
pub struct CopierCfg {
    pub mode: Mode,
    /// The copier's own wallet (JSON keypair, root-only).
    pub wallet_file: String,
    /// Chain reads, statuses and `sendTransaction` (a URL or `cred:NAME`).
    pub rpc_url: String,
    /// The hot unit's config (its `[feeds] grpc` and `[senders]`).
    pub hot_config: String,
    pub api_keys: String,
    /// Jupiter swap API and price API.
    pub jupiter: String,
    pub price_api: String,
    pub buy_slippage_bps: u32,
    pub sell_slippage_bps: u32,
    /// The Jito tip Jupiter adds to each swap (0 = a priority fee instead,
    /// capped at `priority_max_lamports`).
    pub jito_tip_lamports: u64,
    pub priority_max_lamports: u64,
    /// HTTP senders besides our RPC; they must accept a Jito tip (`jito`).
    pub senders: Vec<String>,
    /// Paper: what one side's transaction costs (base fee and tip).
    pub paper_side_cost_lamports: u64,
    /// No new buys once the UTC day's result is at or below
    /// `-daily_stop_sol` (exits continue).
    pub daily_stop_sol: f64,
    /// SOL kept in the wallet after a buy.
    pub min_wallet_sol: f64,
    /// Open positions at once, all wallets together.
    pub max_open: usize,
    /// How often an open position with a take profit or a stop is valued.
    pub poll_ms: u64,
    /// Minimum spacing between two Jupiter calls (the lite API refuses bursts).
    pub jupiter_gap_ms: u64,
    /// How long a sent swap is waited for before its blockhash's expiry is
    /// checked (it is never given up while it can still land).
    pub confirm_s: u64,
    /// A buy of the copied wallet seen more than this many slots after the feed's newest slot is not copied (the
    /// copier fell behind its queue while a swap was waiting); 0 = no check.
    pub max_lag_slots: u64,
    pub journal: String,
    pub state: String,
    /// While this file exists, no new buys (exits continue).
    pub kill_file: String,
    #[serde(rename = "target")]
    pub targets: Vec<TargetCfg>,
}

impl Default for CopierCfg {
    fn default() -> Self {
        Self {
            mode: Mode::Log,
            wallet_file: "/etc/rugsnipe/keys/copier-wallet.json".into(),
            rpc_url: String::new(),
            hot_config: "/etc/rugsnipe/rugsnipe.toml".into(),
            api_keys: "/etc/rugsnipe/keys/api-keys.toml".into(),
            jupiter: jup::SWAP.into(),
            price_api: jup::PRICE.into(),
            buy_slippage_bps: 2_000,
            sell_slippage_bps: 5_000,
            jito_tip_lamports: 1_000_000,
            priority_max_lamports: 1_000_000,
            senders: vec!["jito".into()],
            paper_side_cost_lamports: 1_100_000,
            daily_stop_sol: 1.0,
            min_wallet_sol: 0.05,
            max_open: 6,
            poll_ms: 3_000,
            jupiter_gap_ms: 350,
            confirm_s: 40,
            max_lag_slots: 10,
            journal: "/var/lib/rugsnipe-copier/copier.jsonl".into(),
            state: "/var/lib/rugsnipe-copier/state.json".into(),
            kill_file: "/var/lib/rugsnipe-copier/KILL".into(),
            targets: vec![],
        }
    }
}

impl CopierCfg {
    pub fn from_toml_str(s: &str) -> Result<Self, String> {
        let c: Self = toml::from_str(s).map_err(|e| e.to_string())?;
        c.validate()?;
        Ok(c)
    }

    pub fn validate(&self) -> Result<(), String> {
        let bad = |w: String| Err(format!("copier.toml: {w}"));
        if self.targets.is_empty() {
            return bad("no [[target]]".into());
        }
        for (i, t) in self.targets.iter().enumerate() {
            let n = &t.name;
            if n.is_empty() || self.targets[..i].iter().any(|o| o.name == *n) {
                return bad(format!("target {i}: a name, unique"));
            }
            if t.wallet.parse::<Pubkey>().is_err() {
                return bad(format!("{n}: wallet"));
            }
            if t.stake_sol <= 0.0 && t.stake_frac <= 0.0 {
                return bad(format!("{n}: stake_sol or stake_frac above 0"));
            }
            if t.take_profit != 0.0 && t.take_profit <= 1.0 {
                return bad(format!("{n}: take_profit 0 (off) or above 1"));
            }
            if t.stop != 0.0 && !(t.stop > 0.0 && t.stop < 1.0) {
                return bad(format!("{n}: stop 0 (off) or between 0 and 1"));
            }
            if t.max_hold_s == 0 || t.max_open == 0 || t.min_sol < 0.0 {
                return bad(format!("{n}: max_hold_s, max_open above 0; min_sol at least 0"));
            }
            if t.max_premium < 0.0 {
                return bad(format!("{n}: max_premium at least 0"));
            }
            if t.quotes_deny.iter().any(|q| q.parse::<Pubkey>().is_err()) {
                return bad(format!("{n}: quotes_deny"));
            }
        }
        if self.buy_slippage_bps > 10_000 || self.sell_slippage_bps > 10_000 {
            return bad("slippage in basis points, at most 10000".into());
        }
        // Jupiter puts the tip in the swap, to a Jito tip account: another
        // sender (Nozomi ...) would get a transaction without its own tip
        if self.senders.iter().any(|n| n != "jito") {
            return bad("senders: only \"jito\" (the tip in Jupiter's swap is a Jito tip)".into());
        }
        if !self.senders.is_empty() && self.jito_tip_lamports < 1_000 {
            return bad("senders [\"jito\"] need jito_tip_lamports of at least 1000".into());
        }
        if self.daily_stop_sol <= 0.0 || self.max_open == 0 || self.poll_ms < 500 {
            return bad("daily_stop_sol and max_open above 0, poll_ms at least 500".into());
        }
        Ok(())
    }

    /// The wallets copied, in config order.
    pub fn wallets(&self) -> Vec<Pubkey> {
        self.targets
            .iter()
            .filter_map(|t| t.wallet.parse().ok())
            .collect()
    }
}

// ------------------------------------------------------------- detection

/// Its buy of a coin.
#[derive(Debug, Clone, PartialEq)]
pub struct Buy {
    pub mint: Pubkey,
    /// The coin's token program.
    pub program: Pubkey,
    pub tokens: u64,
    /// Lamports: its SOL change (fees included) plus the tokens it paid with
    /// at their price; `None` when a token it paid with has no price.
    pub sol_value: Option<u64>,
    /// Bought on a pump curve ...
    pub on_pump: bool,
    /// ... priced in this token (`None`: SOL, or not a pump curve).
    pub pump_quote: Option<Pubkey>,
}

/// One thing a copied wallet did in a transaction.
#[derive(Debug, Clone, PartialEq)]
pub enum Act {
    Buy(Buy),
    Sell { mint: Pubkey, tokens: u64 },
}

/// What wallet `w` did in `tx` (a transaction it signed and that succeeded).
/// `price`: lamports per raw unit of a token it paid with.
pub fn read(tx: &TxLite, w: &Pubkey, price: &mut dyn FnMut(&Pubkey) -> Option<f64>) -> Vec<Act> {
    if tx.err || tx.signer() != Some(*w) {
        return vec![];
    }
    // its change per mint (wrapped SOL is counted with SOL)
    let mut d: Vec<(Pubkey, i128, Pubkey)> = vec![];
    for b in tx.tokens.iter().filter(|b| b.owner == *w && b.mint != c::WSOL_MINT) {
        let x = b.post as i128 - b.pre as i128;
        match d.iter_mut().find(|e| e.0 == b.mint) {
            Some(e) => e.1 += x,
            None => d.push((b.mint, x, b.program)),
        }
    }
    let delta = |m: &Pubkey| d.iter().find(|e| e.0 == *m).map(|e| e.1).unwrap_or(0);
    let prog = |m: &Pubkey| {
        d.iter()
            .find(|e| e.0 == *m)
            .map(|e| e.2)
            .or_else(|| tx.mint_program(m))
            .unwrap_or(c::SPL_TOKEN_PROGRAM_ID)
    };
    let trades: Vec<_> = tx.trades().into_iter().filter(|t| t.user == *w).collect();
    let mut out = vec![];
    let mut bought: Vec<(Pubkey, bool, Option<Pubkey>)> = vec![];
    if !trades.is_empty() {
        // its pump trades decide on their coins; the rest of its balance
        // changes are what it paid with or got back
        for t in &trades {
            if t.is_buy {
                if !bought.iter().any(|b| b.0 == t.mint) {
                    let q = t.quote_mint.filter(|q| !c::is_sol_like_quote_mint(q));
                    bought.push((t.mint, true, q));
                }
            } else if !out
                .iter()
                .any(|a| matches!(a, Act::Sell { mint, .. } if *mint == t.mint))
            {
                let left = (-delta(&t.mint)).max(0) as u64;
                out.push(Act::Sell {
                    mint: t.mint,
                    tokens: if left > 0 { left } else { t.token_amount },
                });
            }
        }
    } else {
        let ups: Vec<&(Pubkey, i128, Pubkey)> =
            d.iter().filter(|e| e.1 > 0 && !quote_like(&e.0)).collect();
        let downs: Vec<&(Pubkey, i128, Pubkey)> =
            d.iter().filter(|e| e.1 < 0 && !quote_like(&e.0)).collect();
        for e in &downs {
            out.push(Act::Sell {
                mint: e.0,
                tokens: (-e.1) as u64,
            });
        }
        // one coin up, nothing else of its coins down: a buy (a coin for a
        // coin is read as the sale of the one that fell)
        if ups.len() == 1 && downs.is_empty() {
            bought.push((ups[0].0, false, None));
        }
    }
    for (mint, on_pump, pump_quote) in bought {
        let tokens = delta(&mint).max(0) as u64;
        if tokens == 0 {
            continue;
        }
        let sol = tx.sol_spent(w).max(0) as f64;
        let mut value = Some(sol);
        for (m, x, _) in d.iter().filter(|e| e.1 < 0 && e.0 != mint) {
            value = match (value, price(m)) {
                (Some(v), Some(p)) => Some(v + (-*x) as f64 * p),
                _ => None,
            };
        }
        let value = value.filter(|v| *v > 0.0).map(|v| v as u64);
        if value.is_none() && sol <= 0.0 && d.iter().all(|e| e.1 >= 0 || e.0 == mint) {
            continue; // nothing paid: a transfer in, not a buy
        }
        out.push(Act::Buy(Buy {
            mint,
            program: prog(&mint),
            tokens,
            sol_value: value,
            on_pump,
            pump_quote,
        }));
    }
    out
}

// ------------------------------------------------------------- execution

/// One fill: SOL it cost (a buy, fees included) or brought back (a sale,
/// net of fees), the tokens, the route.
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct Fill {
    pub sig: String,
    pub lamports: u64,
    pub tokens: u64,
    pub route: String,
    /// The slot it priced at (paper: the quote's state) or landed in (live); 0 = unknown.
    #[serde(default)]
    pub slot: u64,
}

/// How the copier trades and prices.
pub trait Exec {
    fn now_ms(&self) -> u64;
    fn paper(&self) -> bool;
    /// Buy `mint` with `lamports` of SOL.
    /// Buy `mint` for `lamports`; refused (an error starting `premium`)
    /// when the quote gives fewer than `min_tokens`.
    fn buy(&mut self, mint: &Pubkey, program: &Pubkey, lamports: u64, min_tokens: u64) -> Result<Fill, String>;
    /// Sell `tokens` of `mint` for SOL.
    fn sell(&mut self, mint: &Pubkey, program: &Pubkey, tokens: u64) -> Result<Fill, String>;
    /// What `tokens` of `mint` sell for now (lamports; `None`: no quote).
    fn value(&mut self, mint: &Pubkey, tokens: u64) -> Option<u64>;
    /// Lamports per raw unit of `mint`.
    fn price(&mut self, mint: &Pubkey) -> Option<f64>;
    /// `true` when pump's own route reaches a curve priced in `quote`: WBTC,
    /// or a canonical PumpSwap pool of `quote` against wrapped SOL or WBTC.
    fn pump_routable(&mut self, quote: &Pubkey) -> bool;
}

impl<T: Exec + ?Sized> Exec for Box<T> {
    fn now_ms(&self) -> u64 {
        (**self).now_ms()
    }
    fn paper(&self) -> bool {
        (**self).paper()
    }
    fn buy(&mut self, mint: &Pubkey, program: &Pubkey, lamports: u64, min_tokens: u64) -> Result<Fill, String> {
        (**self).buy(mint, program, lamports, min_tokens)
    }
    fn sell(&mut self, mint: &Pubkey, program: &Pubkey, tokens: u64) -> Result<Fill, String> {
        (**self).sell(mint, program, tokens)
    }
    fn value(&mut self, mint: &Pubkey, tokens: u64) -> Option<u64> {
        (**self).value(mint, tokens)
    }
    fn price(&mut self, mint: &Pubkey) -> Option<f64> {
        (**self).price(mint)
    }
    fn pump_routable(&mut self, quote: &Pubkey) -> bool {
        (**self).pump_routable(quote)
    }
}

fn wall_ms() -> u64 {
    crate::oracle::now_ms()
}

/// The premium check on a buy quote.
fn premium(q: &jup::Quote, min_tokens: u64) -> Result<(), String> {
    if q.out_amount < min_tokens {
        return Err(format!("premium: the quote gives {} units, under {min_tokens}", q.out_amount));
    }
    Ok(())
}

/// Prices and pump-routability, cached (shared by both executors).
#[derive(Default)]
struct Caches {
    prices: HashMap<Pubkey, (Option<f64>, u64)>,
    routable: HashMap<Pubkey, bool>,
}

impl Caches {
    fn price(&mut self, rpc: &Rpc, api: &str, mint: &Pubkey) -> Option<f64> {
        if let Some((p, at)) = self.prices.get(mint) {
            if wall_ms().saturating_sub(*at) < 60_000 {
                return *p;
            }
        }
        let p = jup::price(rpc, api, mint);
        self.prices.insert(*mint, (p, wall_ms()));
        p
    }

    fn pump_routable(&mut self, rpc: &Rpc, quote: &Pubkey) -> bool {
        if *quote == WBTC || c::is_sol_like_quote_mint(quote) {
            return true;
        }
        if let Some(r) = self.routable.get(quote) {
            return *r;
        }
        let pools = [
            pda::canonical_pump_swap_pool(quote, &c::WSOL_MINT),
            pda::canonical_pump_swap_pool(quote, &WBTC),
        ];
        match rpc.accounts(&pools) {
            Ok(a) => {
                let r = a.iter().any(|x| x.is_some());
                self.routable.insert(*quote, r);
                r
            }
            // unknown: treated as routable, so the copier stays off the coin
            // (the long copy's rule decides it)
            Err(_) => true,
        }
    }
}

/// Paper: fills at a live Jupiter quote, `paper_side_cost_lamports` a side.
pub struct PaperExec {
    pub rpc: Rpc,
    cfg: CopierCfg,
    caches: Caches,
}

impl PaperExec {
    pub fn new(rpc: Rpc, cfg: CopierCfg) -> Self {
        Self {
            rpc,
            cfg,
            caches: Caches::default(),
        }
    }
}

impl Exec for PaperExec {
    fn now_ms(&self) -> u64 {
        wall_ms()
    }
    fn paper(&self) -> bool {
        true
    }
    fn buy(&mut self, mint: &Pubkey, _: &Pubkey, lamports: u64, min_tokens: u64) -> Result<Fill, String> {
        let q = jup::quote(&self.rpc, &self.cfg.jupiter, &c::WSOL_MINT, mint, lamports, self.cfg.buy_slippage_bps)?;
        premium(&q, min_tokens)?;
        Ok(Fill {
            sig: "paper".into(),
            lamports: lamports + self.cfg.paper_side_cost_lamports,
            tokens: q.out_amount,
            route: q.route,
            slot: q.slot,
        })
    }
    fn sell(&mut self, mint: &Pubkey, _: &Pubkey, tokens: u64) -> Result<Fill, String> {
        let q = jup::quote(&self.rpc, &self.cfg.jupiter, mint, &c::WSOL_MINT, tokens, self.cfg.sell_slippage_bps)?;
        Ok(Fill {
            sig: "paper".into(),
            lamports: q.out_amount.saturating_sub(self.cfg.paper_side_cost_lamports),
            tokens,
            route: q.route,
            slot: q.slot,
        })
    }
    fn value(&mut self, mint: &Pubkey, tokens: u64) -> Option<u64> {
        jup::quote_soft(&self.rpc, &self.cfg.jupiter, mint, &c::WSOL_MINT, tokens, self.cfg.sell_slippage_bps)
            .ok()
            .map(|q| q.out_amount)
    }
    fn price(&mut self, mint: &Pubkey) -> Option<f64> {
        let api = self.cfg.price_api.clone();
        self.caches.price(&self.rpc, &api, mint)
    }
    fn pump_routable(&mut self, quote: &Pubkey) -> bool {
        self.caches.pump_routable(&self.rpc, quote)
    }
}

/// Real: Jupiter's swap transaction, signed, sent to our RPC and the
/// senders, waited for, and booked from the chain's own changes.
pub struct LiveExec {
    pub rpc: Rpc,
    signer: rugsnipe_tx::signer::HotSigner,
    me: Pubkey,
    out: Option<crate::send::Out>,
    cfg: CopierCfg,
    caches: Caches,
    resends: u64,
}

impl LiveExec {
    pub fn new(
        rpc: Rpc,
        signer: rugsnipe_tx::signer::HotSigner,
        out: Option<crate::send::Out>,
        cfg: CopierCfg,
    ) -> Self {
        let me = signer.pubkey();
        Self {
            rpc,
            signer,
            me,
            out,
            cfg,
            caches: Caches::default(),
            resends: 0,
        }
    }

    /// Swap along `q` and wait until it is confirmed, or until it can no longer land (its blockhash expired). The
    /// signature and the landed transaction (`None`: confirmed but not readable; the caller books from balances).
    fn swap(&mut self, q: &jup::Quote, kind: rugsnipe_tx::senders::VariantKind) -> Result<(String, Option<TxLite>), SwapErr> {
        let sure = |why: String| SwapErr { why, sig: None };
        let (mut tx, last_valid) = jup::swap_tx(
            &self.rpc,
            &self.cfg.jupiter,
            q,
            &self.me,
            self.cfg.jito_tip_lamports,
            self.cfg.priority_max_lamports,
        )
        .map_err(sure)?;
        let signer = &self.signer;
        let sig = jup::sign_one(&mut tx, |m| signer.sign(m)).map_err(sure)?;
        let s = bs58::encode(sig).into_string();
        self.send_all(&tx, sig, kind, &s, true);
        let unsure = |why: String| SwapErr { why, sig: Some(s.clone()) };
        // Wait for confirmed, not processed: a processed status can be on a fork that is dropped (and the swap land
        // later on the main one), and the confirmed transaction is the one we book. Re-sent every 2 s (the same
        // signed bytes: it can land only once) until it lands or its blockhash expires. Giving up sooner would leave
        // a buy that lands late as tokens no position owns, never sold. Without Jupiter's `lastValidBlockHeight`:
        // confirm_s, then 90 s more (a blockhash is good for 150 blocks, about 60-90 s).
        let start = wall_ms();
        let deadline = start + self.cfg.confirm_s * 1000;
        let hard = deadline + 90_000;
        let (mut expired, mut seen, mut last_send) = (false, false, start);
        loop {
            std::thread::sleep(std::time::Duration::from_millis(400));
            if let Ok(v) = self.rpc.statuses_conf(std::slice::from_ref(&s)) {
                match v.first() {
                    Some(Some(Ok((_, true)))) => break,
                    Some(Some(Err((e, true)))) => return Err(sure(format!("{}: landed and failed: {e}", &s[..8]))),
                    Some(Some(_)) => seen = true, // processed only: wait for confirmed
                    _ if expired && !seen => return Err(sure(format!("{}: not landed, blockhash expired", &s[..8]))),
                    _ => {}
                }
            }
            let now = wall_ms();
            if now > hard + 60_000 {
                // the RPC cannot say: the caller checks the wallet
                return Err(unsure(format!("{}: status unknown (RPC)", &s[..8])));
            }
            if !expired && now >= last_send + 2_000 {
                last_send = now;
                self.send_all(&tx, sig, kind, &s, false);
            }
            if last_valid > 0 || now > deadline {
                expired = if last_valid > 0 {
                    matches!(self.rpc.block_height(), Ok(h) if h > last_valid) || now > hard
                } else {
                    now > hard
                };
            }
            if expired && seen && now > hard {
                // seen processed, never confirmed, and long expired: dropped with its fork, or the RPC is stuck
                return Err(unsure(format!("{}: seen processed, never confirmed", &s[..8])));
            }
        }
        // the confirmed transaction (the RPC may lag a few slots)
        for _ in 0..20 {
            if let Ok(v) = self.rpc.transaction(&s) {
                return match TxLite::from_rpc_json(&v) {
                    Ok(t) => Ok((s, Some(t))),
                    Err(_) => Ok((s, None)),
                };
            }
            std::thread::sleep(std::time::Duration::from_millis(500));
        }
        Ok((s, None))
    }

    /// The signed swap to our RPC and the senders. Re-sends (`first = false`) go to the senders every other time
    /// (Jito takes about one request a second from us).
    fn send_all(&mut self, tx: &[u8], sig: [u8; 64], kind: rugsnipe_tx::senders::VariantKind, s: &str, first: bool) {
        let rpc_sent = self.rpc.send(tx);
        self.resends += 1;
        if first || self.resends % 2 == 0 {
            if let Some(o) = &self.out {
                let tips = o.tips(self.cfg.jito_tip_lamports);
                let txs = vec![(tx.to_vec(), sig); tips.len()];
                for r in o.send_each(kind, &txs, &tips) {
                    if !r.ok && first {
                        eprintln!("copier: sender {} refused {}: {}", r.label, &s[..8], r.why);
                    }
                }
            }
        }
        if let Err(e) = rpc_sent {
            if first {
                eprintln!("copier: rpc send {}: {e}", &s[..8]);
            }
        }
    }

    /// Our coins of `mint` at the confirmed commitment, read up to `n` times 2 s apart until some show.
    fn held_confirmed(&self, mint: &Pubkey, program: &Pubkey, n: u32) -> u64 {
        for i in 0..n {
            if i > 0 {
                std::thread::sleep(std::time::Duration::from_millis(2_000));
            }
            if let Ok(h) = self.rpc.token_balance_confirmed(&self.me, mint, program) {
                if h > 0 {
                    return h;
                }
            }
        }
        0
    }

    /// A sale of `mint` from our wallet that landed (an earlier try whose wait ended in an error): our newest
    /// transactions, back to our buy of it.
    fn landed_sale(&self, mint: &Pubkey) -> Option<(String, TxLite)> {
        for s in self.rpc.recent_signatures(&self.me, 30).ok()? {
            let Ok(v) = self.rpc.transaction(&s) else { continue };
            let Ok(t) = TxLite::from_rpc_json(&v) else { continue };
            let d = t.token_delta(&self.me, mint);
            if d < 0 {
                return Some((s, t));
            }
            if d > 0 {
                return None; // our buy of it: no sale since
            }
        }
        None
    }
}

/// A swap that did not end confirmed. `sig: None`: nothing landed for sure (refused before sending, failed on chain,
/// or expired unseen). `Some`: sent, and the RPC could not say how it ended.
struct SwapErr {
    why: String,
    sig: Option<String>,
}

/// Rent of a new token account, paid in our buy (an estimate for a buy booked from balances).
const ATA_RENT: u64 = 2_039_280;

impl Exec for LiveExec {
    fn now_ms(&self) -> u64 {
        wall_ms()
    }
    fn paper(&self) -> bool {
        false
    }
    fn buy(&mut self, mint: &Pubkey, program: &Pubkey, lamports: u64, min_tokens: u64) -> Result<Fill, String> {
        let bal = self.rpc.balance(&self.me)?;
        let keep = (self.cfg.min_wallet_sol * 1e9) as u64;
        if bal < lamports + keep + self.cfg.jito_tip_lamports {
            return Err(format!("wallet {:.4} SOL: not enough for {:.4} + {:.4} kept", bal as f64 / 1e9, lamports as f64 / 1e9, keep as f64 / 1e9));
        }
        let q = jup::quote(&self.rpc, &self.cfg.jupiter, &c::WSOL_MINT, mint, lamports, self.cfg.buy_slippage_bps)?;
        premium(&q, min_tokens)?;
        let (s, t, why) = match self.swap(&q, rugsnipe_tx::senders::VariantKind::Buy) {
            Ok((s, t)) => (s, t, None),
            Err(SwapErr { why, sig: None }) => return Err(why),
            Err(SwapErr { why, sig: Some(s) }) => (s, None, Some(why)),
        };
        if let Some(t) = t {
            let tokens = t.token_delta(&self.me, mint).max(0) as u64;
            if tokens == 0 {
                return Err(format!("{}: landed with no tokens", &s[..8]));
            }
            return Ok(Fill {
                sig: s,
                lamports: t.sol_spent(&self.me).max(0) as u64,
                tokens,
                route: q.route,
                slot: t.slot,
            });
        }
        // confirmed but unreadable, or the RPC could not say: the wallet decides. A buy that landed is always booked,
        // or its coins would stay in the wallet, never sold.
        let held = self.held_confirmed(mint, program, 4);
        if held == 0 {
            return Err(format!("{}: {}; the wallet holds none of the coin", &s[..8], why.unwrap_or_else(|| "confirmed, not readable".into())));
        }
        Ok(Fill {
            sig: s,
            lamports: lamports + self.cfg.jito_tip_lamports + 5_000 + ATA_RENT,
            tokens: held,
            route: format!("{} (booked from balances: the transaction was not read; cost estimated)", q.route),
            slot: 0,
        })
    }
    fn sell(&mut self, mint: &Pubkey, program: &Pubkey, tokens: u64) -> Result<Fill, String> {
        let mut held = self.rpc.token_balance(&self.me, mint, program)?;
        if held == 0 {
            // A zero read: confirm it (a processed read can hit a node a few slots behind), then look for a sale of
            // ours that landed (an earlier try whose wait ended in an error) before closing with nothing back.
            held = self.held_confirmed(mint, program, 3);
            if held == 0 {
                if let Some((s, t)) = self.landed_sale(mint) {
                    return Ok(Fill {
                        lamports: (-t.sol_spent(&self.me)).max(0) as u64,
                        tokens: (-t.token_delta(&self.me, mint)).max(0) as u64,
                        slot: t.slot,
                        sig: s,
                        route: "an earlier try landed (found on chain)".into(),
                    });
                }
                // nothing held and no sale of ours: gone some other way, closed with nothing back
                return Ok(Fill {
                    sig: "none-held".into(),
                    lamports: 0,
                    tokens: 0,
                    route: String::new(),
                    slot: 0,
                });
            }
        }
        let amount = tokens.min(held);
        let q = jup::quote(&self.rpc, &self.cfg.jupiter, mint, &c::WSOL_MINT, amount, self.cfg.sell_slippage_bps)?;
        let (s, t) = self.swap(&q, rugsnipe_tx::senders::VariantKind::Sell).map_err(|e| e.why)?;
        let Some(t) = t else {
            // confirmed, not readable: the next try finds it on chain and books it
            return Err(format!("{}: confirmed, not readable yet", &s[..8]));
        };
        Ok(Fill {
            sig: s,
            lamports: (-t.sol_spent(&self.me)).max(0) as u64,
            tokens: amount,
            route: q.route,
            slot: t.slot,
        })
    }
    fn value(&mut self, mint: &Pubkey, tokens: u64) -> Option<u64> {
        jup::quote_soft(&self.rpc, &self.cfg.jupiter, mint, &c::WSOL_MINT, tokens, self.cfg.sell_slippage_bps)
            .ok()
            .map(|q| q.out_amount)
    }
    fn price(&mut self, mint: &Pubkey) -> Option<f64> {
        let api = self.cfg.price_api.clone();
        self.caches.price(&self.rpc, &api, mint)
    }
    fn pump_routable(&mut self, quote: &Pubkey) -> bool {
        self.caches.pump_routable(&self.rpc, quote)
    }
}

// ------------------------------------------------------------- the book

/// One position, open or closed.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Pos {
    pub id: u64,
    pub target: String,
    pub mint: String,
    pub program: String,
    pub paper: bool,
    pub its_sig: String,
    /// Its buy, SOL.
    pub its_sol: f64,
    /// Its price: lamports per raw unit of the coin (0 = unknown).
    #[serde(default)]
    pub its_ppu: f64,
    pub opened_ms: u64,
    /// Lamports we paid (fees included).
    pub cost: u64,
    pub tokens: u64,
    pub buy_sig: String,
    pub route: String,
    pub last_value: Option<u64>,
    pub last_poll_ms: u64,
    /// Set once an exit fired; a failed sale is retried until it lands.
    pub exit: Option<String>,
    pub tries: u32,
    pub next_try_ms: u64,
    pub closed_ms: Option<u64>,
    pub proceeds: Option<u64>,
    pub sell_sig: Option<String>,
}

impl Pos {
    pub fn open(&self) -> bool {
        self.closed_ms.is_none()
    }
    /// Lamports won or lost, once closed.
    pub fn net(&self) -> Option<i64> {
        self.proceeds.map(|p| p as i64 - self.cost as i64)
    }
    /// Open, its exit fired, and its sale failed `STUCK_TRIES` times (no route, a pulled pool ...): still retried
    /// every 5 min, but it no longer holds a `max_open` slot, and the daily stop counts it as lost.
    pub fn stuck(&self) -> bool {
        self.open() && self.exit.is_some() && self.tries >= STUCK_TRIES
    }
}

/// Failed sales after which a position is stuck (about 10 min of retries).
pub const STUCK_TRIES: u32 = 20;

const DAY_MS: u64 = 86_400_000;

/// The copier's engine.
pub struct Copier<E: Exec> {
    pub cfg: CopierCfg,
    targets: Vec<(Pubkey, TargetCfg)>,
    pub exec: E,
    /// Open positions and the ones closed today (UTC).
    pub book: Vec<Pos>,
    next_id: u64,
    /// No buys while the feed is down.
    pub feed_up: bool,
    /// The feed's newest slot when the current transaction is handled (0 = unknown: no age check).
    pub tip_slot: u64,
    /// While an exit behind its sale runs: its sale's slot (journaled beside ours).
    its_sale_slot: u64,
    /// Every journal line of this run (also appended to `cfg.journal`).
    pub lines: Vec<Value>,
}

impl<E: Exec> Copier<E> {
    pub fn new(cfg: CopierCfg, exec: E) -> Result<Self, String> {
        cfg.validate()?;
        jup::set_gap_ms(cfg.jupiter_gap_ms);
        let targets = cfg
            .targets
            .iter()
            .map(|t| (t.wallet.parse::<Pubkey>().expect("validated"), t.clone()))
            .collect();
        Ok(Self {
            cfg,
            targets,
            exec,
            book: vec![],
            next_id: 1,
            feed_up: true,
            tip_slot: 0,
            its_sale_slot: 0,
            lines: vec![],
        })
    }

    /// The open positions and today's closed ones from `cfg.state`.
    pub fn load_state(&mut self) -> Result<usize, String> {
        if self.cfg.state.is_empty() {
            return Ok(0);
        }
        let text = match std::fs::read_to_string(&self.cfg.state) {
            Ok(t) => t,
            Err(_) => return Ok(0),
        };
        let book: Vec<Pos> = serde_json::from_str(&text).map_err(|e| format!("{}: {e}", self.cfg.state))?;
        let today = self.exec.now_ms() / DAY_MS;
        self.book = book
            .into_iter()
            .filter(|p| p.open() || p.closed_ms.map(|c| c / DAY_MS) == Some(today))
            .collect();
        self.next_id = self.book.iter().map(|p| p.id).max().unwrap_or(0) + 1;
        // back to paper with real coins still held: paper would "sell" them at a quote and leave them in the wallet
        let real = self.book.iter().filter(|p| p.open() && !p.paper).count();
        if self.exec.paper() && real > 0 {
            return Err(format!(
                "{}: {real} real position(s) still open; run mode on until they close, or sell them by hand",
                self.cfg.state
            ));
        }
        Ok(self.book.iter().filter(|p| p.open()).count())
    }

    fn save(&self) {
        if self.cfg.state.is_empty() {
            return;
        }
        let tmp = format!("{}.tmp", self.cfg.state);
        let r = serde_json::to_string(&self.book)
            .map_err(|e| e.to_string())
            .and_then(|s| std::fs::write(&tmp, s).map_err(|e| e.to_string()))
            .and_then(|_| std::fs::rename(&tmp, &self.cfg.state).map_err(|e| e.to_string()));
        if let Err(e) = r {
            // a restart would not know the open positions: their coins would stay in the wallet
            eprintln!("copier: STATE NOT SAVED ({}): {e}", self.cfg.state);
        }
    }

    fn log(&mut self, ev: &str, mut v: Value) {
        v["ts"] = json!(self.exec.now_ms());
        v["ev"] = json!(ev);
        if v.get("paper").is_none() {
            v["paper"] = json!(self.exec.paper());
        }
        if !self.cfg.journal.is_empty() {
            if let Ok(mut f) = std::fs::OpenOptions::new()
                .create(true)
                .append(true)
                .open(&self.cfg.journal)
            {
                let _ = writeln!(f, "{v}");
            }
        }
        let quiet = ev == "skip"
            && matches!(v["why"].as_str(), Some("small" | "not-pump-unroutable" | "pump-routable" | "large"));
        if !quiet {
            println!("copier {ev} {v}");
        }
        self.lines.push(v);
    }

    /// Today's (UTC) closed result, lamports; paper and real apart (the
    /// mode's own kind counts, so paper trades from before a switch to mode
    /// on never trip the real daily stop).
    pub fn day_net(&self) -> i64 {
        let today = self.exec.now_ms() / DAY_MS;
        let paper = self.exec.paper();
        let closed: i64 = self
            .book
            .iter()
            .filter(|p| p.paper == paper && p.closed_ms.map(|c| c / DAY_MS) == Some(today))
            .filter_map(|p| p.net())
            .sum();
        let stuck: i64 = self.book.iter().filter(|p| p.paper == paper && p.stuck()).map(|p| p.cost as i64).sum();
        closed - stuck
    }

    /// Open positions of the mode's own kind (paper or real).
    pub fn open_count(&self, target: Option<&str>) -> usize {
        let paper = self.exec.paper();
        self.book
            .iter()
            .filter(|p| p.open() && !p.stuck() && p.paper == paper && target.is_none_or(|t| p.target == t))
            .count()
    }

    pub fn set_feed(&mut self, up: bool) {
        if up != self.feed_up {
            self.log("feed", json!({ "up": up }));
        }
        self.feed_up = up;
    }

    /// A transaction from the feed.
    pub fn on_tx(&mut self, tx: &TxLite) {
        let Some(signer) = tx.signer() else { return };
        for i in 0..self.targets.len() {
            if self.targets[i].0 != signer {
                continue;
            }
            let w = self.targets[i].0;
            let acts = {
                let exec = &mut self.exec;
                read(tx, &w, &mut |m| exec.price(m))
            };
            for a in acts {
                match a {
                    Act::Buy(b) => self.on_buy(i, b, &tx.sig_b58(), tx.slot),
                    Act::Sell { mint, .. } => {
                        self.its_sale_slot = tx.slot;
                        self.on_sell(i, &mint);
                        self.its_sale_slot = 0;
                    }
                }
            }
        }
    }

    fn skip(&mut self, t: &str, mint: &Pubkey, its: &str, why: &str, extra: Value) {
        let mut v = json!({ "target": t, "mint": mint.to_string(), "its_sig": its, "why": why });
        if let (Some(o), Some(e)) = (v.as_object_mut(), extra.as_object()) {
            for (k, x) in e {
                o.insert(k.clone(), x.clone());
            }
        }
        self.log("skip", v);
    }

    fn on_buy(&mut self, i: usize, b: Buy, its_sig: &str, slot: u64) {
        let t = self.targets[i].1.clone();
        let name = t.name.as_str();
        if t.coins == Coins::PumpUnroutable {
            match b.pump_quote {
                None => return self.skip(name, &b.mint, its_sig, "not-pump-unroutable", json!({})),
                Some(q) if t.denies(&q) => {
                    return self.skip(name, &b.mint, its_sig, "quote-denied", json!({ "quote": q.to_string() }))
                }
                Some(q) if self.exec.pump_routable(&q) => {
                    return self.skip(name, &b.mint, its_sig, "pump-routable", json!({ "quote": q.to_string() }))
                }
                _ => {}
            }
        }
        let Some(its) = b.sol_value else {
            return self.skip(name, &b.mint, its_sig, "unpriced", json!({}));
        };
        let its_sol = its as f64 / 1e9;
        if its_sol < t.min_sol {
            return self.skip(name, &b.mint, its_sig, "small", json!({ "its_sol": its_sol }));
        }
        if t.max_sol > 0.0 && its_sol > t.max_sol {
            return self.skip(name, &b.mint, its_sig, "large", json!({ "its_sol": its_sol }));
        }
        let ms = b.mint.to_string();
        // seen late: the copier fell behind its queue (a swap was waiting); its sale may already have come
        let lag = self.tip_slot.saturating_sub(slot);
        if self.cfg.max_lag_slots > 0 && self.tip_slot > 0 && lag > self.cfg.max_lag_slots {
            return self.skip(name, &b.mint, its_sig, "stale", json!({ "its_sol": its_sol, "lag_slots": lag }));
        }
        let why = if !self.cfg.kill_file.is_empty() && std::path::Path::new(&self.cfg.kill_file).exists() {
            Some("killed")
        } else if !self.feed_up {
            Some("feed-down")
        } else if self.book.iter().any(|p| p.open() && p.paper == self.exec.paper() && p.mint == ms) {
            Some("held")
        } else if self.open_count(Some(name)) >= t.max_open {
            Some("max-open")
        } else if self.open_count(None) >= self.cfg.max_open {
            Some("max-open-all")
        } else if self.day_net() <= -((self.cfg.daily_stop_sol * 1e9) as i64) {
            Some("daily-stop")
        } else {
            None
        };
        if let Some(w) = why {
            return self.skip(name, &b.mint, its_sig, w, json!({ "its_sol": its_sol }));
        }
        let stake = t.stake(its);
        if stake < 10_000_000 {
            return self.skip(name, &b.mint, its_sig, "stake-under-0.01", json!({ "its_sol": its_sol }));
        }
        // its price, lamports a unit; our quote must give at least this many units
        let its_ppu = if b.tokens > 0 { its as f64 / b.tokens as f64 } else { 0.0 };
        let min_tokens = if t.max_premium > 0.0 && its_ppu > 0.0 {
            (stake as f64 / (its_ppu * (1.0 + t.max_premium))) as u64
        } else {
            0
        };
        match self.exec.buy(&b.mint, &b.program, stake, min_tokens) {
            Ok(f) => {
                let p = Pos {
                    id: self.next_id,
                    target: name.to_string(),
                    mint: ms,
                    program: b.program.to_string(),
                    paper: self.exec.paper(),
                    its_sig: its_sig.to_string(),
                    its_sol,
                    its_ppu,
                    opened_ms: self.exec.now_ms(),
                    cost: f.lamports,
                    tokens: f.tokens,
                    buy_sig: f.sig.clone(),
                    route: f.route.clone(),
                    last_value: None,
                    last_poll_ms: 0,
                    exit: None,
                    tries: 0,
                    next_try_ms: 0,
                    closed_ms: None,
                    proceeds: None,
                    sell_sig: None,
                };
                self.next_id += 1;
                // its slot and ours (paper: the slot our quote was priced on; live: the slot our buy landed in)
                let v = json!({ "id": p.id, "target": name, "mint": p.mint, "its_sig": its_sig, "its_sol": its_sol,
                                "stake": stake, "cost": p.cost, "tokens": p.tokens, "sig": p.buy_sig, "route": p.route,
                                "its_slot": slot, "our_slot": f.slot,
                                "lag_slots": if f.slot > 0 && slot > 0 { f.slot as i64 - slot as i64 } else { -1 } });
                self.book.push(p);
                self.log("buy", v);
                self.save();
            }
            Err(e) if e.starts_with("premium") => {
                self.skip(name, &b.mint, its_sig, "premium", json!({ "its_sol": its_sol, "detail": e }));
            }
            Err(e) => {
                let v = json!({ "target": name, "mint": ms, "its_sig": its_sig, "its_sol": its_sol, "stake": stake, "why": e });
                self.log("buy-failed", v);
            }
        }
    }

    fn on_sell(&mut self, i: usize, mint: &Pubkey) {
        let t = &self.targets[i].1;
        if !t.follow_sell {
            return;
        }
        let (name, ms) = (t.name.clone(), mint.to_string());
        let now = self.exec.now_ms();
        let ks: Vec<usize> = (0..self.book.len())
            .filter(|&k| {
                let p = &self.book[k];
                p.open() && p.exit.is_none() && p.target == name && p.mint == ms
            })
            .collect();
        for k in ks {
            self.exit(k, "its-sale", now);
        }
    }

    fn target_of(&self, name: &str) -> Option<&TargetCfg> {
        self.targets.iter().map(|(_, t)| t).find(|t| t.name == name)
    }

    /// Timers, take profits and stops, and retries of failed sales.
    pub fn on_tick(&mut self) {
        let now = self.exec.now_ms();
        for k in 0..self.book.len() {
            if !self.book[k].open() {
                continue;
            }
            if let Some(r) = self.book[k].exit.clone() {
                if now >= self.book[k].next_try_ms {
                    self.exit(k, &r, now);
                }
                continue;
            }
            let (hold, tp, stop, basis) = match self.target_of(&self.book[k].target) {
                Some(t) => (t.max_hold_s, t.take_profit, t.stop, t.exit_basis),
                None => (300, 0.0, 0.0, Basis::Ours), // its target left the config: the default timer
            };
            let p = &self.book[k];
            if now.saturating_sub(p.opened_ms) >= hold * 1000 {
                self.exit(k, "timer", now);
                continue;
            }
            if (tp > 0.0 || stop > 0.0) && now.saturating_sub(p.last_poll_ms) >= self.cfg.poll_ms {
                let Ok(mint) = p.mint.parse::<Pubkey>() else { continue };
                let tokens = p.tokens;
                let v = self.exec.value(&mint, tokens);
                let p = &mut self.book[k];
                p.last_poll_ms = now;
                p.last_value = v;
                // the reference: our tokens at its price, or what we paid
                let base = match basis {
                    Basis::Its if p.its_ppu > 0.0 => p.its_ppu * p.tokens as f64,
                    _ => p.cost as f64,
                };
                if let Some(v) = v {
                    if tp > 0.0 && v as f64 >= tp * base {
                        self.exit(k, "take-profit", now);
                    } else if stop > 0.0 && v as f64 <= stop * base {
                        self.exit(k, "stop", now);
                    }
                }
            }
        }
    }

    fn exit(&mut self, k: usize, reason: &str, now: u64) {
        let (Ok(mint), Ok(program)) = (
            self.book[k].mint.parse::<Pubkey>(),
            self.book[k].program.parse::<Pubkey>(),
        ) else {
            return;
        };
        self.book[k].exit = Some(reason.to_string());
        let tokens = self.book[k].tokens;
        if self.book[k].paper && !self.exec.paper() {
            // a paper position from before the switch to mode on: the wallet never held it, so it closes as paper
            // at a sell quote and is never sold
            match self.exec.value(&mint, tokens) {
                Some(v) => {
                    let p = &mut self.book[k];
                    p.closed_ms = Some(now);
                    p.proceeds = Some(v.saturating_sub(self.cfg.paper_side_cost_lamports));
                    p.sell_sig = Some("paper".into());
                    let net = p.net().unwrap_or(0);
                    let v = json!({ "id": p.id, "target": p.target, "mint": p.mint, "reason": reason, "cost": p.cost,
                                    "proceeds": p.proceeds, "net": net, "held_s": (now - p.opened_ms) / 1000,
                                    "sig": "paper", "route": "paper, closed at a quote in mode on", "tries": p.tries,
                                    "paper": true });
                    self.log("sell", v);
                }
                None => {
                    let p = &mut self.book[k];
                    p.tries += 1;
                    p.next_try_ms = now + (2_000 * p.tries as u64).min(30_000);
                    let v = json!({ "id": p.id, "target": p.target, "mint": p.mint, "reason": reason, "tries": p.tries,
                                    "why": "no quote to close the paper position", "paper": true });
                    self.log("sell-failed", v);
                }
            }
            self.save();
            return;
        }
        match self.exec.sell(&mint, &program, tokens) {
            Ok(f) => {
                let p = &mut self.book[k];
                p.closed_ms = Some(now);
                p.proceeds = Some(f.lamports);
                p.sell_sig = Some(f.sig.clone());
                let net = p.net().unwrap_or(0);
                let mut v = json!({ "id": p.id, "target": p.target, "mint": p.mint, "reason": reason, "cost": p.cost,
                                "proceeds": f.lamports, "net": net, "held_s": (now - p.opened_ms) / 1000,
                                "sig": f.sig, "route": f.route, "tries": p.tries, "our_slot": f.slot });
                if self.its_sale_slot > 0 {
                    v["its_slot"] = json!(self.its_sale_slot);
                    if f.slot > 0 {
                        v["lag_slots"] = json!(f.slot as i64 - self.its_sale_slot as i64);
                    }
                }
                self.log("sell", v);
            }
            Err(e) => {
                let p = &mut self.book[k];
                p.tries += 1;
                p.next_try_ms = now + if p.tries >= STUCK_TRIES { 300_000 } else { (2_000 * p.tries as u64).min(30_000) };
                let v = json!({ "id": p.id, "target": p.target, "mint": p.mint, "reason": reason, "tries": p.tries, "why": e });
                let stuck = p.tries == STUCK_TRIES;
                let sv = json!({ "id": p.id, "target": p.target, "mint": p.mint, "cost": p.cost, "tries": p.tries,
                                 "why": "the sale keeps failing: retried every 5 min, its slot freed, counted as lost today; sell it by hand if it can be" });
                self.log("sell-failed", v);
                if stuck {
                    self.log("sell-stuck", sv);
                }
            }
        }
        self.save();
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashSet;

    fn fx(name: &str) -> TxLite {
        let p = format!("{}/tests/fixtures/{name}.json", env!("CARGO_MANIFEST_DIR"));
        let v: Value = serde_json::from_str(&std::fs::read_to_string(p).unwrap()).unwrap();
        TxLite::from_rpc_json(&v).unwrap()
    }
    fn pk(s: &str) -> Pubkey {
        s.parse().unwrap()
    }
    // a SOL-coin wallet on Meteora DBC, LaunchLab and the pump curve (its transactions made anonymous:
    // the wallet, its accounts, the coins and the signatures are stand-ins)
    const W2: &str = "FybV7DGJmNBLzv2ocjFAMw9pGXYaen6jLREQYbZzKwDY";
    const W4: &str = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg";
    const DBC_COIN: &str = "BJzupbveTQ2HU9zL69xB1k33RNwQ3RGg5bThASFC1gvu";
    const B_COIN: &str = "2b7vwQsm5KXoZt4scB7esv1THMgch6VaLhd8keZTpump";
    const PUMP: &str = "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn";
    fn nop(_: &Pubkey) -> Option<f64> {
        None
    }

    #[test]
    fn its_meteora_dbc_buy_is_read_from_its_balances_at_its_whole_sol_change() {
        let a = read(&fx("w2_buy_dbc"), &pk(W2), &mut nop);
        assert_eq!(a.len(), 1);
        let Act::Buy(b) = &a[0] else { panic!("{a:?}") };
        assert_eq!(b.mint, pk(DBC_COIN));
        assert_eq!(b.tokens, 155_247_045_035_106);
        // 5 SOL plus fees and tip: the 5.0 tier, under the 5.1 rule
        assert_eq!(b.sol_value, Some(5_046_493_440));
        assert!(!b.on_pump && b.pump_quote.is_none());
    }

    #[test]
    fn its_sale_on_dbc_is_a_sell_and_not_a_buy() {
        let a = read(&fx("w2_sell_dbc"), &pk(W2), &mut nop);
        assert_eq!(
            a,
            vec![Act::Sell {
                mint: pk(DBC_COIN),
                tokens: 155_247_045_035_106
            }]
        );
    }

    #[test]
    fn its_launchlab_and_pump_buys_are_buys_too() {
        let a = read(&fx("w2_buy_launchlab"), &pk(W2), &mut nop);
        assert!(matches!(&a[..], [Act::Buy(b)] if b.sol_value == Some(3_101_493_440)));
        let a = read(&fx("w2_buy_pump"), &pk(W2), &mut nop);
        let [Act::Buy(b)] = &a[..] else { panic!("{a:?}") };
        assert!(b.on_pump && b.pump_quote.is_none(), "a SOL-priced pump curve");
        assert_eq!(b.sol_value, Some(10_101_518_840));
    }

    #[test]
    fn wallet_4s_part_b_buy_is_valued_at_the_pump_it_paid() {
        let mut asked = vec![];
        let a = read(&fx("w4_buy_pump_quote"), &pk(W4), &mut |m| {
            asked.push(*m);
            Some(0.02)
        });
        let [Act::Buy(b)] = &a[..] else { panic!("{a:?}") };
        assert_eq!(b.mint, pk(B_COIN));
        assert_eq!(b.pump_quote, Some(pk(PUMP)));
        assert_eq!(asked, vec![pk(PUMP)]);
        // 23,111,280 lamports of SOL change + 35,123,113,249 PUMP units at 0.02
        assert_eq!(b.sol_value, Some(23_111_280 + 702_462_264));
        // no price for what it paid with: unpriced, not skipped silently
        let a = read(&fx("w4_buy_pump_quote"), &pk(W4), &mut nop);
        assert!(matches!(&a[..], [Act::Buy(b)] if b.sol_value.is_none()));
    }

    #[test]
    fn wallet_4s_sale_back_into_pump_is_a_sale_not_a_buy_of_pump() {
        let a = read(&fx("w4_sell_pump_quote"), &pk(W4), &mut |_| Some(0.02));
        assert_eq!(
            a,
            vec![Act::Sell {
                mint: pk(B_COIN),
                tokens: 28_699_548_051_433
            }]
        );
    }

    #[test]
    fn another_wallets_transaction_is_ignored() {
        assert!(read(&fx("w2_buy_dbc"), &pk(W4), &mut nop).is_empty());
    }

    // ---- the engine on a fake executor

    #[derive(Default)]
    struct Fake {
        live: bool,
        now: u64,
        values: HashMap<Pubkey, u64>,
        routable: HashSet<Pubkey>,
        fail_sells: u32,
        buys: Vec<(Pubkey, u64)>,
        sells: Vec<Pubkey>,
    }
    impl Exec for Fake {
        fn now_ms(&self) -> u64 {
            self.now
        }
        fn paper(&self) -> bool {
            !self.live
        }
        fn buy(&mut self, mint: &Pubkey, _: &Pubkey, lamports: u64, min_tokens: u64) -> Result<Fill, String> {
            if lamports * 10 < min_tokens {
                return Err("premium: fake".into());
            }
            self.buys.push((*mint, lamports));
            Ok(Fill { sig: "b".into(), lamports: lamports + 1_000_000, tokens: lamports * 10, route: "fake".into(), slot: 0 })
        }
        fn sell(&mut self, mint: &Pubkey, _: &Pubkey, tokens: u64) -> Result<Fill, String> {
            if self.fail_sells > 0 {
                self.fail_sells -= 1;
                return Err("no route".into());
            }
            self.sells.push(*mint);
            let v = self.values.get(mint).copied().unwrap_or(tokens / 10);
            Ok(Fill { sig: "s".into(), lamports: v, tokens, route: "fake".into(), slot: 0 })
        }
        fn value(&mut self, mint: &Pubkey, _: u64) -> Option<u64> {
            self.values.get(mint).copied()
        }
        fn price(&mut self, _: &Pubkey) -> Option<f64> {
            Some(0.02)
        }
        fn pump_routable(&mut self, q: &Pubkey) -> bool {
            self.routable.contains(q)
        }
    }

    fn cfg() -> CopierCfg {
        CopierCfg::from_toml_str(&format!(
            r#"
mode = "log"
journal = ""
state = ""
kill_file = ""
daily_stop_sol = 0.5
[[target]]
name = "w2"
wallet = "{W2}"
min_sol = 5.1
stake_sol = 0.3
max_hold_s = 300
follow_sell = true
[[target]]
name = "w4b"
wallet = "{W4}"
coins = "pump_unroutable"
min_sol = 0.5
stake_sol = 0.1
take_profit = 2.0
stop = 0.8
exit_basis = "ours"
max_hold_s = 1790
"#
        ))
        .unwrap()
    }

    fn buy(mint: &str, lamports: u64) -> Buy {
        Buy { mint: pk(mint), program: c::SPL_TOKEN_PROGRAM_ID, tokens: 1, sol_value: Some(lamports), on_pump: false, pump_quote: None }
    }

    #[test]
    fn a_5_0_tier_buy_is_skipped_under_a_5_1_floor() {
        let mut e = Copier::new(cfg(), Fake::default()).unwrap();
        e.on_tx(&fx("w2_buy_dbc")); // 5.046 SOL
        assert!(e.exec.buys.is_empty());
        assert_eq!(e.lines.last().unwrap()["why"], "small");
        e.on_buy(0, buy(DBC_COIN, 5_101_000_000), "x", 0);
        assert_eq!(e.exec.buys, vec![(pk(DBC_COIN), 300_000_000)]);
        assert_eq!(e.open_count(Some("w2")), 1);
    }

    #[test]
    fn its_sale_closes_our_position_right_behind_it() {
        let mut e = Copier::new(cfg(), Fake::default()).unwrap();
        e.on_buy(0, buy(DBC_COIN, 5_101_000_000), "x", 0);
        e.exec.now = 30_000;
        e.on_tx(&fx("w2_sell_dbc"));
        assert_eq!(e.exec.sells, vec![pk(DBC_COIN)]);
        let p = &e.book[0];
        assert_eq!(p.exit.as_deref(), Some("its-sale"));
        assert!(!p.open());
    }

    #[test]
    fn the_timer_sells_at_max_hold() {
        let mut e = Copier::new(cfg(), Fake::default()).unwrap();
        e.on_buy(0, buy(DBC_COIN, 5_101_000_000), "x", 0);
        e.exec.now = 299_000;
        e.on_tick();
        assert!(e.book[0].open());
        e.exec.now = 300_000;
        e.on_tick();
        assert_eq!(e.book[0].exit.as_deref(), Some("timer"));
        assert!(!e.book[0].open());
    }

    #[test]
    fn part_b_takes_only_unroutable_pump_quotes_and_exits_on_value() {
        let mut e = Copier::new(cfg(), Fake::default()).unwrap();
        let mut b = buy(B_COIN, 1_500_000_000);
        b.on_pump = true;
        // a SOL-priced pump coin: not part B
        e.on_buy(1, b.clone(), "x", 0);
        assert_eq!(e.lines.last().unwrap()["why"], "not-pump-unroutable");
        // a quote pump's route reaches: the long copy's (part A)
        b.pump_quote = Some(pk(PUMP));
        e.exec.routable.insert(pk(PUMP));
        e.on_buy(1, b.clone(), "x", 0);
        assert_eq!(e.lines.last().unwrap()["why"], "pump-routable");
        e.exec.routable.clear();
        e.on_buy(1, b, "x", 0);
        assert_eq!(e.exec.buys.len(), 1);
        let cost = e.book[0].cost; // 0.1 SOL + 0.001
        // valued under the stop: out
        e.exec.now = 5_000;
        e.exec.values.insert(pk(B_COIN), (cost as f64 * 0.79) as u64);
        e.on_tick();
        assert_eq!(e.book[0].exit.as_deref(), Some("stop"));
        assert!(e.book[0].net().unwrap() < 0);
    }

    #[test]
    fn a_take_profit_fires_at_twice_our_cost() {
        let mut e = Copier::new(cfg(), Fake::default()).unwrap();
        let mut b = buy(B_COIN, 1_500_000_000);
        b.on_pump = true;
        b.pump_quote = Some(pk(PUMP));
        e.on_buy(1, b, "x", 0);
        let cost = e.book[0].cost;
        e.exec.now = 3_000;
        e.exec.values.insert(pk(B_COIN), cost * 2 - 1);
        e.on_tick();
        assert!(e.book[0].open());
        e.exec.now = 6_000;
        e.exec.values.insert(pk(B_COIN), cost * 2);
        e.on_tick();
        assert_eq!(e.book[0].exit.as_deref(), Some("take-profit"));
        assert_eq!(e.book[0].net(), Some(cost as i64));
    }

    #[test]
    fn by_default_the_levels_are_multiples_of_its_price() {
        let mut c = cfg();
        c.targets[1].exit_basis = Basis::Its;
        let mut e = Copier::new(c, Fake::default()).unwrap();
        // it paid 1.5 SOL for 1,000 units: 1.5e6 lamports a unit
        let b = Buy { tokens: 1_000, pump_quote: Some(pk(PUMP)), on_pump: true, ..buy(B_COIN, 1_500_000_000) };
        e.on_buy(1, b, "x", 0);
        let p = e.book[0].clone();
        assert!((p.its_ppu - 1_500_000.0).abs() < 1e-6);
        // our tokens (fake: stake x 10) at twice its price
        let at_2x = (2.0 * p.its_ppu * p.tokens as f64) as u64;
        e.exec.now = 3_000;
        e.exec.values.insert(pk(B_COIN), at_2x - 1);
        e.on_tick();
        assert!(e.book[0].open());
        e.exec.now = 6_000;
        e.exec.values.insert(pk(B_COIN), at_2x + 1);
        e.on_tick();
        assert_eq!(e.book[0].exit.as_deref(), Some("take-profit"));
    }

    #[test]
    fn a_buy_priced_far_over_its_price_is_skipped() {
        let mut c = cfg();
        c.targets[1].max_premium = 0.3;
        let mut e = Copier::new(c, Fake::default()).unwrap();
        // the fake fills at 0.1 lamports a unit; it paid 0.1 (premium 0): copied
        let b = Buy { tokens: 15_000_000_000, pump_quote: Some(pk(PUMP)), on_pump: true, ..buy(B_COIN, 1_500_000_000) };
        e.on_buy(1, b, "x", 0);
        assert_eq!(e.exec.buys.len(), 1);
        // it paid 0.05 (we would pay twice its price): skipped
        let other = "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU";
        let b = Buy { tokens: 30_000_000_000, pump_quote: Some(pk(PUMP)), on_pump: true, ..buy(other, 1_500_000_000) };
        e.on_buy(1, b, "y", 0);
        assert_eq!(e.exec.buys.len(), 1);
        assert_eq!(e.open_count(Some("w4b")), 1);
    }

    #[test]
    fn a_failed_sale_is_retried_until_it_lands() {
        let mut e = Copier::new(cfg(), Fake::default()).unwrap();
        e.on_buy(0, buy(DBC_COIN, 5_101_000_000), "x", 0);
        e.exec.fail_sells = 2;
        e.exec.now = 300_000;
        e.on_tick();
        assert!(e.book[0].open() && e.book[0].tries == 1);
        e.exec.now = 301_000; // before the 2 s back-off
        e.on_tick();
        assert_eq!(e.book[0].tries, 1);
        e.exec.now = 302_000;
        e.on_tick();
        assert_eq!(e.book[0].tries, 2);
        e.exec.now = 310_000;
        e.on_tick();
        assert!(!e.book[0].open());
        assert_eq!(e.book[0].exit.as_deref(), Some("timer"));
    }

    #[test]
    fn max_open_held_coins_and_the_daily_stop_hold_buys_back() {
        let mut e = Copier::new(cfg(), Fake::default()).unwrap();
        for (i, m) in ["11111111111111111111111111111112", "11111111111111111111111111111113", "11111111111111111111111111111114", "11111111111111111111111111111115"].iter().enumerate() {
            e.on_buy(0, buy(m, 5_200_000_000 + i as u64), "x", 0);
        }
        assert_eq!(e.exec.buys.len(), 3, "w2 max_open 3");
        assert_eq!(e.lines.last().unwrap()["why"], "max-open");
        e.on_buy(1, Buy { pump_quote: Some(pk(PUMP)), on_pump: true, ..buy("11111111111111111111111111111112", 1_500_000_000) }, "x", 0);
        assert_eq!(e.lines.last().unwrap()["why"], "held");
        // close the three at a loss of 0.2 SOL each: past the 0.5 daily stop
        for m in ["11111111111111111111111111111112", "11111111111111111111111111111113", "11111111111111111111111111111114"] {
            e.exec.values.insert(pk(m), 100_000_000);
        }
        e.exec.now = 300_000;
        e.on_tick();
        assert!(e.day_net() < -500_000_000);
        e.on_buy(0, buy("11111111111111111111111111111116", 5_200_000_000), "x", 0);
        assert_eq!(e.lines.last().unwrap()["why"], "daily-stop");
    }

    #[test]
    fn the_kill_file_stops_new_buys_but_not_exits() {
        let k = std::env::temp_dir().join(format!("copier-kill-{}", std::process::id()));
        let mut c = cfg();
        c.kill_file = k.to_string_lossy().into_owned();
        let mut e = Copier::new(c, Fake::default()).unwrap();
        e.on_buy(0, buy(DBC_COIN, 5_200_000_000), "x", 0);
        std::fs::write(&k, b"").unwrap();
        e.on_buy(0, buy("11111111111111111111111111111112", 5_200_000_000), "x", 0);
        assert_eq!(e.lines.last().unwrap()["why"], "killed");
        e.exec.now = 300_000;
        e.on_tick();
        assert!(!e.book[0].open(), "the open position still exits");
        let _ = std::fs::remove_file(k);
    }

    #[test]
    fn no_buys_while_the_feed_is_down() {
        let mut e = Copier::new(cfg(), Fake::default()).unwrap();
        e.set_feed(false);
        e.on_buy(0, buy(DBC_COIN, 5_200_000_000), "x", 0);
        assert_eq!(e.lines.last().unwrap()["why"], "feed-down");
    }

    #[test]
    fn a_restart_picks_up_the_open_positions() {
        let dir = std::env::temp_dir().join(format!("copier-state-{}", std::process::id()));
        let mut c = cfg();
        c.state = dir.to_string_lossy().into_owned();
        let mut e = Copier::new(c.clone(), Fake::default()).unwrap();
        e.on_buy(0, buy(DBC_COIN, 5_200_000_000), "x", 0);
        let mut e2 = Copier::new(c, Fake::default()).unwrap();
        assert_eq!(e2.load_state().unwrap(), 1);
        assert_eq!(e2.book[0].mint, DBC_COIN);
        e2.exec.now = 300_000;
        e2.on_tick();
        assert!(!e2.book[0].open());
        let _ = std::fs::remove_file(dir);
    }

    #[test]
    fn after_the_switch_to_mode_on_a_paper_position_closes_as_paper_and_blocks_nothing() {
        let dir = std::env::temp_dir().join(format!("copier-switch-{}", std::process::id()));
        let mut c = cfg();
        c.state = dir.to_string_lossy().into_owned();
        c.targets[0].max_open = 1;
        let mut e = Copier::new(c.clone(), Fake::default()).unwrap();
        e.on_buy(0, buy(DBC_COIN, 5_200_000_000), "x", 0); // paper
        // mode on: the paper position is loaded, but neither the cap nor the daily stop counts it
        let mut live = Copier::new(c.clone(), Fake { live: true, ..Fake::default() }).unwrap();
        assert_eq!(live.load_state().unwrap(), 1);
        assert_eq!(live.open_count(Some("w2")), 0);
        let other = "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU";
        live.on_buy(0, buy(other, 5_200_000_000), "y", 0);
        assert_eq!(live.exec.buys.len(), 1, "the real buy is not held back by the paper one");
        // its timer: the paper one closes at a quote, never through a real sale
        live.exec.values.insert(pk(DBC_COIN), 250_000_000);
        live.exec.values.insert(pk(other), 300_000_000);
        live.exec.now = 300_000;
        live.on_tick();
        assert!(!live.book[0].open() && live.book[0].paper);
        assert_eq!(live.exec.sells, vec![pk(other)], "only the real position is sold");
        let closed = live.lines.iter().find(|l| l["ev"] == "sell" && l["mint"] == DBC_COIN).unwrap();
        assert_eq!(closed["paper"], true);
        // back to paper while the real one is open: refused (here it closed, so a new real one is opened by hand)
        let _ = std::fs::remove_file(&dir);
        let mut live2 = Copier::new(c.clone(), Fake { live: true, ..Fake::default() }).unwrap();
        live2.on_buy(0, buy(other, 5_200_000_000), "z", 0);
        assert!(Copier::new(c, Fake::default()).unwrap().load_state().is_err());
        let _ = std::fs::remove_file(dir);
    }

    #[test]
    fn a_buy_seen_after_the_queue_fell_behind_is_not_copied() {
        let mut e = Copier::new(cfg(), Fake::default()).unwrap();
        e.tip_slot = 1_000;
        e.on_buy(0, buy(DBC_COIN, 5_101_000_000), "x", 989); // 11 slots behind the feed: stale
        assert!(e.book.is_empty());
        assert_eq!(e.lines.last().unwrap()["why"], "stale");
        e.on_buy(0, buy(DBC_COIN, 5_101_000_000), "x", 990); // 10 behind: copied
        assert_eq!(e.book.len(), 1);
    }

    #[test]
    fn a_sale_that_keeps_failing_frees_its_slot_and_counts_as_lost() {
        let mut e = Copier::new(cfg(), Fake::default()).unwrap();
        e.on_buy(0, buy(DBC_COIN, 5_101_000_000), "x", 0);
        let cost = e.book[0].cost as i64;
        e.exec.fail_sells = 1_000;
        let mut now = 300_000;
        for _ in 0..STUCK_TRIES {
            e.exec.now = now;
            e.on_tick();
            now += 31_000;
        }
        assert!(e.book[0].open() && e.book[0].stuck());
        assert_eq!(e.lines.iter().filter(|l| l["ev"] == "sell-stuck").count(), 1);
        assert_eq!(e.open_count(Some("w2")), 0);
        assert_eq!(e.day_net(), -cost);
        // the slot is free for its next buy, and the stuck sale is still retried, every 5 min
        e.on_buy(0, buy("11111111111111111111111111111112", 5_200_000_000), "y", 0);
        assert_eq!(e.open_count(Some("w2")), 1);
        let t = e.book[0].tries;
        e.exec.now = now + 200_000;
        e.on_tick();
        assert_eq!(e.book[0].tries, t);
        e.exec.now = now + 300_000;
        e.on_tick();
        assert_eq!(e.book[0].tries, t + 1);
    }

    #[test]
    fn the_example_config_loads_with_the_4_sol_plan() {
        let text = include_str!("../../../config/copier.example.toml");
        let c = CopierCfg::from_toml_str(text).unwrap();
        assert_eq!(c.mode, Mode::Log);
        assert_eq!(c.targets.len(), 1, "part B is commented out");
        let r = &c.targets[0];
        assert_eq!((r.name.as_str(), r.coins, r.min_sol, r.max_hold_s), ("rafinha", Coins::Any, 5.0, 300));
        assert_eq!((r.stake(5_100_000_000), r.max_open, r.follow_sell), (1_000_000_000, 1, true));
        assert_eq!((r.take_profit, r.stop, r.max_premium), (0.0, 0.0, 0.0));
        // part B's block, uncommented, is a valid target with the scored exits
        let b: String = text
            .split("# [[target]]\n# name = \"w4b\"")
            .nth(1)
            .unwrap()
            .lines()
            .map(|l| l.strip_prefix("# ").unwrap_or(l))
            .collect::<Vec<_>>()
            .join("\n");
        let c2 = CopierCfg::from_toml_str(&format!("[[target]]\nname = \"w4b\"{b}")).unwrap();
        let w = &c2.targets[0];
        assert_eq!((w.coins, w.exit_basis, w.follow_sell), (Coins::PumpUnroutable, Basis::Ours, false));
        assert_eq!((w.min_sol, w.take_profit, w.stop, w.max_hold_s), (1.45, 2.0, 0.8, 1790));
        assert_eq!(w.stake(1_500_000_000), 100_000_000);
    }

    #[test]
    fn the_config_refuses_bad_values() {
        let bad = |extra: &str| {
            CopierCfg::from_toml_str(&format!("[[target]]\nname = \"a\"\nwallet = \"{W2}\"\n{extra}")).is_err()
        };
        assert!(bad("take_profit = 0.9"));
        assert!(bad("stop = 1.2"));
        assert!(bad("stake_sol = 0.0"));
        assert!(bad("max_hold_s = 0"));
        assert!(!bad(""));
        assert!(CopierCfg::from_toml_str("mode = \"log\"").is_err(), "no target");
        let top = |head: &str| {
            CopierCfg::from_toml_str(&format!("{head}\n[[target]]\nname = \"a\"\nwallet = \"{W2}\"\n")).is_err()
        };
        assert!(top("senders = [\"nozomi\"]"), "a sender without a Jito tip");
        assert!(top("jito_tip_lamports = 0"), "jito without a tip");
        assert!(!top("senders = []\njito_tip_lamports = 0"), "rpc only, priority fee");
        let t = TargetCfg { stake_frac: 0.1, stake_cap_sol: 0.3, ..Default::default() };
        assert_eq!(t.stake(5_100_000_000), 300_000_000);
        assert_eq!(t.stake(2_000_000_000), 200_000_000);
    }
}
