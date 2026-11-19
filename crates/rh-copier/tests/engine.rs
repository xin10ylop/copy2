//! The engine's rules on made-up curve trades (no chain): copy filters, every exit, the skips, the retry.
use rh_copier::config::Config;
use rh_copier::engine::{Action, CurveSt, Engine, PosState, Trade, FEE, K, V0};

const ME: &str = "0x00000000000000000000000000000000000000aa";
const A: &str = "0x9a3955a122ab8a649a8511df2dce169471fd0ec1"; // tp 4, 600 s, coins under 0.5 ETH, its buys 0.1+
const B: &str = "0x5bc235acecff3dde394f4bfc696f7c35efd502f0"; // tp 3.5, 600 s, sell pressure 10 / 30 s from 30 s
const C: &str = "0xc54d3914f91f984d61b63d491f38934c4e706b79"; // tp 2.5, 300 s, sell pressure 8 / 60 s, stall 240
const X: &str = "0x00000000000000000000000000000000000000bb"; // somebody else

fn cfg(extra: &str) -> Config {
    let s = format!(r#"
mode = "on"
ws_url = "wss://x"
rpc_url = "https://x"
wallet_file = "/dev/null"
stake_eth = 0.02
max_open = 2
daily_stop_eth = 0.05
{extra}
[[leaders]]
address = "{A}"
min_its_eth = 0.1
max_curve_eth = 0.5
max_premium = 1.5
take_profit = 4.0
hold_s = 600
[[leaders]]
address = "{B}"
min_its_eth = 0.05
max_premium = 1.5
take_profit = 3.5
hold_s = 600
sell_pressure = [10, 30, 30]
[[leaders]]
address = "{C}"
min_its_eth = 0.03
take_profit = 2.5
hold_s = 300
sell_pressure = [8, 60, 30]
stall_s = 240
"#);
    let c: Config = toml::from_str(&s).unwrap(); c.check().unwrap(); c
}
fn tr(curve: &str, buy: bool, user: &str, quote: f64, net_q: f64, tokens: f64, t_ms: u64) -> Trade {
    Trade { curve: curve.into(), buy, user: user.into(), quote, net_q, tokens, block: 1, t_ms }
}
/// an ETH curve that holds `real` ETH (q·t = 1.68e9, from 1.68 ETH and 1B tokens)
fn curve(real: f64) -> CurveSt { let q = V0 + real; CurveSt { q, t: K / q, real_q: real } }
/// a buy of `eth` (fee 1% + tax 1% out of the quote, as most Nov 18 buys) on a curve holding `real` ETH
fn buy_at(c: &str, user: &str, eth: f64, real: f64, t: u64) -> Trade { let st = curve(real); let net = eth * 0.98; tr(c, true, user, eth, net, st.t - K / (st.q + net), t) }
/// the same on the engine's own copy of the curve
fn buy_on(e: &Engine, c: &str, user: &str, eth: f64, t: u64) -> Trade { let st = e.curves[c]; let net = eth * 0.98; tr(c, true, user, eth, net, st.t - st.q * st.t / (st.q + net), t) }
fn sell_on(e: &Engine, c: &str, user: &str, tokens: f64, t: u64) -> Trade { let st = e.curves[c]; let g = st.q - st.q * st.t / (st.t + tokens); tr(c, false, user, g * 0.98, g, tokens, t) }

/// the leader buys (on a curve holding `real` ETH before it), we buy at once, our buy fills: an open position
fn open(e: &mut Engine, c: &str, leader: &str, its: f64, real: f64, t: u64) {
    let a = e.on_trade(&buy_at(c, leader, its, real, t), t);
    match &a[..] { [Action::Buy { eth, min_tokens, .. }] => { assert_eq!(*eth, 0.02); assert!(*min_tokens > 0.0) } x => panic!("{x:?}") }
    e.on_bought(c, 1e7, t + 400);
    assert_eq!(e.pos[c].state, PosState::Open);
}
fn sold(a: &[Action]) -> Option<&'static str> { a.iter().find_map(|x| if let Action::Sell { why, .. } = x { Some(*why) } else { None }) }

#[test]
fn copies_a_big_enough_buy_at_once_at_its_exact_price() {
    let mut e = Engine::new(cfg(""), ME);
    open(&mut e, "0xc1", A, 0.1, 0.1, 1_000);
    let p = &e.pos["0xc1"]; assert_eq!(p.leader, A);
    assert!((p.its_price / curve(0.1 + 0.098).price() - 1.0).abs() < 1e-9);   // the price its buy left, from its buy alone
}

#[test]
fn the_curve_is_rebuilt_from_one_buy_and_other_quote_tokens_are_refused() {
    for real in [0.0, 0.3, 1.7, 3.5] { for eth in [0.001, 0.05, 0.4] {
        let b = buy_at("0xc1", A, eth, real, 0); let c = CurveSt::after_buy(&b).unwrap();
        assert!((c.real_q - (real + eth * 0.98)).abs() < 1e-6, "{real} {eth}"); assert!((c.q * c.t / K - 1.0).abs() < 1e-9);
    } }
    // a curve quoted in another token (one seen on Nov 18: 147.6 x 1e9, graduation at 369): not an ETH curve
    let (q0, net) = (147.6 + 10.0, 2.0); let n = 1.476e11 / q0 - 1.476e11 / (q0 + net);
    assert!(CurveSt::after_buy(&tr("0xc2", true, A, net / 0.98, net, n, 0)).is_none());
    // a 6-decimal quote token (USDG): the amounts read as ~1e-12 "ETH"
    assert!(CurveSt::after_buy(&tr("0xc3", true, A, 5e-11, 4.9e-11, 3e6, 0)).is_none());
    let mut e = Engine::new(cfg(""), ME);
    assert!(e.on_trade(&tr("0xc2", true, A, net / 0.98, net, n, 0), 0).is_empty());
}

#[test]
fn skips_small_buys_late_coins_and_near_graduation() {
    let mut e = Engine::new(cfg(""), ME);
    assert!(e.on_trade(&buy_at("0xc1", A, 0.09, 0.0, 0), 0).is_empty());        // under its 0.1 minimum
    assert!(e.on_trade(&buy_at("0xc1", X, 1.0, 0.0, 0), 0).is_empty());         // not a copied wallet
    assert!(e.on_trade(&buy_at("0xc2", A, 0.1, 0.6, 0), 0).is_empty());         // 0.6 ETH before its buy: over A's 0.5
    assert!(e.pos.is_empty());
    assert!(e.on_trade(&buy_at("0xc3", B, 0.1, 3.75, 0), 0).is_empty());        // 3.85 after it: past the 3.8 guard
}

#[test]
fn one_copy_per_coin_and_max_open() {
    let mut e = Engine::new(cfg(""), ME);
    open(&mut e, "0xc1", A, 0.1, 0.1, 0);
    let b = buy_on(&e, "0xc1", B, 0.1, 10);
    assert!(e.on_trade(&b, 10).iter().all(|a| !matches!(a, Action::Buy { .. })));
    open(&mut e, "0xc2", B, 0.1, 0.1, 20);
    assert!(e.on_trade(&buy_at("0xc3", C, 0.1, 0.1, 30), 30).is_empty());      // max_open 2
}

#[test]
fn take_profit_at_its_multiple() {
    let mut e = Engine::new(cfg(""), ME);
    open(&mut e, "0xc1", C, 0.05, 0.05, 0);
    let p0 = e.pos["0xc1"].its_price;
    let mut t = 1_000;
    loop {   // others buy until the price is 2.5x its price (C's take profit)
        let b = buy_on(&e, "0xc1", X, 0.05, t); let a = e.on_trade(&b, t); t += 100;
        let r = e.curves["0xc1"].price() / p0;
        if r >= 2.5 { assert_eq!(sold(&a), Some("take_profit")); break }
        assert!(sold(&a).is_none(), "sold at {r}");
    }
    assert_eq!(e.pos["0xc1"].state, PosState::Selling);
    let pnl = e.on_sold("0xc1", Some(0.04), t).unwrap();
    assert!((pnl - 0.02).abs() < 1e-12); assert!(e.pos.is_empty());
}

#[test]
fn time_exit_on_the_clock() {
    let mut e = Engine::new(cfg(""), ME);
    open(&mut e, "0xc1", A, 0.1, 0.1, 0);
    assert!(e.tick(599_000).is_empty());
    assert_eq!(sold(&e.tick(600_000)), Some("time"));
}

#[test]
fn sell_pressure_counts_others_only_and_waits_for_its_start() {
    let mut e = Engine::new(cfg(""), ME);
    open(&mut e, "0xc1", B, 0.1, 0.1, 0);
    for _ in 0..30 { let b = buy_on(&e, "0xc1", X, 0.01, 1_000); e.on_trade(&b, 1_000); }  // tokens for others to sell
    // 40 net sales by others in the first 30 s: too early (B's rule starts at 30 s)
    for i in 0..40 { let s = sell_on(&e, "0xc1", X, 1e5, 2_000 + i); assert!(sold(&e.on_trade(&s, 2_000 + i)).is_none()); }
    // they fall out of the 30 s window; then 10 sales after 30 s trip it (the leader's own sales do not count)
    for i in 0..5 { let s = sell_on(&e, "0xc1", B, 1e5, 70_000 + i); assert!(sold(&e.on_trade(&s, 70_000 + i)).is_none()); }
    let mut hit = None;
    for i in 0..10 { let s = sell_on(&e, "0xc1", X, 1e5, 71_000 + i); hit = sold(&e.on_trade(&s, 71_000 + i)); if hit.is_some() { assert_eq!(i, 9) } }
    assert_eq!(hit, Some("sell_pressure"));
}

#[test]
fn stall_after_no_new_high() {
    let mut e = Engine::new(cfg(""), ME);
    open(&mut e, "0xc1", C, 0.05, 0.05, 0);
    let b = buy_on(&e, "0xc1", X, 0.05, 10_000); e.on_trade(&b, 10_000);  // a new high at 10 s
    assert!(e.tick(249_000).is_empty());
    assert_eq!(sold(&e.tick(250_000)), Some("stall"));                         // 240 s without a new high
}

#[test]
fn its_sale_never_is_ignored_and_always_follows() {
    let mut e = Engine::new(cfg(""), ME);
    open(&mut e, "0xc1", A, 0.1, 0.1, 0);
    let s = sell_on(&e, "0xc1", A, 1e6, 60_000);
    assert!(sold(&e.on_trade(&s, 60_000)).is_none());
    let mut c = cfg(""); c.leaders[0].its_sale = "always".into();
    let mut e = Engine::new(c, ME);
    open(&mut e, "0xc1", A, 0.1, 0.1, 0);
    let s = sell_on(&e, "0xc1", A, 1e6, 60_000);
    assert_eq!(sold(&e.on_trade(&s, 60_000)), Some("its_sell"));
}

#[test]
fn graduation_guard_sells_before_the_pool() {
    let mut e = Engine::new(cfg(""), ME);
    open(&mut e, "0xc1", B, 0.1, 0.1, 0);
    let mut c = e.curves["0xc1"]; c.real_q = 3.85; e.set_curve("0xc1", c);
    assert_eq!(sold(&e.tick(5_000)), Some("graduation_guard"));
}

#[test]
fn a_failed_sale_is_retried_after_5_s() {
    let mut e = Engine::new(cfg(""), ME);
    open(&mut e, "0xc1", A, 0.1, 0.1, 0);
    assert_eq!(sold(&e.tick(600_000)), Some("time"));
    assert!(e.tick(600_500).is_empty());                       // selling: no second order
    assert!(e.on_sold("0xc1", None, 601_000).is_none());
    assert!(e.tick(603_000).is_empty());                       // cooling down
    assert_eq!(sold(&e.tick(606_000)), Some("time"));
}

#[test]
fn a_failed_buy_frees_the_slot_and_daily_stop_halts_new_copies() {
    let mut e = Engine::new(cfg(""), ME);
    assert_eq!(e.on_trade(&buy_at("0xc1", A, 0.1, 0.1, 0), 0).len(), 1);
    e.on_bought("0xc1", 0.0, 500); assert!(e.pos.is_empty());
    open(&mut e, "0xc2", B, 0.1, 0.1, 1_000); e.tick(601_000); e.on_sold("0xc2", Some(0.0), 601_500);   // -0.02
    open(&mut e, "0xc3", B, 0.1, 0.1, 602_000); e.tick(1_202_000); e.on_sold("0xc3", Some(0.0), 1_202_500); // -0.04
    open(&mut e, "0xc4", B, 0.1, 0.1, 1_203_000); e.tick(1_803_000); e.on_sold("0xc4", Some(0.0), 1_803_500); // -0.06: stop 0.05
    assert!(e.on_trade(&buy_at("0xc5", B, 0.1, 0.1, 1_900_000), 1_900_000).is_empty());
    assert!(e.on_trade(&buy_at("0xc6", B, 0.1, 0.1, 86_400_000), 86_400_000).is_empty()); // still today until a sale books the new day
}

#[test]
fn decodes_logs_and_builds_calldata() {
    use rh_copier::chain::*;
    let log = serde_json::json!({"address": "0xC1C1c1c1C1c1C1c1C1C1c1c1c1C1c1C1C1c1c1c1", "blockNumber": "0x10",
        "topics": [topic_buy(), format!("0x{:0>64}", "77"), format!("0x{:0>64}", &A[2..])],
        "data": format!("0x{:064x}{:064x}{:064x}{:064x}", 100_000_000_000_000_000u128, 5_000_000u128 * 1_000_000_000_000_000_000, 1_000_000_000_000_000u128, 2_000_000_000_000_000u128)});
    let t = decode_trade(&log, 7).unwrap();
    assert!(t.buy); assert_eq!(t.user, A); assert_eq!(t.curve, "0xc1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1");
    assert!((t.quote - 0.1).abs() < 1e-12); assert!((t.net_q - 0.097).abs() < 1e-12); assert!((t.tokens - 5e6).abs() < 1e-3); assert_eq!(t.block, 16);
    let d = buy_data(wei(0.02), tok_units(1.0), ME);
    assert_eq!(d.len(), 2 + 8 + 3 * 64); assert!(d.ends_with(&ME[2..]));
    assert_eq!(&d[10..74], &format!("{:064x}", 20_000_000_000_000_000u128));
    assert_eq!(approve_data(A).len(), 2 + 8 + 128);
}

#[test]
fn the_price_limit_is_against_the_price_its_buy_left() {
    let mut e = Engine::new(cfg(""), ME);
    let b = buy_at("0xc1", A, 0.1, 0.1, 0); let its = CurveSt::after_buy(&b).unwrap();
    match &e.on_trade(&b, 0)[..] {
        [Action::Buy { min_tokens, .. }] => {
            // what the stake buys once the price is 1.5x its price (A's limit), less 1%: a fill above that reverts
            let at15 = CurveSt { q: its.q * 1.5f64.sqrt(), t: its.t / 1.5f64.sqrt(), real_q: 0.0 };
            assert!((min_tokens - at15.tokens_for(0.02, FEE) * 0.99).abs() < 1.0);
            assert!(*min_tokens < its.tokens_for(0.02, FEE));
        }
        x => panic!("{x:?}"),
    }
    assert!((e.pos["0xc1"].its_price - its.price()).abs() < 1e-18);
}

#[test]
fn a_wallet_skipped_by_its_own_filter_does_not_hide_another_wallets_copy() {
    // Nov 19 00:44 UTC: wallets 1 and 3 bought the same coin in one block; wallet 1's buy was over its coin-type limit
    // (0.65 ETH in the curve, max 0.5) and marked the coin seen, so wallet 3's buy was dropped
    let mut e = Engine::new(cfg(""), ME);
    assert!(e.on_trade(&buy_at("0xc1", A, 0.1, 0.65, 0), 0).is_empty());           // wallet A: over its 0.5 limit
    let b = buy_on(&e, "0xc1", C, 0.12, 1);
    assert!(matches!(&e.on_trade(&b, 1)[..], [Action::Buy { .. }]));                 // wallet C (any coin): copied
    let b = buy_on(&e, "0xc1", B, 0.1, 2);
    assert!(e.on_trade(&b, 2).iter().all(|a| !matches!(a, Action::Buy { .. })));     // and the coin is now seen
}
