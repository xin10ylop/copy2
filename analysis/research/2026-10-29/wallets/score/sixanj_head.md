## 6anjqMeW in full (`out/6anjqMeW_*.txt`)

**What it buys.** 0.5 SOL of a coin priced in another token (p10 0.25, p90 1.0; its 1.0 SOL buys stopped after P1:
518 coins at 0.9-1.2 SOL in P1, 7 in P2, 5 in P3, `tprate.txt`), never 1.45+. At 0.45+ SOL: 2,140 / 1,072 / 700
coins (535 / 267 / 361 a day), 74% at the create slot or the next (86% / 57% / 63%), and as many SOL-priced coins beside
them (1,418 / 1,530 / 1,113). Its quotes: PUMP 552, CARDS 400, SPCX 361, xStocks 293, DJTu 186, TTWO 183, WBTC 126 of
3,912. Only 19% (746) are routable for our bot, against wallet 4's 48% at 1.45+.

**Its rule** (`exitrule.txt`, `behave_P*.txt`, `early_0.45.txt`). No take profit and no 30-minute timer:

- One-sale coins (3,333, −83.27): held under 5 s (1,400 of 3,332 trips), or to fixed timers of 240 s (301), 480 s
  (197) and 740 s (182) (10-s bins); 1% reach 1,790 s; sold at a median 0.99x. The timers are mostly P1 (its early
  sales held a median 240 s in P1, 2 s in P2, 3 s in P3).
- Coins sold in 2-4 parts (1,101, +131.65): the first part (10-50% of its tokens) 0-4 s after its buy at a median
  1.22-1.28x, the rest a median 5-10 s after its buy; the best part at a median 1.26-1.40x.
- On its 0.45+ one-sale trips the early-sale rate (before 1,790 s, between 0.75x and 2.4x) is 92.0% / 94.6% / 91.6%.

| | one buy, one sale | one buy, 2+ sales | all its tokens (ledger, without the best 2) |
|---|---|---|---|
| P1 Oct 19-22 | 1,800 coins, −16.90 | 395, +36.27 | +32.92 (+26.05) on 4,047 |
| P2 Oct 23-27 | 996, −42.51 | 444, +60.84 | +33.09 (+27.42) on 3,287 |
| P3 Oct 27-28 | 537, −23.86 | 262, +34.54 | +16.54 (+13.36) on 2,200 |

Failed: 2,551 of 30,413 signatures, 8.5% of its own (16.5% in P1, 1.8-1.9% after). The ledger's check: cash moved by
trading +83.15 against +82.39 realized.
