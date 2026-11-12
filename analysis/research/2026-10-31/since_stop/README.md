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

## How far to trust the model: its miss on our real trades (`calib.py`, `out/calib_*.txt`, Nov 8)

On the 15 real trades it can be checked against (the 12 of `report.py` with their real trades between, and the three
1 SOL timer trades at landing 4; one was refused in the model and skipped), the model is **below the real result on 14
of 14**: median **+18.9 points of the stake on take profits** (7), **+9.3 on timer exits** (4), +3.9 on stops (3). The
fee is not the cause (the events charge 300-395 bps a side on most of these coins, and pump takes it), nor the price
model (`PRICE_MODEL=v`, our tokens out of the curve, gives +15.9 / +9.7 / +4.0). Likely contributors: real sells landing
into a still-rising price, and a landing count one trade too high on same-slot fills (the on-chain checks counted its
own buy among the trades before ours). Not resolved.

Corrected by that median miss per exit type, Nov 4 16:11 - Nov 8 at 1 SOL × 2, landing 4, no stop: **raw −1.78 (−4.34),
corrected +5.36 (+2.42)**; since the stop (10.2 days): raw +5.14, corrected +22.6. The correction rests on 15 trades
from one evening and night (Oct 28-29) and should be read as an upper bound; the raw model as a lower one.

## Update, Nov 10 (`out/calib_nov08.txt`, `out/calib_last7.txt`, `out/update_last7_byday.txt`, `out/rules.txt`)

Wallet 4 still trades (last transaction Nov 10 15:17 Beirut). **A second cash-out:** Nov 9 03:17 Beirut, 410 SOL to the
same `EXzuWDVb...` in five transfers within a minute; balance 158 SOL on Nov 10. Its flow is thinner (10 routable buys on
Nov 9, 8 on Nov 10 to 15:17) and its own result per trip weaker (Nov 9 +20.6%, Nov 10 −1.9%); its rule is unchanged
(early sales on 69.5% of all 200 trips since Oct 28).

The copy at 1 SOL × 2, no stop, landing 4 (raw model / corrected by its miss on our real trades):

| window | copies | raw (w/o best 2) | corrected (w/o best 2) |
|---|---|---|---|
| Nov 8 18:10 - Nov 10 15:17 | 24 | −1.50 (−3.06) | +1.22 (−0.72) |
| last 7 days, Nov 3 15:30 - Nov 10 15:17 | 99 | −2.60 (−5.16) | +8.76 (+5.83) |

By day (raw): Nov 3 −1.14, Nov 4 +1.90, Nov 5 +2.53, Nov 6 +1.38, Nov 7 −4.70, Nov 8 −1.30, Nov 9 +0.26, Nov 10 −1.52.
The raw model loses over the week, the corrected one wins; only real fills can say which is right.

## Update, Nov 12 (`out/calib_nov10.txt`, `out/calib_last7_nov12.txt`, `out/funding_1p71.txt`)

Wallet 4 still trades (last transaction Nov 12 02:26 Beirut). On **Nov 11 04:13-04:20 Beirut it swapped about 154 SOL
into USDC** (8 swaps of 20 SOL, about 1,660 USDC each, plus 11.7 SOL at 12:49), kept in its own wallet; its SOL balance
is about 45. Routable buys by day (Beirut): Nov 9 10, Nov 10 10, Nov 11 16, Nov 12 4 to 02:26; its own result per trip
Nov 10 −8.5%, Nov 11 +21.7%.

The copy, no stop, landing 4: since Nov 10 15:17 (22 copies, 1 SOL × 2) raw +1.97 (−1.75), corrected +4.51 (+0.41).
Last 7 days (from Nov 5 02:30):

| setting | copies | raw (w/o best 2) | corrected (w/o best 2) |
|---|---|---|---|
| 1 SOL × 2, all routes (needs about 2.8 SOL) | 105 | −2.33 (−6.05) | +9.46 (+5.36) |
| 1 SOL × 1, wSOL routes only (what 1.71 SOL buys at 1 SOL) | 55 | −5.33 (−8.10) | +0.56 (−2.59) |
| 0.5 SOL × 2, all routes, 0.5 SOL float (fits 1.71 SOL) | 105 | −1.16 (−3.02) | +4.73 (+2.68) |
| 0.1 SOL × 2, all routes | 105 | −0.23 (−0.60) | +0.95 (+0.54) |

## The settings at our speed (`optimize.py`, `out/optimize_N3.txt`, `out/optimize_N4.txt`, `out/tp_compare.txt`, Nov 12)

360 combinations (take profit 1.5 / 1.75 / 2.0 / 2.5 / 3.0; stop none / 0.7 / 0.8; hold 300 / 600 / 900 / 1790 s;
following its sale or not; price limit 1.15 / 1.25 / 1.5), 1 SOL, max_open 2, landing 3 and 4 trades after its buy (our
live speed), picked on Oct 29 14:02 - Nov 5 12:00 Beirut (103 buys) and scored on Nov 5 12:00 - Nov 12 01:38 (100):

- **Take profit 2.5 beats 2.0** at every landing (2, 3, 4, 7) and in both weeks, raw and corrected; 3.0 is about equal to
  2.5. Landing 4, 13.5 days: tp 2.0 raw +4.91 / corrected +27.38; **tp 2.5 raw +11.26 / corrected +31.83**; tp 3.0 +10.73
  / +29.67. On Oct 19-28 (`nostop_old.py`) 2.0 was better; that was before wallet 4 dropped its own timer.
- **No stop and not following its sale** are in every top variant, both weeks.
- **Hold 1790 s** is best on the first week; 300-900 s win some second-week rows, not consistently: kept.
- **Price limit:** 1.15, 1.25 and 1.5 swap places between weeks and landings: 1.25 kept.
- **max_open:** 1 is worse in the second week (raw −7.69 against −3.68); 2, 3 and 4 are within half a SOL: 2 kept.

## Hold through its sale or follow it, and stop losses (`hold_vs_follow.py`, `out/hold_vs_follow_nov12.txt`, Nov 12)

Last 7 days (Nov 5 08:49 to Nov 12 08:49 Beirut), 1 SOL, 2 open, tp 2.5, 1790 s, raw model. Asked after the first
live trades, where wallet 4 sold all three after 3-5 minutes.

- **Hold vs follow is a tie in the raw model:** −0.08 vs −0.16 SOL at landing 4, +0.01 vs −0.07 at landing 8. Without
  the best 2, following is slightly ahead (−4.09 vs −4.44). Holding wins the second half, following the first.
- The shape is real: coin by coin, holding is worse on 57 coins (−13.15 SOL, −0.23 each) and better on 23 (+12.20,
  up to +1.55 on one). Net for holding −0.95; without its best 2 coins −4.04.
- **Stops:** 0.8 and 0.7 lose 3.5-3.9 SOL against no stop (the coins dip and come back). 0.6 and 0.5 gain 0.6-1.1;
  0.5 is ahead of no stop in both halves at both landings, by 0.2-0.7 a half: small, inside the model's error.
