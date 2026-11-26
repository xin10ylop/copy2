# The running wallets' smaller buys: copy them? (Nov 26)

The owner: "plese dig deeper, if it is profitable allow it, do the same for the rest of the wallets, who mentioned a 0.5 sol
floor?". The 0.5 SOL floor was never the owner's: the tape screen (Nov 20) counted copies of buys of 0.5+ SOL, and each
unit since took `min_sol = 0.5` from it (wallet 4's 1.3 from its own study). Below it only a few 0.25-0.5 bands had been
replayed (Nov 24-26: negative for CqCAzte8, HtHkKxYN, GqWfqfG6, FatoU1bj).

1. `s1_replay.sh SP`: `../../2026-11-24/ideas/e1_ideas.py` per wallet and band of its first buy (0.1-0.25, 0.25-0.5; wallet 4
   also 0.5-1.3, its last 5 days), the unit's own exit, 1 SOL a copy (more price impact than the 0.25-0.5 SOL units take),
   COST 0.0064 a round trip, Helius paths, the 14-day histories; every copy saved (`out/*.json`).
2. `s2_dig.py out` (`out/dig.txt`): per band, copies, % a copy, without the best 2%, the 4 time blocks, the two halves, the
   share of the result from the best 5 copies, the win rate, days up. KEEP = positive, positive without the best 2%, both
   halves positive and 3 of 4 blocks positive.

## Results (`out/dig.txt`)

| Unit, band | Copies | % a copy | w/o best 2% | Blocks | Halves | Best 5 | Days up | |
|---|---|---|---|---|---|---|---|---|
| **ppp 0.1-0.25** | 168 | **+10.6%** | **+14.66** | +8.9 / +17.2 / +15.9 / +0.4 | +13.0 / +8.1 | 29% | 9 of 11 | **KEEP** |
| **yyy 0.25-0.5** | 51 | **+23.2%** | **+9.04** | -2.2 / +6.4 / +79.0 / +8.5 | +2.1 / +45.2 | 86% | 8 of 13 | **KEEP** (one block, its best 5 copies 86% of it) |
| ppp 0.25-0.5 | 169 | +1.2% | -1.09 | +6.3 / -4.7 / +1.0 / +1.9 | +0.8 / +1.5 | | 5 of 11 | no (flat) |
| qqq 0.5-1.3 (Nov 21-25) | 326 | +0.9% | -16.62 | | -1.8 / +3.6 | | 2 of 5 | no |
| qqq 0.25-0.5 | 161 | +3.4% | -2.14 | | | | 3 of 5 | no |
| qqq 0.1-0.25 | 41 | +1.7% | -1.83 | | +19.0 / -16.5 | | 2 of 5 | no |
| ooo 0.25-0.5 | 32 | -1.9% | -2.55 | | | | | no |
| uuu 0.25-0.5 | 23 | -11.9% | -3.08 | | | | | no |
| yyy 0.1-0.25 | 20 | -4.1% | -1.86 | | | | | no |
| ttt 0.1-0.25 | 14 | -15.2% | -3.24 | | | | | no |
| eee, iii, rrr, uuu 0.1-0.25, ttt 0.25-0.5 | 3-9 | | | | | | | too few |

The bands that pass: **3SiQo8MJ's 0.1-0.25 SOL buys** and **6nNzEg86's 0.25-0.5 SOL buys** (the latter carried by one
block, Nov 22-23). A unit has a floor and no ceiling: ppp's floor 0.1 takes its flat 0.25-0.5 band too (together +5.9% a
copy at 1 SOL); yyy's floor 0.25 takes only the passing band. The fixed costs weigh more on a smaller stake: 0.0064 SOL a
round trip is 2.6% of ppp's 0.25 SOL against 0.64% at the replay's 1 SOL (its smaller impact gives some of it back).
