//! Prices of the floats in SOL (Jupiter Price API v3, every 20 s on a
//! thread of its own): lamports per raw unit of a mint. Used to value its
//! buys paid from a held token, to size our stake in a float, and to
//! report the floats' value. A price older than [`STALE_MS`] is not used.

use pump_codec::constants as c;
use pump_codec::Pubkey;
use rugsnipe_tx::rpc::HttpGet;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::Duration;

pub const API: &str = "https://lite-api.jup.ag/price/v3";
pub const STALE_MS: u64 = 120_000;

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
                        at_ms: now_ms(),
                    },
                );
                n += 1;
            }
        }
        n
    }

    /// Refresh `mints` every `every` on a thread of its own.
    pub fn spawn(&self, api: &str, mints: Vec<Pubkey>, every: Duration) {
        let api = api.to_string();
        let me = self.clone();
        std::thread::Builder::new()
            .name("long-oracle".into())
            .spawn(move || {
                let http = HttpGet::new(Duration::from_secs(10), 1 << 20);
                let mut ids: Vec<String> = mints.iter().map(|m| m.to_string()).collect();
                ids.push(c::WSOL_MINT.to_string());
                let url = format!("{api}?ids={}", ids.join(","));
                loop {
                    match http.get(&url) {
                        Ok((200, body)) => {
                            if let Ok(v) = serde_json::from_str::<serde_json::Value>(&body) {
                                me.apply(&v);
                            }
                        }
                        Ok((s, _)) => {
                            eprintln!("long oracle: HTTP {s} (retry in {} s)", every.as_secs())
                        }
                        Err(e) => eprintln!("long oracle: {e}"),
                    }
                    std::thread::sleep(every);
                }
            })
            .expect("spawn the oracle thread");
    }
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
}
