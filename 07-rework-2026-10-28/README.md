# 07. The rework (Oct 28): every decision re-examined, fresh data, the code hardened, and how to go live again

In short: **wallet 4 still makes money** (+82 SOL in the 38 hours to Oct 28 14:54 UTC), it is **one bot with no
siblings and no leader**, and it **changed its rule on Oct 27**: it now sells early on half of its big buys, against
3.5% in the week the strategy was picked on. On that fresh period the long copy as tested **loses** (−2.02 SOL on 25
copies; about flat, −0.51, as the bot really trades), and the paper run's +2.47 SOL **came entirely from 3 coins that
graduated**, a kind of coin no earlier backtest contained. The code review found **8 bugs that would lose money
live**; they are fixed, tested, and the never-run paths are now simulated on mainnet. Part B (its buys paid in PUMP,
CARDS ...) **cannot be routed** through pump's programs at all. The best box is a **€59 a month Cherry Servers virtual
server in Frankfurt** with the Triton gRPC feed the owner already pays for. **The plan: do not go to 1 SOL yet.** Run
the hardened bot on paper for 2-3 days on Frankfurt and Ohio side by side, with the new `follow_its_sell` switch
measuring both exit policies in one run, then the 0.1 SOL mechanics test, then decide on 1 SOL with the numbers below.

| Page here | What it is |
|---|---|
| this README | the findings, the decisions re-examined one by one, and the plan |
| [`code-review.md`](code-review.md) | the live-readiness review of `rugsnipe-long`: 35 findings, ranked, with the fix of each |
| [`wallet-check.md`](wallet-check.md) | wallet 4 on chain: funding, the predecessor wallet, the privacy pool, neighbours, creators, its infrastructure |
| [`infra.md`](infra.md) | where to run it and which feed: prices of Oct 28, latency, Triton, the acceptance tests |
| `../analysis/research/2026-10-28/fresh/` | the 8-day study re-run with Oct 27-28 added (P3) |
| `../analysis/research/2026-10-28/more/` | the trades we skip (parts B, C, D, E) and how to copy part A better |
| `../analysis/research/2026-10-28/wallet/` | the wallet check's scripts and outputs |

Times are UTC unless marked; Beirut = UTC+2 since Oct 25 (UTC+3 before). Every number names its source.

## 1. What the fresh data says (P3 = Oct 27 00:20 → Oct 28 14:54 UTC, `fresh/`)

| | P1 Oct 19-22 (picked on) | P2 Oct 23-27 (scored on) | **P3 Oct 27-28 (new)** |
|---|---|---|---|
| wallet 4's own result | +137 on its 1.45+ other-quote trips | +69 | **+82.00 SOL on 546 coins** (+84.55 on other-quote pump coins); +54.60 of it in one 6-hour block (Oct 28 00-06) |
| its 1.45+ SOL other-quote buys a day | 64-80 | 56-112 | 32 (Oct 27), **11 in the 15 h of Oct 28** |
| its early sales (before 30 min, neither its 2.5x nor its 0.7x) | **3.5%** | 13.6% | **49.0%** (24 of 49; all sold everything; median 142 s at 1.18x) |
| held to its 30-minute timer | 67% | 67% | **39%** |
| the long copy, routable, 1 SOL, TP 2.0 / 0.8 / 1790 s, 4 open | +6.73 (+4.76) | +11.13 (+8.48) | **−2.02 (−3.74), 25 copies** |
| the same, as the bot really trades (1.45 floor, its route verdicts, graduated coins in) | +5.44 (+3.47) | +12.79 (+10.00) | **−0.51 (−2.39), 32 copies** |
| wallet 4 on the same coins | +45 | +59 | +17.69 |

(+x) = without the period's best 2 copies. Sources: `fresh/README.md` §1-3 (`ledger.py`, `early.py`, `grid.py`).

- **Every setting loses on P3:** every band, every stake, every stop, every landing delay, every take profit from
  1.75x up. Only a 1.4-1.5x take profit is positive on P3, and it lost on P1. That is a P3 pick, not a finding.
- **Why:** 11 of the 25 copies end behind its early sale (1 of 145 in P1, 8 of 145 in P2). It sells at a median
  1.18x after about 2 minutes, and its own sale pushes the price down before our sell lands.
- **Paper against the model, coin by coin** (`fresh/README.md` §4): the model reproduces paper's exit on every coin
  but one, and 15 of 21 within 0.03 SOL once its costs match paper's. Paper's 21 closed trades: **+2.47 SOL in paper,
  +1.57 at the backtest's costs** (0.062 SOL a trade more: the 0.0155 fill bias and a 5.1% round trip against
  paper's 2.5%).
- **The gap that matters:** the 3 take profits that made paper's whole profit (6y9aDagF, 9UinFHHj, 3xwpPXRJ:
  +2.47 of +2.47) are coins that **graduated before wallet 4 sold**. `full_paths.py` needs a curve sale, so no
  backtest before Oct 28 contained such a coin. Paper's other 18 coins sum to about zero. In P3 there were 5 such
  1.45+ buys (3 routable), in P1 and P2 together 4.
- **The sample is small.** P3 is 38.6 hours and 25-32 copies; one more coin like 6y9aDagF flips its sign. The
  rule-change finding (early sales 49%, timer 39%) rests on 285 trips, 49 of them at 1.45+ SOL.

## 2. Who wallet 4 is, re-checked on chain (`wallet-check.md`)

- **One bot, one operator, not a fresh trader.** Its first transaction is Oct 17 19:22 UTC: 39.52 SOL from a one-day
  test wallet, then 19.92 SOL from a public privacy pool. The same evening an 82-day bot wallet, `HxcdEi6C`, stopped
  trading, put 60 SOL into the same pool and sent 229 SOL to exchanges. All three wallets use a durable nonce first and
  pay the same two tip sizes (exactly 1,067,000 and 1,010,000 lamports), which none of 665 other sampled wallets use.
  The link is probable, not provable: the pool is there to hide it.
- **No deposits in the 10 days.** The docs' "+11.9 deposited" was rent back from closing token accounts plus pump's
  holder-fee payouts. Its SOL went 57.9 → 569.5 (+511.7): trading +505.8, rent +12.9, payouts +0.8, failed fees −2.9,
  **5.0 SOL out into the privacy pool on Oct 27 13:59 UTC** (its only withdrawal ever).
- **No leader, no sibling, no wash trading.** It buys at the coin's create slot or the next (47 of 47 measured), at a
  median 1.08x the launch price; the buyer before it is a different wallet almost every time. It never created a coin,
  never sent SOL to any of the 4,594 creators of its coins. No wallet near it, among the pool's recipients or in a tip
  sample carries its fingerprint.
- **Its copyable flow is thinning:** 1.45+ SOL other-token buys a day: 64, 78, 80, 77, 73, 56, 112 (Oct 19-25), then
  35, 32, and 11 in the 15 hours of Oct 28. Its predecessor's last days looked like this too.
- **Its infrastructure:** one tip per transaction, Helius 54%, Astralane 17%, Jito 12%, Nozomi 10%; median block
  position about 220 (no top-of-block lane); 2.4% of its transactions fail; it does not use any retail router (the
  `FLASHX8D` note in the Oct 28 README was about other traders: it is Axiom's router).
- **Copiers:** `6anjqMeW` (a fast 0.5 SOL launch buyer) lands in its slot or the next on 27 of 40 sampled coins. Our
  fills come behind such buyers.

## 3. The decisions, re-examined one by one

| Decision (as of Oct 28 morning) | Re-examined | Verdict |
|---|---|---|
| copy its 1.45+ SOL buys of other-quote coins (part A) | still its money: +84.55 of its +82.00 in P3 is other-quote pump coins | **keep**, but see the rule change |
| `min_sol` 1.45 (`band.py`) | every band under 1.45 loses on P3 too (`fresh/` §3); the 1.45-1.5 slice is mixed (P1 −1.54, P2 +0.54, P3 +0.96) | keep |
| 1 SOL stakes | at 2-3 SOL the result grew with the stake on P1/P2; on P3 every stake loses; per SOL staked, **2.0 on WBTC routes / 1.0 on wSOL** earns more (P1 +5.8%, P2 +9.8% against +4.6% / +7.7%) (`more/` D-i) | keep 1 SOL; `float_stake_sol` added for later |
| TP 2.0x / stop 0.8x / 1790 s | still the best on P1 and P2; partial exits, trailing floors, a stop per route: none passes out of sample (`more/` D-iii, D-iv) | keep |
| sell behind its early sale (`its_sell`, `f52cee5`) | **the biggest open question.** Ignoring its sale and keeping our exits: paper's 9 copies +1.97 against −1.36 (following); the bot's set P3 **+3.10 (+1.02) against −0.51**; but P2 −0.25 and P1 −0.04. P3's gain rests on 4 frenzy coins (`more/` D-v) | **`follow_its_sell` switch**, default true; paper with it off records both (§5) |
| `max_open` 4 | the cap never binds in P3 (11-32 copies a day); 4 stays the best on P1/P2 | keep |
| `max_premium` 25% | no limit gains +0.68 on P1 and loses on P2 and P3; tighter loses on P1 (`more/` D-vi) | keep |
| paper fills at seen-slot + 1 | right in principle; Ohio's real lag is still unmeasured (`7184554` not deployed) | measure (§5) |
| paper sells on the firing trade | wrong: a real sell lands a slot later; frenzy take profits looked better than real | **fixed**: a paper sell fills at the end of the next slot |
| paper's costs (0.0032 SOL + 1.25% a side) | lighter than the backtest's by 0.062 SOL a trade; the real fee bps is in the trade event | **fixed**: the event's fee; the fixed-cost question goes to the 0.1 SOL test |
| the floors: 30% under at TP, 50% otherwise, down to 0.1% on retries | at a 0.8x stop a 50% floor accepts −0.61 instead of −0.22; the floor also dropped on send errors | **fixed**: 15% / 30%, drops only after landed failures |
| one buy sender (Nozomi), `rpc_send` | right, but `buy_senders = []` meant every sender; the send path was cold (about 0.5 s from Ohio to Frankfurt) | **fixed**: exactly one sender; blockhash thread, keepalive, RPC copy in parallel |
| Ohio for the live run | geography alone costs 0.27 slot on average (0.5 on European leaders); the repo expected 2-3 slots; unmeasured | **Frankfurt VDS, €59/month** (§6); measure both for a day first |
| part B out (PUMP, CARDS, TTWO ...) | `multi_hop_swap` takes canonical pump pools only (`OnlyPumpPools`, simulated on mainnet), and no part-B quote has one; floats fail out of sample (PUMP: P2 +10.13 beside A against +11.13); a ZEC float is the one marginal case (`more/` A) | **out**, confirmed; ZEC float = config-only paper trial, optional |
| part C out (0.8-1.45 SOL buys) | 0.7x stakes, WBTC routes only: P2 −5.98; every band loses on P3 | out |
| part D (SOL coins), E (PumpSwap-only) | its own result on SOL coins in P3: −3.72; E: +1.31 (−1.30) on 36 | out |
| 3-hop routes (2 skips in the paper journal) | fit in a v0 transaction with pump's lookup table (1,027 bytes); worth about +0.1 SOL a day | not now |
| entry filters | coin age is no filter (all its big buys come within 2 s of the create); hour, progress, frenzy: none passes out of sample | none |

## 4. The code: what was wrong, what changed (`code-review.md`, commit on this branch)

The review read `crates/rugsnipe-long` line by line. The real buy and sell path had never run (paper on Ohio had no
wallet). Eight findings could lose money or leave a coin unmanaged; all are fixed with an engine test each
(`crates/rugsnipe-long/tests/engine_paper.rs`, 15 tests, plus 16 library tests; `cargo test -p rugsnipe-long`):

| # | What was wrong | Fix |
|---|---|---|
| 1 | our own feed stream asked for **failed transactions only** (`failed: Some(true)`): a buy given up as dropped that landed after all was never seen, so the coins sat unmanaged; and a restart zeroed the send time, so a buy in flight was dropped on the first tick | the stream carries both; a restart checks the transaction at once but drops it only by its real age |
| 2 | a coin whose curve completed **while our buy was out** got no exit: the price froze and it was held to the timer on the pool (2RR6sfbi's case) | the fill sends it to the pool at once |
| 3 | the chain check re-read **the first landed sell signature**, usually an old failure, on every pass: a success the feed missed was never booked, the slot was lost for good and fees went on every 10 min | every transaction is booked once (`applied`); the check reads unbooked signatures, successes first |
| 4 | a **missing pool was cached forever**; the 6005 "curve complete" error was never read | a miss is remembered 30 s; after a landed failed sell the curve is read and a complete one goes to the pool |
| 5 | the sell floor **dropped on send errors and drops**, down to 0.1% of the expected output after about 4 s of RPC trouble | the floor drops only after landed failures; send failures wait 1-5 s |
| 6 | `buy_senders = []` meant **every enabled sender**: several buys could land, one tracked | exactly one buy sender in mode on |
| 7 | the floors were wide (a stop at 0.8x accepted −0.61 on 1 SOL instead of −0.22) | 15% at a take profit, 30% otherwise, then 50% and 90% after landed failures |
| 8 | never run on chain: the 2-hop pool sell after graduation into wSOL, a sell that closes the coin account, buyback indexes 1-7 | **simulated on mainnet on Oct 28**, all pass: the buy from wSOL (1,088 bytes, 143-149k units) and from WBTC (1,049 bytes), the closing round trip (1,165 bytes), the graduated 2-hop pool sell into wSOL (1,063 bytes, 104k units) and into WBTC (1,056 bytes); indexes 0-7. A sell now creates the float's account too |

Also: the chain check runs every 2.5 s instead of on every message; the blockhash is refreshed on a thread every 3 s,
the senders' connections kept alive, the RPC copy sent beside the sender's (the cold path from Ohio cost about
0.5 s before Nozomi had the buy); a send no path accepted is an error, retried; its sell while our buy is out takes
us out at the fill; the daily stop counts refused buys and failed-sell fees; the reserve is a setting (`reserve_sol`,
0.05: a 0.1 SOL test wallet needs about 0.16 SOL); the book is pruned once per tick (an index could move under a sell);
a float leg without a price warns instead of silently booking 0; the journal records the send time (`sent ... in N
ms`) and the feed lag (`seen at its slot +N`). Two new commands: `simulate --buyback N --close` and `simulate-sell
--graduated` (docs/20 §4). Paper: a sell fills a slot after the firing trade; the fee is the event's. Two switches:
`follow_its_sell`, `float_stake_sol` (§3).

What can wait (review §3): rebroadcasting a transaction until it lands, chain reads off the engine thread, pricing the
quote's pool hop in paper, a `positions.json.bak`, a `check --config` command, TLS in front of the plain-HTTP senders.

## 5. Where to run it (`infra.md`)

- **A slot is about 211 ms now** (measured Oct 28 on the public RPC; the docs said 0.4 s). Ohio adds about 100 ms on a
  European leader (74% of slots): half on the feed, half on the send. That is about **0.27 slot on average, 0.5 on
  European leaders**, worth 0.5-1.5 SOL a month at the backtest's pace. If Ohio is really 1-2 slots behind, as
  `going-live.md` expected, it is 2-8 SOL a month. Only the journal's `seen at its slot +N` on both boxes settles it.
- **Cherry Servers Frankfurt VDS `G2-4-16gb-100nv-ded`** (EPYC 9354P, 4 vCPU, 16 GB): **€59 a month or €0.101 an
  hour**, 10 in stock on Oct 28, 0.37-0.61 ms from the TeraSwitch building that holds Jito, Helius, Nozomi and Triton.
  Nothing faster matters for this bot (in-building bare metal gains 0.3-0.5 ms, about 0.002 slot). Cherry's terms
  allow trading bots; it sells Solana servers.
- **The feed:** the owner's Triton mainnet-shared subscription includes Yellowstone gRPC: `https://riptide.rpcpool.com`
  with the subscription's token as `x-token` (create one under the mainnet-shared subscription → Tokens). It is
  anycast and answers from Frankfurt there. This bot's stream costs about $0.2-0.5 a month, out of the $75 credit.
  Alchemy's Frankfurt node is the fallback (same building).
- **Senders:** Nozomi `fra2` (the default) for buys and sells, `rpc_send` through Triton. One buy sender only.
- **Ohio:** keep it (it holds the only copy of fra1's backup; never Terminate it), as the paper comparison and for
  analytics. Never run two live bots.

## 6. The plan: how to go live again, in order

**Step 0 (today): the code and the measurement.** Point the Ohio box at this repo and branch (or merge this branch
upstream), install, keep `mode = "log"`, set `follow_its_sell = false` (the journal then records both policies: what
our own exits make, and what selling behind it would have made, `its_sell_net` on each record). Order the Cherry
Frankfurt VDS hourly (about €17 for a week), install with `--role hot`, the Triton gRPC feed, paper there too. Run both
for a day and compare `seen at its slot +N` (infra.md §9, test 2).

**Step 1 (2-3 days): paper that decides.** Read `history.py paper` on both boxes, plus the `closed.jsonl` records'
`its_sell_net` for the following policy. Go on only if **all** hold:
1. the paper book is positive over at least 40 closed copies **without its best 2**, at paper's costs minus 0.062 SOL
   a trade (the backtest's costs: 0.031 fixed and the 5.1% round trip), under at least one of the two exit policies;
2. wallet 4 still makes at least 25 copyable buys a day (1.45+ SOL, other-quote, routable); on Oct 28 it made 11 in
   15 hours;
3. its early-sale rate on those buys is known for the week (if it stays near 50%, the policy that paper prefers is the
   one to run; if it falls back under 15%, following it is the tested rule);
4. Frankfurt sees its buys at least 0.3 slot ahead of Ohio, or lands at +1 in step 2.

**Step 2 (1-2 days): the 0.1 SOL mechanics test, on the Frankfurt box.** A new wallet from `rugsnipe-long keygen`,
funded with **at least 0.16 SOL** (0.1 stake + 0.05 reserve + fees + rent) plus a small WBTC float (about 0.15 SOL
of it, `float buy`), `stake_sol = 0.1`, `max_open = 1`, `mode = "on"`. First run the two simulations in docs/20 §4
step 3 from the box. Pass: buys land mostly at its slot +1 and never past +2; every sell lands, a pool sell after a
graduation included; the chain result equals the journal; expected vs received on each sell within the floor. About
5-10 trades; it costs a few hundredths of a SOL.

**Step 3: 1 SOL, only if steps 1 and 2 pass.** `stake_sol = 1.0`, `max_open = 4`, about 4.5 SOL in the wallet, a
WBTC float of 2 SOL (more, with `float_stake_sol = 2.0`, only once the WBTC routes are back: 4-6 copies in P3),
`daily_stop_sol = 3.0`. The owner's Phantom held 3.85 SOL on Oct 28: 1 SOL × 3 open is what that buys. Watch daily:
the early-sale rate, its buys a day, the realized result without the best 2. Stop at once if wallet 4 goes quiet for
3 hours (no 1.45+ buy) or sends 10+ SOL out: its predecessor was emptied in one evening.

**What would stop the plan:** paper negative without its best 2 under both policies; wallet 4's copyable buys staying
near 10 a day; a real sell that fails to land; a chain result that does not match the journal.

## 7. Honest caveats

- The strategy's profit over Oct 19-27 rests on a few take profits a period, and over Oct 27-28 on 3 graduated frenzy
  coins. "Without its best 2" is the number to read.
- The backtests are kind to frenzy take profits (they sell on the next slot's trade, often 2.1-2.3x where paper's peak
  was 2.0x), and paper's fills are kind too (Ohio's lag was not yet in them).
- Wallet 4's operator rotates wallets through a privacy pool. A successor can probably be found by its fingerprint
  (a durable nonce, tips of exactly 1,067,000 / 1,010,000 lamports, 1.5 SOL other-token buys at create+0/+1), but that
  is not built.
- The Triton token the owner pasted into the chat on Oct 28 should be rotated in the Triton portal once the box is set
  up; it is not in this repo.

## Sources

`code-review.md`, `wallet-check.md`, `infra.md` (this folder); `analysis/research/2026-10-28/fresh/README.md`,
`analysis/research/2026-10-28/more/README.md`, `analysis/research/2026-10-28/wallet/`; the data in
`data/datasets/` (`fresh3`, `more`, `w4wallet`); the commits of Oct 28 on this branch (`03-strategy-A-long-copy/changes.md`).
