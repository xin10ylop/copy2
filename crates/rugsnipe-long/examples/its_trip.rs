//! The copied wallet's own trip on one coin, from its transactions on it (RPC `json` encoding, one file each), as
//! `status --chain` computes it. WBTC at PRICE lamports a unit (optional).
//!
//!     cargo run -p rugsnipe-long --example its_trip -- WALLET MINT [PRICE] FILE...
fn main() {
    let a: Vec<String> = std::env::args().skip(1).collect();
    let (w, m) = (&a[0], &a[1]);
    let (price, files) = match a.get(2).and_then(|p| p.parse::<f64>().ok()) {
        Some(p) => (Some(p), &a[3..]),
        None => (None, &a[2..]),
    };
    let txs: Vec<serde_json::Value> = files
        .iter()
        .map(|f| serde_json::from_str(&std::fs::read_to_string(f).unwrap()).unwrap())
        .collect();
    let px = |mint: &str| {
        (mint == "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh")
            .then_some(price)
            .flatten()
    };
    let t = rugsnipe_long::its::trip(&txs, w, m, &px);
    println!("{t:?} pct {:?}", t.pct());
}
