# Skip losing copies without skipping the big winners (Nov 15, researcher "opus")

The owner's question: "a very digged deep study, on how we may skip some losing copies without skipping the big
winning trades."

## The answer

**Yes, one rule holds up: do not copy a coin whose curve fee is under 1.25% (`bps < 125`).** The fee is the
protocol fee plus the creator fee of wallet 4's own trade. The bot already reads it from that trade's event
(`Trigger.fee_bps` in `crates/rugsnipe-long/src/detect.rs`), so it is known in the same millisecond as the buy. In
the data the low values are 1 to 120 bps (mostly 30 and 100). They are 98 of the 781 buys.

Over the 781 buys (Oct 21 18:30 UTC to the end of the data on Nov 14; 0.5 SOL, 2 open, the live exit rule, mean of the three
landings; `out/robust.txt`, `out/filters.txt`):

| | copies | take profits (lost / new) | 20 biggest wins lost | net | without best 5 | without best 10 | A | B | C | losing days (of 23) | worst day | deepest fall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| live rule, no filter | 629.7 | 66.0 | | +36.23 | +30.11 | +24.71 | +8.79 | +19.43 | +8.02 | 4 | −1.31 | −2.86 |
| **skip bps < 125** | 554.3 | 65.3 (2.7 / 2.0) | 0.3 | **+41.18** | **+35.06** | **+29.66** | **+10.48** | **+20.26** | **+10.44** | **1** | **−0.13** | **−2.20** |

- **What it costs in winners:** 2.7 take profits a run are lost and 2.0 come back through the freed slots. Of the
  20 biggest wins, 0.3 are lost on average over the three landings.
- **What it saves:** 66.0 losing copies skipped (−7.83 SOL); the skipped winning copies had made +4.33 SOL.
- **Net: +4.95 SOL.** It is better in each block A / B / C, at each landing in each block
  (9 of 9 cells), and without each block's best 2.
- **Our real trades:** 9 of the bot's real trades had a fee under 125. **All 9 lost, −2.26 SOL together.** The
  rest made +2.48 SOL (`out/robust.txt`).

How sure? Fairly sure. It is not certain:
- **The threshold is smooth.** Any cut from 31 to 121 bps helps in all three blocks (+2.22 to +4.95). The cut
  stops just under 125, the lowest standard fee tier of PUMP- and SPCX-quoted coins. Cutting at 126 takes in that
  tier (79 more coins) and loses in block B.
- **There is a reason behind it.** Low-fee coins run less after wallet 4's buy (`out/why.txt`). Median peak in
  600 s: 1.22x against 1.42x. Coins that reach 3x: 4.1% against 13.5%. They have half the trades in the first 60 s
  (18 against 32). Wallet 4 itself loses on them (mean −2.4% against +24.9%). The same holds for SOL-paid,
  WBTC-paid and PUMP-paid copies on their own.
- **Chance check 1, days redrawn:** the filter is ahead in 99.1% of the 10,000 day draws.
- **Chance check 2, the whole search on shuffled data:** in 1 of 200 shuffles the search found a filter that held
  in all three blocks and gained +4.95 SOL or more. In 107 of 200 it found one that held in all three blocks,
  but with less gain.
- **Chance check 3, pick on two blocks and score on the third:** each way round, the pick on the other two blocks
  was this rule, and it held on the third.
- **The weak point:** 98 low-fee coins hold only about 4 take profits. A few big low-fee winners in the future
  would erase the gain.

**Nothing else holds up:**
- **Entry filters, one at a time:** of the 150 entry filters, the only ones better in all three blocks are this rule
  and a weaker cut of the same rule. Random skips of the same share hold in all three blocks in 0 to 3.8% of draws.
  Among the things that do not work: our entry premium (a tighter refusal limit loses at every value), the size of
  wallet 4's buy, its price impact, how far along the curve is, the coin's age and trades before the buy, the
  creator, the developer's buy, wallet 4's recent activity and results, the hour and the weekday.
- **A second filter on top of the fee rule:** 1 of 145 passes (`w4_last10_ret > 0.588`, +1.82). That is the
  chance rate, and the rule alone loses in block A. Rejected.
- **All features in one model** (ridge regression, fitted on two blocks, used on the third): it helps block A and
  loses in B and C (in 11 of 12 tries without the fee rule, 12 of 12 with it) (`out/model_cv.txt`).
- **Bail-outs in the first 10-60 s** (reported apart, `out/bail.txt`): 1 of 81 rules passes: at 45 s, sell if
  under 0.8x our entry. It gains +0.87 SOL and adds a losing day, and its neighbours are mixed. Rejected. Selling
  early on a weak start cuts too many later take profits. For example, "at 10 s, never above 1.1x" loses 13.3
  take profits and −12.27 SOL.

**What the bot would need:** a new config value, for example `min_fee_bps = 125`, in `rugsnipe-long`. It skips a
buy when `0 < trigger.fee_bps < min_fee_bps`. A fee of 0 means "not in the event", so it never skips those. The
fee is already decoded from wallet 4's trade (`txlite.rs`: fee + creator fee), so no new data and no delay. It
needs an engine test and a line in `docs/20-long-copy.md` §3 (the repo's convention). I did not change any code.

## Evidence

### The baseline (`out/base.txt`, `out/filters.txt`)
The live rule is tp 3.0, 600 s, and his sale followed at 30-290 s under 1.5x. The bot holds 2 copies at once
(SOL 1, WBTC 2, PUMP 1, SPCX 1). F.sim gives +40.30 / +26.28 / +42.10 SOL at landings 4 / 8 / slot+1; my run
(`common.sim`) gives the same. The mean is +36.23, as in `../../2026-11-14/float_exits/out/review_az.txt`. On the
23 full Beirut days: 4 losing days, worst −1.31, deepest fall −2.86, as in `../../steady/`.

### Looking first (`out/explore.txt`, every copy on its own, no slot limit)
- Wallet 4 buys at launch. 378 of 781 buys land in the coin's creation slot and 325 one slot later
  (`slots_since_create`). The coin has 1-14 transactions before its buy.
- **Every group of every feature makes money on average except the low-fee coins.** Over the groups of every other feature
  (categories included), the net a copy is +0.0066 to +0.1131 SOL. The low-fee coins together: −0.0474 a copy,
  2.7 take profits in 98 (`out/robust.txt`).
- Positive in every group means skipping a group throws away profit, unless the freed slot buys something better.
  That is why so few filters work.
- The best single signals for "reaches 3x" are weak (AUC 0.55-0.59): how far along the curve is, market cap, the
  developer's buy share, and the trades before the buy.

### The fee rule from every side (`out/robust.txt`)

| skip when bps < | skipped | net | A | B | C | losing days | worst day | days ahead |
|---|---|---|---|---|---|---|---|---|
| (none) | 0 | +36.23 | +8.79 | +19.43 | +8.02 | 4 | −1.31 | |
| 31 (or 50) | 49 | +38.45 | +9.42 | +19.62 | +9.41 | 2 | −0.86 | 91.6% |
| 76 | 53 | +38.56 | +9.48 | +19.62 | +9.46 | 2 | −0.89 | 92.5% |
| 101 | 96 | +41.00 | +10.45 | +20.26 | +10.30 | 1 | −0.13 | 99.0% |
| **125** | 98 | **+41.18** | +10.48 | +20.26 | +10.44 | 1 | −0.13 | 99.1% |
| 126 (takes in the 125 tier) | 177 | +36.94 | +11.41 | +16.19 | +9.33 | 3 | −0.38 | 58.2% |
| 196 | 242 | +29.13 | +10.33 | +10.98 | +7.82 | 3 | −1.29 | 13.7% |

Each landing in each block, change against the baseline (bps < 125): landing 4 +1.22 / +0.99 / +1.74; landing 8
+1.18 / +0.69 / +3.13; slot+1 +2.69 / +0.82 / +2.39. Without each block's best 2: +1.66 / +0.83 / +2.42.

By kind of copy (bps < 125 applied to one kind only): SOL +2.39 (69 skipped), WBTC +1.85 (22), PUMP +0.64 (7). No
SPCX coin has a fee under 125. Every copy on its own: SOL-paid low-fee −0.0390 a copy (2.7 take profits in 69);
WBTC-paid −0.0734 (0 in 22); PUMP-paid −0.0492 (0 in 7).

Our real trades: 20 of the 24 are among the 781 buys (the other 4 are not in the data). The 9 skipped:
7dDprVHP −0.1106, GZn6HC8d −0.3763, 3EKoHX4f −0.0600, GLmWEbqA −0.2837, FAVdiH3q −0.0851, KgcdZjU4 −0.2493,
oxbezHbo −0.4291, EH6yuh4Y −0.4260, 6KpdMXAS −0.2420. All are SOL-paid. The 3 real take profits in the data are kept. These
coins are inside the study period, so this agrees with the model on the same coins; it is not a new sample.

### Why low fee (`out/why.txt`)
Fee values among the 98: 30 (44 coins), 100 (41), and 13 others from 1 to 120. They are spread over many quote
tokens (the top one, `C5xph2yL`, has 18) and over the blocks (A 46, B 20, C 32). The fee is protocol plus creator
fee (`txlite.rs`), and for most quote tokens the usual total is 300. So these are most likely coins whose creator
set a low or zero creator fee. I did not decode the two parts separately. After wallet 4's buy they draw fewer
trades and fewer traders, and they run less (see the answer above).

### Chance (`out/filters.txt`, `out/robust.txt`)
- Random skips of 5 / 10 / 20 / 30 / 40% of the buys hold in all three blocks in 3.8 / 1.8 / 0.5 / 0 / 0% of 400
  draws each. Their median change is −1.46 to −13.12 SOL.
- The whole 150-filter search on data with the features shuffled across the buys, 200 times: on average 0.88
  filters hold in all three blocks per shuffle (at most 5). A gain of +4.95 or more happened in 1 shuffle of 200.
  The largest gains among the shuffles: +5.14, +4.52, +3.92, ...

## Filters tried (count)
- 150 single entry filters (`filters.py`, after dropping duplicates): 25 numeric features, each with its lowest or
  highest 10 / 20 / 30 / 40% skipped. Also the kind of copy, the route, the weekday, 6-hour windows, the creation
  check, a creator seen before, and the refusal limit at 1.05 / 1.10 / 1.15 / 1.20.
- 12 fee thresholds and 3 single-kind versions of the fee rule (`robust.py`).
- 145 second filters on top of the fee rule (`filters2.py`).
- 36 ridge-model variants (`model_cv.py`).
- 81 bail-out rules (`bail.py`).
- In all, 427 rules were scored. Only the fee rule survives.

## Not tested
- The creator's own history beyond our 781 coins (their other launches, wallet age). The creator is known only from
  the creation transaction, and "creator seen before" among our coins showed nothing.
- Holders, social links and metadata of the coin.
- Wallet 4's buys under 1.45 SOL or a whole-wallet loss streak (I only used its 1.45+ SOL buys and its own results
  on the coins in our set).
- The two parts of the fee separately (protocol and creator). A rule like "under the quote token's usual fee"
  (catching the 150 and 200 bps coins) was not tested.
- Bail-outs on buyer counts or buy volume (only trade counts and price were used), and bail-outs combined with the
  fee rule.
- Other stakes. All runs are at 0.5 SOL a copy, and the bot runs 0.3 SOL now.
- The model is the raw model of `../../2026-11-14/float_exits/lib.py`. Its known miss on real trades is not
  corrected here.

## Run order
`SPD` = `/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/floatq`. `SKQ` = the cache
folder `.../scratchpad/skipq_opus`, hard-coded in `common.py`. The RPC URL is read from the scratchpad, never
printed.
```
python3 -I fetch_before.py SPD SKQ > out/fetch_before.txt   # the coin's signatures before its buy, then its creation tx (RPC, cached)
python3 -I base.py SPD SKQ > out/base.txt                    # the model once: every copy x 3 landings + features -> SKQ/base.pkl
python3 -I explore.py > out/explore.txt                      # each feature in groups, AUC
python3 -I filters.py > out/filters.txt                      # 150 entry filters, blocks, pick-on-two, random skips
python3 -I robust.py > out/robust.txt                        # the fee rule: thresholds, cells, kinds, real trades, shuffled search
python3 -I why.py SPD > out/why.txt                          # what low-fee coins do after its buy
python3 -I filters2.py > out/filters2.txt                    # a second filter on top
python3 -I model_cv.py > out/model_cv.txt                    # all features in one model, fit on two blocks
python3 -I bail.py SPD > out/bail.txt                        # bail-outs in the first 10-60 s
```
`common.py` holds the shared parts: the bot's run with a skip rule (a skipped copy frees its slot), the measures,
and the day bootstrap.
