# A steadier exit, even for less profit? (Nov 15)

The owner: "something more consistent and less dependent on luck that coins go to tp, even if profits drop a bit".
`steady.py` scores 150 exit rules on steadiness over 23 full Beirut days (Oct 22 - Nov 13; 781 buys of the four live
kinds; 0.5 SOL, 2 open, raw, each day the mean of three landings): negative days, the worst and 3rd worst day, the
deepest fall from a high, the share of the total made by the best 5 trades, and the total without the best 5 and 10.
Rules: take profit 1.5-3.0 at once; part sales (25/50/75% at 1.2x-2.5x) with the rest at tp 3.0 or the timer;
trailing stops; stops; timers 300 / 600 / 1200 s. The model now takes a trailing stop (`lib.py` `model`, `trail`).

    python3 -I steady.py SPD > out/steady.txt

**Results (`out/steady.txt`):**
- **The live rule (tp 3.0, 600 s) is already the least dependent on lucky trades:** its best 5 trades make 17% of its
  +37.21 SOL, and without its best 10 it keeps +25.64, the most of all 150 rules. 4 negative days of 23, worst −1.31,
  deepest fall −2.86.
- **Part sales at 1.2x-1.4x make it less steady, not more:** 5-8 negative days, worst days no better, and much less
  profit (25% at 1.3x +28.57; 50% at 1.3x +19.97; 75% at 1.3x +10.97). The coins that touch 1.2-1.4x and fade still
  lose on the rest, and the winners are cut.
- **The steadiest by negative days** are a small part sale with a 300 s timer: 25% at 1.5x, tp 3.0, 300 s: 2 negative
  days (one in each half), 3rd worst day +0.09, deepest fall −2.61, total +30.69 (−18%); 25% at 2.0x, tp 3.0, 300 s:
  2 negative days, +34.14 (−8%), but the deepest fall −3.18. Picked out of 150 rules on the same days; the gain is 2
  losing days fewer in 23, within the noise.
- **The smallest falls** come with no take profit: 50% at 1.5x, the rest on a 300 s timer: −1.98, total +29.92, but
  the best 5 trades make 32% of it (more dependent on big runs, not less).
- No rule is steadier on every measure. **The live rule stays.** The bot does not sell part of a position today; it
  would be an engine change, not worth it for this.
- What does make the days steadier is more copies a day (more chances at a take profit): the new floats
  (`../all_tokens/`) and possibly a third open slot.
