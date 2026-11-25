//! `/etc/rugsnipe/long.toml`: the long copy's own settings. The feed
//! endpoint, its token and the senders come from the hot unit's config and
//! key files (`hot_config`, `api_keys`), so both processes use the same
//! providers.

use serde::Deserialize;

/// What the process does with a trigger.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum Mode {
    /// Nothing (the process only reports).
    Off,
    /// Paper: a position on the live curve, journaled, nothing sent.
    #[default]
    Log,
    /// Real buys and sells from the long wallet.
    On,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields, default)]
pub struct LongCfg {
    pub mode: Mode,
    /// The wallet copied (H9kuqGKN).
    pub copy_wallet: String,
    /// The long wallet's keypair (JSON array, root-only).
    pub wallet_file: String,
    /// Its buy, valued in SOL, of at least this much: its 1.5-SOL tier
    /// (docs/20: 1.5 in the backtest; its tier reads 1.45-1.51 by the
    /// route's valuation).
    pub min_sol: f64,
    /// Our buy, valued in SOL.
    pub stake_sol: f64,
    /// Sell when the curve price (without our own tokens) reaches this
    /// multiple of the price its buy left.
    pub take_profit: f64,
    /// ... or falls to this multiple.
    pub stop: f64,
    /// ... or this long after its buy (seconds; it sells at 1800).
    pub max_hold_s: u64,
    /// Open positions at once (each `stake_sol`).
    pub max_open: usize,
    /// Our buy is refused above this premium over its average price
    /// (`min_out` from its own fill).
    pub max_premium: f64,
    /// No new buys once the UTC day's realized result is at or below
    /// `-daily_stop_sol` (exits continue).
    pub daily_stop_sol: f64,
    /// Mints held as floats besides wrapped SOL (WBTC ...): routes may start
    /// and end in them.
    pub floats: Vec<String>,
    /// Chain reads (blockhash, accounts, statuses) and simulation.
    pub rpc_url: String,
    /// The hot unit's config (its `[feeds] grpc` and `[senders]`).
    pub hot_config: String,
    /// The hot unit's API keys (gRPC token, sender keys).
    pub api_keys: String,
    /// Sender labels for buys: one transaction goes to each, so keep one
    /// (two landing would double the position).
    pub buy_senders: Vec<String>,
    /// Sender labels for sells (empty = every enabled sender; a second sell
    /// of the same position fails harmlessly).
    pub sell_senders: Vec<String>,
    /// Also send every transaction through `rpc_url` (`sendTransaction`).
    pub rpc_send: bool,
    pub buy_tip_lamports: u64,
    pub sell_tip_lamports: u64,
    /// Priority fee, micro-lamports per compute unit.
    pub buy_cu_price: u64,
    pub sell_cu_price: u64,
    pub cu_limit: u32,
    /// Sell `min_out` slack under the expected output: take profit, the
    /// others (stop, time, retries).
    pub sell_slack_tp: f64,
    pub sell_slack_exit: f64,
    /// Failed-sell fees (SOL) on one position past which its sells retry
    /// only every 10 min (they never stop).
    pub max_sell_fail_sol: f64,
    /// A paper buy fills on the curve at the end of this many slots after
    /// the slot we saw its buy in (a real buy lands after we see it); a
    /// paper sell fills the same way after the trade that fired the exit.
    pub paper_land_slots: u64,
    /// SOL kept in the wallet beyond the stakes (fees, rent): a wSOL buy
    /// needs `stake_sol + reserve_sol` in the wallet.
    pub reserve_sol: f64,
    /// Sell right behind its own sell when it leaves before any rule of
    /// ours fires (the backtest's rule). With `false` the position keeps
    /// our own exits and the journal records what selling behind it would
    /// have made (2026-10-28: it sells early on half of its big buys now,
    /// against 3.5% on Oct 19-22; on Oct 27-28 holding to our exits scored
    /// +3.10 against -0.51, on Oct 19-27 about even).
    pub follow_its_sell: bool,
    /// With `follow_its_sell = false`: still sell behind its sale when it
    /// comes `[from, to)` seconds after its buy and the price is under
    /// `follow_early_below` (an early sale of a coin that has not taken off).
    /// Empty = off. Oct 29 - Nov 12, [30, 180] and 1.5: better in both weeks
    /// on the copies it changes, +0.82 and +1.49 SOL at 1 SOL after the live
    /// calibration (analysis/research/2026-10-31/since_stop/follow_when.py).
    pub follow_early_s: Vec<u64>,
    pub follow_early_below: f64,
    /// Our buy, valued in SOL, when the route starts from a float (WBTC);
    /// 0 = `stake_sol`. WBTC-routed copies made about +0.12 SOL a copy
    /// against +0.02 from wrapped SOL (backtests §9).
    pub float_stake_sol: f64,
    /// Skip its buy when the coin's fee tier (protocol + creator fee of its
    /// own buy, basis points) is under this; 0 = off. A fee of 0 (not in the
    /// event) is never skipped. Oct 21 - Nov 14 the copies of coins under 125
    /// bps lost in every block (98 of 781, 4 take profits, -4.5 SOL at 0.5
    /// SOL), found by two studies apart; the next 10 made +3.9 SOL in the
    /// model, so it is off until more of them are seen
    /// (analysis/research/2026-11-15/skip_filters/).
    pub min_fee_bps: u32,
    /// Sell when the other traders' sells outnumber their buys by `n` or more
    /// over the last `w` seconds, from `from` seconds after its buy: `[n, w,
    /// from]`; empty = off. Oct 21 - Nov 15, [5, 60, 30] made +6.5 SOL at 0.5
    /// SOL over 24 days on its own, ahead in each block; any n from 2 to 10
    /// over 60-120 s was ahead, over 10 s all lost
    /// (analysis/research/2026-11-16/signals/).
    pub sell_pressure: Vec<u64>,
    /// Sell when the price has made no new high for this many seconds, once
    /// it has been back at our fill price; 0 = off. 180 s: +6.5 SOL on its
    /// own, 90-240 s all ahead; with sell_pressure and take_profit 4.0, +75.3
    /// against +56.6 SOL, 3 losing days of 24 against 6 (the same study).
    pub stall_s: u64,
    /// A float that holds less than the stake (a loss is paid back in it)
    /// still buys, with all it holds, when that is at least this share of
    /// the stake; under it the buy is skipped. 1.0 = the whole stake or
    /// nothing. Several small floats (PUMP, SPCX, 2026-11-14) would
    /// otherwise stop copying after one losing trade until topped up.
    pub float_min_frac: f64,
    /// Positions, journal-only state, the kill file.
    pub state_dir: String,
    /// Float prices (Jupiter Price API v3; with a key: `https://api.jup.ag/price/v3`
    /// and `cred:` is not supported here, so the free endpoint by default).
    pub price_api: String,
    /// The take profit over our own fill price instead of the price its buy
    /// left (the ladder flip sells at +20% over what we paid).
    pub tp_from_fill: bool,
    /// The DIP entry (Nov 19, the dip unit; `analysis/research/2026-11-17/wallet_hunt/market/m15*`): 0 = off (buy at once,
    /// the copy). Else its buy is not copied at once: for `dip_within_s` seconds we watch the coin and buy at the first
    /// trade of a later slot that leaves the price at or under (1 - dip_drop) x the price its buy left. The exits run
    /// from that buy (with `tp_from_fill`, the take profit is over our own fill).
    pub dip_drop: f64,
    pub dip_within_s: u64,
    /// The dip as a SECOND leg of this unit (Nov 19, the owner: "from the same bot ... we split 0.5, 0.5"): > 0, the copy
    /// still buys at once (`stake_sol`) and the dip buys `dip_stake_sol` more of the same coin; 0, the dip is the only
    /// entry (the separate dip unit). The dip leg's exits: take profit `dip_take_profit` over our fill, `dip_max_hold_s`,
    /// no stop, no sell pressure, no stall, its sale not followed.
    pub dip_stake_sol: f64,
    pub dip_take_profit: f64,
    pub dip_max_hold_s: u64,
    /// The dip leg only when our route pays with a float (not wrapped SOL); the copy leg is not affected.
    pub dip_float_only: bool,
    /// Other units trading from the SAME wallet (Nov 18: the TAB16RxX unit on wallet 4's
    /// wallet): their state dirs. A coin one of them holds (seen in the last hour) is not
    /// bought, and a sale never closes the coin's token account while one of them still
    /// holds the coin (the close would fail on its tokens and cost the sale a try).
    pub other_state_dirs: Vec<String>,
    /// Buy its coin even when another unit on this wallet holds it (Nov 25, the owner: "yes", on
    /// analysis/research/2026-11-25/consensus/: a copy of a coin another of our wallets had bought in the hour before
    /// made +16.7% a copy against +10.8% alone). Both units then hold the coin; each sells its own tokens, and the
    /// shared token account stays open while either holds it (`pos::close_on_sale`).
    pub join_others: bool,
    /// Copy its buys of SOL-priced coins too (Nov 22, the CqCAzte8 unit), with SOL on their curve; off: only coins
    /// priced in another token, as wallet 4's unit has always copied.
    pub copy_sol_coins: bool,
    /// Separate exits for the SOL-coin copies (Nov 22, the CqCAzte8 unit: its SOL coins made the most with tp 2x / 120 s,
    /// its token coins with tp 3x / 420 s / stall 240): with `sol_exits`, a `sol_curve` position takes profit at
    /// `sol_take_profit`, sells at `sol_max_hold_s`, and has its own `sol_sell_pressure` and `sol_stall_s` (0 / [] off);
    /// the stop and its sale stay the unit's. Off: one exit for every position, as before.
    pub sol_exits: bool,
    pub sol_take_profit: f64,
    pub sol_max_hold_s: u64,
    pub sol_stall_s: u64,
    pub sol_sell_pressure: Vec<u64>,
    /// Pay only with a float (Nov 18): wrapped SOL is not an anchor, so no route starts from SOL (a
    /// coin whose quote is reached through a pool from SOL is skipped). TAB16RxX's copies paid from SOL
    /// lost 9.4% a copy on Oct 31 - Nov 14 (467), its float-paid ones made +5.6% over 18 days (370).
    pub float_only: bool,
    /// The ladder flip (`ladder.rs`): watch every pump launch's create slot;
    /// when enabled the copied wallet's buys are not copied (a unit of its own).
    pub ladder: crate::ladder::LadderCfg,
}

impl Default for LongCfg {
    fn default() -> Self {
        Self {
            mode: Mode::Log,
            copy_wallet: "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg".into(),
            wallet_file: "/etc/rugsnipe/keys/long-wallet.json".into(),
            min_sol: 1.45,
            stake_sol: 1.0,
            take_profit: 2.0,
            stop: 0.8,
            max_hold_s: 1790,
            max_open: 4,
            max_premium: 0.25,
            daily_stop_sol: 3.0,
            floats: vec!["3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh".into()],
            rpc_url: String::new(),
            hot_config: "/etc/rugsnipe/rugsnipe.toml".into(),
            api_keys: "/etc/rugsnipe/keys/api-keys.toml".into(),
            buy_senders: vec!["nozomi".into()],
            sell_senders: vec![],
            rpc_send: true,
            buy_tip_lamports: 1_000_000,
            sell_tip_lamports: 1_000_000,
            buy_cu_price: 2_000_000,
            sell_cu_price: 1_000_000,
            cu_limit: 300_000,
            sell_slack_tp: 0.15,
            sell_slack_exit: 0.30,
            max_sell_fail_sol: 0.01,
            paper_land_slots: 1,
            reserve_sol: 0.05,
            follow_its_sell: true,
            follow_early_s: vec![],
            follow_early_below: 1.5,
            float_stake_sol: 0.0,
            float_min_frac: 1.0,
            min_fee_bps: 0,
            sell_pressure: vec![],
            stall_s: 0,
            state_dir: "/var/lib/rugsnipe-long".into(),
            price_api: crate::oracle::API.into(),
            tp_from_fill: false,
            dip_drop: 0.0,
            dip_within_s: 60,
            dip_stake_sol: 0.0,
            dip_take_profit: 1.5,
            dip_max_hold_s: 900,
            dip_float_only: false,
            other_state_dirs: vec![],
            join_others: false,
            copy_sol_coins: false,
            sol_exits: false,
            sol_take_profit: 2.0,
            sol_max_hold_s: 120,
            sol_stall_s: 0,
            sol_sell_pressure: vec![],
            float_only: false,
            ladder: crate::ladder::LadderCfg::default(),
        }
    }
}

impl LongCfg {
    pub fn from_toml_str(s: &str) -> Result<Self, String> {
        let c: Self = toml::from_str(s).map_err(|e| e.to_string())?;
        c.validate()?;
        Ok(c)
    }

    pub fn validate(&self) -> Result<(), String> {
        let bad = |w: &str| Err(format!("long.toml: {w}"));
        if self.ladder.enabled {
            self.ladder.validate().map_err(|e| format!("long.toml: {e}"))?;
        }
        if self.copy_wallet.parse::<pump_codec::Pubkey>().is_err() {
            return bad("copy_wallet is not a pubkey");
        }
        if !(0.01..=100.0).contains(&self.stake_sol) {
            return bad("stake_sol must be in [0.01, 100]");
        }
        if !(self.take_profit > 1.0 && self.take_profit < 100.0) {
            return bad("take_profit must be above 1");
        }
        // 0 = no stop: the trip ends at the take profit or the hold (2026-11-04: since wallet 4 dropped its
        // timer and sells early, the 0.8 stop sold into its own sale; analysis/research/2026-10-31/since_stop)
        if !(self.stop >= 0.0 && self.stop < 1.0) {
            return bad("stop must be in [0, 1); 0 = no stop");
        }
        if !(0.0..=1.0).contains(&self.max_premium) {
            return bad("max_premium must be in [0, 1]");
        }
        if !(0.0..1.0).contains(&self.sell_slack_tp) || !(0.0..1.0).contains(&self.sell_slack_exit)
        {
            return bad("sell slacks must be in [0, 1)");
        }
        if self.paper_land_slots > 50 {
            return bad("paper_land_slots must be in 0..=50");
        }
        if self.max_open == 0 || self.max_open > 50 {
            return bad("max_open must be in 1..=50");
        }
        if self.max_hold_s == 0 {
            return bad("max_hold_s must be positive");
        }
        if !(0.0..0.9).contains(&self.dip_drop) {
            return bad("dip_drop must be in [0, 0.9)");
        }
        if self.dip_drop > 0.0 && !(5..=900).contains(&self.dip_within_s) {
            return bad("dip_within_s must be in 5..=900");
        }
        if !(0.0..=100.0).contains(&self.dip_stake_sol) {
            return bad("dip_stake_sol must be in [0, 100]");
        }
        if self.sol_exits && (self.sol_take_profit <= 1.0 || self.sol_max_hold_s == 0) {
            return bad("sol_exits needs sol_take_profit > 1 and sol_max_hold_s > 0");
        }
        if !self.sol_sell_pressure.is_empty() && self.sol_sell_pressure.len() != 3 {
            return bad("sol_sell_pressure is [] or [sells, window_s, from_s]");
        }
        if self.dip_drop > 0.0 && (self.dip_take_profit <= 1.0 || self.dip_max_hold_s == 0) {
            return bad("the dip leg needs dip_take_profit > 1 and dip_max_hold_s > 0");
        }
        for f in &self.floats {
            if f.parse::<pump_codec::Pubkey>().is_err() {
                return bad("floats must be mints");
            }
        }
        // exactly one: an empty list means every enabled sender (send.rs),
        // and two buys landing would double the position
        if self.mode == Mode::On && self.buy_senders.len() != 1 {
            return bad("buy_senders must name exactly one sender in mode on");
        }
        if !(0.0..=10.0).contains(&self.reserve_sol) {
            return bad("reserve_sol must be in [0, 10]");
        }
        if !(0.0..=100.0).contains(&self.float_stake_sol) {
            return bad("float_stake_sol must be in [0, 100]");
        }
        if self.min_fee_bps > 10_000 {
            return bad("min_fee_bps must be in [0, 10000]");
        }
        if !(self.float_min_frac > 0.0 && self.float_min_frac <= 1.0) {
            return bad("float_min_frac must be in (0, 1]");
        }
        if !(self.follow_early_s.is_empty()
            || (self.follow_early_s.len() == 2 && self.follow_early_s[0] < self.follow_early_s[1]))
        {
            return bad("follow_early_s must be [] or [from, to] seconds with from < to");
        }
        if !(self.sell_pressure.is_empty()
            || (self.sell_pressure.len() == 3 && self.sell_pressure[0] > 0 && self.sell_pressure[1] > 0))
        {
            return bad("sell_pressure must be [] or [n, w, from] with n > 0 and w > 0 seconds");
        }
        if !(self.follow_early_below > 0.0) {
            return bad("follow_early_below must be positive");
        }
        Ok(())
    }

    /// Our stake, lamports, for a route from `anchor` (a float or wSOL).
    pub fn stake_for(&self, float: bool) -> u64 {
        let s = if float && self.float_stake_sol > 0.0 {
            self.float_stake_sol
        } else {
            self.stake_sol
        };
        (s * 1e9) as u64
    }

    /// What a float buy spends: `(stake, amount_in)` as asked when the
    /// float holds it, scaled down to all it holds when that is at least
    /// `float_min_frac` of it, `None` (skip) under that.
    pub fn float_buy(&self, stake: u64, amount_in: u64, held: u64) -> Option<(u64, u64)> {
        if held >= amount_in {
            Some((stake, amount_in))
        } else if amount_in > 0 && held as f64 >= amount_in as f64 * self.float_min_frac && self.float_min_frac < 1.0 {
            Some(((stake as f64 * held as f64 / amount_in as f64) as u64, held))
        } else {
            None
        }
    }

    pub fn copy_pk(&self) -> pump_codec::Pubkey {
        self.copy_wallet.parse().expect("validated")
    }

    pub fn float_pks(&self) -> Vec<pump_codec::Pubkey> {
        self.floats.iter().filter_map(|f| f.parse().ok()).collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_float_under_the_stake_buys_with_what_it_holds() {
        // the default: the whole stake or nothing
        let c = LongCfg::default();
        assert_eq!(c.float_buy(500, 1000, 1000), Some((500, 1000)));
        assert_eq!(c.float_buy(500, 1000, 999), None);
        // half the stake or more: all it holds, the stake scaled with it
        let c = LongCfg::from_toml_str("float_min_frac = 0.5").unwrap();
        assert_eq!(c.float_buy(500_000_000, 1000, 2000), Some((500_000_000, 1000)));
        assert_eq!(c.float_buy(500_000_000, 1000, 700), Some((350_000_000, 700)));
        assert_eq!(c.float_buy(500_000_000, 1000, 500), Some((250_000_000, 500)));
        assert_eq!(c.float_buy(500_000_000, 1000, 499), None);
        assert_eq!(c.float_buy(500_000_000, 0, 0), Some((500_000_000, 0)));
    }

    #[test]
    fn defaults_validate_and_parse() {
        LongCfg::default().validate().unwrap();
        let c = LongCfg::from_toml_str("mode = \"on\"\nstake_sol = 0.5\nmax_open = 2\n").unwrap();
        assert_eq!(c.mode, Mode::On);
        assert_eq!(c.max_open, 2);
        assert!(LongCfg::from_toml_str("float_min_frac = 0.0").is_err());
        assert!(LongCfg::from_toml_str("stop = 1.2").is_err());
        assert!(LongCfg::from_toml_str("stop = 0.0").is_ok());
        assert!(LongCfg::from_toml_str("stop = -0.1").is_err());
        assert!(LongCfg::from_toml_str("mode = \"on\"\nbuy_senders = [\"a\", \"b\"]").is_err());
        // an empty list would mean every enabled sender: several buys
        assert!(LongCfg::from_toml_str("mode = \"on\"\nbuy_senders = []").is_err());
        assert!(
            LongCfg::from_toml_str("buy_senders = []").is_ok(),
            "paper: not sent"
        );
        assert!(LongCfg::from_toml_str("nope = 1").is_err());
    }

    /// The dip unit's example (Nov 19) parses and passes `validate`; a dip_drop out of range is refused.
    #[test]
    fn the_dip_units_example_config_is_valid() {
        let c = LongCfg::from_toml_str(include_str!("../../../config/long-dip.example.toml")).unwrap();
        assert!((c.dip_drop - 0.10).abs() < 1e-9 && c.dip_within_s == 60 && c.tp_from_fill && !c.follow_its_sell);
        assert!(c.validate().is_ok(), "{:?}", c.validate());
        let mut bad = c.clone();
        bad.dip_drop = 0.95;
        assert!(bad.validate().is_err());
    }

    /// FatoU1bj's unit (Nov 24): its own exit (tp 1.5x, 15 s, behind its sale) parses and passes `validate`, and every
    /// live example (eleven since Nov 25 late) validates and lists the other ten units' state dirs, never its own.
    #[test]
    fn the_flippers_example_config_is_valid_and_the_units_skip_each_other() {
        let c = LongCfg::from_toml_str(include_str!("../../../config/long-fat.live.example.toml")).unwrap();
        assert!(c.validate().is_ok(), "{:?}", c.validate());
        assert!((c.take_profit - 1.5).abs() < 1e-9 && c.max_hold_s == 15 && c.follow_its_sell && c.follow_early_s.is_empty());
        assert!((c.stake_sol - 0.3).abs() < 1e-9 && c.max_open == 4 && c.stall_s == 0 && c.sell_pressure.is_empty() && c.copy_sol_coins && !c.sol_exits);
        for src in [
            include_str!("../../../config/long.live.example.toml"),
            include_str!("../../../config/long-cq.live.example.toml"),
            include_str!("../../../config/long-cgy.live.example.toml"),
            include_str!("../../../config/long-3xe.live.example.toml"),
            include_str!("../../../config/long-6lw.live.example.toml"),
            include_str!("../../../config/long-6nn.live.example.toml"),
            include_str!("../../../config/long-gqw.live.example.toml"),
            include_str!("../../../config/long-fat.live.example.toml"),
            include_str!("../../../config/long-htk.live.example.toml"),
            include_str!("../../../config/long-3si.live.example.toml"),
            include_str!("../../../config/long-bng.live.example.toml"),
        ] {
            let u = LongCfg::from_toml_str(src).unwrap();
            assert!(u.validate().is_ok(), "{}: {:?}", u.state_dir, u.validate());
            assert_eq!(u.other_state_dirs.len(), 10, "{}", u.state_dir);
            assert!(!u.other_state_dirs.contains(&u.state_dir), "{}", u.state_dir);
        }
    }
}
