//! The copied wallet's own result on a coin we copied, for `status`: its
//! SOL out on the buys and back on the sales, from its transactions on the
//! coin (its token account's history), so each of our trades can be read next
//! to its own (2026-11-12: "how do we compare to him on the same coins").
//! A token it paid with or was paid in other than SOL (WBTC) is valued at the
//! price `status` reads from the price API.

use serde::{Deserialize, Serialize};
use serde_json::Value;

const WSOL: &str = "So11111111111111111111111111111111111111112";

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct ItsTrip {
    /// Lamports out on its buys and back on its sales (fees and tips in).
    pub spent: i64,
    pub back: i64,
    /// It still holds some of the coin.
    pub holding: bool,
    /// Seconds from its first buy to its first sale.
    pub sold_after_s: Option<u64>,
    /// A token in one of its trades had no price: the result is incomplete.
    pub unpriced: bool,
}

impl ItsTrip {
    /// Its result in % of what it spent.
    pub fn pct(&self) -> Option<f64> {
        (self.spent > 0).then(|| (self.back - self.spent) as f64 / self.spent as f64 * 100.0)
    }
}

/// `wallet`'s token changes in a `getTransaction` result (`json` encoding):
/// mint -> raw amount (post minus pre).
pub fn token_deltas(tx: &Value, wallet: &str) -> Vec<(String, i128)> {
    let mut out: Vec<(String, i128)> = vec![];
    for (k, sign) in [("preTokenBalances", -1i128), ("postTokenBalances", 1)] {
        for b in tx["meta"][k].as_array().into_iter().flatten() {
            if b["owner"].as_str() != Some(wallet) {
                continue;
            }
            let (Some(m), Some(a)) = (
                b["mint"].as_str(),
                b["uiTokenAmount"]["amount"]
                    .as_str()
                    .and_then(|a| a.parse::<i128>().ok()),
            ) else {
                continue;
            };
            match out.iter_mut().find(|(x, _)| x == m) {
                Some(e) => e.1 += sign * a,
                None => out.push((m.to_string(), sign * a)),
            }
        }
    }
    out.retain(|(_, d)| *d != 0);
    out
}

/// The token account `wallet` holds `mint` in, from a transaction that moved
/// it (its buy). Wallet 4 does not use the associated token account: its
/// account for 5tePJcGm was 4AVcSZET..., the ATA would be W4FA3jsJ... .
pub fn token_account(tx: &Value, wallet: &str, mint: &str) -> Option<String> {
    let mut keys: Vec<&str> = tx["transaction"]["message"]["accountKeys"]
        .as_array()?
        .iter()
        .filter_map(Value::as_str)
        .collect();
    for k in ["writable", "readonly"] {
        if let Some(a) = tx["meta"]["loadedAddresses"][k].as_array() {
            keys.extend(a.iter().filter_map(Value::as_str));
        }
    }
    ["postTokenBalances", "preTokenBalances"]
        .iter()
        .find_map(|k| {
            tx["meta"][*k].as_array()?.iter().find_map(|b| {
                (b["owner"].as_str() == Some(wallet) && b["mint"].as_str() == Some(mint))
                    .then(|| b["accountIndex"].as_u64())
                    .flatten()
                    .and_then(|i| keys.get(i as usize).map(|k| k.to_string()))
            })
        })
}

/// Its trip on `mint` from its transactions on the coin (any order; failed
/// ones are skipped). `lamports_per_unit` prices any other token it moved.
pub fn trip(
    txs: &[Value],
    wallet: &str,
    mint: &str,
    lamports_per_unit: &dyn Fn(&str) -> Option<f64>,
) -> ItsTrip {
    let mut v: Vec<&Value> = txs.iter().filter(|t| t["meta"]["err"].is_null()).collect();
    v.sort_by_key(|t| (t["slot"].as_u64(), t["blockTime"].as_u64()));
    let mut r = ItsTrip::default();
    let (mut held, mut first_buy) = (0i128, None::<u64>);
    for t in v {
        let d = token_deltas(t, wallet);
        let Some(coin) = d.iter().find(|(m, _)| m == mint).map(|x| x.1) else {
            continue;
        };
        let mut value = crate::extra::sol_delta(t, wallet).unwrap_or(0) as f64;
        for (m, a) in &d {
            if m == mint {
                continue;
            }
            if m == WSOL {
                value += *a as f64;
            } else {
                match lamports_per_unit(m) {
                    Some(p) => value += *a as f64 * p,
                    None => r.unpriced = true,
                }
            }
        }
        let bt = t["blockTime"].as_u64();
        held += coin;
        if coin > 0 {
            r.spent += -value as i64;
            first_buy = first_buy.or(bt);
        } else {
            r.back += value as i64;
            if r.sold_after_s.is_none() {
                r.sold_after_s = first_buy.zip(bt).map(|(b, s)| s.saturating_sub(b));
            }
        }
    }
    r.holding = held > 0;
    r
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn tx(slot: u64, bt: u64, sol: (i64, i64), toks: &[(&str, &str, &str)]) -> Value {
        // toks: (mint, pre, post) for "W"
        json!({
            "slot": slot, "blockTime": bt,
            "transaction": {"message": {"accountKeys": ["W"]}},
            "meta": {"err": null, "preBalances": [sol.0], "postBalances": [sol.1],
                     "preTokenBalances": toks.iter().map(|(m, a, _)| json!({"owner": "W", "mint": m, "uiTokenAmount": {"amount": a}})).collect::<Vec<_>>(),
                     "postTokenBalances": toks.iter().map(|(m, _, b)| json!({"owner": "W", "mint": m, "uiTokenAmount": {"amount": b}})).collect::<Vec<_>>()}
        })
    }

    #[test]
    fn its_token_account_comes_from_its_buy() {
        let t = json!({
            "transaction": {"message": {"accountKeys": ["W", "X"]}},
            "meta": {"loadedAddresses": {"writable": ["ACCT"], "readonly": []},
                     "preTokenBalances": [],
                     "postTokenBalances": [{"accountIndex": 1, "owner": "Y", "mint": "C"},
                                           {"accountIndex": 2, "owner": "W", "mint": "C"}]}
        });
        assert_eq!(token_account(&t, "W", "C").as_deref(), Some("ACCT"));
        assert_eq!(token_account(&t, "W", "D"), None);
    }

    #[test]
    fn its_buy_and_sale_in_sol_and_wbtc() {
        let none = |_: &str| None;
        // bought for 2.3371 SOL, sold for 4.9846 SOL 224 s later (5tePJcGm, 2026-11-12)
        let t = [
            tx(
                2,
                1224,
                (10_000_000_000, 14_984_600_000),
                &[("C", "500", "0")],
            ),
            tx(
                1,
                1000,
                (12_337_100_000, 10_000_000_000),
                &[("C", "0", "500")],
            ),
        ];
        let r = trip(&t, "W", "C", &none);
        assert_eq!(
            (r.spent, r.back, r.holding, r.sold_after_s),
            (2_337_100_000, 4_984_600_000, false, Some(224))
        );
        assert!((r.pct().unwrap() - 113.28).abs() < 0.01);
        // a sale paid in WBTC: valued at its price; an unpriced token is flagged
        let w = |m: &str| (m == "WBTC").then_some(8442.0);
        let t2 = [
            tx(1, 10, (2_000_000_000, 500_000_000), &[("C", "0", "7")]),
            tx(
                2,
                70,
                (500_000_000, 499_990_000),
                &[("C", "7", "0"), ("WBTC", "0", "200000")],
            ),
        ];
        let r2 = trip(&t2, "W", "C", &w);
        assert_eq!(
            (r2.spent, r2.back, r2.sold_after_s, r2.unpriced),
            (1_500_000_000, 1_688_390_000, Some(60), false)
        );
        assert!(trip(&t2, "W", "C", &none).unpriced);
        // still holding part of it
        assert!(trip(&t2[..1], "W", "C", &w).holding);
    }
}
