# Where wallet 4 makes its money now (Nov 16)

The owner: "other than the floats we don't hold, see what makes him good money and we can engineer to copy".
`decomp.py` redoes `02-decomposition/` on Oct 29 12:02 UTC - Nov 15 14:12 UTC (17.1 days) from its landed
transactions (`out/decomp.txt`): every coin it bought and sold out of, its own result, the class from its first buy.

| class | coins | a day | its net | a coin | without its best 5 | 1st half / 2nd half |
|---|---|---|---|---|---|---|
| A: 1.45+ SOL, paid with a token the bot holds | 1,076 | 63.0 | +333.76 | +16.7% | +293.40 | +200.57 / +133.19 |
| B: 1.45+ SOL, paid with another token | 248 | 14.5 | +63.91 | +14.1% | +39.93 | +34.84 / +29.07 |
| C: 1.0-1.45 SOL | 1,978 | 115.7 | +202.57 | +8.6% | +160.51 | +127.77 / +74.80 |
| C: 0.5-1.0 SOL | 4,603 | 269.3 | +157.52 | +4.7% | +125.94 | +74.47 / +83.05 |
| C: under 0.5 SOL | 4,009 | 234.6 | −7.09 | −0.5% | −23.92 | −1.77 / −5.32 |
| E: no curve trade of its own | 816 | 47.7 | −2.84 | −0.4% | −38.23 | −31.67 / +28.83 |

SOL-priced coins (part D) are not in this table (wrong until Nov 17: "none since Oct 29"; it trades 350-780 a day, `../sol_coins/`). B by the token it paid with: HYPE +21.19 on 57, AAPLx +12.46 on 23, MNSTy46h
+9.27 on 3, WXMRyRZh +8.55 on 21, USDC +6.74 on 21. Tokens at prices_full2.json (Nov 15). 79 coins traded together with
another coin in one transaction are left out.

**Our copy of its 1.0-1.45 SOL buys** (`c_band.py`, `out/c_band.txt`; every third of the 1,087 routable buys in the
band, Oct 21 - Nov 15; every copy with no slot limit, the live rule, 0.5 SOL, mean of three landings):

| | copies | take profits | A | B | C | all | a copy |
|---|---|---|---|---|---|---|---|
| its 1.0-1.45 SOL buys (a third) | 361 | 25 (7.3%) | +3.50 | −0.02 | +1.35 | +4.83 | +2.8% |
| its 1.45+ SOL buys (all; copied now) | 896 | 86 (10.3%) | +10.34 | +17.86 | +16.96 | +45.16 | +10.8% |

By size inside the band: 1.0-1.1 −2.1% a copy, 1.1-1.2 +5.5%, 1.2-1.3 −4.3%, **1.3-1.45 +9.8% (+2.38 / +1.61 / +0.71
in the three blocks)**. By what we pay with: TTWO +20.5%, PUMP +10.7%, WBTC −0.3%, SOL −4.6%, SPCX −12.1%. Wallet 4
makes +8.6% a coin on the band, about half its +16.7% on the 1.45+ buys; our copy keeps +2.8%, too little to give up
slots of the 1.45+ copies for. The 1.3-1.45 slice was then fetched in full.

**`min_sol` 1.3 against 1.45** (`min13.py`, `out/min13.txt`; the bot's run, the live rule, the six kinds, the fee rule
on, 0.5 SOL, mean of three landings; 784 buys of 1.45+ and 257 of 1.3-1.45):

| | net (without the best 5) | A | B | C | losing days | worst day | deepest fall | copies, take profits (landing 4) |
|---|---|---|---|---|---|---|---|---|
| 2 open, min_sol 1.45 (live) | +43.82 (+37.57) | +10.08 | +18.35 | +15.39 | 3.7 | −1.31 | −2.82 | 709, 75 |
| **2 open, min_sol 1.3** | **+54.82 (+48.54)** | +12.60 | +20.93 | +21.29 | 4.7 | −1.11 | −2.89 | 916, 103 |
| 3 open, min_sol 1.45 | +45.47 (+39.16) | +10.14 | +20.16 | +15.17 | 4.0 | −1.31 | −2.82 | 722, 75 |
| 3 open, min_sol 1.3 | +56.31 (+49.98) | +13.46 | +21.78 | +21.07 | 4.7 | −0.87 | −2.65 | 943, 104 |

The slice was chosen on the first sample (88 of its copies, +10.4% a copy); **the 169 it was not chosen on make +10.5% a
copy, +8.88 SOL, positive in each block (A +2.54, B +1.56, C +4.78)**. The edge at 1.3 is not smooth (1.2-1.3 was −4.3%
a copy in the sample, 78 copies), and in October (`02-decomposition/` §2) the 1.25-1.45 band lost: to be watched.
Recommended Nov 16: `min_sol = 1.3`, 2 open.

## The HYPE float (`hype.py`, `out/hype.txt`, Nov 16)

HYPE = `98sMhvDwXj1RQi5c5Mndm3vPe9cBqPrbLaufMXFNMh5g` (an SPL token, no freeze authority). 53 HYPE-paid buys with a
path (1.45+ SOL; the 1.3-1.45 ones were not fetched); 52 pass the fee rule. Every copy: +2.88 SOL, +11.1% a copy, but
by block A −0.14, B +4.14, C −1.12. The bot's run (six kinds, min_sol 1.3, fee rule, 2 open, 0.5 SOL): +54.82 →
+57.75 with HYPE (without the best 5: +48.54 → +51.12); by block A +12.60 → +12.37, B +20.93 → +25.03, C +21.29 →
+20.35. One good block carries it. Added on the owner's call.
