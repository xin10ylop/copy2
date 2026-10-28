# copy2: wallet 4 (H9kuqGKN): the long copy (A) and the launch copy (D)

Everything about copying **wallet 4**, `H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg`, in one place: who it is, where its
money comes from, what we can and can't trade and why, the two strategies built on it, every backtest, the live and
paper results, the code, and how to run it. Operator 1 ("him", AHwJSnFN) and the other copied wallets are in the
**copy1** repo. Both repos carry the same code snapshot (`xin10ylop/rugsnipe` at `7184554`, Oct 28).

**Agents: read [`CLAUDE.md`](CLAUDE.md) first.**

## Where things stand (Oct 28, evening)

**Re-examined on Oct 28** ([`07-rework-2026-10-28/`](07-rework-2026-10-28/README.md)): wallet 4 still makes money (+82 SOL
in the 38 hours to Oct 28 14:54 UTC) and is one bot with no siblings, but it **changed its rule on Oct 27** (early sales
on 49% of its big buys, against 3.5% in the week the strategy was picked on), and on that fresh period the long copy
**loses** (−2.02 SOL on 25 copies; about flat as the bot really trades). The paper run's +2.47 SOL came from 3 coins
that graduated, a kind no earlier backtest contained. The code review found 8 money-losing bugs in the never-run real
path; **fixed, tested, and simulated on mainnet**. Part B cannot be routed through pump's programs at all. The plan: 2-3
more days of paper with the hardened bot on a €59/month Frankfurt box (running since Oct 28 17:58 UTC; Ohio was
terminated that evening), then the 0.1 SOL test, then decide.


| | Strategy A: the long copy | Strategy D: the launch copy |
|---|---|---|
| What | copy its **1.45+ SOL buys of coins priced in other tokens** that pump's own programs can route; 1 SOL each; sell at 2.0x / 0.8x / 1790 s / behind its own sell | copy its **launch buys of SOL-priced coins**; sell at create + 12 slots (about 5 s); 20% price bound |
| Its share of wallet 4's profit (Oct 19-27) | part A: **+102 of +355 SOL** | a slice of part D: +29 of +355 |
| Backtest (out of sample Oct 23-27) | **+11.13 SOL** at 4 open (Oct 19-22: +6.73) | +0.22 (P2), +1.48 (live replay); slightly negative without the 2 best coins |
| Live | **paper only**. On the Ohio box Oct 27 16:11 UTC to Oct 28 (old code): 21 closed, 9 won, **+2.4666 SOL** to Oct 28 13:31 UTC (+1.57 at the backtest's costs; all of it 3 graduated coins); checked on chain: nothing missed. On the Frankfurt box: paper 17:58-18:34 UTC, then **real money at 0.1 SOL since Oct 28 18:34 UTC** (the mechanics test: wallet `E7KX1hcM...`, 1 open, daily stop 0.3). **First evening: 5 closed, 4 won, +0.3513 SOL on 0.1 SOL stakes**, every trade checked on chain, 4 of 6 buys in its own slot | **real money** Oct 26 17:36 → Oct 27 07:50 UTC: **+0.1456** on 77 filled; **about −0.43** with the stuck coin 2RR6sfbi |
| Status | **live at 0.1 SOL on the Frankfurt box** (`fra-long`, Cherry VDS, this branch's code) since Oct 28 18:34 UTC, after 36 minutes of paper there; Ohio terminated the same evening; next: 5-10 clean real trades, then `max_open = 4` at 0.1 SOL as the deciding sample, then 1 SOL ([the plan](07-rework-2026-10-28/README.md#6-the-plan-how-to-go-live-again-in-order)) | **stopped**: the copy bot is off and its server (fra1) terminated |
| Pages | [`03-strategy-A-long-copy/`](03-strategy-A-long-copy/README.md) | [`04-strategy-D-launch-copy/`](04-strategy-D-launch-copy/README.md) |

**Known problems, read before trusting any number:**
- **The stuck coin 2RR6sfbi** (a D copy): it graduated as we bought, the copy bot failed 405 curve sells, and it cost
  about **0.57 SOL**. Fixed in code, never deployed. → [`05-live/stuck-coin-2RR6sfbi.md`](05-live/stuck-coin-2RR6sfbi.md)
- **check.sh's per-coin "ITS NET" for wallet 4 is wrong coin by coin** (only the total is right), and its "since the
  start" line counts closed trades only (−0.76 while the wallet was −1.41).
- **The Ohio paper run was optimistic:** it filled at the slot it saw the buy and sold on the firing trade; the hardened
  code (on the Frankfurt box) fills and sells a slot later. 4 of 5 of its take profits came within 10 s.
- **Wallet 4 changed:** early sales on 49% of its 1.45+ SOL other-quote buys since Oct 27 (3.5% on Oct 19-22, 13.6% on
  Oct 23-27), confirmed on chain; the copy as tested loses on Oct 27-28 (`07-rework-2026-10-28/`). Its copyable buys fell
  to 11 in the 15 hours of Oct 28. It put 5 SOL into a privacy pool on Oct 27; its predecessor wallet was emptied the
  same way on Oct 17.
- **The paper run's profit is 3 coins** that graduated before wallet 4 sold; the other 18 sum to about zero.
- **The code before Oct 28 evening had 8 bugs that would lose money live** (`07-rework-2026-10-28/code-review.md`):
  fixed on this branch, which is what the Frankfurt box runs.

## A to Z

| Folder | What's in it |
|---|---|
| [`01-who-it-is/`](01-who-it-is/README.md) | wallet 4: how it was found, its +355 SOL, its rule (2.5x / 0.7x / 30 min), bet sizes, coins at once, fees, what's changing |
| [`02-decomposition/`](02-decomposition/README.md) | **where its profit comes from, parts A-F**, over 8 days and in check.sh's window; what we can and can't trade, and why |
| [`03-strategy-A-long-copy/`](03-strategy-A-long-copy/README.md) | the long copy: [rule and code](03-strategy-A-long-copy/README.md), [every backtest](03-strategy-A-long-copy/backtests.md), [the paper run](03-strategy-A-long-copy/paper-run.md), [running it on Ohio](03-strategy-A-long-copy/deploy-ohio.md), [going live](03-strategy-A-long-copy/going-live.md), [changes](03-strategy-A-long-copy/changes.md) |
| [`04-strategy-D-launch-copy/`](04-strategy-D-launch-copy/README.md) | the launch copy: rule, how it was found and tuned, live results, why it made +0.15 while wallet 4 made +2.77 |
| [`04-backtests/`](04-backtests/README.md) | an index of every test, its result, its page and its script |
| [`05-live/`](05-live/README.md) | **check.sh exactly as pasted**, the copy bot's history, the paper history and journal, the stuck coin, the timeline, the money |
| [`06-infrastructure/`](06-infrastructure/README.md) | the boxes (fra1 and Ohio terminated; the Frankfurt box), the code map, deploy files, runbooks, wallets |
| [`07-rework-2026-10-28/`](07-rework-2026-10-28/README.md) | **the Oct 28 rework**: every decision re-examined, the fresh data (P3), the code review and fixes, wallet 4 on chain, where to run it, the plan |
| `docs/` | the project's original docs: 00-08 (background, mechanics, speed, architecture, deploy, runbook), 19 (copy targets; §11 found wallet 4, §13 strategy D), **20 (the long copy)**, `docs/research/` (the early research), `docs/PROJECT-README.md` (the original repo README) |
| `analysis/research/` | the studies: `2026-10-26/h9/` (D), `2026-10-26/wallets2/` (the search), `2026-10-27/h9long/` (A, 8 days), `2026-10-27/refused/` (refused copies), `2026-10-28/` (decomposition of check.sh's window, the paper chain check, single coins; **`fresh/`** the study on Oct 27-28 data, **`more/`** the skipped trades and copying better, **`wallet/`** the wallet check) |
| `data/datasets/` | the fetched data behind the studies, compressed; see CLAUDE.md "Datasets" |
| `crates/`, `deploy/`, `config/` | the code (Rust workspace), install and units, config templates |

## The words used

- **curve**: pump.fun's bonding curve, where a new coin trades until it fills; then it **graduates** to a **PumpSwap**
  pool.
- **priced in SOL / in another token**: the curve's quote token. Wallet 4's best coins are quoted in WBTC, PUMP, CARDS ...
- **launch buy**: a buy in the coin's create slot or the next. **slot**: about 0.2 s (211 ms measured on Oct 28; older pages say 0.4 s). **create + 12**: 12 slots after the
  coin's create.
- **route**: how our buy reaches the coin (`multi_hop_swap` from wrapped SOL or a WBTC float, at most 2 hops).
- **paper** (`mode = "log"`): decisions priced on the live curve, nothing sent. **P1 / P2**: Oct 19-22 / Oct 23-27.
- **(+x)** after a result: the same without each period's best 2 trades. **P3**: Oct 27 00:20 → Oct 28 14:54 UTC.
- **Beirut time** = UTC+2 on these dates (check.sh and history tables); docs use UTC.

## Security

This repo is **public**. It has no private keys, API keys or config files with credentials. Wallet addresses are public
chain data. fra1's backup (keys included) was only on the Ohio box and went with it on Oct 28; none of it is in
git. A pre-commit hook
(`.githooks/pre-commit`, enable with `git config core.hooksPath .githooks`) refuses key material.
