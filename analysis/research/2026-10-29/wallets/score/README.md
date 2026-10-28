# Scoring other wallets with wallet 4's pipeline (Oct 28-29)

Strategy A copies wallet 4 (`H9kuqGKN`): its 1.45+ SOL buys of pump coins priced in another token, at the create slot or
the next, held to 2.0x / 0.8x / 1,790 s (`../../../2026-10-28/fresh/README.md`). This folder runs the same per-wallet
pipeline on other wallets, to find ones with the same edge. First batch: the four neighbours named in
`07-rework-2026-10-28/wallet-check.md` §4b.

| short | address | what wallet-check.md §4b says |
|---|---|---|
| 6anjqMeW | `6anjqMeWigQFo5wpciARAunVQUXTqoat8w8fFWarCkpc` | fast launch buyer, fixed 0.5 SOL, on 28 of 40 sampled wallet-4 coins |
| AMDEmVoc | `AMDEmVocLtN5ji2gBY7BrmSHEyM5vt6TGszBbg4crMXg` | 0.6 SOL buys, on 11 of 40 |
| Fhbh1DTU | `Fhbh1DTUDKt6qu9zVg8Q5VgnZa1WWWbxBxG6pCoJoggA` | micro-buy bot (0.002-0.003 SOL), on 5 of 40 |
| dKMjeGJ4 | `dKMjeGJ4Mk9S3hxdfTThvZ7exks2xMwWqSM5NvN2CTK` | slot-0 sniper that sells in 0-3 s (docs/research/strategy-copytrade.md, docs/19) |

Periods (UTC, by the coin's first buy): **P1** Oct 19-22 (pick), **P2** Oct 23 → Oct 27 00:20 (score), **P3** Oct 27
00:20 → the wallet's last row (Oct 28 22:22-22:52). (+x) = without each period's best 2. Costs as everywhere: 0.0095 SOL a
transaction, 0.0155 SOL bias a fill, 5.13% round trip on coins priced in another token; model q + lift (`grid.py`).
Every number below is in `out/<w8>_<step>.txt`.

**Priority change (23:20 UTC, from `../neighbours/README.md`):** only 6anjqMeW passed the neighbours' profile screen, so
it got the full pipeline on its own history (also at a 0.45 SOL floor, its own size). AMDEmVoc, Fhbh1DTU and dKMjeGJ4
got the cheap marks only (counts, hold, early sales, failed share, routes, own result): no paths, no backtest.

## The answer

**None of the four has wallet 4's edge. Not worth copying with strategy A, as is or with a changed exit.** All four are
launch scalpers: they buy at the create slot or the next, sell most coins in one piece within seconds or minutes at
about the price they paid, and make most of their money on the coins that run in the first seconds, which they sell in
parts (6anjqMeW: one-sale coins −83.27 SOL, coins sold in parts +131.65). Wallet 4 is the opposite: it sells 99.9% of
its coins in one piece, and those make its money (+140.45 / +111.93 / +45.68 in P1 / P2 / P3). It held 74% of them to
its 30-minute timer; the median one-sale hold here is 1 s (Fhbh1DTU), 2 s (dKMjeGJ4), 6 s (AMDEmVoc) and 43 s
(6anjqMeW, with timers at 4, 8 and 12 minutes); at most 2% of any one's one-sale trips reach 30 minutes. A copy that lands a slot
later buys what they are already selling.

## The table

| wallet | 1. big other-token launch buys a day, P1 / P2 / P3 | 2. its rule | 3. early sales | 4. failed | 5. routable | 6. its own result, P1 / P2 / P3 | 7. our copy, P1 / P2 / P3 (copies) | 8. frenzy |
|---|---|---|---|---|---|---|---|---|
| **wallet 4** (reference) | 1.45+: **100.0 / 73.7 / 34.2** (0.5+: 440 / 294 / 174); create+0/+1: 47 of 47 measured, 322 of 323 within 2 s; via SOL 218, WBTC 133, PUMP 92, CARDS 80 (of 751) | 2.5x / 0.7x / 30 min: **74%** of 3,325 one-sale trips held to 1,790 s+ (1.45+: 65%); hold p25 / median 1,378 / 1,800 s | 1.45+: 3.5% / 13.6% / 49.0% | 2.9% | 1.45+: **48%** (358 of 751, its own route); 0.5+: 29% | +248.54 (+227.32) / +112.27 (+98.48) / +82.00 (+58.80) | 1.45 floor: **+5.19 (+3.22), 153 / +12.27 (+9.62), 161 / −2.98 (−4.70), 30**; landing slot +3: +4.62 / +11.27 / −3.19 | 2 (p25 1, p75 4; 734) |
| **6anjqMeW** | 1.45+: **0 / 0 / 0**. Its size, 0.45+: 535.0 / 267.1 / 361.0; create+0/+1 86% / 57% / 63%; PUMP 552, CARDS 400, SPCX 361, xStocks 293 (of 3,912) | no take profit, no 30-min timer: one-sale trips held < 5 s (42%) or to 240 / 480 / 740 s timers, 1% to 1,790 s; one-sale coins −83.27, coins sold in 2-4 parts within seconds +131.65 | 1.45+: none; 0.45+: 92.0% / 94.6% / 91.6% | 8.5% (P1 16.5%, P2-P3 1.8-1.9%) | 1.45+: none; 0.45+: **19%** (746 of 3,912) | +32.92 (+26.05) / +33.09 (+27.42) / +16.54 (+13.36) | 1.45 floor: **no copies**. 0.45 floor (MULTI): **−11.60 (−13.87), 416 / −17.81 (−20.77), 208 / −8.48 (−10.94), 96**; landing slot +3: −14.25 / −18.67 / −8.22 | 1 (p25 0, p75 2; 724) |
| **AMDEmVoc** | 1.45+: 0.2 / 0.2 / 0 (2 coins). 0.5+: 139.8 / 189.6 / 152.3; create+0/+1 98%; PUMP 178, xStocks 120, CARDS 103 (of 1,615) | one-sale trips held 4 / 6 / 8 s (p25 / median / p75) at 1.00x, 0% to 1,790 s; profit from 75 coins sold in parts | 1.45+: 1 trip; 0.55+: 95.1% / 96.6% / 95.1% | 3.2% | 1.45+: 0 of 2; 0.5+: 28% | +27.29 (+21.08) / +55.34 (+50.36) / +17.02 (+11.17) | not run (cheap marks only) | not run |
| **Fhbh1DTU** | 1.45+: **95.5 / 65.0 / 61.4**; create+0/+1 72% / 65% / 69%; PUMP 307, CSocnzcR 99, CARDS 66, DoGEV7LA 34 (of 762) | one-sale trips held 1 / 1 / 2 s at 1.00x, 0% to 1,790 s; profit from coins sold in parts | 1.45+: 99.4% / 99.0% / 94.7% | **86.3%** | 1.45+: 40% (308 of 762); 0.5+: 29% | +125.49 (+94.11) / +160.04 (+137.04) / +59.79 (+42.38), plus +1,777.50 from tokens it did not buy here | not run | not run |
| **dKMjeGJ4** | 1.45+: 15.0 / 53.1 / 51.1; create+0/+1 99%; PUMP 116, SPCX 54, xStocks 51, DJTu 46 (of 371). SOL-priced 1.45+: 1,327 / 1,155 / 564 coins | 2-8 SOL slot-0 sniper; sells in parts, first sale 6-13 slots, last 26-37 slots (medians) | 1.45+: 3 / 48 / 1 trips, 92-100% | **47.2%** | 1.45+: 11% (39 of 371) | +390.82 (+328.72) / +290.23 (+221.77) / +68.51 (+44.71); other-token coins +0.15 / +10.16 / −4.63 | not run | not run |

Wallet 4's row is its own data (`fresh3`, Oct 19 → Oct 28 14:54 UTC) through the same scripts (`out/H9kuqGKN_*.txt`):
`marks.py` with its own route class (`ROUTECLS=wallet4`), `grid.py cap|land q 1 1.45 9` at 4 open, `frenzy.py`. Its
create share is from `07-rework-2026-10-28/wallet-check.md` §6 (47 of 47 measured coins at the create slot or the next)
and `../../../2026-10-28/more/` (age.py: 322 of 323 big buys within 2 s of the create); `create.py` was not re-run on it.
Column 1 counts first buys of a coin; the 0.5+ counts include the 1.45+ ones.

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

**Our copy** (`grid_*_0.45.txt`; routable buys from 0.45 SOL, coins priced in another token, `MULTI=1`, 1 SOL a copy,
TP 2.0 / SL 0.8 / 1,790 s, q + lift, landing at its slot + 1, at most 4 open). At the 1.45 floor there is nothing to
copy (`grid_cap.txt`: 0 buys). From its own size:

| variant | P1 Oct 19-22 | P2 Oct 23-27 | P3 Oct 27-28 |
|---|---|---|---|
| **as built, 4 open** | **−11.60 (−13.87), 416** | **−17.81 (−20.77), 208** | **−8.48 (−10.94), 96** |
| 1 open / 3 open / no cap | −12.56 / −11.81 / −11.23 | −13.49 / −17.04 / −17.81 | −8.10 / −8.12 / −8.48 |
| one-sale coins only (no MULTI) | −11.46 (−13.67), 349 | −24.60 (−24.94), 149 | −11.96 (−12.09), 64 |
| 0.5 SOL a copy | −12.75 (−13.86) | −12.38 (−13.94) | −5.87 (−7.10) |
| no lift (ITS_TP=99) | −11.87 (−14.22) | −16.17 (−20.61) | −8.40 (−10.85) |
| best take profit, 1.1x to none (SL 0.8; SL 0.9 is no better) | 2.0x: −11.60 | 1.2x: −12.17 | 1.4x: −6.58 |
| landing slot + 2 / + 3 / + 10 | −13.51 / −14.25 / −24.49 | −17.69 / −18.67 / −20.11 | −8.05 / −8.22 / −10.19 |
| 6anjqMeW itself on the same coins (`itsown`) | +15.90 | −1.53 | +1.13 |

Every take profit from 1.1x to none, every cap, both stakes and every landing lose in all three periods, and every day
loses but Oct 27 in P2 (2 copies, +0.06; `grid_days_0.45.txt`). What closes the copies (`grid_mix_0.45.txt`, P1): 332
of 416 end right after its sale ("its early sell, we follow", −34.55, −0.104 a copy), 44 hit 2.0x (+34.38), 35 the stop
(−11.23). Its sale comes before our rule on four copies in five, at about the price we paid plus the costs. The frenzy
behind its buys is thin: a median 1 landed curve transaction after it in its slot and the next (p25 0, p75 2; 724
buys), against wallet 4's 2 (p25 1, p75 4).

**Verdict: not worth it.** No buy reaches the 1.45 floor, and at its own size the copy loses in every period and every
setting. Its own edge is selling into the first seconds of a run, which a copy one slot behind cannot have.

## The other three: cheap marks only

**AMDEmVoc** (`out/AMDEmVoc_marks.txt`, `_early_0.55.txt`, `_behave_P*.txt`). A 0.6 SOL launch scalper: 1,615 first
buys of other-token coins at 0.5+ SOL, 1,590 of them at the create slot or the next; only 2 at 1.45+ (CARDS, PUMP, not
routable). Its one-buy one-sale trips (1,783) are held 4 / 6 / 8 s (p25 / median / p75), first sale after a median 25-32
slots, sold at a median 1.00x; its one-sale coins (1,786) net −2.45 over the three periods. Its profit on these coins is
the 75 it sold in parts (+49.82). Early sales on its own size (0.55+): 95.1% / 96.6% / 95.1%. Failed 3.2%. Its whole result is real
(+99.64 SOL on 6,271 tokens, the ledger's check: cash moved by trading +99.49) but it is made in seconds.

**Fhbh1DTU** (`out/Fhbh1DTU_marks.txt`). Not a micro-buy bot on its own coins: 762 first buys of 1.45+ SOL in other-token
coins (95.5 / 65.0 / 61.4 a day), 69% at the create slot or the next, 40% routable (all class A: quotes with a wSOL
pool). This is the volume we want, but it sells them in 1-2 s (one-sale trips p25 / median / p75 1 / 1 / 2 s, 98% within
20 s, at a median 1.00x); 99.4% / 99.0% / 94.7% of its 1.45+ one-sale trips are early sales. On wallet 4's coins it is often just
before wallet 4 (wallet-check.md §4b) and sells into the buying that follows. 86.3% of its signatures fail (155,007 of
182,408: it sprays). Its result by first buy is +125.49 / +160.04 / +59.79, but the ledger also shows +1,777.50 SOL of
sales of tokens it held before Oct 19 or received (217 token transfers): it is part of a larger operation, and its
own P&L is not readable from this wallet alone.

**dKMjeGJ4** (`out/dKMjeGJ4_marks.txt`). A 2-8 SOL slot-0 sniper of **SOL-priced** coins: +653.14 of its +749.56 SOL
realized (cash check +752.63) comes from 3,215 SOL-priced coins (1,327 / 1,155 / 564 first buys of 1.45+ SOL a period).
Its other-token coins started on Oct 23 in volume (15.0 / 53.1 / 51.1 a day at 1.45+, 99% at create+0/+1), 11%
routable (PUMP, SPCX, xStocks, DJTu), and made +0.15 (−3.66) / +10.16 (−5.27) / −4.63 (−7.42): no edge there. It
sells in parts within seconds (first sale a median 6-13 slots after its buy, last sale 26-37 slots). Failed 47.2%.
The research of Oct 24 already found its edge is the first fill, which a copier cannot inherit
(`docs/research/strategy-copytrade.md`).

<!-- NEW -->

## Run order (any wallet)

The scripts are the fresh study's (`../../../2026-10-28/fresh/`, which are the h9long ones with P3), copied here and
changed as little as possible. Data goes to `SP = /tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/score`
(`SP/h9long/<w8>*.json*`, the same file names as for wallet 4); `SP=... ` in the environment points every script elsewhere.
The helpers (`month/tri.py` with the Triton URL, `rivalpnl/`) are read from the old session scratchpad, as before.

```
W=<address>; export W
bash run.sh $W fetch          # sigs.py (Oct 19 00:00 UTC on), pull.py in 3 shards, merge.py
bash run.sh $W score          # ledger, groups, trips, byquote, exitrule, behave, tprate, route_q, early,
                              # create, full_paths 1.45, marks, grid cap|land|tp|mix (CAP=4, q 1 1.45 9)
bash run.sh $W band 0.45      # its own size: full paths of its routable buys from 0.45 SOL (MULTI=1), grid from
                              # 0.45 (cap land tp mix days itsown, one-sale only, STAKE=0.5, ITS_TP=99), early, marks
python3 -I row.py $W [0.45]   # its row of the table below, from marks.py's json and the grid files
```
Cheap marks only (no paths, no backtest): run `score` and stop before `full_paths.py`, as was done for AMDEmVoc,
Fhbh1DTU and dKMjeGJ4. `missing.py W8` tells how many landed signatures no file holds yet (to stop extra fetchers).

| script | from | what changed |
|---|---|---|
| `sigs.py` | `2026-10-27/h9long/` | SP from the environment; optional MAXN (stop paging) |
| `pull.py` | `2026-10-27/h9long/` | SP; each row also keeps `qm` = {coin: the curve's quote mint} (the token account the bonding curve owns besides the coin); `SHARD=k/n` and `REV=1` let several processes share the fetch |
| `merge.py` | new | folds the shard files into `<w8>.jsonl`, one row per signature |
| `ledger.py`, `groups.py`, `trips.py`, `byquote.py`, `exitrule.py`, `behave.py` | `2026-10-28/fresh/` | SP only |
| `tprate.py` | `2026-10-28/fresh/` | SP; a coin with no ledger entry counts 0 (it stopped on None) |
| `early.py`, `grid.py` | `2026-10-28/fresh/` | SP; the wallet from `W` (was wallet 4); route class from `route_q.py`. `grid.py` also: `ITS_TP` (the wallet's own take profit in the lift, default 2.5), `STAKE` (default 1 SOL), `MULTI=1` (a coin it bought once and sold in parts is one trip to its last sale; without it only one-sale coins are copied) |
| `full_paths.py` | `2026-10-28/fresh/` | SP; `KINDS` and `ROUTES` filters; `MULTI=1` (as in grid.py, the path runs to its last sale); keeps `n01`, the landed curve transactions after its buy in its slot and the next (mark 8) |
| `route_q.py` | new | route class from the curve's quote token: C = WBTC-quoted, A = canonical PumpSwap pool vs wSOL, B = vs WBTC only, E = none (`more/pools.py`'s PDA, getAccountInfo). `route_cls.py` read wallet 4's own route, which other wallets do not share. `ROUTECLS=wallet4` uses route_cls.py |
| `create.py` | new (`more/age.py`'s method) | the create slot of each coin it first bought for 0.5+ SOL in another token: the oldest signature on the bonding curve before its buy |
| `marks.py`, `row.py` | new | marks 1-6 and 8 from the files above (also its result by the shape of the coin's trades: one sale or several); one table row |
| `frenzy.py`, `missing.py` | new | mark 8 for wallet 4 (its old paths have no n01); the fetch check |

Checked on wallet 4's own data (`SP=.../fresh3 ROUTECLS=wallet4`): `grid.py cap q 1 1.45 9` at 4 open gives P1 +5.19
(+3.22) 153, P2 +12.27 (+9.62) 161, P3 −2.98 (−4.70) 30, the fresh README's "1.45+ floor" row exactly; `marks.py` gives
its P3 +82.00 (+58.80) and the early-sale table (3.5% / 13.6% / 49.0%) as published (`out/H9kuqGKN_*.txt`).

## Fetch (Oct 28, 22:51-23:30 UTC)

`sigs.py WALLET 1792368000` (Oct 19 00:00 UTC) on every candidate. All four were fetched in full, Oct 19 to their last
row (22:22-22:52 UTC Oct 28): pull.py reads landed transactions only, and those were 16,012-33,792 a wallet, not far
above wallet 4's 19,981, so no window was cut. Fhbh1DTU's 155,007 failed signatures were counted, not fetched.

| wallet | signatures | failed | landed (fetched by pull.py) |
|---|---|---|---|
| 6anjqMeW | 30,413 | 2,551 | 27,862 |
| AMDEmVoc | 16,436 | 424 | 16,012 |
| Fhbh1DTU | 182,408 | 155,007 | 27,401 |
| dKMjeGJ4 | 52,169 | 18,377 | 33,792 |
| (wallet 4, fresh3, to Oct 28 14:54) | 20,476 | 495 | 19,981 |

Throughput was about 60 transactions a second however many fetch processes ran (the session's HTTPS proxy was the
limit, at about 240% CPU): about 25 minutes for the four, then 12 minutes for 6anjqMeW's 724 paths.

## The marks (how each column is measured)

1. **Big other-token launch buys**: its first buys of pump coins priced in another token, by the SOL value
   `ledger.py` gives the buy (a quote token paid is valued at its price then), per day of P1 / P2 / P3, at 1.45+ SOL
   (0.5+ in brackets); how many came at the coin's create slot or the next (`create.py`); the quote tokens (`qm`).
2. **Its rule**: its one-buy one-sell curve trips on those coins (`exitrule.py`, `behave.py`): the hold, the price
   multiple at its sale ((vt after its buy / vt before its sale)²), the share held to 1,790 s or more (wallet 4's
   30-minute timer).
3. **Early sales** (`early.py`): of its 1.45+ SOL one-buy one-sell trips, the share sold before 1,790 s between 0.75x
   and 2.4x (neither wallet 4's take profit, nor its stop, nor its timer). These are the trips our copy ends behind.
4. **Lands**: failed signatures / (failed + landed transactions it signed). Wallet 4's own page counts failed / all
   signatures (2.4%); both are in `out/<w8>_marks.txt`.
5. **Routable**: share of its 1.45+ (0.5+) first buys whose curve quote `route_q.py` puts in A, B or C.
6. **Its own result** (`ledger.py`, every token, by the period of its first buy), and without the period's best 2.
7. **Our copy** (`grid.py`, routable, 1.45-9 SOL, 1 SOL a copy, at most 4 open, TP 2.0 / SL 0.8 / 1,790 s, q + lift,
   landing at its slot + 1; and + 3 from `grid.py land`), P1 / P2 / P3, (without the best 2), copies. For 6anjqMeW also
   from its own size (0.45 SOL), with `MULTI=1`.
8. **The frenzy**: landed transactions on the coin's curve after its buy in its slot and the next (median), on its
   1.45+ SOL trips of coins priced in another token (`full_paths.py`'s n01; wallet 4: `frenzy.py`).
