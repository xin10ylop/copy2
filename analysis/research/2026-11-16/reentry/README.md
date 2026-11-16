# Not missing the run after a signal exit (Nov 16)

The owner, after #64 `J8Lutktx` (sold on `sell_pressure` at 1.06x at 131 s; 0.71x at 240 s, 4x at 526 s): "isn't there
something we can adjust to not miss the 4x with sell pressure? something very smart". Two ideas with a reason, each
against the live setup on the 1,238 buys, the bot's run (`reentry.py`, `out/reentry.txt`):

    python3 -I reentry.py CQ ALL > out/reentry.txt

| idea | settings | gain against the live setup (+75.29) | ahead in all three blocks |
|---|---|---|---|
| **back in** once the coin has turned (a new high 10 / 30% over the high while we held; the price back over 1.5x or 2x its price; 10+ or 20+ more buys than sells in 30 s), before 480 s; the second leg to tp 4 / the timer, with or without the pressure rule | 12 | −4.62 to +1.59 | none |
| **a runner**: keep 10 / 20 / 30 / 50% of the position to tp 4 or the timer | 4 | −4.61 to −6.04 | none |

The noise of one change is about ±3.4 SOL: the best re-entry (+1.59, the price back over 2x) is inside it and behind in
one block. The runner loses in every setting: the share kept holds the slot for the full ten minutes (the next copies
are missed) and most of the coins left on a signal keep falling. **Nothing to change.** On #64 the 2x re-entry would
have bought back at about 2.03x at 290 s and sold at 4x; on the other coins the same rule buys back into a bounce that
fails about as often as not.
