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
