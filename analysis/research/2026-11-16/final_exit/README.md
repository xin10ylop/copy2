# The last exit study before the freeze (Nov 15 night)

The owner: "recompute deeply the exit strategy, when we sell after him and the holding and everything after adding
the new filters ... a smart combination that is not overfitted and most importantly smart and logic. After the study
now we stop making changes."

Method (`final_exit.py`, `out/final_exit.txt`): each part of the exit is one mechanism with a few coarse values, changed
**alone** against the live setup (tp 4.0, timer 600 s, its sale followed 30-290 s under 1.5x, `sell_pressure
[5, 60, 30]`, `stall_s 180`); a part goes into a combination only if it is ahead in all three blocks; the result is
walked forward (picked on A, scored on B; picked on A+B, scored on C). 1,238 buys, 0.5 SOL, 2 open, mean of three
landings. **The noise, measured:** when the 24 days are drawn again, a one-change gain moves by about ±3.4 SOL (half
the 5%-95% band, the median over 53 changes). A difference under that is not a finding.

    python3 -I final_exit.py CQ ALL > out/final_exit.txt

## Where the money comes from: the live setup by what wallet 4 did (every copy, landing 4)

| what it did | copies | net | a copy | won |
|---|---|---|---|---|
| had not sold when we closed | 694 | +25.99 | +7.5% | 30% |
| **sold at 1.5x or more: not followed** | **100** | **+47.15** | **+94.3%** | **82%** |
| sold in its first 30 s: not followed | 77 | +13.10 | +34.0% | 40% |
| sold under 1.5x at 30-290 s: followed | 130 | −6.67 | −10.3% | 32% |
| sold after 290 s: not followed | 162 | −0.59 | −0.7% | 20% |

Its sale is two different messages. Under 1.5x after half a minute it has given up on the coin: we leave, and these
still lose 10% a copy. At 1.5x or more it is taking profit on a coin that works: 100 such copies make more than half of
everything. In its first 30 s it is usually flipping a coin that goes on (+34% a copy; #39, sold at 3 s and dead in a
minute, is the minority).

## Each part alone

| part | what the data says | beyond the noise? |
|---|---|---|
| **its sale followed** | 0-290 s −9.38, 10-290 s −4.13, under 2.0x −8.11; 30-180 s −0.64, 30-600 s +0.32, never −0.94 | the live window is right; the first 30 s and above 1.5x must stay out |
| **after a sale of its we did not follow** | a floor at 0.9 / 0.8x of its sale price −8.56 / −6.25; out 30-120 s later −18.60 to −8.11; a shorter stall −16.72 to −0.87; a lower pressure count −2.30 to −10.98 | every tightening loses: these are the +94% coins |
| **timer** | 300 s −7.68; 450-1790 s within −1.62 to +0.63 | only "not under 450 s" |
| **take profit** | 2.5 / 3.0 / 3.5: −20.20 / −9.93 / −7.36, in every block; 4.5 / 5 / 6: +0.22 / +1.35 / +3.22; 8 and none: one block up, two down | **4.0 is the lowest value on the flat top** |
| **stall** | off +0.08; 120-150 s −2.27, −1.66; 240 s +1.76; 300 s +3.12 (all blocks) | no: off is the same as on |
| **pressure** | off −2.51; from 20 s +0.79; 4 in 90 s +0.43 | no single setting; see below |
| neither signal, tp 4 | −6.54, band [−15.6, +3.4], ahead of live in 14% of draws | the two signals together: probably real (86%), not proven |
| neither signal, tp 3 (the setup before Nov 15) | −18.65, band [−27.9, −8.7], 0% | **yes** |

## Combinations and the walk-forward

Four changes are ahead in all three blocks alone (its sale to 600 s +0.32, timer 750 s +0.63, stall 300 s +3.12,
pressure from 20 s +0.79); all four together +4.54. Walk-forward over the 60 setups: the best on A loses on B (−1.87)
and C (−1.71); the best on A+B makes +0.10 on C; the ten best on A+B make −0.40 on C on average, 5 of 10 ahead. **No
combination is worth more than the live setup on days it was not picked on.**

## The setup, and why (frozen Nov 15)

- **Take profit 4.0:** under 4 loses in every block; from 4 to 6 the same within the noise; 4.0 is the lowest of them,
  so the most often reached.
- **Its sale followed only at 30-290 s under 1.5x:** it gave up. Never above 1.5x, never in its first 30 s.
- **Nothing special after a sale of its we did not follow:** those coins are where the profit is.
- **Timer 600 s:** anything from 450 s on is the same; 600 s frees the slot sooner.
- **`sell_pressure [5, 60, 30]` and `stall_s 180`:** together +6.5 SOL over tp 4.0 alone, 3 losing days against 4, worst
  day −1.23 against −1.94, ahead in 86% of redrawn days. The stall adds nothing once the pressure rule is on; it stays
  as the backup that needs only the price.
- What is solid: the whole against the setup before Nov 15 (+18.65, never behind when the days are redrawn), most of
  it the take profit. What is probable: the two signals. What is noise: every finer setting.
