# copy2: wallet 4 (H9kuqGKN): the long copy (A) and the launch copy (D)

Everything about copying **wallet 4**, `H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg`, in one place: who it is, where its
money comes from, what we can and can't trade and why, the two strategies built on it, every backtest, the live and
paper results, the code, and how to run it. Operator 1 ("him", AHwJSnFN) and the other copied wallets are in the
**copy1** repo. Both repos carry the same code snapshot (`xin10ylop/rugsnipe` at `7184554`, Oct 28).

**Agents: read [`CLAUDE.md`](CLAUDE.md) first.**

## Where things stand (Oct 28)

| | Strategy A: the long copy | Strategy D: the launch copy |
|---|---|---|
| What | copy its **1.45+ SOL buys of coins priced in other tokens** that pump's own programs can route; 1 SOL each; sell at 2.0x / 0.8x / 1790 s / behind its own sell | copy its **launch buys of SOL-priced coins**; sell at create + 12 slots (about 5 s); 20% price bound |
| Its share of wallet 4's profit (Oct 19-27) | part A: **+102 of +355 SOL** | a slice of part D: +29 of +355 |
| Backtest (out of sample Oct 23-27) | **+11.13 SOL** at 4 open (Oct 19-22: +6.73) | +0.22 (P2), +1.48 (live replay); slightly negative without the 2 best coins |
| Live | **paper only**, on the Ohio box since Oct 27 16:11 UTC: 20 closed, 9 won, **+2.6541 SOL**; checked on chain: nothing missed | **real money** Oct 26 17:36 → Oct 27 07:50 UTC: **+0.1456** on 77 filled; **about −0.43** with the stuck coin 2RR6sfbi |
| Status | running (paper); next: deploy `7184554`, 2-3 days of paper, then a 0.1 SOL real test | **stopped**: the copy bot is off and its server (fra1) terminated |
| Pages | [`03-strategy-A-long-copy/`](03-strategy-A-long-copy/README.md) | [`04-strategy-D-launch-copy/`](04-strategy-D-launch-copy/README.md) |

**Known problems, read before trusting any number:**
- **The stuck coin 2RR6sfbi** (a D copy): it graduated as we bought, the copy bot failed 405 curve sells, and it cost
  about **0.57 SOL**. Fixed in code, never deployed. → [`05-live/stuck-coin-2RR6sfbi.md`](05-live/stuck-coin-2RR6sfbi.md)
- **check.sh's per-coin "ITS NET" for wallet 4 is wrong coin by coin** (only the total is right), and its "since the
  start" line counts closed trades only (−0.76 while the wallet was −1.41).
- **Paper is optimistic:** real fills from Ohio will land later, and 4 of 5 paper take profits came within 10 s.
- **Wallet 4 changed:** early sells on 8 of 20 paper copies, against 3-6% in the data. Its edge shrank from Oct 19 to
  Oct 27.

## A to Z

| Folder | What's in it |
|---|---|
| [`01-who-it-is/`](01-who-it-is/README.md) | wallet 4: how it was found, its +355 SOL, its rule (2.5x / 0.7x / 30 min), bet sizes, coins at once, fees, what's changing |
| [`02-decomposition/`](02-decomposition/README.md) | **where its profit comes from, parts A-F**, over 8 days and in check.sh's window; what we can and can't trade, and why |
| [`03-strategy-A-long-copy/`](03-strategy-A-long-copy/README.md) | the long copy: [rule and code](03-strategy-A-long-copy/README.md), [every backtest](03-strategy-A-long-copy/backtests.md), [the paper run](03-strategy-A-long-copy/paper-run.md), [running it on Ohio](03-strategy-A-long-copy/deploy-ohio.md), [going live](03-strategy-A-long-copy/going-live.md), [changes](03-strategy-A-long-copy/changes.md) |
| [`04-strategy-D-launch-copy/`](04-strategy-D-launch-copy/README.md) | the launch copy: rule, how it was found and tuned, live results, why it made +0.15 while wallet 4 made +2.77 |
| [`04-backtests/`](04-backtests/README.md) | an index of every test, its result, its page and its script |
| [`05-live/`](05-live/README.md) | **check.sh exactly as pasted**, the copy bot's history, the paper history and journal, the stuck coin, the timeline, the money |
| [`06-infrastructure/`](06-infrastructure/README.md) | the boxes (fra1 terminated, Ohio), the code map, deploy files, runbooks, wallets |
| `docs/` | the project's original docs: 00-08 (background, mechanics, speed, architecture, deploy, runbook), 19 (copy targets; §11 found wallet 4, §13 strategy D), **20 (the long copy)**, `docs/research/` (the early research), `docs/PROJECT-README.md` (the original repo README) |
| `analysis/research/` | the studies: `2026-10-26/h9/` (D), `2026-10-26/wallets2/` (the search), `2026-10-27/h9long/` (A, 8 days), `2026-10-27/refused/` (refused copies), `2026-10-28/` (decomposition of check.sh's window, the paper chain check, single coins) |
| `data/datasets/` | the fetched data behind the studies, compressed; see CLAUDE.md "Datasets" |
| `crates/`, `deploy/`, `config/` | the code (Rust workspace), install and units, config templates |

## The words used

- **curve**: pump.fun's bonding curve, where a new coin trades until it fills; then it **graduates** to a **PumpSwap**
  pool.
- **priced in SOL / in another token**: the curve's quote token. Wallet 4's best coins are quoted in WBTC, PUMP, CARDS ...
- **launch buy**: a buy in the coin's create slot or the next. **slot**: about 0.4 s. **create + 12**: 12 slots after the
  coin's create.
- **route**: how our buy reaches the coin (`multi_hop_swap` from wrapped SOL or a WBTC float, at most 2 hops).
- **paper** (`mode = "log"`): decisions priced on the live curve, nothing sent. **P1 / P2**: Oct 19-22 / Oct 23-27.
- **(+x)** after a result: the same without each period's best 2 trades.
- **Beirut time** = UTC+2 on these dates (check.sh and history tables); docs use UTC.

## Security

This repo is **public**. It has no private keys, API keys or config files with credentials. Wallet addresses are public
chain data. fra1's backup (keys included) stays on the Ohio box, root only, never in git. A pre-commit hook
(`.githooks/pre-commit`, enable with `git config core.hooksPath .githooks`) refuses key material.
