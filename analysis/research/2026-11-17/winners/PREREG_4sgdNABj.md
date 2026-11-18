# 4sgdNABj: the rule, frozen Nov 18 ~00:50 UTC, before the rest of its sample is modelled

Found on the first 64 of its 265 sampled buys (`out/study_4sgdNABj_interim*.txt`): at the usual 1.25x refusal, 55 of 63
copies are refused (the launch runs past 1.25x within a slot of its buy); with the limit at 2x every copy lands (none
between 2x and 10x). At 0.0345 SOL a round trip, sell pressure 10/60 +20.9% then +45.5% a copy, 5/60 +5.3% then +50.8%;
without the best 5 negative in both halves under every exit.

**Frozen:** copy its buy one slot after, refused past **2x** its price (`PMAX=2`), 0.5 SOL, exit **sell pressure 5 sales
in 60 s** (the plateau with 10/60; our standard), else 1,800 s.
**Scored once on the copies not in the first 64** (`w14_score.py`, the full study minus the interim's coins).
**Pass:** 40+ copies; positive at 0.0345; positive without the best 5.
