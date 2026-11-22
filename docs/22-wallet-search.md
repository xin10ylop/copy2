# 22. Finding wallets like wallet 4, and engineering their copy (the playbook, Nov 18)

> **Since Nov 22 the search runs from the tape (§0 below): it found CqCAzte8, now live.** §1-8 are the Nov 18 method on
> fetched launches, kept for reference; their rules (§2) still hold.

## 0. The tape pipeline (Nov 22; `analysis/research/2026-11-20/tape_screen/`)

| Step | Where, what | Cost | Drops |
|---|---|---|---|
| 1. Screen | the box: `s1_screen.py` on `/var/lib/rugsnipe-tape` (`TOPN=60`); our copy replayed on every first buy of 0.5+ SOL, landing a slot after its buy, refused over 1.5x, 5 fixed exits | free (no RPC) | speed traders (median hold < 20 s), launch bundles (half their buys in the create slot), flat bundles, jumpy coins (half refused over 1.5x) |
| 2. Two lists | `TOPMEAN60`: the 5 fixed exits' mean, no tuning, shrunk to 30 copies; `TOPOWN60`: what the wallet made itself on the tape | free | |
| 3. Own history | `w3_robust.py` (via `c1_fetch.py`, Helius `getTransactionsForAddress`, successful transactions only, `MAXPAGES=10`): 14 days of its own pump trades | ~100 credits a request (1,000 transactions), so cents | loses money itself, or up on under half its days |
| 4. Gate 1 | all its first buys of 0.5+ SOL (or 80 for a first look), cut in 4 blocks in time; the mean of 8 fixed exits, no pick, on the 3 blind blocks | ~100 credits a coin replayed | not positive on average, or positive in under 2 of 3 blocks |
| 5. The pick | from 48 fixed settings (8 exits x SOL / token / all coins x its buy 0.5+ / 1.3+), picked on the blocks before each blind block, against a luck baseline | (same replays) | blind mean not positive, under 2 of 3 blocks, or negative without the best 2% |
| 6. Exits by kind | `TABLE=1` / `w3_kind_table.py`: each exit alone by coin kind on the blind blocks, in SOL and copies | (same) | the exit chosen: the one positive in every block |
| 7. Deploy | a second unit on the wallet (`rugsnipe-long-cq` as the model), `copy_sol_coins` / `sol_exits` when the kinds differ | | |

What found CqCAzte8: on the 17 h screen it was 5th on `TOPMEAN` (24 copies, +19.3%), made money itself over 15 days (+11.93,
9 up), passed gate 1 (+5.7 / +6.3 / +16.8% on all 268 buys) and the pick (+8.0% a copy blind on 138, 3 of 3 blocks),
token coins +26.2% and SOL coins +8.4% a copy blind. What the 2026-11-22 runs taught:
- **Do not pick from millions of settings on 60 buys** (`w2_grid.py`): the older half always looks good, the blind half
  keeps half or nothing (4MzQcBVN +11.2 -> +6.1 -> fails on all buys). A real edge is positive under almost any simple
  exit (wallet 4: the median of 282,240 settings +25.97 SOL blind).
- **Use all its buys, not a sample**: a 150-buy sample moved between runs (SOL coins +8.9% on one draw, +1.1% on another).
- **A short history flatters**: 4vw54BmA passed on 1 day (+14.3% blind on 10) and failed on 5 (-0.1% on 77).
- **Making money itself is not enough**: 5Y5nsbGf (+139 SOL), 4vw54BmA (+122), GYhRMtoD (+250, a bundle) all fail the copy.
- **Helius bills per request**: a coin replay is ~100 credits however small; 7,200 requests used ~800,000 credits on
  Nov 22. Test the own history first (cheap), replay coins only for wallets that pass it.


How to search for another wallet to copy, the way TAB16RxX was found and put live on Nov 18. Written after one long
search (Nov 17-18) in which a dozen methods failed and one worked. The failures are listed because each one became a
rule. Every number here has its source in `analysis/research/2026-11-17/wallet_hunt/market/README_direct.md` or the
folders it names.

## 1. What we are looking for

**Wallet 4's edge is its choice of coins, not its speed.** On the 48 h of other-token launches fetched in full, its
coins bought at the launch make +8.4% a buy, every other coin −10.5% (`2026-11-18/creators/`). Wallets that buy the
very same launches in wallet 4's own slot win only on wallet 4's coins and lose 6-22% on the rest (EcrMBga8, Fhbh1DTU,
DsGJkPzF, 8ptvshQR: `README_direct.md`). Its creators' next coins lose (−12.9%), and no rule built from the launch
slot (buyers, SOL, the dev's buy, the quote token) reproduces its choice (`creators/c4_rule.py`: the best of 154 rules
loses on the day it was picked). Whatever it uses is off-chain.

So a "wallet 4" is: **a wallet whose own coin choices make money when we copy them, under our exits, on coins we can
trade**. We cannot find it by what it looks like; we find it by scoring the copy of every wallet directly.

**Where to look: coins priced in a token we hold as a float.** Wallet 4's profit is its other-token buys (part A,
`02-decomposition/`); TAB16RxX's 140 copies were all on float-quote coins (TTWO 97, PUMP 21, SPCX 14, WBTC 6, HYPE
2). The floats: WBTC `3NZ9JMVB`, PUMP `pumpCmXq`, SPCX `SPCXxcqX`, TTWO `TTWofwAg`, DJT `DJTu7vi8`, HYPE `98sMhvDw`,
AAPLx `XsbEhLAt` (the box's `/etc/rugsnipe/long.toml`). Float-quote coins carry 47% of the other-token volume; the
rest (USDC, Xsc9qvGR, BPxxfRCX, ...) we cannot route, so a copy there is worth nothing to us.

## 2. The rules the failures taught

| Failure (Nov 17-18) | What it taught | The rule |
|---|---|---|
| The ladder flip: +51% a copy in the backtest, −16.9% live, −7.8% in the true order | the cached paths had each slot's transactions in reverse order; the bundle sells into whoever follows it | every path in true in-slot order (`2026-11-18/churn/slot_order.py`); a wallet that buys at fixed sizes, in bundles, or one creator's coins at the launch is an operation, not a picker |
| The bundle wait (buy if the bundle has not sold yet): −10% a trade | the bundle sells right after we buy | no "wait for a signal" on operation coins |
| Crew wallets, consensus of pickers | by the 3rd-4th good wallet in, the move is over (−3% to −12%) | copy one wallet's first buy, never "after the k-th" |
| 6ua7w2Gv, 5mWe9kLZ, Z6BLE1zw, AMDEmVoc, 7djZvJGN ... | 48 h gives 6-35 copies a wallet; 1 wallet in 100 passes by luck; all died with more data (7djZvJGN +22.7% on 21 copies, +0.6% on 127) | at least 4 days; judge on 50+ copies; the best 2% out; a bootstrap |
| A fixed "without the best 5" | it removes 0.3% of wallet 4's copies but 12% of a 42-copy wallet's | without the best **2%**, the same share for all |
| The pool traders (PumpSwap, 6 h after the migration) | −19.2% on 18 copies after the pick; they lose on their own trades | the curve's other-token launches are where the edge is |
| The exit grid's automatic pick | the best of 23 exits x quote x size on days 1-2 often scores on 5-7 copies, and fails (TAB16RxX's pick: pumpCmXq only, +65% on 13, then −4.2% on 8) | read the whole table; trust an exit that is positive on BOTH halves, not the single best |
| Copying a wallet's sale | TAB16RxX sells routinely within minutes: its sale is the weakest exit | test its sale like any other exit; drop it if it is not the best on both halves |

## 3. The pipeline

All scripts are in `analysis/research/2026-11-17/wallet_hunt/market/` unless named; the data in the session
scratchpad `SP` (`SP/market/`). Every fetch is batched: 100 `getTransaction` a request on a kept-alive connection
(about 150 times the one-by-one speed), `maxSupportedTransactionVersion: 1` (version-1 transactions exist).

### Step 1. The launch list, cheaply (`m1c_days.py SP T0 T1`)

1. The signatures of pump's `quote-control` PDA (`6z6GDdfb2AjR9ZhJmAUQ5cipJCVxQvLJhB2H8mCwTFBP`): it is in the
   `create_v2` of every coin priced in another token and in no SOL create, so it lists a quarter of the creates.
   Checked on 6 h: it catches 95.5% of the known other-token creates; every miss is USDC-quoted (no float missed).
2. Those create transactions: the coin, its quote, its creator; kept: float quotes only.
3. Each coin's signatures back to its create, its first 2,400 s. `MAXPAGES=60`: the busiest coins (10,000+
   signatures since) are the winners; at the default 10 pages, 140 of one day's coins were left out.

Size, one day: Nov 14: 1,490 float-quote creates, 783 live coins (30+ transactions), 461,291 transactions; Nov 17-18:
1,144 live coins, 838,899 transactions. The bulk is the next step.

### Step 2. The paths (`m2b_full.py`, `LAUNCHES=<list>`)

Every transaction of each live coin's first 40 minutes, its pump trade events, in true in-slot order ->
`SP/market/paths_full/<mint>.json.gz`. Two fetchers a list (one with `REVERSE=1`); each skips a coin the other saved.
A coin with 15,000+ transactions in 40 minutes can be skipped (one was, out of 4,397).

### Step 3. The direct screen (`m4_direct.py`, `PATHS=paths_full FLOATQ=1 LAUNCHES=a,b,c`)

Every wallet's first buy of each coin (0.5+ SOL) gets our copy scored with wallet 4's live model (`hunt_lib`: landing
4 / 8 trades or the next slot, refused past 1.25x, tp 4.0, its early sale followed, sell pressure, stall, 600 s, 0.5
SOL), the mean of the three landings, **0.0345 SOL a round trip**. Found = positive on both halves by time, positive
without the best 2%, 6+ copies. Wallet 4's 1.45+ SOL buys are the yardstick on the same coins.

The 4-day result (Nov 14 01:07 - Nov 18 01:07 UTC, `../out/m4_direct_4days.txt`): 2,172 wallets with 6+ copies, all
pooled −2,720 SOL on 44,127 copies; 30 found, only one with numbers: **TAB16RxX, 140 copies, +9.0% a copy, w/o 2%
+2.48, P(mean > 0) 97.2%**. Wallet 4's 1.45+ buys: +7.1% (30 copies). The other 29 had 6-21 copies.

### Step 4. Sort out the operations (no fetch)

From the screen's columns and a look at the paths: one creator, or 90%+ of buys at the launch -> an insider or a
bundle, out (BCyNgSB1, DnkLKQtY, F5XvCe42, A9H4qn1L, rNAUS5wm). Fixed buy sizes in the create slot -> a ladder, out.
Already judged before (a paused or failed wallet) -> read why first (TAB16RxX's Nov 15 study:
`analysis/research/2026-11-16/tab/`).

### Step 5. Engineer the copy (`e2_market_exits.py`, `ONLY=<prefix>,...`)

On the same paths, no fetch. Each copy under 23 exits, picked on days 1-2 and scored on days 3-4:
- its sale; time 30 / 60 / 120 / 300 / 600 s; tp 1.2 / 1.5 / 2 / 3 / 4x from **our** entry; sell pressure 3/30, 5/60,
  10/60; stall 60 / 120 / 180 s; its sale + tp 2x / 4x; its sale + sell pressure 5/60; sell pressure + stall + tp 4x
  (with and without its sale); wallet 4's live model;
- by coin: all floats, or one quote token; by its buy size: 0.5+ / 1.0+ / 1.3+ / 2.0+ SOL.

Read the full table (`ONLY=`), not the automatic pick. TAB16RxX (`../out/e2_focus_TAB16.txt`): nearly every exit is
positive on both halves (time 60 s +8.6% / +9.6%, stall 60 s +11.7% / +10.3%, wallet 4's live model +6.7% / +11.2%); its
sale is the weakest (+4.4% / +4.3%, negative w/o 2% on days 3-4); its 0.5+ buys beat its 1.0+ and 1.3+; one quote
token alone does not hold. **An edge that is positive under most exits on both halves is real; one that needs a
single exit is luck.**

### Step 5b. Every combination, three ways by payment (`e8_engineer.py`; mandatory, Nov 18)

The owner's rule: test every part at small steps, in every combination, and choose by logic. Run it three times:
```
PAY=all   LIVE=<running setting> python3 -I e8_engineer.py SP WALLET > ../out/e10_<w8>_all.txt
PAY=float LIVE=... python3 -I e8_engineer.py SP WALLET > ../out/e10_<w8>_float.txt
PAY=wsol  LIVE=... python3 -I e8_engineer.py SP WALLET > ../out/e10_<w8>_wsol.txt
```
- The grid: its buy size 0.5 to 2.0 SOL in 0.1 steps (then 1.75, 2.0) x price limit 1.1 / 1.25 / 1.5x / none x tp
  1.5 to 8x / none x 60 to 600 s x sell pressure off or 3/5/8/10 over 30/60 s x stall off or 60 to 240 s x its sale
  never / early / always: 505,440 settings. `LIVE="1.3,1.25,4,600,5/60,180,early"` scores the running setting.
- The ranking: the SOL the **weaker half** makes **without its best 2%** of copies, then smoothed over the
  neighbours (a lone spike cannot win). Not the mean a copy: a thin filter raises the mean while it drops copies that
  still make money.
- Read, then choose by logic: each part varied alone (a plateau, take its middle; parts within noise keep the running
  or simplest value); what each size band adds (a filter that keeps one narrow band is luck); the setting picked on the
  first half alone and its rank on the second (the overfitting check).
- **Payment:** if the floats make money and wSOL breaks even or loses (its own best setting not positive on both
  halves), the copy pays with floats only (`float_only = true`). Nov 18: TAB wSOL 0 of 486,000 settings positive on
  both halves, −24.39 SOL on 466 copies; wallet 4 wSOL −0.81 SOL on 302, its best setting −0.7% a copy.

### Step 6. The exact config, backtested as deployed (`e3_tab_exact.py`)

Score the exact rule that will run, with the bot's own exit logic (`hunt_lib.model`; `early=None` = its sale never
followed). TAB16RxX: +10.8% a copy on 140 (days 1-2 +5.7%, days 3-4 +13.9%), w/o 2% +3.72, P 99.0%; with its sale
followed as the main unit does, +9.0%. The deployed rule is the first.

### Step 7. Outside the window, when the screen has few copies (`m5_confirm.py`, `e1_exits.py`)

The wallet's own history (`winners/w4_history.py`, batched), its buys outside the screened days (`OTHER_ONLY=1`: its
other-token coins; `NOT_W4=1`: the coins wallet 4 never bought; `NS=150`: a fixed random sample, seed 7), scored the same
way. This is what killed 5mWe9kLZ, Z6BLE1zw, AMDEmVoc, the same-slot wallets and 7djZvJGN.

## 4. Pass criteria (all of them)

- **(Nov 18, after TAB16RxX) The days outside the screen must pass on their own, without their best day.** TAB was
  found on Nov 14-18, which held two of its three best days; its 12 older days at the deployed setting made +5.58 SOL,
  and without Nov 11 alone +1.24 over 11 days (about breakeven). Live it lost −0.88 SOL in 31 trades, and its first
  live day was the worst in its record (its own trades −4.7% a coin, 27% won; the model on all 49 copies −5.09). The
  bot and the model were checked and agree (`analysis/research/2026-11-17/wallet_hunt/out/e14_*`, `e16_path_check.txt`).

- 50+ copies over 4+ days, positive on both halves by time;
- positive without the best 2% of copies;
- bootstrap (10,000 resamples, seed 7) P(mean > 0) of 95% or more;
- positive under most exits on both halves, not one;
- not an operation (Step 4), and not mostly wallet 4's own coins (its overlap made nothing: +0.24 SOL on 35 coins, Nov
  15 study; the second unit skips them anyway).

## 5. Deploying a found wallet (as TAB16RxX, Nov 18)

- A second unit, `rugsnipe-long-tab` (`deploy/systemd/rugsnipe-long-tab.service`), on the **same wallet** as the main
  unit (the owner's call: no second wallet to fund). Each config lists the other's state dir in `other_state_dirs`
  (commit `6bc6120`): a coin the other unit holds is skipped, and a sale never closes a token account the other still
  uses (`docs/20-long-copy.md` §3).
- Its config: `copy_wallet`, `min_sol` (0.5 for TAB16RxX), the exits from Step 6 (`follow_its_sell = false`,
  `follow_early_s = []` when its sale is not followed), the main unit's `floats` and `wallet_file`, its own `state_dir`,
  `daily_stop_sol`. The exact edit block is in the session of Nov 18 (README, Nov 18 entry).
- Floats are shared: raise the float its coins use most (`/etc/rugsnipe/float-levels`; TTWO went to 1.2 SOL, the
  `rugsnipe-float-level` timer holds it there).
- Stake: a 0.1 SOL run only checks the mechanics (the fixed fees, about 0.003 SOL a transaction, are 6% of a 0.1 stake);
  the backtest stake (0.5) once the buys land and the journal matches the chain.

## 6. Cost and the RPCs

- **Alchemy** (paid): 650-1,100 transactions a second when batched (100 getTransaction a request, a kept-alive
  session, up to 8 in parallel: no 429s, Nov 18 test). The 8 a second seen first was our own one-call-per-request
  client. Always batch.
- **Triton**: hundreds of paths a minute, but paid by use. On Nov 18 a burst of about a million transactions in minutes
  emptied the balance and then got this machine refused (HTTP 403 "Your IP or provider is blocked from this endpoint")
  for about 15 minutes; Triton documents per-IP blocks for sources with many 403/429 errors and filters on data-centre
  ranges. Rule: batched, a few fetchers, no bursts; Alchemy for the bulk when time allows; Triton only on the owner's
  say, with the budget in mind. The box's own Triton feed is the live bot's: never risk it.
- Data already on disk is reusable: `paths_full` holds Nov 14 01:07 - Nov 18 01:07 UTC (4,397 float-quote coins). A new
  day costs about 0.5-0.85 million transactions.

## 7. The tools' known traps (each one cost an hour on Nov 18)

- Slot order: the cached paths list a busy slot's transactions newest first. `w5_copy.cpath` and `screen.py FIX=1`
  reorder from the curve's reserves; `RAW_ORDER=1` gives the old order.
- Version-1 transactions: request `maxSupportedTransactionVersion: 1`, or about 1 in 50 is refused.
- Scripts that `exec` `w5_copy.py` rewrite `sys.argv`: save the wallet list before (`m5_confirm.py`'s `WALLETS`).
- Python closures in a grid: bind the loop values (`lambda r, nb=nb: ...`), or every rule gets the last ones.
- A launch buy's "its sale" is a random trader's: never follow a sale that is not the copied wallet's.
- `CACHED_ONLY=1` scores only what is fetched (a partial run); `NOFETCH=1` for wallet_study.

## 8. Next, when we search again

1. Extend the screen backwards day by day (Nov 13, 12, ...) with Steps 1-2 and rerun Steps 3-6 on all the days: every
   wallet gets more copies, and TAB16RxX is re-judged on days it was never picked on.
2. FDhoU1DE (21 copies, wallet 4's live model +23.9% / +21.3%, negative w/o 2% on days 3-4): re-judge with more days.
3. Not covered: USDC-quoted coins (quote-control misses them; no USDC float), SOL coins (left out by design), wallets
   whose buys are under 0.5 SOL.
