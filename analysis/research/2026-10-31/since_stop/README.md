# Wallet 4 and the long copy since the box died (Oct 29 13:52 Beirut to Nov 4 16:11, 5.9 days)

**Did it change its rule? Yes, again.** On its 111 routable 1.45+ SOL buys since Oct 28 (`out/rules.txt`):
- the 30-minute timer is gone: 9 trips held to it in all, none since Oct 31 (67% in Oct 19-27, 39% on Oct 27-28);
- early sales on 67% of trips (74 of 111; 80% on Oct 31 - Nov 1), at a median 1.10x the price its buy left after a
  median 300 s, always all at once;
- it still profits on them, +35% a trip on average in its own quote.

**Its money:** on Oct 30 02:15 Beirut it sent 510 SOL to `EXzuWDVba3BQL14UYxSbvz1pZwZNYHXbyQwMBQutPFey` (a plain
account, 8 transactions), which swapped 460 of it through Jupiter within 11 minutes: profit taken, not a rotation.
Its balance went 622 → 114 → 393 SOL by Nov 4, trading as before. A lookalike `H9kuecgK...` sent it a zero-SOL
transaction in the same minute (address poisoning). `build_rows.py` lists the transfers.

**Would the copy have made money? As built, barely.** 92 routable buys (15.6 a day), 1 SOL, max_open 3
(`out/copy_grid_N4.txt`, `out/nostop_new.txt`):

| our buy lands | as built (stop 0.8) | the same, no stop |
|---|---|---|
| 2 trades behind its buy | +3.14 (first half +2.12, second +1.02) | **+7.79** (+3.00, +4.79) |
| **4 behind (the live median)** | **+1.79** (+0.46, +1.33) | **+6.26** (+1.27, +4.99) |
| 7 behind | −0.21 | +3.91 |

Without each half's best 2, landing 4: as built −1.15 / −0.70; no stop −0.34 / +2.64. Worst single trip: −0.5 with the
stop, −0.8 without; worst day −1.66 / −1.30. Following its sale instead (`follow_its_sell = true`): +0.77, worse.
By day as built (landing 4): Oct 29 −0.23, Oct 30 +1.48, Oct 31 −0.79, Nov 1 +2.60, Nov 2 −1.66, Nov 3 −1.05, Nov 4 +1.44.
The model is cautious: on the bot's 12 real closed trades it came out 12.8 points of the stake below the real result
(`out/report.txt`), most of it on take profits.

**Why no stop:** it now sells early and all at once; its sale pushes the price under 0.8x and the stop sells into it,
then the coin often recovers within the hold. On the old data (`nostop_old.py`, `out/nostop_old.txt`: Oct 19-28, paths
that end at its own sale) no stop is neutral: Oct 19-22 −0.7, Oct 23-27 +0.8, Oct 27-28 the same. In the 384-variant
grid (`copy_grid.py`, picked on the first half, scored on the second) every top variant drops the stop; take profit and
hold picks differ between landings, so they stay as built.

## Run order
```
python3 -I fetch_w4.py SPD/w4tx "2026-10-28 18:30"              # wallet 4's 15,297 landed transactions (Triton)
target/release/examples/scan RPC SPD/w4tx SPD/prices.json 1.45 > SPD/scan.out     # the bot's own detection
python3 -I build_rows.py SPD                                       # -> routable.json, and its big SOL transfers
python3 -I model.py SPD 1.0 4                                      # each coin's 31-minute curve (cached)
python3 -I report.py SPD > out/report.txt                          # the model against the bot's real trades
python3 -I rules.py SPD > out/rules.txt                            # its own exits
python3 -I copy_grid.py SPD 4 > out/copy_grid_N4.txt               # the copy with the cap, and the exit grid
python3 -I nostop_new.py SPD > out/nostop_new.txt
(cd ../../2026-10-28/fresh && CAP=3 NOT=AvcwGFaF,2FSWwQwj GRAD=1 python3 -I ../../2026-10-31/since_stop/nostop_old.py)
```
`SPD` = a scratchpad folder; `prices.json` = WBTC at 7,950 lamports a unit.

## The trips where it sells first (`out/after_its_sale.txt`, Nov 4)

At 1 SOL × 2, landing 4, no stop (the plan): it sold while we still held on 51 of 90 trips; those 51 made −5.97 SOL
together (median −0.195, worst −0.79, 12 won; 45 ended on our timer, 6 still reached 2.0x). The other 39, where the coin
hit 2.0x before its sale, made the profit. Selling right behind its sale instead (`follow_its_sell = true`, no stop)
totals +2.19 against +6.92: our sell lands after its own and its copiers', and the 6 coins that reached 2.0x after its
sale are cut. With the 0.8 stop the 29 such trips lost −0.94, but the stop costs more elsewhere (+1.79 in all).

## Update, Nov 8 (`update.py`, `out/update_nov08.txt`, `out/update_since_stop_nov08.txt`, `out/rules.txt`)

Wallet 4 is still trading (last transaction Nov 8 18:27 Beirut; balance 507 SOL, from 393 on Nov 4; no transfer out
since Oct 30). 66 routable buys from Nov 4 16:11 to Nov 8 18:10 Beirut (4.1 days, 16 a day). Its rule is the same as
since Oct 31 (early sales 68% of all 177 trips, the timer on none since Oct 31), but its own result per trip fell:
+35% a trip on Oct 28 - Nov 1, about +19% on Nov 2-6, **−22.5% on Nov 7**, +15% on Nov 8.

The copy at the plan's settings (1 SOL, 2 open) over those 4.1 days **loses in every variant**:

| landing | 0.8 stop | no stop |
|---|---|---|
| 2 trades behind | −1.82 (−3.51) | −2.09 (−4.09) |
| 4 behind | −0.36 (−2.60) | −1.78 (−4.34) |
| 7 behind | −0.50 (−2.63) | −3.97 (−6.06) |

(brackets: without the best 2). By day at landing 4, no stop: Nov 4 −0.63, Nov 5 +2.53, Nov 6 +1.38, **Nov 7 −4.70**,
Nov 8 −0.36. Since the stop (Oct 29 13:52 to Nov 8, 10.2 days, 153 copies), no stop is still ahead: **+5.14 (+2.59)**
against +1.43 (−0.94) with the stop. The model came out cautious on the bot's real trades (about 13 points of the stake
a trade, mostly take profits), so the real figures are likely somewhat better, but not enough to turn the last 4 days.
