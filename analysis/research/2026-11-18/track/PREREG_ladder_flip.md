# The ladder flip, frozen Nov 18 ~01:40 UTC, before groups C-F are scored

Found on ladder group A (4sgdNABj, AsDCYFPT; `out/t5_*.txt`): holding loses (the coins dump within minutes; 5-minute and
30-minute exits lose); the first 30 s after the ladder carry the followers. 4sgdNABj, all 265 copies, "ours x1.2 cap 30 s":
positive in 7 of 8 day-blocks, +9.4% / +9.3% / +11.5% a copy in the three UTC blocks; after the screen, 110 copies, -4.0%
then +15.6% (+5.8% a copy overall).

**The rule, frozen:**
- Trigger: a launch whose create slot holds buys of 2+ ladder sizes (1.10 / 1.54 / 2.18 SOL, within 0.005) from different
  wallets.
- Entry: one slot after the ladder, at any price (`PMAX=1000`), 0.5 SOL.
- Exit: +20% over **our** entry price, or 30 s after the ladder, whichever first; the curve completing sells there.
- Cost 0.0345 SOL a round trip.

**Scored once** on groups C-F (one wallet each: 64Dn57gX, H2nsBdjF, EhS8bGVC, Gf9gk8sZ; never used to pick the exit), all
their copies and those after Nov 17 01:07 UTC separately (`t5_angles.py`, exit "ours x1.2 cap 30s").
**Pass:** positive; positive without the best 2%; bootstrap P(mean > 0) 95%+.

## The same flip on the dropped wallets (Nov 18 ~01:50 UTC, `out/t5_dropped_*.txt`, every copy of each)

| wallet | copies | the frozen flip | without the best 2% | P(mean > 0) |
|---|---|---|---|---|
| 6ua7w2Gv holdout | 274 | −10.4% | −15.06 | 0% |
| 6ua7w2Gv exploration | 206 | −7.7% | −8.37 | 0% |
| 8Fux3NDf | 299 | −18.6% | −37.85 | 0% |
| Dj216RQs | 300 | −10.2% | −41.41 | 14% |
| AnHnjfGJ | 149 | −5.4% | −4.91 | 0% |
| q2jJy82z | 191 | −6.2% | −6.89 | 0% |
| q2q38wAb | 150 | −11.5% | −9.38 | 0% |

Every one fails; selling at the very next trade loses too (−4% to −9%). The flip's edge on group A is specific to the
ladder's launches (buyers arrive right after the ladder), not a property of the exit.

## Why 8Fux3NDf and Dj216RQs fail (Nov 18 ~02:15 UTC, `out/t5_dropped_8Fux3NDf.txt`, `..._Dj216RQs.txt`)

Not the entry: 282 of 299 and 299 of 300 copies land within 1.05x of their own price. At that price their coins still
lose under every exit (its own sale −13.3% / −3.4%; sell at the next trade −4.8% / −6.3%; 30 s flip −20.4% / −10.4%;
5 min −23.5% / −7.4%). Their coins graduate more often than chance, but the price does not rise in a way a follower can
catch; their own profit is selling within seconds (8Fux3NDf a median 5 s). Closed.

## RESULT (Nov 18 ~02:45 UTC): the frozen flip PASSES on every unseen group

Groups C-F, all copies (`out/t5_<w>.txt`), the frozen exit "ours x1.2 cap 30s", 0.0345 SOL a round trip, any price:

| group | copies | a copy | halves | without the best 2% | P(mean > 0) |
|---|---|---|---|---|---|
| C 64Dn57gX | 125 | +23.3% | +7.7% / +38.6% | +13.20 | 100% |
| F H2nsBdjF | 111 | +26.5% | +4.0% / +48.6% | +13.28 | 100% |
| D EhS8bGVC | 42 | +28.5% | +21.5% / +35.5% | +5.54 | 100% |
| E Gf9gk8sZ | 42 | +32.3% | +14.9% / +49.6% | +6.28 | 100% |

**After every screen** (coins from Nov 17 13:49 UTC, the end of the week screen that picked groups C-F; all six ladder
wallets pooled, one copy per coin; `out/t6_grad_check.txt`): 108 coins, **+27.59 SOL, +51.1% a copy**, halves +42.2% /
+60.0%, without the best 2% +25.73, bootstrap 100%. **No exit falls at a graduation** (the flip sells within 30 s; the
coins that complete do so a median 131 s after the ladder), so the curve-top graduation price of the model plays no part.
(The slower exits' profit is all in the 17% of coins that graduate: sp10/60s +108% a copy at the curve top, +83% at 0.8x,
+46% at 0.5x.)

**Limits:** one operation, seen since about Nov 15; the clean sample is about 11 hours (108 coins); the model lands one
slot after the ladder and sells into the trades that followed, with our own buy's weight on the curve and the 0.0155
fill bias, but the live bot does not detect a ladder today (it follows wallets): a new trigger is needed.
