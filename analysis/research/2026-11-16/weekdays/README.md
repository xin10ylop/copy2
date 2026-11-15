# Is wallet 4 slow on Sundays? (Nov 16)

`weekdays.py` over wallet 4's transactions, Oct 22 - Nov 14 (24 full Beirut days; the data ends Nov 15 14:10
Beirut), `out/weekdays.txt`: its 1.45+ SOL buys that the bot can copy now (SOL, WBTC, PUMP, SPCX, TTWO, DJT) a day.

- **Sundays are its busiest days, not its slowest:** 50.3 copyable buys a day (Oct 25 62, Nov 1 39, Nov 8 50),
  against 34.5 on weekdays; the weekend 42.0.
- **What is slow is the last few days, whatever the weekday:** Nov 12 27, Nov 13 15, Nov 14 18, against 22-62 on the
  days before (Nov 15 to 14:10 Beirut: 11).

## The worst losing run of the setup live on Nov 16 (`risk_now.py`, `out/risk_now.txt`)

Six kinds (SOL, WBTC, PUMP, SPCX, TTWO, DJT), tp 3.0, 600 s, early 30-290 s, 2 open; Oct 21 - Nov 15; landings 4 / 8
/ one block late. Deepest fall from a high, trade by trade:

| stake | fee rule | deepest fall | losing days of 24 | worst day | total |
|---|---|---|---|---|---|
| 0.5 | off | −3.68 / −3.13 / −2.93 | 6 / 6 / 5 | −1.95 / −1.92 / −1.64 | +45.52 / +34.44 / +49.10 |
| 0.5 | on | −3.09 / −3.00 / −2.36 | 4 / 3 / 4 | −1.41 / −1.73 / −0.78 | +45.16 / +35.99 / +50.31 |
| 0.7 | off | −5.09 / −4.32 / −4.04 | 6 / 6 / 5 | −2.70 / −2.65 / −2.27 | +63.36 / +48.05 / +68.29 |
| 0.7 | on | −4.27 / −4.14 / −3.27 | 4 / 3 / 4 | −1.95 / −2.40 / −1.09 | +62.85 / +50.17 / +69.96 |

The deepest fall is the same stretch every time: Oct 25 evening to Oct 27 evening (Beirut).
