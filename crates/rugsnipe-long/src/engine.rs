//! The loop: triggers, fills, exits and the book. One thread; the feed and
//! the oracle run on their own. Chain reads (blockhash, statuses, a new
//! quote token's pool) are blocking RPC calls on this thread, tens of ms
//! each.
//!
//! **Accounting is chain-true on a real position**: its result is the sum
//! of our wallet's lamport changes over its transactions (buy, sells, the
//! failed ones) plus the anchor's token changes valued at the oracle price
//! when the anchor is a float. A paper position is priced on the live curve
//! with our tokens added (the curve as it would be with us in it), the
//! route's other hops at its own fill's rate, and the fees we would pay.

use crate::chain::{Blockhashes, Rpc};
use crate::config::{LongCfg, Mode};
use crate::detect::{self, Seen, Trigger};
use crate::feed::{FeedHandle, FeedMsg, Src};
use crate::oracle::{now_ms, Oracle};
use crate::pos::{self, Book, Position, Reason, State};
use crate::route;
use crate::send::Out;
use crate::txb::{self, Fees};
use crate::txlite::TxLite;
use pump_codec::constants as c;
use pump_codec::Pubkey;
use rugsnipe_tx::senders::VariantKind;
use rugsnipe_tx::signer::HotSigner;
use std::collections::{BTreeSet, HashMap};
use std::io::Write as _;
use std::path::PathBuf;
use std::sync::mpsc;
use std::time::Duration;

/// Pump's curve fee on coins priced in other tokens (estimate for bounds
/// and paper; the real fee is in the chain-true result).
const CURVE_FEE_BPS: u32 = 125;
/// A buy not seen landed after this is asked for by signature.
const BUY_WAIT_MS: u64 = 20_000;
const SELL_WAIT_MS: u64 = 15_000;
/// An unseen transaction is asked for at most this often (2026-10-28: it
/// was asked for on every tick, a blocking call several times a second).
const CHASE_EVERY_MS: u64 = 2_500;
/// A transaction not seen this long after its send is given up (the
/// blockhash is past its life).
const DROP_AFTER_MS: u64 = 90_000;
/// A cached blockhash older than this is not used.
const BLOCKHASH_MAX_AGE_MS: u64 = 20_000;

pub struct Engine {
    pub cfg: LongCfg,
    me: Pubkey,
    signer: Option<HotSigner>,
    rpc: Rpc,
    /// Refreshed on its own thread in real mode (`set_blockhashes`).
    bh: Blockhashes,
    oracle: Oracle,
    out_buy: Option<Out>,
    out_sell: Option<Out>,
    feed: Option<FeedHandle>,
    pub book: Book,
    book_path: PathBuf,
    closed_path: PathBuf,
    anchors: Vec<Pubkey>,
    copy: Pubkey,
    slot: u64,
    blockhash: Option<([u8; 32], u64)>,
    its_bought: HashMap<Pubkey, u64>,
    sol_balance: u64,
    floats: HashMap<Pubkey, u64>,
    last_refresh_ms: u64,
    last_save_ms: u64,
    watched: BTreeSet<Pubkey>,
    buyback_rr: usize,
}

fn m8(k: &Pubkey) -> String {
    k.to_string()[..8].to_string()
}

fn sol(l: i128) -> String {
    format!("{:+.4}", l as f64 / 1e9)
}

impl Engine {
    pub fn new(
        cfg: LongCfg,
        me: Pubkey,
        signer: Option<HotSigner>,
        rpc: Rpc,
        oracle: Oracle,
        out_buy: Option<Out>,
        out_sell: Option<Out>,
    ) -> Result<Self, String> {
        let dir = PathBuf::from(&cfg.state_dir);
        std::fs::create_dir_all(&dir).map_err(|e| format!("{}: {e}", dir.display()))?;
        let book_path = dir.join("positions.json");
        let book = Book::load(&book_path)?;
        let mut anchors = vec![c::WSOL_MINT];
        anchors.extend(cfg.float_pks());
        Ok(Self {
            copy: cfg.copy_pk(),
            cfg,
            me,
            signer,
            rpc,
            bh: Blockhashes::default(),
            oracle,
            out_buy,
            out_sell,
            feed: None,
            book,
            book_path,
            closed_path: dir.join("closed.jsonl"),
            anchors,
            slot: 0,
            blockhash: None,
            its_bought: HashMap::new(),
            sol_balance: 0,
            floats: HashMap::new(),
            last_refresh_ms: 0,
            last_save_ms: 0,
            watched: BTreeSet::new(),
            buyback_rr: 0,
        })
    }

    pub fn set_feed(&mut self, f: FeedHandle) {
        self.feed = Some(f);
        self.rewatch();
    }

    /// The blockhash cache a thread keeps fresh (real mode).
    pub fn set_blockhashes(&mut self, bh: Blockhashes) {
        self.bh = bh;
    }

    fn real(&self) -> bool {
        self.cfg.mode == Mode::On
    }

    fn killed(&self) -> bool {
        std::path::Path::new(&self.cfg.state_dir)
            .join("KILL")
            .exists()
    }

    /// Write the book (pruning is `on_tick`'s, once per tick, so that
    /// positions never move under an index held by the caller).
    fn save(&mut self) {
        if let Err(e) = self.book.save(&self.book_path) {
            eprintln!("long: saving positions: {e}");
        }
        self.last_save_ms = now_ms();
    }

    fn rewatch(&mut self) {
        let want: BTreeSet<Pubkey> = self.book.live().map(|p| p.mint_pk()).collect();
        if want != self.watched {
            self.watched = want.clone();
            if let Some(f) = &self.feed {
                f.watch(want);
            }
        }
    }

    /// Run until the feed channel closes.
    pub fn run(&mut self, rx: mpsc::Receiver<FeedMsg>) {
        self.refresh(true);
        self.recover();
        loop {
            match rx.recv_timeout(Duration::from_millis(250)) {
                Ok(FeedMsg::Tx(src, tx)) => self.on_tx(src, &tx),
                Ok(FeedMsg::Slot(s)) => self.on_slot(s),
                Ok(FeedMsg::Up(up)) => println!(
                    "long feed {}",
                    if up { "connected" } else { "disconnected" }
                ),
                Err(mpsc::RecvTimeoutError::Timeout) => {}
                Err(mpsc::RecvTimeoutError::Disconnected) => break,
            }
            self.on_tick(now_ms());
        }
        self.save();
    }

    // ------------------------------------------------------------- inputs
    pub fn on_slot(&mut self, s: u64) {
        self.slot = self.slot.max(s);
    }

    pub fn on_tx(&mut self, src: Src, tx: &TxLite) {
        // the curve of every held coin
        if !tx.err {
            for t in tx.trades() {
                for p in self
                    .book
                    .positions
                    .iter_mut()
                    .filter(|p| p.live() && p.mint_pk() == t.mint)
                {
                    // a paper buy (sell) fills on the state at the end of its
                    // landing slot: later trades wait for the fill
                    if p.paper
                        && ((p.state == State::Buying && tx.slot > p.fill_slot())
                            || (p.state == State::Selling && tx.slot > p.sell_land_slot))
                    {
                        continue;
                    }
                    if tx.slot >= p.last_slot {
                        p.vt = t.vt;
                        p.vq = t.vq;
                        p.last_slot = tx.slot;
                        p.peak = p.peak.max(p.price());
                    }
                    if t.complete() {
                        // also while a sell is out: its curve sell fails, and
                        // the next one goes to the pool
                        p.graduated = true;
                        if p.state == State::Open && p.reason.is_none() {
                            p.reason = Some(Reason::Complete);
                        }
                    }
                }
            }
        }
        if src == Src::Ours || tx.signer() == Some(self.me) {
            self.on_ours(tx);
        }
        if tx.signer() == Some(self.copy) && !tx.err {
            let o = self.oracle.clone();
            for s in detect::read(tx, &self.copy, &|m: &Pubkey| o.lamports_per_unit(m)) {
                match s {
                    Seen::Buy(t) => self.on_trigger(*t),
                    Seen::Sell { mint, .. } => {
                        // it sold before any rule of ours fired: out behind it,
                        // as the backtest sells (its price path ends at its sale)
                        let follow = self.cfg.follow_its_sell;
                        let fees = self.paper_fees();
                        for p in self
                            .book
                            .positions
                            .iter_mut()
                            .filter(|p| p.mint_pk() == mint)
                        {
                            if !follow && p.live() && p.its_sell_px == 0.0 {
                                // our own exits stay; what selling behind it
                                // would have made goes on the record
                                p.its_sell_px = p.price();
                                p.its_sell_net = if p.state == State::Buying {
                                    0
                                } else {
                                    Self::paper_net(p, fees)
                                };
                                println!(
                                    "long its-sell #{} {} at {:.2}x: not followed (would make {} SOL); holding to our exits",
                                    p.id,
                                    m8(&mint),
                                    p.its_sell_px,
                                    sol(p.its_sell_net as i128)
                                );
                                continue;
                            }
                            // (an exit of ours waiting to be retried goes now too)
                            if p.state == State::Open && p.reason != Some(Reason::Complete) {
                                p.reason = Some(Reason::ItsSell);
                                println!("long its-sell #{} {}: out behind it", p.id, m8(&mint));
                            } else if p.live() {
                                // our buy still out, or a sell of ours: out
                                // behind it as soon as the buy fills
                                p.its_sold = true;
                                println!(
                                    "long its-sell #{} {} while {:?}: out behind it once filled",
                                    p.id,
                                    m8(&mint),
                                    p.state
                                );
                            }
                        }
                    }
                    Seen::SolBuy { .. } => {}
                }
            }
        }
    }

    fn skip(&self, t: &Trigger, why: &str) {
        println!(
            "long skip {} its {} SOL ({}): {why}",
            m8(&t.mint),
            t.sol_value
                .map_or("?".into(), |v| format!("{:.3}", v as f64 / 1e9)),
            if t.route.is_some() {
                "multihop"
            } else {
                "direct"
            }
        );
    }

    pub fn on_trigger(&mut self, t: Trigger) {
        let now = now_ms();
        let t0 = std::time::Instant::now();
        // its own trade prices a token it paid with when the SOL came in the
        // same transaction (a Jupiter leg): a WBTC/SOL rate on every such buy
        if let Some(v) = t.sol_value {
            if t.via_jupiter && t.input_amount > 0 && !c::is_sol_like_quote_mint(&t.input_mint) {
                self.oracle
                    .set(t.input_mint, v as f64 / t.input_amount as f64);
            }
        }
        let rebuy = self
            .its_bought
            .insert(t.mint, now)
            .is_some_and(|at| now.saturating_sub(at) < 3_600_000);
        let Some(v) = t.sol_value else {
            return self.skip(&t, "its buy has no SOL value (paid in an unpriced token)");
        };
        if (v as f64) < self.cfg.min_sol * 1e9 {
            // its smaller tiers: not copied, not journaled
            return;
        }
        if rebuy {
            return self.skip(&t, "its second buy of the coin");
        }
        if self
            .book
            .positions
            .iter()
            .any(|p| p.mint_pk() == t.mint && now.saturating_sub(p.seen_ms) < 3_600_000)
        {
            return self.skip(&t, "coin already ours");
        }
        if t.real_token_post == Some(0) {
            return self.skip(&t, "curve complete");
        }
        if self.cfg.mode == Mode::Off {
            return self.skip(&t, "mode off");
        }
        if self.killed() {
            return self.skip(&t, "KILL file");
        }
        let paper = !self.real();
        let open = self.book.live().filter(|p| p.paper == paper).count();
        if open >= self.cfg.max_open {
            return self.skip(&t, &format!("{open} open (max_open)"));
        }
        let today = self.book.realized_today(now, paper);
        if (today as f64) <= -self.cfg.daily_stop_sol * 1e9 {
            return self.skip(
                &t,
                &format!("daily stop ({} SOL today)", sol(today as i128)),
            );
        }
        let plan = match route::plan(&t, &self.anchors, &mut self.rpc) {
            Ok(p) => p,
            Err(e) => return self.skip(&t, &format!("route: {e}")),
        };
        let stake = self.cfg.stake_for(plan.anchor != c::WSOL_MINT);
        // our amount in, in anchor units, and its SOL value
        let amount_in = if plan.anchor == c::WSOL_MINT {
            stake
        } else {
            match self.oracle.lamports_per_unit(&plan.anchor) {
                Some(p) if p > 0.0 => (stake as f64 / p) as u64,
                _ => return self.skip(&t, &format!("no price for the float {}", m8(&plan.anchor))),
            }
        };
        // our share of its buy: in the same unit when we pay what it paid
        let share = if plan.anchor == t.input_mint && t.input_amount > 0 {
            amount_in as f64 / t.input_amount as f64
        } else {
            stake as f64 / v as f64
        };
        let quote_in_est = (t.its_quote_in as f64 * share) as u64;
        let min_out = pos::buy_min_out(t.vt_post, t.vq_post, quote_in_est, self.cfg.max_premium);
        let (input, hops) = Position::store_route(&plan.route);
        let id = self.book.next_id;
        self.book.next_id += 1;
        let mut p = Position {
            id,
            paper,
            mint: t.mint.to_string(),
            quote_mint: t.quote_mint.to_string(),
            quote_program: t.quote_program.to_string(),
            coin_program: t.coin_program.to_string(),
            anchor: plan.anchor.to_string(),
            anchor_program: plan.anchor_program.to_string(),
            route_input: input,
            route: hops,
            how: plan.how.to_string(),
            its_sig: t.sig.clone(),
            its_slot: t.slot,
            its_lamports: v,
            its_quote_in: t.its_quote_in,
            its_tokens: t.its_tokens,
            seen_ms: now,
            vt_ref: t.vt_post,
            vq_ref: t.vq_post,
            amount_in,
            stake_lamports: stake,
            tokens: 0,
            state: State::Buying,
            buy_sig: None,
            buy_sent_ms: now,
            sell_sigs: vec![],
            sell_sent_ms: 0,
            sell_tries: 0,
            reason: None,
            vt: t.vt_post,
            vq: t.vq_post,
            last_slot: t.slot,
            peak: 1.0,
            out_anchor: 0,
            out_lamports: 0,
            net_lamports: 0,
            closed_ms: 0,
            costs: 0,
            quote_in: quote_in_est,
            sell_next_ms: 0,
            dropped: false,
            graduated: false,
            // the slot we saw its buy in (our feed's latest), plus the landing
            land_slot: t.slot.max(self.slot) + self.cfg.paper_land_slots,
            applied: vec![],
            send_fails: 0,
            its_sold: false,
            fee_bps: t.fee_bps,
            sell_land_slot: 0,
            its_sell_px: 0.0,
            its_sell_net: 0,
            next_chase_ms: 0,
            recovered: false,
        };
        if paper {
            println!(
                "long paper-buy #{id} {} its {:.3} SOL route {} ({} hops) stake {:.3} SOL; seen at its slot +{}, fills at the end of +{}",
                m8(&t.mint),
                v as f64 / 1e9,
                plan.how,
                plan.route.hops.len(),
                stake as f64 / 1e9,
                self.slot.saturating_sub(t.slot),
                p.land_slot - t.slot
            );
        } else {
            // money checks
            let reserve = (self.cfg.reserve_sol * 1e9) as u64;
            if plan.anchor == c::WSOL_MINT {
                if self.sol_balance < stake + reserve {
                    return self.skip(
                        &t,
                        &format!(
                            "SOL balance {:.3} under the stake + reserve {:.3}",
                            self.sol_balance as f64 / 1e9,
                            reserve as f64 / 1e9
                        ),
                    );
                }
            } else if self.floats.get(&plan.anchor).copied().unwrap_or(0) < amount_in {
                return self.skip(&t, &format!("float {} under the stake", m8(&plan.anchor)));
            }
            match self.send_buy(&p, &plan.route, min_out) {
                Ok(sig) => {
                    println!(
                        "long buy #{id} {} its {:.3} SOL route {} ({} hops) in {} of {} min_out {} sent {} in {} ms; seen at its slot +{}",
                        m8(&t.mint),
                        v as f64 / 1e9,
                        plan.how,
                        plan.route.hops.len(),
                        amount_in,
                        m8(&plan.anchor),
                        min_out,
                        &sig[..8],
                        t0.elapsed().as_millis(),
                        self.slot.saturating_sub(t.slot)
                    );
                    p.buy_sig = Some(sig);
                    if plan.anchor == c::WSOL_MINT {
                        self.sol_balance = self.sol_balance.saturating_sub(stake);
                    } else if let Some(f) = self.floats.get_mut(&plan.anchor) {
                        *f = f.saturating_sub(amount_in);
                    }
                }
                Err(e) => return self.skip(&t, &format!("send: {e}")),
            }
        }
        self.book.positions.push(p);
        self.rewatch();
        self.save();
    }

    fn fees(&self, buy: bool) -> (Fees, Vec<Option<(Pubkey, u64)>>) {
        let tip = if buy {
            self.cfg.buy_tip_lamports
        } else {
            self.cfg.sell_tip_lamports
        };
        let out = if buy { &self.out_buy } else { &self.out_sell };
        let tips = out.as_ref().map(|o| o.tips(tip)).unwrap_or_default();
        (
            Fees {
                cu_limit: self.cfg.cu_limit,
                cu_price: if buy {
                    self.cfg.buy_cu_price
                } else {
                    self.cfg.sell_cu_price
                },
                tip: None,
            },
            tips,
        )
    }

    /// The cache's hash (a thread keeps it fresh), else one from this
    /// process's last fetch, else a fetch now.
    fn blockhash(&mut self) -> Result<[u8; 32], String> {
        if let Some(h) = self.bh.get(BLOCKHASH_MAX_AGE_MS) {
            return Ok(h);
        }
        match self.blockhash {
            Some((h, at)) if now_ms().saturating_sub(at) < BLOCKHASH_MAX_AGE_MS => Ok(h),
            _ => {
                let (h, _) = self.rpc.blockhash()?;
                self.blockhash = Some((h, now_ms()));
                self.bh.set(h);
                Ok(h)
            }
        }
    }

    /// Sign one copy per sender (each with its tip), send them, and the
    /// first copy through `sendTransaction` too. Returns every signature
    /// (first: the one `sendTransaction` carried).
    fn send_signed(
        &mut self,
        kind: VariantKind,
        ixs_for: &dyn Fn(Option<(Pubkey, u64)>) -> Vec<pump_codec::Instruction>,
    ) -> Result<Vec<String>, String> {
        let bh = self.blockhash()?;
        let signer = self.signer.as_ref().ok_or("no wallet loaded")?;
        let (_, tips) = self.fees(kind == VariantKind::Buy);
        let tips = if tips.is_empty() { vec![None] } else { tips };
        let mut txs = vec![];
        for tip in &tips {
            let ixs = ixs_for(*tip);
            txs.push(
                txb::sign(&self.me, &ixs, &bh, |m| signer.sign(m)).map_err(|e| e.to_string())?,
            );
        }
        let first = bs58::encode(txs[0].1).into_string();
        let out = if kind == VariantKind::Buy {
            &self.out_buy
        } else {
            &self.out_sell
        };
        // the senders and the RPC copy at the same time (the RPC copy is
        // the same bytes as the first sender's: the same signature)
        let rpc = &self.rpc;
        let rpc_copy = (self.cfg.rpc_send || out.is_none()).then_some(&txs[0].0);
        let (sent, rpc_res) = std::thread::scope(|sc| {
            let h = rpc_copy.map(|b| sc.spawn(move || rpc.send(b)));
            let sent = out
                .as_ref()
                .map(|o| o.send_each(kind, &txs, &tips))
                .unwrap_or_default();
            (
                sent,
                h.map(|h| h.join().unwrap_or_else(|_| Err("rpc send thread".into()))),
            )
        });
        let mut accepted = false;
        for s in &sent {
            accepted |= s.ok;
            if !s.ok {
                eprintln!("long send {} {}: {}", s.label, &s.sig[..8], s.why);
            }
        }
        match rpc_res {
            Some(Ok(_)) => accepted = true,
            Some(Err(e)) => eprintln!("long send rpc {}: {e}", &first[..8]),
            None => {}
        }
        if !accepted {
            return Err("no path accepted the transaction".into());
        }
        Ok(txs
            .iter()
            .map(|(_, s)| bs58::encode(s).into_string())
            .collect())
    }

    fn send_buy(
        &mut self,
        p: &Position,
        r: &pump_codec::multihop::Route,
        min_out: u64,
    ) -> Result<String, String> {
        let (fees, _) = self.fees(true);
        let (ap, cp) = (
            Position::pk(&p.anchor_program),
            Position::pk(&p.coin_program),
        );
        let (me, amount_in) = (self.me, p.amount_in);
        self.buyback_rr = self.buyback_rr.wrapping_add(1);
        let bb = self.buyback_rr;
        let r = r.clone();
        // one buy sender: one transaction (two landing would double the position)
        self.send_signed(VariantKind::Buy, &move |tip| {
            txb::buy_ixs(
                &me,
                &r,
                &ap,
                &cp,
                amount_in,
                min_out,
                &Fees { tip, ..fees },
                bb,
            )
        })
        .map(|v| v.into_iter().next().unwrap_or_default())
    }

    /// Expected anchor out for selling our tokens now, and the floor. The
    /// floor drops only after sells that landed and failed (`sell_tries`:
    /// the price moved past the floor), never after send errors or drops
    /// (`send_fails`): 2 landed failures take half, 4 take almost any
    /// price (a coin that cannot be sold is a full loss, 2RR6sfbi).
    fn sell_min_out(&self, p: &Position) -> u64 {
        let quote_out = pos::curve_sell_live(p.vt, p.vq, p.tokens, p.fee(CURVE_FEE_BPS)) as f64;
        // the route's other hops at our buy's own rate (anchor per quote)
        let rate = if p.quote_in > 0 && p.anchor != p.quote_mint {
            p.amount_in as f64 / p.quote_in as f64
        } else {
            1.0
        };
        let expected = quote_out * rate;
        let slack = match (p.reason, p.sell_tries) {
            (_, n) if n >= 4 => 0.9,
            (_, n) if n >= 2 => 0.5,
            (Some(Reason::Tp), _) => self.cfg.sell_slack_tp,
            _ => self.cfg.sell_slack_exit,
        };
        (expected * (1.0 - slack)) as u64
    }

    fn send_sell(&mut self, i: usize) -> Result<Vec<String>, String> {
        let p = self.book.positions[i].clone();
        let mut r = p.buy_route().ok_or("stored route unreadable")?.reversed();
        // the curve completed (or sells keep failing on it): the coin trades
        // on its canonical PumpSwap pool now
        let coin = p.mint_pk();
        let pool = pump_codec::pda::canonical_pump_swap_pool(&coin, &Position::pk(&p.quote_mint));
        if p.reason == Some(Reason::Complete)
            || p.graduated
            || (p.sell_tries >= 3 && route::Chain::pool_exists(&mut self.rpc, &pool))
        {
            let qp = if p.quote_program.is_empty() {
                c::TOKEN_2022_PROGRAM_ID
            } else {
                Position::pk(&p.quote_program)
            };
            let hops: Vec<_> = r
                .hops
                .iter()
                .map(|h| {
                    if h.venue == pump_codec::multihop::Venue::Curve && h.base_mint == coin {
                        pump_codec::multihop::Hop::pool(
                            &pool,
                            &coin,
                            &Position::pk(&p.coin_program),
                            &h.quote_mint,
                            &qp,
                        )
                    } else {
                        *h
                    }
                })
                .collect();
            r = pump_codec::multihop::Route::new(r.input, hops).map_err(|e| format!("{e:?}"))?;
        }
        let close_coin = p.sell_tries < 2;
        let min_out = self.sell_min_out(&p);
        let (fees, _) = self.fees(false);
        let (ap, cp, me, tokens) = (
            Position::pk(&p.anchor_program),
            Position::pk(&p.coin_program),
            self.me,
            p.tokens,
        );
        self.buyback_rr = self.buyback_rr.wrapping_add(1);
        let bb = self.buyback_rr;
        self.send_signed(VariantKind::Sell, &move |tip| {
            txb::sell_ixs(
                &me,
                &r,
                &ap,
                &cp,
                tokens,
                min_out,
                close_coin,
                &Fees { tip, ..fees },
                bb,
            )
        })
    }

    /// Our own transaction: a fill, a sell, or a failure of either. Booked
    /// once, whichever way it arrives (the feed, a chain check, both).
    fn on_ours(&mut self, tx: &TxLite) {
        let sig = tx.sig_b58();
        let me = self.me;
        let Some(i) =
            self.book.positions.iter().position(|p| {
                p.buy_sig.as_deref() == Some(sig.as_str()) || p.sell_sigs.contains(&sig)
            })
        else {
            return;
        };
        if !self.book.positions[i].apply(&sig) {
            return;
        }
        let now = now_ms();
        let price = {
            let a = Position::pk(&self.book.positions[i].anchor);
            if a == c::WSOL_MINT {
                Some(1.0)
            } else {
                self.oracle.last_known(&a)
            }
        };
        let p = &mut self.book.positions[i];
        let anchor = Position::pk(&p.anchor);
        let mint = p.mint_pk();
        // chain-true running result: lamports plus a float's token change
        let lam = tx.lamport_delta(&me);
        let anc = if anchor == c::WSOL_MINT {
            0
        } else {
            tx.token_delta(&me, &anchor)
        };
        if anc != 0 && price.is_none() {
            println!(
                "long WARNING #{} {}: no price for the float {}; its {} units are booked at 0",
                p.id,
                m8(&mint),
                m8(&anchor),
                anc
            );
        }
        p.net_lamports += lam as i64 + (anc as f64 * price.unwrap_or(0.0)) as i64;
        let is_buy = p.buy_sig.as_deref() == Some(sig.as_str());
        if tx.err {
            p.costs += tx.fee;
            if is_buy {
                p.state = State::Failed;
                p.dropped = false;
                p.closed_ms = now;
                println!("long buy-failed #{} {} cost {}", p.id, m8(&mint), sol(lam));
            } else if p.state == State::Selling {
                p.state = State::Open;
                p.sell_tries += 1;
                let cap = (self.cfg.max_sell_fail_sol * 1e9) as u64;
                let wait = pos::sell_backoff_ms(p.sell_tries, p.costs, cap);
                p.sell_next_ms = now + wait;
                println!(
                    "long sell-failed #{} {} try {} cost {} (next try in {} s)",
                    p.id,
                    m8(&mint),
                    p.sell_tries,
                    sol(lam),
                    wait / 1000
                );
                if cap > 0 && p.costs >= cap && p.costs - tx.fee < cap {
                    println!(
                        "long CRITICAL sells of #{} {} keep failing: {} tries, {} SOL of failed fees; retrying every 10 min",
                        p.id,
                        m8(&mint),
                        p.sell_tries,
                        sol(-(p.costs as i128))
                    );
                }
                // the curve may have completed unseen (a feed gap, a
                // restart): read it, so the next sell goes to the pool
                let (id, graduated) = (p.id, p.graduated);
                if !graduated && self.rpc.curve_complete(&mint) == Some(true) {
                    let p = &mut self.book.positions[i];
                    p.graduated = true;
                    println!(
                        "long #{id} {}: the curve is complete; selling on the pool",
                        m8(&mint)
                    );
                }
            }
        } else if is_buy && (p.state == State::Buying || (p.state == State::Failed && p.dropped)) {
            if p.dropped {
                println!(
                    "long late-fill #{} {}: the buy given up landed after all",
                    p.id,
                    m8(&mint)
                );
                p.dropped = false;
                p.closed_ms = 0;
            }
            p.tokens = tx.token_delta(&me, &mint).max(0) as u64;
            // our curve trade's quote in (the rate for the sell bound); the
            // trigger's estimate stays when the trade is not in the transaction
            match tx
                .trades()
                .iter()
                .find(|t| t.user == me && t.mint == mint && t.is_buy)
            {
                Some(t) => p.quote_in = t.quote_amount,
                None => println!(
                    "long WARNING #{} {}: no curve trade of ours in the fill; keeping the estimated quote",
                    p.id,
                    m8(&mint)
                ),
            }
            p.state = if p.tokens > 0 {
                State::Open
            } else {
                State::Failed
            };
            for t in tx.trades().iter().filter(|t| t.mint == mint) {
                p.vt = t.vt;
                p.vq = t.vq;
                p.last_slot = tx.slot;
            }
            // what happened while the buy was out decides the exit now:
            // the curve completed (sell on the pool), or it sold (out
            // behind it)
            if p.state == State::Open {
                if p.graduated {
                    p.reason = Some(Reason::Complete);
                } else if p.its_sold {
                    p.reason = Some(Reason::ItsSell);
                }
            }
            println!(
                "long fill #{} {} tokens {} paid {} (vs its price {:+.1}%){}",
                p.id,
                m8(&mint),
                p.tokens,
                sol(lam),
                (p.its_tokens as f64
                    / p.its_lamports.max(1) as f64
                    / (p.tokens as f64 / (p.stake_lamports.max(1) as f64))
                    - 1.0)
                    * 100.0,
                match p.reason {
                    Some(Reason::Complete) =>
                        "; the curve completed meanwhile: selling on the pool",
                    Some(Reason::ItsSell) => "; it sold meanwhile: out behind it",
                    _ => "",
                }
            );
        } else if !is_buy {
            let left = tx.token_delta(&me, &mint);
            p.out_anchor = if anchor == c::WSOL_MINT {
                lam.max(0) as u64
            } else {
                anc.max(0) as u64
            };
            if left < 0 {
                p.state = State::Closed;
                p.closed_ms = now;
                p.tokens = 0;
                let held = now.saturating_sub(p.seen_ms) / 1000;
                println!(
                    "long closed #{} {} {} net {} SOL ({:+.1}%) held {}s peak {:.2}x",
                    p.id,
                    m8(&mint),
                    p.reason.map_or("?", Reason::name),
                    sol(p.net_lamports as i128),
                    p.net_lamports as f64 / p.stake_lamports.max(1) as f64 * 100.0,
                    held,
                    p.peak
                );
                let rec = serde_json::to_string(&*p).unwrap_or_default();
                if let Ok(mut f) = std::fs::OpenOptions::new()
                    .create(true)
                    .append(true)
                    .open(&self.closed_path)
                {
                    let _ = writeln!(f, "{rec}");
                }
            }
        }
        self.rewatch();
        self.save();
    }

    // -------------------------------------------------------------- clock
    pub fn on_tick(&mut self, now: u64) {
        // old closed positions leave the book here only: nothing below holds
        // an index across it
        self.book.prune(now, 3 * 86_400_000);
        if self.real() && now.saturating_sub(self.last_refresh_ms) > 30_000 {
            self.refresh(false);
        }
        enum Act {
            PaperFill,
            PaperClose,
            Chase(bool),
            Exit(Reason),
        }
        let cfg = &self.cfg;
        let slot = self.slot;
        let acts: Vec<(usize, Act)> = self
            .book
            .positions
            .iter()
            .enumerate()
            .filter_map(|(i, p)| match p.state {
                // a paper buy fills once its landing slot is over
                State::Buying if p.paper && slot > p.fill_slot() => Some((i, Act::PaperFill)),
                // a paper sell the same way
                State::Selling if p.paper && slot > p.sell_land_slot => Some((i, Act::PaperClose)),
                // a transaction not seen in time (or out when we started)
                // is asked for, every CHASE_EVERY_MS
                State::Buying
                    if !p.paper
                        && now >= p.next_chase_ms
                        && (p.recovered || now.saturating_sub(p.buy_sent_ms) > BUY_WAIT_MS) =>
                {
                    Some((i, Act::Chase(true)))
                }
                State::Selling
                    if !p.paper
                        && now >= p.next_chase_ms
                        && (p.recovered || now.saturating_sub(p.sell_sent_ms) > SELL_WAIT_MS) =>
                {
                    Some((i, Act::Chase(false)))
                }
                State::Open if now >= p.sell_next_ms => p
                    .reason
                    .filter(|r| matches!(r, Reason::Complete | Reason::ItsSell))
                    // the curve completed while our buy was out: the price
                    // is frozen, no rule of ours would fire (2RR6sfbi)
                    .or_else(|| p.graduated.then_some(Reason::Complete))
                    .or_else(|| pos::exit_due(p, now, cfg.take_profit, cfg.stop, cfg.max_hold_s))
                    .map(|r| (i, Act::Exit(r))),
                _ => None,
            })
            .collect();
        // a paper buy is refused past max_premium as the real one is (its
        // min_out), at the fee a landed failure pays (the tip transfer reverts)
        let max_premium = self.cfg.max_premium;
        let refused_fee = 5_000 + self.cfg.cu_limit as u64 * self.cfg.buy_cu_price / 1_000_000;
        let mut changed = false;
        for (i, a) in acts {
            match a {
                Act::PaperFill => {
                    let p = &mut self.book.positions[i];
                    let share = p.stake_lamports as f64 / p.its_lamports.max(1) as f64;
                    // its quote in is what the curve took, fees apart (the
                    // event reports it before fees), and its SOL value is
                    // all it spent: our share of the quote buys tokens at
                    // the curve's rate with no fee off it again
                    let q = (p.its_quote_in as f64 * share) as u64;
                    p.tokens = pos::curve_buy(p.vt, p.vq, q, 0);
                    p.quote_in = q;
                    let min_out = pos::buy_min_out(p.vt_ref, p.vq_ref, q, max_premium);
                    if p.tokens < min_out {
                        p.state = State::Failed;
                        p.costs = refused_fee;
                        p.net_lamports = -(refused_fee as i64);
                        p.closed_ms = now;
                        println!(
                            "long paper-refused #{} {}: at {:.3}x its price, {} tokens under min_out {} (max_premium {})",
                            p.id,
                            &p.mint[..8],
                            p.price(),
                            p.tokens,
                            min_out,
                            max_premium
                        );
                        changed = true;
                        continue;
                    }
                    p.state = State::Open;
                    // what happened while the buy was out (paper too)
                    if p.graduated {
                        p.reason = Some(Reason::Complete);
                    } else if p.its_sold {
                        p.reason = Some(Reason::ItsSell);
                    }
                    println!(
                        "long paper-fill #{} {} tokens {} at {:.3}x its price",
                        p.id,
                        &p.mint[..8],
                        p.tokens,
                        p.price()
                    );
                    changed = true;
                }
                Act::PaperClose => {
                    self.paper_close(i, now);
                    changed = true;
                }
                Act::Chase(buy) => changed |= self.chase(i, buy),
                Act::Exit(r) => {
                    self.exit(i, r, now);
                    changed = true;
                }
            }
        }
        // an exit decided by a fill in this tick (the curve completed, or it
        // sold, while our buy was out) goes now, not after the next message
        let due: Vec<(usize, Reason)> = self
            .book
            .positions
            .iter()
            .enumerate()
            .filter(|(_, p)| p.state == State::Open && now >= p.sell_next_ms)
            .filter_map(|(i, p)| {
                p.reason
                    .filter(|r| matches!(r, Reason::Complete | Reason::ItsSell))
                    .map(|r| (i, r))
            })
            .collect();
        for (i, r) in due {
            self.exit(i, r, now);
            changed = true;
        }
        if changed {
            self.rewatch();
            self.save();
        } else if now.saturating_sub(self.last_save_ms) > 30_000 {
            self.save();
        }
    }

    fn exit(&mut self, i: usize, r: Reason, now: u64) {
        let p = &mut self.book.positions[i];
        p.reason = Some(r);
        let px = p.price();
        if p.paper {
            // a paper sell lands like a paper buy: on the state at the end
            // of `paper_land_slots` after the trade that fired the exit
            // (2026-10-28: it closed on the firing trade's own state, which
            // a real sell never gets)
            p.state = State::Selling;
            p.sell_sent_ms = now;
            p.sell_land_slot = self.slot + self.cfg.paper_land_slots;
            println!(
                "long paper-sell #{} {} {} at {:.2}x; fills at the end of slot +{}",
                p.id,
                &p.mint[..8],
                r.name(),
                px,
                self.cfg.paper_land_slots
            );
            return;
        }
        let (id, mint, tries) = (p.id, p.mint.clone(), p.sell_tries);
        let t0 = std::time::Instant::now();
        match self.send_sell(i) {
            Ok(sigs) => {
                let sig = sigs.first().cloned().unwrap_or_default();
                let p = &mut self.book.positions[i];
                p.state = State::Selling;
                p.sell_sent_ms = now;
                p.sell_sigs.extend(sigs);
                println!(
                    "long sell #{id} {} {} at {px:.2}x try {tries} sent {} in {} ms",
                    &mint[..8],
                    r.name(),
                    &sig[..8],
                    t0.elapsed().as_millis()
                );
            }
            Err(e) => {
                // not sent: no floor change (nothing landed), a short wait
                let p = &mut self.book.positions[i];
                p.send_fails += 1;
                p.sell_next_ms = now + 1_000 * p.send_fails.min(5) as u64;
                eprintln!(
                    "long sell #{id} {}: not sent ({e}); send failure {} (retry in {} s)",
                    &mint[..8],
                    p.send_fails,
                    p.send_fails.min(5)
                );
            }
        }
    }

    /// The fees a paper round trip pays: both transactions' base and
    /// priority fees and both tips.
    fn paper_fees(&self) -> u64 {
        2 * 5_000
            + self.cfg.cu_limit as u64 * (self.cfg.buy_cu_price + self.cfg.sell_cu_price)
                / 1_000_000
            + self.cfg.buy_tip_lamports
            + self.cfg.sell_tip_lamports
    }

    /// A paper position's result if sold on the curve as it is now
    /// (lamports): our tokens back into it, the route's other hops at our
    /// own fill's rate, less `fees`.
    fn paper_net(p: &Position, fees: u64) -> i64 {
        let quote_out = pos::curve_sell_paper(p.vt, p.vq, p.tokens, p.fee(CURVE_FEE_BPS)) as f64;
        let back = quote_out * p.stake_lamports as f64 / p.quote_in.max(1) as f64;
        back as i64 - p.stake_lamports as i64 - fees as i64
    }

    /// A paper sell at the end of its landing slot: the curve as it is then,
    /// our tokens sold back into it.
    fn paper_close(&mut self, i: usize, now: u64) {
        let fees = self.paper_fees();
        let p = &mut self.book.positions[i];
        let r = p.reason.unwrap_or(Reason::Manual);
        let px = p.price();
        let net = Self::paper_net(p, fees);
        p.out_lamports = (net + p.stake_lamports as i64 + fees as i64).max(0) as u64;
        p.net_lamports = net;
        p.state = State::Closed;
        p.closed_ms = now;
        println!(
            "long paper-closed #{} {} {} at {:.2}x net {} SOL ({:+.1}%) held {}s peak {:.2}x",
            p.id,
            &p.mint[..8],
            r.name(),
            px,
            sol(p.net_lamports as i128),
            p.net_lamports as f64 / p.stake_lamports.max(1) as f64 * 100.0,
            now.saturating_sub(p.seen_ms) / 1000,
            p.peak
        );
        let rec = serde_json::to_string(&*p).unwrap_or_default();
        if let Ok(mut f) = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.closed_path)
        {
            let _ = writeln!(f, "{rec}");
        }
    }

    /// A buy or sell not seen landed in time: ask the chain. Only the
    /// signatures not booked yet are read (2026-10-28: it re-read the first
    /// landed one, an old failed sell, and never the newer one), a landed
    /// success first.
    fn chase(&mut self, i: usize, buy: bool) -> bool {
        let now = now_ms();
        let p = &mut self.book.positions[i];
        p.next_chase_ms = now + CHASE_EVERY_MS;
        p.recovered = false;
        let sigs: Vec<String> = if buy {
            p.buy_sig.iter().cloned().collect()
        } else {
            p.sell_sigs.clone()
        }
        .into_iter()
        .filter(|s| !p.applied.contains(s))
        .collect();
        if sigs.is_empty() {
            return false;
        }
        let st = match self.rpc.statuses(&sigs) {
            Ok(s) => s,
            Err(_) => return false,
        };
        // landed: read every one as the feed would have, the successes first
        let mut landed: Vec<(&String, bool)> = sigs
            .iter()
            .zip(&st)
            .filter_map(|(s, r)| r.as_ref().map(|r| (s, r.is_ok())))
            .collect();
        landed.sort_by_key(|(_, ok)| !ok);
        let mut applied = false;
        for (s, _) in landed {
            if let Ok(v) = self.rpc.transaction(s) {
                if let Ok(tx) = TxLite::from_rpc_json(&v) {
                    self.on_ours(&tx);
                    applied = true;
                }
            }
        }
        if applied {
            return true;
        }
        // nothing landed: the blockhash is past its life after ~60 s
        let p = &mut self.book.positions[i];
        let age = now.saturating_sub(if buy { p.buy_sent_ms } else { p.sell_sent_ms });
        if age < DROP_AFTER_MS {
            return false;
        }
        if buy {
            p.state = State::Failed;
            p.dropped = true;
            p.closed_ms = now;
            println!("long buy-dropped #{} {}", p.id, &p.mint[..8]);
        } else {
            // not a landed failure: the floor stays
            p.state = State::Open;
            p.send_fails += 1;
            println!(
                "long sell-dropped #{} {} (send failure {}; retried)",
                p.id,
                &p.mint[..8],
                p.send_fails
            );
        }
        true
    }

    /// Balances (SOL, floats) and the oracle's view of the floats.
    fn refresh(&mut self, log: bool) {
        self.last_refresh_ms = now_ms();
        if !self.real() {
            return;
        }
        if let Ok(b) = self.rpc.balance(&self.me) {
            self.sol_balance = b;
        }
        for f in self
            .anchors
            .clone()
            .into_iter()
            .filter(|a| *a != c::WSOL_MINT)
        {
            let prog =
                route::Chain::mint_program(&mut self.rpc, &f).unwrap_or(c::SPL_TOKEN_PROGRAM_ID);
            if let Ok(b) = self.rpc.token_balance(&self.me, &f, &prog) {
                self.floats.insert(f, b);
            }
        }
        if log {
            let fl: Vec<String> = self
                .floats
                .iter()
                .map(|(m, b)| {
                    let v = self
                        .oracle
                        .lamports_per_unit(m)
                        .map_or("?".into(), |p| format!("{:.3}", *b as f64 * p / 1e9));
                    format!("{} {} ({v} SOL)", m8(m), b)
                })
                .collect();
            println!(
                "long wallet {} SOL {:.4} floats [{}]",
                self.me,
                self.sol_balance as f64 / 1e9,
                fl.join(", ")
            );
        }
    }

    /// After a restart: live positions whose transactions were in flight.
    pub fn recover(&mut self) {
        let live = self.book.live().count();
        if live > 0 {
            println!("long recover: {live} live position(s)");
        }
        // its buys we already copied (a second buy of a coin is not copied
        // for an hour), rebuilt from the book
        for p in &self.book.positions {
            self.its_bought.insert(p.mint_pk(), p.seen_ms);
        }
        // a transaction out when we stopped: ask the chain for it at once,
        // but give it up only by its real age (2026-10-28: the send time
        // was zeroed, so a buy in flight was dropped on the first tick)
        for p in self.book.positions.iter_mut() {
            if !p.paper && matches!(p.state, State::Buying | State::Selling) {
                p.recovered = true;
                p.next_chase_ms = 0;
            }
        }
        // a buy given up shortly before the stop may have landed while we
        // were down: read it from the chain (a landed one reopens)
        let now = now_ms();
        let late: Vec<String> = self
            .book
            .positions
            .iter()
            .filter(|p| p.dropped && !p.paper && now.saturating_sub(p.closed_ms) < 600_000)
            .filter_map(|p| p.buy_sig.clone())
            .collect();
        for sig in late {
            if let Ok(v) = self.rpc.transaction(&sig) {
                if let Ok(tx) = TxLite::from_rpc_json(&v) {
                    self.on_ours(&tx);
                }
            }
        }
        self.rewatch();
    }
}
