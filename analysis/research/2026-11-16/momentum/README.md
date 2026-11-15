# Buying that slows, selling that rises (Nov 15 night)

The owner: "why not check when buy pressure is fast, then slows down, and maybe also then if sell pressure is rising".
The earlier rounds used the level of buys and sells over a window; this is their change, the last W seconds against
the W seconds before. A test only: the exit is frozen (`../final_exit/`).

    python3 -I momentum.py CQ ALL > out/momentum.txt

**Part 1, what follows each pattern** (1,238 buys, landing 4; the first time it shows while the live setup still holds
the copy; the price afterwards in multiples of the price then):

| pattern | copies | median at 600 s | lower at 600 s | a new high 20%+ above, after it |
|---|---|---|---|---|
| the live rule: 5 more sells than buys in 60 s | 246 | 0.88x | **74%** | **34%** |
| buying was fast (10+ in 30 s), now half or less | 455 | 0.82x | 65% | 54% |
| the same, and sells now above buys | 346 | 0.82x | 67% | 49% |
| the same fade at 2x or more | 86 | 0.93x | 56% | 55% |
| selling has risen (8+ sells in 30 s, twice the earlier 30 s) | 322 | 0.88x | 60% | 60% |
| the same at 1.5x or more | 181 | 0.95x | 55% | 65% |

After the live rule the coin makes a new high one time in three. After a fade or a rise in selling it does so half
the time or more: **buying in these coins comes in bursts, a pause after a burst is normal, and a jump in sells is
profit-taking that the next burst absorbs.** The change says less than the level.

**Part 2, the rules** (36, each added to the live setup, +75.29 SOL; the noise of one change is about ±3.4 SOL):
- buying was fast and has slowed: −15.57 to −0.02 (12 settings);
- that, and sells now above buys: −4.78 to +0.19 (12);
- selling has risen: −22.88 to −10.29 (12).

None is ahead in all three blocks. Nothing to change.
