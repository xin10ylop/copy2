//! `rugsnipe-long`: see the crate docs (docs/20).
//!
//! ```text
//! rugsnipe-long run [--config /etc/rugsnipe/long.toml]
//!     The service: mode log (paper) or on (real), from long.toml.
//! rugsnipe-long status [--config ...] [--tz +0200] [--last 15] [--chain]
//!     Positions now, today's result (paper and real), the last closed;
//!     `--chain`: the wallet's SOL and floats.
//! rugsnipe-long float buy MINT SOL | float sell MINT all|AMOUNT [--config ...]
//!     Buy or sell a float through Jupiter from the long wallet. Selling a
//!     coin that is not a float (an airdrop) books its SOL for `status`.
//! rugsnipe-long float book SIG [--config ...]
//!     Book a sale already made (its SOL change) for `status`.
//! rugsnipe-long copy [--config /etc/rugsnipe/copier.toml]
//!     The copier (docs/21): several wallets' buys on any venue through
//!     Jupiter (wallet 4's part B, other wallets); mode log (paper) or on.
//! rugsnipe-long copy-status [--config ...] [--tz +0200] [--last 15]
//!     The copier's result by wallet (today, all), open positions, the last closed.
//! rugsnipe-long copy-replay --config ... --rpc URL [--tick-s 30] SIG...
//!     Paper only: the given transactions of the copied wallets through the
//!     copier, at live Jupiter quotes, then its exits ticked for a while (a
//!     check of the whole path without the gRPC feed).
//! rugsnipe-long keygen --out /etc/rugsnipe/keys/long-wallet.json
//!     A new wallet for the long copy (JSON keypair, 0400; prints the address).
//! rugsnipe-long simulate --rpc URL --tx SIG [--user PUBKEY] [--sol 0.02] [--float MINT]...
//!     Its buy SIG copied with our route from the user's wallet, simulated on
//!     the chain now: the buy alone, then buy + sell back in one transaction.
//! ```

use pump_codec::constants as c;
use pump_codec::{pda, Pubkey};
use rugsnipe_long::chain::{token_amount, Rpc};
use rugsnipe_long::config::{LongCfg, Mode};
use rugsnipe_long::detect::{self, Seen};
use rugsnipe_long::engine::Engine;
use rugsnipe_long::oracle::{now_ms, Oracle};
use rugsnipe_long::pos::{Book, State};
use rugsnipe_long::send::Out;
use rugsnipe_long::txb::{self, Fees};
use rugsnipe_long::{feed, keys, route, txlite::TxLite};
use std::time::Duration;

fn arg(args: &[String], k: &str) -> Option<String> {
    args.iter()
        .position(|a| a == k)
        .and_then(|i| args.get(i + 1))
        .cloned()
}

fn args_all(args: &[String], k: &str) -> Vec<String> {
    args.windows(2)
        .filter(|w| w[0] == k)
        .map(|w| w[1].clone())
        .collect()
}

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let r = match args.first().map(String::as_str) {
        Some("simulate") => simulate(&args[1..]),
        Some("simulate-sell") => simulate_sell(&args[1..]),
        Some("run") => run(&args[1..]),
        Some("status") => status(&args[1..]),
        Some("float") => float(&args[1..]),
        Some("keygen") => keygen(&args[1..]),
        Some("copy") => copy_run(&args[1..]),
        Some("copy-status") => copy_status(&args[1..]),
        Some("copy-replay") => copy_replay(&args[1..]),
        _ => Err("usage: rugsnipe-long run|status|copy|copy-status|float buy MINT SOL|float sell MINT all|AMOUNT|simulate ... (see --help in the source docs)".into()),
    };
    if let Err(e) = r {
        eprintln!("rugsnipe-long: {e}");
        std::process::exit(2);
    }
}

fn simulate(args: &[String]) -> Result<(), String> {
    let url = arg(args, "--rpc").ok_or("--rpc URL")?;
    let sig = arg(args, "--tx").ok_or("--tx SIG")?;
    let w4: Pubkey = arg(args, "--copy")
        .unwrap_or("H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg".into())
        .parse()
        .map_err(|_| "--copy")?;
    let user: Pubkey = arg(args, "--user")
        .unwrap_or("4g49xGbgHZk3QYR1o6QSfDUbHmJZFwN6iDp6Vco1skff".into())
        .parse()
        .map_err(|_| "--user")?;
    let sol: f64 = arg(args, "--sol")
        .unwrap_or("0.02".into())
        .parse()
        .map_err(|_| "--sol")?;
    let mut anchors = vec![c::WSOL_MINT];
    for f in args_all(args, "--float") {
        anchors.push(f.parse().map_err(|_| "--float MINT")?);
    }
    // the buyback fee recipient index the engine would rotate to (0-7), and
    // whether the sell closes the coin account (the engine's first sells do)
    let buyback: usize = arg(args, "--buyback")
        .unwrap_or("0".into())
        .parse()
        .map_err(|_| "--buyback N")?;
    let close_coin = args.iter().any(|a| a == "--close");
    let mut rpc = Rpc::new(&url);
    let tx = TxLite::from_rpc_json(&rpc.transaction(&sig)?)?;
    let seen = detect::read(&tx, &w4, &|_| None);
    let t = seen
        .into_iter()
        .find_map(|s| match s {
            Seen::Buy(t) => Some(*t),
            _ => None,
        })
        .ok_or(
            "no buy of a coin priced in another token by the copied wallet in that transaction",
        )?;
    println!(
        "its buy: {} quote {} input {} amount {} valued {:?} SOL, route {}",
        t.mint,
        t.quote_mint,
        t.input_mint,
        t.input_amount,
        t.sol_value.map(|v| v as f64 / 1e9),
        t.route
            .as_ref()
            .map_or("direct curve".into(), |r| format!("{} hops", r.hops.len()))
    );
    let plan = route::plan(&t, &anchors, &mut rpc).map_err(|e| e.to_string())?;
    println!(
        "our route ({}): {:?}",
        plan.how,
        plan.route
            .mints()
            .iter()
            .map(|m| m.to_string()[..8].to_string())
            .collect::<Vec<_>>()
    );
    let amount_in = if plan.anchor == c::WSOL_MINT {
        (sol * 1e9) as u64
    } else {
        match (t.sol_value, plan.anchor == t.input_mint) {
            (Some(v), true) => (t.input_amount as f64 * sol * 1e9 / v as f64) as u64,
            // no oracle here: its buy is read as its 1.5 SOL tier
            (None, true) => (t.input_amount as f64 * sol / 1.5) as u64,
            _ => return Err("a float anchor needs its own buy from the same float".into()),
        }
    };
    let fees = Fees {
        cu_limit: 400_000,
        cu_price: 1,
        tip: None,
    };
    let coin_ata = pda::associated_token_address(&user, &t.mint, &t.coin_program);
    let buy = txb::buy_ixs(
        &user,
        &plan.route,
        &plan.anchor_program,
        &t.coin_program,
        amount_in,
        1,
        &fees,
        buyback,
    );
    let (bytes, _) = txb::sign(&user, &buy, &[0; 32], |_| [0; 64]).map_err(|e| e.to_string())?;
    println!(
        "buy transaction: {} bytes (buyback index {buyback}, sell closes the coin account: {close_coin})",
        bytes.len()
    );
    let v = rpc.simulate(&bytes, &[coin_ata])?;
    let tokens = v["accounts"][0]["data"][0]
        .as_str()
        .map(|s| {
            token_amount(
                &base64::Engine::decode(&base64::engine::general_purpose::STANDARD, s)
                    .unwrap_or_default(),
            )
        })
        .unwrap_or(0);
    println!(
        "buy: err {} units {} tokens {}",
        v["err"], v["unitsConsumed"], tokens
    );
    if !v["err"].is_null() || tokens == 0 {
        for l in v["logs"]
            .as_array()
            .into_iter()
            .flatten()
            .rev()
            .take(12)
            .collect::<Vec<_>>()
            .into_iter()
            .rev()
        {
            println!("   {}", l.as_str().unwrap_or(""));
        }
        return Err("the buy does not simulate".into());
    }
    // buy then sell back in one transaction (one budget): all of it when
    // the coin account is closed after (as the engine's first sells do),
    // else 98%
    let sell = txb::sell_ixs(
        &user,
        &plan.route.reversed(),
        &plan.anchor_program,
        &t.coin_program,
        if close_coin {
            tokens
        } else {
            tokens * 98 / 100
        },
        1,
        close_coin,
        &fees,
        buyback,
    );
    let mut both = buy.clone();
    both.extend(sell.into_iter().skip(2));
    let watch = if plan.anchor == c::WSOL_MINT {
        user
    } else {
        pda::associated_token_address(&user, &plan.anchor, &plan.anchor_program)
    };
    match txb::sign(&user, &both, &[0; 32], |_| [0; 64]) {
        Err(e) => println!("round trip: does not fit one transaction ({e}); the buy simulated"),
        Ok((bytes, _)) => {
            let before = if plan.anchor == c::WSOL_MINT {
                rpc.balance(&user)?
            } else {
                rpc.token_balance(&user, &plan.anchor, &plan.anchor_program)?
            };
            let v = rpc.simulate(&bytes, &[watch])?;
            let after = if plan.anchor == c::WSOL_MINT {
                v["accounts"][0]["lamports"].as_u64().unwrap_or(0)
            } else {
                v["accounts"][0]["data"][0]
                    .as_str()
                    .map(|s| {
                        token_amount(
                            &base64::Engine::decode(&base64::engine::general_purpose::STANDARD, s)
                                .unwrap_or_default(),
                        )
                    })
                    .unwrap_or(0)
            };
            println!(
                "round trip ({} bytes): err {} units {} anchor {} -> {} ({:+.2}% of the stake)",
                bytes.len(),
                v["err"],
                v["unitsConsumed"],
                before,
                after,
                (after as f64 - before as f64) / amount_in as f64 * 100.0
            );
            if !v["err"].is_null() {
                for l in v["logs"]
                    .as_array()
                    .into_iter()
                    .flatten()
                    .rev()
                    .take(12)
                    .collect::<Vec<_>>()
                    .into_iter()
                    .rev()
                {
                    println!("   {}", l.as_str().unwrap_or(""));
                }
            }
        }
    }
    Ok(())
}

/// `simulate-sell --rpc URL --mint MINT --quote QUOTE --user HOLDER [--float WBTC]
/// [--graduated] [--buyback N] [--close]`: the sell the engine would send for
/// a coin priced in QUOTE, from HOLDER's whole balance, along
/// coin -> quote (the curve, or the coin's PumpSwap pool with `--graduated`)
/// -> the anchor's pool, simulated on mainnet (nothing sent, HOLDER's
/// signature not checked). 2026-10-28: the engine's pool sell after a
/// graduation had never run; the hot bot lost 0.57 SOL on exactly that.
fn simulate_sell(args: &[String]) -> Result<(), String> {
    let url = arg(args, "--rpc").ok_or("--rpc URL")?;
    let mint: Pubkey = arg(args, "--mint")
        .ok_or("--mint")?
        .parse()
        .map_err(|_| "--mint")?;
    let quote: Pubkey = arg(args, "--quote")
        .ok_or("--quote")?
        .parse()
        .map_err(|_| "--quote")?;
    let user: Pubkey = arg(args, "--user")
        .ok_or("--user HOLDER")?
        .parse()
        .map_err(|_| "--user")?;
    let graduated = args.iter().any(|a| a == "--graduated");
    let close_coin = args.iter().any(|a| a == "--close");
    let buyback: usize = arg(args, "--buyback")
        .unwrap_or("0".into())
        .parse()
        .map_err(|_| "--buyback N")?;
    let mut anchors = vec![c::WSOL_MINT];
    for f in args_all(args, "--float") {
        anchors.push(f.parse().map_err(|_| "--float MINT")?);
    }
    let mut rpc = Rpc::new(&url);
    let coin_program = route::Chain::mint_program(&mut rpc, &mint).ok_or("coin program")?;
    let quote_program = route::Chain::mint_program(&mut rpc, &quote).ok_or("quote program")?;
    let tokens = rpc.token_balance(&user, &mint, &coin_program)?;
    if tokens == 0 {
        return Err(format!("{user} holds none of {mint}"));
    }
    // the route the engine stores for a direct curve buy behind the quote's
    // pool (or the curve alone when the quote is an anchor), reversed; the
    // coin's hop as a pool after graduation (engine.rs send_sell)
    let curve = pump_codec::multihop::Hop::curve(&mint, &coin_program, &quote, &quote_program);
    let (anchor, mut hops) = if anchors.contains(&quote) {
        (quote, vec![curve])
    } else {
        let mut found = None;
        for a in &anchors {
            let pool = pda::canonical_pump_swap_pool(&quote, a);
            if route::Chain::pool_exists(&mut rpc, &pool) {
                let ap = route::Chain::mint_program(&mut rpc, a).ok_or("anchor program")?;
                found = Some((
                    *a,
                    pump_codec::multihop::Hop::pool(&pool, &quote, &quote_program, a, &ap),
                ));
                break;
            }
        }
        let (a, hop) = found.ok_or("no anchor's pool against the quote")?;
        (a, vec![hop, curve])
    };
    let anchor_program = route::Chain::mint_program(&mut rpc, &anchor).ok_or("anchor program")?;
    let buy_route =
        pump_codec::multihop::Route::new(anchor, hops.clone()).map_err(|e| format!("{e:?}"))?;
    let mut r = buy_route.reversed();
    if graduated {
        let pool = pda::canonical_pump_swap_pool(&mint, &quote);
        if !route::Chain::pool_exists(&mut rpc, &pool) {
            return Err(format!("no canonical pool for {mint} against {quote}"));
        }
        hops = r
            .hops
            .iter()
            .map(|h| {
                if h.venue == pump_codec::multihop::Venue::Curve && h.base_mint == mint {
                    pump_codec::multihop::Hop::pool(
                        &pool,
                        &mint,
                        &coin_program,
                        &h.quote_mint,
                        &quote_program,
                    )
                } else {
                    *h
                }
            })
            .collect();
        r = pump_codec::multihop::Route::new(r.input, hops).map_err(|e| format!("{e:?}"))?;
    }
    println!(
        "sell route ({} hops{}): {:?}; {} tokens, buyback index {buyback}, close coin account {close_coin}",
        r.hops.len(),
        if graduated { ", graduated" } else { "" },
        r.mints().iter().map(|m| m.to_string()[..8].to_string()).collect::<Vec<_>>(),
        tokens
    );
    let fees = Fees {
        cu_limit: 400_000,
        cu_price: 1,
        tip: None,
    };
    let sell = txb::sell_ixs(
        &user,
        &r,
        &anchor_program,
        &coin_program,
        tokens,
        1,
        close_coin,
        &fees,
        buyback,
    );
    let (bytes, _) = txb::sign(&user, &sell, &[0; 32], |_| [0; 64]).map_err(|e| e.to_string())?;
    let watch = if anchor == c::WSOL_MINT {
        user
    } else {
        pda::associated_token_address(&user, &anchor, &anchor_program)
    };
    let before = if anchor == c::WSOL_MINT {
        rpc.balance(&user)?
    } else {
        rpc.token_balance(&user, &anchor, &anchor_program)?
    };
    let v = rpc.simulate(&bytes, &[watch])?;
    let after = if anchor == c::WSOL_MINT {
        v["accounts"][0]["lamports"].as_u64().unwrap_or(0)
    } else {
        v["accounts"][0]["data"][0]
            .as_str()
            .map(|s| {
                token_amount(
                    &base64::Engine::decode(&base64::engine::general_purpose::STANDARD, s)
                        .unwrap_or_default(),
                )
            })
            .unwrap_or(0)
    };
    println!(
        "sell ({} bytes): err {} units {} anchor {} -> {} ({:+})",
        bytes.len(),
        v["err"],
        v["unitsConsumed"],
        before,
        after,
        after as i128 - before as i128
    );
    if !v["err"].is_null() {
        for l in v["logs"]
            .as_array()
            .into_iter()
            .flatten()
            .rev()
            .take(14)
            .collect::<Vec<_>>()
            .into_iter()
            .rev()
        {
            println!("   {}", l.as_str().unwrap_or(""));
        }
        return Err("the sell does not simulate".into());
    }
    Ok(())
}

fn load_cfg(args: &[String]) -> Result<LongCfg, String> {
    let p = arg(args, "--config").unwrap_or("/etc/rugsnipe/long.toml".into());
    let text = std::fs::read_to_string(&p).map_err(|e| format!("{p}: {e}"))?;
    LongCfg::from_toml_str(&text)
}

fn load_hot(cfg: &LongCfg) -> Result<rugsnipe_core::config::Config, String> {
    let text =
        std::fs::read_to_string(&cfg.hot_config).map_err(|e| format!("{}: {e}", cfg.hot_config))?;
    rugsnipe_core::config::Config::from_toml_str(&text)
        .map_err(|e| format!("{}: {e}", cfg.hot_config))
}

fn rpc_of(cfg: &LongCfg, k: &rugsnipe_tx::senders::ApiKeys) -> Result<Rpc, String> {
    if cfg.rpc_url.is_empty() {
        return Err("long.toml: rpc_url is empty (a URL or cred:NAME)".into());
    }
    Ok(Rpc::new(&keys::resolve_url(k, &cfg.rpc_url)?))
}

fn run(args: &[String]) -> Result<(), String> {
    let cfg = load_cfg(args)?;
    let hot = load_hot(&cfg)?;
    let k = keys::api_keys(&cfg.api_keys)?;
    let rpc = rpc_of(&cfg, &k)?;
    // the wallet: required for real trading; paper uses it (if present) to
    // see our own transactions, which it never sends
    let signer = match keys::wallet(&cfg.wallet_file) {
        Ok(s) => Some(s),
        Err(e) if cfg.mode == Mode::On => {
            return Err(format!("mode on needs the long wallet: {e}"))
        }
        Err(e) => {
            eprintln!("long: no wallet ({e}): paper only");
            None
        }
    };
    let me = signer.as_ref().map(|s| s.pubkey()).unwrap_or_default();
    let (out_buy, out_sell) = if cfg.mode == Mode::On {
        (
            Some(Out::build(&hot, &k, &cfg.buy_senders)?),
            Some(Out::build(&hot, &k, &cfg.sell_senders)?),
        )
    } else {
        (None, None)
    };
    if !hot.feeds.grpc.enabled || hot.feeds.grpc.url.is_empty() {
        return Err(format!("{}: [feeds] grpc is not enabled", cfg.hot_config));
    }
    let url = keys::resolve_url(&k, &hot.feeds.grpc.url)?;
    let x_token = if hot.feeds.grpc.x_token.is_empty() {
        None
    } else {
        Some(
            k.get(&hot.feeds.grpc.x_token)
                .ok_or_else(|| {
                    format!(
                        "feeds.grpc.x_token {:?} not in the api-keys file",
                        hot.feeds.grpc.x_token
                    )
                })?
                .to_string(),
        )
    };
    println!(
        "long start: mode {:?} wallet {} copy {} min_sol {} stake {} SOL tp {}x stop {}x hold {}s max_open {} floats {:?} buy senders {:?} sell senders {:?} feed {}",
        cfg.mode,
        me,
        cfg.copy_wallet,
        cfg.min_sol,
        cfg.stake_sol,
        cfg.take_profit,
        cfg.stop,
        cfg.max_hold_s,
        cfg.max_open,
        cfg.floats,
        out_buy.as_ref().map(|o| o.labels()).unwrap_or_default(),
        out_sell.as_ref().map(|o| o.labels()).unwrap_or_default(),
        keys::redact(&url)
    );
    let oracle = Oracle::default();
    oracle.spawn(&cfg.price_api, cfg.float_pks(), Duration::from_secs(20));
    let copy = cfg.copy_pk();
    // real mode: the blockhash is kept fresh off the send path
    let bh = rugsnipe_long::chain::Blockhashes::default();
    if cfg.mode == Mode::On {
        bh.spawn(
            &keys::resolve_url(&k, &cfg.rpc_url)?,
            Duration::from_secs(3),
        );
    }
    let mut eng = Engine::new(cfg, me, signer, rpc, oracle, out_buy, out_sell)?;
    eng.set_blockhashes(bh);
    let (tx, rx) = std::sync::mpsc::channel();
    let h = feed::spawn(
        feed::FeedCfg {
            url,
            x_token,
            copied: copy,
            more: vec![],
            ours: (me != Pubkey::default()).then_some(me),
        },
        tx,
    );
    eng.set_feed(h);
    eng.run(rx);
    Ok(())
}

/// `+0200` (from `date +%z`) as seconds.
fn tz_offset(args: &[String]) -> i64 {
    let z = arg(args, "--tz").unwrap_or_default();
    let (sign, d) = match z.as_bytes().first() {
        Some(b'-') => (-1, &z[1..]),
        Some(b'+') => (1, &z[1..]),
        _ => (1, z.as_str()),
    };
    let h: i64 = d.get(..2).and_then(|x| x.parse().ok()).unwrap_or(0);
    let m: i64 = d.get(2..4).and_then(|x| x.parse().ok()).unwrap_or(0);
    sign * (h * 3600 + m * 60)
}

fn hhmm(ms: u64, off: i64) -> String {
    let s = (ms / 1000) as i64 + off;
    let d = s.rem_euclid(86_400);
    format!("{:02}:{:02}:{:02}", d / 3600, d % 3600 / 60, d % 60)
}

fn status(args: &[String]) -> Result<(), String> {
    let cfg = load_cfg(args)?;
    let off = tz_offset(args);
    let last: usize = arg(args, "--last")
        .and_then(|x| x.parse().ok())
        .unwrap_or(15);
    let dir = std::path::Path::new(&cfg.state_dir);
    let book = Book::load(&dir.join("positions.json"))?;
    let now = now_ms();
    let wallet = keys::wallet(&cfg.wallet_file).ok().map(|w| w.pubkey());
    println!(
        "== long copy (rugsnipe-long, docs/20): mode {:?}, wallet {}, copying {} buys of {}+ SOL, {} SOL each, tp {}x stop {}x {}s, max_open {}{}",
        cfg.mode,
        wallet.map_or("none (paper only)".into(), |w| w.to_string()),
        &cfg.copy_wallet[..8],
        cfg.min_sol,
        cfg.stake_sol,
        cfg.take_profit,
        cfg.stop,
        cfg.max_hold_s,
        cfg.max_open,
        if dir.join("KILL").exists() { "  KILL: no new buys" } else { "" }
    );
    if args.iter().any(|a| a == "--chain") {
        if let (Some(w), Ok(k)) = (wallet, keys::api_keys(&cfg.api_keys)) {
            if let Ok(mut rpc) = rpc_of(&cfg, &k) {
                let b = rpc
                    .balance(&w)
                    .map(|b| format!("{:.4}", b as f64 / 1e9))
                    .unwrap_or("?".into());
                let mut fl = vec![];
                for f in cfg.float_pks() {
                    let prog =
                        route::Chain::mint_program(&mut rpc, &f).unwrap_or(c::SPL_TOKEN_PROGRAM_ID);
                    let a = rpc.token_balance(&w, &f, &prog).unwrap_or(0);
                    let d = rpc.decimals(&f).unwrap_or(0);
                    fl.push(format!(
                        "{} {:.8}",
                        &f.to_string()[..8],
                        a as f64 / 10f64.powi(d as i32)
                    ));
                }
                println!(
                    "   wallet {b} SOL  floats: {}",
                    if fl.is_empty() {
                        "none".into()
                    } else {
                        fl.join(", ")
                    }
                );
            }
        }
    }
    let day = now / 86_400_000;
    for paper in [true, false] {
        let c: Vec<_> = book
            .positions
            .iter()
            .filter(|p| {
                p.paper == paper && p.state == State::Closed && p.closed_ms / 86_400_000 == day
            })
            .collect();
        if c.is_empty() && paper != (cfg.mode != Mode::On) {
            continue;
        }
        println!(
            "   today (the UTC day) {}: {} closed, {} won, net {:+.4} SOL; {} open; {} buys failed",
            if paper { "paper" } else { "REAL" },
            c.len(),
            c.iter().filter(|p| p.net_lamports > 0).count(),
            c.iter().map(|p| p.net_lamports).sum::<i64>() as f64 / 1e9,
            book.positions
                .iter()
                .filter(|p| p.paper == paper && p.live())
                .count(),
            book.positions
                .iter()
                .filter(|p| p.paper == paper
                    && p.state == State::Failed
                    && p.closed_ms / 86_400_000 == day)
                .count()
        );
    }
    let open: Vec<_> = book.positions.iter().filter(|p| p.live()).collect();
    if !open.is_empty() {
        println!("   open now:");
        println!(
            "     {:>4}  {:5}  {:8}  {:8}  {:>7}  {:11}  {:8}  {:>6}  {:>6}  {:>6}",
            "#", "side", "bought", "coin", "its SOL", "route", "state", "price", "peak", "held"
        );
        for p in open {
            println!(
                "     {:>4}  {:5}  {:8}  {:8}  {:>7.3}  {:11}  {:8}  {:>5.2}x  {:>5.2}x  {:>5}s",
                p.id,
                if p.paper { "paper" } else { "REAL" },
                hhmm(p.seen_ms, off),
                &p.mint[..8],
                p.its_lamports as f64 / 1e9,
                p.how,
                format!("{:?}", p.state).to_lowercase(),
                p.price(),
                p.peak,
                now.saturating_sub(p.seen_ms) / 1000
            );
        }
    }
    // the closed ones, newest first (closed.jsonl keeps them all)
    let text = std::fs::read_to_string(dir.join("closed.jsonl")).unwrap_or_default();
    let mut closed: Vec<rugsnipe_long::pos::Position> = text
        .lines()
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect();
    closed.sort_by_key(|p| std::cmp::Reverse(p.closed_ms));
    if !closed.is_empty() {
        println!("   last {} closed, newest first:", last.min(closed.len()));
        println!(
            "     {:>4}  {:5}  {:8}  {:8}  {:>7}  {:11}  {:11}  {:>6}  {:>6}  {:>6}  {:>8}  {:>7}",
            "#",
            "side",
            "bought",
            "coin",
            "its SOL",
            "route",
            "exit",
            "peak",
            "held",
            "",
            "net SOL",
            "pct"
        );
        for p in closed.iter().take(last) {
            println!(
                "     {:>4}  {:5}  {:8}  {:8}  {:>7.3}  {:11}  {:11}  {:>5.2}x  {:>5}s  {:>6}  {:>+8.4}  {:>+6.1}%",
                p.id,
                if p.paper { "paper" } else { "REAL" },
                hhmm(p.seen_ms, off),
                &p.mint[..8],
                p.its_lamports as f64 / 1e9,
                p.how,
                p.reason.map_or("?", |r| r.name()),
                p.peak,
                p.closed_ms.saturating_sub(p.seen_ms) / 1000,
                "",
                p.net_lamports as f64 / 1e9,
                p.net_lamports as f64 / p.stake_lamports.max(1) as f64 * 100.0
            );
        }
        let all: i64 = closed
            .iter()
            .filter(|p| !p.paper)
            .map(|p| p.net_lamports)
            .sum();
        let pap: i64 = closed
            .iter()
            .filter(|p| p.paper)
            .map(|p| p.net_lamports)
            .sum();
        println!(
            "   all closed: real {} ({:+.4} SOL), paper {} ({:+.4} SOL)",
            closed.iter().filter(|p| !p.paper).count(),
            all as f64 / 1e9,
            closed.iter().filter(|p| p.paper).count(),
            pap as f64 / 1e9
        );
    }
    // coins airdropped to the wallet and sold (`float sell`, `float book`)
    let ex = rugsnipe_long::extra::load(dir);
    if !ex.is_empty() {
        let today: Vec<_> = ex.iter().filter(|e| e.ms / 86_400_000 == day).collect();
        let sum = |v: &mut dyn Iterator<Item = i64>| v.sum::<i64>() as f64 / 1e9;
        let real_today: i64 = book
            .positions
            .iter()
            .filter(|p| !p.paper && p.state == State::Closed && p.closed_ms / 86_400_000 == day)
            .map(|p| p.net_lamports)
            .sum();
        let real_all: i64 = closed.iter().filter(|p| !p.paper).map(|p| p.net_lamports).sum();
        let ex_today = sum(&mut today.iter().map(|e| e.lamports));
        let ex_all = sum(&mut ex.iter().map(|e| e.lamports));
        println!(
            "   airdrops sold: today {} ({:+.4} SOL), all {} ({:+.4} SOL)",
            today.len(),
            ex_today,
            ex.len(),
            ex_all
        );
        println!(
            "   trades + airdrops: today {:+.4} SOL, all {:+.4} SOL",
            real_today as f64 / 1e9 + ex_today,
            real_all as f64 / 1e9 + ex_all
        );
    }
    Ok(())
}

/// Jupiter swap API v1 (lite).
const JUP: &str = "https://lite-api.jup.ag/swap/v1";

/// Book a sale outside the copy (an airdropped coin sold) in
/// `<state_dir>/extra.jsonl`: our SOL change in transaction `sig`.
fn book_extra(cfg: &LongCfg, rpc: &Rpc, me: &Pubkey, sig: &str) -> Result<String, String> {
    let mut tx = Err(String::new());
    for _ in 0..10 {
        tx = rpc.transaction(sig);
        if tx.is_ok() {
            break;
        }
        std::thread::sleep(Duration::from_secs(2));
    }
    let tx = tx?;
    if !tx["meta"]["err"].is_null() {
        return Err(format!("{sig} failed on chain"));
    }
    let d = rugsnipe_long::extra::sol_delta(&tx, &me.to_string()).ok_or("our wallet is not in it")?;
    let mint = tx["meta"]["preTokenBalances"]
        .as_array()
        .into_iter()
        .flatten()
        .find(|b| b["owner"].as_str() == Some(&me.to_string()) && !cfg.floats.iter().any(|f| Some(f.as_str()) == b["mint"].as_str()))
        .and_then(|b| b["mint"].as_str())
        .unwrap_or("?")
        .to_string();
    let e = rugsnipe_long::extra::Extra {
        ms: tx["blockTime"].as_u64().unwrap_or(0) * 1000,
        sig: sig.to_string(),
        mint,
        lamports: d,
    };
    let new = rugsnipe_long::extra::append(std::path::Path::new(&cfg.state_dir), &e)?;
    Ok(format!(
        "{} {} {:+.4} SOL ({})",
        if new { "booked" } else { "already booked:" },
        &e.mint[..e.mint.len().min(8)],
        d as f64 / 1e9,
        &sig[..8]
    ))
}

fn float(args: &[String]) -> Result<(), String> {
    let cfg = load_cfg(args)?;
    let k = keys::api_keys(&cfg.api_keys)?;
    let rpc = rpc_of(&cfg, &k)?;
    let signer = keys::wallet(&cfg.wallet_file)?;
    let me = signer.pubkey();
    let (side, mint) = (
        args.first().map(String::as_str),
        args.get(1).ok_or("float buy|sell MINT ...")?,
    );
    if side == Some("book") {
        let n = book_extra(&cfg, &rpc, &me, mint)?;
        println!("{n}");
        return Ok(());
    }
    let mint: Pubkey = mint.parse().map_err(|_| "MINT")?;
    let airdrop = side == Some("sell") && !cfg.float_pks().contains(&mint);
    let mut chain = rpc;
    let prog = route::Chain::mint_program(&mut chain, &mint).ok_or("unknown mint")?;
    let (input, output, amount) = match side {
        Some("buy") => {
            let s: f64 = args
                .get(2)
                .ok_or("float buy MINT SOL")?
                .parse()
                .map_err(|_| "SOL")?;
            (c::WSOL_MINT, mint, (s * 1e9) as u64)
        }
        Some("sell") => {
            let held = chain.token_balance(&me, &mint, &prog)?;
            let a = match args.get(2).map(String::as_str) {
                Some("all") | None => held,
                Some(x) => x
                    .parse::<u64>()
                    .map_err(|_| "AMOUNT (raw units) or all")?
                    .min(held),
            };
            (mint, c::WSOL_MINT, a)
        }
        _ => return Err("float buy MINT SOL | float sell MINT all|AMOUNT | float book SIG".into()),
    };
    if amount == 0 {
        return Err("nothing to swap".into());
    }
    let q = chain.rpc.get_json(&format!(
        "{JUP}/quote?inputMint={input}&outputMint={output}&amount={amount}&slippageBps=50"
    ))?;
    println!(
        "quote: {} {} -> {} {} (impact {}%)",
        q["inAmount"],
        &input.to_string()[..8],
        q["outAmount"],
        &output.to_string()[..8],
        q["priceImpactPct"]
    );
    let body = serde_json::json!({
        "quoteResponse": q,
        "userPublicKey": me.to_string(),
        "wrapAndUnwrapSol": true,
        "dynamicComputeUnitLimit": true,
        "prioritizationFeeLamports": {"priorityLevelWithMaxLamports": {"maxLamports": 2_000_000, "priorityLevel": "high"}}
    });
    let (st, text) = chain.rpc.post_raw(
        &format!("{JUP}/swap"),
        "application/json",
        body.to_string().as_bytes(),
    )?;
    if st != 200 {
        return Err(format!(
            "jupiter swap: HTTP {st}: {}",
            text.chars().take(200).collect::<String>()
        ));
    }
    let v: serde_json::Value = serde_json::from_str(&text).map_err(|e| e.to_string())?;
    let mut tx = base64::Engine::decode(
        &base64::engine::general_purpose::STANDARD,
        v["swapTransaction"].as_str().ok_or("no swapTransaction")?,
    )
    .map_err(|e| e.to_string())?;
    // [n_sigs (compact, 1 here)][sigs][message]: sign the message
    if tx.first() != Some(&1) {
        return Err("expected one signer".into());
    }
    let sig = signer.sign(&tx[65..]);
    tx[1..65].copy_from_slice(&sig);
    let s = chain.send(&tx)?;
    println!("sent {s}");
    for _ in 0..30 {
        std::thread::sleep(Duration::from_secs(2));
        if let Ok(st) = chain.statuses(std::slice::from_ref(&s)) {
            match st.first() {
                Some(Some(Ok(slot))) => {
                    println!(
                        "landed in slot {slot}; {} balance now {}",
                        &mint.to_string()[..8],
                        chain.token_balance(&me, &mint, &prog)?
                    );
                    if airdrop {
                        // not a float: an airdropped coin sold, part of the result
                        match book_extra(&cfg, &chain, &me, &s) {
                            Ok(n) => println!("{n}"),
                            Err(e) => println!("not booked ({e}): run `float book {s}` later"),
                        }
                    }
                    return Ok(());
                }
                Some(Some(Err(e))) => return Err(format!("failed: {e}")),
                _ => {}
            }
        }
    }
    Err("not landed after 60 s (check the signature)".into())
}

fn keygen(args: &[String]) -> Result<(), String> {
    use std::io::Read as _;
    let out = arg(args, "--out").ok_or("keygen --out PATH")?;
    if std::path::Path::new(&out).exists() {
        return Err(format!("{out} exists: not overwritten"));
    }
    let mut seed = zeroize::Zeroizing::new([0u8; 32]);
    std::fs::File::open("/dev/urandom")
        .and_then(|mut f| f.read_exact(&mut seed[..]))
        .map_err(|e| format!("/dev/urandom: {e}"))?;
    let signer = rugsnipe_tx::signer::HotSigner::from_seed(&seed);
    let pubkey = signer.pubkey();
    let mut bytes = zeroize::Zeroizing::new(Vec::with_capacity(64));
    bytes.extend_from_slice(&seed[..]);
    bytes.extend_from_slice(pubkey.as_ref());
    let json = zeroize::Zeroizing::new(format!(
        "[{}]",
        bytes
            .iter()
            .map(|b| b.to_string())
            .collect::<Vec<_>>()
            .join(",")
    ));
    #[cfg(unix)]
    {
        use std::io::Write as _;
        use std::os::unix::fs::OpenOptionsExt;
        let mut f = std::fs::OpenOptions::new()
            .write(true)
            .create_new(true)
            .mode(0o400)
            .open(&out)
            .map_err(|e| format!("{out}: {e}"))?;
        f.write_all(json.as_bytes())
            .map_err(|e| format!("{out}: {e}"))?;
    }
    // the file loads back to the same address
    let back = rugsnipe_tx::signer::HotSigner::load_file(std::path::Path::new(&out))
        .map_err(|e| format!("{out}: {e}"))?;
    if back.pubkey() != pubkey {
        return Err("the written keypair does not load back".into());
    }
    println!("{pubkey}");
    eprintln!(
        "wrote {out} (0400). Fund this address with SOL; keep a copy of the file somewhere safe."
    );
    Ok(())
}

// ---------------------------------------------------------------- copier

fn copy_cfg(args: &[String]) -> Result<rugsnipe_long::copier::CopierCfg, String> {
    let p = arg(args, "--config").unwrap_or("/etc/rugsnipe/copier.toml".into());
    let text = std::fs::read_to_string(&p).map_err(|e| format!("{p}: {e}"))?;
    rugsnipe_long::copier::CopierCfg::from_toml_str(&text)
}

/// The hot config's gRPC feed: its URL and token.
fn grpc_of(
    hot: &rugsnipe_core::config::Config,
    k: &rugsnipe_tx::senders::ApiKeys,
    file: &str,
) -> Result<(String, Option<String>), String> {
    if !hot.feeds.grpc.enabled || hot.feeds.grpc.url.is_empty() {
        return Err(format!("{file}: [feeds] grpc is not enabled"));
    }
    let url = keys::resolve_url(k, &hot.feeds.grpc.url)?;
    let x = if hot.feeds.grpc.x_token.is_empty() {
        None
    } else {
        Some(
            k.get(&hot.feeds.grpc.x_token)
                .ok_or_else(|| format!("feeds.grpc.x_token {:?} not in the api-keys file", hot.feeds.grpc.x_token))?
                .to_string(),
        )
    };
    Ok((url, x))
}

fn copy_run(args: &[String]) -> Result<(), String> {
    use rugsnipe_long::copier::{Copier, Exec, LiveExec, PaperExec};
    let cfg = copy_cfg(args)?;
    let text = std::fs::read_to_string(&cfg.hot_config).map_err(|e| format!("{}: {e}", cfg.hot_config))?;
    let hot = rugsnipe_core::config::Config::from_toml_str(&text).map_err(|e| format!("{}: {e}", cfg.hot_config))?;
    let k = keys::api_keys(&cfg.api_keys)?;
    if cfg.rpc_url.is_empty() {
        return Err("copier.toml: rpc_url is empty (a URL or cred:NAME)".into());
    }
    let rpc_url = keys::resolve_url(&k, &cfg.rpc_url)?;
    let (url, x_token) = grpc_of(&hot, &k, &cfg.hot_config)?;
    let wallets = cfg.wallets();
    let (exec, me): (Box<dyn Exec>, String) = match cfg.mode {
        Mode::On => {
            let signer = keys::copier_wallet(&cfg.wallet_file)
                .map_err(|e| format!("mode on needs the copier wallet: {e}"))?;
            let me = signer.pubkey().to_string();
            let out = if cfg.senders.is_empty() {
                None
            } else {
                Some(Out::build(&hot, &k, &cfg.senders)?)
            };
            (Box::new(LiveExec::new(Rpc::new(&rpc_url), signer, out, cfg.clone())), me)
        }
        Mode::Log => (Box::new(PaperExec::new(Rpc::new(&rpc_url), cfg.clone())), "paper".into()),
        Mode::Off => return Err("copier.toml: mode off".into()),
    };
    let mut cp = Copier::new(cfg.clone(), exec)?;
    let n = cp.load_state()?;
    let rules: Vec<String> = cfg
        .targets
        .iter()
        .map(|t| {
            format!(
                "{} {} {:?} its buy >= {} SOL, stake {} (frac {} cap {}), tp {} stop {} hold {} s, follow its sale {}, max_open {}",
                t.name, &t.wallet[..8], t.coins, t.min_sol, t.stake_sol, t.stake_frac, t.stake_cap_sol,
                t.take_profit, t.stop, t.max_hold_s, t.follow_sell, t.max_open
            )
        })
        .collect();
    println!(
        "copier start: mode {:?} wallet {me} open {n} daily stop {} SOL, max_open {} | {} | senders {:?} + rpc | feed {}",
        cfg.mode,
        cfg.daily_stop_sol,
        cfg.max_open,
        rules.join(" | "),
        cfg.senders,
        keys::redact(&url)
    );
    let (tx, rx) = std::sync::mpsc::channel();
    let _h = feed::spawn(
        feed::FeedCfg {
            url,
            x_token,
            copied: wallets[0],
            more: wallets[1..].to_vec(),
            ours: None,
        },
        tx,
    );
    // no buys until the feed says it is up
    cp.feed_up = false;
    loop {
        match rx.recv_timeout(Duration::from_millis(500)) {
            Ok(feed::FeedMsg::Tx(feed::Src::Copied, t)) => {
                // the feed's newest slot now, not the queue's: a buy that waited behind a swap is seen as old
                cp.tip_slot = feed::latest_slot();
                cp.on_tx(&t)
            }
            Ok(feed::FeedMsg::Up(u)) => cp.set_feed(u),
            Ok(_) => {}
            Err(std::sync::mpsc::RecvTimeoutError::Timeout) => {}
            Err(std::sync::mpsc::RecvTimeoutError::Disconnected) => {
                return Err("copier: the feed thread ended".into())
            }
        }
        cp.on_tick();
    }
}

fn copy_status(args: &[String]) -> Result<(), String> {
    use std::collections::BTreeMap;
    let cfg = copy_cfg(args)?;
    let off = tz_offset(args);
    let last: usize = arg(args, "--last").and_then(|x| x.parse().ok()).unwrap_or(15);
    let text = std::fs::read_to_string(&cfg.journal).unwrap_or_default();
    let now = now_ms();
    let day = |ms: u64| ((ms / 1000) as i64 + off).div_euclid(86_400);
    let today = day(now);
    #[derive(Default)]
    struct Agg {
        buys: u32,
        failed: u32,
        closed: u32,
        won: u32,
        net: i64,
        closed_today: u32,
        net_today: i64,
    }
    let mut by: BTreeMap<(String, bool), Agg> = BTreeMap::new();
    let mut sells = vec![];
    for line in text.lines() {
        let Ok(v) = serde_json::from_str::<serde_json::Value>(line) else { continue };
        let key = (v["target"].as_str().unwrap_or("-").to_string(), v["paper"].as_bool().unwrap_or(true));
        let ts = v["ts"].as_u64().unwrap_or(0);
        match v["ev"].as_str() {
            Some("buy") => by.entry(key).or_default().buys += 1,
            Some("buy-failed") => by.entry(key).or_default().failed += 1,
            Some("sell") => {
                let a = by.entry(key).or_default();
                let net = v["net"].as_i64().unwrap_or(0);
                a.closed += 1;
                a.net += net;
                if net > 0 {
                    a.won += 1;
                }
                if day(ts) == today {
                    a.closed_today += 1;
                    a.net_today += net;
                }
                sells.push(v);
            }
            _ => {}
        }
    }
    println!("copier ({:?}), times at UTC{:+}h", cfg.mode, off / 3600);
    println!("  {:<12} {:<5} {:>5} {:>6} {:>7} {:>5} {:>10} {:>7} {:>10}", "wallet", "kind", "buys", "failed", "closed", "won", "net SOL", "today", "today SOL");
    for ((t, paper), a) in &by {
        println!(
            "  {:<12} {:<5} {:>5} {:>6} {:>7} {:>5} {:>+10.4} {:>7} {:>+10.4}",
            t,
            if *paper { "paper" } else { "real" },
            a.buys,
            a.failed,
            a.closed,
            a.won,
            a.net as f64 / 1e9,
            a.closed_today,
            a.net_today as f64 / 1e9
        );
    }
    if let Ok(st) = std::fs::read_to_string(&cfg.state) {
        if let Ok(book) = serde_json::from_str::<Vec<rugsnipe_long::copier::Pos>>(&st) {
            let open: Vec<_> = book.iter().filter(|p| p.open()).collect();
            println!("  open now: {}", open.len());
            for p in open {
                println!(
                    "    #{} {} {} since {} ({} s), cost {:.4} SOL, last value {}{}",
                    p.id,
                    p.target,
                    &p.mint[..8],
                    hhmm(p.opened_ms, off),
                    now.saturating_sub(p.opened_ms) / 1000,
                    p.cost as f64 / 1e9,
                    p.last_value.map(|v| format!("{:.4} SOL", v as f64 / 1e9)).unwrap_or("-".into()),
                    p.exit.as_ref().map(|r| format!(", selling ({r}, {} tries)", p.tries)).unwrap_or_default()
                );
            }
        }
    }
    println!("  last {} closed:", last.min(sells.len()));
    for v in sells.iter().rev().take(last) {
        println!(
            "    {} {} {} {} held {} s, cost {:.4} back {:.4} net {:+.4} SOL ({})",
            hhmm(v["ts"].as_u64().unwrap_or(0), off),
            v["target"].as_str().unwrap_or("-"),
            &v["mint"].as_str().unwrap_or("-")[..8.min(v["mint"].as_str().unwrap_or("-").len())],
            v["reason"].as_str().unwrap_or("-"),
            v["held_s"].as_u64().unwrap_or(0),
            v["cost"].as_u64().unwrap_or(0) as f64 / 1e9,
            v["proceeds"].as_u64().unwrap_or(0) as f64 / 1e9,
            v["net"].as_i64().unwrap_or(0) as f64 / 1e9,
            v["route"].as_str().unwrap_or("-")
        );
    }
    Ok(())
}

fn copy_replay(args: &[String]) -> Result<(), String> {
    use rugsnipe_long::copier::{Copier, PaperExec};
    let mut cfg = copy_cfg(args)?;
    cfg.mode = Mode::Log;
    // a replay is paper at today's prices: it never writes the service's journal or state (its paper positions would
    // be picked up by the running copier); --journal FILE keeps its lines
    cfg.state = String::new();
    cfg.journal = arg(args, "--journal").unwrap_or_default();
    cfg.kill_file = String::new();
    let url = match arg(args, "--rpc") {
        Some(u) if u.starts_with('@') => std::fs::read_to_string(&u[1..])
            .map_err(|e| format!("{}: {e}", &u[1..]))?
            .trim()
            .to_string(),
        Some(u) => u,
        None => cfg.rpc_url.clone(),
    };
    if !url.starts_with("http") {
        return Err("copy-replay: --rpc URL (or @file holding it)".into());
    }
    let tick_s: u64 = arg(args, "--tick-s").and_then(|x| x.parse().ok()).unwrap_or(30);
    // the signatures: every argument that is not a flag or a flag's value
    let mut sigs = vec![];
    let mut i = 0;
    while i < args.len() {
        if args[i].starts_with("--") {
            i += 2;
            continue;
        }
        sigs.push(args[i].clone());
        i += 1;
    }
    let rpc = Rpc::new(&url);
    let mut cp = Copier::new(cfg.clone(), PaperExec::new(Rpc::new(&url), cfg.clone()))?;
    for s in &sigs {
        let v = rpc.transaction(s)?;
        let t = TxLite::from_rpc_json(&v)?;
        println!("replay {} slot {} signer {}", &s[..12.min(s.len())], t.slot, t.signer().map(|p| p.to_string()).unwrap_or_default());
        cp.on_tx(&t);
        cp.on_tick();
    }
    let end = now_ms() + tick_s * 1000;
    while now_ms() < end && cp.open_count(None) > 0 {
        std::thread::sleep(Duration::from_millis(500));
        cp.on_tick();
    }
    println!(
        "replay done: {} open, today's result {:+.4} SOL (paper)",
        cp.open_count(None),
        cp.day_net() as f64 / 1e9
    );
    Ok(())
}
