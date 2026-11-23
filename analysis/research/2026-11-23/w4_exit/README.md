# Wallet 4's exit review (Nov 23; the frozen exit's review was due Nov 29, the owner asked for it now)

`exit_review.py`: wallet 4's first buys of 1.3+ SOL paid in our floats (what `rugsnipe-long` copies), Nov 17 13:17 to
Nov 23 14:07 UTC (its Helius history, capped at 10,000 transactions), 92 copies at 1 SOL, refused over 1.5x, COST 0.0064;
the live exit against fixed alternatives, no picking, in 4 time blocks (`out_exit_review.txt`):

| Exit | Blocks 1 / 2 / 3 / 4 (% a copy) | All | SOL | W/o best 2% |
|---|---|---|---|---|
| **live: tp 4, 600 s, sell pressure 5/60, stall 180, its sale 30-290 s** | +12.5 / +1.2 / +11.3 / -2.9 | **+5.5%** | +5.09 | +0.40 |
| live, sell pressure 10/60 | +15.3 / +7.7 / +11.4 / -3.8 | +7.7% | +7.06 | +2.28 |
| live, sell pressure 8/60 | +11.4 / +8.3 / +9.6 / -3.7 | +6.4% | +5.89 | +1.12 |
| live without its sale | +12.5 / +0.3 / +10.7 / -3.1 | +5.1% | +4.69 | -0.00 |
| live without sell pressure | +12.6 / +5.2 / +6.0 / -14.5 | +2.3% | +2.15 | -2.79 |
| tp 4 / 600 / stall 180 only | +12.5 / +3.2 / +5.4 / -16.0 | +1.3% | +1.16 | -3.78 |
| tp 2x / 120 s | +1.1 / -5.8 / +3.3 / -6.8 | -2.1% | -1.90 | -3.76 |
| its sale (to 600 s) | +2.4 / +12.0 / -5.0 / -18.5 | -2.3% | -2.07 | -6.61 |
| tp 3x / 420 / stall 240 + its sale | +2.5 / +0.9 / -5.0 / -9.5 | -2.8% | -2.58 | -5.76 |
| held 300 s | -4.8 / -6.2 / +6.7 / -12.3 | -4.2% | -3.82 | -8.81 |
| tp 3x / 420 / stall 240 (the other units') | +1.9 / -3.0 / -6.7 / -12.4 | -5.1% | -4.65 | -7.83 |

1. **The live exit stays.** It is the best of the plain alternatives and within the noise of the best variants (a less
   sensitive sell pressure, 8/60 or 10/60 s, +1 to +2 points on 92 copies, against about 5 points of noise): picking one
   of them on 6 days is the overfitting the freeze was set against.
2. **Every exit lost in block 4 (Nov 22 06:43 to Nov 23 14:07 UTC):** the losing run is wallet 4's coins, not the exit
   (its own result on its copyable coins went negative on Nov 23, `../w4_floats/README.md`).
3. **Sell pressure earned its place:** without it block 4 is -14.5% against -2.9%; the many sell-pressure exits in `qqq`
   cut losses.
4. The other units' exit (tp 3x / 420 / stall 240) loses on wallet 4 (-5.1%): each wallet keeps its own exit.
Live since the 0.5 SOL restart: 32 real, -1.45 SOL (-9% a copy); the model's live exit on block 4: -2.9% (23 copies).
