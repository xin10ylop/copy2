# Strategy A: the long copy (wallet 4's big buys of other-token coins, held up to 30 minutes)

In short: when wallet 4 buys **1.45 SOL or more** of a pump coin **priced in another token** that we can route, buy
**1 SOL** right behind it, then sell at **2.0x** its price, **0.8x**, after **1790 s**, or right behind its own sell if
it leaves first. Backtest, picked on Oct 19-22 and scored out of sample on Oct 23-27, at most 4 open: **+6.73 / +11.13
SOL**. It runs **in paper mode on the Ohio box** since Oct 27 16:11 UTC (no wallet, nothing sent). Paper so far: 23
positions, 21 closed, 9 won, **+2.47 SOL** to Oct 28 15:31 Beirut time (+1.57 at the backtest's costs; all of it 3 coins
that graduated). It has entered every buy it should have (checked on chain). It has **never traded real money**.
**Oct 28 evening:** wallet 4 changed its rule on Oct 27 (early sales on half of its big buys) and the copy as tested loses
on Oct 27-28; the code was hardened (8 money-losing fixes); the plan before any real money is in
[`07-rework-2026-10-28/`](../07-rework-2026-10-28/README.md).

| | |
|---|---|
| Status | **paper** (`mode = "log"`) on the Ohio box (AWS us-east-2) since Oct 27 16:11 UTC, still on the Oct 28 morning code; on fra1 before that (Oct 27 morning to 12:45 UTC, 1 trade). Next: this branch's code, a Frankfurt box, 2-3 days of paper, the 0.1 SOL test ([the plan](../07-rework-2026-10-28/README.md#6-the-plan-how-to-go-live-again-in-order)) |
| Built from | wallet 4's rule (01-who-it-is §3) and part A of the decomposition (02-decomposition) |
| Code | `crates/rugsnipe-long/` (process), `crates/pump-codec/src/multihop.rs` (route codec), `deploy/systemd/rugsnipe-long.service` |
| Config | `config/long.example.toml` → `/etc/rugsnipe/long.toml` on the box |
| Source doc | [`docs/20-long-copy.md`](../docs/20-long-copy.md) |
| Research | [`analysis/research/2026-10-27/h9long/`](../analysis/research/2026-10-27/h9long/README.md) |
| Pages here | [backtests](backtests.md) · [paper run](paper-run.md) · [deploy on Ohio](deploy-ohio.md) · [going live](going-live.md) · [changes](changes.md) |

## 1. The rule

**Entry** (its buy, as the bot reads it, `src/detect.rs`):
- wallet 4's **landed** buy of a pump coin whose curve quote is **not SOL**;
- valued at **1.45 SOL or more** (its 1.5 tier; reads 1.45-1.51 by route). The value is the wrapped SOL into its
  `multi_hop_swap`, or the share of what it sent Jupiter that the buy used, or a held token at the oracle price;
- **routable** by pump's own programs: its own route when it starts from wrapped SOL or a float we hold (WBTC), or a
  direct curve buy behind its quote's canonical PumpSwap pool against wSOL or WBTC; at most 2 hops;
- skipped if: its second buy of a coin, a coin already ours, a complete curve, `max_open` reached, the daily stop hit,
  or a `KILL` file in the state dir. Buys paid in a token it can't price, with no route, or with 3 hops are skipped too
  (journal `long skip ...`).

**Our buy:** 1 SOL (`stake_sol`), one transaction, one sender plus the same bytes by `sendTransaction`. It's refused if
the price is more than **25%** above wallet 4's (`max_premium`; `min_out` from its own fill).

**Exits**, on every trade of the coin: the curve price against the price its buy left, *without our own tokens*:

| Exit | Setting | Journal / history name |
|---|---|---|
| take profit | 2.0x (`take_profit`) | `tp` |
| stop | 0.8x (`stop`) | `stop` |
| time | 1790 s after its buy (`max_hold_s`), 10 s before its own 30-minute sale | `time` |
| its own sell first | sell right behind it (added Oct 27, commit `f52cee5`); with `follow_its_sell = false` (Oct 28) our exits stay and the record keeps what selling behind it would have made | `its_sell` |
| the curve completes | sell on the canonical PumpSwap pool | `complete` |

The sell goes back along the route and closes the wSOL and coin accounts, so their rent comes back. If it fails or drops,
it's retried with a lower floor, with a back-off (see the stuck-coin page, `../05-live/stuck-coin-2RR6sfbi.md`).

**Why 2.0x and not its 2.5x:** its own sale is as fast as ours and big enough to move the price. At 2.45x its sale came
first on 83 of 126 take profits; at 2.0x only on 8-10. 2.5x and above backtest the same as no take profit at all.

**Why we don't take its profit:** our buy lifts the price by our own tokens (about 6%, 8.5% at 2x), and our sell takes
exactly that back out. Once we're out, the curve is where it would be without us.

## 2. The settings (as on Ohio, `/etc/rugsnipe/long.toml`)

| Key | Value | Why |
|---|---|---|
| `mode` | `"log"` | paper: decisions priced on the live curve, nothing sent |
| `copy_wallet` | `H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg` | wallet 4 |
| `min_sol` | 1.45 | its 1.5 tier; every band below loses or flips (backtests §4) |
| `stake_sol` | 1.0 | at 0.5 the fixed costs eat the edge (backtests §5) |
| `take_profit` / `stop` / `max_hold_s` | 2.0 / 0.8 / 1790 | backtests §2-3 |
| `max_open` | 4 (set on Ohio Oct 28 00:35 UTC) | best on both periods; nothing past 4 (backtests §6) |
| `max_premium` | 0.25 | its coins keep rising past the first buyers |
| `daily_stop_sol` | 3.0 | no new buys once the UTC day's realized result is at or below −3 |
| `floats` | WBTC `3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh` | routes may start and end in it; WBTC carried Oct 23-27 |
| `buy_senders` / `sell_senders` | `["nozomi"]` | one buy sender: two landing would double the position |
| `buy_tip_lamports` / `sell_tip_lamports` | 1,000,000 (0.001 SOL, Nozomi's minimum) | |
| `buy_cu_price` / `sell_cu_price` / `cu_limit` | 2,000,000 / 1,000,000 µlamports, 300k units | buy 0.0006 + tip = 0.0016 SOL; sell 0.0013 |
| `sell_slack_tp` / `sell_slack_exit` | 0.15 / 0.30 (were 0.30 / 0.50 until Oct 28) | the sell's floor under the expected output; it drops only after sells that landed and failed (2: half, 4: almost any price) |
| `max_sell_fail_sol` | 0.01 | failed-sell fees per position before slowing to every 10 min |
| `paper_land_slots` | 1 | paper fills at the end of the slot after the one our feed saw its buy in (since `7184554`); a paper sell the same way after the trade that fired it (Oct 28) |
| `reserve_sol` | 0.05 | SOL kept beyond the stakes: a wSOL buy needs `stake_sol + reserve_sol` in the wallet (a 0.1 SOL test wallet needs about 0.16) |
| `follow_its_sell` | true (paper next: **false**) | sell behind its early sale, or keep our exits and record what following would have made (07-rework §3) |
| `float_stake_sol` | 0 (= `stake_sol`) | a bigger stake on WBTC-routed copies (+0.12 SOL a copy against +0.02), for later |
| `hot_config` | `/etc/rugsnipe/fra1-hot.toml` on Ohio | the feed and senders come from fra1's saved hot config |

## 3. How the code is laid out (`crates/rugsnipe-long/src/`)

| File | What it does |
|---|---|
| `main.rs` | CLI: `run`, `status [--chain] [--last N]`, `keygen`, `float buy MINT SOL` / `float sell MINT all\|AMOUNT` (through Jupiter), `simulate [--buyback N] [--close]`, `simulate-sell --graduated` (Oct 28: the never-run paths, simulated on mainnet) |
| `feed.rs` | its own Yellowstone gRPC stream (processed commitment): wallet 4's landed transactions, every transaction of ours, every transaction on a coin we hold, slots |
| `txlite.rs`, `detect.rs` | one landed transaction reduced to what the bot reads; wallet 4's trigger buys and its sells |
| `route.rs` | our route for a trigger (`multi_hop_swap`, at most 2 hops), anchored on wrapped SOL or a float we hold |
| `oracle.rs` | float prices in SOL (Jupiter Price API v3, every 20 s), to value its buys and our floats |
| `txb.rs`, `send.rs`, `chain.rs` | build the buy and sell (the codec is byte-equal to wallet 4's own: `crates/pump-codec/tests/multihop_fixtures.rs`), send through the hot config's senders plus `sendTransaction`, read accounts, blockhash and statuses |
| `engine.rs`, `pos.rs` | the loop and the book: triggers, paper fills, exits (`Reason::{Tp, Stop, Time, Complete, ItsSell}` and by hand), retries, journal lines, `positions.json` / `closed.jsonl` |
| `config.rs`, `keys.rs` | `long.toml`; secrets from the systemd credentials (no wallet = paper only) |

Examples: `scan.rs` (the bot's own detection over fetched transactions; `SCAN_SOL=1` lists the SOL-priced buys too),
`curve_path.rs` (a coin's curve trade by trade, the price against the wallet's first buy), `sim_pool_sell.rs` (a
graduated coin's pool sell, simulated on mainnet). Tests: `tests/engine_paper.rs` (9 engine tests: its early sell, the
paper price limit, the paper landing, graduation, retries ...), plus 16 library tests: `cargo test -p rugsnipe-long` (15 engine tests since Oct 28 evening).

**Accounting is chain-true.** A real position's result is the sum of our wallet's lamport changes over its transactions,
plus a float's token change at the oracle price. Paper prices the same decisions on the live curve and charges the fee a
landed transaction would pay.

**Measured on mainnet** (simulated from our wallet, a 2-hop wSOL route): buy 1,088 bytes, 166k compute units; buy and
sell back in one transaction 1,158 bytes. The round trip costs about 3% at 1 SOL (the backtest charged 5.1%).

## 4. Status and what's next

1. **Paper on Ohio**, running on the Oct 28 morning code. Check it with `sudo python3 -I ~/history.py paper` (see
   [deploy-ohio.md](deploy-ohio.md)).
2. **Deploy this branch** (the hardening; `follow_its_sell = false` for the paper test), add a **Frankfurt box**, and
   run 2-3 days of paper that decide; then the **0.1 SOL mechanics test** on Frankfurt; then 1 SOL only if both pass.
   The steps and the pass conditions: [`07-rework-2026-10-28/README.md`](../07-rework-2026-10-28/README.md) §6;
   the box: [`07-rework-2026-10-28/infra.md`](../07-rework-2026-10-28/infra.md) §9; the test: [going-live.md](going-live.md).

## 5. Risks

- **Its rule changed on Oct 27:** early sales on 49% of its 1.45+ SOL other-quote buys (3.5% on Oct 19-22); the copy as
  tested loses on Oct 27-28 (−2.02 on 25 copies), about flat as the bot trades (−0.51 on 32); 11 of 25 copies end behind
  its early sale. Holding to our own exits instead scores +3.10 on that period but about even before it (07-rework §1, §3).
- **Its copyable buys are thinning:** 56-112 a day on Oct 19-25, 35, 32, then 11 in the 15 hours of Oct 28. The operator
  rotates wallets through a privacy pool; 5 SOL went out on Oct 27.
- **The edge is shrinking:** its big buys hit 2.5x 29% of the time on Oct 19, about 10% by Oct 27.
- **A few take profits carry everything.** Every period is thin without its best 2 copies.
- **Oct 23-27 rests on WBTC-routed coins** (+10.0 of +12.2). WBTC-routed copies make about +0.12 SOL a copy in both
  periods, SOL-routed about +0.02.
- **Speed matters most on the quickest winners:** in paper, 4 of 5 take profits fired 1-10 s after its buy, on frenzy
  coins. Real fills from Ohio will land later than paper assumes.
- **It now sells early much more often** (8 of 20 in paper against 3-6% in the data).
- **Real sending has never run end to end.** Since Oct 28 evening every path is simulated on mainnet (the buy from wSOL
  and WBTC, the closing round trip, the pool sell after graduation into both) and the 8 money-losing bugs of the review
  are fixed; the 0.1 SOL test is what proves it.

## Sources

- [`docs/20-long-copy.md`](../docs/20-long-copy.md) §2-4; `config/long.example.toml`; `crates/rugsnipe-long/`.
- [`analysis/research/2026-10-27/h9long/README.md`](../analysis/research/2026-10-27/h9long/README.md).
- [`05-live/long-paper-history-and-journal-2026-10-28.txt`](../05-live/long-paper-history-and-journal-2026-10-28.txt).
- Commits `a7fe78a` (the bot), `ec2463c`, `e9c403a`, `f52cee5`, `0aa4f24`, `2314377`, `7184554` (see [changes.md](changes.md)).
