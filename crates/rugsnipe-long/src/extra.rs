//! SOL from outside the copy that belongs in the result: coins airdropped to
//! the wallet and sold (`float sell` of a mint that is not a float, or
//! `float book SIG` for a sale already made). One JSON line per sale in
//! `<state_dir>/extra.jsonl`; `status` adds them to the totals (2026-11-12:
//! two airdropped coins sold for +0.26 SOL).

use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::path::Path;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Extra {
    /// The transaction's block time (unix ms).
    pub ms: u64,
    pub sig: String,
    pub mint: String,
    /// Our SOL change in that transaction, fee included (lamports, signed).
    pub lamports: i64,
}

/// Our SOL change in a `getTransaction` result (`encoding = "json"`):
/// post minus pre balance of `me`, looked up in the static keys and the
/// loaded addresses (writable, then read-only).
pub fn sol_delta(tx: &Value, me: &str) -> Option<i64> {
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
    let i = keys.iter().position(|k| *k == me)?;
    let pre = tx["meta"]["preBalances"].get(i)?.as_i64()?;
    let post = tx["meta"]["postBalances"].get(i)?.as_i64()?;
    Some(post - pre)
}

/// The floats that came to `me` in a transaction, valued in lamports: holder
/// fees are paid in the coin's quote token, so for a coin priced in a float
/// they land in the float itself (2026-11-14: 1,028 PUMP while we held
/// DHcZRxRX). `(lamports, the float's mint)`; `None` when no float moved or
/// one has no price.
pub fn float_value(
    tx: &Value,
    me: &str,
    floats: &[String],
    lamports_per_unit: &dyn Fn(&str) -> Option<f64>,
) -> Option<(i64, String)> {
    let mut out: Option<(i64, String)> = None;
    for (m, a) in crate::its::token_deltas(tx, me) {
        if !floats.contains(&m) {
            continue;
        }
        let v = (a as f64 * lamports_per_unit(&m)?) as i64;
        out = Some((out.as_ref().map_or(0, |o| o.0) + v, m));
    }
    out
}

/// Book one sale (once per signature).
pub fn append(dir: &Path, e: &Extra) -> Result<bool, String> {
    if load(dir).iter().any(|x| x.sig == e.sig) {
        return Ok(false);
    }
    use std::io::Write;
    let mut f = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(dir.join("extra.jsonl"))
        .map_err(|e| e.to_string())?;
    writeln!(
        f,
        "{}",
        serde_json::to_string(e).map_err(|e| e.to_string())?
    )
    .map_err(|e| e.to_string())?;
    Ok(true)
}

/// Every booked sale, each signature once.
pub fn load(dir: &Path) -> Vec<Extra> {
    let text = std::fs::read_to_string(dir.join("extra.jsonl")).unwrap_or_default();
    let mut out: Vec<Extra> = vec![];
    for e in text
        .lines()
        .filter_map(|l| serde_json::from_str::<Extra>(l).ok())
    {
        if !out.iter().any(|x| x.sig == e.sig) {
            out.push(e);
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn our_sol_change_from_static_or_loaded_keys() {
        let tx = json!({
            "transaction": {"message": {"accountKeys": ["A", "B"]}},
            "meta": {"preBalances": [10, 20, 30], "postBalances": [9, 20, 130],
                     "loadedAddresses": {"writable": ["ME"], "readonly": []}}
        });
        assert_eq!(sol_delta(&tx, "ME"), Some(100));
        assert_eq!(sol_delta(&tx, "A"), Some(-1));
        assert_eq!(sol_delta(&tx, "Z"), None);
    }

    #[test]
    fn holder_fees_paid_into_a_float_are_valued() {
        // 1,028.10523 PUMP to us, nothing in SOL (2FSqwb8j, 2026-11-14)
        let tx = json!({
            "transaction": {"message": {"accountKeys": ["X", "ME"]}},
            "meta": {"preBalances": [10, 20], "postBalances": [9, 20],
                     "preTokenBalances": [{"owner": "ME", "mint": "PUMP", "uiTokenAmount": {"amount": "0"}}],
                     "postTokenBalances": [{"owner": "ME", "mint": "PUMP", "uiTokenAmount": {"amount": "1028105230"}},
                                           {"owner": "ME", "mint": "COIN", "uiTokenAmount": {"amount": "5"}}]}
        });
        let fl = vec!["PUMP".to_string()];
        let p = |m: &str| (m == "PUMP").then_some(0.0442);
        assert_eq!(float_value(&tx, "ME", &fl, &p), Some((45_442_251, "PUMP".into())));
        assert_eq!(float_value(&tx, "ME", &fl, &|_| None), None);
        assert_eq!(float_value(&tx, "ME", &["WBTC".to_string()], &p), None);
        assert_eq!(sol_delta(&tx, "ME"), Some(0));
    }

    #[test]
    fn a_sale_is_booked_once() {
        let dir = std::env::temp_dir().join(format!("extra-test-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let _ = std::fs::remove_file(dir.join("extra.jsonl"));
        let e = Extra {
            ms: 1,
            sig: "S".into(),
            mint: "M".into(),
            lamports: 196_772_825,
        };
        assert!(append(&dir, &e).unwrap());
        assert!(!append(&dir, &e).unwrap());
        assert_eq!(load(&dir), vec![e]);
        std::fs::remove_dir_all(&dir).unwrap();
    }
}
