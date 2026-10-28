# Strategy A: every backtest

In short: the rule was picked on **P1 = Oct 19-22** and scored on **P2 = Oct 23-27** (out of sample), with harsh costs
and wallet 4's own sale placed ahead of ours whenever the two are within a slot. On the coins the bot can route, at 1 SOL
and 3 open: **P1 +5.03, P2 +9.63** (4 open: **+6.73 / +11.13**). TP 2.0x is the best take profit in both periods. 1 SOL
is the smallest stake that clears the fixed costs. Every band of its smaller buys loses or flips. Landing late costs
about 3-5% of the profit per slot. Numbers in brackets are without each period's best 2 copies.

All scripts are in `analysis/research/2026-10-27/h9long/` (read its README for the run order). They read the fetched
data from the session scratchpad (`SP`); the data is in `data/datasets/` (see CLAUDE.md "Datasets").

## 1. Method

- **Data:** wallet 4's every signature since Oct 19 00:00 UTC (17,278; 16,845 landed: `sigs.py`, `pull.py`), its
  ledger (`ledger.py`), its round trips (`trips.py`), and the curve path of each copied coin from its buy to its sell
  (`full_paths.py`, `full_paths_band.py`; long paths sampled).
- **Costs everywhere:** its own median round-trip cost on the curve and routes (2.9% SOL-quoted coins, 5.1% other
  quotes); **0.0095 SOL a transaction** (worst case); the **0.0155 SOL model bias** off every fill (real fills came out
  that much worse than the replay on 35 real copies, `../../2026-10-26/h9/calib.py`). About **0.0345 SOL fixed a
  trade** in all.
- **Fills:** at the end of its slot or the next.
- **Exits, two models:**
  - `exits.py` fills a take profit on the trade that fired it and never puts its own sell ahead of ours (optimistic);
  - **`exits_pess.py`** (used for every number below unless stated): a TP / SL fired within a slot of its own sell is
    filled on the state its sell leaves; otherwise on the next trade of the path. A rule that never fired sells before
    its 30-minute sell, or after it when its TP / SL jumped past ours in one trade. `HAIR` takes a further share off every
    TP / SL fill (other copiers ahead).
- **Price models for our own size** (`scale.py`, `grid.py`): **v** shifts the recorded path by our tokens (later buyers
  trade fixed token amounts); **q** (cautious) shifts it by our quote (copy bots spend fixed SOL) and lets its own exits
  fire on the price with our tokens in.
- **Open-position cap:** copies in buy order, a copy skipped while the cap is full.

## 2. The rule on all its 1.5-SOL buys (TP 2.0 / SL 0.8 / 1790 s)

| coins | P1 Oct 19-22 | P2 Oct 23-27 | P2, 5% haircut |
|---|---|---|---|
| SOL-priced | −11.12 (73 copies) | −2.34 (31) | |
| **other quote tokens** | **+39.53 (+35.92), 352** | **+15.27 (+12.22), 246** | +8.53 (+5.74) |

- By day: +11.7 +10.0 +0.1 +17.7 / +2.1 +5.8 +6.6 +1.3. P2 rests on WBTC-priced coins (+10.9 on 83).
- **Its own 2.45x as our TP:** our TP lands after its sell on 83 of 126 TP trips: P2 +5.0 (+1.6), negative with the
  5% haircut. At 2.0x only 8-10 land after it.
- Capital, P2: 1 open +4.69 (+2.03), 2 open +7.50 (+4.84), 3 open +10.48 (+7.43), 5 open +15.26 (+12.21).
- Copying every buy, mirroring its sell, or scalping the copiers behind it all lose (first pass, `sim1.py`, `sim2.py`).

## 3. What the bot can route (`routable.json`, `route_cls.py`)

The bot routes through pump's own programs only. A direct curve buy is routable when its quote is a float or has a
canonical PumpSwap pool against wSOL or WBTC. 598 qualifying buys:

| buys | count | P1 | P2 | P2, at most 3 open |
|---|---|---|---|---|
| **routable (what is built)** | 293 | +10.97 (+8.51) | **+12.21 (+9.34)** | **+11.03 (+8.16)** |
| of which multihop from wSOL (route class A) | 179 | +5.32 | +1.08 | |
| of which multihop from WBTC, a float (route class B) | 91 | +2.35 | +10.02 (+7.64) | +8.89 |
| of which curve quoted in WBTC (route class C) | 20 | +1.71 | +1.12 | |
| not routable without Jupiter (direct buys of other quotes, PUMP floats, 3+ hops) | 305 | +28.57 | +3.06 (+0.41) | +1.44 |

The routable part holds in both periods; the rest made its money in P1 and is about zero in P2. `route_cls.py` rebuilt
routability from the transaction rows: 593 of 598 agree with `routable.json`.

## 4. Its smaller buys (`band.py`): the 1.45 floor

Routable only, no cap, cautious model q / path model v:

| its buy | copies | P1 (q / v) | P2 (q / v) |
|---|---|---|---|
| 0.8-1.0 SOL | 199 | −1.40 / −0.49 | −2.39 / −1.62 |
| 1.0-1.25 SOL | 162 | +5.62 / +6.97 | −6.46 / −6.32 |
| 1.25-1.45 SOL | 56 | −1.84 / −1.82 | −0.92 / −0.66 |
| 1.45-1.5 SOL | 28 | −1.54 / −1.58 | +0.54 / +0.78 |
| **1.5+ SOL** | 295 | **+6.69 / +9.11** | **+10.43 / +12.91** |

A stake of two thirds of its buy instead of 1 SOL changes none of the signs. The 1.45-1.5 slice is about −0.03 SOL a
copy on 28, too few to move the floor.

## 5. Stake (`scale.py`): 1 SOL, not less

Routable, TP 2.0 / SL 0.8 / 1790 s, its sell ahead of ours within a slot, at most 3 open, the cautious model:

| stake | P1 | P2 | P2, 5% haircut |
|---|---|---|---|
| 1 SOL | +6.74 (+4.77) | +8.84 (+6.19) | +5.90 (+3.48) |
| 1.5 SOL | +10.92 (+8.04) | +14.42 (+10.51) | |
| 2 SOL | +14.30 (+10.56) | +18.98 (+13.87) | +13.25 (+8.59) |
| 3 SOL | +18.66 (+13.32) | +26.05 (+18.70) | +17.67 (+11.00) |
| 5 SOL | +3.86 (−3.33) | +25.58 (+15.62) | |

- `scale.py` and `grid.py` (sections 6-8) differ slightly in their fill details, so compare numbers within one table.
- Up to 2-3 SOL the result grows about with the stake: the fixed costs thin out, and our own impact eats part. At 5 SOL,
  P1 is negative without its best 2: our own lift makes its 2.5x fire earlier and ahead of our 2.0x (39 trips at 1 SOL,
  55 at 3, 65 at 5).
- The path model v is far rosier (5 SOL: +96 on P2), because there later buyers pay more for the same tokens. It isn't
  used for decisions.
- **Below 1 SOL:** the fixed costs (about 0.0345 SOL a trade) are about 3.5% of 1 SOL, but the whole edge at 0.5 SOL
  (P2 about 0 without the best 2), and about a third of a 0.1 SOL stake.
- Price lift of our buy right behind its buy (293 routable coins): its own 1.5 SOL buy lifts the price about 10%. Our
  1 SOL about 6% more (8.5% at 2x).

## 6. Positions open at once (`grid.py cap`): 4

1 SOL, 1.5+ SOL buys, routable, cautious model:

| at most open | P1 | P2 | SOL needed |
|---|---|---|---|
| 1 | +2.59 | +3.51 | 1 |
| 2 | +6.50 | +8.11 | 2 |
| 3 | +5.03 | +9.63 | 3 |
| **4 (set)** | **+6.73** | **+11.13** | about 4.1 with fees |
| 5 | +6.69 | +10.86 | 5 |
| no cap | +6.69 | +10.43 (146 and 149 copies against 135 and 136 at 3) | |

## 7. Take profit (`grid.py tp`): 2.0x

Stop 0.8, 1790 s, at most 3 open (the 0.9 stop came out worse at almost every take profit):

| take profit | P1 | P2 | won (P1) |
|---|---|---|---|
| 1.1x | −7.76 | −4.66 | 45 of 144 |
| 1.2x | −6.17 | −0.25 | 59 of 142 |
| 1.3x | −4.21 | +1.89 | 55 of 140 |
| 1.4x | −2.90 | +5.85 | 48 of 139 |
| 1.5x | +0.57 | +5.61 | 49 of 138 |
| 1.6x | +0.48 | +7.18 | 40 of 135 |
| 1.75x | +3.72 | +8.59 | 40 of 135 |
| **2.0x (set)** | **+5.03** | **+9.63** | 37 of 135 |
| 2.25x | +4.15 | +9.21 | 34 of 135 |
| 2.5x or higher | −0.49 | +4.05 | 32 of 135 |

- A small take profit is mostly eaten by the round trip (the curve fees plus about 0.0345 SOL fixed), wins only a little
  more often, and cuts off the runs that pay for the losers.
- 2.5x and above equal no take profit: wallet 4's own 2.5x sale lands first and we sell after it.

## 8. Landing delay

1 SOL, at most 3 open:

| our buy lands | P1 | P2 | profit lost |
|---|---|---|---|
| 1 slot after wallet 4 (what Frankfurt got) | +5.03 | +9.63 | |
| 2 slots after | +4.88 | +9.02 | 3-6% |
| 3 slots after | +4.58 | +8.80 | about 9% |
| 5 slots after | +4.15 | +7.69 | about 20% |
| 10 slots after | +1.80 | +4.63 | about half (P1 negative without its best 2) |

## 9. The rest of the settings (`grid.py`, at most 3 open)

- **Exits:** the built exits rank 5 of 129 on P1 under q. Trailing stops are never in the top 15. A 0.85 stop helps the
  SOL routes only.
- **Entry premium:** a tighter one does nothing on P1.
- **By route:** WBTC-routed copies make about +0.12 SOL a copy in both periods (28 and 76 copies), SOL-routed about
  +0.02 (110, 63). The WBTC profit comes on 3 of the 8 days.
- **By day (q):** +3.1 +1.4 +1.0 −0.5 / −1.0 +5.8 +3.5 +1.4. Wallet 4's own result on the same coins was positive every
  day (+82 against our +17 over the 8 days).
- **Its early sell** (`grid.py mix`, `KIND` per exit): the price path ends at its sale, so a copy sells right behind it.
  That happens on 1 of 135 copies in P1 and 8 of 136 in P2; those copies average about −0.14 SOL.

## 10. The big buys we can't route (part B; `ROUTES=E grid.py`)

Copied as if we held every token they're paid in (no price risk on the token counted): P1 +24.63 on 189 copies, P2
+0.43 on 94 (PUMP −1.32). With them beside the routable ones (`ROUTES=ABCE`, 3 open), P2 falls to +7.38 against +9.63:
they take the open slots. Left out.

## 11. Fees: what wallet 4 pays and what we'd pay

- Wallet 4 on these buys: a median 0.0071 SOL fee (10%: 0.0035, 90%: 0.0134), plus a 0.00107 SOL tip on 40-55% of them.
  On its sells a median 0.00001 SOL, no tip.
- Ours as configured: buy about 0.0016 SOL (0.001 Nozomi tip + 0.0006 priority), sell about 0.0013; about 0.003 a round
  trip. The backtest charged 0.0095 a transaction. If our cheaper fee lands fine, real costs come out about 0.016 SOL a
  trade below the backtest's, roughly +2 SOL per 135 trades. **Not confirmed**: it needs the real test (going-live.md).
- We don't need to beat wallet 4, only follow it. Landing 2 slots later costs about 0.003-0.006 SOL a trade, about what
  its 0.007 fee would cost us to land faster.

## Sources

- `analysis/research/2026-10-27/h9long/README.md` and the scripts named in each section.
- `docs/20-long-copy.md` §2.
- Session analyses of Oct 27-28 (landing delay, fees, cap, TP sweep), each committed to the h9long README:
  `252e561` (TP), `7cc6f5b` (cap and fees), `8845447` (part B), `611dbcb` and `553ed1d` (bands), `435723f` (stake),
  `3cbd0d0` (the grid).
