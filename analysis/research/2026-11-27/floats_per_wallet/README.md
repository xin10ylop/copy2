# New floats? Each running unit's payments over Nov 20-27 (Nov 27)

The owner: "any new floats to add?", then "check for each wallet". The 12 units running on Nov 27, each wallet's last 7 days
fetched fresh from Helius (`histfl_<wallet>`, `../../2026-11-19/candidates/c1_fetch.py`, MAXPAGES 15; every history
reaches Nov 20, wallet 4 10,771 transactions). Each coin by the wallet's first buy, at its unit's floor and coin kind.

Run order (scratchpad SP, `env_helius.sh`):
1. `f1_wallets.py SP 7 none QUOTES` writes the 245 quote mints; `quote_route` PDAS_ONLY=1 with the 8 floats, then
   `../../2026-11-26/uncopied2/u6_routes.py` (batches, retries): `routes.txt`, 123 reached through a pool, 114 none.
2. `f1_wallets.py SP 7 routes.txt` -> `out/wallets7.txt`: per unit, SOL / float / pool route / no route.
3. `f2_sizes.py SP 7` (SIZES=1.0,1.5,2.0,3.0) -> `out/sizes7.txt`: the floats' sizes against the week's copies.
4. `../../2026-11-24/ideas/e1_ideas.py` with QUOTE, HIST_PREFIX=histfl_, FETCH=1, each unit's exit, 1 SOL a copy, COST
   0.0064 (ppp: BASEX 2,120,0,5,60, MINSOL 0.1) -> `out/fl/`: our copy of the coins priced in the top unreached tokens.

## Per unit (`out/wallets7.txt`): coins at its floor, and what paid

| Unit | Coins | SOL | Float | Pool route | No route | Its no-route coins, its own SOL |
|---|---|---|---|---|---|---|
| qqq (wallet 4, token 1.3+) | 150 | - | 100 | 11 | 39 (26%) | +7.40, spread over ~25 tokens (3 at most each) |
| eee | 69 | 40 | 20 | 1 | 8 | +2.01 (DJT 3) |
| rrr (token) | 18 | - | 11 | 2 | 5 | +2.36 |
| ttt (token) | 35 | - | 18 | 9 | 8 | -0.39 |
| yyy (token, 0.25+) | 43 | - | 38 | 1 | 4 | +0.25 |
| uuu | 75 | 58 | 14 | 0 | 3 | -0.21 |
| iii | 80 | 74 | 3 | 3 | 0 | - |
| ooo | 107 | 86 | 13 | 1 | 7 | +3.44 |
| ppp (token, 0.1+) | 269 | - | 176 | 48 | 45 (17%) | +1.69 (TSLAx 9, ANT 7) |
| ddd | 106 | 69 | 20 | 2 | 15 | -0.26 |
| fff | 34 | 31 | 2 | 0 | 1 | 0.00 |
| hhh | 23 | 17 | 4 | 0 | 2 | -0.37 |

The unreached tokens with the most coins over all units: TSLAx 18 (own +2.97 SOL), DJT 13 (-0.49), ANT 10 (+1.05), SQQQ 10
(+0.39), WXMR 6 (-1.00), VVV 6 (-0.44); the rest 5 or fewer, most negative (SPYx 4 +3.09, ETH 3 +1.04).

## Our copy of the top three (`out/fl/`, 1 SOL a copy, each unit's exit)

| Token | Copies | SOL | % a copy | Without its best coin |
|---|---|---|---|---|
| TSLAx | 17 (ppp 9 +0.25, rrr 1 +1.88, qqq 2 -0.36, ttt 1 -0.54, ddd 2 -0.20, ooo 2 -0.07; uuu no path) | +0.96 | +5.6% | -0.92 |
| ANT | 10 (ppp 7 +1.06, qqq 2 -0.35, rrr 1 +0.01) | +0.72 | +7.2% | ppp +0.24 without its best 2% |
| SQQQ | 10 (uuu 1 +1.18, ppp 4 +0.39, ddd 2 -0.59, fff 1 -0.19, ooo 1 -0.17, qqq 1 -0.08) | +0.54 | +5.4% | -0.64 |

Each rests on one or two coins; on Nov 26 (14 days, `../../2026-11-26/uncopied2/`) TSLAx replayed -5.5% on 11 and ANT -2.8% on
17. **No new float.**

## The sizes (`out/sizes7.txt`): copies skipped / shrunk in 7 days (an upper bound: each copy holds for its unit's longest hold)

| Float | Now | Copies | Most at once | Now | 1.0 | 1.5 | 2.0 | 3.0 |
|---|---|---|---|---|---|---|---|---|
| hSOL | 2.0 | 91 | 2.8 | 2/1 | 24/4 | 9/1 | 2/1 | 0/0 |
| PUMP | 1.0 | 84 | 1.8 | 5/2 | 5/2 | 0/2 | 0/0 | 0/0 |
| NVDAx | 1.5 | 81 | 3.2 | **9/7** | 22/3 | 9/7 | 6/4 | 1/1 |
| TTWO | 2.5 | 53 | 1.5 | 0/0 | 3/5 | 0/0 | 0/0 | 0/0 |
| SPCX | 1.0 | 52 | 1.5 | 2/0 | 2/0 | 0/0 | 0/0 | 0/0 |
| USDC | 1.0 | 39 | 1.2 | 0/1 | 0/1 | 0/0 | 0/0 | 0/0 |
| WBTC | 0.5 | 13 | 1.0 | 0/2 | 0/0 | 0/0 | 0/0 | 0/0 |
| PAID | 0.6 | 6 | 1.5 | 1/1 | 1/0 | 0/0 | 0/0 | 0/0 |

NVDAx is the float that runs short (16 of 81 copies skipped or shrunk; ppp 43, qqq 17, uuu 7 of its copies), then PUMP (7 of
84). TTWO's copies fell from 239 a week (Nov 24) to 53: 2.5 SOL is more than it needs. SOL coins tied up at most 4.5 SOL at
once (30 copies found more than 1.5 SOL tied up).
