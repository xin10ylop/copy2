# Its rules, and ours

## Its exits, read from its sales (`analysis/final/sim_g1.py`, this week's first sales)

- No fixed timer: the most common hold bin holds 2 of 17 first sales on days 1-4 (a timer needs 25%).
- No fixed take profit or stop: 2 and 1 trips in the most common bins (a level needs 5).
- Winning first sales p25 / 50 / 75: 1.56 / 1.93 / 2.93x (this week), 1.27 / 1.55 / 2.83x (Oct 4 00:09 → Oct 25 00:09 UTC).

It sells on judgement, fast, into the first run. With no levels of its own, the sweep falls back to the general grid
(take profit 1.3-3x, stop 0.6-0.9, timers 300 / 1790 / 3590 s), always selling behind it if it sells first.

## Our rule (picked on its days 1-4 of Oct 25 → Nov 1)

- Copy only its buys of **5.1 SOL or more** (the median of its buys that week).
- Stake = **its size, capped at 3 SOL**.
- Exit: **300 s after our buy, or right behind its first sale**, whichever comes first. No take profit, no stop.
- Our entry: 2 trades behind its buy (the long copy's live median, calibrated on wallet 4's live trades).

The other filters picked on the same days were positive too (`03-backtests/out/this-week_oct25-nov01.txt`): every buy
with a 3.0x take profit and 300 s (+11.14 → +32.39, +4.77 without the best 2), SOL-quoted only (+10.86 → +33.74,
+6.12), its 1.45+ SOL buys (+11.11 → +31.67, +2.87). The picked one is the strictest of them.
