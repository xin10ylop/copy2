# How does wallet 4 choose? Hypothesis 1: it follows creators (Nov 18) — FAILS

`c1_creators.py` on the 48 h of other-token launches fetched in full (2,955 coins with a launch buy modelled; our 0.5
SOL at the first trade after the create slot, wallet 4's live model, 0.0345 SOL a round trip):

| coins | buys | a buy | w/o 2% | P(mean>0) |
|---|---|---|---|---|
| (a) wallet 4 bought them (1.3+ SOL), our buy at LAUNCH | 27 | +8.4% | −0.08 | 69% |
| (b) later coins of creators wallet 4 had bought; it skipped them | 27 | −12.9% | −1.89 | 0.1% |
| (c) every other coin | 2,901 | −10.5% | −259 | 0% |

**Corrected (the first run followed a random launch-slot trader's sale as "its sale"): rerun with no sale followed.** (a) +8.4% (27, P 69%), (b) −12.9% (27), (c) −10.5% (2,901). Following its creators fails; wallet 4's coins themselves, bought at the launch, make money: the edge is its CHOICE. `c2_parts.py`: on 24 of its 1.3+ buys, the copy +14.9%, the copy without following its sale +16.0%, a launch buy +13.1% (it buys in the create slot).

## Step 2-3: what wallet 4 sees at the launch (`c3_features.py`, `c4_rule.py`) — no rule reproduces it

On its coins (1.3+ SOL buys, 30 of 4,737 coins) against the rest: the creator's own buy is smaller (median 1.35 against
2.88 SOL), more other buyers in the create slot (4 against 2) with more SOL (6.0 against 2.6), more TTWofwAg quotes
(43% against 23%). A launch rule on these (154 rules with 10+ day-1 buys on coins wallet 4 skipped): even the best one
loses on day 1 (−8.4%, 27 buys), the day it was picked; picked, it makes −16.8% on day 2 (23 buys). Every coin: −10.2% /
−10.5% a buy. What wallet 4 uses is not in the launch slot (likely off-chain: a channel, social posts, the name).
(A first run of c4 gave every rule the same numbers: a late-binding closure; fixed.)
