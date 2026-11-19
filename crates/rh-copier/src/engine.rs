//! The decisions, without any I/O (unit-tested in tests/engine.rs). Fed every Pons curve trade the feed sees and a
//! clock tick; returns actions for the executor (buy, sell). Mirrors the research model
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
    pub net_q: f64,     // ETH the curve's reserve gained (a buy: quoteIn - fee - tax) or lost (a sale: quoteOut + fee + tax)
    pub tokens: f64,    // whole tokens
    pub block: u64,
    pub t_ms: u64,      // when we saw it
}

#[derive(Clone, Debug, PartialEq)]
pub enum Action {
    Buy { curve: String, leader: String, eth: f64, min_tokens: f64 },
    Sell { curve: String, tokens: f64, min_eth: f64, why: &'static str },
}

#[derive(Clone, Copy, Debug, Default)]
pub struct CurveSt {
    pub q: f64,      // virtual quote reserve, ETH
    pub t: f64,      // virtual token reserve, tokens
    pub real_q: f64, // real quote in the curve, ETH (graduation at 4.2 for ETH-quoted coins)
}
/// An ETH-quoted Pons curve (measured on Nov 18 from reserves before and after single trades): virtual quote x virtual
/// tokens = 1.68e9 exactly, starting at 1.68 ETH and 1B tokens; the fee and the creator's tax come out of the quote.
/// Curves quoted in other tokens have other constants (one seen: 147.6 x 1e9, graduating at 369).
pub const V0: f64 = 1.68;
pub const K: f64 = 1.68e9;
impl CurveSt {
    pub fn price(&self) -> f64 { if self.t > 0.0 { self.q / self.t } else { 0.0 } }
    fn apply(&mut self, tr: &Trade) {
        if tr.buy { self.q += tr.net_q; self.real_q += tr.net_q; self.t -= tr.tokens } else { self.q -= tr.net_q; self.real_q -= tr.net_q; self.t += tr.tokens }
    }
    /// The curve right after a buy, from the buy alone (no read): with q·t = K, the net quote dq and the tokens n out,
    /// the quote before q0 solves n = K/q0 - K/(q0 + dq), i.e. q0² + dq·q0 - K·dq/n = 0. None when the buy does not fit
    /// an ETH curve (another quote token, or bad numbers): such a coin is not copied.
    pub fn after_buy(tr: &Trade) -> Option<CurveSt> {
        let (dq, n) = (tr.net_q, tr.tokens);
        if !tr.buy || !(dq > 0.0) || !(n > 0.0) { return None }
        let q0 = (-dq + (dq * dq + 4.0 * K * dq / n).sqrt()) / 2.0;
        let q = q0 + dq; let real = q - V0;
        if !(q0 >= V0 * 0.999 && real <= 4.21) { return None }
        Some(CurveSt { q, t: K / q, real_q: real.max(0.0) })
    }
    /// tokens out for `eth` in (the fee and the creator's tax, 2-3% of the quote, come out of the quote)
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
    pub our_block: u64, // the block our buy landed in (0 = not yet / paper)
    pub its_price: f64,
    pub its_ms: u64,
    pub eth_in: f64,
    pub tokens: f64,
    pub peak: f64,     // the best price / its price seen
    pub hi_ms: u64,    // when the peak was set
    pub state: PosState,
    pub flow: VecDeque<(u64, bool)>, // (ms, sell) of the other traders on the curve, for sell pressure
    pub retry_ms: u64, // after a failed sale: no new try before this
    pub sell_fails: u32, // failed sale rounds so far: the wait before the next grows (5, 10, 20, 40, then 60 s)
}

pub struct Engine {
    pub cfg: Config,
    me: String,
    pub curves: HashMap<String, CurveSt>,
    pub pos: HashMap<String, Position>,
    seen: HashMap<String, u64>, // curves a leader bought: never a second copy of a coin (ms)
    pub day: u64,
    pub day_pnl: f64,
}

pub const FEE: f64 = 0.03; // the curve fee + the creator's tax a buy or sale pays (measured: about 3% on Nov 18)

impl Engine {
    pub fn new(cfg: Config, me: &str) -> Self {
        Engine { cfg, me: me.to_lowercase(), curves: HashMap::new(), pos: HashMap::new(), seen: HashMap::new(), day: 0, day_pnl: 0.0 }
    }
    fn leader(&self, a: &str) -> Option<&Leader> { self.cfg.leaders.iter().find(|l| l.address.eq_ignore_ascii_case(a)) }
    fn open_count(&self) -> usize { self.pos.len() }
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
        if tr.quote < l.min_its_eth || self.seen.contains_key(&tr.curve) || self.pos.contains_key(&tr.curve) { return None }
        if self.open_count() >= self.cfg.max_open || self.stopped() { log(&format!("skip {} of {}: {}", short(&tr.curve), short(&l.address), if self.stopped() { "daily stop" } else { "max_open" })); return None }
        // the curve right after its buy, from its buy itself (no read): its price exactly, at once
        let Some(c) = CurveSt::after_buy(tr) else { log(&format!("skip {} of {}: not an ETH-quoted curve", short(&tr.curve), short(&l.address))); return None };
        self.curves.insert(tr.curve.clone(), c);
        // the coin counts as seen only once it is copied: a skip by one wallet's filter must not block another wallet's
        // copy of the same coin (Nov 19 00:44 UTC: wallet 1's buy, over its coin-type limit, hid wallet 3's in the same block)
        let a = self.decide(l, &tr.curve, c, now_ms, tr.net_q, tr.quote, tr.block);
        if a.is_some() { self.seen.insert(tr.curve.clone(), now_ms); }
        a
    }

    /// the reserves of a held curve read from the chain (the 15 s refresh, and after a restart)
    pub fn set_curve(&mut self, curve: &str, st: CurveSt) { self.curves.insert(curve.to_string(), st); }

    /// `at_its` = the curve right after its buy; `its_net` its net quote in, `its_quote` its quoteIn
    fn decide(&mut self, l: &Leader, curve: &str, at_its: CurveSt, its_ms: u64, its_net: f64, its_quote: f64, its_block: u64) -> Option<Action> {
        let c = at_its;
        // the coin type: ETH in the curve before its buy
        let before = at_its.real_q - its_net;
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
        self.pos.insert(curve.to_string(), Position { id: 0, curve: curve.to_string(), leader: l.address.to_lowercase(), its_eth: its_quote, its_block, our_block: 0, its_price, its_ms, eth_in: eth, tokens: 0.0,
            peak: 1.0, hi_ms: its_ms, state: PosState::Buying, flow: VecDeque::new(), retry_ms: 0, sell_fails: 0 });
        Some(Action::Buy { curve: curve.to_string(), leader: l.address.to_lowercase(), eth, min_tokens })
    }

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
            None => {
                if let Some(p) = self.pos.get_mut(curve) {
                    p.state = PosState::Open; p.sell_fails += 1; p.retry_ms = now_ms + (5_000u64 << (p.sell_fails - 1).min(4)).min(60_000)
                }
                None
            }
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
