# Taking the skipped trades, and copying better (Oct 28)

What the long copy skips (part B "paid in an unpriced token", "no anchor reaches", "route of 3 hops", part C) and what
would make the copy of part A better, tested the repo's way: picked on **P1** (Oct 19-22), scored on **P2** (Oct 23 →
Oct 27 00:20), and re-scored on **P3** (Oct 27 00:20 → Oct 28 14:54, 38.6 h) from the other session's re-run
(`../fresh/`, `SP/fresh3/h9long`). grid.py's model everywhere (`sim.py`: the cautious price model q + lift, its sale
ahead of ours within a slot, 0.0095 SOL a transaction, the 0.0155 SOL bias, its 5.1% round trip), at most 4 open,
(+x) = without each period's best 2. Times UTC.

## In short

1. **Part B can't be routed through pump's programs, priced or not.** `multi_hop_swap` takes canonical pump pools only
   (simulated on mainnet: `OnlyPumpPools`), and no part-B quote token (PUMP, CARDS, TTWO, USDC, ZEC, XMR, SPCX, the
   xStocks) has a canonical pool against wSOL or WBTC. Pricing them in `oracle.rs` would only change the skip's wording.
   Holding them as floats: PUMP fails out of sample, CARDS stopped; ZEC is the one float positive beside part A in all
   three periods, on few wins.
2. **3 hops fit** in a v0 transaction with pump's own lookup table (about 1,027 bytes against 1,270 legacy), but its 3-hop
   buys from wSOL or WBTC are rare (7 in 9.6 days) and add about +0.1 SOL a day.
3. **Part C stays out** (0.7x stakes, WBTC routes only: P2 −5.98).
4. **For part A the big open question is its early sell.** Ignoring it and keeping our own exits: paper's 9 copies
   +1.97 against −1.36 (model), the bot's set on P3 **+3.10 (+1.02) against −0.51 (−2.39)**, but P2 −0.25 and P1 −0.04.
   Partial exits, entry filters, the stop by route, a looser entry limit: none passes out of sample. Speed is worth up to
   +0.4-1.2 SOL a day. More SOL on WBTC routes earns more per SOL staked in P1 and P2.
5. **The bot as built is not grid.py's set:** it takes the 1.45-1.5 band and none of the 3-hop routes grid.py counts. Its
   own set (with the coins that graduated before wallet 4 sold) makes **+5.44 (+3.47) / +12.79 (+10.00) / −0.51 (−2.39)**
   at 4 open (P1 / P2 / P3), against grid.py's +6.73 / +11.13 / −2.02.

## What to change, ranked by SOL a day (P1 / P2 / P3 a day; the bot's set, at most 4 open, unless said)

P1 = 4.0 days, P2 = 4.0, P3 = 1.61. (+x) = the period's total without its best 2.

| # | change | SOL a day P1 / P2 / P3 | evidence: the bot's set P1 / P2 / P3 | code | risk |
|---|---|---|---|---|---|
| 1 | **don't sell behind its early sell** (paper first) | −0.01 / −0.06 / **+2.24** | +5.44 → +5.40 (+3.43), +12.79 → +12.54 (+9.75), **−0.51 → +3.10 (+1.02)**; paper's 9: +3.34 | `config.rs` `follow_its_sell` (default true), read in `engine.rs`'s `Seen::Sell` branch; journal the price it would have sold at; engine test; docs/20 §3 | P2 says the opposite (small); P3 rests on 4 take profits on frenzy coins, where the model's fill is kind |
| 2 | **land faster** (measure first) | +0.54 / +0.41 / +1.16 (upper bound) | land 0: +7.58 (+5.60), +14.44 (+11.62), +1.36 (−0.56); each slot past +1 costs 0.2-0.6 a period | none in the strategy: deploy `7184554`, read `seen at its slot +N`, then the feed / sender | none; land 0 can't be reached in practice |
| 3 | **more SOL on WBTC routes** (2.0 on WBTC, 1.0 on wSOL), when scaling | +0.67 / +3.06 / +0.95 (more capital) | +8.13 (+4.64), +25.07 (+20.60), +1.02 (−2.36); per SOL staked (grid's set) +5.80% / +9.75% against +4.64% / +7.68% | a float stake in `config.rs`, used in `engine.rs::on_trigger` when `plan.anchor` is a float; engine test | a WBTC float of 8 SOL at 4 open; wallet 4's WBTC buys fell in P3 (6 copies) |
| 4 | **a ZEC float** (paper trial) | +0.33 / +0.34 / +0.53 (grid's set) | beside part A: +8.04 (+6.05), +12.48 (+9.76), −1.16 (−3.05) against +6.73, +11.13, −2.02; alone −0.53 / −1.05 without its best 2 | config only: ZEC (`A7bdiYdS...`) in `floats` | a few wins carry it; ZEC's price (−7.7% worst fall in 10 days) |
| 5 | **3-hop routes** (v0 + pump's lookup table) | −0.06 / +0.17 / +0.34 | +5.19 (+3.22), +13.49 (+10.70), +0.03 (−1.85) | v0 compile in `rugsnipe-tx`, `txb.rs::sign` with pump's table, `route.rs` `MAX_OUR_HOPS = 3`; tests | a new transaction format on the send path |
| - | stop 0.9 on WBTC routes | +0.06 / +0.06 / 0 | +5.70, +13.04, −0.51 | `config.rs` stop per anchor | not worth a change |

**Don't:** route part B through pools (the program refuses them); float PUMP, CARDS or TTWO; copy part C; partial exits
or take-profit floors; entry filters (age, progress, hour, its open positions, frenzy); a looser or tighter entry limit.

## A. The "unpriced" skips: part B (`quotes.py`, `routes.py`, `skips.py`, `pools.py`, `btable.py`, `sim_pool.py`, `partb.py`, `floats.py`)

**Answer: no route exists through pump's programs for any part-B quote token, priced or not.** `multi_hop_swap` takes
only canonical pump pools, and none of these tokens has one. Leave B out. The one float worth a paper trial is ZEC
(below), and it rests on few wins.

**What the paper run skipped** (`skips.py`, the journal's 73 skips in 21.0 h matched to its transactions):

| journal reason | skips | of them 1.45+ SOL | paid in (1.45+ only) |
|---|---|---|---|
| paid in an unpriced token | 68 | 10 | PUMP 3, XsDoVfqe (an xStock) 3, ZEC 1, TTWO 1, XMR 1, SPCX 1 |
| no anchor reaches ... | 3 | 3 | ZEC, 6GmAFSYs, XMR (a Jupiter leg from SOL in its transaction) |
| route of 3 hops | 2 | 2 | wSOL (AvcwGFaF, 2FSWwQwj) |

58 of the 68 "unpriced" skips are its small buys: `engine.rs` returns on `sol_value = None` before the `min_sol` check, so
every size is journaled. Over the same 21 h it made 21 paper buys (2 refused at the price limit): for every 3 big buys
it takes, it skips about 2.

**Why it skips.** `detect.rs` values its buy from wrapped SOL into its route, or from SOL it sent Jupiter in the same
transaction, or from a held token at the oracle's price. Its PUMP, ZEC, SPCX and xStock buys are paid from tokens it
already holds, and the oracle prices only the floats (WBTC), so `sol_value` is `None`. When it bought the quote through
Jupiter in the same transaction (TTWO, XMR, most xStocks) the buy is valued, and then `route::plan` looks for the
canonical pool `["pool", 0, pool_authority(quote), quote, wSOL|WBTC]` and finds none ("no anchor reaches").

**Would pricing them help? No.** Per pay token (`btable.py`; its class-E buys of 1.45+ SOL, Oct 19-27; pools now, Oct 28):

| paid in | buys | P1 its net | P2 its net | its route | wSOL pools (canonical) | deepest SOL side | 1 SOL impact | WBTC pools | routable (2 hops) |
|---|---|---|---|---|---|---|---|---|---|
| PUMP | 86 | +32.30 (54) | +8.92 (32) | direct 56, 2-hop 30 | 23 (no) | 17.4 | 5.4% | 0 (no) | no |
| CARDS | 80 | +22.25 (80) | +0.00 (0) | direct 77, 2-hop 1, 3-hop 2 | 0 (no) | - | - | 0 (no) | no |
| ZEC (A7bd) | 23 | +3.40 (7) | +1.93 (16) | direct 23 | 1 (no) | 0.0 | 96.3% | 0 (no) | no |
| TTWO | 23 | +10.30 (15) | +0.07 (8) | direct 15, 2-hop 8 | 0 (no) | - | - | 0 (no) | no |
| XMR (WXMR) | 15 | +6.48 (9) | +0.70 (6) | direct 15 | 0 (no) | - | - | 0 (no) | no |
| SPCX | 14 | -1.00 (7) | -0.51 (7) | direct 13, 2-hop 1 | 0 (no) | - | - | 0 (no) | no |
| Pren1F | 11 | +3.10 (8) | -0.57 (3) | direct 10, 2-hop 1 | 0 (no) | - | - | 0 (no) | no |
| USDC | 10 | +7.11 (8) | +2.65 (2) | direct 9, 2-hop 1 | 117 (no) | 28212.3 | 0.0% | 0 (no) | no |
| WETH | 7 | -0.56 (3) | -0.17 (4) | direct 7 | 1 (no) | 0.0 | 98.9% | 0 (no) | no |
| DJTu | 7 | +0.00 (0) | -2.03 (7) | direct 7 | 0 (no) | - | - | 0 (no) | no |
| 42 other tokens | 92 | | | | canonical: 1 | | | | |

- **Canonical pools: none.** Of the 78 tokens checked (every pay token, the curve quotes of its multihop routes, the
  paper run's skips), the only one with a canonical PumpSwap pool against wSOL is H74CYmXg, a graduated pump coin whose
  direct buys the bot already routes ("pool+curve"). None has one against WBTC.
- **Other PumpSwap pools exist** for a few: USDC (117 pools, the deepest 28,212 SOL), PUMP (23, the deepest only 17.4 SOL:
  5.4% impact on 1 SOL each way), PUMP / USDC (11.5 M USDC deep), 9BB6NFEc (39.8 SOL), 2zMMhcVQ (7,033 SOL). CARDS, TTWO,
  XMR, SPCX and the xStocks have no PumpSwap pool against wSOL, WBTC or USDC at all.
- **`multi_hop_swap` refuses them** (`sim_pool.py`, simulated on mainnet with wallet 4 as the payer, nothing sent):
  wSOL → USDC through the 28,212 SOL pool fails with `OnlyPumpPools` (error 6078, "Only canonical pump pools are
  supported by this instruction"); wSOL → USDC → PUMP the same. The control, wSOL → H74CYmXg through its canonical pool,
  succeeds (67,861 compute units). All 352 pool hops in its own 663 routes are canonical.
- So a price for PUMP, CARDS, TTWO, USDC in `oracle.rs` would only turn "unpriced" into "no anchor reaches". A pool
  table in `route.rs` would build routes the program rejects. Even if they worked (`partb.py`, an upper bound with
  PumpSwap's 0.25% fee and the pool's impact each way): 2 hops adds 9 copies on P1 (+4.67) and 3 on P2 (+1.46, −0.25
  without the best 2); 3 hops through USDC adds PUMP, which loses on both (P1 −0.74 on 24, P2 −1.61 on 15).

**The float alternative** (`floats.py`: hold the pay token and buy its coins straight on the curve; copies priced as if
the token were held at no risk; at most 4 open; P3 from `DATA=fresh3`):

| held float | alone P1 | alone P2 | alone P3 | beside part A: P1 / P2 / P3 (A alone +6.73 / +11.13 / −2.02) |
|---|---|---|---|---|
| PUMP | +8.65 (+5.48), 41 | −1.32 (−3.31), 19 | +1.20 (−0.12), 3 | +14.51 / **+10.13** / −0.82 |
| CARDS | +0.78 (−1.59), 63 | none (0 buys since Oct 22) | +1.13, 1 | +8.37 / +11.13 / −0.89 |
| TTWO | +2.17 (+0.26), 11 | −0.42 (−0.64), 5 | +0.32, 1 | +8.90 / **+10.71** / −1.70 |
| ZEC (A7bdiYdS) | +1.32 (−0.53), 6 | +1.08 (−1.05), 15 | +0.86, 2 | +8.04 / +12.48 / −1.16 |
| USDC | +5.26 (+3.14), 8 | +1.03, 1 | none | +11.99 / +11.13 / −2.02 |

Its price in SOL from its own swaps (`floats.py`), and what a 4 SOL float would have made or lost:

| token | P1 | P2 | P3 | worst fall (peak to trough) | on a 4 SOL float |
|---|---|---|---|---|---|
| PUMP | +4.6% | −3.5% | −1.2% | −12.5% (to Oct 26) | −0.50 SOL |
| CARDS | +16.5% | −4.5% | +0.6% | −14.7% (to Oct 27) | −0.59 |
| ZEC | +7.0% | +3.9% | +4.6% | −7.7% (to Oct 24) | −0.31 |
| TTWO | +2.8% | +0.6% | −2.0% | −2.9% | −0.11 |
| USDC | +1.2% | +2.4% | −0.1% | −4.3% | −0.17 |
| WBTC (held now) | +0.2% | +1.8% | +0.1% | −1.3% | −0.05 |

- **PUMP fails out of sample**: beside part A it lowers P2 (+10.13 against +11.13), and a PUMP float carries a 12.5%
  drawdown risk. CARDS stopped (no big CARDS buys after Oct 22). TTWO and USDC are too few.
- **ZEC is the only float positive beside part A in all three periods** (+1.31, +1.35, +0.86), but alone it is negative
  without its best 2 in P1 and P2: a few wins carry it, and ZEC itself rose in SOL over the 10 days. It is a
  config-only paper trial: add the ZEC mint to `floats` in `long.toml` (the oracle prices floats, `route::plan` treats a
  float quote as an anchor: a 1-hop "curve" buy). Real money would need about 4 SOL of ZEC bought with `float buy`.

## B. "route of 3 hops" (`routes.py`, `txsize.py`, `hops3.py`)

**Answer: a 3-hop buy fits in a v0 transaction with pump's own lookup table (about 1,027 bytes), and the 3-hop buys add
about +0.1 SOL a day. Worth it only as part of other transaction work.**

- **Which buys:** its own route has 3 hops (always 2 pools then the curve). 7 of its 663 big multihop or class-E buys
  in Oct 19-27: 5 from wSOL or WBTC (the bot's "route of 3 hops"), 2 from CARDS (no route anyway). Its 2-hop routes from
  a token we don't hold (PUMP 30, TTWO 8, ...) would need a pool in front, and none of those tokens has a canonical
  pool, so they never become 3-hop routes. The paper journal had 2 in 21 h.
- **Bytes** (`txsize.py`, our buy as `txb.rs` builds it, counted from the wire format; the count gives the measured
  1,088 bytes for the 2-hop buy without a tip):

| hops | accounts | legacy (as built) | legacy, no wSOL wrap | v0 + our own lookup table | v0 + pump's table (Hyif6eWb) |
|---|---|---|---|---|---|
| 2 | 28 | 1,137 | 1,098 | 832 | 894 |
| 3 | 32 | **1,270 (over 1,232)** | 1,231 (1 byte spare) | 965 | **1,027** |
| 4 | 36 | 1,403 | 1,364 | 1,098 | 1,160 |

- pump's mainnet lookup table (`constants.rs PUMP_MAINNET_ALT`, read from the chain: 184 addresses, never deactivated)
  holds 12 of our fixed accounts: PumpSwap's global config, fee config, event authority and program, pump's global,
  fee config, event authority and program, Token-2022, the SPL token and system programs, the wSOL mint. Not WBTC. No
  table of our own is needed.
- **Wallet 4 itself sends version-1 transactions** (all 663, no lookup tables), 902-2,367 bytes; its 3-hop buys are
  1,377-1,853 bytes. It keeps a funded wSOL account and creates the coin account with a seed, and uses a durable nonce.
  The 1,232-byte limit doesn't bind it.
- **Their value** (`hops3.py`, `p3.py`): grid.py's routable set counts them (route_cls.py classes a multihop from wSOL or
  WBTC as routable at any length). The bot as built can't take them: at most 4 open, grid's set P1 +6.97 (+5.01) /
  P2 +10.43 (+7.77) without them, against +6.73 / +11.13 with. On the bot's set: P1 −0.25 (NotmcxBN), P2 +0.70
  (CCci2Fr6 +0.87 tp, CcLYZCSg −0.17, 6dp2JZAY 0.00), P3 +0.54 (2FSWwQwj +0.52, AvcwGFaF +0.02). **+0.99 over 9.6 days
  on 7 copies.**
- **Code:** `crates/rugsnipe-tx` gains a v0 compile with a lookup table; `txb.rs::sign` compiles v0 with pump's table
  (resolve its addresses once at start); `route.rs` `MAX_OUR_HOPS = 3`. A `txb.rs` test that a 3-hop buy and sell fit;
  a `route.rs` test that a 3-hop route from wSOL is copied. Risk: a new transaction format on the send path (simulate on
  mainnet first, as `sim_pool_sell.rs` does).

## C. Part C again: its 0.8-1.45 SOL buys (`partc.py`)

**Answer: still out.** Routable, no cap; 0.7x its buy as stake, or 1 SOL:

| its buy, routes | copies | 0.7x: P1 | 0.7x: P2 | 1 SOL: P1 | 1 SOL: P2 |
|---|---|---|---|---|---|
| 0.8-1.45, WBTC routes (B, C) | 207 | +1.12 (−0.40) | **−5.98 (−7.57)** | +2.62 (+0.53) | −5.98 (−7.94) |
| 0.8-1.45, wSOL routes (A) | 210 | −1.02 (−2.76) | −3.39 (−4.98) | −0.23 (−2.69) | −3.79 (−5.95) |
| 0.8-1.0, WBTC | 92 | +0.72 (−0.59) | −1.25 (−2.31) | +1.68 | −0.68 |
| 1.0-1.25, WBTC | 78 | +0.94 (−0.44) | −3.61 (−4.41) | +1.45 | −4.22 |
| 1.25-1.45, WBTC | 37 | −0.55 (−1.33) | −1.11 (−2.19) | −0.52 | −1.08 |

Beside part A (4 open) the WBTC-routed band at 0.7x drags P2 from +11.13 to +4.78. On P3 every band loses too
(`../fresh/` README §3).

## D. Copying part A better

The bot as built is not quite grid.py's set: it takes 1.45+ SOL (grid.py: 1.5+) and no 3-hop routes. At most 4 open
(`better.py base`, `p3.py`): grid's set +6.73 (+4.76) / +11.13 (+8.48) / −2.02 (−3.74); **the bot's set (1.45+, its
route verdicts, the coins that graduated before it sold, as `../fresh/` defines it, and no 3-hop) +5.44 (+3.47) /
+12.79 (+10.00) / −0.51 (−2.39)** on 152 / 159 / 32 copies. The tables below use grid's set (P1/P2) and give the bot's
set where it differs.

### (i) WBTC routes (`better.py route`, `p3.py`)

WBTC-routed copies make about +0.12 SOL a copy, wSOL-routed about +0.02: P1 +3.49 on 28 / +3.23 on 117; P2 +10.03 on 81 /
+1.11 on 64.

| at most 4 open | P1 | P2 | P3 | bot's set P1 / P2 / P3 |
|---|---|---|---|---|
| as built (1 SOL everywhere) | +6.73 (+4.76) | +11.13 (+8.48) | −2.02 (−3.74) | +5.44 / +12.79 / −0.51 |
| WBTC routes only | +3.49 (+1.52), 28 | +10.03 (+7.86), 81 | −0.21, 4 | +2.67 / +11.23 / +1.56 |
| 1.5 on WBTC, 0.5 on wSOL | +5.07 (+2.39) | +15.27 (+12.09) | | |
| 1.5 on WBTC, 1.0 on wSOL | +8.34 (+5.66) | +16.81 (+13.62) | −2.07 | +6.73 / +19.16 / +0.25 |
| **2.0 on WBTC, 1.0 on wSOL** | **+10.04 (+6.55)** | **+22.04 (+17.90)** | −2.11 | **+8.13 / +25.07 / +1.02** |
| 1.5 everywhere | +10.98 (+8.11) | +17.90 (+13.98) | | |
| 2.0 everywhere | +14.41 (+10.67) | +23.56 (+18.43) | −3.31 | +12.13 / +27.07 / −0.25 |

Per SOL staked (grid's set): as built +4.64% (P1) / +7.68% (P2); 2.0 WBTC / 1.0 wSOL **+5.80% / +9.75%**; 2.0 everywhere
+4.97% / +8.12%. Dropping the wSOL routes loses (they are about zero, not negative). More SOL on the WBTC routes is
the better use of a bigger bankroll, in both periods; on P3 wallet 4 made few WBTC buys (4-6 copies). Code: a stake per
anchor in `engine.rs::on_trigger` (`let stake = ...`): a `float_stake_sol` (or a per-float map) in `config.rs`, used when
`plan.anchor` is a float; an engine test that a WBTC-routed trigger buys the float stake. Risk: the WBTC float must hold
4 x 2 SOL; our own lift grows with the stake (`scale.py`: fine to 2-3 SOL).

### (ii) Entry filters (`filters.py`; the old `filt.py`, `filt2.py`)

**Answer: none passes.** The old studies' best cells were the rule itself (its size >= 1.5, other quotes; filt.py P1
+67.17 / P2 +14.31 on 352 / 246) and multihop routes; tip, stage and "copiers ahead" cells fell apart on P2. The new
features, as built per copy (no cap), on its 1.45+ set:

- **Coin age and trades before its buy are no filter: every one of its big buys comes within 2 s of the coin's create**
  (age.py: 322 of 323 under 2 s; 314 with fewer than 5 curve trades before it). They are launch buys.
- Its first buy on the coin: always. Every one of its 601 big other-quote buys (1.5+ SOL) is its only buy of that coin.
- Size tier 1.45-1.5: P1 −1.54 on 8, P2 +0.54 on 20 (min_sol 1.5: P1 +1.53, P2 −1.14, P3 +0.96 on the bot's set: mixed).
- Curve progress, its open big positions, hour, quote, route: the best of 62 filters picked on P1 (4 open, 1.45+) was
  **"not 18-24h UTC"**: P1 +8.02 (+6.05) against +5.19, then P2 +11.42 against +12.27. On the bot's set (`p3.py`)
  P1 +8.02 against +5.44, P2 +12.81 against +12.79, **P3 −1.52 against −0.51**. "progress not 5-10%" (P2 +7.23) and
  "its open not 4-6" (P2 +11.34) also lose on P2.
- **Frenzy** (trades in its slot and the 2 after; not known when we buy at +1): 1-2 trades lost on P1 (−2.80 on 107)
  and won on P2 (+9.30 on 86). Waiting to see it and buying at +3 only after 3+ trades: P1 +5.23 on 29, P2 −0.29 on 34
  (buying everything at +3: +4.62 / +11.27).

### (iii) Partial exits (`better.py partial`, `p3.py`)

**Answer: no.** Every partial sale loses on P1 and P2 (each extra sell charged 0.0095 + half the bias); the take-profit
floors flip between periods:

| at most 4 open | P1 | P2 | P3 |
|---|---|---|---|
| as built: all at 2.0x | +6.73 (+4.76) | +11.13 (+8.48) | −2.02 |
| half 1.5x, half 2.0x | +3.46 (+1.81) | +7.83 (+5.46) | −1.11 |
| half 1.5x, half 2.5x (before its sell) | +0.44 (−1.13) | +4.99 (+2.75) | |
| thirds 1.5 / 2.0 / 2.5 | +1.69 (+0.10) | +6.34 (+3.99) | |
| thirds 1.5 / 1.75 / 2.0 | +3.19 (+1.59) | +7.77 (+5.49) | |
| tp 2.0, floor 1.5 after 1.8 | +4.78 (+2.95) | +11.89 (+9.23) | −1.84 |
| tp 2.0, floor 1.2 after 1.5 | +7.98 (+6.02) | +10.86 (+8.20) | −1.75 |
| tp 2.5 / 3.0 / none, floor 1.8 after 2.0 | +2.19 (+0.04) | +7.58 (+4.81) | |

Its own 2.5x sale lands first above 2.0, so a runner is sold behind it; a first half at 1.5x gives up more on the runs
than it saves on the falls. The floor variants flip between periods.

### (iv) The stop by route class (`better.py stop`, `p3.py`)

**Answer: keep 0.8.** Picked on P1, the best pair is 0.8 on wSOL / 0.9 on WBTC routes: P1 +6.97 (+5.00), P2 +11.15
(+8.50), P3 −2.02 (bot's set: +0.26 / +0.25 / 0.00). About +0.03 SOL a day. 0.85 on wSOL routes is worse on P1 (+6.56).

### (v) Its early sells (`early.py`, `early2.py`)

The engine sells behind any sell of its (`engine.rs`, the `Seen::Sell` branch, `Reason::ItsSell`). The backtest paths end
at its sale, so the other choice, ignoring it and keeping our own exits, needs the curve after its sale: fetched to
1,800 s after its buy.

**The 9 paper copies closed `its_sell`** (`early.py`, every curve trade, no sampling; both ways priced by the model at the
backtest's costs; paper's own net beside them):

| coin | its buy (UTC) | it sold after | paper | follow it (model) | ignore it (model) | ignore's exit | best price after its sale |
|---|---|---|---|---|---|---|---|
| BPhav4G4 | Oct 27 19:49 | 197 s | −0.2958 | −0.332 | −0.347 | time | 0.84x |
| ChonQdJ8 | 20:09 | 7 s | −0.1756 | −0.224 | **+0.673** | tp | 5.27x |
| FUCKKmZZ | 21:02 | 475 s | −0.2468 | −0.288 | **+1.020** | tp | 9.33x |
| HytpiyuR | Oct 28 00:24 | 287 s | +0.1038 | +0.036 | **+0.891** | tp | 4.20x |
| 6DS5ErwH | 01:04 | 142 s | −0.3031 | −0.340 | −0.280 | stop | 0.83x |
| DJXThGNt | 01:31 | 4 s | −0.0623 | −0.118 | −0.507 | stop | 1.27x |
| 9hhXcHT9 | 02:41 | 908 s | +0.1424 | +0.069 | −0.150 | time | 1.23x |
| 3j9ex53k | 06:49 | 1,360 s | +0.1429 | +0.071 | +0.015 | time | 1.24x |
| 9ENc9LwF | 13:31 | 12 s | −0.1874 | −0.237 | **+0.656** | tp | 2.44x |
| **9 copies** | | | **−0.8819** | **−1.364** | **+1.972** | | |

Ignoring its sale would have made **+3.34 more** on paper's 9 (4 coins ran to 2x after it sold out). Over every period
(`early2.py`: the backtest's copies that end behind its early sale, the bot's set, 4 open; after its sale the first 25
transactions and a sample of the rest):

| | copies behind its early sale | follow (as built) | ignore | the bot's set, follow → ignore |
|---|---|---|---|---|
| P1 | 1 | −0.37 | −0.41 | +5.44 (+3.47) → +5.40 (+3.43) |
| P2 | 10 | −1.69 | −1.94 | +12.79 (+10.00) → **+12.54 (+9.75)** |
| P3 | 13 | −2.37 | +1.23 | −0.51 (−2.39) → **+3.10 (+1.02)** |

**It depends on the period.** In P2 (its early sales 13.6% of its big buys) following was slightly better: the coins
fell to our stop after it left. In P3 (49%, `../fresh/` §2) 4 of its 13 early exits were followed by a run to 2x. P1
can't pick (1 copy). On the sampled paths the 4 P3 take profits come out 0.03-0.27 better than on the full paths
above, and all of them are frenzy coins where the model's next-trade fill is kind (`../fresh/` §4). **A paper test
before a real one:** a `follow_its_sell` switch in `config.rs` (default true) read in the `Seen::Sell` branch of
`engine.rs`; when false, journal `long its-sell #N: kept (follow_its_sell = false), curve at {x}x` (the price we would
have sold at) and leave the position to its own exits. An engine test in `tests/engine_paper.rs` (its sell with the
switch off: the position stays open and the take profit still fires), a line in `docs/20-long-copy.md` §3. Risk: if
P2's behavior comes back, about −0.06 SOL a day; if P3's holds, about +2.2.


### (vi) The entry limit, 25% (`better.py premium`)

grid.py's "as built" has no limit. At most 4 open: none +6.73 / +11.13 / −2.02; **25% (the bot's) +6.05 / +11.24 /
−1.86**; 50% +6.63 / +10.65; 10% +4.48 / +12.86; 5% +4.77 / +11.36. The 8 copies 25% refuses make P1 +0.68 (4) and
P2 −0.11 (4) when taken. No limit gains on P1 and loses on P2 and P3 (bot's set: P3 −0.51 against −0.34). Paper's two
refusals (5a7nDZcR at 1.518x, EwsKTHxB at 1.321x) would have made +0.2432 and −0.4049 in the model (`../fresh/` §4).
Keep 25%.

### (vii) Landing (`better.py land`, `p3.py`)

| at most 4 open | P1 | P2 | P3 | bot's set P1 / P2 / P3 |
|---|---|---|---|---|
| in its own slot (land 0) | **+8.87 (+6.89)** | **+12.63 (+9.81)** | **−0.86** | **+7.58 / +14.44 / +1.36** |
| slot +1 (as tested; paper) | +6.73 (+4.76) | +11.13 (+8.48) | −2.02 | +5.44 / +12.79 / −0.51 |
| +2 | +6.48 | +10.53 | −2.11 (`../fresh/`) | |
| +3 | +6.15 | +10.31 | −2.20 | +4.87 / +11.79 / −0.66 |
| +5 | +4.99 | +9.16 | −2.41 (`../fresh/`) | |

Landing in its own slot is worth about +2.1 / +1.5-1.7 / +1.2-1.9 SOL a period: **the upper bound on speed, +0.4-1.2
SOL a day.** Each slot later than +1 costs 0.2-0.6 a period. Ohio's real lag is the open question (deploy `7184554`, read
`seen at its slot +N`).

## E. Parts D and E

**D (SOL-priced coins): out.** Copying its big SOL-coin buys and holding them the long copy's way loses on both
periods (`exits_pess.py`: P1 −11.12 on 73, P2 −2.34 on 31). Its own edge there is about +0.02 SOL a coin, below a copy's
fixed 0.0345, and on P3 wallet 4 itself lost on its SOL-priced coins (−3.72 on 212, `../fresh/` §1). The launch copy
(strategy D) made +0.15 live against its +2.77, every setting about zero without the best 2 (02-decomposition §4).

**E (PumpSwap-only tokens): out.** Wallet 4's own net there: +17 over 8 days (CARDS +13.5), −2.76 in check.sh's
window, +1.31 (−1.30) on 36 coins in P3 (`../fresh/` §1). Neither bot follows pool trades, `multi_hop_swap` routes canonical pump pools only
(`sim_pool.py`), and no backtest of copying them exists. Not worth building on this evidence.


## Notes

- Pools and reserves are as of Oct 28 ~15:30 UTC, not as they were on each buy. Token prices in SOL come from wallet 4's
  own swaps (ledger.py's way); Jupiter's price API (lite-api v3) prices every part-B token (`pools.py`), so a price was
  never the blocker.
- `early.py` uses every curve trade; `early2.py` and the backtest's long paths are sampled. The take profits after its
  early sale are on frenzy coins, where the model's next-trade fill is kind and real fills from Ohio land later.
- `sim.py` charges each extra sell of a partial exit 0.0095 + half the bias (0.01725). The stake tests price our own
  impact with model q; scale.py's caution about stakes past 2-3 SOL holds.
- Every number here comes from the scripts' printed output, run on Oct 28. P3 is 38.6 h and 25-32 copies.

## Run order

`SP` = the session scratchpad of the 8-day study (CLAUDE.md "Datasets"); the fetchers write to this session's scratchpad
(`SPX` in the scripts: change it to rerun elsewhere; `quotes.py` first). The Triton client is `SP/month/tri.py` (its URL
is never printed or stored). `DATA=fresh3` needs the other session's `SP/fresh3/h9long` (`../fresh/` README).

```
python3 -I check.py                 # sim.py = grid.py: +5.03 / +9.63 at 3 open, +6.73 / +11.13 at 4
python3 -I quotes.py 1.45           # its big buys by pay token and route class -> SPX/quotes.json
python3 -I routes.py                # each one's transaction: hops, input, size, version (Triton) -> SPX/routes.json
python3 -I skips.py                 # the paper run's 73 skips matched to its transactions -> SPX/skips.json
python3 -I pools.py                 # PumpSwap pools from wSOL / WBTC / USDC per token (Triton, Jupiter prices) -> SPX/pools.json
python3 -I btable.py                # the part-B table
python3 -I sim_pool.py              # multi_hop_swap through a non-canonical pool, simulated on mainnet
python3 -I partb.py 2|3|4           # part B IF those pools worked (upper bound); FLOAT=USDC, MINR=
python3 -I floats.py                # part B held as floats; DATA=fresh3 adds P3
python3 -I txsize.py                # the buy's bytes by hops: legacy, v0 + a lookup table; pump's own table
python3 -I hops3.py                 # its 3-hop buys and what they add
python3 -I partc.py                 # its 0.8-1.45 SOL buys at 0.7x its size, by route class
python3 -I age.py                   # the coin's age at its buy (Triton) -> SPX/age.json
python3 -I filters.py 1.45          # entry filters, picked on P1
python3 -I better.py base|route|stop|premium|land|partial [LO]   # BOT=1: the bot's set (no 3-hop)
python3 -I early.py                 # the 9 paper copies closed behind its early sale: ignore it instead? (Triton)
python3 -I early2.py                # the same over P1-P3 from the backtest's copies (Triton; DATA=fresh3 inside)
python3 -I p3.py                    # the ideas on P3 (DATA=fresh3)
```
