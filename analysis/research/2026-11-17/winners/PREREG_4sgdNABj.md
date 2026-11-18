# 4sgdNABj: the rule, frozen Nov 18 ~00:50 UTC, before the rest of its sample is modelled

Found on the first 64 of its 265 sampled buys (`out/study_4sgdNABj_interim*.txt`): at the usual 1.25x refusal, 55 of 63
copies are refused (the launch runs past 1.25x within a slot of its buy); with the limit at 2x every copy lands (none
between 2x and 10x). At 0.0345 SOL a round trip, sell pressure 10/60 +20.9% then +45.5% a copy, 5/60 +5.3% then +50.8%;
without the best 5 negative in both halves under every exit.

**Frozen:** copy its buy one slot after, refused past **2x** its price (`PMAX=2`), 0.5 SOL, exit **sell pressure 5 sales
in 60 s** (the plateau with 10/60; our standard), else 1,800 s.
**Scored once on the copies not in the first 64** (`w14_score.py`, the full study minus the interim's coins).
**Pass:** 40+ copies; positive at 0.0345; positive without the best 5.

## Amendment, Nov 18 ~01:15 UTC, before the score (stricter, not looser)

A flaw: the candidates were picked on the 48 h screen (Nov 15 01:07 - Nov 17 01:07 UTC) **because** their buys of
those days graduated, so their copies of those days are biased upward. The clean test is **only the buys after Nov 17
01:07 UTC** (unseen by the screen). `w14_score.py` reports both; **the pass is judged on the after-screen buys only**,
with the same bar (positive at 0.0345, positive without the best 5; 20+ copies, the after period being one day). The
same applies to every launch picker (B4BMZH3T has no buy after the screen yet: its result so far is in-sample only).

B4BMZH3T (Nov 18 ~01:25 UTC): its last pump trade is Nov 16 08:13 UTC (its later transactions are not pump trades), so it has no buy after the screen: its 42 copies (in-sample, +21% then +33% under its own sale at 2x) cannot be scored fairly. Parked, with 8QzUkGJi (quiet since Nov 16 21:41).

AsDCYFPT (Nov 18 ~01:15 UTC, group A of the ladder, the 1.1 SOL wallet): at 1.25-2x, 132 of 150 copies refused (the rest of the ladder buys after it in the same slot); paying any price, 150 copies +20.5% a copy, but after the screen 67 copies -13.6% a copy at 0.0345. Fails the clean test.
