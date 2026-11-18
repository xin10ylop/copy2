//! The decisions, without any I/O (unit-tested in tests/engine.rs). Fed every Pons curve trade the feed sees and a
//! clock tick; returns actions for the executor (fetch a curve's reserves, buy, sell). Mirrors the research model
//! (analysis/research/2026-11-18/robinhood/rh6_engineer.py): prices are the curve's marginal price (quote reserve /
//! token reserve, both virtual), "its price" is the price its buy left, and every exit is measured against it;
//! the age of a position counts from its buy.
use crate::config::{Config, Leader};
use std::collections::{HashMap, VecDeque};

/// One curve trade as the feed decodes it (CurveBuy / CurveSell of a Pons V2 curve).
#[derive(Clone, Debug, PartialEq)]
pub struct Trade {
    pub curve: String,  // the curve contract, lowercase 0x hex
    pub buy: bool,
    pub user: String,   // a buy's recipient, a sale's seller (lowercase)
    pub quote: f64,     // ETH: a buy's quoteIn, a sale's quoteOut
    pub tokens: f64,    // whole tokens
    pub block: u64,
    pub t_ms: u64,      // when we saw it
}

#[derive(Clone, Debug, PartialEq)]
pub enum Action {
    /// read quoteReserve / tokenReserve / realQuoteReserve of this curve now and at the end of `block` (its buy's),
    /// then call `set_signal`
    FetchCurve { curve: String, block: u64 },
    Buy { curve: String, leader: String, eth: f64, min_tokens: f64 },
    Sell { curve: String, tokens: f64, min_eth: f64, why: &'static str },
}

#[derive(Clone, Copy, Debug, Default)]
pub struct CurveSt {
    pub q: f64,      // virtual quote reserve, ETH
    pub t: f64,      // virtual token reserve, tokens
    pub real_q: f64, // real quote in the curve, ETH (graduation at 4.2 for ETH-quoted coins)
}
impl CurveSt {
    pub fn price(&self) -> f64 { if self.t > 0.0 { self.q / self.t } else { 0.0 } }
    fn apply(&mut self, tr: &Trade) {
        if tr.buy { self.q += tr.quote; self.real_q += tr.quote; self.t -= tr.tokens } else { self.q -= tr.quote; self.real_q -= tr.quote; self.t += tr.tokens }
    }
    /// tokens out for `eth` in (fees and the creator's tax are about 3% of the quote, taken from the tokens)
    pub fn tokens_for(&self, eth: f64, fee: f64) -> f64 { let net = eth * (1.0 - fee); self.t - self.t * self.q / (self.q + net) }
    pub fn eth_for(&self, tokens: f64, fee: f64) -> f64 { (self.q - self.q * self.t / (self.t + tokens)) * (1.0 - fee) }
}

#[derive(Clone, Debug, PartialEq)]
pub enum PosState { Buying, Open, Selling }

#[derive(Clone, Debug)]
pub struct Position {
    pub id: u64,       // set by the executor (the journal's #)
    pub curve: String,
    pub leader: String,
    pub its_eth: f64,  // its buy, ETH
    pub its_block: u64,
    pub its_price: f64,
    pub its_ms: u64,
    pub eth_in: f64,
    pub tokens: f64,
    pub peak: f64,     // the best price / its price seen
    pub hi_ms: u64,    // when the peak was set
    pub state: PosState,
    pub flow: VecDeque<(u64, bool)>, // (ms, sell) of the other traders on the curve, for sell pressure
    pub retry_ms: u64, // after a failed sale: no new try before this
}

/// A leader's buy waiting for the curve's reserves
#[derive(Clone, Debug)]
struct Pending { leader: String, its_ms: u64, its_quote: f64, block: u64 }

pub struct Engine {
    pub cfg: Config,
    me: String,
    pub curves: HashMap<String, CurveSt>,
    pub pos: HashMap<String, Position>,
    pending: HashMap<String, Pending>,
    seen: HashMap<String, u64>, // curves a leader bought: never a second copy of a coin (ms)
    pub day: u64,
    pub day_pnl: f64,
}

pub const FEE: f64 = 0.03; // the curve fee + the creator's tax a buy or sale pays (measured: about 3% on Nov 18)

impl Engine {
    pub fn new(cfg: Config, me: &str) -> Self {
        Engine { cfg, me: me.to_lowercase(), curves: HashMap::new(), pos: HashMap::new(), pending: HashMap::new(), seen: HashMap::new(), day: 0, day_pnl: 0.0 }
    }
    fn leader(&self, a: &str) -> Option<&Leader> { self.cfg.leaders.iter().find(|l| l.address.eq_ignore_ascii_case(a)) }
    fn open_count(&self) -> usize { self.pos.len() + self.pending.len() }
    fn stopped(&self) -> bool { self.cfg.daily_stop_eth > 0.0 && self.day_pnl <= -self.cfg.daily_stop_eth }

    /// Every curve trade the feed sees.
    pub fn on_trade(&mut self, tr: &Trade, now_ms: u64) -> Vec<Action> {
        let mut out = vec![];
        if let Some(c) = self.curves.get_mut(&tr.curve) { c.apply(tr) }
        // a leader's buy: a copy candidate
        if tr.buy && tr.user != self.me {
            if let Some(l) = self.leader(&tr.user).cloned() {
                if let Some(a) = self.consider(&l, tr, now_ms) { out.push(a) }
            }
        }
        // a position on this curve: its flow, then the exits
        let mut its_sold = None;
        if let Some(p) = self.pos.get_mut(&tr.curve) {
            if tr.user != self.me && !tr.user.eq_ignore_ascii_case(&p.leader) { p.flow.push_back((tr.t_ms, !tr.buy)) }
            if !tr.buy && tr.user.eq_ignore_ascii_case(&p.leader) { its_sold = Some(p.leader.clone()) }
        }
        if let Some(ld) = its_sold {
            if let Some(l) = self.leader(&ld).cloned() {
                if let Some(a) = self.its_sale(&l, &tr.curve, now_ms) { out.push(a); return out }
            }
        }
        if let Some(a) = self.exit(&tr.curve, now_ms) { out.push(a) }
        out
    }

    fn consider(&mut self, l: &Leader, tr: &Trade, now_ms: u64) -> Option<Action> {
        if tr.quote < l.min_its_eth || self.seen.contains_key(&tr.curve) || self.pos.contains_key(&tr.curve) || self.pending.contains_key(&tr.curve) { return None }
        if self.open_count() >= self.cfg.max_open || self.stopped() { log(&format!("skip {} of {}: {}", short(&tr.curve), short(&l.address), if self.stopped() { "daily stop" } else { "max_open" })); return None }
        self.seen.insert(tr.curve.clone(), now_ms);
        match self.curves.get(&tr.curve).copied() {
            Some(c) => self.decide(l, &tr.curve, c, c, now_ms, tr.quote, tr.block),
            None => { self.pending.insert(tr.curve.clone(), Pending { leader: l.address.to_lowercase(), its_ms: now_ms, its_quote: tr.quote, block: tr.block }); Some(Action::FetchCurve { curve: tr.curve.clone(), block: tr.block }) }
        }
    }

    /// the reserves of a curve read from the chain now (a refresh, or a signal's reserves when only these are known)
    pub fn set_curve(&mut self, curve: &str, st: CurveSt, now_ms: u64) -> Vec<Action> { self.set_signal(curve, st, st, now_ms) }
    /// a signal's reserves: `now` = the latest block's, `at_its` = at the end of its buy's block (its price)
    pub fn set_signal(&mut self, curve: &str, now: CurveSt, at_its: CurveSt, now_ms: u64) -> Vec<Action> {
        self.curves.insert(curve.to_string(), now);
        let _ = now_ms;
        let Some(p) = self.pending.remove(curve) else { return vec![] };
        let Some(l) = self.leader(&p.leader).cloned() else { return vec![] };
        self.decide(&l, curve, now, at_its, p.its_ms, p.its_quote, p.block).into_iter().collect()
    }

    fn decide(&mut self, l: &Leader, curve: &str, c: CurveSt, at_its: CurveSt, its_ms: u64, its_quote: f64, its_block: u64) -> Option<Action> {
        // the coin type: ETH in the curve before its buy
        let before = at_its.real_q - its_quote;
        if l.max_curve_eth > 0.0 && before >= l.max_curve_eth { log(&format!("skip {} of {}: {:.3} ETH in the curve before its buy (max {})", short(curve), short(&l.address), before, l.max_curve_eth)); return None }
        if c.real_q >= self.cfg.grad_guard_eth { log(&format!("skip {}: {:.3} ETH in the curve, near graduation", short(curve), c.real_q)); return None }
        let its_price = at_its.price();
        let lim = if l.max_premium > 0.0 { l.max_premium } else { 3.0 };
        if c.price() > lim * its_price { log(&format!("skip {} of {}: the price is already {:.2}x its price (limit {lim})", short(curve), short(&l.address), c.price() / its_price)); return None }
        let eth = self.cfg.stake_eth;
        // the minimum tokens: what the stake buys at the limit price (the curve moved to lim x its price: t / sqrt(lim)),
        // less 1% for the fee's rounding; without a limit, also no less than the expected amount less `slippage`
        let r = lim.sqrt(); let at_lim = CurveSt { q: at_its.q * r, t: at_its.t / r, real_q: 0.0 };
        let mut min_tokens = at_lim.tokens_for(eth, FEE) * 0.99;
        if l.max_premium <= 0.0 { min_tokens = min_tokens.max(c.tokens_for(eth, FEE) * (1.0 - self.cfg.slippage)) }
        self.pos.insert(curve.to_string(), Position { id: 0, curve: curve.to_string(), leader: l.address.to_lowercase(), its_eth: its_quote, its_block, its_price, its_ms, eth_in: eth, tokens: 0.0,
            peak: 1.0, hi_ms: its_ms, state: PosState::Buying, flow: VecDeque::new(), retry_ms: 0 });
        Some(Action::Buy { curve: curve.to_string(), leader: l.address.to_lowercase(), eth, min_tokens })
    }

    /// the reserves could not be read: the signal is dropped (the coin stays seen: no late copy)
    pub fn drop_pending(&mut self, curve: &str) { self.pending.remove(curve); }
    /// our buy landed (tokens received) or failed (tokens = 0)
    pub fn on_bought(&mut self, curve: &str, tokens: f64, now_ms: u64) {
        if tokens <= 0.0 { self.pos.remove(curve); return }
        if let Some(p) = self.pos.get_mut(curve) { p.tokens = tokens; p.state = PosState::Open; let _ = now_ms; }
    }
    /// our sale landed (ETH received) or failed (None: the position goes back to Open, the next trade or tick retries)
    pub fn on_sold(&mut self, curve: &str, eth_out: Option<f64>, now_ms: u64) -> Option<f64> { self.on_sold_pos(curve, eth_out, now_ms).map(|(p, _)| p) }
    /// as `on_sold`, with the closed position
    pub fn on_sold_pos(&mut self, curve: &str, eth_out: Option<f64>, now_ms: u64) -> Option<(f64, Position)> {
        match eth_out {
            Some(e) => { let p = self.pos.remove(curve)?; let pnl = e - p.eth_in; self.book(pnl, now_ms); Some((pnl, p)) }
            None => { if let Some(p) = self.pos.get_mut(curve) { p.state = PosState::Open; p.retry_ms = now_ms + 5_000 } None }
        }
    }
    fn book(&mut self, pnl: f64, now_ms: u64) {
        let d = now_ms / 86_400_000;
        if d != self.day { self.day = d; self.day_pnl = 0.0 }
        self.day_pnl += pnl;
    }

    fn its_sale(&mut self, l: &Leader, curve: &str, now_ms: u64) -> Option<Action> {
        let c = *self.curves.get(curve)?; let p = self.pos.get(curve)?;
        if p.state != PosState::Open { return None }
        let age = now_ms.saturating_sub(p.its_ms) as f64 / 1000.0; let ratio = c.price() / p.its_price;
        let go = match l.its_sale.as_str() { "always" => true, "early" => (30.0..290.0).contains(&age) && ratio < 1.5, _ => false };
        if go { self.sell(curve, "its_sell", now_ms) } else { None }
    }

    /// The exits of one position, in the research model's order: graduation guard, take profit, sell pressure,
    /// stall, time.
    fn exit(&mut self, curve: &str, now_ms: u64) -> Option<Action> {
        let c = *self.curves.get(curve)?;
        let (why, ok) = {
            let p = self.pos.get_mut(curve)?;
            if p.state != PosState::Open { return None }
            let l = self.cfg.leaders.iter().find(|l| l.address.eq_ignore_ascii_case(&p.leader))?.clone();
            let age = now_ms.saturating_sub(p.its_ms) as f64 / 1000.0; let ratio = c.price() / p.its_price;
            if ratio > p.peak { p.peak = ratio; p.hi_ms = now_ms }
            if l.sell_pressure.len() == 3 {
                let w = l.sell_pressure[1] * 1000; while p.flow.front().is_some_and(|(t, _)| *t + w < now_ms) { p.flow.pop_front(); }
            }
            let pressure = l.sell_pressure.len() == 3 && age >= l.sell_pressure[2] as f64
                && p.flow.iter().map(|(_, s)| if *s { 1i64 } else { -1 }).sum::<i64>() >= l.sell_pressure[0] as i64;
            let stall = l.stall_s > 0 && p.peak >= 1.0 && now_ms.saturating_sub(p.hi_ms) >= l.stall_s * 1000;
            if c.real_q >= self.cfg.grad_guard_eth { ("graduation_guard", true) }
            else if l.take_profit > 0.0 && ratio >= l.take_profit { ("take_profit", true) }
            else if pressure { ("sell_pressure", true) }
            else if stall { ("stall", true) }
            else if age >= l.hold_s as f64 { ("time", true) }
            else { ("", false) }
        };
        if ok { self.sell(curve, why, now_ms) } else { None }
    }
    fn sell(&mut self, curve: &str, why: &'static str, now_ms: u64) -> Option<Action> {
        let c = *self.curves.get(curve)?; let p = self.pos.get_mut(curve)?;
        if p.state != PosState::Open || p.tokens <= 0.0 { return None }
        if now_ms < p.retry_ms { return None }
        p.state = PosState::Selling;
        Some(Action::Sell { curve: curve.to_string(), tokens: p.tokens, min_eth: c.eth_for(p.tokens, FEE) * (1.0 - self.cfg.sell_slippage), why })
    }

    /// The clock: time exits and stalls on quiet curves; forgets old "seen" coins.
    pub fn tick(&mut self, now_ms: u64) -> Vec<Action> {
        self.seen.retain(|_, t| *t + 3_600_000 > now_ms);
        let curves: Vec<String> = self.pos.keys().cloned().collect();
        curves.iter().filter_map(|c| self.exit(c, now_ms)).collect()
    }
}

pub fn short(a: &str) -> String { a.chars().take(10).collect() }
pub fn log(s: &str) { println!("rh {s}") }
