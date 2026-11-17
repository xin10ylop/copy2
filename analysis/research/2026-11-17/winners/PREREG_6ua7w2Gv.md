# 6ua7w2Gv: the deeper study, written before it starts (Nov 17, ~23:50 UTC)

The owner, Nov 17: "these are good results, digging deeper will certainly improve alot".

**Where it stands** (206 of its 300 sampled copies, `out/study_6ua7w2Gv_partial*.txt`): best exit on the first half, sell
pressure 5 sales in 60 s: +9.9% a copy, then +1.0% on the second half at 0.01 SOL a round trip; +5.0% then −3.9% at 0.0345.
Without the best 5, negative in both halves. Its profit is in the coins the SolHouse VIP alerts after its buy (23 copies).

**The sets.** It made 2,939 copyable buys since Nov 3 (`vipw_res.json`: 1,864 before, 965 in the screen, 110 after).
- Exploration: the 300 already sampled (seed 7, the first 300 of the shuffle). Everything is tried here.
- Holdout: the next 300 of the same shuffle (`OFFSET=300 SUFFIX=_holdout`), disjoint. **Not fetched until the rule below is
  frozen and committed.** Scored once.
- Forward: its buys after Nov 18, if the holdout passes.

**What is explored** (logic first: what, known at its buy, says the attention is coming):
1. The coin at its buy: the attention study's create-time signals (`../attention/`: mayhem, tips in the create, dev buy,
   the creator's first launch of the day, the creator's record), the coin's age, the curve sold.
2. The market at its buy: buys and sells by others in the 60 s before, distinct buyers.
3. Its own buy: size, and whether it adds to a coin it already holds.
4. The exit, near sell pressure 5/60 only (a plateau, not a peak): 3-10 sales, 30-90 s.

**Pass, on the holdout, at 0.0345 SOL a round trip:** positive; positive without its best 5; at least 40 copies kept. The
rule is fixed before the holdout is fetched: no change after it is seen.

## The rule, frozen Nov 17 ~23:55 UTC, before the holdout is fetched

Found on the exploration set (206 of the 300 sampled copies; `out/explore_6ua7w2Gv*.txt`, about 40 groups compared, so
luck alone could make one or two look good in both halves; that is what the holdout is for):

- **Copy 6ua7w2Gv's buy only when the coin's dev bought more than 0 and at most 2 SOL in its create transaction.**
- **Exit: sell pressure, 5 sales by others within 60 s, counted from 30 s after our buy**; else at 1,800 s; the curve
  completing sells there (`wallet_study.py` `sim(sp=(5, 60))`).
- Exploration, at 0.0345 SOL a round trip: 88 copies, +6.89 SOL (+15.7% a copy), first half +17.4%, second +14.0%,
  −0.68 without the best 5. Neighbours: 10 sales in 60 s +14.7%; dev buy 0 SOL −25%, over 2 SOL −11.5%.
- The logic: no dev buy, no stake; a big dev buy, a bag to dump; a moderate one, a stake without a dump.

**Holdout:** `OFFSET=300 SUFFIX=_holdout` (the next 300 of the same shuffle) and `w9_buyctx.py` on it, scored once by
`w11_holdout.py`. **Pass:** at least 40 copies kept; positive at 0.0345 SOL a round trip; positive without the best 5.
