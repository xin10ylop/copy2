# The direct screen (Nov 18): every wallet's copy scored at once, then confirmed outside the screen

`m4_direct.py` on 2,380 of the 6,049 live other-token coins of the 48 h (fetched in full, true in-slot order; the
fetch was stopped on the owner's call, a random sample by mint): 679 wallets with 6+ copies, 3 positive on both days
and without the best 2% (BCyNgSB1 out: one creator). Wallet 4's 1.45+ SOL buys: +46.2% a copy (9 copies).
On wallet 4's 27 days of coins (`screen.py FIX=1`, at 0.0345 SOL), 17 wallets pass; 4 buy in wallet 4's own slot.

`m5_confirm.py` (NS=150 random buys, seed 7; wallet 4's live model; 0.0345 SOL) — every candidate FAILS:

| wallet | test | copies | a copy | w/o 2% | P(mean>0) |
|---|---|---|---|---|---|
| 5mWe9kLZ | outside the screen, other-token coins | 69 | −8.7% | −4.43 | 6.8% |
| Z6BLE1zw | outside the screen, other-token coins | 46 | −11.6% | −2.92 | 0.0% |
| EcrMBga8 | coins wallet 4 never bought | 133 | −11.0% | −9.29 | 0.0% |
| Fhbh1DTU | coins wallet 4 never bought | 111 | −19.6% | −13.39 | 0.0% |
| 8ptvshQR | coins wallet 4 never bought | 24 | −21.6% | −3.12 | 0.3% |
| DsGJkPzF | coins wallet 4 never bought | 106 | −5.6% | −6.23 | 13.5% |

The same-slot wallets make money only on wallet 4's coins: the edge is wallet 4's CHOICE of coins, not the timing.
They follow no one (`2026-11-18/leaders/l1_leaders.py`: no wallet leads 3+ of their buys): launch-feed snipers.

## The full screen (5,337 coins of 6,049; Nov 18)

`../out/m4_direct.txt`: 1,869 wallets with 6+ copies; 15 positive on both days and without the best 2%; all 1,869
pooled: −2,618 SOL on 35,858 copies. Wallet 4's 1.45+ SOL buys: +25.2% a copy (19 copies). Out by the lessons: 4
single-creator launch buyers (DnkLKQtY, F5XvCe42, A9H4qn1L, rNAUS5wm), BCyNgSB1 (4 creators, 90% at launch), TAB16RxX
(paused Nov 14), 5mWe9kLZ (failed above). The 8 others go to m5 (NS=100, Triton).

## Triton refused this machine for ~15 minutes (Nov 18 ~03:00 UTC)

HTTP 403 "Your IP or provider is blocked from this endpoint", right after the ~1M-transaction refetch burst; it answered
again ~15 min later. Triton documents per-IP blocks for sources that generate many 403/429 errors, extra filters on
data-centre ranges and proxies (this machine goes out through a data-centre egress proxy), and a stop of service at a
zero pay-as-you-go balance (the balance was ~$5 before the burst). From now on: no Triton bursts; batches, a few
fetchers, and Alchemy for the bulk.

## The 8 confirmed, then engineered like wallet 4 (Nov 18, `m5_confirm.py`, `e1_exits.py`)

NS=100 random buys outside the screen, wallet 4's live model: AMDEmVoc −11.4% (30 other-token copies), 8TPkrBcR +0.8%,
3P3XSWAA +4.8%, 8Y3segeZ +1.9%, H1xshmCR +3.5%, HjuSthan −9.3% (all negative without the best 2%); 7djZvJGN +22.7%
and CzsxDQz6 +14.4% (21 copies each). The exit engineering (23 exits x 16 coin/size filters, picked on the 1st half)
passes none; AMDEmVoc loses under every exit.

**7djZvJGN and CzsxDQz6 on their other-token buys** (OTHER_ONLY, 127 and 130 of their 339 / 350 copies, the fetch
stopped there to save Triton; `../out/m5_other_partial_*.txt`, `../out/e1_exits_other_partial.txt`): +0.6% and −0.3% a
copy under wallet 4's live model, −3.23 / −4.09 without the best 2%. The 21-copy results were luck. Engineered: every
mechanical exit (time, take profit, sell pressure, stall) loses on both halves; the exits built on ITS sale are the
only positive ones (7djZvJGN "its sale + tp 4x": 1st half +13.2%, 2nd +2.7%, w/o 2% −0.36; the filter "tradable now,
its 1.0+ SOL": 2nd half +4.7% / +5.9% on 21 copies, negative w/o 2%). Its sale carries information; the copy is about
break-even at 0.0345 SOL a round trip. Not a wallet 4.

## The 4-day screen (Nov 14 01:07 - Nov 18 01:07 UTC, float-quote coins; `../out/m4_direct_4days.txt`)

4,397 coins (one with 15,409 transactions skipped: 32 min on Alchemy's cap), 2,172 wallets with 6+ copies; all pooled
−2,720 SOL on 44,127 copies. Wallet 4: all 0.5+ buys +2.6% (187), its 1.45+ buys +7.1% (30, P 72%). 30 wallets pass
(both halves, w/o 2%); most on 6-8 copies. **The one with numbers: TAB16RxX, 140 copies, +9.0% a copy, w/o 2% +2.48,
halves +1.99 / +4.32, 123 creators, P 97.2%** — the wallet of the unit `rugsnipe-long-tab`, paused Nov 14 (14 real at
0.1 SOL, −0.1665) and studied again Nov 15 (`2026-11-16/tab/`: +8.8% a copy on the coins it buys alone). These 4 days
are after that study's data: an out-of-sample confirmation under wallet 4's frozen exits. Next: FDhoU1DE (21 copies,
+22.3%, halves equal, P 92.7%). The engineering (`e2_market_exits.py`) is running on the same paths.

## The engineering on the 4 days (`e2_market_exits.py`; `../out/e2_market_exits_4days.txt`, `../out/e2_focus_TAB16.txt`)

The grid's automatic pick (best of exit x quote token x size on days 1-2) overfits: its 4 "passes" score on 5-7 copies,
and for TAB16RxX it picked pumpCmXq coins only (+65% on 13 copies, then −4.2% on 8). The full table is the evidence.

**TAB16RxX, all its 0.5+ SOL buys on float-quote coins, 140 copies (days 1-2: 60, days 3-4: 80):** nearly every exit is
positive on both halves. Wallet 4's live model +6.7% / +11.2% a copy (w/o 2% +0.85 / +1.81); time 60 s +8.6% / +9.6%;
time 120 s (the best on days 1-2) +14.7% / +7.8%; stall 60 s +11.7% / +10.3% (w/o 2% +1.98 / +2.10); sell pressure 5/60
+ stall 180 + tp 4x +10.0% / +13.9%. Its sale is the weakest exit (+4.4% / +4.3%, w/o 2% −0.71 on days 3-4), as the
Nov 15 study found. Size: the 0.5+ set beats 1.0+ and 1.3+ (fewer copies, mixed). One quote token alone does not hold.
Wallet 4 on the same days: its live model +6.8% on days 3-4 (96 copies).

**FDhoU1DE** (21 copies): wallet 4's live model +23.9% / +21.3%, w/o 2% +0.37 / −0.30: a lead to watch, too few copies.

**Reading:** TAB16RxX is a real, modest edge that survives a sample never used to pick it, and wallet 4's frozen exits
suit it. What would run it: the paused unit `rugsnipe-long-tab` with `min_sol` 0.5, the main unit's exits, floats in its
own wallet (63 of its 80 days-3-4 copies are TTWofwAg coins). The owner's call.

## TAB16RxX, the exact config to deploy (`e3_tab_exact.py`, `../out/e3_tab_exact.txt`)

hunt_lib's live model (tp 4.0, 600 s, sell pressure [5, 60, 30], stall 180 s once back at our fill) with its sale
never followed, all its 0.5+ SOL first buys on the 4 days' float-quote coins, 0.0345 SOL a round trip: days 1-2 +5.7%
(53), days 3-4 +13.9% (87), all 140 +10.8% a copy, +7.55 SOL at 0.5, w/o 2% +3.72, P(mean>0) 99.0%. With its sale
followed as the main unit does: +3.7% / +12.2%, all +9.0%. Quotes of the 140: TTWofwAg 97, pumpCmXq 21, SPCXxcqX 14,
3NZ9JMVB (WBTC) 6, 98sMhvDw (HYPE) 2.

## Is the TAB unit's exit the best? (`e4_tab_grid.py`, `../out/e4_tab_grid.txt`, Nov 18)

hunt_lib's live model with every setting free (tp 2/3/4/6x x stall off/60/120/180 x sell pressure off/3-30/5-60/10-60
x 300/600 s = 128), its sale never followed, TAB16RxX's 140 copies. **All 128 are positive on both halves**: the edge
does not hang on the exit. The deployed setting (tp 4, stall 180, sp 5/60, 600 s): +5.6% / +14.0%, all +10.8% a copy;
rank 23 of 128 on all four days, 56 of 128 by its weaker half. The steadiest (tp 3x, stall 60, no sell pressure, 600 s):
+9.9% / +10.2%, all +10.1%. The best on all four days (tp 6x, others as deployed): +13.8%, but +3.1% on days 1-2. The
setting picked on days 1-2 alone (tp 3x, no stall, no sell pressure, 300 s) ranks 119 of 128 on days 3-4: the gaps of a
few points between settings are the noise of 140 copies. One part at a time, no change beats the deployed one on both
halves. **Kept as deployed**; re-judged on the unit's own real trades (the main unit's rule: about 50).

Take profit in fine steps (`TPS=1.5,...,8 e4_tab_grid.py`, `../out/e4_tab_tp_fine.txt`; stall 180 / sp 5-60 / 600 s as
deployed): 1.5x +1.8%, 2x +6.1%, 2.5x +7.7%, 2.75x +9.4%, 3x +9.6%, 3.25x +10.9%, 3.5x +11.2%, 4x +10.8% (deployed),
4.5x +12.6%, 5x +14.2%, 6x +13.8%, 8x +11.1% a copy. Below about 2.75x it is clearly worse; from 2.75x to 6x a plateau
whose ups and downs differ by half (3.25-3.5x the same on both halves, about +10-12%; 4.5-6x higher only on days 3-4).
Kept at 4.0, inside the plateau and the same as the main unit.

## The TAB unit's filters reviewed (`e5_tab_filters.py`, `../out/e5_tab_filters.txt`, Nov 18; tp 3.5x as set)

As deployed (refused past 1.25x): 139 copies, +12.7% a copy. Bands that lose on both halves: its buy size 1.0-1.3 SOL
(17 copies: −5.6% / −14.6%), HYPE and WBTC quotes (2 and 6 copies), our price 1.05-1.1x its price (33: −6.4% / −3.6%,
between two winning bands: noise). None is large or clean enough to filter on. Mixed: SPCX (+1.9% / −13.0%, 14), TTWO
(−7.2% / +18.7%, 97). Steady: PUMP (+76.6% / +25.5%, 21), its 1.3-2.0 SOL buys (+24.4% / +15.8%, 43), fee tier 195 bps
(+28.2% / +15.9%) over 125 (−0.5% / +8.1%). It buys in the create slot (135 of 140; all within 10 s). Every 6-hour block
positive over the 4 days. Coins wallet 4 also bought: +47.6% (13), skipped by the unit only while the main unit holds
the coin (the main unit trades it then). **No filter changed**; to re-check on more days or ~50 real trades: the 1.0-1.3
SOL band, SPCX, the 125 bps tier.

## TAB16RxX on its 14 earlier days: it does NOT hold (`e6_tab_older.py`, `../out/e6_tab_older.txt`, Nov 18)

No fetch: the Nov 15 study's paths (`SP/tab/lk/paths`) and the bot's own detection of its buys with the floats of then
(`SP/tab2/scan_all.out`: ROUTABLE, the float it pays with). Its routable first buys of 0.5+ SOL from Oct 31 12:43 to Nov
14 01:00 UTC (before the 4 days that found it), true in-slot order, 0.0345 SOL a round trip: **697 copies, −5.6% a copy
under the deployed exit (−19.46 SOL at 0.5), P(mean > 0) 0.2%; all 160 exit settings negative over the 14 days.** By the
float the copy pays with: wSOL-routed (its coin's quote reached through a pool from SOL: not in the 4-day test, which
kept float-quote coins only) 467 copies −9.4%; float-paid 230 copies about +2% (WBTC +4.7% on 91, PUMP +3.2% on 56,
TTWO +2.2% on 49, SPCX −9.5% on 13, HYPE −23.2% on 17, DJT +75.6% on 4). The +10.8% of Nov 14-18 is not its usual
result: on float-quote coins it was about break-even before, and the live unit also takes wSOL-routed coins, which lost.

**wSOL-paid copies, the check by period (Nov 18):** TAB16RxX, deployed exit (tp 3.5x): Oct 31 - Nov 5 55 copies −9.0%
(P 5.6%), Nov 6 - 13 412 copies −9.5% (P 0.0%), Nov 15-17 its coins quoted in a non-float token 21 copies −11.1% (P 1.3%):
negative in every period, hence `float_only = true` on `rugsnipe-long-tab` (06:11 UTC). Wallet 4 is different: its
real trades since Nov 12 (the box's journal, Nov 18): wSOL-paid 35 trades +2.1636 SOL, float-paid 54 trades +2.4500;
the float study had wSOL-paid +4.34 SOL on Oct 21-29 (149) and −1.71 on Oct 29 - Nov 13 (135). Wallet 4 keeps paying
from wSOL.
