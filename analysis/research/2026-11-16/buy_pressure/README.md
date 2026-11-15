# Buy pressure and the take profit (Nov 15 night)

The owner: "as well as sell pressure, why not also test buy pressure? maybe it is also a smart way to know if tp should
be lowered". The reason it could work: on a bonding curve the price rises only while buys outnumber sells, so strong
buying at a high price would say the run is not over, and no buying that it is. Tested after the freeze of the exit
(`../final_exit/`); a test changes nothing on the box.

    python3 -I buy_pressure.py CQ ALL > out/buy_pressure.txt

**Part 1, the idea itself** (1,238 buys, landing 4; the others' buys minus sells over the 60 s before the price first
crosses a level, within 600 s of its buy):

| crossing | copies | with 16+ more buys than sells | reach the next level: 16+ / 6-15 / 5 or less |
|---|---|---|---|
| 1.5x (next 2x) | 460 | 152 | 57% / 57% / 57% (104 copies) |
| 2x (next 3x) | 262 | 173 | 56% / 45% / 38% (16 copies) |
| 3x (next 4x) | 135 | 100 | 61% / 52% / 50% (8 copies) |
| 4x (next 6x) | 79 | 64 | 36% / 50% / 0% (3 copies) |

Two things. **When a coin crosses 2x, 3x or 4x, buying is strong almost every time** (it is what pushed the price
there): only 16, 8 and 3 copies cross with 5 or fewer net buys, so "buying has faded at the take profit" hardly ever
happens. And where there are enough copies to compare (16+ against 6-15), the stronger buying does not reliably go
further: ahead at 2x and 3x, behind at 4x; 600 s after its buy the median price is back at about 1.0x of the level in
every group.

**Part 2, the rules, each added to the live setup (+75.29 SOL; the noise of one change is about ±3.4 SOL):**
- **A lower take profit when buying has faded** (out at 2 / 2.5 / 3 / 3.5x if buys minus sells over 30-120 s is 0 or
  less, or −3 or less): 16 settings, −9.49 to +0.27. It fires on 1 to 85 copies, and those do better left alone.
- **The take profit only once buying has faded** (armed at 4x or 3x, out when buys minus sells falls under 1 / 5 / 10):
  armed at 4x +1.70 to +4.02, armed at 3x −1.67 to +3.22. Block A up (+3.3 to +4.7), block C down in all but one;
  without the best 5 trades it is behind (+59.6 to +62.9 against +65.65): it is "no take profit" with another name
  (+0.29, the same block pattern), a bet on the few biggest runs.

**Nothing to change.** What buy pressure knows, the live rules already use: the price only gets to the take profit
while buying is strong, and when buying turns into net selling for a minute `sell_pressure` sells.

## From 1.2x (`low_levels.py`, `out/low_levels.txt`; the owner: "how didn't you start at 1.2x?")

- **The crossings of 1.2x, 1.3x, 1.5x, 1.75x:** buy pressure does not separate them either. Crossing 1.2x (662
  copies): 74% / 68% / 71% / 68% reach 1.5x with 0 or less / 1-5 / 6-15 / 16+ more buys than sells. Crossing 1.3x (585):
  42% / 46% / 47% / 40% reach 2x. At these levels weak buying is common (384 of 662 cross 1.2x with 5 or fewer net
  buys), so there is something to act on, and it carries no information.
- **A take profit at 1.2 / 1.3 / 1.5 / 1.75x when buying has faded,** 24 settings added to the live setup: all lose,
  −0.81 to −19.03 SOL (the tightest, "0 or less in 30 s": −19.03 at 1.2x, −17.64 at 1.3x, −14.98 at 1.5x). They do
  cut the worst day (to −0.18 at best) by selling 200-390 copies early, at the price of the runs.
- For scale, a plain take profit there: 1.2x −79.16, 1.3x −67.94, 1.5x −51.97, 1.75x −42.36, 2.0x −31.17.
