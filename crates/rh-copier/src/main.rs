//! rh-copier run | status [--tz +0200] [--last N] | keygen FILE | address     [--config /etc/rugsnipe/rh-copier.toml]
//! The live loop: the node's WebSocket feed (every Pons CurveBuy / CurveSell) -> the engine -> buys and sales signed
//! here and sent to every send url, each confirmed from its receipt. One wallet copies every leader. Journal lines
//! start with "rh " (journalctl -u rh-copier). The state dir holds state.json (open positions, the day's result),
//! closed.jsonl (every closed trade), failed.jsonl (failed buys) and its.json (the leaders' own trips, for status).
use rh_copier::chain::{self, Rpc, Wallet};
use rh_copier::config::Config;
use rh_copier::engine::{log, short, Action, CurveSt, Engine, PosState, Position};
use serde_json::{json, Value};
use std::io::Write as _;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use tokio::sync::{mpsc, Mutex};

fn now_ms() -> u64 { std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).map(|d| d.as_millis() as u64).unwrap_or(0) }

struct Ctx { cfg: Config, rpc: Rpc, wallet: Wallet, eng: Mutex<Engine>, nonce: AtomicU64, gas: AtomicU64, seq: AtomicU64, dir: String }

/// under systemd the key comes as a credential (LoadCredential=rh-wallet:...); by hand, the config's wallet_file
fn wallet_path(cfg: &Config) -> String {
    std::env::var("CREDENTIALS_DIRECTORY").ok().map(|d| format!("{d}/rh-wallet")).filter(|p| std::path::Path::new(p).exists()).unwrap_or(cfg.wallet_file.clone())
}
fn arg(args: &[String], k: &str) -> Option<String> { args.iter().position(|a| a == k).and_then(|i| args.get(i + 1)).cloned() }

fn main() {
    // the TLS engine, chosen once: the workspace build gives rustls both aws-lc-rs and ring (other crates bring ring),
    // and with two it refuses to pick and panics on the first TLS connection (the crash of Nov 18 22:03 UTC on the box)
    let _ = rustls::crypto::aws_lc_rs::default_provider().install_default();
    let args: Vec<String> = std::env::args().collect();
    let cfg_path = arg(&args, "--config").unwrap_or("/etc/rugsnipe/rh-copier.toml".into());
    let cmd = args.get(1).map(String::as_str).unwrap_or("");
    let rt = tokio::runtime::Builder::new_multi_thread().worker_threads(4).enable_all().build().expect("runtime");
    let r = match cmd {
        "keygen" => match args.get(2) { Some(p) => chain::keygen(p).map(|a| println!("new wallet {a}, key in {p} (root-only, never printed)")), None => Err("keygen FILE".into()) },
        "address" => Config::load(&cfg_path).and_then(|c| Wallet::load(&c.wallet_file)).map(|w| println!("{}", w.address)),
        "status" => Config::load(&cfg_path).and_then(|c| rt.block_on(status(c, &args))),
        "run" => Config::load(&cfg_path).and_then(|c| rt.block_on(run(c))),
        _ => Err("usage: rh-copier run | status [--tz +0200] [--last N] | keygen FILE | address  [--config FILE]".into()),
    };
    if let Err(e) = r { eprintln!("rh-copier: {e}"); std::process::exit(1) }
}

// ---------------------------------------------------------------- state on disk
#[derive(serde::Serialize, serde::Deserialize, Default)]
struct Disk { open: Vec<Value>, day: u64, day_pnl: f64, seq: u64 }
fn load_disk(dir: &str) -> Disk { std::fs::read_to_string(format!("{dir}/state.json")).ok().and_then(|s| serde_json::from_str(&s).ok()).unwrap_or_default() }
fn pos_json(p: &Position) -> Value {
    json!({"id": p.id, "curve": p.curve, "leader": p.leader, "its_eth": p.its_eth, "its_block": p.its_block, "our_block": p.our_block, "its_price": p.its_price, "its_ms": p.its_ms,
        "eth_in": p.eth_in, "tokens": p.tokens, "peak": p.peak, "hi_ms": p.hi_ms, "state": format!("{:?}", p.state).to_lowercase()})
}
async fn save(ctx: &Ctx) {
    let d = { let eng = ctx.eng.lock().await;
        Disk { open: eng.pos.values().filter(|p| p.state != PosState::Buying).map(pos_json).collect(), day: eng.day, day_pnl: eng.day_pnl, seq: ctx.seq.load(Ordering::SeqCst) } };
    let f = format!("{}/state.json", ctx.dir); let tmp = format!("{f}.tmp");
    if std::fs::write(&tmp, serde_json::to_string_pretty(&d).unwrap_or_default()).is_ok() { let _ = std::fs::rename(&tmp, &f); }
}
fn append(dir: &str, file: &str, v: &Value) {
    if let Ok(mut f) = std::fs::OpenOptions::new().create(true).append(true).open(format!("{dir}/{file}")) { let _ = writeln!(f, "{v}"); }
}
fn read_jsonl(dir: &str, file: &str) -> Vec<Value> {
    std::fs::read_to_string(format!("{dir}/{file}")).unwrap_or_default().lines().filter_map(|l| serde_json::from_str(l).ok()).collect()
}

// ---------------------------------------------------------------- run
async fn run(cfg: Config) -> Result<(), String> {
    let wallet = Wallet::load(&wallet_path(&cfg))?;
    let rpc = Rpc::new(&cfg.rpc_url, &cfg.send_urls);
    std::fs::create_dir_all(&cfg.state_dir).map_err(|e| e.to_string())?;
    let chain_id = rpc.u64_of("eth_chainId", json!([])).await? as u64;
    if chain_id != cfg.chain_id { return Err(format!("the RPC is chain {chain_id}, the config says {}", cfg.chain_id)) }
    let nonce = rpc.u64_of("eth_getTransactionCount", json!([wallet.address, "pending"])).await? as u64;
    let bal = rpc.u64_of("eth_getBalance", json!([wallet.address, "latest"])).await? as f64 / 1e18;
    let gas = rpc.u64_of("eth_gasPrice", json!([])).await? as u64;
    let mut eng = Engine::new(cfg.clone(), &wallet.address);
    // positions left open by the last run
    let d = load_disk(&cfg.state_dir); eng.day = d.day; eng.day_pnl = d.day_pnl;
    for p in d.open {
        let c = p["curve"].as_str().unwrap_or("").to_string(); if c.is_empty() { continue }
        let f = |k: &str| p[k].as_f64().unwrap_or(0.0); let u = |k: &str| p[k].as_u64().unwrap_or(0);
        eng.pos.insert(c.clone(), Position { id: u("id"), curve: c, leader: p["leader"].as_str().unwrap_or("").into(), its_eth: f("its_eth"), its_block: u("its_block"), our_block: u("our_block"),
            its_price: f("its_price"), its_ms: u("its_ms"), eth_in: f("eth_in"), tokens: f("tokens"), peak: p["peak"].as_f64().unwrap_or(1.0), hi_ms: u("hi_ms"),
            state: PosState::Open, flow: Default::default(), retry_ms: 0 });
    }
    log(&format!("start mode {} wallet {} balance {:.4} ETH nonce {} gas {:.4} gwei; {} leaders, {} ETH a copy, max_open {}, daily stop {}; {} open from the last run",
        cfg.mode, wallet.address, bal, nonce, gas as f64 / 1e9, cfg.leaders.len(), cfg.stake_eth, cfg.max_open, cfg.daily_stop_eth, eng.pos.len()));
    for (i, l) in cfg.leaders.iter().enumerate() { log(&format!("wallet {} = {}", i + 1, l.address)) }
    let ctx = Arc::new(Ctx { cfg: cfg.clone(), rpc, wallet, eng: Mutex::new(eng), nonce: AtomicU64::new(nonce), gas: AtomicU64::new(gas), seq: AtomicU64::new(d.seq), dir: cfg.state_dir.clone() });
    // reserves of the curves held after a restart
    let held: Vec<String> = ctx.eng.lock().await.pos.keys().cloned().collect();
    for c in held { if let Ok((q, t, r)) = ctx.rpc.reserves(&c).await { ctx.eng.lock().await.set_curve(&c, CurveSt { q, t, real_q: r }); } }

    let (tx, mut rx) = mpsc::channel::<Value>(10_000);
    tokio::spawn(feed(cfg.ws_url.clone(), tx));
    // gas price, and the reserves of held curves, every 15 s (the tracked reserves drift a little: fees, rounding)
    { let ctx = ctx.clone(); tokio::spawn(async move { loop {
        tokio::time::sleep(std::time::Duration::from_secs(15)).await;
        if let Ok(g) = ctx.rpc.u64_of("eth_gasPrice", json!([])).await { ctx.gas.store(g as u64, Ordering::Relaxed) }
        let held: Vec<String> = ctx.eng.lock().await.pos.keys().cloned().collect();
        for c in held { if let Ok((q, t, r)) = ctx.rpc.reserves(&c).await { ctx.eng.lock().await.set_curve(&c, CurveSt { q, t, real_q: r }); } }
    } }); }
    let mut tick = tokio::time::interval(std::time::Duration::from_millis(500));
    // the heartbeat: every 10 minutes, the trades the feed brought (Pons trades all day: 0 means a dead feed)
    let beat_s: u64 = std::env::var("RH_HEARTBEAT_S").ok().and_then(|x| x.parse().ok()).unwrap_or(600);
    let (mut n_tr, mut n_lead, mut last_blk, mut beat) = (0u64, 0u64, 0u64, std::time::Instant::now());
    loop {
        if beat.elapsed().as_secs() >= beat_s {
            let e = ctx.eng.lock().await;
            log(&format!("heartbeat: {n_tr} curve trades in {beat_s} s, {n_lead} buys by the copied wallets, last block {last_blk}; {} open, day {:+.5} ETH", e.pos.len(), e.day_pnl));
            drop(e); n_tr = 0; n_lead = 0; beat = std::time::Instant::now();
        }
        tokio::select! {
            Some(l) = rx.recv() => {
                let Some(tr) = chain::decode_trade(&l, now_ms()) else { continue };
                n_tr += 1; last_blk = last_blk.max(tr.block);
                if tr.buy && ctx.cfg.leaders.iter().any(|x| x.address.eq_ignore_ascii_case(&tr.user)) {
                    n_lead += 1;
                    // how late the feed brought it: the node's head when it arrived (read in the background, after the buy is sent)
                    let (c2, b, u) = (ctx.clone(), tr.block, tr.user.clone());
                    tokio::spawn(async move { if let Ok(h) = c2.rpc.u64_of("eth_blockNumber", json!([])).await {
                        log(&format!("signal {} buy at block {b}: the node was at {h} when it arrived (+{} blocks)", short(&u), (h as u64).saturating_sub(b))) } });
                }
                let acts = ctx.eng.lock().await.on_trade(&tr, now_ms());
                for a in acts { tokio::spawn(act(ctx.clone(), a)); }
            }
            _ = tick.tick() => {
                let acts = ctx.eng.lock().await.tick(now_ms());
                for a in acts { tokio::spawn(act(ctx.clone(), a)); }
            }
        }
    }
}

async fn feed(url: String, tx: mpsc::Sender<Value>) {
    use futures_util::{SinkExt, StreamExt};
    use tokio_tungstenite::tungstenite::Message;
    loop {
        match tokio_tungstenite::connect_async(url.as_str()).await {
            Ok((mut ws, _)) => {
                let sub = json!({"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["logs", {"topics": [[chain::topic_buy(), chain::topic_sell()]]}]});
                if ws.send(Message::Text(sub.to_string().into())).await.is_ok() {
                    log("feed connected");
                    let mut ping = tokio::time::interval(std::time::Duration::from_secs(20));
                    let mut last = std::time::Instant::now();
                    loop {
                        tokio::select! {
                            m = ws.next() => match m {
                                Some(Ok(Message::Text(t))) => {
                                    last = std::time::Instant::now();
                                    if let Ok(v) = serde_json::from_str::<Value>(&t) {
                                        if v["method"] == "eth_subscription" && !v["params"]["result"]["removed"].as_bool().unwrap_or(false) { let _ = tx.send(v["params"]["result"].clone()).await; }
                                        else if v.get("error").is_some() { log(&format!("feed error {}", v["error"])); break }
                                    }
                                }
                                Some(Ok(_)) => { last = std::time::Instant::now() }
                                _ => break,
                            },
                            _ = ping.tick() => {
                                // Pons trades every few seconds all day: 3 minutes of silence is a dead feed
                                if last.elapsed().as_secs() > 180 { log("feed silent 180 s"); break }
                                if ws.send(Message::Ping(vec![].into())).await.is_err() { break }
                            }
                        }
                    }
                }
                log("feed lost, reconnecting");
            }
            Err(e) => log(&format!("feed connect failed: {e}")),
        }
        tokio::time::sleep(std::time::Duration::from_secs(1)).await;
    }
}

async fn resync_nonce(ctx: &Ctx) {
    if let Ok(n) = ctx.rpc.u64_of("eth_getTransactionCount", json!([ctx.wallet.address, "pending"])).await { ctx.nonce.store(n as u64, Ordering::SeqCst) }
}
fn max_fee(ctx: &Ctx) -> u128 { (ctx.gas.load(Ordering::Relaxed) as f64 * ctx.cfg.fee_mult) as u128 }

/// sign, send, wait for the receipt; Ok(receipt) when it landed with status 1
async fn send(ctx: &Ctx, to: &str, value: u128, data: &str, gas: u64, what: &str) -> Result<Value, String> {
    let n = ctx.nonce.fetch_add(1, Ordering::SeqCst); let t0 = std::time::Instant::now();
    let raw = ctx.wallet.sign(ctx.cfg.chain_id, n, to, value, data, gas, max_fee(ctx))?;
    let (r, times) = ctx.rpc.send_raw(&raw).await;
    let h = match r { Ok(h) => h, Err(e) => { resync_nonce(ctx).await; return Err(format!("{what} not sent ({times}): {e}")) } };
    let sent_ms = t0.elapsed().as_millis();
    match ctx.rpc.receipt(&h, 20).await {
        Some(r) if r["status"].as_str() == Some("0x1") => {
            let b = u64::from_str_radix(r["blockNumber"].as_str().unwrap_or("0x0").trim_start_matches("0x"), 16).unwrap_or(0);
            log(&format!("{what} landed {h} nonce {n} block {b} in {} ms (sent in {sent_ms} ms: {times})", t0.elapsed().as_millis())); Ok(r)
        }
        Some(_) => Err(format!("{what} {h} reverted")),
        None => { resync_nonce(ctx).await; Err(format!("{what} {h} not landed in 20 s")) }
    }
}

fn closed_rec(p: &Position, eth_out: f64, pnl: f64, why: &str, paper: bool) -> Value {
    let mut v = pos_json(p); let now = now_ms();
    v["closed_ms"] = json!(now); v["eth_out"] = json!(eth_out); v["pnl"] = json!(pnl); v["why"] = json!(why);
    v["held_s"] = json!(now.saturating_sub(p.its_ms) / 1000); v["paper"] = json!(paper); v.as_object_mut().map(|o| o.remove("state")); v
}

async fn act(ctx: Arc<Ctx>, a: Action) {
    match a {
        Action::Buy { curve, leader, eth, min_tokens } => {
            let id = ctx.seq.fetch_add(1, Ordering::SeqCst) + 1;
            let n = ctx.cfg.leaders.iter().position(|l| l.address.eq_ignore_ascii_case(&leader)).map_or(0, |i| i + 1);
            let its = { let mut e = ctx.eng.lock().await; e.pos.get_mut(&curve).map(|p| { p.id = id; p.its_eth }).unwrap_or(0.0) };
            log(&format!("buy #{id} wallet {n} {curve} its {its:.4} ETH; ours {eth:.4} ETH min {min_tokens:.0} tokens"));
            if std::path::Path::new(&format!("{}/KILL", ctx.dir)).exists() { log(&format!("skip #{id}: KILL file, no new buys")); ctx.eng.lock().await.on_bought(&curve, 0.0, now_ms()); return }
            if ctx.cfg.mode != "on" { let exp = { let e = ctx.eng.lock().await; e.curves.get(&curve).map_or(0.0, |c| c.tokens_for(eth, rh_copier::engine::FEE)) }; ctx.eng.lock().await.on_bought(&curve, exp, now_ms()); log(&format!("paper fill #{id} {:.0} tokens", exp)); save(&ctx).await; return }
            let me = ctx.wallet.address.clone();
            // the buy, and right behind it (the next nonce, without waiting for the buy's receipt) the approval for the
            // later sale, so a quick take profit never meets an unapproved token; a wasted approval costs ~0.000002 ETH
            let (bdata, bwhat) = (chain::buy_data(chain::wei(eth), chain::tok_units(min_tokens), &me), format!("buy #{id}"));
            let buy = send(&ctx, &curve, chain::wei(eth), &bdata, ctx.cfg.gas_buy, &bwhat);   // takes its nonce on the first poll
            let approve = async { match ctx.rpc.token_of(&curve).await {
                Ok(tok) => if let Err(e) = send(&ctx, &tok, 0, &chain::approve_data(&curve), ctx.cfg.gas_approve, &format!("approve #{id}")).await { log(&format!("WARNING {e}")) },
                Err(e) => log(&format!("WARNING token of #{id} failed: {e}; its sale fails until approved")) } };
            let (r, ()) = tokio::join!(buy, approve);
            match r {
                Ok(rc) => {
                    let got = rc["logs"].as_array().into_iter().flatten().filter_map(|l| chain::decode_trade(l, now_ms())).find(|t| t.buy && t.user == me && t.curve == curve);
                    match got { Some(t) => {
                                    // the lag: blocks between its buy and ours (the backtest assumed 2, 3 and 5; a block is ~0.1 s)
                                    let blk = t.block; let lag = { let mut e = ctx.eng.lock().await; e.on_bought(&curve, t.tokens, now_ms());
                                        e.pos.get_mut(&curve).map_or(0, |p| { p.our_block = blk; blk.saturating_sub(p.its_block) }) };
                                    log(&format!("fill #{id} {:.0} tokens for {:.4} ETH, block {blk}, lag {lag} blocks behind its buy", t.tokens, t.quote)) }
                                None => { log(&format!("buy-failed #{id}: no CurveBuy in the receipt")); ctx.eng.lock().await.on_bought(&curve, 0.0, now_ms()) } }
                }
                Err(e) => {
                    log(&format!("buy-failed #{id}: {e}")); ctx.eng.lock().await.on_bought(&curve, 0.0, now_ms());
                    append(&ctx.dir, "failed.jsonl", &json!({"id": id, "t": now_ms(), "curve": curve, "leader": leader, "err": e}));
                }
            }
            save(&ctx).await;
        }
        Action::Sell { curve, tokens, min_eth, why } => {
            let id = ctx.eng.lock().await.pos.get(&curve).map_or(0, |p| p.id);
            if ctx.cfg.mode != "on" {
                let out = min_eth / (1.0 - ctx.cfg.sell_slippage);
                if let Some((pnl, p)) = ctx.eng.lock().await.on_sold_pos(&curve, Some(out), now_ms()) {
                    log(&format!("paper closed #{id} {why} net {pnl:+.4} ETH")); append(&ctx.dir, "closed.jsonl", &closed_rec(&p, out, pnl, why, true));
                }
                save(&ctx).await; return
            }
            let me = ctx.wallet.address.clone();
            // sell what the wallet holds (the fill's token count is a float; the balance is exact)
            let units = match ctx.rpc.token_of(&curve).await { Ok(tok) => ctx.rpc.balance_of(&tok, &me).await.unwrap_or(0), Err(_) => 0 };
            let units = if units == 0 { chain::tok_units(tokens * 0.999) } else { units };
            log(&format!("sell #{id} {why} {:.0} tokens min {min_eth:.4} ETH", units as f64 / 1e18));
            let mut res = None;
            for (i, m) in [min_eth, min_eth * 0.5, 0.0].iter().enumerate() {   // the floor falls on a retry: getting out matters more
                match send(&ctx, &curve, 0, &chain::sell_data(units, chain::wei(*m), &me), ctx.cfg.gas_sell, &format!("sell #{id} try {i}")).await {
                    Ok(rc) => { res = rc["logs"].as_array().into_iter().flatten().filter_map(|l| chain::decode_trade(l, now_ms())).find(|t| !t.buy && t.user == me && t.curve == curve).map(|t| t.quote); break }
                    Err(e) => log(&format!("sell-failed #{id}: {e}")),
                }
            }
            match ctx.eng.lock().await.on_sold_pos(&curve, res, now_ms()) {
                Some((pnl, p)) => {
                    let out = res.unwrap_or(0.0);
                    log(&format!("closed #{id} {why} net {pnl:+.4} ETH ({:+.1}%) held {}s", 100.0 * pnl / p.eth_in.max(1e-9), now_ms().saturating_sub(p.its_ms) / 1000));
                    append(&ctx.dir, "closed.jsonl", &closed_rec(&p, out, pnl, why, false));
                }
                None => log(&format!("CRITICAL sale of #{id} failed 3 times; retried in 5 s")),
            }
            save(&ctx).await;
        }
    }
}

// ---------------------------------------------------------------- status (the same layout as rugsnipe-long status)
fn tz_offset(args: &[String]) -> i64 {
    let z = arg(args, "--tz").unwrap_or_default();
    let (sign, d) = match z.as_bytes().first() { Some(b'-') => (-1, &z[1..]), Some(b'+') => (1, &z[1..]), _ => (1, z.as_str()) };
    let h: i64 = d.get(..2).and_then(|x| x.parse().ok()).unwrap_or(0); let m: i64 = d.get(2..4).and_then(|x| x.parse().ok()).unwrap_or(0);
    sign * (h * 3600 + m * 60)
}
fn hhmm(ms: u64, off: i64) -> String { let d = ((ms / 1000) as i64 + off).rem_euclid(86_400); format!("{:02}:{:02}:{:02}", d / 3600, d % 3600 / 60, d % 60) }

/// the leader's own trip on a coin: (its pct, seconds from its buy to its last sale; None while it holds)
#[derive(serde::Serialize, serde::Deserialize, Clone)]
struct ItsTrip { pct: Option<f64>, sold_s: Option<u64>, holding: bool }
async fn its_trip(rpc: &Rpc, curve: &str, leader: &str, from: u64, to: u64) -> Result<ItsTrip, String> {
    let logs = rpc.curve_logs(curve, from, to).await?;
    let (mut ein, mut eout, mut tin, mut tout, mut last) = (0.0, 0.0, 0.0, 0.0, 0u64);
    for l in &logs {
        let Some(t) = chain::decode_trade(l, 0) else { continue };
        if !t.user.eq_ignore_ascii_case(leader) { continue }
        if t.buy { ein += t.quote; tin += t.tokens } else { eout += t.quote; tout += t.tokens; last = t.block }
    }
    if ein <= 0.0 { return Err("its buy not found".into()) }
    let holding = tout < tin * 0.99;
    let sold_s = if !holding && last > 0 { Some(rpc.block_time(last).await?.saturating_sub(rpc.block_time(from).await?)) } else { None };
    Ok(ItsTrip { pct: (!holding).then(|| 100.0 * (eout - ein) / ein), sold_s, holding })
}

async fn status(cfg: Config, args: &[String]) -> Result<(), String> {
    let off = tz_offset(args); let last: usize = arg(args, "--last").and_then(|x| x.parse().ok()).unwrap_or(15);
    let dir = cfg.state_dir.clone(); let d = load_disk(&dir); let now = now_ms(); let day = now / 86_400_000;
    let rpc = Rpc::new(&cfg.rpc_url, &cfg.send_urls);
    let addr = Wallet::load(&cfg.wallet_file).map(|w| w.address).unwrap_or_else(|_| "none".into());
    let wn = |a: &str| cfg.leaders.iter().position(|l| l.address.eq_ignore_ascii_case(a)).map_or("?".to_string(), |i| (i + 1).to_string());
    println!("== Robinhood copy (rh-copier, Pons): mode {:?}, wallet {addr}, copying {} wallets, {} ETH each, max_open {}, daily stop {}{}",
        cfg.mode, cfg.leaders.len(), cfg.stake_eth, cfg.max_open, cfg.daily_stop_eth, if std::path::Path::new(&format!("{dir}/KILL")).exists() { "  KILL: no new buys" } else { "" });
    let eth_usd: Option<f64> = async {
        let r = reqwest::Client::builder().timeout(std::time::Duration::from_secs(8)).build().ok()?.get("https://api.coinbase.com/v2/prices/ETH-USD/spot").send().await.ok()?;
        r.json::<Value>().await.ok()?["data"]["amount"].as_str()?.parse().ok()
    }.await;
    let bal = rpc.u64_of("eth_getBalance", json!([addr, "latest"])).await.map(|b| format!("{:.5}", b as f64 / 1e18)).unwrap_or("?".into());
    println!("   wallet {bal} ETH{}", eth_usd.map_or(String::new(), |u| format!("  (ETH ${u:.2})")));
    let usd = |e: f64| eth_usd.map_or(String::new(), |u| format!(" (${:+.2})", e * u));
    let mut closed = read_jsonl(&dir, "closed.jsonl"); closed.sort_by_key(|c| std::cmp::Reverse(c["closed_ms"].as_u64().unwrap_or(0)));
    let failed = read_jsonl(&dir, "failed.jsonl");
    let pnl = |c: &Value| c["pnl"].as_f64().unwrap_or(0.0);
    let real = |c: &&Value| !c["paper"].as_bool().unwrap_or(false);
    let today: Vec<&Value> = closed.iter().filter(real).filter(|c| c["closed_ms"].as_u64().unwrap_or(0) / 86_400_000 == day).collect();
    println!("   today (the UTC day) REAL: {} closed, {} won, net {:+.5} ETH{}; {} open; {} buys failed", today.len(), today.iter().filter(|c| pnl(c) > 0.0).count(),
        today.iter().map(|c| pnl(c)).sum::<f64>(), usd(today.iter().map(|c| pnl(c)).sum()), d.open.len(),
        failed.iter().filter(|f| f["t"].as_u64().unwrap_or(0) / 86_400_000 == day).count());
    if !d.open.is_empty() {
        println!("   open now:");
        println!("     {:>4}  {:6}  {:8}  {:10}  {:>7}  {:8}  {:>6}  {:>6}", "#", "wallet", "bought", "coin", "its ETH", "state", "peak", "held");
        for p in &d.open {
            println!("     {:>4}  {:6}  {:8}  {:10}  {:>7.4}  {:8}  {:>5.2}x  {:>5}s", p["id"].as_u64().unwrap_or(0), wn(p["leader"].as_str().unwrap_or("")), hhmm(p["its_ms"].as_u64().unwrap_or(0), off),
                short(p["curve"].as_str().unwrap_or("")), p["its_eth"].as_f64().unwrap_or(0.0), p["state"].as_str().unwrap_or(""), p["peak"].as_f64().unwrap_or(0.0),
                now.saturating_sub(p["its_ms"].as_u64().unwrap_or(0)) / 1000);
        }
    }
    if !closed.is_empty() {
        let its_path = format!("{dir}/its.json");
        let mut cache: std::collections::HashMap<String, ItsTrip> = std::fs::read_to_string(&its_path).ok().and_then(|t| serde_json::from_str(&t).ok()).unwrap_or_default();
        let hist = Rpc::new(&cfg.logs_url, &[]);
        let tip = hist.u64_of("eth_blockNumber", json!([])).await.unwrap_or(0) as u64;
        let mut its_err: Option<String> = None;
        println!("   last {} closed, newest first:", last.min(closed.len()));
        println!("     {:>4}  {:5}  {:6}  {:8}  {:10}  {:>7}  {:>4}  {:16}  {:>6}  {:>6}  {:>9}  {:>7}  {:>7}  {:>8}  {:>8}",
            "#", "side", "wallet", "bought", "coin", "its ETH", "lag", "exit", "peak", "held", "net ETH", "pct", "net $", "its pct", "it sold");
        for c in closed.iter().take(last) {
            let curve = c["curve"].as_str().unwrap_or(""); let leader = c["leader"].as_str().unwrap_or(""); let blk = c["its_block"].as_u64().unwrap_or(0);
            let key = format!("{curve}:{leader}");
            let its = match cache.get(&key) { Some(t) => Some(t.clone()), None if blk > 0 && tip > blk => {
                // up to 3.3 hours after its buy (120,000 blocks); later sales show as holding
                match its_trip(&hist, curve, leader, blk, tip.min(blk + 120_000)).await {
                    Ok(t) => { if !t.holding { cache.insert(key, t.clone()); } Some(t) }
                    Err(e) => { its_err.get_or_insert(format!("{}: {e}", short(curve))); None }
                } }
                None => None };
            let e_in = c["eth_in"].as_f64().unwrap_or(0.0);
            let lag = match (c["our_block"].as_u64().unwrap_or(0), blk) { (o, b) if o > 0 && b > 0 => format!("{}", o.saturating_sub(b)), _ => String::new() };
            println!("     {:>4}  {:5}  {:6}  {:8}  {:10}  {:>7.4}  {:>4}  {:16}  {:>5.2}x  {:>5}s  {:>+9.5}  {:>+6.1}%  {:>7}  {:>8}  {:>8}",
                c["id"].as_u64().unwrap_or(0), if c["paper"].as_bool().unwrap_or(false) { "paper" } else { "REAL" }, wn(leader), hhmm(c["its_ms"].as_u64().unwrap_or(0), off), short(curve),
                c["its_eth"].as_f64().unwrap_or(0.0), lag, c["why"].as_str().unwrap_or("?"), c["peak"].as_f64().unwrap_or(0.0), c["held_s"].as_u64().unwrap_or(0), pnl(c),
                100.0 * pnl(c) / e_in.max(1e-12), eth_usd.map_or(String::new(), |u| format!("{:+.2}", pnl(c) * u)),
                its.as_ref().and_then(|t| t.pct).map_or(String::new(), |x| format!("{x:+.1}%")),
                its.as_ref().map_or(String::new(), |t| match (t.sold_s, t.holding) { (Some(s), _) => format!("{s}s"), (None, true) => "holding".into(), _ => "?".into() }));
        }
        if let Some(e) = its_err { println!("   (its own result incomplete: {e})"); }
        if let Ok(t) = serde_json::to_string(&cache) { let _ = std::fs::write(&its_path, t); }
        // each copied wallet's result, then the total
        println!("   by wallet (REAL):");
        for (i, l) in cfg.leaders.iter().enumerate() {
            let mine: Vec<&Value> = closed.iter().filter(real).filter(|c| c["leader"].as_str().unwrap_or("").eq_ignore_ascii_case(&l.address)).collect();
            let td: Vec<&&Value> = mine.iter().filter(|c| c["closed_ms"].as_u64().unwrap_or(0) / 86_400_000 == day).collect();
            println!("     wallet {} {}: today {} ({:+.5} ETH{}), all {} ({:+.5} ETH{}), {} won", i + 1, short(&l.address),
                td.len(), td.iter().map(|c| pnl(c)).sum::<f64>(), usd(td.iter().map(|c| pnl(c)).sum()),
                mine.len(), mine.iter().map(|c| pnl(c)).sum::<f64>(), usd(mine.iter().map(|c| pnl(c)).sum()), mine.iter().filter(|c| pnl(c) > 0.0).count());
        }
        let all: Vec<&Value> = closed.iter().filter(real).collect(); let pap: Vec<&Value> = closed.iter().filter(|c| !real(c)).collect();
        println!("   all closed: real {} ({:+.5} ETH{}), paper {} ({:+.5} ETH)", all.len(), all.iter().map(|c| pnl(c)).sum::<f64>(), usd(all.iter().map(|c| pnl(c)).sum()),
            pap.len(), pap.iter().map(|c| pnl(c)).sum::<f64>());
    }
    Ok(())
}
