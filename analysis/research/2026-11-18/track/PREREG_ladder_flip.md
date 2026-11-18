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
