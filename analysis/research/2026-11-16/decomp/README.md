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

**Next (running):** our copy of its 1.0-1.45 SOL buys. The scan at 1.0 SOL with the six kinds the bot holds finds 1,087
routable buys in the band (Oct 21 - Nov 15); every third by time (363) is being fetched; `c_band.py CQ ALL` models
them against the 1.45+ copies.
