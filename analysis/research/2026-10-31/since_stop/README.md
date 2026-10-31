# The long copy since the box died (Oct 29 11:52 UTC to Oct 31 18:20 UTC, 52.5 hours)

Wallet 4 made 36 copyable buys in the 52.5 hours (16.5 a day). The copy as built, 1 SOL a copy, landing 4 trades of the
coin behind its buy (the live median), modelled trade by trade on chain: +0.92 SOL, without the best 2 -0.70. The model
came out 12.8 points of the stake below the real result on the bot's 12 real closed trades (take profits most), so the
real figure is likely higher. Landing 2 trades behind: +2.56 (+0.89); 7 behind: +0.56 (-0.99). By day: Oct 29 -0.23,
Oct 30 +1.48, Oct 31 -0.34. Full table in out/report.txt; scan.out is the bot's own detection on every transaction.

Run: fetch_w4.py SPD/w4tx, then examples/scan over it (> SPD/scan.out), then model.py SPD 1.0 4, then report.py SPD.
