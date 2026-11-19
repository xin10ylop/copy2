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

## The re-screen with no exit assumed, by buy size (`e7_robust_screen.py`, `../out/e7_robust_screen.txt`, Nov 18)

The 4 days' float-quote coins, 64 exit settings (tp x stall x sell pressure x time x its sale), each wallet on its
0.5+ / 1.0+ / 1.3+ SOL buys (30+ copies a band): 225 wallets, 403 wallet-bands. The bar (75%+ of the settings positive on
both halves, the median setting positive w/o 2%, P 90%+) is passed by TAB16RxX 0.5+ alone (98%, median +8.0% a copy,
w/o 2% +2.29, P 96.2%) — and wallet 4's own 1.3+ buys would not pass it on these 4 days (43 copies: 55%, +8.2%, +0.90,
P 85.9%). With the bar set at wallet 4's level (50%+, w/o 2% positive, P 85%+) one more: **5KcKcGcz 0.5+** (33 copies,
53%, median +12.0%, w/o 2% +1.31, P 95.4%, 32 creators, never at the launch: a later buyer). The next ones fall well
short (AMDEmVoc 45% / +0.08 / 68%; 54YNHFVt 1.0+ 12%). Every steadiest setting has its sale NOT followed.

## e8 v2: every combination, three ways by payment, ranked by SOL (Nov 18, morning)

The owner: "test with all coins, all sizes; if floats win and wSOL breaks even or loses, remove them; be structured;
same for future wallets". `e8_engineer.py` now runs each wallet three times (`PAY=all / float / wsol`, outputs
`../out/e10_<wallet>_<pay>.txt`; `LIVE=` scores the running setting beside the choice). Two fixes over the first run
(`e9_*`, kept): wallet 4's corpus was not split by payment (the route planner's `input:` from each folder's scan is
now used; a coin quoted in one of the 7 floats counts as float-paid), and the ranking is now the SOL the **weaker half
makes without its best 2% of copies** (the mean a copy let a thin 1.75+ band win: +37% on 162 copies = 30 SOL, against
1.3+ at +13% on 545 = 36). At least 20 copies in each half. A table of what each buy-size band adds is printed.

**What we pay with** (the running setting; all coins in the window):

| wallet | float-paid | wSOL-paid | wSOL's own best setting |
|---|---|---|---|
| TAB16RxX (Oct 31 - Nov 18) | 363 copies, +6.7%, +12.19 SOL, P 98.3% | 466, −10.5%, −24.39 SOL, P 0.0% | 0 of 486,000 settings positive on both halves |
| wallet 4 (Oct 21 - Nov 18) | 749, +12.6%, +47.27 SOL, P 100% | 302, −0.5%, −0.81 SOL, w/o 2% −9.14, P 41% | 21 of 427,680 positive on both halves; the choice −0.7% |
| 5KcKcGcz (Nov 14-17) | 33, −0.9% (its own choice +28.5%) | 8, too few | too few |

wSOL loses for TAB and breaks even at best for wallet 4 (its live 35 wSOL-paid trades since Nov 12 made +2.16 SOL;
the 302-copy history says that was the lucky side of a coin that breaks even). By the owner's rule: floats only for both.

**Wallet 4, float-paid** (1,071 copies): the choice is 1.2+ SOL, no price limit, tp 4, 600 s, sell pressure 10/60,
stall 240, its sale never (+59.15 SOL, weaker half w/o 2% +17.50). Each part varied alone: tp 4 is the middle of the
3.5-5 plateau (the running value); 600 s best; sell pressure 5/60, 8/60 and 10/60 within 3 SOL; stall off/180/240
within 3 SOL; its sale never or early equal. So the exit stays (frozen anyway). Entry: buy size 1.0+ to 1.3+ is one
plateau (+57 to +59 SOL), the bands [1.0, 1.2) add 0.05 SOL on 132 copies and [1.2, 1.3) +2.21 on 47 (positive in
both halves); price limit 1.5x or none +57 to +59 against 1.25x +52. Scored: running 1.3+ / 1.25x +47.27 (w/o 2%
+11.88 / +13.69); **1.2+ / 1.5x +53.20 (+15.02 / +15.18), rank 326 of 466,560**; 1.3+ / 1.5x +50.14; 1.2+ / 1.25x +48.35.

**TAB16RxX, float-paid** (370 copies): the choice 1.2+ rests on one band, [1.3, 1.4) SOL (74 copies, +11.85 of the
+19.57), a narrow pick, so the size stays 0.5+. Exit: tp 5 to none is a plateau (6 its middle), stall 240 and sell
pressure 10/60 beat the running 180 and 5/60, its sale never. Scored at 0.5+: running (1.25x, tp 3.5, 5/60, 180)
+12.19 SOL, weaker half w/o 2% −3.97; **1.5x, tp 6, 10/60, 240: +19.50, w/o 2% +0.06 / +2.22, P 99.4%, rank 685 of
437,400**; tp 6 alone (5/60, 180) +15.52; 10/60 + 240 alone (tp 3.5) +14.14. Its edge without its best copies is thin.

**5KcKcGcz**: 33 float-paid copies in 4 days; the choice (tp 2-3, 300 s) +23-28% a copy, P 99.8%. Too few to deploy;
it needs its earlier days fetched (Alchemy, batched).

**Alchemy speed** (`alch_bench.py`, scratchpad): one batch of 100 getTransaction 0.14 s (726 tx/s); 8 batches of 50 in
parallel 556 tx/s, no 429s; week-old transactions 650-1,100 tx/s. The 8 tx/s seen before was our one-call-per-request
client; batched fetching (m1c, m2b, w5) runs near the plan's speed.

## The double check before deploying (Nov 18, `e11_check.py`, outputs `../out/e11*_<wallet>.txt`)

Each change alone and together against the running setting, on the same copies: SOL, by week, the halves without
their best 2%, each landing (4 trades / 8 trades / the next slot) apart, the price limit applied per landing, and a
paired bootstrap of the difference (P(better), 10,000 resamples).

Wallet 4 (1,479 copies, Oct 21 - Nov 18; running = 1.3+, 1.25x, tp 4, 600 s, 5/60, 180, its early sale, both payments):
| change | SOL vs running | P(better) | every landing | w/o its best 2% halves |
|---|---|---|---|---|
| floats only | +1.68 (322 fewer trades) | 65.8% | +0.52 / +4.78 / −0.26 | +4.29 / +10.86 → +7.47 / +17.12 |
| price limit 1.5x | +4.01 | 98.4% | +2.12 / +9.91 / 0.00 | better both; 4 of 5 weeks |
| 1.5x on top of floats only | +3.06 | 97.6% | all better | every week |
| 1.2+ on top of floats + 1.5x | +2.65 | 88.7% | +3.90 / +0.54 / +3.51 | +1.72 / +0.93; 3 of 5 weeks |
| all three | +7.39 (+53.17 against +45.78) | 91.4% | +6.77 / +11.75 / +3.65 | +9.44 / +19.47 |

TAB16RxX (370 float-paid copies, Oct 31 - Nov 18; running = 0.5+, 1.25x, tp 3.5, 600 s, 5/60, 180, its sale never):
| change | SOL vs running | P(better) | note |
|---|---|---|---|
| tp 6 | +3.34 | 84.6% | every landing better; +1.98 without the 2% of copies that gained most |
| price limit 1.5x | +1.92 | 98.1% | every week better |
| tp 6 + 1.5x | **+5.24 (+16.23 against +10.99)** | 92.9% | every landing; +3.88 without the top 2% of gains |
| sell pressure 10/60 on top | +2.97 | 88.5% | −1.08 without the top 2% of gains: a few copies |
| stall 240 on top | −0.14 | 42.1% | not better |
| its sale always (sell behind it) | −6.00 | 0.3% | worse every week; the early rule −2.28, P 6.5% |

Deployed by this check: wallet 4 floats only + 1.5x (+ 1.2+, the weakest of the three); TAB tp 6 + 1.5x, sell pressure
and stall unchanged, its sale not followed.

## 5KcKcGcz on its other days: rejected (Nov 18, `e13_outside.py`, `../out/e13_5KcKcGcz.txt`, `../out/m5_5KcKcGcz.txt`)

Its history since Nov 1 (Alchemy, batched: 7,121 transactions, 2,592 first buys), its first buys of 0.5+ SOL on coins
priced in another token outside the screen's 48 h: 353 copies (Nov 1-18; 154 float-quoted). The exit picked on its 4
days (tp 2x, 300 s, no sell pressure, stall 240): −27.69 SOL, −15.7% a copy, both halves negative, P 0.0%; floats alone
−13.74. Wallet 4's live exit −13.66, TAB's −15.53. **Not one of the 9,720 exits makes money over these days**, even
picked with hindsight (the best −5.71). Its 4 days (+23-28% a copy on 33) were luck.
From scratch on these days (the owner: engineer the exit from scratch; the full grid, 505,440 settings): floats only,
**0 settings make money on both halves**; all coins 4,700 (0.9%, all on thin size cuts of ~20 copies: the best, 1.4+
SOL, 22 copies, +1.90 SOL, half 1 −0.82); at 0.5+ none of the 9,720 exits makes money. Rejected stands.

## Wallet 4's look-alikes by their own trading (Nov 18 afternoon; `p1_profile.py`, `e13_outside.py`, `../out/p1_*`, `../out/p2_*`)

The owner: find wallets that make SOL like wallet 4, buy float-quoted coins and hold. `p1_profile.py` reads every
wallet's OWN trading on the 4 days of paths (7,263 other-token coins, 24,964 wallets; no copy model, no fetch) and
keeps those shaped like wallet 4, the filters calibrated on wallet 4 itself (it passes them): own result positive and
without its best 2 coins, 3+ days active, 2+ positive, a median hold of 60/90-1,200 s (wallet 4 180 s), under 10% sold
within 10 s (wallet 4 3%), no fixed sale delay (TAB's 210 s), the create slot allowed (wallet 4 53%), half or more on
float-quoted coins. Wallet 4 is alone in size (+47.45 SOL without its best 2; the next +12.90); the big earners are all
1-2 s snipers. 17 look-alikes tested on their other days (the screen's 4 days left out), the full grid from scratch:

| wallet | other-day copies | floats only: settings positive on both halves | verdict |
|---|---|---|---|
| CuDe51GP | 223 (137 float) | 5,425 of ~500,000 (1%); best with hindsight +3.61 on 137 | fails |
| FZU56d9i | 975 (558) | 0 | fails |
| 4xPvbD8z, 5Y5nsbGf, 8pdyvAy2, DsGJkPzF, EgYa22bN, 75gEU53q | 38-117 | 0 | fail |
| 94JRjXuR | 39 (20) | 5,740 (1%) | fails |
| 6GGytYh7 | 29 (19) | too few | not judged |
| 5hAgYC8T, AfUULgXg, 965Nk2u3, D4HZgnoP | 4-13 | too few (new wallets) | not judged |
| 4vw54BmA, 6DQAGJT7 | - | their signature lists hold no pump trades of their own | not judged |
| **9H692HgE** (with ApEGuisw, GkqnbJYm: one operator, the same coin in the same slot on 196 of 197 buys, all three born Nov 12 07:09 UTC) | 35 (26) | **185,259 (37%)** | **promising, too young** |

9H692HgE on its 2.7 other days (Nov 12-14, Nov 18), float-paid: held 600 s with no tp, sell pressure or stall, 26
copies +6.80 SOL (+52% a copy), w/o 2% +3.74, P 91.5%; with wallet 4's exit +0.25. Every part has a plateau
(tp 8x-none, 600 s, sell pressure off). Too few days for the rule (the days outside the screen must pass on their own
without their best day): re-score from the chain in a few days.

### 9H692HgE: August against November (Nov 18, cached paths only after the owner asked to spare Alchemy)

The trio is not new: it traded Aug 9-24 (1,038 buys, all SOL-priced coins), was quiet until Nov 12. August, 568
copies of its 0.5+ SOL first buys (Aug 9-20, 552 of 714 paths fetched before the fetch was stopped):
- the November exit (600 s, no tp, sell pressure or stall, its sale never): **−18.12 SOL**, P 6.6%;
- its sale followed (always) is the exit that works there: tp 3.5x, sell pressure 10/60, stall 180, 600 s, its sale
  always **+26.86 SOL**, +9.5% a copy, both halves (+18.49 / +8.37), w/o 2% +14.27, P 100%; 151,746 of ~500,000
  settings positive on both halves; "its sale always" is the part that matters (never +12.21, early +14.91, always
  +30.95 at best);
- that August exit on November's 26 float copies outside the screen: +1.14 SOL, P 75%, w/o 2% +0.14 (the November
  exit +6.80 there).
No exit is strong in both periods: it changed style (coin class, and how its own sales time the top). Not deployed.
Paper copy (no money, no RPC credits) proposed to gather November-style data with the August exit and both policies.

## The owner's angle, Nov 19: "2 good coins a day and profitable = a good wallet" (`m6_days.py`, `../out/m6_days.txt`)

Every wallet's copy on the 4 days fetched in full (7,263 coins, Nov 14 01:07 - Nov 18 01:07 UTC; 72,133 copies of 4,886
wallets with 4+ first buys of 0.5+ SOL, pooled −4,737 SOL), judged by day: days up, big winners (a copy +100% or more)
and on how many days. **Up on every active day (3+) with a big winner on 3+ days: one wallet, TAB16RxX** (161 copies,
+6.5%, 4 of 4 days up, 10 big winners on 4 days), the wallet that then lost live on Nov 18 (−0.88 SOL, 31 real). Up on
all but one day with big winners on 2+ days: 33, most on 2-3 active days and 8-30 copies (3cfxKE7z, HUYdMo42 and
2rvKbvgT are one trader). **Blind: chosen on days 1-2 by the rule (up both days, a big winner both days), scored on days
3-4: 20 wallets, −13.69 SOL on 538 copies (−5.1% a copy; every wallet −14.0%), 3 of 20 up (TAB16RxX +3.46, wallet 4
+1.63, FDhoU1DE +0.81).** Two good days do not predict the next two. FDhoU1DE (27 copies, +23.4%, up 3 of 4 days) is the
one left to check on a longer history.

## The winners themselves against our copy of them (Nov 19; the owner: "of course there are wallets that every day have a big winner that covers all the losses")

`m7_own_vs_copy.py` (`../out/m7_own_vs_copy.txt`): each wallet's OWN result on the same 4 days (its sales minus its
buys, tokens left at the last curve price). Together the 4,886 wallets made **+3,779 SOL themselves; our copy of them
−4,737 SOL**. **16 wallets were themselves up on every active day (3+) with a big winner (+100% on a coin) every day:
+503 SOL themselves, our copy −130 SOL (−7.6% a copy)**; e.g. 8YcbyX92 +112.5 SOL itself, our copy −1.43. Blind (39
wallets chosen on their own days 1-2): on days 3-4, 29 of 35 were themselves up again (+327 SOL), our copy −122 SOL
(−8.7% a copy). Their edge is real and lasting; it is not copyable. Who they are: 3 buy in the create block of 2-3
creators' coins (insiders); the others never buy at the launch and sell fast.

`m8_follow_sale.py` (`../out/m8_follow_sale.txt`): the same copies selling when THEY sell (else 600 s / tp 4): the 16
together −111 SOL (−6.5% a copy), only wallet 4 (+3.9%), TAB16RxX (+2.1%) and four wallets of 4-5 copies above zero;
blind −98 SOL (−7.0% a copy), 7 of 35 up. Wallet 4 remains the only wallet whose edge survives the copy.

## Learning from the winners instead of copying them (Nov 19; the owner: "not copying but on wallets we identify", "bots that always do the same thing")

- `m9_profile.py` (`../out/m9_profile.txt`): the six daily winners that do not buy at the launch (ARu4n5mF, AEdnzgqM,
  HLU8QbLd, HryU8vPB, FZU56d9i, 9dVSVwrU; 2,897 round trips, +179 SOL themselves) buy coins a median 0-152 s old,
  hold a median 5-261 s and win only 37-45% of their trips; their winners and losers look the same when they buy (age
  8 / 10 s, price 0.92 / 0.89 of the high so far, 14 / 15 buys in the last 30 s). The edge is being first, not the pick.
- `m10_scalp_rule.py` (`../out/m10_scalp_rule.txt`): their rule traded ourselves on every coin (enter 3-30 s after the
  launch with 0-20 buys in the last 30 s, out at 10-60 s unless up 0-10%, then tp / a 30% fall / 300 s): **0 of 540
  rules positive on days 1-2; on days 3-4 the median −15.7% a trade, the best −11.0%.**
- `m11_follow_flow.py` (`../out/m11_follow_flow.txt`): copy-bots follow wallets (a median 16 buys by others in the 10 s
  after a wallet's buy); a fast flip into them (in at the next slot, out 2-20 s later or at x1.2 / x1.5): on all 72,133
  buys −7.4% to −8.4% a trade (the 0.0345 SOL round trip is 6.4% of it: about −1% to −2% before costs); the wallets best
  on days 1-2 (by the flip or by followers) lose on days 3-4 in every setting (−0.2% to −6.9% a trade).
