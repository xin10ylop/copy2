# Wallet 4's floats, Nov 16-22 (Nov 23)

The owner: "we aren't making money like the other days, check if it is his trades or he is trading with other floats".
Its history from Helius (`own_only.py`, MAXPAGES 10: 10,000 transactions reach back only to Nov 16 21:44 UTC), its first
buys of **1.3+ SOL** (what the unit copies) by the token it pays with, its own result on them (SOL, Jupiter prices now):

| Day (UTC) | In our floats: buys, its result | Other tokens | SOL curve (not copied) |
|---|---|---|---|
| 11-17 | 20, +14.0 (TTWO 15, PUMP 2, SPCX 2, WBTC 1) | 10, +21.6 | 24, +21.0 |
| 11-18 | 21, +16.4 (TTWO 19, PUMP 2) | 4, +2.2 | 20, +8.8 |
| 11-19 | 25, +12.8 (TTWO 23, PUMP 2) | 13, +7.1 | 21, -1.8 |
| 11-20 | 4, -0.9 (TTWO 4) | 11, +2.1 | 32, +3.0 |
| 11-21 | 6, +0.7 (SPCX 3, PUMP 2, TTWO 1) | 6, +4.3 | 20, +4.0 |
| 11-22 | 9, +2.4 (PUMP 4, TTWO 3, SPCX 1, WBTC 1) | 20, +9.9 | 24, +0.3 |

1. **Its TTWO coins stopped.** 15-23 copyable TTWO buys a day on Nov 17-19 (its +13 to +16 SOL a day in our floats),
   then 4, 1, 3. Our copyable buys went from 20-25 a day to 4-9. That is its trading, not our bot.
2. **A new quote: hSOL** (`he1iusmfkpAdwvxLNGV8Y1iSbj4rUy6yMhEA3fotn9A`, Helius staked SOL): 12 buys of 1.3+ SOL (2 on
   Nov 21, 10 on Nov 22), its result +11.8. Not a float of ours. Our copy (`quote_replay.py`): 11 copies, +5.86 SOL at
   1 SOL a copy with the live exit (+53.3% a copy: -39 +255 +180 +17 +133 +93 -25 -13 -21 -24 +29%), three wins carry
   it. Earlier one-day quotes: DOOMSDAY (Nov 19, 7 buys, +6.3), GTA6 (Nov 17-18, 5, +5.3).
3. **HYPE: no buy of 1.3+ SOL in the 6 days** (one small buy a day Nov 19-21). TTWO copies on the same replay: 66,
   +7.17 SOL (+11.0% a copy).

## Nov 23 evening: is the unit's losing run normal? (fresh history, Nov 17 12:02 to Nov 23 UTC)

The owner's `qqq` on Nov 23: 13 closed today, 3 won, -1.07 SOL; 32 real since the 0.5 SOL restart, -1.45 SOL (-9% a
copy). Wallet 4's own result on its first buys of 1.3+ SOL:

| Day (UTC) | In our floats | Other tokens | SOL curve (not copied) |
|---|---|---|---|
| 11-17 | 6, +1.3 | 8, +20.3 | 20, +9.6 |
| 11-18 | 14, +14.6 | 4, +2.1 | 20, +8.8 |
| 11-19 | 20, +9.2 | 10, +5.4 | 21, -1.8 |
| 11-20 | 3, -0.6 | 9, +1.2 | 32, +3.0 |
| 11-21 | 9, +5.7 | 1, -0.4 | 20, +4.0 |
| 11-22 | 18, +8.5 | 5, +0.8 | 24, +3.4 |
| 11-23 | 9, **-3.0** | 7, -2.1 | 22, -1.2 |

On the coins of our last 15 copies it lost too: 8 of the 11 found lost (-18% to -53% of its buy), the same coins our
copies lost on. Its first losing day in all three groups since Nov 17. 6 of the 15 were hSOL-paid (since the swap):
our copies -0.463 SOL on them, its own result 5 of 6 losing. The exit is frozen (the owner's rule) until about 50 real
trades or Nov 29.

## Nov 23 evening: floats to add for the five units? None (`floats_need.py`)

Buys of copyable size paid in tokens we do not hold, a day over each wallet's history: NVDAx (NVIDIA xStock) 2.35 (wallet
4 5, CqCAzte8 2, 3XeFcZKS 13, 6LwMLkCe 6), USDC 2.20 (CgyPomTG 24), mihao 1.41, ANT 0.92, GTA6 0.89, the rest under 0.7.
NVDAx's copies replayed with each unit's exit (`w3_small.py`, `quote_replay.py`, at 1 SOL): 3XeFcZKS +3.3% (13, -0.03
without the best), 6LwMLkCe -26.0% (6), CqCAzte8 +113.1% (2), wallet 4 -15.0% (4): +0.53 SOL on 25, all of it from
CqCAzte8's two. USDC: CgyPomTG's 24 at +3.9% (negative without the best 2%). mihao: CqCAzte8 stopped using it (Nov 13).
None is worth a float's price risk.
