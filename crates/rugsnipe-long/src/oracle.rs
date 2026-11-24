//! Prices of the floats in SOL (Jupiter Price API v3, every 20 s on a
//! thread of its own): lamports per raw unit of a mint. Used to value its
//! buys paid from a held token, to size our stake in a float, and to
//! report the floats' value. A price older than [`STALE_MS`] is not used.
//!
//! The units on one wallet share one fetch (Nov 24: seven units asking every
//! 20 s from one address drew HTTP 429 on most requests, and its float-paid
//! buys went unvalued and skipped): each writes its answer to [`SHARED_FILE`]
//! in its state dir, and a unit that finds another's under 20 s old uses it
//! instead of asking.

use pump_codec::constants as c;
use pump_codec::Pubkey;
use rugsnipe_tx::rpc::HttpGet;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};
use std::time::Duration;

pub const API: &str = "https://lite-api.jup.ag/price/v3";
/// Nov 24: 10 minutes (was 2): a float moves a few % at most in that time, and a
/// refused fetch or two no longer leaves its float-paid buys unvalued.
pub const STALE_MS: u64 = 600_000;
/// A unit's last answer from the price API, in its state dir.
pub const SHARED_FILE: &str = "prices.json";

#[derive(Debug, Clone, Copy, PartialEq)]
struct Px {
    /// Lamports per raw unit.
    lamports: f64,
    at_ms: u64,
}

/// Shared prices.
#[derive(Debug, Clone, Default)]
pub struct Oracle {
    inner: Arc<Mutex<HashMap<Pubkey, Px>>>,
}

pub fn now_ms() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(0)
}

/// `float level`: the swap that brings a float holding `held` raw units, at
/// `lamports_per_unit`, to `target_sol`: `Some((true, lamports))` to buy
/// with, `Some((false, units))` to sell, `None` when it is within 5% of the
/// target (or 0.02 SOL).
pub fn level(held: u64, lamports_per_unit: f64, target_sol: f64) -> Option<(bool, u64)> {
    let have = held as f64 * lamports_per_unit / 1e9;
    let diff = target_sol - have;
    if diff.abs() < (0.05 * target_sol).max(0.02) || lamports_per_unit <= 0.0 {
        return None;
    }
    Some(if diff > 0.0 {
        (true, (diff * 1e9) as u64)
    } else {
        (false, ((-diff * 1e9 / lamports_per_unit) as u64).min(held))
    })
}

impl Oracle {
    /// Lamports per raw unit of `mint` (wrapped SOL: 1).
    pub fn lamports_per_unit(&self, mint: &Pubkey) -> Option<f64> {
        if *mint == c::WSOL_MINT {
            return Some(1.0);
        }
        let g = self.inner.lock().ok()?;
        let p = g.get(mint)?;
        (now_ms().saturating_sub(p.at_ms) < STALE_MS).then_some(p.lamports)
    }

    /// The last price known, however old (accounting: a result is better
    /// valued at an old rate than at none).
    pub fn last_known(&self, mint: &Pubkey) -> Option<f64> {
        if *mint == c::WSOL_MINT {
            return Some(1.0);
        }
        self.inner.lock().ok()?.get(mint).map(|p| p.lamports)
    }

    /// Set a price (tests, or a fill's own rate).
    pub fn set(&self, mint: Pubkey, lamports_per_unit: f64) {
        if let Ok(mut g) = self.inner.lock() {
            g.insert(
                mint,
                Px {
                    lamports: lamports_per_unit,
                    at_ms: now_ms(),
                },
            );
        }
    }

    /// One refresh from the API body (`{mint: {usdPrice, decimals}}`).
    pub fn apply(&self, body: &serde_json::Value) -> usize {
        self.apply_at(body, now_ms())
    }

    /// [`Oracle::apply`] for an answer fetched at `at_ms` (another unit's).
    pub fn apply_at(&self, body: &serde_json::Value, at_ms: u64) -> usize {
        let sol = body[c::WSOL_MINT.to_string()]["usdPrice"]
            .as_f64()
            .filter(|p| *p > 0.0);
        let Some(sol) = sol else { return 0 };
        let mut n = 0;
        if let (Some(obj), Ok(mut g)) = (body.as_object(), self.inner.lock()) {
            for (k, v) in obj {
                let (Ok(m), Some(usd), Some(dec)) = (
                    k.parse::<Pubkey>(),
                    v["usdPrice"].as_f64(),
                    v["decimals"].as_u64(),
                ) else {
                    continue;
                };
                if m == c::WSOL_MINT || usd <= 0.0 {
                    continue;
                }
                let lamports = usd / 10f64.powi(dec as i32) / sol * 1e9;
                g.insert(
                    m,
                    Px {
                        lamports,
                        at_ms,
                    },
                );
                n += 1;
            }
        }
        n
    }

    /// Refresh `mints` every `every` on a thread of its own: from another
    /// unit's answer (`others`, [`SHARED_FILE`] paths) when one is fresher
    /// than `every` and asked for every mint we need, else from the API,
    /// writing the answer to `own` for the others.
    pub fn spawn(
        &self,
        api: &str,
        mints: Vec<Pubkey>,
        every: Duration,
        own: Option<PathBuf>,
        others: Vec<PathBuf>,
    ) {
        let api = api.to_string();
        let me = self.clone();
        std::thread::Builder::new()
            .name("long-oracle".into())
            .spawn(move || {
                let http = HttpGet::new(Duration::from_secs(10), 1 << 20);
                let mut ids: Vec<String> = mints.iter().map(|m| m.to_string()).collect();
                ids.push(c::WSOL_MINT.to_string());
                let url = format!("{api}?ids={}", ids.join(","));
                let every_ms = every.as_millis().max(1) as u64;
                // the units restart together: each asks at a phase of its own
                if let Some(p) = &own {
                    std::thread::sleep(Duration::from_millis(phase_ms(p, every_ms)));
                }
                let (mut last_log, mut refused) = (0u64, 0u32);
                loop {
                    let now = now_ms();
                    if let Some((at, body)) = fresh_shared(&others, &ids, now, every_ms) {
                        me.apply_at(&body, at);
                    } else {
                        let failed = match http.get(&url) {
                            Ok((200, body)) => match serde_json::from_str::<serde_json::Value>(&body) {
                                Ok(v) => {
                                    if me.apply(&v) > 0 {
                                        if let Some(p) = &own {
                                            if let Err(e) = write_shared(p, &ids, now_ms(), &v) {
                                                eprintln!("long oracle: writing {}: {e}", p.display());
                                            }
                                        }
                                    }
                                    None
                                }
                                Err(e) => Some(format!("bad answer: {e}")),
                            },
                            Ok((s, _)) => Some(format!("HTTP {s}")),
                            Err(e) => Some(e.to_string()),
                        };
                        // one line a minute at most, with the count
                        if let Some(why) = failed {
                            refused += 1;
                            if now.saturating_sub(last_log) >= 60_000 {
                                eprintln!(
                                    "long oracle: {why} ({refused} failed since the last line; retry in {} s)",
                                    every.as_secs()
                                );
                                (last_log, refused) = (now, 0);
                            }
                        }
                    }
                    std::thread::sleep(every);
                }
            })
            .expect("spawn the oracle thread");
    }
}

/// A unit's wait before its first ask, from its file's path: spread over `every_ms`.
fn phase_ms(own: &Path, every_ms: u64) -> u64 {
    let h = own
        .to_string_lossy()
        .bytes()
        .fold(0xcbf2_9ce4_8422_2325u64, |h, b| (h ^ b as u64).wrapping_mul(0x100_0000_01b3));
    h % every_ms
}

/// The freshest of `paths` fetched under `max_age_ms` before `now` that
/// asked for every one of `ids`: `(fetched_at_ms, body)`.
pub fn fresh_shared(
    paths: &[PathBuf],
    ids: &[String],
    now: u64,
    max_age_ms: u64,
) -> Option<(u64, serde_json::Value)> {
    paths
        .iter()
        .filter_map(|p| {
            let mut v: serde_json::Value = serde_json::from_str(&std::fs::read_to_string(p).ok()?).ok()?;
            let at = v["at_ms"].as_u64()?;
            let asked: Vec<&str> = v["ids"].as_array()?.iter().filter_map(|x| x.as_str()).collect();
            (now.saturating_sub(at) < max_age_ms && ids.iter().all(|i| asked.contains(&i.as_str())))
                .then(|| (at, v["body"].take()))
        })
        .max_by_key(|(at, _)| *at)
}

/// Write an answer for the other units (a whole file or none: a rename).
pub fn write_shared(
    path: &Path,
    ids: &[String],
    at_ms: u64,
    body: &serde_json::Value,
) -> std::io::Result<()> {
    let tmp = path.with_extension("json.tmp");
    std::fs::write(&tmp, serde_json::json!({ "at_ms": at_ms, "ids": ids, "body": body }).to_string())?;
    std::fs::rename(&tmp, path)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_float_is_levelled_to_its_target() {
        // PUMP at 0.0429 lamports a raw unit: 11.655e9 units = 0.5 SOL
        let p = 0.0429;
        assert_eq!(level(0, p, 0.5), Some((true, 500_000_000)));
        // 0.3 SOL held: buy the missing 0.2
        let (buy, a) = level(6_993_006_993, p, 0.5).unwrap();
        assert!(buy && (a as i64 - 200_000_000).abs() < 10);
        // 0.8 SOL held: sell 0.3 SOL of it, in raw units
        let (buy, a) = level(18_648_018_648, p, 0.5).unwrap();
        assert!(!buy && (a as f64 * p / 1e9 - 0.3).abs() < 1e-6);
        // within 5% (or 0.02 SOL): left alone; target 0 sells all of it
        assert_eq!(level(11_900_000_000, p, 0.5), None);
        assert_eq!(level(11_655_011_655, p, 0.0), Some((false, 11_655_011_655)));
        assert_eq!(level(1000, 0.0, 0.5), None);
    }

    #[test]
    fn prices_in_lamports_per_raw_unit() {
        let o = Oracle::default();
        let wbtc: Pubkey = "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh"
            .parse()
            .unwrap();
        let body = serde_json::json!({
            "So11111111111111111111111111111111111111112": {"usdPrice": 200.0, "decimals": 9},
            "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh": {"usdPrice": 100000.0, "decimals": 8}
        });
        assert_eq!(o.apply(&body), 1);
        // 1 WBTC = 500 SOL: one sat (1e-8) = 5e-6 SOL = 5000 lamports
        let p = o.lamports_per_unit(&wbtc).unwrap();
        assert!((p - 5000.0).abs() < 1e-6, "{p}");
        assert_eq!(o.lamports_per_unit(&c::WSOL_MINT), Some(1.0));
        assert_eq!(o.lamports_per_unit(&Pubkey::new_from_array([1; 32])), None);
    }

    #[test]
    fn a_fresh_answer_of_another_unit_is_used_and_a_stale_or_narrow_one_is_not() {
        let dir = std::env::temp_dir().join(format!("oracle-share-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let (a, b) = (dir.join("a.json"), dir.join("b.json"));
        let wbtc = "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh".to_string();
        let sol = c::WSOL_MINT.to_string();
        let ids = vec![wbtc.clone(), sol.clone()];
        let body = serde_json::json!({
            sol.clone(): {"usdPrice": 200.0, "decimals": 9},
            wbtc.clone(): {"usdPrice": 100000.0, "decimals": 8}
        });
        // a: 30 s old; b: 5 s old (the freshest under 20 s is taken)
        write_shared(&a, &ids, 1_000_000, &body).unwrap();
        write_shared(&b, &ids, 1_025_000, &body).unwrap();
        let paths = vec![a.clone(), b.clone(), dir.join("missing.json")];
        let (at, got) = fresh_shared(&paths, &ids, 1_030_000, 20_000).unwrap();
        assert_eq!(at, 1_025_000);
        // its price carries the other unit's fetch time
        let o = Oracle::default();
        assert_eq!(o.apply_at(&got, at), 1);
        assert_eq!(o.inner.lock().unwrap()[&wbtc.parse::<Pubkey>().unwrap()].at_ms, 1_025_000);
        // all too old: none
        assert!(fresh_shared(&paths, &ids, 1_046_000, 20_000).is_none());
        // a unit that asked for fewer mints than we need: not used
        let more = vec![wbtc, sol, "he1iusmfkpAdwvxLNGV8Y1iSbj4rUy6yMhEA3fotn9A".to_string()];
        assert!(fresh_shared(&paths, &more, 1_030_000, 20_000).is_none());
        // the units' phases are spread, and stable
        let p1 = phase_ms(Path::new("/var/lib/rugsnipe-long/prices.json"), 20_000);
        assert!(p1 < 20_000);
        assert_eq!(p1, phase_ms(Path::new("/var/lib/rugsnipe-long/prices.json"), 20_000));
        let _ = std::fs::remove_dir_all(&dir);
    }
}
