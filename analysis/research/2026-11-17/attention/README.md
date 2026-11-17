# What predicts attention? (Nov 17)

The owner, Nov 17: "think well, about what makes a memecoin successful, with the data that we have access to ... yes it
is an attention market, but isnt there something that predicts attention?"

## The logic

Attention is not random. It is delivered by a supply chain, and each link leaves a trace on chain before the crowd arrives:

1. **The creator and team** prepare: a record, a community, a promotion deal. Visible days before: the creator's past
   launches and how they ended, how often it launches, and its funding.
2. **The distributors** (callers, KOLs, VIP channels) buy before they post. Measured on Nov 17: wallet 4 buys a median
   91 s before a SolHouse VIP alert; the wallets on the VIP coins buy 68-80 s before (`telegram/`, `winners/`). Their
   buys are visible a minute or more before the attention.
3. **The crowd** arrives after the post: many distinct new buyers, accelerating. That is the attention itself, and by
   then the price has moved (the VIP study: following the alert loses about 18% a copy).

So whatever predicts attention must be visible at link 1 or 2: who made the coin, and who buys it in its first minute.
Whatever everyone can see (volume, holders, market cap after the fact) is already in the price.

## Pre-registered (written before the outcomes were read)

Universe: every pump launch of Nov 15 01:07 to Nov 17 01:07 UTC (`SP/market/creates.json`, 83,432 creates).
Outcome: the coin graduated (its bonding curve complete, read on Nov 17 night, `a1_outcomes.py`).
Split by time: **pick on the first 24 h, score on the second 24 h**. Report the test half's rate in the top tenth by
the feature against the base rate, and how many coins that is. Every feature uses only what was known at the decision
time (a creator's record counts only its earlier coins).

| | Hypothesis | When it is known | Data |
|---|---|---|---|
| H1 | A creator whose earlier coins graduated graduates more; a serial launcher less | at the create | all 83k |
| H2 | The quote token matters (SOL coins vs other-token coins) | at the create | all 83k |
| H3 | Time of day (US hours) | at the create | all 83k |
| H4 | Bundles: much of the supply bought in the create slot predicts failure | at the create slot | other-token live coins (paths) |
| H5 | Breadth: many distinct buyers in the first 60 s for the SOL put in | 60 s | other-token live coins |
| H6 | Who buys: first-minute buyers with a record of early buys into earlier winners | 60 s | other-token live coins |
| H7 | Wallet 4's pick: what, known at the create, separates the coins it snipes from the rest | at the create | other-token coins |

A feature that predicts graduation is not yet a trade: a pass goes on to the copy model (entry price at the decision
time, 0.0345 SOL a round trip) before it means money.

## Results so far (Nov 17-18; `out/a2_create_time.txt`, `a3_w4_pick.txt`, `a5_create_features.txt`, `a6_w4_creators.txt`, `a7_bursts.txt`)

- 82,790 launches, 1.83% graduated. Stable on both days: the creator's first launch of the day x1.8, no tips in the create
  x1.7, a dev buy over 5 SOL x3.9. Narrative bursts (same-theme launches in the 30 min before): nothing (x0.8-1.1). Mayhem:
  nothing on the full set.
- Wallet 4 buys at the create (98% within 2 s) and its picks graduate 8.86%, the same creators' other coins 3.07%, the
  rest 1.69%. It never buys a mayhem coin and never buys inside the create transaction.
- The score (signals kept on day 1: no mayhem, no tips, dev buy > 2, first launch, 1-15 same-theme launches before):
  score 4: 5.79% then 5.69%; score 5: 21.4% then 10.7%. Wallet 4's score 2-3 picks still graduate 6-8% against 1-2%:
  it reads more than the score.

## The money test, pre-registered (Nov 18 ~00:30 UTC, before any path is fetched)

Graduating is not profit. **Buy every score 4+ coin at its create** (the first trade 1 s or more after the create, as a
bot reading the creates would land; refused past 1.25x the create's price), 0.5 SOL, the fixed exits of `tg_test.py`
(tp2/tp3/tp5, graduation, sell at 10/30 min). A random 250 of day 1's score 4+ coins and 250 of day 2's (seed 7,
`a8_money.py`). **Pick the exit on day 1, score it on day 2 at 0.0345 SOL a round trip. Pass: positive on day 2, and
positive without the best 5.**
