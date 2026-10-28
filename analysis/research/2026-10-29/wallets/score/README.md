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
00:20 → the wallet's last row (Oct 28 about 23:00). (+x) = without each period's best 2. Costs as everywhere: 0.0095 SOL a
transaction, 0.0155 SOL bias a fill, 5.13% round trip on coins priced in another token; model q + lift (`grid.py`).

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
```

| script | from | what changed |
|---|---|---|
| `sigs.py` | `2026-10-27/h9long/` | SP from the environment; optional MAXN (stop paging) |
| `pull.py` | `2026-10-27/h9long/` | SP; each row also keeps `qm` = {coin: the curve's quote mint} (the token account the bonding curve owns besides the coin); `SHARD=k/n` and `REV=1` let several processes share the fetch |
| `merge.py` | new | folds the shard files into `<w8>.jsonl`, one row per signature |
| `ledger.py`, `groups.py`, `trips.py`, `byquote.py`, `exitrule.py`, `behave.py`, `tprate.py` | `2026-10-28/fresh/` | SP only |
| `early.py`, `grid.py` | `2026-10-28/fresh/` | SP; the wallet from `W` (was wallet 4); route class from `route_q.py`; `grid.py` also `ITS_TP` (the wallet's own take profit in the lift, default 2.5) |
| `full_paths.py` | `2026-10-28/fresh/` | SP; `KINDS` filter; keeps `n01`, the landed curve transactions after its buy in its slot and the next (mark 8) |
| `route_q.py` | new | route class from the curve's quote token: C = WBTC-quoted, A = canonical PumpSwap pool vs wSOL, B = vs WBTC only, E = none (`more/pools.py`'s PDA, getAccountInfo). `route_cls.py` read wallet 4's own route, which other wallets do not share. `ROUTECLS=wallet4` uses route_cls.py |
| `create.py` | new (`more/age.py`'s method) | the create slot of each coin it first bought for 0.5+ SOL in another token: the oldest signature on the bonding curve before its buy |
| `marks.py` | new | marks 1-6 and 8 from the files above |

Checked on wallet 4's own data (`SP=.../fresh3 ROUTECLS=wallet4`): `grid.py cap q 1 1.45 9` at 4 open gives P1 +5.19
(+3.22) 153, P2 +12.27 (+9.62) 161, P3 −2.98 (−4.70) 30, the fresh README's "1.45+ floor" row exactly; `marks.py` gives
its P3 +82.00 (+58.80) and the early-sale table (3.5% / 13.6% / 49.0%) as published (`out/H9kuqGKN_*.txt`).

## Fetch (Oct 28, 22:51-23:30 UTC)

`sigs.py WALLET 1792368000` (Oct 19 00:00 UTC) on every candidate; all four were fetched in full, Oct 19 to about
23:00 UTC Oct 28 (none is "far more" than wallet 4's 20,476 signatures in transactions it landed):

| wallet | signatures | failed | landed (fetched by pull.py) |
|---|---|---|---|
| 6anjqMeW | 30,413 | 2,551 | 27,862 |
| AMDEmVoc | 16,436 | 424 | 16,012 |
| Fhbh1DTU | 182,408 | 155,007 | 27,401 |
| dKMjeGJ4 | 52,169 | 18,377 | 33,792 |
| (wallet 4, fresh3, to Oct 28 14:54) | 20,476 | 495 | 19,981 |

Throughput was about 60 transactions a second over 12 fetch processes (the session's HTTPS proxy is the limit).

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
   landing at its slot + 1; and + 3 from `grid.py land`), P1 / P2 / P3, (without the best 2), copies.
8. **The frenzy**: landed transactions on the coin's curve after its buy in its slot and the next (median), on its
   1.45+ SOL trips of coins priced in another token (`full_paths.py`'s n01; wallet 4: `frenzy.py`).

## The table

Wallet 4's row is its own data (`fresh3`, Oct 19 → Oct 28 14:54 UTC) through the same scripts (`out/H9kuqGKN_*.txt`):
`marks.py` with its own route class (`ROUTECLS=wallet4`), `grid.py cap|land q 1 1.45 9` at 4 open, `frenzy.py`. Its
create+0/+1 share is from `07-rework-2026-10-28/wallet-check.md` §6 (47 of 47 measured coins at the create slot or the
next) and `../../../2026-10-28/more/` (age.py: 322 of 323 big buys within 2 s of the create); `create.py` was not re-run
on it.

## Status (Oct 28, 23:26 UTC)

Priority changed at 23:20 (the neighbours search, `../neighbours/README.md`): only 6anjqMeW passes its profile screen, so
6anjqMeW gets the full pipeline on its own history (also at a 0.45 SOL floor, its own size), and AMDEmVoc, Fhbh1DTU and
dKMjeGJ4 only the cheap marks (daily counts, hold, failed share), no backtest. 6anjqMeW and AMDEmVoc are fetched in full;
dKMjeGJ4 and Fhbh1DTU were paused at about 80% so 6anjqMeW's paths come first.

**6anjqMeW does not trade like wallet 4.** It buys 0.5 SOL (p25-p75; 0.25 at p10, 1.0 on 556 coins) of coins priced in
another token, never 1.45+. It sells most coins in one piece within seconds or on fixed timers (10-s bins: 0 s 1,445
trips, 240 s 301, 480 s 197, 740 s 182, 60 s 98, of 3,332), and those one-sale coins lose: −83.52 SOL. Its profit is
the coins it sells in 2-4 parts (1,101 coins, +131.6): a first sale of 10-50% of its tokens 1-7 s after its buy at a
median 1.22x, the rest later. By period (coins priced in another token, first trade a buy, `marks.py` data):

| period | one buy, one sale | one buy, 2+ sales | its whole result (every token, ledger) |
|---|---|---|---|
| P1 Oct 19-22 | 1,800 coins, −16.90 | 395, +36.27 | +32.92 on 4,047 tokens |
| P2 Oct 23-27 | 996, −42.51 | 444, +60.84 | +33.09 on 3,287 |
| P3 Oct 27-28 | 537, −23.86 | 262, +34.54 | +16.54 on 2,200 |

`grid.py` copies one-buy one-sale trips only. For 6anjqMeW that set is exactly the coins it gave up on, so
`full_paths.py` and `grid.py` got `MULTI=1`: a coin it bought once and sold in parts is one trip from its buy to its
last sale, its earlier partial sales being trades on the recorded path.
