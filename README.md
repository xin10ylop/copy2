# copy2: the wallets we copy, and the bots that copy them

Two copied wallets, kept apart, and the shared code:

| | Wallet | Bot | Where |
|---|---|---|---|
| **Wallet 4** | `H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg` | part A: the long copy (`rugsnipe-long run`); part B: the copier, off | folders `01`-`07` below |
| **Rafinhaaaaaa** | `Hn6vBWWySnxA8XjxRQDEmZEuH5QL7KqosnJGcLcUzFJ6` | the copier (`rugsnipe-long copy`) | [`rafinhaaaaaa/`](rafinhaaaaaa/README.md) |
| Both, on one box | | | [`08-new-box/`](08-new-box/README.md): the 4 SOL plan, from an empty server to live |

Code: `crates/rugsnipe-long/` (the long copy, docs/20; the copier, [`docs/21-copier.md`](docs/21-copier.md)), with
`deploy/` and `config/`. Operator 1 ("him", AHwJSnFN) and the other copied wallets are in the **copy1** repo. Both
repos started from the same code snapshot (`xin10ylop/rugsnipe` at `7184554`, Oct 28). The box builds from this repo's
branch `claude/magical-einstein-k78idp`.

**Agents: read [`CLAUDE.md`](CLAUDE.md) first.**

## Live again (Nov 12)

**The long copy (wallet 4's part A) runs live since Nov 12 01:23 UTC (03:23 Beirut)** on a Vultr Frankfurt box
(`fra-long`, High Performance AMD, 4 vCPU / 8 GB, $48 a month, a card on file; every Cherry Frankfurt VDS was out of
stock). Settings: 0.1 SOL a copy, 2 open, take profit 2.5x, **no stop**, 1790 s, its sale not followed, price limit
1.25x, daily stop 0.3 SOL. Wallet `Eao8T2Pk2aDzPWUFCA8si7oWd5ndFKfnX3HjYMpERst6` (1.78 SOL in, 0.2 of it as the WBTC float); **its key file was copied to
the owner's Mac (sha256 prefix checked on both) before any SOL went in.** Pings: 0.54-0.70 ms to Jito, Helius,
Nozomi and Triton in Frankfurt. The copier (Rafinhaaaaaa) is installed but not enabled. Next: about 20 closed trades
at 0.1, checked on chain against the model (`analysis/research/2026-10-31/since_stop/`), then 0.5 SOL × 2.
**0.5 SOL × 2 since Nov 12 14:18 UTC (16:18 Beirut)**, the owner's call after the first 3 closed: daily stop 1.0 SOL;
the WBTC float topped up with 0.4 SOL (44,861 units, slot 468555971; float 67,418 units, about 0.57 SOL at wallet 4's
own swap rate that week) so WBTC-routed copies (40 of its 105 last week) still fit a stake. SOL 1.4236 after.
At 0.5 SOL (journal, Nov 12 UTC): #3 `7dDprVHP` timer −0.1106, #4 `57pQW4mw` timer −0.0124 (peak 1.83x), #5
`Eymbsj8M` take profit 2.50x after 312 s +0.6228. The day: 6 closed, 2 won, +0.7477 SOL. Two coins airdropped to the
wallet by `HckQ93Xq...` (15:06-15:51 UTC; we signed nothing) were sold through Jupiter with `float sell`: +0.1968 and
+0.0674 SOL on chain. SOL 2.1877 after, plus the WBTC float (about 0.59 SOL).
**Take profit 2.4 since Nov 12 16:42 UTC** (was 2.5; `since_stop/out/tp_fine.txt`: the 2.3-2.6 plateau, 2.4 ahead by
0.4 SOL over two weeks and just under wallet 4's own 2.5x target). The restart's journal: `tp 2.4x`, feed connected.
**A second copy, of `TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3`, in paper from Nov 12** (the lookalike search,
branch `claude/dreamy-dijkstra-ln0wdk`, `analysis/research/2026-11-13/lookalikes/out/compare.txt`): the only wallet
that passed the pick-on-week-1 test (tp 3.0, 300 s: week 2 raw +13.76, corrected +20.95; week 1 raw −2.28 with the
live exit, its own week 1 −1.78 without its best 2). Checked Nov 12 with the bot's own detection on its last 150
transactions (`examples/scan.rs`, `W=`): its buys are seen and valued (SOL through Jupiter or wSOL, 4 of 34 unpriced);
its 1.0+ SOL buys that day were mostly in an unroutable quote (Xsc9qvGR), 2 of 7 routable. 74% of its transactions fail
(96% on Nov 12). Unit `rugsnipe-long-tab` (config `/etc/rugsnipe/long-tab.toml`, state `/var/lib/rugsnipe-long-tab`,
wallet `tab-wallet.json`): min_sol 1.0, tp 3.0, 300 s, no stop, its sale not followed, paper at 0.1. Real only after
its paper record, at 0.1 SOL with its own wallet.

**First 3 closed (Nov 12, checked on chain, journal = chain):** +0.2479 SOL. All three landed in wallet 4's own block
(3, 7 and 8 coin trades between its buy and ours).

| # | Coin | Exit | Real | Raw model, same landing | Real minus model |
|---|---|---|---|---|---|
| 0 | `Ci9Bg1Bx` | timer (2 sells failed 6004, the 3rd landed) | −0.0597 | −0.0372 | −22.5 pts |
| 1 | `BttUQVPM` | timer | −0.0455 | −0.0368 | −8.7 pts |
| 2 | `5tePJcGm` | take profit, 351 s | +0.3531 | +0.1475 | +205.6 pts |

Source: `analysis/research/2026-10-31/since_stop/out/live_nov12_vs_model.txt`. Too few to judge: one win carries the
total, and the two losers did worse than the model.

Wallet 4 on the same coins (`his_vs_ours.py`, `out/his_vs_ours_nov12.txt`): it sold all three after 3 to 5 minutes;
we hold to our own exits.

| Coin | Wallet 4 | We | Its sale |
|---|---|---|---|
| `Ci9Bg1Bx` | +2.9% | −59.7% | after 303 s |
| `BttUQVPM` | −28.1% | −45.5% | after 179 s |
| `5tePJcGm` | +113.3% | +353.1% | after 224 s |
| Total | +39.4% (+2.22 on 5.65 SOL) | +82.6% (+0.248 on 0.3 SOL) | |

## Where things stood (Nov 3)

**Nothing runs; no box exists since Oct 29.** The plan for the next box ([`08-new-box/`](08-new-box/README.md)) is
4 SOL in two wallets. Its backtests give about +0.7 to +3.5 SOL a day (§1 there); expect the low half.

| Bot | Copies | Stake | Open at once |
|---|---|---|---|
| The long copy | wallet 4's part A | 1 SOL | 2 |
| The copier | Rafinhaaaaaa | 1 SOL | 1 |

It is prepared, not started: paper first, then the first live hours at 0.1 / 0.3 SOL.

**Nov 4, wallet 4 since the box died** ([`analysis/research/2026-10-31/since_stop/`](analysis/research/2026-10-31/since_stop/README.md)):
it changed its rule again (the 30-minute timer is gone, early sales on two thirds of its big buys), took 510 SOL of
profit on Oct 30 and kept trading (balance 114 → 393 SOL by Nov 4). The long copy as built would have made +1.79 SOL in
5.9 days at 1 SOL × 2, about zero without the best 2; **with no stop, +6.92**, better at every landing and in both
halves. The plan's long config now sets `stop = 0.0` (the code allows it since Nov 4).

## Wallet 4

### Where things stood (Oct 28, evening)

**Re-examined on Oct 28** ([`07-rework-2026-10-28/`](07-rework-2026-10-28/README.md)): wallet 4 still makes money (+82 SOL
in the 38 hours to Oct 28 14:54 UTC) and is one bot with no siblings, but it **changed its rule on Oct 27** (early sales
on 49% of its big buys, against 3.5% in the week the strategy was picked on), and on that fresh period the long copy
**loses** (−2.02 SOL on 25 copies; about flat as the bot really trades). The paper run's +2.47 SOL came from 3 coins
that graduated, a kind no earlier backtest contained. The code review found 8 money-losing bugs in the never-run real
path; **fixed, tested, and simulated on mainnet**. Part B cannot be routed through pump's programs at all. The plan: 2-3
more days of paper with the hardened bot on a €59/month Frankfurt box (running since Oct 28 17:58 UTC; Ohio was
terminated that evening), then the 0.1 SOL test, then decide.

**Nov 2: the copier** ([`docs/21-copier.md`](docs/21-copier.md), `rugsnipe-long copy`). It copies several wallets on
any venue through Jupiter, so wallet 4's part B (pump coins priced in PUMP, CARDS, USDC ...) is tradeable now. So are
other wallets' coins on Meteora and Raydium. Code, tests, the unit and a paper replay are done. **Nothing has run on a
box** (none exists since Oct 29). Part B copied through Jupiter is weak (`analysis/research/2026-11-02/`): +4.88 on
Oct 23-26, +8.08 on Oct 27 - Nov 1, −6.05 without the best 2. It is off in the 4 SOL plan (`config/copier.example.toml`). The same study
found no rule to pick part-A or part-B launches ourselves.


| | Strategy A: the long copy | Strategy D: the launch copy |
|---|---|---|
| What | copy its **1.45+ SOL buys of coins priced in other tokens** that pump's own programs can route; 1 SOL each; sell at 2.0x / 0.8x / 1790 s / behind its own sell | copy its **launch buys of SOL-priced coins**; sell at create + 12 slots (about 5 s); 20% price bound |
| Its share of wallet 4's profit (Oct 19-27) | part A: **+102 of +355 SOL** | a slice of part D: +29 of +355 |
| Backtest (out of sample Oct 23-27) | **+11.13 SOL** at 4 open (Oct 19-22: +6.73) | +0.22 (P2), +1.48 (live replay); slightly negative without the 2 best coins |
| Live | **paper only**. On the Ohio box Oct 27 16:11 UTC to Oct 28 (old code): 21 closed, 9 won, **+2.4666 SOL** to Oct 28 13:31 UTC (+1.57 at the backtest's costs; all of it 3 graduated coins); checked on chain: nothing missed. On the Frankfurt box: paper 17:58-18:34 UTC, then **real money at 0.1 SOL since Oct 28 18:34 UTC** (wallet `E7KX1hcM...`). **At 0.1 SOL, 18:34-22:04 UTC: 6 closed, 4 won, +0.3146 SOL**, every trade checked on chain, 5 of 7 buys in its own slot. **Since 22:04 UTC: 0.5 SOL × 3 open, daily stop 1.0** (the owner's decision). First night at 0.5: 7 closed, 3 won, +1.08; **13 closed, 7 won, +1.39 SOL since the start**. **Since Oct 29 08:21 UTC: 1 SOL × 3 open, daily stop 3.0** (the owner's decision), 3.2 SOL put in, 4.6 SOL in the wallet | **real money** Oct 26 17:36 → Oct 27 07:50 UTC: **+0.1456** on 77 filled; **about −0.43** with the stuck coin 2RR6sfbi |
| Status | **stopped: the Frankfurt box was deleted by Cherry on Oct 29 ~13:40 UTC for a zero hourly balance, the wallet's only key with it; 4.5 SOL lost** (`03-strategy-A-long-copy/deploy-frankfurt.md`). Before that, live at 1 SOL × 3 on the Frankfurt box (`fra-long`, Cherry VDS, this branch's code) since Oct 29 08:21 UTC, after 0.5 SOL from Oct 28 22:04, 0.1 SOL from 18:34 and 36 minutes of paper; next: watch the book without the best 2, wallet 4's pace and its early-sale rate daily ([the plan](07-rework-2026-10-28/README.md#6-the-plan-how-to-go-live-again-in-order)) | **stopped**: the copy bot is off and its server (fra1) terminated |
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
| [`analysis/research/2026-10-29/wallets/`](analysis/research/2026-10-29/wallets/README.md) | **other wallets with wallet 4's edge? (Oct 29)**: 856 coins' early buyers, 24 hours of creates, 6 wallets scored in full: none copyable; wallet 4 is alone in holding its big launch buys |
| `docs/` | the project's original docs: 00-08 (background, mechanics, speed, architecture, deploy, runbook), 19 (copy targets; §11 found wallet 4, §13 strategy D), **20 (the long copy)**, `docs/research/` (the early research), `docs/PROJECT-README.md` (the original repo README) |
| `analysis/research/` | the studies: `2026-10-26/h9/` (D), `2026-10-26/wallets2/` (the search), `2026-10-27/h9long/` (A, 8 days), `2026-10-27/refused/` (refused copies), `2026-10-28/` (decomposition of check.sh's window, the paper chain check, single coins; **`fresh/`** the study on Oct 27-28 data, **`more/`** the skipped trades and copying better, **`wallet/`** the wallet check) |
| `data/datasets/` | the fetched data behind the studies, compressed; see CLAUDE.md "Datasets" |
| [`08-new-box/`](08-new-box/README.md) | **the next box**: both bots, 4 SOL, every step from an empty server to live |
| [`rafinhaaaaaa/`](rafinhaaaaaa/README.md) | **the second copied wallet**: who it is, its rules, its backtests, the analysis pipeline, its data |
| `crates/`, `deploy/`, `config/` | the code (Rust workspace), install and units, config templates (`long.example.toml` the long copy, `copier.example.toml` the copier) |

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
