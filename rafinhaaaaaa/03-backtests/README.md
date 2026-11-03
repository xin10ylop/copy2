# Backtests

Both outputs are verbatim in `out/`. Costs: 0.003 SOL a round trip (our live fees, wallet 4's copy) + the swap fee of each venue
our route crosses (pump curve 1.25% a side, PumpSwap and other pools about 0.30%, plus 0.30% for a hop through another
quote token). Our price: K trades behind each of its trades on the pool's fitted curve, with our own impact.

## 1. This week, Oct 25 00:09 → Nov 1 00:09 UTC (`out/this-week_oct25-nov01.txt`)

All 33 of its trades (no sampling). Rule and stake picked on days 1-4, scored on days 5-7.

| | Days 1-4 | Days 5-7 | Days 5-7 without the best 2 |
|---|---|---|---|
| Picked: its 5.1+ SOL buys, its size (≤ 3 SOL), 300 s, behind its sale; K = 2 | +14.14 (8) | +32.19 (9) | +3.39 |
| Same, K = 1 / 4 / 7 | +14.34 / +15.97 / +19.31 | +33.84 / +29.58 / +23.76 | +4.68 / +1.03 / −1.70 |
| Following its sales at 1 SOL, K = 2 | +0.14 (17) | +13.62 (16) | +1.58 |
| the long copy's wallet-4 rule (1.45+ SOL token-quoted, 2.0 / 0.8 / 1790 s, 1 SOL) | +0.45 (5) | −0.41 (1) | — |

## 2. Out of sample: the picked rule, unchanged, on Oct 4 00:09 → Oct 25 00:09 UTC (`out/out-of-sample_oct04-25.txt`)

The week before alone (Oct 18-25) had only 4 trades, so the rule was scored on its three earlier weeks together
(95 trades, 35 of them 5.1+ SOL buys; `analysis/final/runoos.sh` with `FIXRULE="buy>=5.10|None|None|300|its size"`).

| Landing | Total | Without the best 2 | A trade, median |
|---|---|---|---|
| K = 1 | +47.73 (35) | +23.10 | −0.484 |
| **K = 2** | **+37.67 (35)** | **+14.23** | −0.598 |
| K = 4 | +34.53 (35) | +10.40 | −0.825 |
| K = 7 | +33.52 (35) | +9.77 | −0.634 |

By week (K = 2): week 1 (Oct 4-11) +27.89 on 23, week 2 (Oct 11-18) +9.79 on 12, week 3 (Oct 18-25) no trades of
5.1+ SOL.

## 3. Where we land, in slots

K counts trades, but our speed is measured in slots: wallet 4's live copies (all 15 sends of Oct 28-29,
`../../03-strategy-A-long-copy/deploy-frankfurt.md` §6) landed 7 buys in its own slot and 8 in the next (47% / 53%; the first 7 alone were 5 / 2). On
this wallet's coins, K = 2 gives the nearest split, so the **K = 2 rows are the ones that match our live speed** and K = 1
is a step faster (`analysis/final/sim_g1.py`, "landing by slot" line). On wallet 4 itself the same slot match gives K = 4
while its real fills matched K = 2 (within 0.4%), so the slot match errs on the slow side:

| Trades behind | This week: its slot / next | Oct 4-25: its slot / next |
|---|---|---|
| K = 1 | 73% / 27% | 74% / 21% |
| **K = 2** | **58% / 36%** | **59% / 33%** |
| K = 4 | 30% / 64% | 40% / 37% |
| K = 7 | 19% / 44% | 19% / 40% |

The same check threw out a wallet that looked far better on paper (Bob_Benson, +193.63 out of sample 2 trades behind):
its coins are crowded right behind its buys, so our live split there is 4 to 7 trades behind, where it lost −69.71 and
−126.66.

## What the model is worth

The same pipeline replayed wallet 4's 16 live copies (Oct 28-29) trade by trade: the same exit on 16 of 16 at
the same second, +1.36 SOL at live costs against +1.345 live; our entry price within 0.4% (median) at the real landing.
Details: `../analysis/final/REFERENCE.md` and `../../03-strategy-A-long-copy/`.

## 4. A fixed stake, and how often its copies overlap (Nov 3)

The picked rule with the stake fixed instead of its size (`out/stakes_fixed_nov03.txt`, `sim_g1.py` with `FIXRULE`):

| Stake | Oct 4-25, K = 2 (K = 4) | without the best 2 | This week Oct 25 - Nov 1, K = 2 | without the best 2 |
|---|---|---|---|---|
| 0.5 SOL | +7.73 (+7.13) on 35 | +3.60 (+2.87) | +8.33 on 19 | +3.44 |
| **1 SOL** | **+14.91 (+13.74)** | **+6.75 (+5.33)** | **+16.45** | **+6.71** |
| 2 SOL | +27.44 (+25.23) | +11.47 (+8.78) | +31.93 | +12.59 |
| its size (≤ 3 SOL) | +37.67 (+34.53) | +14.23 (+10.40) | +46.45 | +17.65 |

Its copies rarely overlap: of its 37 buys of 5.1+ SOL over Oct 4-25, 3 had another inside our 300 s; this week 1 of 19;
never more than 2 open at once. One position at a time loses almost nothing.
