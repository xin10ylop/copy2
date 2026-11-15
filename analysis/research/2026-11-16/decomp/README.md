# Where wallet 4 makes its money now (Nov 16; in progress)

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

No SOL-priced coin (part D) since Oct 29. B by the token it paid with: HYPE +21.19 on 57, AAPLx +12.46 on 23, MNSTy46h
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
slots of the 1.45+ copies for. The 1.3-1.45 slice is the one to test: the rest of it is being fetched (`routable.json`
grows by every 1.3-1.45 buy not in the sample) for a run of the bot with `min_sol` 1.3 against 1.45.
