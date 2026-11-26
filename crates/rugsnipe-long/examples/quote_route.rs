//! Which quote tokens the long copy can reach (Nov 26): a coin priced in token Q is bought over the curve from Q, so a
//! route needs Q to be an anchor (wrapped SOL or a float) or a canonical PumpSwap pool between Q and an anchor (the
//! "pool+curve" plan of `route::plan`). Reads quote mints, one a line, from FILE; prints `MINT anchor|pool ANCHOR|none`.
//!
//!     FLOATS=MINT,... cargo run -p rugsnipe-long --example quote_route -- RPC_URL FILE
use pump_codec::constants as c;
use pump_codec::{pda, Pubkey};
use rugsnipe_long::chain::Rpc;
use rugsnipe_long::route::Chain;

fn main() {
    let a: Vec<String> = std::env::args().skip(1).collect();
    let mut rpc = Rpc::new(&a[0]);
    let mut anchors: Vec<Pubkey> = vec![c::WSOL_MINT];
    if let Ok(f) = std::env::var("FLOATS") {
        anchors.extend(f.split(',').filter_map(|m| m.parse::<Pubkey>().ok()));
    }
    // PACE_MS between tokens (Nov 26): a refused lookup reads as "no pool", and 2,400 fast lookups drew refusals (FIONA
    // read "none" with its canonical pool to wSOL live)
    let pace = std::env::var("PACE_MS").ok().and_then(|v| v.parse().ok()).unwrap_or(0u64);
    for l in std::fs::read_to_string(&a[1]).unwrap().lines() {
        let Ok(q) = l.trim().parse::<Pubkey>() else { continue };
        std::thread::sleep(std::time::Duration::from_millis(pace));
        // PDAS_ONLY=1: print "MINT ANCHOR POOL" lines and check nothing (a batch check with retries elsewhere)
        if std::env::var_os("PDAS_ONLY").is_some() {
            for x in &anchors {
                println!("{q} {x} {}", pda::canonical_pump_swap_pool(&q, x));
            }
            continue;
        }
        if std::env::var_os("SHOW_POOLS").is_some() {
            for x in &anchors {
                let pool = pda::canonical_pump_swap_pool(&q, x);
                println!("  {} canonical pool with {}: {pool} exists {}", &q.to_string()[..8], &x.to_string()[..8], rpc.pool_exists(&pool));
            }
        }
        let how = if anchors.contains(&q) {
            "anchor".to_string()
        } else {
            anchors
                .iter()
                .find(|x| rpc.pool_exists(&pda::canonical_pump_swap_pool(&q, x)))
                .map(|x| format!("pool {}", &x.to_string()[..8]))
                .unwrap_or_else(|| "none".into())
        };
        println!("{q} {how}");
    }
}
