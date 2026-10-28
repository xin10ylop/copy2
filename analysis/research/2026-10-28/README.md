# Wallet 4 against the bots, coin by coin (Oct 27-28)

Three checks made on Oct 27-28, all from wallet 4's own transactions on chain, fetched through the public RPC
(`https://api.mainnet-beta.solana.com`, no key; resumable, retried, 2 threads), and the long copy's own detection code:

```
python3 -I fetch/<script>.py OUTDIR            # wallet 4's transactions in the script's window, one JSON file each
cargo run -p rugsnipe-long --example scan -- RPC_URL OUTDIR > scan.out              # the bot's verdict on each buy
SCAN_SOL=1 cargo run -p rugsnipe-long --example scan -- RPC_URL OUTDIR > scan.out   # SOL-priced buys listed too
```
`RPC_URL` is any mainnet RPC (the route planner reads pools). The fetched transactions are in `data/datasets/`
(CLAUDE.md "Datasets").

## `decomp/`: check.sh's window, split into parts A-F

- `fetch/w4fetchwin.py`: Oct 26 13:00 → Oct 27 09:50 UTC (3,000 signatures, 2,538 in the window, 2,495 landed).
- `check_w4.tsv`: the 212 wallet-4 rows of `05-live/check-sh-2026-10-27.txt`, typed out: Beirut time, coin (8 chars),
  its net (`H` = holding), its SOL, the bot's status (`C`/`CR`/`CN`/`CO`/`CNS` copied: filled, refused, not landed,
  open, not sent; `SO` skipped, coin ours; `NS` not seen; `NW` not watched yet), our net.
- `kind_trips.json`: each coin's kind from the 8-day data (`../2026-10-27/h9long/`, up to Oct 27 00:19 UTC): SOL-priced
  or the route class of its buy.
- `scan.out`: the bot's detection on the fetched window (the coins after Oct 27 00:19 UTC).
- `decomp.py scan.out`: the table in `02-decomposition` §3 (the parts add back up to +36.92). Five token rows
  (PUMP, DJTU, DOGE, SPCX, an xStock) are F and 9 graduated coins are E, both listed in the script.

## `verify/`: did the paper long copy enter everything it should have?

- `fetch/w4fetchlive.py`: Oct 27 17:50 UTC → now (1,218 transactions parsed).
- `scan.out`: every buy of 1.45+ SOL or paid in an unpriced token, with the bot's verdict (ROUTABLE, no route, 3 hops,
  unpriced).
- `journal.txt`: the journal's coins by verdict (BUY 21, NOROUTE 5, UNPRICED 67), from the user's journal paste
  (`05-live/long-paper-history-and-journal-2026-10-28.txt`).
- Result: from the Ohio start (Oct 27 16:11 UTC) to Oct 28 13:14 UTC, 94 buys on 93 coins; all 21 qualifying and routable
  entered, all 5 without a route and all 67 unpriced skipped. Nothing missing either way
  (`03-strategy-A-long-copy/paper-run.md` §4). (`w4fetch3.py` fetched Oct 27 16:00 → Oct 28 00:00 for the first pass.)

## `coins/`: single coins checked on chain

- `fetch/fetch_mint.py MINT FROM_UTC TO_UTC OUTDIR`: a coin's transactions between two times.
- `6y9a.path`: 6y9aDagF (paper #3, take profit after 1 s), its curve trade by trade from
  `cargo run -p rugsnipe-long --example curve_path -- DIR MINT WALLET`: 1.2x after 1 s, 2.0x after 2 s.
- ChonQdJ8 (paper #5): wallet 4 sold everything 7 s after buying, losing 10% itself; the copy sold behind it as built.
- `fetch/w4fetch.py`: Oct 27 09:00 → 13:00 UTC, the fra1 paper check (157 transactions, PePEwjLD the only qualifying buy).

A note on the parser: a first hand-written parser here missed most transactions routed through `FLASHX8D...`; every
number above comes from the bot's own `TxLite` parser (`scan.rs`, `curve_path.rs`).
