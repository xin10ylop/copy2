//! The engine in paper mode on wallet 4's real wSOL multi-hop buy: the
//! trigger, the paper fill once the landing slot is over, and each exit.

use rugsnipe_long::chain::Rpc;
use rugsnipe_long::config::{LongCfg, Mode};
use rugsnipe_long::engine::Engine;
use rugsnipe_long::feed::Src;
use rugsnipe_long::oracle::{now_ms, Oracle};
use rugsnipe_long::pos::{Reason, State};
use rugsnipe_long::txlite::TxLite;

fn fx(name: &str) -> TxLite {
    let p = format!("{}/tests/fixtures/{name}.json", env!("CARGO_MANIFEST_DIR"));
    let v: serde_json::Value = serde_json::from_str(&std::fs::read_to_string(p).unwrap()).unwrap();
    TxLite::from_rpc_json(&v).unwrap()
}

fn engine(tag: &str) -> Engine {
    let dir = std::env::temp_dir().join(format!("long-engine-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    let cfg = LongCfg {
        mode: Mode::Log,
        state_dir: dir.to_string_lossy().into(),
        ..Default::default()
    };
    // a copied route from wrapped SOL needs no chain read
    Engine::new(
        cfg,
        Default::default(),
        None,
        Rpc::new("http://127.0.0.1:9"),
        Oracle::default(),
        None,
        None,
    )
    .unwrap()
}

/// Move position 0's curve to `px` times its reference price (constant
/// product: both reserves move, as a trade event reports them).
fn price_to(e: &mut Engine, px: f64) {
    let p = &mut e.book.positions[0];
    let k = p.vt_ref as f64 * p.vq_ref as f64;
    p.vt = (p.vt_ref as f64 / px.sqrt()) as u64;
    p.vq = (k / p.vt as f64) as u64;
}

fn opened(tag: &str) -> Engine {
    let mut e = engine(tag);
    let tx = fx("w4_buy_wsol_multihop");
    e.on_tx(Src::Copied, &tx);
    assert_eq!(e.book.positions.len(), 1, "a paper position for its buy");
    let p = &e.book.positions[0];
    assert!(p.paper && p.state == State::Buying && p.how == "copied");
    // the landing slot is not over: no fill yet
    e.on_slot(tx.slot + 1);
    e.on_tick(now_ms());
    assert_eq!(e.book.positions[0].state, State::Buying);
    e.on_slot(tx.slot + 2);
    e.on_tick(now_ms());
    let p = &e.book.positions[0];
    assert_eq!(p.state, State::Open);
    assert!(p.tokens > 0);
    e
}

/// A paper sell fills at the end of the slot after the one it was sent
/// in, like a paper buy: the exit fires, the slot ends, the next one too.
fn land_sell(e: &mut Engine) {
    let s = e.book.positions[0].sell_land_slot;
    assert!(s > 0, "a paper sell is out");
    e.on_slot(s);
    e.on_tick(now_ms());
    assert_eq!(
        e.book.positions[0].state,
        State::Selling,
        "its slot is not over"
    );
    e.on_slot(s + 1);
    e.on_tick(now_ms());
}

#[test]
fn take_profit_closes_with_a_gain() {
    let mut e = opened("tp");
    price_to(&mut e, 2.1);
    e.on_tick(now_ms());
    let p = &e.book.positions[0];
    assert_eq!((p.state, p.reason), (State::Selling, Some(Reason::Tp)));
    land_sell(&mut e);
    let p = &e.book.positions[0];
    assert_eq!(p.state, State::Closed);
    assert_eq!(p.reason, Some(Reason::Tp));
    // 2.1x its price, less our own impact both ways and the fees
    assert!(
        p.net_lamports > 700_000_000 && p.net_lamports < 1_100_000_000,
        "{}",
        p.net_lamports
    );
    // the closed record went to closed.jsonl and the book file
    let dir = std::path::PathBuf::from(&e.cfg.state_dir);
    assert!(std::fs::read_to_string(dir.join("closed.jsonl"))
        .unwrap()
        .contains("\"tp\""));
    assert!(std::fs::read_to_string(dir.join("positions.json"))
        .unwrap()
        .contains("closed"));
}

#[test]
fn stop_closes_with_a_loss_and_time_after_the_hold() {
    let mut e = opened("stop");
    price_to(&mut e, 0.75);
    e.on_tick(now_ms());
    assert_eq!(e.book.positions[0].reason, Some(Reason::Stop));
    land_sell(&mut e);
    let p = &e.book.positions[0];
    assert_eq!(p.state, State::Closed);
    assert!(
        p.net_lamports < -200_000_000 && p.net_lamports > -400_000_000,
        "{}",
        p.net_lamports
    );

    let mut e = opened("time");
    let seen = e.book.positions[0].seen_ms;
    e.on_tick(seen + 1_789_000);
    assert_eq!(e.book.positions[0].state, State::Open);
    e.on_tick(seen + 1_790_000);
    assert_eq!(e.book.positions[0].reason, Some(Reason::Time));
    assert_eq!(e.book.positions[0].state, State::Selling);
}

/// `stop = 0` is no stop: a coin at a third of its price is held, and the
/// hold still ends the trip (2026-11-04: wallet 4 sells early now, and the
/// 0.8 stop sold into its sale; since_stop/nostop_new.py).
#[test]
fn no_stop_holds_through_a_drop_until_the_hold() {
    let mut e = opened("nostop");
    e.cfg.stop = 0.0;
    price_to(&mut e, 0.3);
    e.on_tick(now_ms());
    assert_eq!(e.book.positions[0].state, State::Open);
    assert_eq!(e.book.positions[0].reason, None);
    let seen = e.book.positions[0].seen_ms;
    e.on_tick(seen + 1_790_000);
    assert_eq!(e.book.positions[0].reason, Some(Reason::Time));
}

/// A paper sell is priced on the curve at the end of the slot after the
/// trade that fired it, not on that trade's own state: a real sell lands a
/// slot later, and on a frenzy coin the price has moved by then.
#[test]
fn a_paper_sell_fills_a_slot_later_on_the_curve_then() {
    let mut e = opened("selllate");
    price_to(&mut e, 2.1);
    e.on_slot(e.book.positions[0].fill_slot() + 5);
    e.on_tick(now_ms());
    let p = &e.book.positions[0];
    assert_eq!(p.state, State::Selling);
    assert_eq!(p.sell_land_slot, p.fill_slot() + 6);
    // the price falls back to 1.5x before the landing slot ends: that is
    // the price it gets
    price_to(&mut e, 1.5);
    land_sell(&mut e);
    let p = &e.book.positions[0];
    assert_eq!((p.state, p.reason), (State::Closed, Some(Reason::Tp)));
    assert!(
        p.net_lamports > 300_000_000 && p.net_lamports < 500_000_000,
        "about 1.5x less fees: {}",
        p.net_lamports
    );
}

#[test]
fn its_second_buy_and_max_open_and_kill_are_skipped() {
    let mut e = opened("skips");
    // the same transaction again: its second buy of the coin, not a second position
    e.on_tx(Src::Copied, &fx("w4_buy_wsol_multihop"));
    assert_eq!(e.book.positions.len(), 1);
    // KILL: no new buys
    let mut e = engine("kill");
    std::fs::create_dir_all(&e.cfg.state_dir).unwrap();
    std::fs::write(std::path::Path::new(&e.cfg.state_dir).join("KILL"), b"").unwrap();
    e.on_tx(Src::Copied, &fx("w4_buy_wsol_multihop"));
    assert!(e.book.positions.is_empty());
    // max_open reached
    let mut e = engine("max");
    e.cfg.max_open = 1;
    e.on_tx(Src::Copied, &fx("w4_buy_wsol_multihop"));
    e.on_tx(Src::Copied, &fx("w4_buy_wbtc_multihop"));
    assert_eq!(e.book.positions.len(), 1);
}

#[test]
fn a_restart_keeps_the_open_position() {
    let e = opened("restart");
    let dir = e.cfg.state_dir.clone();
    drop(e);
    let cfg = LongCfg {
        mode: Mode::Log,
        state_dir: dir,
        ..Default::default()
    };
    let e2 = Engine::new(
        cfg,
        Default::default(),
        None,
        Rpc::new("http://127.0.0.1:9"),
        Oracle::default(),
        None,
        None,
    )
    .unwrap();
    assert_eq!(e2.book.positions.len(), 1);
    assert_eq!(e2.book.positions[0].state, State::Open);
    assert!(
        e2.book.positions[0].buy_route().is_some(),
        "the stored route reads back"
    );
}

/// Our own transaction on position 0 (the engine's wallet is the default
/// key): signature `sig`, landed failed or not, fee, and the coin balance
/// change.
fn ours(e: &Engine, sig: u8, err: bool, fee: u64, coin_pre: u64, coin_post: u64) -> TxLite {
    let me = pump_codec::Pubkey::default();
    let mint = e.book.positions[0].mint_pk();
    TxLite {
        sig: vec![sig; 64],
        slot: 1,
        err,
        fee,
        keys: vec![me],
        outer: vec![],
        inner: vec![],
        pre_lamports: vec![1_000_000_000],
        post_lamports: vec![1_000_000_000 - fee],
        tokens: vec![rugsnipe_long::txlite::TokBal {
            index: 1,
            mint,
            owner: me,
            program: pump_codec::constants::TOKEN_2022_PROGRAM_ID,
            pre: coin_pre,
            post: coin_post,
        }],
    }
}

fn b58(sig: u8) -> String {
    bs58::encode(vec![sig; 64]).into_string()
}

/// 2026-10-27, the hot bot's 2RR6sfbi: a sell that kept failing was re-sent
/// 405 times. Here failed sells go again at once three times (the exit
/// matters and the floor drops each time), then wait 5 s, 30 s and 2 min, and
/// past `max_sell_fail_sol` of failed fees every 10 min; never given up.
#[test]
fn a_sell_that_keeps_failing_backs_off_instead_of_spending() {
    let mut e = opened("sellfail");
    e.cfg.mode = Mode::On;
    e.cfg.max_sell_fail_sol = 0.001;
    {
        let p = &mut e.book.positions[0];
        p.paper = false;
        p.tokens = 5_000;
    }
    price_to(&mut e, 2.5);
    let t0 = now_ms();
    for k in 1..=3u8 {
        let p = &mut e.book.positions[0];
        p.state = State::Selling;
        p.sell_sigs.push(b58(k));
        let tx = ours(&e, k, true, 300_005, 5_000, 5_000);
        e.on_tx(Src::Ours, &tx);
        let p = &e.book.positions[0];
        assert_eq!((p.state, p.sell_tries), (State::Open, k as u32));
    }
    let p = &e.book.positions[0];
    assert_eq!(p.costs, 3 * 300_005);
    let wait = p.sell_next_ms.saturating_sub(t0);
    assert!(
        (4_000..=6_000).contains(&wait),
        "the 4th try waits 5 s: {wait}"
    );
    // within the wait nothing is sent (an attempt here would fail to send and count a try)
    e.on_tick(t0 + 1_000);
    assert_eq!(e.book.positions[0].sell_tries, 3);
    // past it the exit is tried again (no wallet here: it cannot be sent).
    // A send failure is not a landed failure: the floor stays where it is
    // (`sell_tries`), and the sell is retried after a short wait
    e.on_tick(t0 + 6_000);
    let p = &e.book.positions[0];
    assert_eq!((p.sell_tries, p.send_fails), (3, 1));
    assert!(p.sell_next_ms > t0 + 6_000 && p.sell_next_ms <= t0 + 7_000);
    // one more failure crosses the 0.001 SOL cap: every 10 min from now
    let p = &mut e.book.positions[0];
    p.state = State::Selling;
    p.sell_sigs.push(b58(9));
    let tx = ours(&e, 9, true, 300_005, 5_000, 5_000);
    e.on_tx(Src::Ours, &tx);
    let p = &e.book.positions[0];
    assert!(p.costs >= 1_000_000);
    assert!(p.sell_next_ms >= now_ms() + 590_000, "10 min after the cap");
    assert!(p.live(), "never given up: the coins are still ours to sell");
}

/// A buy not seen within 90 s is given up as dropped; if it lands after all,
/// the position reopens on the tokens it bought instead of leaving them in
/// the wallet unmanaged.
#[test]
fn a_dropped_buy_that_lands_late_reopens() {
    let mut e = opened("latebuy");
    e.cfg.mode = Mode::On;
    {
        let p = &mut e.book.positions[0];
        p.paper = false;
        p.tokens = 0;
        p.state = State::Failed;
        p.dropped = true;
        p.closed_ms = now_ms();
        p.buy_sig = Some(b58(42));
    }
    let tx = ours(&e, 42, false, 1_005_000, 0, 7_777);
    e.on_tx(Src::Ours, &tx);
    let p = &e.book.positions[0];
    assert_eq!(p.state, State::Open);
    assert_eq!(p.tokens, 7_777);
    assert!(!p.dropped && p.live());
    // a buy that landed and failed stays failed (its signature cannot land twice)
    let mut e = opened("failedbuy");
    e.cfg.mode = Mode::On;
    {
        let p = &mut e.book.positions[0];
        p.paper = false;
        p.tokens = 0;
        p.state = State::Failed;
        p.dropped = false;
        p.buy_sig = Some(b58(43));
    }
    let tx = ours(&e, 43, false, 1_005_000, 0, 7_777);
    e.on_tx(Src::Ours, &tx);
    assert_eq!(e.book.positions[0].state, State::Failed);
}

/// 2026-10-27, CkFH2smc: the wallet sold after 14 minutes and the paper copy
/// held to 30 (-18.4%). The backtest's price path ends at its sale, so its
/// copies sell right behind it; the engine does the same.
#[test]
fn its_early_sell_takes_us_out_behind_it() {
    use rugsnipe_long::detect::{self, Seen};
    let mut e = opened("itssell");
    let sell = fx("w4_sell_wbtc_multihop");
    let w4: pump_codec::Pubkey = e.cfg.copy_wallet.parse().unwrap();
    let mint = match detect::read(&sell, &w4, &|_| None).as_slice() {
        [Seen::Sell { mint, .. }] => *mint,
        s => panic!("{s:?}"),
    };
    // our open position is on the coin it sells
    e.book.positions[0].mint = mint.to_string();
    e.on_tx(Src::Copied, &sell);
    assert_eq!(e.book.positions[0].reason, Some(Reason::ItsSell));
    e.on_tick(now_ms());
    assert_eq!(e.book.positions[0].state, State::Selling);
    land_sell(&mut e);
    let p = &e.book.positions[0];
    assert_eq!((p.state, p.reason), (State::Closed, Some(Reason::ItsSell)));
    let dir = std::path::PathBuf::from(&e.cfg.state_dir);
    assert!(std::fs::read_to_string(dir.join("closed.jsonl"))
        .unwrap()
        .contains("\"its_sell\""));
    // a sale of a coin we no longer hold changes nothing
    e.on_tx(Src::Copied, &sell);
    assert_eq!(e.book.positions[0].state, State::Closed);
}

/// A paper buy fills only where the real one would: past `max_premium` over
/// its price the real buy's min_out refuses it, so the paper buy is refused
/// too (2026-10-27: coins wallet 4 buys can double within 2 seconds).
#[test]
fn a_paper_buy_past_the_price_limit_is_refused() {
    let mut e = engine("refused");
    let tx = fx("w4_buy_wsol_multihop");
    e.on_tx(Src::Copied, &tx);
    assert_eq!(e.book.positions[0].state, State::Buying);
    // by the end of its landing slot the curve is at 1.5x its price
    price_to(&mut e, 1.5);
    e.on_slot(tx.slot + 2);
    e.on_tick(now_ms());
    let p = &e.book.positions[0];
    assert_eq!(p.state, State::Failed);
    assert!(
        p.net_lamports < 0 && p.net_lamports > -1_000_000,
        "the fee only: {}",
        p.net_lamports
    );
    // at 1.1x it fills
    let mut e = engine("notrefused");
    e.on_tx(Src::Copied, &tx);
    price_to(&mut e, 1.1);
    e.on_slot(tx.slot + 2);
    e.on_tick(now_ms());
    assert_eq!(e.book.positions[0].state, State::Open);
}

/// The limit is against the price its buy left, not its average price, and
/// it does not tighten with our stake (2026-10-29: at 0.5 SOL two real buys
/// were refused at 1.25x its average, about 1.17x the price it left).
#[test]
fn the_price_limit_is_against_the_price_its_buy_left() {
    let tx = fx("w4_buy_wsol_multihop");
    for (px, open) in [(1.2, true), (1.3, false)] {
        let mut e = engine(if open { "limit_in" } else { "limit_out" });
        e.on_tx(Src::Copied, &tx);
        price_to(&mut e, px);
        e.on_slot(tx.slot + 2);
        e.on_tick(now_ms());
        assert_eq!(e.book.positions[0].state == State::Open, open, "at {px}x");
    }
}

/// A paper buy lands after we see its buy, not after its own slot: seen 3
/// slots late (our feed's latest slot), it fills on the state at the end of
/// the slot after that (`paper_land_slots` = 1).
#[test]
fn a_paper_buy_fills_a_slot_after_we_saw_its_buy() {
    let mut e = engine("land");
    let tx = fx("w4_buy_wsol_multihop");
    e.on_slot(tx.slot + 3);
    e.on_tx(Src::Copied, &tx);
    assert_eq!(e.book.positions[0].land_slot, tx.slot + 4);
    e.on_slot(tx.slot + 4);
    e.on_tick(now_ms());
    assert_eq!(
        e.book.positions[0].state,
        State::Buying,
        "slot +4 is not over"
    );
    e.on_slot(tx.slot + 5);
    e.on_tick(now_ms());
    assert_eq!(e.book.positions[0].state, State::Open);
}

/// 2026-10-28: the curve completed while our buy was still out (the hot
/// bot's 2RR6sfbi: "it graduated as we bought"). The completing trade set
/// `graduated`, but the exit reason only on an open position; after the
/// fill the curve had no more trades, so no rule of ours could fire and the
/// coin sat until the time exit. Now the fill itself sends it to the pool.
#[test]
fn a_coin_that_completes_while_our_buy_is_out_sells_on_the_pool_at_the_fill() {
    let mut e = engine("gradbuy");
    let tx = fx("w4_buy_wsol_multihop");
    e.on_tx(Src::Copied, &tx);
    assert_eq!(e.book.positions[0].state, State::Buying);
    // what on_tx does on a completing trade of the coin, in any state
    e.book.positions[0].graduated = true;
    e.on_slot(tx.slot + 2);
    e.on_tick(now_ms());
    let p = &e.book.positions[0];
    assert_eq!(
        (p.state, p.reason),
        (State::Selling, Some(Reason::Complete))
    );
    // and an open position whose curve completes unseen by the fill path
    let mut e = opened("gradopen");
    e.book.positions[0].graduated = true;
    e.on_tick(now_ms());
    assert_eq!(e.book.positions[0].reason, Some(Reason::Complete));
}

/// It sold while our buy was still out (ChonQdJ8 sold 7 s after buying):
/// out behind it at the fill, not 30 minutes later.
#[test]
fn its_sell_while_our_buy_is_out_takes_us_out_at_the_fill() {
    use rugsnipe_long::detect::{self, Seen};
    let mut e = engine("itssellbuying");
    let tx = fx("w4_buy_wsol_multihop");
    e.on_tx(Src::Copied, &tx);
    let sell = fx("w4_sell_wbtc_multihop");
    let w4: pump_codec::Pubkey = e.cfg.copy_wallet.parse().unwrap();
    let mint = match detect::read(&sell, &w4, &|_| None).as_slice() {
        [Seen::Sell { mint, .. }] => *mint,
        s => panic!("{s:?}"),
    };
    e.book.positions[0].mint = mint.to_string();
    e.on_tx(Src::Copied, &sell);
    let p = &e.book.positions[0];
    assert_eq!(p.state, State::Buying);
    assert!(p.its_sold && p.reason.is_none());
    e.on_slot(tx.slot + 2);
    e.on_tick(now_ms());
    let p = &e.book.positions[0];
    assert_eq!((p.state, p.reason), (State::Selling, Some(Reason::ItsSell)));
}

/// One of our transactions is booked once, however many times it arrives
/// (the feed and a chain check can both deliver it): 2026-10-28, a chain
/// check re-read the first landed sell, an old failure, on every pass.
#[test]
fn our_transaction_is_booked_once_however_often_it_arrives() {
    let mut e = opened("once");
    e.cfg.mode = Mode::On;
    {
        let p = &mut e.book.positions[0];
        p.paper = false;
        p.tokens = 5_000;
        p.state = State::Selling;
        p.sell_sigs.push(b58(7));
    }
    let tx = ours(&e, 7, true, 300_005, 5_000, 5_000);
    e.on_tx(Src::Ours, &tx);
    e.on_tx(Src::Ours, &tx);
    e.on_tx(Src::Mint, &tx);
    let p = &e.book.positions[0];
    assert_eq!((p.state, p.sell_tries, p.costs), (State::Open, 1, 300_005));
    assert_eq!(p.net_lamports, -300_005);
    assert_eq!(p.applied, vec![b58(7)]);
    // the same for a fill
    let mut e = opened("oncefill");
    e.cfg.mode = Mode::On;
    {
        let p = &mut e.book.positions[0];
        p.paper = false;
        p.tokens = 0;
        p.state = State::Buying;
        p.buy_sig = Some(b58(8));
    }
    let tx = ours(&e, 8, false, 1_005_000, 0, 9_999);
    e.on_tx(Src::Mint, &tx);
    e.on_tx(Src::Ours, &tx);
    let p = &e.book.positions[0];
    assert_eq!(
        (p.state, p.tokens, p.net_lamports),
        (State::Open, 9_999, -1_005_000)
    );
}

/// A buy out when the process stopped is checked at once after the
/// restart, but given up only by its real age (2026-10-28: its send time
/// was zeroed at the restart, so it read as 90 s old and was dropped on the
/// first tick; had it then landed, nothing would have managed the coins).
#[test]
fn a_restart_checks_an_unseen_buy_at_once_but_keeps_it_until_its_real_age() {
    let mut e = opened("restartbuy");
    e.cfg.mode = Mode::On;
    let sent = now_ms();
    {
        let p = &mut e.book.positions[0];
        p.paper = false;
        p.tokens = 0;
        p.state = State::Buying;
        p.buy_sig = Some(b58(44));
        p.buy_sent_ms = sent;
    }
    let dir = e.cfg.state_dir.clone();
    e.book
        .save(&std::path::PathBuf::from(&dir).join("positions.json"))
        .unwrap();
    drop(e);
    let cfg = LongCfg {
        mode: Mode::Log,
        state_dir: dir,
        ..Default::default()
    };
    let mut e2 = Engine::new(
        cfg,
        Default::default(),
        None,
        Rpc::new("http://127.0.0.1:9"),
        Oracle::default(),
        None,
        None,
    )
    .unwrap();
    e2.recover();
    let p = &e2.book.positions[0];
    assert!(p.recovered && p.next_chase_ms == 0);
    assert_eq!(p.buy_sent_ms, sent, "the real send time is kept");
    // the chain is unreachable here: the check fails, and the buy is not
    // dropped (not 90 s old)
    e2.on_tick(now_ms());
    let p = &e2.book.positions[0];
    assert_eq!(p.state, State::Buying);
    assert!(!p.dropped);
    assert!(p.next_chase_ms > now_ms() + 2_000, "the next check waits");
}

/// `follow_its_sell = false`: its early sale leaves our exits alone, and the
/// record keeps what selling behind it would have made (2026-10-28: it
/// sells early on half of its big buys now; on Oct 27-28 holding to our own
/// exits scored +3.10 against -0.51 behind it, on Oct 19-27 about even).
#[test]
fn an_early_sale_under_the_price_is_followed_when_its_sales_are_not() {
    use rugsnipe_long::detect::{self, Seen};
    let sell = fx("w4_sell_wbtc_multihop");
    let setup = |tag: &str, window: Vec<u64>| {
        let mut e = opened(tag);
        e.cfg.follow_its_sell = false;
        e.cfg.follow_early_s = window;
        e.cfg.follow_early_below = 1.5;
        let w4: pump_codec::Pubkey = e.cfg.copy_wallet.parse().unwrap();
        let mint = match detect::read(&sell, &w4, &|_| None).as_slice() {
            [Seen::Sell { mint, .. }] => *mint,
            s => panic!("{s:?}"),
        };
        e.book.positions[0].mint = mint.to_string();
        e
    };
    // its sale within the window (seconds after its buy) and under 1.5x: out behind it
    let mut e = setup("early1", vec![0, 600]);
    price_to(&mut e, 1.3);
    e.on_tx(Src::Copied, &sell);
    assert_eq!(e.book.positions[0].reason, Some(Reason::ItsSell), "followed");
    // over the price: our own exits stay
    let mut e = setup("early2", vec![0, 600]);
    price_to(&mut e, 1.6);
    e.on_tx(Src::Copied, &sell);
    let p = &e.book.positions[0];
    assert_eq!((p.state, p.reason), (State::Open, None), "a coin that took off is held");
    assert!(p.its_sell_px > 1.5, "and the sale is on the record");
    // outside the window: our own exits stay
    let mut e = setup("early3", vec![600, 1200]);
    price_to(&mut e, 1.3);
    e.on_tx(Src::Copied, &sell);
    assert_eq!(e.book.positions[0].reason, None, "a sale outside the window is not followed");
}

#[test]
fn its_early_sell_is_not_followed_when_configured_and_is_recorded() {
    use rugsnipe_long::detect::{self, Seen};
    let mut e = opened("notfollow");
    e.cfg.follow_its_sell = false;
    let sell = fx("w4_sell_wbtc_multihop");
    let w4: pump_codec::Pubkey = e.cfg.copy_wallet.parse().unwrap();
    let mint = match detect::read(&sell, &w4, &|_| None).as_slice() {
        [Seen::Sell { mint, .. }] => *mint,
        s => panic!("{s:?}"),
    };
    e.book.positions[0].mint = mint.to_string();
    price_to(&mut e, 1.3);
    e.on_tx(Src::Copied, &sell);
    let p = &e.book.positions[0];
    assert_eq!((p.state, p.reason), (State::Open, None), "our exits stay");
    assert!((p.its_sell_px - 1.3).abs() < 0.01, "{}", p.its_sell_px);
    assert!(
        p.its_sell_net > 150_000_000 && p.its_sell_net < 300_000_000,
        "about +0.2 SOL behind it: {}",
        p.its_sell_net
    );
    e.on_tick(now_ms());
    assert_eq!(e.book.positions[0].state, State::Open);
    // the same sale again (delivered twice, or a second sale): still ours to
    // hold, and the record keeps the first
    price_to(&mut e, 1.1);
    e.on_tx(Src::Copied, &sell);
    e.on_tick(now_ms());
    let p = &e.book.positions[0];
    assert_eq!((p.state, p.reason, p.its_sold), (State::Open, None, false), "never followed");
    assert!((p.its_sell_px - 1.3).abs() < 0.01, "the first sale's price: {}", p.its_sell_px);
    // then our own take profit
    price_to(&mut e, 2.1);
    e.on_tick(now_ms());
    assert_eq!(e.book.positions[0].reason, Some(Reason::Tp));
    land_sell(&mut e);
    let p = &e.book.positions[0];
    assert_eq!(p.state, State::Closed);
    assert!(p.its_sell_net > 0 && p.net_lamports > p.its_sell_net);
}

/// `min_fee_bps`: a coin whose fee tier is under it is not copied (2026-11-15:
/// the copies of low-fee coins lost in every block of the backtest); off (0)
/// by default, and a fee that is not in the event is never skipped.
#[test]
fn a_coin_under_the_fee_floor_is_skipped() {
    let tx = fx("w4_buy_wsol_multihop");
    let fee = rugsnipe_long::detect::read(&tx, &LongCfg::default().copy_pk(), &|_| None)
        .into_iter()
        .find_map(|s| match s {
            rugsnipe_long::detect::Seen::Buy(t) => Some(t.fee_bps),
            _ => None,
        })
        .expect("the fixture is its buy");
    assert!(fee > 0, "the fixture carries its fee");
    let mut e = engine("feefloor");
    e.cfg.min_fee_bps = fee + 1;
    e.on_tx(Src::Copied, &tx);
    assert!(e.book.positions.is_empty(), "under the floor: skipped");
    let mut e = engine("feefloor-at");
    e.cfg.min_fee_bps = fee;
    e.on_tx(Src::Copied, &tx);
    assert_eq!(e.book.positions.len(), 1, "at the floor: copied");
}

/// No new high for `stall_s` once the price has been back at our fill:
/// out on the stall signal (2026-11-15, #36 GGSWz3uu peaked at 2.56x and
/// drifted down for minutes; analysis/research/2026-11-16/signals/).
#[test]
fn a_coin_that_stops_making_highs_is_sold_on_the_stall() {
    let mut e = opened("stall");
    e.cfg.stall_s = 180;
    let p = &e.book.positions[0];
    assert!(p.entry_px > 0.0, "the fill price is kept");
    let (seen, fill_ms) = (p.seen_ms, p.hi_ms);
    // a high above our fill, then nothing higher
    e.book.positions[0].hi = e.book.positions[0].entry_px * 1.8;
    e.book.positions[0].hi_ms = fill_ms;
    e.on_tick(fill_ms + 179_000);
    assert_eq!(e.book.positions[0].state, State::Open);
    e.on_tick(fill_ms + 180_000);
    assert!(fill_ms + 180_000 < seen + e.cfg.max_hold_s * 1000, "before the timer");
    let p = &e.book.positions[0];
    assert_eq!((p.state, p.reason), (State::Selling, Some(Reason::Stall)));
}

/// The other traders' sells outnumber their buys by `n` over `w` seconds:
/// out on the pressure signal; its own trades are not counted.
#[test]
fn other_traders_selling_more_than_buying_takes_us_out() {
    let mut e = opened("pressure");
    e.cfg.sell_pressure = vec![5, 60, 30];
    // its own trade on the coin again: not part of the flow
    e.on_tx(Src::Copied, &fx("w4_buy_wsol_multihop"));
    assert!(e.book.positions[0].flow.is_empty());
    let seen = e.book.positions[0].seen_ms;
    for k in 0..4 {
        e.book.positions[0].flow.push_back((seen + 40_000 + k * 1_000, true));
    }
    e.on_tick(seen + 45_000);
    assert_eq!(e.book.positions[0].state, State::Open, "4 net is under 5");
    e.book.positions[0].flow.push_back((seen + 46_000, true));
    e.on_tick(seen + 46_000);
    let p = &e.book.positions[0];
    assert_eq!((p.state, p.reason), (State::Selling, Some(Reason::Pressure)));
    land_sell(&mut e);
    assert_eq!(e.book.positions[0].state, State::Closed);
    let dir = std::path::PathBuf::from(&e.cfg.state_dir);
    assert!(std::fs::read_to_string(dir.join("closed.jsonl"))
        .unwrap()
        .contains("\"sell_pressure\""));
}

/// Two units on one wallet (Nov 18: the TAB16RxX unit on wallet 4's wallet): a coin the
/// other unit holds is not bought; once its position there is closed and over an hour
/// old, it is.
#[test]
fn a_coin_the_other_unit_on_this_wallet_holds_is_not_bought() {
    let mut a = opened("other-a");
    let a_dir = a.cfg.state_dir.clone();
    let a_book = std::path::Path::new(&a_dir).join("positions.json");
    a.book.save(&a_book).unwrap();
    let with_other = |tag: &str| {
        let dir = std::env::temp_dir().join(format!("long-engine-{tag}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        let cfg = LongCfg {
            mode: Mode::Log,
            state_dir: dir.to_string_lossy().into(),
            other_state_dirs: vec![a_dir.clone()],
            ..Default::default()
        };
        Engine::new(cfg, Default::default(), None, Rpc::new("http://127.0.0.1:9"), Oracle::default(), None, None).unwrap()
    };
    let mut b = with_other("other-b");
    b.on_tx(Src::Copied, &fx("w4_buy_wsol_multihop"));
    assert!(b.book.positions.is_empty(), "held by the other unit: skipped");
    // the other unit's position closed and seen two hours ago: the coin is free again
    a.book.positions[0].state = State::Closed;
    a.book.positions[0].seen_ms = now_ms().saturating_sub(2 * 3_600_000);
    a.book.save(&a_book).unwrap();
    let mut c = with_other("other-c");
    c.on_tx(Src::Copied, &fx("w4_buy_wsol_multihop"));
    assert_eq!(c.book.positions.len(), 1, "no longer held: bought");
}

/// `float_only` (Nov 18): wrapped SOL is no anchor, so its buy routed from wSOL is not
/// copied (the same buy is copied without the switch: `opened`).
#[test]
fn float_only_does_not_pay_from_sol() {
    let dir = std::env::temp_dir().join(format!("long-engine-floatonly-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    let cfg = LongCfg { mode: Mode::Log, state_dir: dir.to_string_lossy().into(), float_only: true, ..Default::default() };
    let mut e = Engine::new(cfg, Default::default(), None, Rpc::new("http://127.0.0.1:9"), Oracle::default(), None, None).unwrap();
    e.on_tx(Src::Copied, &fx("w4_buy_wsol_multihop"));
    assert!(e.book.positions.is_empty(), "a wSOL-routed buy is skipped under float_only");
}

/// The dip unit (Nov 19, `dip_drop`): its buy is watched, not copied; a trade in a later slot at or under (1 - drop)
/// of the price its buy left buys, with that state as the reference; a trade in its own slot, or not deep enough, does
/// not; a watch past `dip_within_s` ends with no trade.
fn dip_engine(tag: &str) -> Engine {
    let mut e = engine(tag);
    e.cfg.dip_drop = 0.10;
    e.cfg.dip_within_s = 60;
    e
}

#[test]
fn the_dip_unit_watches_its_buy_and_buys_only_on_the_dip() {
    let mut e = dip_engine("dip");
    let tx = fx("w4_buy_wsol_multihop");
    e.on_tx(Src::Copied, &tx);
    assert!(e.book.positions.is_empty(), "no copy at once");
    assert_eq!(e.dips.len(), 1, "a dip watch");
    let (d, _) = e.dips[0].clone();
    let (vt, vq) = (d.vt_post as f64, d.vq_post as f64);
    // the price at x (constant product): vt / sqrt(x), vq * sqrt(x)
    let at = |x: f64| ((vt / x.sqrt()) as u64, (vq * x.sqrt()) as u64);
    // its own slot, even far down: no
    let (t1, q1) = at(0.5);
    e.on_dip_trades(d.slot, &[(d.mint, t1, q1)]);
    assert!(e.book.positions.is_empty() && e.dips.len() == 1);
    // a later slot at 0.95x: not deep enough
    let (t2, q2) = at(0.95);
    e.on_dip_trades(d.slot + 1, &[(d.mint, t2, q2)]);
    assert!(e.book.positions.is_empty() && e.dips.len() == 1);
    // a later slot at 0.88x: the dip, bought; the reference is this state
    let (t3, q3) = at(0.88);
    e.on_dip_trades(d.slot + 2, &[(d.mint, t3, q3)]);
    assert!(e.dips.is_empty(), "the watch is used");
    assert_eq!(e.book.positions.len(), 1, "bought on the dip");
    let p = &e.book.positions[0];
    assert_eq!((p.vt_ref, p.vq_ref, p.its_slot), (t3, q3, d.slot + 2));
    // a second dip trade of the coin buys nothing more
    e.on_dip_trades(d.slot + 3, &[(d.mint, t3, q3)]);
    assert_eq!(e.book.positions.len(), 1);
}

#[test]
fn a_dip_watch_ends_after_its_time_without_a_trade() {
    let mut e = dip_engine("dip-expire");
    e.on_tx(Src::Copied, &fx("w4_buy_wsol_multihop"));
    assert_eq!(e.dips.len(), 1);
    e.on_tick(now_ms() + 61_000);
    assert!(e.dips.is_empty() && e.book.positions.is_empty(), "no dip in 60 s: no trade");
}

#[test]
fn without_dip_drop_the_copy_buys_at_once_as_before() {
    let mut e = engine("dip-off");
    e.on_tx(Src::Copied, &fx("w4_buy_wsol_multihop"));
    assert!(e.dips.is_empty());
    assert_eq!(e.book.positions.len(), 1);
}

/// The split (Nov 19, the owner: "from the same bot ... we split 0.5, 0.5"): `dip_stake_sol > 0` keeps the copy (bought at
/// once, `stake_sol`) and adds the dip leg (`dip_stake_sol`) on the same coin, one of each.
fn split_engine(tag: &str) -> (Engine, pump_codec::Pubkey, u64, u64, u64) {
    let mut e = dip_engine(tag);
    e.cfg.stake_sol = 0.5;
    e.cfg.dip_stake_sol = 0.3;
    e.cfg.take_profit = 4.0;
    let tx = fx("w4_buy_wsol_multihop");
    e.on_tx(Src::Copied, &tx);
    assert_eq!(e.book.positions.len(), 1, "the copy buys at once");
    assert_eq!(e.dips.len(), 1, "and the dip is watched");
    let (d, _) = e.dips[0].clone();
    let (vt, vq) = (d.vt_post as f64, d.vq_post as f64);
    let x = 0.88f64;
    let (t3, q3) = ((vt / x.sqrt()) as u64, (vq * x.sqrt()) as u64);
    e.on_dip_trades(d.slot + 2, &[(d.mint, t3, q3)]);
    (e, d.mint, d.slot, t3, q3)
}

#[test]
fn the_split_buys_the_copy_at_once_and_the_dip_leg_on_the_dip() {
    let (mut e, mint, slot, _, _) = split_engine("split");
    assert_eq!(e.book.positions.len(), 2, "two legs on the coin");
    let (c, d) = (&e.book.positions[0], &e.book.positions[1]);
    assert!(!c.is_dip() && d.is_dip());
    assert_eq!((c.mint_pk(), d.mint_pk()), (mint, mint));
    assert_eq!(d.stake_lamports, 300_000_000, "the dip leg's stake");
    assert_ne!(c.stake_lamports, d.stake_lamports, "the copy's own stake");
    // a second dip trade buys nothing more; both legs fill
    e.on_dip_trades(slot + 3, &[]);
    assert_eq!(e.book.positions.len(), 2);
    e.on_slot(slot + 5);
    e.on_tick(now_ms());
    assert!(e.book.positions.iter().all(|p| p.state == State::Open));
}

#[test]
fn the_dip_leg_takes_its_own_profit_and_the_copy_leg_holds() {
    let (mut e, _, slot, _, _) = split_engine("split-tp");
    e.on_slot(slot + 5);
    e.on_tick(now_ms());
    // 1.7x the dip leg's fill: over its 1.5x, far under the copy's 4x
    let p = &mut e.book.positions[1];
    let k = p.vt_ref as f64 * p.vq_ref as f64;
    p.vt = (p.vt_ref as f64 / 1.7f64.sqrt()) as u64;
    p.vq = (k / p.vt as f64) as u64;
    e.on_tick(now_ms());
    assert_eq!((e.book.positions[1].state, e.book.positions[1].reason), (State::Selling, Some(Reason::Tp)));
    assert_eq!(e.book.positions[0].state, State::Open, "the copy keeps its own exits");
}

#[test]
fn the_dip_leg_ends_on_its_own_hold_and_ignores_the_signals() {
    let (mut e, _, slot, _, _) = split_engine("split-hold");
    e.cfg.max_hold_s = 600;
    e.cfg.dip_max_hold_s = 900;
    e.cfg.stall_s = 180;
    e.on_slot(slot + 5);
    e.on_tick(now_ms());
    let seen = e.book.positions[1].seen_ms;
    for p in e.book.positions.iter_mut() {
        p.hi = p.entry_px * 1.3;
    }
    // past the stall and the copy's 600 s: the copy is out, the dip leg holds
    e.on_tick(seen + 601_000);
    assert_eq!(e.book.positions[0].state, State::Selling);
    assert_eq!(e.book.positions[1].state, State::Open, "no stall, no 600 s for the dip leg");
    e.on_tick(seen + 900_000);
    assert_eq!((e.book.positions[1].state, e.book.positions[1].reason), (State::Selling, Some(Reason::Time)));
}

#[test]
fn its_early_sale_takes_out_the_copy_leg_only() {
    use rugsnipe_long::detect::{self, Seen};
    let (mut e, _, slot, _, _) = split_engine("split-itssell");
    e.on_slot(slot + 5);
    e.on_tick(now_ms());
    let sell = fx("w4_sell_wbtc_multihop");
    let w4: pump_codec::Pubkey = e.cfg.copy_wallet.parse().unwrap();
    let mint = match detect::read(&sell, &w4, &|_| None).as_slice() {
        [Seen::Sell { mint, .. }] => *mint,
        s => panic!("{s:?}"),
    };
    for p in e.book.positions.iter_mut() {
        p.mint = mint.to_string();
    }
    e.on_tx(Src::Copied, &sell);
    assert_eq!(e.book.positions[0].reason, Some(Reason::ItsSell));
    assert_eq!(e.book.positions[1].reason, None, "the dip leg does not follow its sale");
}

#[test]
fn each_leg_has_its_own_max_open() {
    let mut e = dip_engine("split-max");
    e.cfg.dip_stake_sol = 0.3;
    e.cfg.max_open = 1;
    let tx = fx("w4_buy_wsol_multihop");
    e.on_tx(Src::Copied, &tx);
    let (d, _) = e.dips[0].clone();
    let x = 0.88f64;
    let (t3, q3) = ((d.vt_post as f64 / x.sqrt()) as u64, (d.vq_post as f64 * x.sqrt()) as u64);
    e.on_dip_trades(d.slot + 2, &[(d.mint, t3, q3)]);
    assert_eq!(e.book.positions.len(), 2, "the copy's one open slot does not block the dip leg");
}
