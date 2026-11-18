# How does wallet 4 choose? Hypothesis 1: it follows creators (Nov 18) — FAILS

`c1_creators.py` on the 48 h of other-token launches fetched in full (2,955 coins with a launch buy modelled; our 0.5
SOL at the first trade after the create slot, wallet 4's live model, 0.0345 SOL a round trip):

| coins | buys | a buy | w/o 2% | P(mean>0) |
|---|---|---|---|---|
| (a) wallet 4 bought them (1.3+ SOL), our buy at LAUNCH | 27 | −0.1% | −1.24 | 46% |
| (b) later coins of creators wallet 4 had bought; it skipped them | 27 | −10.9% | −1.66 | 0.9% |
| (c) every other coin | 2,901 | −10.7% | −254 | 0% |

Following its creators is no better than buying everything. And the striking line is (a): the same coins bought at
launch make −0.1%, while copying wallet 4 (landing just after ITS buy, following ITS sale) made +25% a copy on this
window (`../../2026-11-17/wallet_hunt/out/m4_direct.txt`). The edge is not in the coin alone: it is in wallet 4's
moment and its sale.
