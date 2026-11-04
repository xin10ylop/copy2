# Rafinhaaaaaa: the second wallet we copy, beside wallet 4

Wallet `Hn6vBWWySnxA8XjxRQDEmZEuH5QL7KqosnJGcLcUzFJ6` (pump.fun username **Rafinhaaaaaa**, 521 SOL on Nov 1 00:00 UTC).
Found on the copy-trading app's leaderboard the owner pasted on Oct 31 (+$135.7k realized over 30 days, ROI +131%,
121 trades, 30 s holds); resolved to its wallet through its pump.fun profile page.

**Status (Nov 4): qualified, not run yet; how fast the copier lands decides it.** The copier (`rugsnipe-long copy`,
[`../docs/21-copier.md`](../docs/21-copier.md)) trades every venue it uses, through Jupiter. Its `[[target]]` is in
[`../config/copier.example.toml`](../config/copier.example.toml): **its buys of 5.0 SOL or more, 1 SOL, one position at
a time** (the 4 SOL plan, [`../08-new-box/`](../08-new-box/README.md)).

**Nov 4 check** ([`04-check-nov04/`](04-check-nov04/README.md)):

- **Still trading:** +57.0 SOL by its own fills on 12 coins since Nov 1.
- **The floor moves from 5.1 to 5.0 SOL:** the old floor was picking its 5 SOL buys by its tip.
- **Our landing decides it.** Out of sample (Oct 4-25), with our buy at the end of the slot after its buy, it makes
  +11.48 SOL on 45 trades, +3.32 without the best 2. Two slots after: +5.66, and −2.33 without the best 2.
  The copier waits 0.35 s for Jupiter before it sends, so the first live hours must show where it lands.
- **Nov 1-4 was about flat:** 8 copies, +0.18 at slot +1.
- **The copier's live code:** three bugs found by a review are fixed.
- **Nov 4 evening, a second wallet** ([`04-check-nov04/wallets.md`](04-check-nov04/wallets.md)): the main wallet still
  trades and holds 461 SOL + about 8,523 USDC. But `BwBWFMFX...`, funded from its money on Nov 3, started trading at
  20:15 UTC with its exact setup (5.05 SOL buys, Axiom, 0.045 tip). One coin so far; check again before adding it
  as a second `[[target]]`.

Everything about this wallet is in this folder; the rest of the repo is wallet 4 (folders `01`-`07`) and the shared
code. It was studied in a separate private repo (copy3) and moved here on Nov 3; the owner chose to keep this repo
public, so its wallet and rule are public.

## The verdict

| Test (SOL; costs: 0.003 SOL a round trip + the swap fee of each venue) | Result |
|---|---|
| This week, Oct 25 00:09 → Nov 1 00:09 UTC: rule and stake picked on days 1-4, scored on days 5-7 | days 1-4 **+14.14** (8 trades), days 5-7 **+32.19** (9), days 5-7 without the best 2 **+3.39** |
| **Out of sample:** the same rule, unchanged, on its 3 weeks before (Oct 4 00:09 → Oct 25 00:09 UTC) | **+37.67 on 35 trades, +14.23 without the best 2** |
| Landing 1 / 2 / 4 / 7 trades behind it (out of sample) | +47.73 / +37.67 / +34.53 / +33.52; without the best 2 +23.10 / +14.23 / +10.40 / +9.77 |
| By week (out of sample) | week 1 +27.89 (23 trades), week 2 +9.79 (12), week 3 a quiet week (4 trades in all) |
| Landing that matches our live speed (7 of 15 copies in its slot, 8 in the next; wallet 4's live run) | 2 trades behind: 59% in its slot, 33% the next (out of sample), the K = 2 rows above (`03-backtests/README.md` §3) |

Sources: `03-backtests/out/this-week_oct25-nov01.txt`, `03-backtests/out/out-of-sample_oct04-25.txt` (`analysis/final/sim_g1.py`).

## Its logic, and our rules

| | It does | We do |
|---|---|---|
| What | big buys, about 5 SOL (p10/50/90 2.05 / 5.05 / 7.32 SOL over Oct 4-25), mostly coins priced in SOL (79 of 95), on the pump curve, Meteora DBC, Raydium LaunchLab and CPMM, through the Axiom router | copy only its **buys of 5.1 SOL or more** |
| Landing | pays 0.045-0.1 SOL tips to land first | we land 2 trades behind it (our live median, wallet 4's copy) |
| Exit | sells fast: first sale a median 18-31 s after its buy, at a median 1.3-1.6x | **sell after 300 s, or right behind it if it sells first**; no take profit, no stop |
| Size | its own size | backtest: **its size, capped at 3 SOL**; the 4 SOL plan: **1 SOL** (`03-backtests/README.md` §4) |

Its own trades: 76 of 95 won (Oct 4 00:09 → Oct 25 00:09 UTC), a trade's median +28.6%, mean +78.5% (GMGN prices). Our copy behind it pays
about +36% over its price (median), so a typical copied trade loses (median about −0.6 SOL at a ~3 SOL stake); the
copy makes its money on the runners it catches, a handful a week, and stays positive without its best 2 in both tests.

## The risks

- **Skewed:** most copied trades lose a little; a few runners pay for them. Expect losing days.
- **Few trades and quiet weeks:** 12-23 copyable buys a week; one week in four had almost none.
- **Big stakes:** up to 3 SOL a trade; size the bankroll for a run of losers (a typical loss is ~0.6 SOL).
- **Venues, the main blocker:** our long bot (`rugsnipe-long run`) routes the pump curve and PumpSwap only
  (up to 2 pools). On those coins alone the rule earns almost nothing: out of sample (Oct 4-25, stake 0.3 SOL, 1 behind)
  +0.74 on 18 trades and **−0.73 without the best 2**, against +5.80 on all 35 (+3.18 without the best 2). Its winners
  are on Meteora DBC (23 of its 95 trades), Raydium LaunchLab and CPMM, and Meteora DAMM v2. **Built Nov 2:** the copier
  routes them through Jupiter. A paper replay copied its 10.1 SOL pump buy and skipped its 5.0-tier DBC buy
  (`analysis/final/sim_g1.py` on the `.route` trip files for the venue split).
- **The copier is slower than the long bot:** it asks Jupiter for a quote and a swap over HTTP before it sends. The rule
  holds further back: 4 and 7 trades behind, +34.53 and +33.52 out of sample (+10.40 and +9.77 without the best 2).
- **Model, not live:** the model reproduced wallet 4's live run trade by trade (+1.36 vs +1.345 SOL, same exit on 16 of
  16), but this wallet's coins and venues differ. Paper first.

## How it was tested

`analysis/final/` holds the whole pipeline (`run.sh WALLET` runs it): every closed round trip of the week from GMGN
(`build.py`), each trade's chain facts (`chain.py`), our price 1 / 2 / 4 / 7 trades behind each of its buys and sales
on the pool's fitted curve with our own impact (`reprice.py`, `addk.py`), price paths from the chain (`paths_g1.py`),
its own exit levels read from its sales, ours placed just inside them, and the stake, picked on days 1-4 and scored on
days 5-7 (`sim_g1.py`), then the picked rule scored unchanged on earlier weeks (`runoos.sh`, `FIXRULE`). The method and
its calibration against wallet 4's live trades are in `analysis/final/REFERENCE.md`. Data: `data/<wallet>/`.

## At 1 SOL (the 4 SOL plan)

Out of sample (Oct 4-25), 2 trades behind: **+14.91 on 35 trades, +6.75 without the best 2** (4 behind: +13.74,
+5.33); this week (Oct 25 - Nov 1): +16.45 on 19, +6.71 without the best 2. Its copies rarely overlap: 3 of its 37
buys of 5.1+ SOL came while another of our copies would be open, never more than 2. One position at a time loses
almost nothing (`03-backtests/README.md` §4).

## Next steps

1. Done Nov 2: the copier and this wallet's `[[target]]` (`../config/copier.example.toml`).
2. Paper on the new box: the journal's paper buys against the model (price paid vs its price, exit, net).
3. A few hours at 0.3 SOL, every trade checked on chain (`../03-strategy-A-long-copy/deploy-frankfurt.md` §6 is the
   template), then 1 SOL (`../08-new-box/`).
4. Re-score it every week with `analysis/final/run.sh`; stop if a week's out-of-sample result turns negative without
   the best 2.

**Re-running the analysis:** `analysis/final/run.sh WALLET` needs `GMGN_API_KEY` in the environment, the Triton URL file
the scripts read, `gmgn-cli` and Python 3; `runoos.sh WALLET WIN_T0 WIN_NOW "FIXRULE" SUFFIX` scores a fixed rule on
another window. Run Python with `python3 -I`. The scripts still hard-code the session scratchpad paths they were
written in; adjust `g1lib.py` / `rescore2.py`. No key is in this folder.
