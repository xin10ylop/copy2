//! The ladder (2026-11-18, `analysis/research/2026-11-18/track/`): one
//! operation buys its own launches in the create slot from several wallets
//! at fixed sizes (1.10 / 1.54 / 2.18 SOL so far), a new set of wallets every
//! day or two. A SOL-priced coin whose create slot holds buys of the ladder
//! sizes from `min_wallets` or more different wallets is a trigger, whoever
//! the wallets are. The flip on it (buy at once, sell at +20% over our fill
//! or 30 s later) made +23% to +32% a copy on four groups never used to pick
//! it, and +51% on the 108 launches after every screen
//! (`PREREG_ladder_flip.md`).
//!
//! The core takes plain events (`on_create`, `on_buy`) so it is tested
//! without transactions; `on_tx` feeds it from a parsed transaction.

use crate::txlite::TxLite;
use pump_codec::Pubkey;
use serde::Deserialize;
use std::collections::{BTreeSet, HashMap};

/// The `[ladder]` section of the config.
#[derive(Debug, Clone, Deserialize, PartialEq)]
#[serde(default, deny_unknown_fields)]
pub struct LadderCfg {
    /// Watch every pump launch for the ladder (needs the feed's pump filter).
    pub enabled: bool,
    /// The ladder's buy sizes, SOL moved by the curve (fees out).
    pub sizes_sol: Vec<f64>,
    /// How close a buy must be to one of `sizes_sol`.
    pub tol_sol: f64,
    /// Different wallets at the ladder sizes in the create slot to fire.
    pub min_wallets: usize,
    /// Leave mayhem coins out (the research did not single them out; the
    /// SOL buy's `partial_fill` matters only there).
    pub skip_mayhem: bool,
}

impl Default for LadderCfg {
    fn default() -> Self {
        Self {
            enabled: false,
            sizes_sol: vec![1.10, 1.54, 2.18],
            tol_sol: 0.005,
            min_wallets: 2,
            skip_mayhem: true,
        }
    }
}

impl LadderCfg {
    pub fn validate(&self) -> Result<(), String> {
        if self.sizes_sol.is_empty() || self.sizes_sol.iter().any(|s| !(*s > 0.0 && *s < 100.0)) {
            return Err("ladder.sizes_sol: one or more sizes between 0 and 100 SOL".into());
        }
        if !(self.tol_sol > 0.0 && self.tol_sol < 0.1) {
            return Err("ladder.tol_sol must be in (0, 0.1)".into());
        }
        if self.min_wallets < 2 {
            return Err("ladder.min_wallets must be 2 or more (one wallet is not a ladder)".into());
        }
        Ok(())
    }
}

/// A ladder found: buy now.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Hit {
    pub mint: Pubkey,
    /// The create slot (the ladder's slot).
    pub slot: u64,
    pub token_program: Pubkey,
    /// The ladder's wallets seen so far (at least `min_wallets`).
    pub wallets: Vec<Pubkey>,
    /// The curve's virtual reserves after the last ladder buy seen.
    pub vt: u64,
    pub vq: u64,
}

#[derive(Debug, Clone)]
struct Launch {
    slot: u64,
    token_program: Pubkey,
    wallets: BTreeSet<Pubkey>,
    fired: bool,
}

/// The detector: the launches of the last few slots and their ladder buys.
#[derive(Debug, Clone, Default)]
pub struct Ladder {
    pub cfg: LadderCfg,
    open: HashMap<Pubkey, Launch>,
}

/// Launches older than this many slots are dropped (the ladder is in the
/// create slot; a few slots of margin for late deliveries).
const KEEP_SLOTS: u64 = 40;

impl Ladder {
    pub fn new(cfg: LadderCfg) -> Self {
        Self { cfg, open: HashMap::new() }
    }

    /// A coin created in `slot`. Coins priced in another token (and mayhem
    /// coins, with `skip_mayhem`) are not watched.
    pub fn on_create(&mut self, mint: Pubkey, slot: u64, token_program: Pubkey, sol_quoted: bool, mayhem: bool) {
        if !sol_quoted || (mayhem && self.cfg.skip_mayhem) {
            return;
        }
        self.open.entry(mint).or_insert(Launch { slot, token_program, wallets: BTreeSet::new(), fired: false });
        self.open.retain(|_, l| slot.saturating_sub(l.slot) <= KEEP_SLOTS);
    }

    /// A buy of `quote_lamports` (the curve's SOL, fees out) by `user` in
    /// `slot`. A hit the first time the coin's create slot holds
    /// `min_wallets` different wallets at the ladder sizes.
    pub fn on_buy(&mut self, mint: &Pubkey, slot: u64, user: &Pubkey, quote_lamports: u64, vt: u64, vq: u64) -> Option<Hit> {
        let cfg = &self.cfg;
        let l = self.open.get_mut(mint)?;
        if slot != l.slot || l.fired {
            return None;
        }
        let sol = quote_lamports as f64 / 1e9;
        if !cfg.sizes_sol.iter().any(|s| (sol - s).abs() <= cfg.tol_sol) {
            return None;
        }
        l.wallets.insert(*user);
        if l.wallets.len() < cfg.min_wallets {
            return None;
        }
        l.fired = true;
        Some(Hit {
            mint: *mint,
            slot: l.slot,
            token_program: l.token_program,
            wallets: l.wallets.iter().copied().collect(),
            vt,
            vq,
        })
    }

    /// A parsed transaction: its creates first (a create's own dev buy is in
    /// the same transaction), then its SOL-priced buys.
    pub fn on_tx(&mut self, tx: &TxLite) -> Vec<Hit> {
        if tx.err {
            return vec![];
        }
        for c in tx.creates() {
            self.on_create(c.mint, tx.slot, c.token_program, c.sol_quoted, c.mayhem);
        }
        let mut hits = vec![];
        for t in tx.trades() {
            if t.is_buy && t.sol_quoted() {
                if let Some(h) = self.on_buy(&t.mint, tx.slot, &t.user, t.quote_amount, t.vt, t.vq) {
                    hits.push(h);
                }
            }
        }
        hits
    }

    /// Launches watched now (for the status line).
    pub fn watched(&self) -> usize {
        self.open.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn pk(n: u8) -> Pubkey {
        Pubkey::new_from_array([n; 32])
    }
    fn on() -> Ladder {
        Ladder::new(LadderCfg { enabled: true, ..Default::default() })
    }
    const T22: u8 = 9;

    #[test]
    fn a_ladder_of_two_sizes_fires_once() {
        let mut d = on();
        d.on_create(pk(1), 100, pk(T22), true, false);
        assert_eq!(d.on_buy(&pk(1), 100, &pk(10), 1_100_000_000, 5, 6), None);
        let h = d.on_buy(&pk(1), 100, &pk(11), 1_540_000_000, 7, 8).expect("two ladder wallets");
        assert_eq!((h.slot, h.wallets.len(), h.vt, h.vq, h.token_program), (100, 2, 7, 8, pk(T22)));
        // the third rung: no second trigger
        assert_eq!(d.on_buy(&pk(1), 100, &pk(12), 2_180_000_000, 9, 9), None);
    }

    #[test]
    fn one_wallet_twice_is_not_a_ladder() {
        let mut d = on();
        d.on_create(pk(1), 100, pk(T22), true, false);
        assert_eq!(d.on_buy(&pk(1), 100, &pk(10), 1_100_000_000, 0, 0), None);
        assert_eq!(d.on_buy(&pk(1), 100, &pk(10), 1_540_000_000, 0, 0), None);
    }

    #[test]
    fn the_ladder_sizes_a_slot_late_do_not_fire() {
        let mut d = on();
        d.on_create(pk(1), 100, pk(T22), true, false);
        assert_eq!(d.on_buy(&pk(1), 101, &pk(10), 1_100_000_000, 0, 0), None);
        assert_eq!(d.on_buy(&pk(1), 101, &pk(11), 1_540_000_000, 0, 0), None);
    }

    #[test]
    fn other_sizes_do_not_count() {
        let mut d = on();
        d.on_create(pk(1), 100, pk(T22), true, false);
        assert_eq!(d.on_buy(&pk(1), 100, &pk(10), 1_000_000_000, 0, 0), None);
        assert_eq!(d.on_buy(&pk(1), 100, &pk(11), 1_540_000_000, 0, 0), None);
        // 1.106 is outside 1.10 +/- 0.005
        assert_eq!(d.on_buy(&pk(1), 100, &pk(12), 1_106_000_000, 0, 0), None);
        assert!(d.on_buy(&pk(1), 100, &pk(13), 2_177_000_000, 0, 0).is_some());
    }

    #[test]
    fn coins_in_another_token_and_mayhem_are_not_watched() {
        let mut d = on();
        d.on_create(pk(1), 100, pk(T22), false, false);
        d.on_create(pk(2), 100, pk(T22), true, true);
        for m in [pk(1), pk(2)] {
            assert_eq!(d.on_buy(&m, 100, &pk(10), 1_100_000_000, 0, 0), None);
            assert_eq!(d.on_buy(&m, 100, &pk(11), 1_540_000_000, 0, 0), None);
        }
        // a buy of a coin never seen created: nothing
        assert_eq!(d.on_buy(&pk(3), 100, &pk(11), 1_540_000_000, 0, 0), None);
    }

    #[test]
    fn old_launches_are_dropped() {
        let mut d = on();
        d.on_create(pk(1), 100, pk(T22), true, false);
        d.on_create(pk(2), 100 + KEEP_SLOTS + 1, pk(T22), true, false);
        assert_eq!(d.watched(), 1);
    }

    #[test]
    fn the_config_is_checked() {
        assert!(LadderCfg::default().validate().is_ok());
        assert!(LadderCfg { min_wallets: 1, ..Default::default() }.validate().is_err());
        assert!(LadderCfg { sizes_sol: vec![], ..Default::default() }.validate().is_err());
        assert!(LadderCfg { tol_sol: 0.0, ..Default::default() }.validate().is_err());
    }
}
