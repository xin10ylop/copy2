# Skipping losing copies without skipping the winners: researcher `fable` (Nov 15)

## The answer

**No rule I can stand behind yet.** One candidate looked real on 3.5 weeks of data and on our real trades, then
went the wrong way on the first buys it had never seen. Nothing else survived the guard against luck.

- **The candidate: skip a coin whose fee tier is 100 basis points or less** (the fee in wallet 4's own buy event,
  protocol + creator: these are coins priced in another coin whose creator set a fee of 0.3% or 1% instead of the
  usual 3%). 96 of the 781 buys.
  - On the study data (Oct 21 - Nov 14) in the bot's run: net **+41.00 SOL against +36.23**, better in each block
    (A +10.45 / +8.79, B +20.26 / +19.43, C +10.30 / +8.02) and at each landing, losing days 3.3 against 5.3 of 23,
    worst day −0.49 against −1.31, deepest fall −2.21 against −2.86; 71 losing copies skipped, 2.7 take profits
    lost of 66 (the freed slots caught others: 65.3 kept), 0.3 of the 20 biggest wins lost. Days drawn again: ahead
    in 98.8% of draws (`out/filters.txt`).
  - On the real trades: it would have skipped 8 of the 20 in the data, **all 8 losers, −2.1515 SOL together**, and
    none of the take profits (`out/filters.txt`).
  - The guard: among 66,430 rules (one or two conditions) the best valid one gains +5.39 SOL; the same search on
    results shuffled inside each block finds as much 4% of the time (`out/rules_tp4.txt`). Borderline.
  - **Then the buys after the study data (Nov 14 17:39 - Nov 15 12:54 Beirut, `out/fresh_check.txt`): 10 low-fee
    copies made +3.91 SOL in the model** (3vhbd6FN +2.45 and Bip1Z2Qc +1.52: a dump right after its buy let the copy
    in at about half its price). The rule would have skipped both. With them, the low-fee copies are 105 at −0.96
    SOL (−1.8% a copy) against +11.3% for the rest: still the weak group, no longer a losing one.
  - No reason behind it either: the same creator fees on coins priced in PUMP, SPCX or WBTC do well (creator fee 30
    bps there: 70 copies, +16.3% a copy; `out/fee_parts.txt`), and the low-fee coins come from 88 different creators
    (`out/creators.txt`).
- **Everything else:** without the fee tier, the best of 62,835 rules gains +3.47 SOL and luck does as well 77% of the
  time; picked on two blocks, the 20 best rules lose on the third in every direction (`out/rules_tp4_nobps.txt`).
  No single feature has a group that loses in all three blocks (`out/scan1.txt`).
- **Bailing out in the first seconds** (57 rules: price under X at T seconds, never above Y by T, more sells than
  buys): 8 are a little better in all three blocks (at most +1.1 SOL of 36), which is what 57 coin tosses give by
  chance; the stricter ones lose take profits (`out/bail.txt`). Nothing.

**What I would do:** not skip anything now. Have the bot print the fee tier on each buy line, and after about 50
more low-fee copies (2-3 weeks) rerun `fresh_check.py`. If they lose again, the rule is one config value: wallet 4's
buy event already carries the fee (`Trigger.fee_bps` in `crates/rugsnipe-long/src/engine.rs`), known the instant
its buy is seen.

## The evidence in short

781 copyable buys (SOL, WBTC, PUMP, SPCX), Oct 21 - Nov 14; live rule (tp 3.0, 600 s, early 30-290 s under 1.5x);
0.5 SOL; blocks A (to Oct 29 12:02 UTC), B (to Nov 6 05:32), C (after).

**The fee tier** (`out/bps_look.txt`, every copy, mean of three landings):

| fee tier | copies | take profits | A | B | C | all | a copy |
|---|---|---|---|---|---|---|---|
| 30 bps | 44 | 1 | −0.48 | −0.35 | −1.39 | −2.23 | −10.1% |
| 100 bps | 41 | 2 | −0.59 | −0.74 | −0.73 | −2.06 | −10.1% |
| all <= 100 | 96 | 4 | −0.88 | −1.32 | −2.28 | −4.47 | −9.3% |
| 125 (PUMP / SPCX coins) | 79 | 16 | +0.50 | +4.57 | +1.45 | +6.52 | +16.5% |
| 300 | 364 | 25 | +7.83 | +8.26 | +2.80 | +18.89 | +10.4% |
| 395 | 89 | 14 | +1.63 | +2.42 | +3.75 | +7.80 | +17.5% |

Share of copies whose price reached 2x within 600 s: 10% for the low-fee coins, 28% for the others.

**Candidate rules on the bot's run** (`out/filters.txt`; mean of landings):

| skip | buys matched | net | A | B | C | take profits lost | without best 5 / 10 | losing days | worst day | deepest fall | ahead in |
|---|---|---|---|---|---|---|---|---|---|---|---|
| nothing | 0 | +36.23 | +8.79 | +19.43 | +8.02 | | +30.11 / +24.71 | 5.3 | −1.31 | −2.86 | |
| fee tier <= 100 | 96 | +41.00 | +10.45 | +20.26 | +10.30 | 2.7 | +34.88 / +29.48 | 3.3 | −0.49 | −2.21 | 98.8% |
| fee tier <= 30 | 49 | +38.45 | +9.42 | +19.62 | +9.41 | 1.3 | +32.33 / +26.93 | 4.3 | −0.95 | −2.59 | 90.8% |
| fee tier 31-100 | 47 | +38.71 | +9.74 | +20.06 | +8.90 | 1.3 | +32.59 / +27.19 | 4.3 | −0.82 | −2.39 | 95.2% |
| its buy moved the price over 1.12x and under 16% of the curve sold | 83 | +39.98 | +11.26 | +19.56 | +9.15 | 1.3 | +33.85 / +28.42 | 3.3 | −1.10 | −2.66 | 98.8% |
| under 10% of the curve sold | 157 | +35.95 | +10.68 | +19.55 | +5.73 | 6.7 | +29.84 / +24.45 | 6.0 | −1.19 | −3.40 | 48.0% |
| every SOL-paid copy | 287 | +32.05 | +4.70 | +18.84 | +8.51 | 16.3 | +26.38 / +21.20 | 2.3 | −1.06 | −2.21 | 18.9% |

("Its buy moved the price over 1.12x and under 16% of the curve sold" came out of the same search; shuffled results
give as much, `out/rules_tp4_nobps.txt`: I do not trust it.)

## What I tried, and what I did not

- **Tried:** 24 features of each buy known at its moment (what we pay with, hops, its buy's size, the price move of
  its buy, the share of the curve sold, the curve's reserve, the fee tier and its parts, trades ahead of it in its
  block and right after, the coin's transactions before its buy, wallet 4's buys in the last 5 / 10 / 30 / 60 min,
  seconds since its last buy and sale, its result on its last 3 / 5 / 10 coins, the hour, our entry premium); 364
  conditions, **66,430 one- or two-condition rules** plus 12 named ones on the bot's run; 57 bail-out rules. The
  coin's creator (733 creators for 781 coins: no use).
- **A bug of mine on the way:** the first feature table left out wallet 4's transactions of the first week, which
  made "wallet 4 idle for hours" look like a signal. Fixed before any result here.
- **Not tested:** rules of three or more conditions; a fitted model (no library here, and 80 take profits is little
  to fit); the coin's name, picture or socials; its holders; who else bought in the block by name (the same copy
  bots appear after its buys: `9SKw`, `RRRb`, `9JJS`, `kurt`, `HnFf`); the bot's real position in the block.
- **Seen on the way:** wallet 4 buys almost only brand-new coins (631 of 781 have no history before its buy's
  second), so "the coin's history" has nothing to offer.

## Run order

```
python3 -I features.py SPD SKIPQ        # the feature table (one RPC call a coin, cached) -> SKIPQ/features.json
python3 -I features2.py SPD SKIPQ       # wallet 4's own state
python3 -I quote_look.py SPD SKIPQ > out/quote_look.txt     # adds the quote token
python3 -I fee_parts.py SPD SKIPQ > out/fee_parts.txt       # adds the fee's parts and the creator
python3 -I scan1.py SKIPQ > out/scan1.txt                   # each feature alone
python3 -I rules.py SKIPQ 4 > out/rules_tp4.txt             # the wide search and the guard
EXCL=bps python3 -I rules.py SKIPQ 4 > out/rules_tp4_nobps.txt
python3 -I bps_look.py SKIPQ > out/bps_look.txt
python3 -I creators.py SKIPQ > out/creators.txt
python3 -I filters.py SPD SKIPQ > out/filters.txt           # the candidates on the bot's run, days redrawn, real trades
python3 -I bail.py SPD SKIPQ > out/bail.txt                 # part 2
python3 -I fresh_check.py ALL SKIPQ > out/fresh_check.txt   # the buys after the study data (ALL = the wider dataset)
```
`SPD` = the float study's data folder, `SKIPQ` = a scratchpad folder for the feature table and the cache.
