# Wallet 4 on fresh data: P3 = Oct 27 00:20 → Oct 28 14:54 UTC (Oct 28)

The 8-day study (`../../2026-10-27/h9long/`) re-run on wallet 4's transactions extended to Oct 28 14:54:39 UTC
(20,476 signatures, 19,981 landed). **P3** (Oct 27 00:20 UTC to the last row, 38.6 h) is a second out-of-sample period
after P1 (Oct 19-22, pick) and P2 (Oct 23 → Oct 27 00:20, score). Same costs everywhere: 0.0095 SOL a transaction, the
0.0155 SOL bias, its median round trip (5.1% other quotes), strict exits (`exits_pess.py`, `grid.py` model q + lift).
(+x) = without each period's best 2. Times UTC (Beirut = UTC+2).

## In short

1. **Wallet 4 still makes money: +82.00 SOL on the 546 coins it first bought in P3** (+84.55 on pump coins priced in
   other tokens). +54.60 of it came in one 6-hour block (Oct 28 00-06 UTC). Its balance rose 467.7 → 570.379 SOL. Its
   rows give +100.96 native SOL over P3, of which −3.21 is transfers (one 5.00 SOL out). The ledger's trading result
   over P3 is +87.90.
2. **Its rule changed. Confirmed on chain.** Of its 1.45+ SOL buys of other-quote coins (one buy, one sale), it sold
   **49% early in P3** (before 30 minutes, between 0.75x and 2.4x: neither its take profit, nor its stop, nor its
   timer), against 3.5% in P1 and 13.6% in P2. Only 39% ran to its 30-minute timer (67% before). Every early sale sold everything. The median hold was
   142 s, at a median 1.18x.
3. **The long copy as tested loses on P3:** −2.02 (−3.74) on 25 copies, at 4 open (P1 +6.73, P2 +11.13 unchanged). As
   the bot really trades (1.45 floor, its own route verdicts, plus the coins that graduated before wallet 4 sold) it
   comes out about flat: **−0.51 (−2.39) on 32 copies**, −0.34 with the 25% price limit. 13 of the 32 copies end
   behind its early sale. Every band, every stake and every take profit from 1.75x up lose on P3. On the same coins
   wallet 4 made +17.69.
4. **The backtest reproduces paper coin by coin, once its costs match paper's:** on the 21 closed paper coins, paper
   +2.4666, model **+2.8722 at paper's costs** (15 of 21 within 0.03 SOL) and **+1.5657 at the backtest's costs**. One
   gap matters: all of paper's profit came from 3 take profits on coins that graduated before wallet 4 sold (6y9aDagF,
   9UinFHHj, 3xwpPXRJ: +2.47). **No earlier backtest contained such coins.** `full_paths.py` needs a curve sale.
5. **Nothing was missed from Oct 28 13:14 to 14:54 UTC.** Wallet 4 made 3 buys of 1.45+ SOL in coins priced in another
   token; 9ENc9LwF (13:31:34, route B) was the only routable one.

## Run order

Setup (the other session's `SP/h9long` is untouched):
`mkdir -p $SP/fresh3 && cp -r $SP/h9long $SP/fresh3/h9long && ln -s $SP/{month,rivalpnl,live} $SP/fresh3/`.
The scripts are the h9long ones with `SP` pointed at `fresh3` and `per()` split into P1 / P2 / P3 (P3: blockTime ≥
1793060400). Every table prints P3. Further additions, all off by default: `ledger.py`/`groups.py` `T0` `T1` `SUFFIX`
(a windowed ledger); `behave.py`/`exitrule.py` `PER`; `exits_pess.py` `MIN_SOL` and cap 4; `grid.py` `CAP`, `NOT`,
`GRAD`, `FEE`/`BIAS`/`COSTO` and the modes `paper`, `grad`, `list`, `itsown`; `scale.py` routes coins after the old
data by `route_cls.py`. Check before regenerating: on the copied old files, `grid.py` gave +6.73 / +11.13 (cap 4) and
+5.03 / +9.63 (cap 3), `exits_pess.py` +39.53 / +15.27, and the old-window ledger +354.91. All as published.

```
W=H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg   # outputs in out/<name>.txt
python3 -I ledger.py $W; T1=1793060400 SUFFIX=_old python3 -I ledger.py $W; T0=1793060400 SUFFIX=_p3 python3 -I ledger.py $W
python3 -I groups.py $W; SUFFIX=_old python3 -I groups.py $W; python3 -I balance.py
python3 -I trips.py $W; python3 -I byquote.py $W; python3 -I exitrule.py $W
for p in P1 P2 P3; do PER=$p python3 -I exitrule.py $W; PER=$p python3 -I behave.py $W; done
python3 -I tprate.py $W; python3 -I early.py
python3 -I full_paths.py $W 1.45                                   # 847 trips, 52 new (49 in P3): minutes
MAX_SOL=1.5 KINDS="pump, other quote" python3 -I full_paths_band.py $W 0.8   # 181 new band trips
python3 -I grad.py; python3 -I grad_paths.py $W; python3 -I routecheck.py; python3 -I paper_early.py
python3 -I window.py "2026-10-28 13:14" "2026-10-28 14:55"
CAP=4 python3 -I grid.py cap|mix|quote|days|tp|stops|land|premium [q 1 1.45 9]; ROUTES=A|BC|E|ABCE ...
CAP=4 NOT=AvcwGFaF,2FSWwQwj GRAD=1 python3 -I grid.py <same> q 1 1.45 9                       # the bot's set
GRAD=1 python3 -I grid.py paper q 1 0 99; GRAD=1 COSTO=0.97515625 FEE=0.001605 BIAS=0 python3 -I grid.py paper q 1 0 99
MIN_SOL=1.5 python3 -I exits_pess.py 0 2.0 0.8 other -v; python3 -I band.py LO HI 1 q|v 1; python3 -I scale.py S q 1
```

## 1. Wallet 4 over P3 (`ledger.txt`, `ledger_old.txt`, `ledger_p3.txt`, `groups.txt`, `balance.txt`, `byquote.txt`)

| ledger | realized | open | sold from before | transfers | check: cash moved by trading; open positions at cost |
|---|---|---|---|---|---|
| Oct 19 → Oct 27 00:20 (old) | +357.94 | −3.04 | +78.62 | 257, +11.87 | +402.70; 26.55 |
| Oct 19 → Oct 28 14:54 (all) | +444.36 | −1.55 | +83.66 | 301, +8.66 | +506.67; 13.27 |
| P3 alone | +85.61 | −0.79 | +32.37 | 44, −3.21 | +103.97; 12.42 |

In each, realized + sold from before − open at cost exceeds the cash moved by 7.31 (old), 8.08 (all) and 1.59 (P3):
what token transfers and unpriced multi-token legs leave unexplained. The ledger moved by **+87.90** (442.81 −
354.91): +82.00 on the coins first bought in P3, +2.92 on P2 coins (pump coins +3.15, PumpSwap-only −0.22), and +2.98 on tokens first
bought in P1 (the quote tokens and xStocks it holds +1.73, PumpSwap-only +1.17, other +0.09), sold or re-marked in P3
(`groups.txt` against `groups_old.txt`).

| P3, by kind (first buy) | coins | net | (without best 2) |
|---|---|---|---|
| pump, priced in another token | 295 | **+84.55** | +61.35 |
| pump, SOL-priced | 212 | −3.72 | −7.84 |
| PumpSwap only | 36 | +1.31 | −1.30 |
| other / xStock | 3 | −0.13 | |
| **all** | **546** | **+82.00** | |

| 6-hour block (UTC) | Oct 27 00h (from 00:20) | 06h | 12h | 18h | Oct 28 00h | 06h | 12h (to 14:54) |
|---|---|---|---|---|---|---|---|
| coins | 78 | 54 | 80 | 143 | 98 | 50 | 43 |
| net | +1.91 | +3.80 | +6.87 | +15.01 | **+54.60** | +1.23 | −1.42 |
| (without best 2) | −0.14 | +1.20 | +1.92 | −1.03 | +36.11 | −1.03 | −3.62 |

By day: Oct 27 (from 00:20) +27.59 on 355 coins (+11.56), Oct 28 to 14:54 +54.40 on 191 (+35.91). By quote token (P3,
closed coins): via SOL +20.65 (104), PUMP +17.04 (33), H74CYmXg +12.04 (3), A7bd +9.97 (20), WBTC +4.57 (34: down from
275 coins in P2).

**Activity** (`balance.txt`): signatures / landed: P1 9,664 / 9,465 (2,366 landed a day), P2 7,613 / 7,379 (1,839),
P3 3,199 / 3,137 (1,952). Within P3: Oct 27 2,551 / 2,506, Oct 28 to 14:54 648 / 631 (a quieter day).

**Its balance**, 467.7 SOL (Oct 27, `01-who-it-is`) → 570.379 (Oct 28 ~15:00, getBalance): +102.68.

| over P3, from its rows | SOL |
|---|---|
| native SOL change, 00:20 → 14:54:39 | **+100.958** |
| transfers (ledger xfer list) | **−3.212**: one −5.0016 out (Oct 27 13:59, signed by it, program `9fhQBbum…`), 39 token-account closings +1.706 (rent back), 2 small in +0.090, 2 account openings −0.006 |
| native less transfers | +104.170 |
| wSOL / USD held | −0.629 / 0.00 |
| tokens held, sold down (at each token's last price) | about −15.27 (TTWO −3.25, DoGE −2.63, WXMR −2.45 ...) |
| **trading, cash view** | **about +88.3**, against the ledger's +87.90 |
| fees and tips paid | 5.209 |

No deposits: the 5.00 SOL left the wallet, and nothing came in but rent and dust. The rows give +100.96 where the two
balances give +102.68. The 1.72 gap is about the size of its native swings in the first two hours of P3 (−1.84 to
+1.55), so the time of the 467.7 reading probably explains it. The rows also give +413.56 before P3 where the docs say
+412.

## 2. Its rule on P3 (`exitrule_P*.txt`, `behave_P*.txt`, `tprate.txt`, `early.txt`, `grad.txt`)

Its one-buy one-sell trips on coins priced in another token, all sizes (exitrule.py, marginal multiple at its sale):

| | P1 | P2 | P3 |
|---|---|---|---|
| trips | 1,828 | 1,212 | 285 |
| held to its 30-minute timer (1,800-1,850 s) | 1,348 (74%) | 857 (71%) | **117 (41%)** |
| sold < 1,700 s at 2.5x or more (its take profit) | 202 (11%) | 89 (7.3%) | 16 (5.6%) |
| sold < 1,700 s at 0.65-0.7x (its stop) | 71 (3.9%) | 25 (2.1%) | 1 (0.4%) |
| sold < 1,700 s at 0.8-2.5x | 82 (4.5%) | 136 (11%) | **121 (42%)** |
| median slots to its first sale (behave.py) | 8,299 | 8,474 | **3,749** |

It also tips more: a 1.067M-lamport tip on its first buy from the 25th percentile in P3, from the 75th in P1 and P2.

**Its 1.45+ SOL buys of other-quote coins** (early.py; tp = ≥ 2.4x before 1,790 s, stop ≤ 0.75x, early = neither and
before 1,790 s):

| | P1 | P2 | P3 |
|---|---|---|---|
| trips | 398 | 294 | 49 |
| its take profit (= tprate.py's TP rate) | 87 (21.9%) | 32 (10.9%) | 6 (12.2%) |
| its stop | 30 (7.5%) | 24 (8.2%) | 0 |
| its timer | 267 (67.1%) | 198 (67.3%) | 19 (38.8%) |
| **early** | **14 (3.5%)** | **40 (13.6%)** | **24 (49.0%)** |
| routable only (A/B/C): early | 1 of 154 (0.6%) | 19 of 169 (11.2%) | **15 of 30 (50.0%)** |
| its net | +137.25 | +68.75 | +22.95 |
| graduated before its sale (not above, `grad.py`) | 2 | 2 | 5 |

**Paper's 40% (8 of 20) is confirmed on chain.** The backtest's own measure, copies that end behind its sale (`grid.py
mix`), was 1 of 135 in P1 and 8 of 136 in P2 (backtests.md §9). On P3 it is 11 of 25 (44%). On chain, its early-sale
rate on these buys was 3.5% in P1 and already 13.6% in P2.

The 24 early sales in P3: **all sold everything** (the tokens sold equal the tokens bought, every one). Held 7 / 24 / 142
/ 410 / 830 s (p10 / p25 / median / p75 / p90): 4 under 10 s, 6 at 10-60 s, 7 at 1-5 min, 5 at 5-15 min, 2 at
15-30 min. Multiple at the sale 0.83 / 0.95 / 1.18 / 1.38 / 1.95x: 9 at 0.75-1.0x, 10 at 1.0-1.5x, 4 at 1.5-2.0x, 1 at
2.0-2.4x. 12 of 24 won. Quotes: via SOL 12, WXMR 3, WBTC 3, one each of GRNDYDpq, A7bd, TTWO, SPCX, PUMP. Route
class A 12, B 2, C 1, E 9. (P2's 40: median 308 s, 1.10x, 23 won.)

All 9 of paper's `its_sell` exits are early sales on chain (`paper_early.txt`), at 0.83-1.38x after 4-1,360 s. So
are CkFH2smc (830 s, 1.18x) and EwsKTHxB (26 s, 0.95x); rAPE9kiT sold at 0.76x after 24 s (paper's stop fired). **6DS5ErwH and BPhav4G4 were not its stop** (paper-run.md §5
says "its stop firing in a crash"). It sold at 0.83x and 0.94x. The copies lost about 30% because they entered at
1.06x and 1.16x its price, and its own sale pushed the price to 0.76x and 0.85x: exit / entry 0.72 and 0.73.

## 3. The long copy on P3 (`grid_*.txt`, `exits_pess_*.txt`, `band.txt`, `scale.txt`)

As built: routable (ROUTES=ABC), 1 SOL, TP 2.0 / SL 0.8 / 1790 s, model q + lift, landing at its slot + 1.

| set | at most open | P1 | P2 | P3 |
|---|---|---|---|---|
| as published (1.5+ floor) | 3 | +5.03 (+3.06), 135 | +9.63 (+6.98), 136 | **−2.02 (−3.74), 25** |
| as published (1.5+ floor) | 4 | +6.73 (+4.76), 145 | +11.13 (+8.48), 145 | **−2.02 (−3.74), 25** |
| 1.45+ floor (the bot's) | 4 | +5.19 (+3.22), 153 | +12.27 (+9.62), 161 | −2.98 (−4.70), 30 |
| **the bot's set**: 1.45+, its route verdicts, graduated coins in | 3 | +3.49 (+1.53), 143 | +11.89 (+9.10), 153 | −0.51 (−2.39), 32 |
| **the bot's set** | 4 | +5.19 (+3.22), 153 | +13.49 (+10.70), 162 | **−0.51 (−2.39), 32** |
| the bot's set, 25% price limit | 4 | +4.51 (+2.54), 149 | +13.60 (+10.80), 158 | −0.34 (−2.23), 30 |
| 1.5+, its route verdicts, graduated coins in | 4 | +6.73 (+4.76), 145 | +12.35 (+9.56), 146 | +0.45 (−1.43), 27 |

The bot's set leaves out AvcwGFaF (route_cls says A; the bot said 3 hops, `routecheck.txt`: route_cls agrees with the
bot on 32 of 34 buys in its window). It adds 6y9aDagF, 9UinFHHj and 3xwpPXRJ (graduated, P3) and 3R1Kry3r (graduated,
P2). The cap never binds in P3. The rest at 4 open, 1.5+ floor (bot's set in brackets where it differs):

| what | P3 |
|---|---|
| `mix` | 11 of 25 copies end behind its early sale, −2.01 (bot's set: 13 of 32, −2.37); timer 9, −1.21; tp 3, +1.96 (bot's set: 6, +4.45); sl 2, −0.76 |
| by route | A: −1.81 on 21 (P1 +3.20, P2 +1.11); B/C: −0.21 on 4 (P1 +3.49, P2 +10.03). Bot's set: A −2.06 on 26; B/C +1.56 on 6 |
| `quote` | via SOL −1.81 (21), WBTC −0.21 (4) |
| `days` | Oct 27 −1.90 (14), Oct 28 −0.12 (11). Bot's set: −1.12 (20), +0.61 (12) |
| `tp` (sl 0.8) | 1.4x +0.31, 1.5x +0.18, 1.75x −1.97, 2.0x −2.02, 2.25x+ −2.45. Bot's set: 1.4x +1.19 (+0.02), 1.5x +1.14, 2.0x −0.51 |
| `stops` | 0.75 −2.02, 0.8 −2.02, 0.85 −1.90, 0.9 −1.79 |
| `land` | slot +1 −2.02, +2 −2.11, +3 −2.20, +5 −2.41, +10 −4.00 |
| `premium` | none −2.02, 0.25 −1.86 (23), 0.15 −1.24 (21), 0.10 −0.71 (18), 0.07 −0.00 (16) |
| wallet 4 on the same coins (`itsown`) | +7.04 against our −2.02. Bot's set: +17.69 against −0.51 (P1 +45.33 / +5.19, P2 +59.34 / +13.49) |

Only a 1.4-1.5x take profit is positive on P3 in both sets. In the bot's set it made −3.48 and +0.30 (−1.37) on P1,
and +5.04 and +6.68 on P2 against 2.0x's +13.49. It is a P3 pick, not a finding.

**Everything, routable or not** (`exits_pess.py 0 2.0 0.8`, its other-quote buys of 1.5+ SOL, no cap): P1 +39.53
(+35.92), 352; P2 +15.44 (+12.39), 247; **P3 +3.78 (+1.37), 42**. At 1.45+: P3 +2.45 (+0.04), 49. SOL-priced 1.5+: P3
1 copy −0.51. By UTC day: Oct 27 −0.34 (29, of which 3 before 00:20), Oct 28 +3.66 (16).

**Part B, the big buys we can't route** (`ROUTES=E`, as if we held every quote token): **P3 +4.85 (+2.65) on 17 copies**
(WXMR +0.65, PUMP +1.20, CARDS +1.13, GRNDYDpq +1.07, A7bd +0.86; SPCX −0.62). P2 is now +0.58 on 95 at 3 open
(published +0.43 on 94; one trip closed after 00:20). Beside the routable ones (ABCE, 4 open): P3 +2.83 (+0.63) on 42.
They recovered a little in P3, on 17 copies. Graduated class E coin AsY6oq86 (wallet 4 +11.02): model +0.61.

**Bands** (`band.py`, routable, no cap, q / v): 0.8-1.0 SOL −1.72 / −1.58 (33); 1.0-1.25 −1.35 / −1.27 (24); 1.25-1.45
−0.93 / −0.70 (22); 1.45-1.5 −0.96 / −0.99 (5); 1.5+ −2.02 / −2.01 (25). Every band loses on P3.
**Stakes** (`scale.py`, 3 open, q): 1 SOL −2.02, 1.5 −2.65, 2 −3.31, 3 −4.98, 5 −10.99. 1 SOL with a 5% haircut −2.81.

## 4. Paper against the model (`grid_paper.txt`, `grid_paper_papercosts.txt`, `grid_grad_*.txt`)

`grid.py paper`: `one()` as built, no cap, landing at its slot + 1 (paper filled there until `7184554`), GRAD=1. The
backtest's costs are 0.0095 SOL a transaction ×2 + the 0.0155 bias + its 5.13% round trip. Paper's costs (engine.rs
`exit()`, config defaults) are 1.25% curve fee each way, nothing for the pool leg, and 2 × (5,000 + 300,000 CU ×
2,000,000 µlamports / 10^6) + 2 tips of 1,000,000 lamports = 0.00321 SOL. Re-run with `COSTO=0.97515625 FEE=0.001605 BIAS=0`.
The entry agrees exactly: the model's slot + 1 entry is 1.518x and 1.321x its price on the 2 coins paper refused at
1.518x and 1.321x (`paper_early.txt`).

| # | bought UTC | coin | paper exit | paper | model | model at paper's costs | why they differ |
|---|---|---|---|---|---|---|---|
| 0 | 27 10:29 | PePEwjLD | time | −0.0230 | −0.0812 | −0.0233 | costs only |
| 1 | 27 16:14 | CkFH2smc | time | −0.1843 | −0.1429 | −0.0868 | it sold at 830 s; paper had no `its_sell` exit before `f52cee5` (18:08) |
| 2 | 27 18:25 | 6qUyTWv4 | time | −0.1277 | −0.1768 | −0.1215 | costs |
| 3 | 27 19:07 | 6y9aDagF | tp | +0.8377 | +0.9736 | +1.0609 | graduated; the model sells on the next slot's first trade, at 2.33x its price (paper's peak 2.04x) |
| 4 | 27 19:49 | BPhav4G4 | its_sell | −0.2958 | −0.3322 | −0.2813 | costs |
| 5 | 27 20:09 | ChonQdJ8 | its_sell | −0.1756 | −0.2240 | −0.1701 | costs |
| 6 | 27 21:02 | FUCKKmZZ | its_sell | −0.2468 | −0.2883 | −0.2362 | costs |
| 7 | 27 21:31 | 69iQjjf8 | tp | +0.9869 | +0.8051 | +0.8877 | both sell at 2.05-2.08x; the model's entry (1.024x) and sale state give 0.10 less; the journal paste has no fill prices to say which |
| 8 | 27 21:39 | rAPE9kiT | stop | −0.3124 | −0.3863 | −0.3370 | the model puts its own sale (0.76x, 24 s) first |
| 9 | 27 21:46 | 9UinFHHj | tp | +0.8769 | +0.7930 | +0.8753 | graduated; same |
| 10 | 27 23:10 | CogafBTp | time | −0.0973 | −0.1479 | −0.0919 | costs |
| 11 | 28 00:24 | HytpiyuR | its_sell | +0.1038 | +0.0356 | +0.0967 | costs |
| 12 | 28 01:04 | 6DS5ErwH | its_sell | −0.3031 | −0.3404 | −0.2898 | costs |
| 13 | 28 01:10 | 3xwpPXRJ | tp | +0.7511 | +0.7309 | +0.8114 | graduated; the model sells at 2.12x (paper's peak 2.01x) |
| 14 | 28 01:15 | 4BvM3fKH | time | −0.2238 | −0.2665 | −0.2138 | costs |
| 15 | 28 01:27 | 5f45YWuV | tp | +0.8557 | +0.9086 | +0.9941 | its 2.53x sale lands within a slot; the model sells on the state it leaves, 2.24x (paper's peak 2.02x) |
| 16 | 28 01:31 | DJXThGNt | its_sell | −0.0623 | −0.1177 | −0.0609 | costs |
| 17 | 28 02:23 | 5a7nDZcR | refused 1.518x | 0 | +0.2432 | +0.3101 | refused by the 25% limit in both |
| 18 | 28 02:27 | w9XZuzKe | time | +0.0087 | −0.0795 | −0.0216 | the time-exit fill |
| 19 | 28 02:41 | 9hhXcHT9 | its_sell | +0.1424 | +0.0692 | +0.1313 | costs |
| 20 | 28 06:49 | 3j9ex53k | its_sell | +0.1429 | +0.0709 | +0.1330 | costs |
| 21 | 28 08:40 | EwsKTHxB | refused 1.321x | 0 | −0.4049 | −0.3561 | refused by the 25% limit in both |
| 22 | 28 13:31 | 9ENc9LwF | its_sell | −0.1874 | −0.2374 | −0.1839 | costs |
| | | **21 closed** | | **+2.4666** | **+1.5657** | **+2.8722** | |

- **Exits:** the model's exit matches paper's on every coin but CkFH2smc. **15 of 21 agree within 0.03 SOL** at paper's
  costs. The backtest's costs take 1.31 SOL over 21 trades (0.062 a trade: 0.031 fixed and the rest the 5.1% round
  trip against paper's 2.5%).
- **Where the model is too kind:** take profits on frenzy coins, where it sells on the next slot's trade after 2.0x and
  the price has run on (#3 at 2.33x, #15 2.24x, #13 2.12x: +0.22, +0.14, +0.06 over paper; #7 −0.10 the other way).
  Paper is itself optimistic there: real fills from Ohio land later. Entry and fill multiples per coin are in
  `grid_paper*.txt` ("we buy at ..., sell at ...").
- **The gap that matters:** the 3 graduated coins made +2.4657 of paper's +2.4666. Paper's other 18 coins sum to about
  zero. No backtest before this one included a coin that graduated before wallet 4 sold. In P3 there are 5 such
  1.45+ buys (3 routable by the bot); in P1/P2 there were 4 (3R1Kry3r routable: model +1.22). On all 5 that route_cls
  calls routable, our 2.0x fired on the curve before graduation (`grid_grad_lift.txt`); on 2 class E ones the curve never
  reached 2.0x after its buy.
- The model's P3 (bot's set, 32 copies, −0.51) = 6 copies before paper's first trade (Oct 27 03:47-08:49, −1.20) + 3
  while no paper ran (14:56-15:55, after fra1 stopped and before Ohio started, −0.71) + the 23 paper coins (+1.40,
  `grid_list_bot145.txt`).

## 5. Oct 28 13:14 → 14:54 UTC (15:14 → 16:54 Beirut, `window.txt`)

10 curve buys of coins priced in another token (and 18 SOL-priced). Three were 1.45+ SOL (none between 1.2 and 1.45):

| UTC | coin | its SOL | route | paid with |
|---|---|---|---|---|
| 13:26:38 | DNiG4gF1 | 1.501 | E | PUMP (unpriced for the bot) |
| **13:31:34** | **9ENc9LwF** | 1.509 | **B** (WBTC multihop) | WBTC: **paper #22** |
| 14:07:41 | 4iEirfYp | 1.478 | E | an xStock (XsaBXg8d) |

9ENc9LwF was the only routable one, and paper entered it.

## 6. Where our buy lands inside its slot (`land_pos.py`, `out/land_pos.txt`; Oct 28 evening)

`grid.py land` moves our fill by whole slots (slot +1 is what paper and every backtest assume). `land_pos.py` moves it
by **block position inside wallet 4's own slot**: our buy fills on the state after the last trade at block index
≤ its index + K (`("pos", K)`; the path rows carry the index, `r[1]`), so K = 0 is the trade right behind its buy and
K = 600 is the end of its slot (= `land` 0). Same model, costs and cap as §3 (q + lift, CAP=4, 1.45-9 SOL, routable).

| our buy fills | P1 (Oct 19-22) | P2 (Oct 23-27) | P3 (Oct 27-28) | bot's set P3 |
|---|---|---|---|---|
| right behind its buy (K = 0; the ceiling) | +17.28 (+15.05) | +18.57 (+16.14) | −0.47 (−2.36) | +2.44 (+0.27) |
| 30 positions behind | +14.17 (+11.94) | +16.21 (+13.33) | −0.78 | +2.12 |
| 60 positions behind | +12.70 (+10.47) | +15.01 (+12.19) | −0.94 | +1.96 |
| 100 positions behind | +10.82 (+8.59) | +14.51 (+11.70) | −1.03 | +1.87 |
| 130 positions behind | +10.13 (+7.96) | +14.20 (+11.38) | −1.10 | +1.80 |
| 300 positions behind | +7.96 (+5.98) | +13.94 (+11.13) | −1.37 | +1.54 |
| end of its slot (K = 600 = `land` 0) | +7.70 (+5.72) | +13.92 (+11.10) | −1.41 | +1.36 |
| **next slot (`land` 1: paper and the backtests)** | **+5.19 (+3.22)** | **+12.27 (+9.62)** | **−2.98 (−4.70)** | **−0.51 (−2.39)** |
| 2 slots after | +4.94 | +11.51 | −3.09 | −0.56 |

(+x) = without the period's best 2. The bot's set = `NOT=AvcwGFaF,2FSWwQwj GRAD=1` (its P1 is the same, its P2
+13.49 → +15.73 at 100 positions → +19.81 at K = 0).

- **The slot matters more than any setting in §3.** From the next slot to 100-130 positions behind it in its own slot,
  P1 about doubles and P2 gains 2 SOL; over the 8 days that is about **+1 SOL a day at 4 open** (+17.5 → +24.5-25.3).
  The trades in those positions are the frenzy that follows its buy; filling before them is the whole gain.
- **The ceiling (right behind its buy) is +36 over the 8 days against +17.5**, but nobody fills there: the other
  copiers race for the same positions.
- **What a pre-execution (shred) trigger adds**, if it moves us from about 100-130 positions behind to 60-100 (the
  figure claimed for another bot's Deshred feed, about 6 ms or 30 positions earlier): about +0.5-1.9 on P1 and
  +0.3-0.5 on P2 per period, roughly **+0.2 SOL a day**. Worth having once the same-slot landing exists, not before.
- P3 stays negative in every row but the ceiling (the bot's set is positive from 300 positions in): a better landing
  does not undo its early sales.
- Where we really land is measured by the journal's `long fill ... paid X (vs its price +N%)` and the fill slot in
  the 0.1 SOL test (plan §6 step 2); paper only shows `seen at its slot +N`.

**Under the live bot's conditions** (`land_cond.py`, `out/land_cond.txt`; the bot's set, following its early sell as
in every row above; the live bot holds instead, which `more/` D-v puts at −0.51 → +3.10 on P3 at slot +1):

| stake × cap, costs | landing | P1 | P2 | P3 |
|---|---|---|---|---|
| 1 SOL × 4, the backtest's costs (0.0095 a transaction, 0.0155 bias) | slot +1 (published) | +5.19 (+3.22) | +13.49 (+10.70) | **−0.51 (−2.39)** |
| same | its slot, 100 positions behind | +10.82 (+8.59) | +15.73 (+12.92) | +1.87 (−0.30) |
| **0.1 SOL × 1, the live costs** (0.0014 a transaction, no bias) | slot +1 | +0.26 (+0.06) | +0.54 (+0.31) | −0.02 (−0.21) |
| same | its slot, 100 / 30 positions behind | +0.63 / +0.83 | +0.67 / +0.77 | **+0.17 / +0.19** (−0.06 / −0.04) |
| 0.3 SOL × 3, the live costs | its slot, 100 / 30 positions | +4.16 / +5.07 | +5.73 / +6.18 | +0.91 / +0.98 (+0.22 / +0.30) |
| 1 SOL × 3, the live costs | slot +1 | +8.03 (+6.00) | +16.75 (+13.89) | +0.51 (−1.44) |
| same | its slot, 100 / 30 positions | +13.51 / +16.41 | +18.71 / +20.15 | +2.89 / +3.13 (+0.66 / +0.90) |

The first evening live (Oct 28 18:34-21:32 UTC, 0.1 SOL × 1, 4 of 6 buys in its slot 5-7 trades behind its buy) made
+0.35 on 5 closed: the model's P3 pace at that size is about +0.1 a day, so the evening was a hot stretch, in the
direction the model gives once the landing and the costs are the real ones. The published −0.51 is the same data with
the buy a slot later, the costs 7 times tonight's, and selling behind its early sales.

## Notes

- `behave.py` (the original too) prints its first-buy SOL with a minus sign, so its size buckets put every coin under
  0.6 SOL. Size is taken from `tprate.py` / `early.py` here.
- P3 is 38.6 hours and 25-32 copies. One more coin like 6y9aDagF turns it positive. The rule-change finding (early
  sales 49%, timer 39%) rests on 285 trips (49 of 1.45+ SOL).
- Long paths are sampled (at most 40 transactions a trip: the first 8, the last 4, an even sample between), so a trigger
  between samples fires late: 27 of the 49 P3 paths are sampled. The graduated coins' paths are complete to the
  migration (`grad_paths.txt`; AsY6oq86 cut at 600 of 628).
- Paper's costs here are the committed defaults (`crates/rugsnipe-long/src/config.rs`, `engine.rs` `exit()` at HEAD);
  the box's `long.toml` may differ.
