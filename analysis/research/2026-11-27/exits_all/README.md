# Every running unit's exit and copy rule, picked without fitting the past (Nov 27)

The owner: "review the exits ... after QQQ you're not engineering well every other wallet. Like neither sell pressure, buy
pressure, following it sell, timer, you take profit, you're not optimizing really well without overfitting", then "even for
the by size, if it's sol or floats or these things, like everything". Until today every unit but wallet 4's got one deep
check of 8 fixed exits, then the standard exit (tp 3x / 420 s / stall 240). Here each of the 11 running units gets the
full search, on 14 fresh days of its wallet (Helius, `histx_<wallet>`, Nov 13-27).

Run order (scratchpad SP, `env_helius.sh`, HIST_PREFIX=histx_ MAXPAGES=20 PATHS_AT_ONCE=3 LK=SP/lk):
1. `x1_grid.py SP UNIT`: the copies the unit takes (its floor and coin kind, the most recent 300), each replayed over
   12,960 exit settings: tp none/1.3/1.5/1.75/2/2.5/3/4/5 x timer 60/90/120/180/240/300/420/600 s x sell pressure
   off/3-30/5-30/5-60/8-60/10-120 x stall off/60/120/180/240 x its sale never/always/30-290 s under 1.5x/30-290 s/0-60 s/
   0-120 s. As w2_grid.py replays (slot after its buy, the unit's stake, 0.0064 SOL a round trip, refused over 1.5x).
   `OUTSIDE=1`: the buys it does not take (0.1+ SOL, outside its floor or kind; wallet 4's 6,970 sampled to 300).
2. `x2_analyze.py SP UNIT` -> `out/<unit>.txt`: the exit alone. `x3_pooled.py` -> `out/pooled.txt`: one exit picked on the
   other units. `x4_rules.py SP UNIT` -> `out/<unit>_rules.txt`: floor x coin kind x price limit x token exit x SOL exit.

**The rules, written before any result:** 4 time blocks; walk-forward (pick on the blocks before, score blind on the next);
a new exit or rule only if the walk-forward beats the live one on the 3 blind blocks in total, without the best 2% of copies
and in 2 of 3 (A); else one change from live that wins 3 of 4 blocks, in total and without the best 2% (B); else keep (C).
Not modelled: max_open (two copies at once a unit), so a rule taking more coins is a little flattered.

## The exit alone (`out/<unit>.txt`), % a copy of the stake

| Unit | Copies | Live | Follow its sale (to 600 s) | Wallet 4's exit | tp 2 / 120 s / sp 5/60 | Verdict |
|---|---|---|---|---|---|---|
| qqq (wallet 4) | 280 | **+8.6** (4/4 blocks) | +4.6 | (live) | +2.6 | B: sp 5/30, +0.7 points (frozen, skip) |
| eee | 246 | **+10.7** (4/4) | +3.5 | +4.8 | +4.2 | C |
| rrr | 53 | **+12.8** (4/4) | +9.6 | +11.2 | +10.3 | B: 300 s, +0.9 points (noise, skip) |
| ttt | 141 | +7.5 (4/4) | -3.5 | +5.7 | +1.0 | **A: tp 5x / 600 s / sp 10/120 / stall 180** |
| yyy | 131 | **+18.4** | +5.8 | +5.9 | +7.0 | C |
| uuu | 112 | **+15.6** | +4.4 | +6.5 | +5.9 | C |
| iii | 96 | **+12.8** | +1.9 | +8.5 | +4.7 | C |
| ooo | 208 | +7.1 (4/4) | +1.3 | +4.0 | -0.7 | A (narrow): tp 5x / 600 s / stall 240 |
| ppp | 300 | +3.2 | +3.8 | +5.0 | (live) | C |
| ddd | 130 | +5.4 | -0.9 | +6.0 | +2.9 | C |
| hhh | 36 | **+16.3** | +11.0 | +12.9 | +6.6 | C (the pooled exit +2.5 points on 36: noise) |

- **ttt:** the walk-forward picked tp 5x each time, blind **+16.6% a copy against +8.1%, without the best 2% +9.0% against
  +1.9%, better in 3 of 3**; tp 5x alone beats live in 4 of 4 blocks. Its coins run past 3x.
- **ooo:** tp 5x, blind +10.1% against +6.6%, 2 of 3, but without the best 2% +3.0% against +2.9%: a few runners carry it.
- **Following its sale** is worse than the live exit for 10 of 11 units (ppp +3.8 against +3.2); wallet 4's exit is worse
  for 9 of 10; **sell pressure** never helped alone except as part of ttt's pick (10/120). The walk-forward lost to the live
  exit for 8 of 11 units: the past blocks' best exit did not carry over.
- **One exit for all** (`out/pooled.txt`, picked on the other units, scored blind): worse than each live exit for 10 of 11.

## The whole rule: size, coin kind, price limit, per-kind exits (`out/<unit>_rules.txt`), stakes won in 14 days vs live

| Unit | Smaller buys (next floor down) | SOL coins added / dropped | Limit 1.25x | Own SOL-coin exit | Verdict |
|---|---|---|---|---|---|
| qqq | -44.8 (2/4) | added +115.4 (2/4; 300 sampled for 6,970) | 0 | - | C |
| eee | +0.9 (1/4) | dropped -16.0 (0/4) | 0 | no | C |
| rrr | -0.9 (0/4) | **added +9.9 (3/4), w/o best 2% +3.8** | 0 | no | **B: copy its SOL coins, the same exit** |
| ttt | -3.2 (0/4) | added +4.2 (3/4), w/o 2% -0.0 | 0 | no | A (the exit above; its SOL coins fail without the best 2%) |
| yyy | -0.1 (1/4) | added -5.3 (1/4) | 0 | (passes, but it copies no SOL coins) | C |
| uuu | -3.0 (0/4) | dropped -11.1 (1/4) | 0 | no | C |
| iii | +1.1 (2/4) | dropped -12.5 (1/4) | 0 | no | C |
| ooo | -0.8 (3/4) | dropped -10.0 (0/4) | 0 | no | C |
| ppp | 0.25 floor -2.4 (1/4) | added -0.6 (0/4) | 0 | no | C |
| ddd | -16.5 (1/4) | dropped -9.7 (2/4) | 0 | no | C |
| hhh | -9.0 (1/4) | dropped -3.3 (0/4) | 0 | no | C |

- **rrr's SOL coins** agree with Nov 26 (`../../2026-11-26/uncopied2/`: 3XeFcZKS's SOL coins +5.6% a copy on 152, "the only
  candidate"): two tests on different windows.
- **ttt's whole-rule pick** (floor 1.3, limit 1.25x, SOL coins) differs from what its walk-forward picked blind (floor 0.25):
  only the exit is taken from it, the part that was the same in every blind block.
- Smaller buys lose for every unit; SOL coins help no all-coins unit by dropping them; the 1.25x limit changes nothing (no
  copy fell between 1.25x and 1.5x).

**Changes it supports:** ttt's exit (strong); rrr copies its SOL coins (two tests agree); ooo tp 5x / 600 s (narrow,
optional). The rest stay as they are: their live exit beats every other exit blind.
