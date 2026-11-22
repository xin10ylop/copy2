# copy2: the wallets we copy, and the bots that copy them

Two copied wallets, kept apart, and the shared code:

| | Wallet | Bot | Where |
|---|---|---|---|
| **Wallet 4** | `H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg` | part A: the long copy (`rugsnipe-long run`); part B: the copier, off | folders `01`-`07` below |
| **Rafinhaaaaaa** | `Hn6vBWWySnxA8XjxRQDEmZEuH5QL7KqosnJGcLcUzFJ6` | the copier (`rugsnipe-long copy`) | [`rafinhaaaaaa/`](rafinhaaaaaa/README.md) |
| Both, on one box | | | [`08-new-box/`](08-new-box/README.md): the 4 SOL plan, from an empty server to live |
| **Robinhood Chain** (Pons) | wallets 1-3: `0x9a3955a1`, `0x5bc235ac`, `0xc54d3914`; 4-8: the group led by `0xe3fdae6c` (since Nov 19 11:51 UTC) | `rh-copier`, one wallet `0x35bb5c55...`, 0.02 ETH a copy; **live since Nov 18 22:10 UTC** (0.15 ETH) | [`docs/23-rh-copier.md`](docs/23-rh-copier.md), [`analysis/research/2026-11-18/robinhood/`](analysis/research/2026-11-18/robinhood/README.md) |

Code: `crates/rugsnipe-long/` (the long copy, docs/20; the copier, [`docs/21-copier.md`](docs/21-copier.md); how to find another wallet to copy, [`docs/22-wallet-search.md`](docs/22-wallet-search.md)); `crates/rh-copier/` (Robinhood Chain, [`docs/23-rh-copier.md`](docs/23-rh-copier.md)), with
`deploy/` and `config/`. Operator 1 ("him", AHwJSnFN) and the other copied wallets are in the **copy1** repo. Both
repos started from the same code snapshot (`xin10ylop/rugsnipe` at `7184554`, Oct 28). The box builds from this repo's
branch `claude/magical-einstein-k78idp`.

**Agents: read [`CLAUDE.md`](CLAUDE.md) first.**

## Live again (Nov 12)

**Nov 23: HYPE swapped for hSOL in the floats** (`he1iusmfkpAdwvxLNGV8Y1iSbj4rUy6yMhEA3fotn9A`, Helius staked SOL; the
owner's call). Wallet 4's coins paid in TTWO, 15-23 copyable buys a day on Nov 17-19, fell to 4, 1 and 3; it paid with
hSOL for 12 buys of 1.3+ SOL on Nov 21-22 (our replayed copy +5.86 SOL on 11 at 1 SOL) and with HYPE for none in 6 days
(`analysis/research/2026-11-23/w4_floats/`).

**Nov 21 ~13:57 UTC (15:57 Beirut): the long copy moved to a new Cherry box** (Premium VDS 2, Frankfurt, Ubuntu 24.04,
**monthly billing**; hostname `fra-long`, user `ops`): the Vultr box was suspended for an unpaid bill and is given up,
**with its tape (Nov 20 13:32 to Nov 21) and its journal**. Same wallet `Eao8T2Pk...` (the key put back from the
owner's copy), same settings (`config/long.live.example.toml`, `config/float-levels.live`, `fd7911f`); start line
`mode On ... min_sol 1.3 stake 1 SOL tp 4x stop 0x hold 600s sell_pressure [5, 60, 30] stall 180s max_open 2`, feed
connected; wallet 1.9693 SOL and the 6 floats at 0.94-1.00 SOL (the timer topped TTWO up). **The tape restarts on
the new box at 13:59 UTC Nov 21** (60 days kept). The screen results of the lost tape stay in
`analysis/research/2026-11-20/tape_screen/README.md`.
**Nov 20 13:32 UTC (15:32 Beirut): the pump.fun tape records on the Frankfurt box** (unit `rugsnipe-tape`, every curve
trade and create, `/var/lib/rugsnipe-tape`, 14 days kept; first minute 3,544 events; `analysis/research/2026-11-19/tape/`),
for the wallet search. **Nov 20 13:23 UTC: leg 2 off in the main unit** (`dip_drop = 0`; it gets its own wallet later),
floats back to 1.0 SOL each (the timer's file too).

**Nov 20 01:09 UTC (03:09 Beirut): leg 1 at 1.0 SOL, leg 2 at 0.25; floats WBTC, PUMP, SPCX, TTWO, DJT, HYPE at 1.15 SOL each**
(AAPLx and USDC sold and removed; the float timer's `/etc/rugsnipe/float-levels` set to the same 6 at 1.15). Why:
`analysis/research/2026-11-20/split/` (leg 1 alone at 1 SOL +123.23 SOL over Oct 21 - Nov 13 against +62.89 for 0.5 + 0.5).

**Nov 19 22:53 UTC (Nov 20 00:53 Beirut): the split, two legs on each copyable buy of wallet 4** (`0c0c6b9`, the
box's restart journal): leg 1 = the copy as before (0.5 SOL, tp 4x, 600 s, sell pressure 5/60/30, stall 180, max_open 2;
the frozen exit is unchanged), leg 2 = the dip entry (0.5 SOL at or under 0.90x its price within 60 s, tp 1.5x our fill,
900 s, its own max_open 2, floats only; research `analysis/research/2026-11-17/wallet_hunt/market/m15*`, docs/20 §3
"the split"). Daily stop 1.5 SOL over both legs. `status` shows pct1 / pct2 per trade.

**The long copy (wallet 4's part A) runs live since Nov 12 01:23 UTC (03:23 Beirut)** on a Vultr Frankfurt box
(`fra-long`, High Performance AMD, 4 vCPU / 8 GB, $48 a month, a card on file; every Cherry Frankfurt VDS was out of
stock). Settings: 0.1 SOL a copy, 2 open, take profit 2.5x, **no stop**, 1790 s, its sale not followed, price limit
1.25x, daily stop 0.3 SOL. Wallet `Eao8T2Pk2aDzPWUFCA8si7oWd5ndFKfnX3HjYMpERst6` (1.78 SOL in, 0.2 of it as the WBTC float); **its key file was copied to
the owner's Mac (sha256 prefix checked on both) before any SOL went in.** Pings: 0.54-0.70 ms to Jito, Helius,
Nozomi and Triton in Frankfurt. The copier (Rafinhaaaaaa) is installed but not enabled. Next: about 20 closed trades
at 0.1, checked on chain against the model (`analysis/research/2026-10-31/since_stop/`), then 0.5 SOL × 2.
**0.5 SOL × 2 since Nov 12 14:18 UTC (16:18 Beirut)**, the owner's call after the first 3 closed: daily stop 1.0 SOL;
the WBTC float topped up with 0.4 SOL (44,861 units, slot 468555971; float 67,418 units, about 0.57 SOL at wallet 4's
own swap rate that week) so WBTC-routed copies (40 of its 105 last week) still fit a stake. SOL 1.4236 after.
At 0.5 SOL (journal, Nov 12 UTC): #3 `7dDprVHP` timer −0.1106, #4 `57pQW4mw` timer −0.0124 (peak 1.83x), #5
`Eymbsj8M` take profit 2.50x after 312 s +0.6228. The day: 6 closed, 2 won, +0.7477 SOL. Two coins airdropped to the
wallet by `HckQ93Xq...` (15:06-15:51 UTC; we signed nothing) were sold through Jupiter with `float sell`: +0.1968 and
+0.0674 SOL on chain. SOL 2.1877 after, plus the WBTC float (about 0.59 SOL).
**Take profit 2.4 since Nov 12 16:42 UTC** (was 2.5; `since_stop/out/tp_fine.txt`: the 2.3-2.6 plateau, 2.4 ahead by
0.4 SOL over two weeks and just under wallet 4's own 2.5x target). The restart's journal: `tp 2.4x`, feed connected.
**Nov 12 23:54 UTC: the early-sale rule on** (`follow_early_s = [30, 180]`, `follow_early_below = 1.5`). **Nov 13 00:34
UTC: 3-hop routes live** (`0d2b078`; journal `long lookup table Hyif6eWb: 184 addresses`, feed connected).
**Nov 13 11:48 UTC: TAB16RxX copied with real money at 0.1 SOL × 2** (unit `rugsnipe-long-tab`, tp 3.0, 300 s, no stop,
daily stop 0.3), its own wallet `7ByEajSYmXjBK56LX4Wj3kVBAAeLYNW3soRE1T1WTubs` (the key copied to the owner's Mac first,
sha256 prefix checked on both), funded with 0.5 SOL from the long wallet (`send`, slot 468915460), 0.15 SOL of it as
its WBTC float (17,436 units). Why: its 9 paper trades Nov 12-13 −0.0220 SOL raw, +0.0545 with the +8.5-point gap
measured on it; the 0.1 SOL run measures whether our real fills earn that gap. Stop if, at about 30 trades, they do
not.
TAB16RxX real against the model, trade by trade (the gap the 0.1 SOL run measures): #10 481Ntemy (Nov 13 11:56 UTC,
pool+curve, landed in its slot 2 trades after it, timer at 300 s): real −0.0301 SOL on chain, model at that landing
−0.0345: **real +4.4 points over the model.**
**Nov 13 12:57 UTC: TAB16RxX's exits changed to tp 4.0, 600 s, its sale followed when it comes within 60 s of its buy**
(`follow_early_s = [0, 60]`, `follow_early_below = 100.0`; `analysis/research/2026-11-13/tab_exits/`: corrected two
weeks at 0.1 SOL +2.64 against +1.85 for tp 3.0 / 300 s). The restart's journal: `tp 4x … hold 600s`, feed connected.
Nov 13 evening: wallet 4's bot 14 closed, +1.4410 SOL; two more airdrops from `HckQ93Xq...` sold (9cRCn9rG +0.2838,
4FP2GRQS +0.0913): airdrops +0.6394 in all, **trades + airdrops +2.0804 SOL**. Its first WBTC-routed copy (#13
BTCmcoKg, tp in 25 s, +0.5786) came back into the float (134,432 units). TAB16RxX's bot: 11 real, −0.1201.
**Wallet 4's bot at 1 SOL × 2 since Nov 13 17:25 UTC (19:25 Beirut)**, the owner's call after 14 closed (+1.44 SOL),
daily stop 2.0 SOL; the rest unchanged (tp 2.4, no stop, 1790 s, early-sale rule, 3-hop routes). The restart's journal:
`stake 1 SOL tp 2.4x stop 0x hold 1790s max_open 2`, wallet SOL 2.1750 plus the WBTC float (134,432 units), feed connected.
A stop at 0.5x or 0.4x was asked again after #11 (−56.7%) and #12 (−44.0%); it stays off (`since_stop/out/stop_scan.txt`:
0.5x −0.83 SOL raw over two weeks, −1.83 SOL in week 1; 0.4x +0.45 raw, −0.06 calibrated, a wash).
First at 1 SOL: #14 FAVdiH3q timer −0.0851 (−8.5%; wallet 4 +9.4%, sold at 196 s), #15 KgcdZjU4 timer −0.2493
(−24.9%; wallet 4 +8.4%, sold at 299 s); both of its sales after the 180 s early-sale window, so held, as the rule says.
Nov 13 UTC: 8 closed, 2 won, +0.9236; all 16 real +1.1066, trades + airdrops +1.7460 SOL. TAB16RxX's bot: 14 real,
1 won, −0.1665; two of them (3a8RGrQg, FAVdiH3q) the same coin bought in the same second as wallet 4 (the lookalike
study's overlap: 26 of its 149 buys).
**Nov 14 01:20 UTC (03:20 Beirut): 0.5 SOL × 2 again, PUMP and SPCX added as floats, new exits** (the owner's call on
the floats and the stake; `analysis/research/2026-11-14/float_exits/`): take profit 3.0, timer 1200 s, early-sale
window 30-290 s under 1.5x, no stop, daily stop 1.0, `float_min_frac = 0.5`. Backtest, raw, 0.5 SOL, 15.5 days:
+8.82 SOL as it ran, +22.92 with the two floats, +31.14 with the new exits too. `float level` (commit `6138ade`):
WBTC sold down to 0.6 SOL (68,011 units, slot 469141427), PUMP bought for 0.5 SOL (11,231,836,808 units, slot
469141436); the SPCX buy was refused by Jupiter (HTTP 429) and run again after the start: 0.45 SOL, 255,427 units,
slot 469142936. After it: SOL 0.6180, floats 0.599 / 0.500 / 0.449 SOL (`status --chain`). The restart's journal: `stake 0.5
SOL tp 3x stop 0x hold 1200s max_open 2`, three floats, SOL 1.0696, feed connected.
**The 1 SOL hours (Nov 13 17:25 - Nov 14 01:18 UTC): 4 copies, 4 losses, −1.1895 SOL** (#14 −0.0851, #15 −0.2493,
#16 −0.4291 behind its sale, #17 `EH6yuh4Y` timer −0.4260; wallet 4 sold #17 at 180 s, one second past the old
window). All 18 real: +0.2515 SOL; with the airdrops +0.8909.
**The first copies from the PUMP float (Nov 14, chain = journal, checked on Triton):** #18 `4TMzhGzY` 04:01:56 UTC, route
curve, in its slot, 11,068,310,820 PUMP in, sold behind its sale at 256 s, 10,406,863,982 back: −0.0310 SOL. #19
`6KpdMXAS` (SOL route) sold behind its sale at 200 s after two failed sells (0.0002 SOL each): −0.2420. #20 `DHcZRxRX`
04:17:36, the whole float (10,570,389,970 PUMP, 0.4775 SOL: `float_min_frac`), timer 1200 s, 6,238,253,472 back:
−0.1991. **While we held #20, 1,028.105 PUMP came to the float as holder fees** (`2FSqwb8j`, pump's
`DistributeFeeToHolders` from `HckQ93Xq...`, about +0.045 SOL): the "airdrops" of Nov 12-13 were the same thing, paid
in the coin's quote token. Also unsold in the wallet: 3,280.6 `H74CYmXg` (FAVdiH3q's quote, about 0.054 SOL). Nov 14 to
08:45 UTC: 4 closed, 0 won, −0.8980 (three at the new settings, −0.4721); all 21 real −0.2205, with the airdrops
+0.4189. SOL 0.3708 (SOL routes skipped under 0.55), floats 0.605 / 0.321 / 0.460 SOL. The unit restarted between
06:13 and 07:10 UTC (pid 136093 to 153466) with the settings unchanged; cause not yet known.
**Nov 14 11:54 UTC (13:54 Beirut): 0.3 SOL × 2, timer 600 s** (take profit 3.0 and the early-sale window 30-290 s
kept; daily stop 0.6; `analysis/research/2026-11-14/float_exits/`, the A-to-Z review: over 23.5 days and 781 buys a
600 s timer makes as much as 1200 s with the deepest fall −3.08 SOL instead of −5.24 at 0.5 SOL, the owner's own
suggestion; tp 4.0 was recommended for a few hours and withdrawn, it wins only on the few largest trades). 0.3 SOL
because the wallet (about 1.8 SOL) no longer carried four kinds of copy at 0.5: SOL routes were blocked under 0.55
SOL and the PUMP float was one loss from its floor. The restart's journal: `stake 0.3 SOL tp 3x stop 0x hold 600s
max_open 2`, SOL 0.4254, floats PUMP 0.315 / WBTC 0.601 / SPCX 0.458 SOL, feed connected. Booked with it: the holder
fee paid in PUMP (`2FSqwb8j`, +0.0446 SOL) and the `H74CYmXg` fee sold (+0.0545, slot 469318341): holder fees
+0.7385 SOL in all, trades −0.2205, **together +0.5180 SOL**. The 06:59 UTC restart was a clean stop and start by
systemd (`Deactivated successfully`), not a crash and not the owner (the box shows "System restart required": an
automatic update, most likely); no copy was open.
**Nov 15 12:25 UTC (14:25 Beirut): back to 0.5 SOL × 2** (the owner recharged the wallet; daily stop 1.0 again; the 0.6
of Nov 14 had blocked every buy for the rest of that day because the day was already at −0.898, a mistake of mine).
Floats levelled: WBTC 1.0 SOL (110,931 units, slot 469728526; room for its 2 open), PUMP 0.6 (sold 5,594,088,980
units, slot 469728630), SPCX 0.6 (314,740 units, slot 469728733). The restart: `stake 0.5 SOL tp 3x stop 0x hold 600s
max_open 2`, SOL 1.9478, feed connected. Before it, Nov 15: **#30 `BURn1o8x`, the first take profit from the PUMP
float**, 3.00x at 330 s, +0.6038 SOL (its float held less than a stake, so +258%; wallet 4 +96.1%, sold at 157 s).
Nov 14 also #22 `8FE3SQjW` −0.0924 and #23 `4A7n9wq8` (PUMP) −0.0703, both sold behind its early sale. By UTC day:
Nov 12 +0.1830, Nov 13 +0.4946, **Nov 14 −1.0608**, Nov 15 +0.6038 to 12:00. All 24 real +0.2206; with the holder
fees +0.9591 SOL. Numbers #21 and #24-#29 were buys skipped for lack of SOL after the number was taken.
**Nov 15 13:08 UTC (15:08 Beirut): two more floats and the fee floor.** TTWO (`TTWofwAg...`, Take-Two tokenized stock)
and DJT (`DJTu7vi8...`, Trump Media tokenized stock) held as floats at 0.5 SOL each
(`analysis/research/2026-11-15/all_tokens/`: with both the bot's run is ahead in each of three blocks, +43.02 SOL
against +34.94 over 24.7 days): DJT 7,953,726 units (slot 469735371); TTWO failed once on chain (Jupiter slippage,
`Custom 6001`, a Sunday) and landed on the second try, 156,826 units (slot 469740926). **`min_fee_bps = 125`** (the
owner's call after `analysis/research/2026-11-15/skip_filters/`: the same money over 26 days, 4 losing days against
8, and all 9 real trades of that kind had lost; it would have skipped two winners on Nov 15). Code `3404441` (buy
lines end with `fee N bps`). After it: SOL 0.9444, floats WBTC 0.997 / PUMP 0.600 / SPCX 0.598 / TTWO 0.499 / DJT 0.498
SOL, about 4.14 SOL in all; 0.5 SOL × 2, tp 3.0, 600 s unchanged.
**Nov 15 14:12 UTC (16:12 Beirut): 0.7 SOL × 2, daily stop 1.4** (the owner topped the wallet up to about 5.6 SOL).
Floats levelled for 0.7: WBTC 1.402 SOL (155,038 units, room for its 2 open), PUMP 0.749, SPCX 0.752, TTWO 0.750, DJT
0.750 (slots 469758159-469758565); SOL 1.7441. The restart: `stake 0.7 SOL tp 3x stop 0x hold 600s max_open 2`, five
floats, feed connected. The backtest's deepest fall for this setup at 0.7 SOL: −3.27 to −4.27 SOL with the fee rule
(`analysis/research/2026-11-16/weekdays/out/risk_now.txt`).
**Nov 15 14:47 UTC (16:47 Beirut): `min_sol = 1.3`** (was 1.45; `analysis/research/2026-11-16/decomp/`: its 1.3-1.45 SOL
buys copy at +10.5% a copy, as the 1.45+ ones do; the bot's run +54.82 against +43.82 SOL at 0.5 over Oct 21 - Nov 15,
better in each block, and on the buys the threshold was not picked on). The restart: `min_sol 1.3 stake 0.7 SOL tp 3x
… max_open 2`, five floats, feed connected.
**Nov 15 14:57 UTC (16:57 Beirut): a HYPE float** (`98sMhvDw...`, the owner's call; `analysis/research/2026-11-16/decomp/`
`hype.py`: +57.75 against +54.82 SOL at 0.5 over 25 days, but only one block better): 795,530,045 units for 0.75 SOL
(slot 469771258). The restart: six floats; SOL 0.9926, WBTC 1.406, PUMP 0.748, SPCX 0.759, TTWO 0.758, DJT 0.757, HYPE
0.750 SOL (about 6.17 SOL in all); feed connected. The TAB16RxX bot was paused by the owner on Nov 14 (14
real, −0.1665); `send TO all` built to return its balance.
**Nov 15, one copy by 15:01 UTC: a quiet day, not a fault.** Wallet 4's own transactions (876, fetched from 00:00 UTC,
scanned with `examples/scan.rs` and today's floats): 18 buys of 1.3+ SOL, 5 with no route (USDC, XsCPL9dN, Pren1FvF).
Of the 13 routable, 9 were on 100 bps coins, which `min_fee_bps = 125` now skips; 2 more (`3Xtzu55E` 04:30 UTC,
`29xjBYAf` 10:54) were skipped by the journal for "SOL balance 0.33 under the stake", before the top-up. The rest:
`BURn1o8x` copied (#30, take profit); `Dtobp85W` (11:50) paid in TTWO before the TTWO float; `JBR2Avtr` (04:16, 1.42)
and `HHsWnAKw` (13:04, WBTC 1.34) under the then 1.45 minimum. From the fee floor (13:08) to 15:01 UTC it made no buy
of 1.3+ SOL at all. Of today's low-fee buys, the 7 modelled make +3.99 SOL at 0.5 (two of them +2.45 and +1.52);
over 26 days the floor makes the same money (+35.75 against +34.94) with 4 losing days against 8.
**Nov 15 15:14 UTC (17:14 Beirut): the fee floor removed** (`min_fee_bps = 0`), the owner's call: one search out of 66,430 rules, the
gain +0.81 SOL over 26 days, so it may be luck. At 0.7 SOL without it the backtest's deepest fall is −4.04 to −5.09
SOL, worst day −2.27 to −2.70 (with it −3.27 to −4.27 and −1.09 to −2.40; `2026-11-16/weekdays/out/risk_now.txt`). The
restart: `min_sol 1.3 stake 0.7 SOL tp 3x stop 0x hold 600s max_open 2`, six floats, feed connected. Before it: **#32
`832qVw3x`, the first TTWO copy** (195 bps), bought 15:06:55 in its slot +0 with 214,528 TTWO units, sold behind its
early sale at 1.13x after 178 s (peak 1.69x): journal +0.0116 SOL; chain (slots 469773850, 469774689) 219,082 units
back, +4,554 units and −0.00261 SOL in fees, about +0.012 SOL at the status price. One skip by the floor while it ran:
`9TV1aVdJ` (1.758 SOL, 100 bps, 15:11:57). Day: 2 closed, 2 won, +0.6154 SOL; all real 25, +0.2321; with holder fees
+0.9706 SOL.
After it, three losses, each by its rules and equal to the chain: **#33 `EqcJFqoL`** (TTWO) sold behind its early sale
at 0.77x after 156 s, −0.1122 SOL (chain −33,092 TTWO units and the fees); **#34 `EdWqZQVq`** (TTWO, 1.301 SOL, the
whole float) behind its early sale at 0.68x after 37 s, −0.2533 (−76,938 units); **#35 `99KxrsW6`** (SOL, 100 bps,
the kind the floor skipped) bought 64.3% under its price after a dump in its slot, it sold at 298 s (outside 30-290),
our timer sold at 0.35x after 600 s: −0.4229 (chain −0.702919 + 0.280420 and two failed tries of −0.000205, the third
landed in the same slot 469811411). Day −0.1730; all real 28, −0.5563; with holder fees +0.1822 SOL.
**Nov 15 18:48 UTC (20:48 Beirut): back to 0.5 SOL × 2, daily stop 1.0** (the owner's call). Floats levelled: WBTC
1.0 SOL (−45,164 units, +0.4109 SOL, slot 469835546), PUMP 0.6 (+0.1408, slot 469835556); SPCX, TTWO, DJT and HYPE
refused by Jupiter's price API (HTTP 429), to be levelled again. The restart: `min_sol 1.3 stake 0.5 SOL tp 3x stop 0x
hold 600s max_open 2`, six floats, feed connected; SOL 1.1135.
**#36 `GGSWz3uu`** (SPCX float, bought 19:02:34 UTC): peak 2.56x, wallet 4 sold at 63 s at +107% (above 1.5x, so not
followed), our timer sold at 600 s: −0.0864 SOL (chain −42,721 SPCX units and the fees, about −0.085). **#37
`Da5Gbwd8`** (TTWO, the whole float, 127,753 units = 0.418 SOL): take profit 3.02x after 68 s, **+1.0501 SOL** (chain
+323,105 TTWO units, about +1.048). A holder fee in SPCX for GGSWz3uu, +13,060 units (`2rtWCTbw`, from `HckQ93Xq...`), booked with `float book` at +0.0252 SOL.
Day +0.7906 SOL.
**Nov 15 19:29:51 UTC (21:29 Beirut): take profit 4.0 and two exit signals** (`82d0768`; the owner's go after
`analysis/research/2026-11-16/signals/`): `sell_pressure = [5, 60, 30]` (out when the other traders' sells outnumber
their buys by 5 over 60 s, from 30 s after its buy) and `stall_s = 180` (out after 180 s without a new high, once back
at our fill price). Backtest, 1,238 buys at 0.5 SOL over 24 days: +75.29 against +56.63 SOL, 3 losing days against
6, worst day −1.23 against −2.41; tp 3.0-3.5 with the signals +65.35 to +67.92 (`out/tp_scan.txt`). Trailing stops
(10-70% under the peak) and top-holder sells were tested and do not help. Floats levelled to 0.6 (SPCX −51,335
units +0.0995 SOL, TTWO −266,105 +0.8662, DJT −2,449,539 +0.1554, HYPE −153,277,322 +0.1433; slots 469847066-165,
each on chain). The restart: `tp 4x stop 0x hold 600s sell_pressure [5, 60, 30] stall 180s max_open 2`, six floats,
feed connected; SOL 2.3728, WBTC 0.994, the five others 0.600-0.603 SOL.
**#38 `Dyc9zPSt`, the first `sell_pressure` exit** (TTWO float, bought 19:56:53 UTC in its slot +0, 152,080 units):
sold at 1.75x after 89 s (peak 1.88x), journal **+0.2906 SOL (+58.1%)**; chain (slots 469854763, 469855179) 241,314
TTWO units back, +89,234 units and −0.00261 SOL in fees, about +0.291 SOL at the status price. Wallet 4 was still
holding. Day: 8 closed, 4 won, +1.0812 SOL.
**#39 `E3c6RqFX`** (TTWO, 20:26:37 UTC): wallet 4 sold 3 s after its buy (before the 30 s of the early-sale rule), the
coin fell to 0.44x, `sell_pressure` sold at 62 s: −0.2685 SOL (chain −80,202 TTWO units and the fees, about −0.266).
**#40 `DA9ehd4f`** (SOL, 3 hops, 100 bps): the buy failed on chain, −0.0004 SOL: the program refused the price
(`ExceededSlippage`) and the transaction then ran out of compute (`ComputationalBudgetExceeded`, 200,000 of 200,000
units). **The box's `cu_limit = 200000` (set Oct 28 for 2-hop routes) is too low for 3 hops:** wallet 4's own 3-hop
buys use up to 177,930 units (2-hop float routes up to 274,262), and ours add about 40,000 for the token accounts.
Raised to 350,000 at 20:44:19 UTC (about +0.0003 SOL a transaction; the restart's journal: the same start line, feed connected). Day: 9 closed, 4 won, +0.8127; all real 32, +0.4295; with
holder fees +1.1932 SOL.
**The exit, studied one last time and frozen (Nov 15 night, `analysis/research/2026-11-16/final_exit/`):** each part
changed alone against the live setup, the noise measured (±3.4 SOL when the days are drawn again). The 100 copies
where wallet 4 sold at 1.5x or more and we stayed make +47.15 of the total (+94% a copy, 82% won); every way of
leaving behind such a sale loses 2 to 19 SOL; following its sale in its first 30 s loses 9. Take profit under 4 loses
in every block, 4 to 6 is the same. No combination beats the live setup walked forward. **Nothing changes; no more
changes to the exit until about 50 real trades or two weeks have judged it** (the owner's rule).
**Nov 15 21:38 UTC (23:38 Beirut): an Apple float** (AAPLx, `XsbEhLAtcf6HdfpFZ5xEMdqW8nfAvcsP5bdudRLJzJp`, a tokenized
stock, Token-2022 with a freeze authority, a pause switch and a permanent delegate like TTWO and DJT; the owner's
call, as `analysis/research/2026-11-15/all_tokens/` recommended once 0.5 SOL was spare: 26 buys in 24.7 days, +3.05 SOL
at 0.5, block by block −0.20 / +2.86 / +0.39, simulated on chain Nov 15): 12,036,623 units for 0.6 SOL (slot
469883188). The exit is not touched. The restart: seven floats, feed connected; SOL 1.8689, WBTC 0.992, PUMP 0.612,
SPCX 0.549, TTWO 0.580, DJT 0.596, HYPE 0.603, AAPLx 0.598 SOL. Day: 12 closed, 5 won, +0.8062 SOL.
**Nov 18 ~11:00 UTC (13:00 Beirut): TAB16RxX removed, wallet 4 back to paying from wSOL too** (the owner's call). TAB's
day: 17 real closed, 3 won, −0.7099 SOL; all 31 real −0.8764. The model on every one of its 49 copyable buys of the day
(`analysis/research/2026-11-17/wallet_hunt/out/e14_TAB16RxX_nov18.txt`, fetched from the chain) is −5.09 SOL, far below
the backtest's worst day (−2.20); on the 14 coins the bot traded, model −1.21 and live −0.71: the bot followed its
rules, the wallet's coins stopped running (a 210 s seller since Nov 17). Wallet 4: `float_only = false`, `min_sol`
back to 1.3 (1.2 was tested better only with floats only: with wSOL coins, +0.75 SOL, P 64.5%, worse at landing 8),
`max_premium 0.5` kept (+4.01 SOL with wSOL coins, P 98.4%, 4 of 5 weeks).

**Nov 18 ~06:45 UTC (08:45 Beirut): both units re-engineered, every combination by payment** (the owner's rule: floats
win and wSOL breaks even or loses, so wSOL goes; `analysis/research/2026-11-17/wallet_hunt/market/README_direct.md`,
"e8 v2" and "The double check"). Wallet 4's unit: `float_only = true`, `min_sol 1.2`, `max_premium 0.5` (backtest Oct 21 -
Nov 18: +53.17 SOL against +45.78 running, P(better) 91.4%, better at every landing; its wSOL-paid copies −0.81 SOL on
302); the exit not touched. TAB's unit: `max_premium 0.5`, tp 6 then **4.0** (the owner: 6x fires once in 2 days; 4x
about once a day, +0.94 SOL a day against +1.05, worst day −1.96; `out/e12c_TAB16RxX_tp_days.txt`); sell pressure 10/60
and stall 240 tested and not taken (their gain rested on a few copies); its sale not followed (following it: −6.00 SOL,
worse every week). TAB live so far: 19 real, −0.4908 SOL.

**Nov 18 03:52 UTC (05:52 Beirut): TAB16RxX copied live again, on wallet 4's wallet** (the owner's call: no second
wallet). The 4-day direct screen of every market wallet (Nov 14 01:07 - Nov 18 01:07 UTC, float-quote coins;
`analysis/research/2026-11-17/wallet_hunt/market/README_direct.md`) passed it alone on a real sample: 140 copies,
under the deployed exits +10.8% a copy (days 1-2 +5.7%, days 3-4 +13.9%), w/o 2% +3.72, P 99%. Unit `rugsnipe-long-tab`:
`min_sol 0.5`, 0.5 SOL x 2 (0.1 for its first 3 minutes), daily stop 1.5, tp 4.0, 600 s, sell pressure [5, 60, 30],
stall 180, its sale never followed, the main unit's 7 floats; the two units keep apart with `other_state_dirs`
(commit `6bc6120`: a coin the other holds is skipped; no account close while the other holds the coin). TTWO float
raised to 1.2 SOL in `/etc/rugsnipe/float-levels` (69% of its coins). Wallet 2.45 SOL + floats.
**TAB16RxX studied again and left paused (Nov 15 night, `analysis/research/2026-11-16/tab/`):** 890 copyable buys over
15 days (nothing copyable before Oct 31); what it would add to wallet 4 is +0.37 SOL a day at 0.5 SOL on 18.8 copies a
day, −2.52 without its best 5 trades; its own sale is not wallet 4's (the 86 copies it sold at 30-60 s lose 24% each).
The owner declined a paper run. Tested on wallet 4 the same night and not adopted: buy pressure as a guide for the
take profit (`2026-11-16/buy_pressure/`, from 1.2x) and buying that slows or selling that rises
(`2026-11-16/momentum/`).
**#41-#48 (Nov 15 20:53-22:26 UTC), each by its rules and equal to the chain** (journal / chain at the status price):
#41 `GqAzs7Pb` (SOL) sell_pressure +0.0725 / +0.0725 (wallet 4 −35.9% at 301 s); #42 `3DCv33mL` (SPCX) sell_pressure
−0.0538 / −0.0530; #43 `DAnPxZ7s` (TTWO) sell_pressure −0.0252 / −0.0237; #44 `Z3kN3Xpm` (TTWO) sell_pressure at 1.49x
+0.2120 / +0.2137; #45 `GkJDPnXR` (TTWO) its early sale −0.0307 / −0.0313; #46 `Dy1ZHNtB` (TTWO) its early sale
−0.1286 / −0.1292; #47 `wQPAb4FH` (SPCX) its early sale −0.1016 / −0.1020; #48 `AUtnQZej` (SPCX) sell_pressure −0.0740
/ −0.0727. A round trip now costs 0.00306 SOL (0.00261 before `cu_limit` 350,000). **The frozen setup so far: 10 closed
(#38-#48), −0.1073 SOL**; the seven `sell_pressure` exits +0.1536 together. Day: 17 closed, 6 won, +0.6833; all real
40, +0.3001; with holder fees +1.0638 SOL. SPCX at 0.378 SOL after three losses: the floats are now levelled by
themselves (`deploy/bin/rugsnipe-float-level`, a 5-minute timer since Nov 17, 10 before; only while no copy is open; docs/20 §3).
**#49 `CcV84RDz`** (SPCX, 22:49:40 UTC) sell_pressure at 1.02x after 61 s, −0.0211 SOL. **What the eight coins sold on
`sell_pressure` did afterwards** (`analysis/research/2026-11-16/live_checks/after_exit.py`, `out/after_exit_nov15.txt`;
each coin's trades for 31 minutes, the price in multiples of the price wallet 4's buy left): none reached 4x, before the
600 s timer or after it. Six were lower at the timer than where we sold (our sale -> the timer: E3c6RqFX 0.44 -> 0.35x,
GqAzs7Pb 1.05 -> 0.54x, 3DCv33mL 0.94 -> 0.82x, DAnPxZ7s 0.99 -> 0.81x, AUtnQZej 0.87 -> 0.85x, CcV84RDz 1.02 -> 0.86x),
two higher (Dyc9zPSt 1.75 -> 1.79x after a high of 2.89x at 250 s; Z3kN3Xpm 1.49 -> 2.09x after 2.37x at 297 s).
Day: 18 closed, 6 won, +0.6623; all real 41, +0.2790; with holder fees +1.0427 SOL; the frozen setup 11 closed, −0.1284.
**Nov 16 to 08:34 UTC (#50-#62):** the frozen setup at 24 closed (#38-#62), 7 won, **−0.8043 SOL**; Nov 16 −0.2491 to
then; all real 54, −0.3968; with holder fees +0.3669 SOL. **None of the 24 coins reached 3x**, while we held them or
after, in the first 600 s after wallet 4's buy (`analysis/research/2026-11-16/live_checks/out/after_exit_nov16.txt`;
highest while held 2.00x, #57 `4NahCr5e`; highest in the first 600 s 2.89x, #38 `Dyc9zPSt` at 250 s, after our sale).
In the backtest 11.6% of the copies cross 3x within 600 s and 6.8% cross 4x (`2026-11-16/buy_pressure/`): 2.8 and 1.6
expected in 24; none at 3x has about a 5% chance, none at 4x about 19%. So a take profit of 3x would have made no
difference to these 24. The owner's question on the pressure rule ("after his sell and earlier than 30 seconds"):
`2026-11-16/final_exit/after_his_sale.py` — counted from 0 / 10 s −4.94 / −2.61, from 20 s +0.79 (noise); after its
sale with no floor −0.37, with lower counts −3.09 to −12.04, out at once −26.70; its sale followed in its first 30 s
−9.38. Unchanged.
**#49-#63 checked on chain (Nov 16, to 11:59 UTC): all 15 equal the journal** within 0.002 SOL (#51 `CdM8ufFW`, the
first `stall` exit, −0.2990: two sell tries failed on chain with `Custom 6004` for 0.000355 each before the third
landed). The float top-up ran by itself between trades (SPCX +114,359 units at 22:43, TTWO, WBTC, PUMP). #63 `9WoGxMZD`
(SOL, 2 hops, filled 20.6% over its price) sold on `sell_pressure` at 34 s, −0.1469. **The frozen setup: 25 closed, 7
won, −0.9512 SOL**; Nov 16 −0.3960 to then; all real 55, −0.5437; with holder fees +0.2200 SOL.
**Is something wrong? No: the bot does what the backtest assumes** (`analysis/research/2026-11-16/live_checks/`
`live_vs_model.py`, `stretch.py`). The backtest model run on the same 24 coins (#38-#62): real −6.8% a copy, the model
at the exact place our buys landed −8.3%, at the backtest's landings −9.1%, wallet 4 on the same coins −5.6%; the exit
reason the same on 21 of 24. The coins were bad, not the execution. In the backtest (1,163 copies, +13.6% a copy on
average, **the median copy −7.1%**, the standard deviation 69.7 points) 6.0% of all runs of 24 consecutive copies are
this bad or worse, and 32.5% have no take profit. A run of 50 copies under the backtest's 5th percentile would say the
backtest no longer describes wallet 4.
**#63-#65 (Nov 16 to 14:28 UTC), equal to the chain** (#65 `Lu5fUofk` −0.2803 in the journal, −0.2664 at the status
price: the 14,000 lamports are TTWO's own fall since our buy; at the rate of our buy the chain gives −0.2802). **#64
`J8Lutktx` (SOL, 2 hops) sold on `sell_pressure` at 1.06x after 131 s, +0.1632; the coin then fell to 0.71x at 240 s,
went to 2.03x at 290 s and crossed 4x at 526 s (4.44x at 600 s)** (`live_checks/out/after_exit_nov16b.txt`). Wallet 4
sold it at 167 s at 0.98x. Every exit of the setup would have left it before the run: its early sale (167 s, under
1.5x), the stall (no new high from about 60 s, so about 240 s, at 0.71x); only holding to the timer with no other exit
catches it, which the backtest prices (`final_exit/`: no signals −6.54, its sale never followed −0.94). The frozen
setup: 27 closed, 8 won, −1.0680 SOL; Nov 16 −0.5131 to then; all real 57, −0.6608; with holder fees +0.1029 SOL.
The float top-up now keeps 0.6 SOL in the wallet (`85c24e7`): on Nov 16 it had taken the wallet to 0.65 SOL.
**Wallet 4's newest days, never studied (`analysis/research/2026-11-16/new_days/`):** Nov 15 13:04 - Nov 16 14:25 UTC,
32 copies, +11.0% a copy (the backtest +13.6%; 46% of its 32-copy runs are as bad or worse); the bot's run +1.22 SOL in
25.3 hours. **For the live hours the model gives −1.09 SOL on 26 copies; the bot's 27 real trades made −1.0680.** The
setup works as built and the edge is still there on the new coins; the live hours were the bad half of them.
**#66 `GTa6uKEz`, the frozen setup's first take profit (Nov 16 16:30 UTC):** TTWO float, bought in its slot (+0),
4.09x after 15 s, **+1.4537 SOL (+290.7%)**; chain (slots 470199169, 470199241) −160,327 then +627,396 TTWO units,
+467,069 units = +1.4535 SOL at the rate of our buy, less 0.00306 of fees. Wallet 4 +308.2%, sold at 92 s. **The frozen
setup: 28 closed, 9 won, +0.3857 SOL**; Nov 16 +0.9405; all real 58, +0.7929; with holder fees +1.5565 SOL. The win
sat in the TTWO float (2.05 SOL). The top-up's sale of the excess was refused by Jupiter (HTTP 429) at 16:55: since
`85c24e7` the script priced all seven floats once a float, a fault of mine; fixed in `b01919b` (one read a run). At
16:59 it sold 464,011 TTWO units for 1.4395 SOL (slot 470207435): **SOL 2.0861**, WBTC 1.004, the six others 0.593-0.604.
**#67 `8bGUGTEB`** (PUMP) `sell_pressure` at 0.90x after 54 s, −0.1038 (chain −2,491,062,499 PUMP units and the fees,
−0.1034 at the rate of our buy); **#68 `6zBt4nSa`** (SOL, 2 hops, filled 32.9% under its price) `sell_pressure` at 1.20x
after 222 s, **+0.3209** (chain −0.503219 + 0.824154); wallet 4 sold it at 13 s for −50.2%. **The frozen setup: 30
closed, 10 won, +0.6028 SOL; against wallet 4 on the same coins (29 with its result): +4.2% a copy against its +3.0%,
median −7.0% against −12.9%, better on 14, worse on 15** (its sale in its first 30 s not followed: #68 +64% against
−50%; it held longer and won on #38, #60, #61). Nov 16 +1.1577; all real 60, +1.0100; with holder fees +1.7737 SOL.
**The settings of the two signals, all of them, on the live setup** (`analysis/research/2026-11-16/signals/out/grid.txt`,
520 settings): windows of 20-45 s lose 5 to 21 SOL, 60-120 s are flat, counting from 0-10 s after its buy loses 3 to
5, SOL in place of the trade count loses everywhere, a stall under 120 s loses 2 to 17 and 180-300 s are flat (+3.1
at 300 s); the best joint setting +6.69, picked on two blocks −0.64 on the third. The live values stay. Top holders
with their real bags (`2026-11-16/holders/`, from the cached transactions): 33 rules, all lose 7 to 39 SOL.
**A second copy, of `TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3`, in paper from Nov 12** (the lookalike search,
branch `claude/dreamy-dijkstra-ln0wdk`, `analysis/research/2026-11-13/lookalikes/out/compare.txt`): the only wallet
that passed the pick-on-week-1 test (tp 3.0, 300 s: week 2 raw +13.76, corrected +20.95; week 1 raw −2.28 with the
live exit, its own week 1 −1.78 without its best 2). Checked Nov 12 with the bot's own detection on its last 150
transactions (`examples/scan.rs`, `W=`): its buys are seen and valued (SOL through Jupiter or wSOL, 4 of 31 unpriced);
its 1.0+ SOL buys that day were mostly in an unroutable quote (Xsc9qvGR), 2 of 7 routable. 74% of its transactions fail
(96% on Nov 12). Unit `rugsnipe-long-tab` (config `/etc/rugsnipe/long-tab.toml`, state `/var/lib/rugsnipe-long-tab`,
wallet `tab-wallet.json`): min_sol 1.0, tp 3.0, 300 s, no stop, its sale not followed, paper at 0.1. Real only after
its paper record, at 0.1 SOL with its own wallet.
The exact check (the bot's own detection over all its 1.0+ buys, lookalike branch commit `89b9332`,
`out/scan_score_TAB16RxX.txt`): 183 copyable first buys (week 1 53, week 2 130; 55 route from our WBTC float), still
10-32 a day on Nov 10-12. Tp 3.0 + 300 s at landing 4: week 1 raw +1.28 (−2.36 without the best 2), corrected +6.63;
week 2 +3.08 (−3.23), corrected +13.03. Raw without the best 2 is negative in both weeks for every exit; the profit
rests on the correction (+10.5 / +8.5 points, measured on its own trades, never yet on our fills). Without the WBTC
routes it loses raw in both weeks. Weaker than the route-class approximation (+13.76 raw in week 2).

**Wallet 4 against us on the same coins, Nov 12 (status --chain on the box):**

| # | Coin | Us | Wallet 4 | It sold after |
|---|---|---|---|---|
| 0 | Ci9Bg1Bx | −59.7% | +2.9% | 303 s |
| 1 | BttUQVPM | −45.5% | −28.1% | 179 s |
| 2 | 5tePJcGm | +353.1% | +113.3% | 224 s |
| 3 | 7dDprVHP | −22.1% | −11.3% | 302 s |
| 4 | 57pQW4mw | −2.5% | −24.0% | 182 s |
| 5 | Eymbsj8M | +124.6% | +93.4% | 289 s |
| 6 | GZn6HC8d | −75.3% | −71.4% | 141 s |
| 7 | GaHAZThn | −37.7% | −13.6% | 299 s |

Average a trade: us +29.4%, wallet 4 +7.7%. The early-sale rule (`follow_early_s`, on since Nov 12 23:54 UTC) would
have followed its sales on #1 (179 s) and #6 (141 s). TAB16RxX in paper: 2 closed on Nov 12 (4GrVD8NA −24.6%,
BW41hQ7J −35.0%, both on the 300 s timer).

**First 3 closed (Nov 12, checked on chain, journal = chain):** +0.2479 SOL. All three landed in wallet 4's own block
(3, 7 and 8 coin trades between its buy and ours).

| # | Coin | Exit | Real | Raw model, same landing | Real minus model |
|---|---|---|---|---|---|
| 0 | `Ci9Bg1Bx` | timer (2 sells failed 6004, the 3rd landed) | −0.0597 | −0.0372 | −22.5 pts |
| 1 | `BttUQVPM` | timer | −0.0455 | −0.0368 | −8.7 pts |
| 2 | `5tePJcGm` | take profit, 351 s | +0.3531 | +0.1475 | +205.6 pts |

Source: `analysis/research/2026-10-31/since_stop/out/live_nov12_vs_model.txt`. Too few to judge: one win carries the
total, and the two losers did worse than the model.

Wallet 4 on the same coins (`his_vs_ours.py`, `out/his_vs_ours_nov12.txt`): it sold all three after 3 to 5 minutes;
we hold to our own exits.

| Coin | Wallet 4 | We | Its sale |
|---|---|---|---|
| `Ci9Bg1Bx` | +2.9% | −59.7% | after 303 s |
| `BttUQVPM` | −28.1% | −45.5% | after 179 s |
| `5tePJcGm` | +113.3% | +353.1% | after 224 s |
| Total | +39.4% (+2.22 on 5.65 SOL) | +82.6% (+0.248 on 0.3 SOL) | |

## Where things stood (Nov 3)

**Nothing runs; no box exists since Oct 29.** The plan for the next box ([`08-new-box/`](08-new-box/README.md)) is
4 SOL in two wallets. Its backtests give about +0.7 to +3.5 SOL a day (§1 there); expect the low half.

| Bot | Copies | Stake | Open at once |
|---|---|---|---|
| The long copy | wallet 4's part A | 1 SOL | 2 |
| The copier | Rafinhaaaaaa | 1 SOL | 1 |

It is prepared, not started: paper first, then the first live hours at 0.1 / 0.3 SOL.

**Nov 4, wallet 4 since the box died** ([`analysis/research/2026-10-31/since_stop/`](analysis/research/2026-10-31/since_stop/README.md)):
it changed its rule again (the 30-minute timer is gone, early sales on two thirds of its big buys), took 510 SOL of
profit on Oct 30 and kept trading (balance 114 → 393 SOL by Nov 4). The long copy as built would have made +1.79 SOL in
5.9 days at 1 SOL × 2, about zero without the best 2; **with no stop, +6.92**, better at every landing and in both
halves. The plan's long config now sets `stop = 0.0` (the code allows it since Nov 4).

## Wallet 4

### Where things stood (Oct 28, evening)

**Re-examined on Oct 28** ([`07-rework-2026-10-28/`](07-rework-2026-10-28/README.md)): wallet 4 still makes money (+82 SOL
in the 38 hours to Oct 28 14:54 UTC) and is one bot with no siblings, but it **changed its rule on Oct 27** (early sales
on 49% of its big buys, against 3.5% in the week the strategy was picked on), and on that fresh period the long copy
**loses** (−2.02 SOL on 25 copies; about flat as the bot really trades). The paper run's +2.47 SOL came from 3 coins
that graduated, a kind no earlier backtest contained. The code review found 8 money-losing bugs in the never-run real
path; **fixed, tested, and simulated on mainnet**. Part B cannot be routed through pump's programs at all. The plan: 2-3
more days of paper with the hardened bot on a €59/month Frankfurt box (running since Oct 28 17:58 UTC; Ohio was
terminated that evening), then the 0.1 SOL test, then decide.

**Nov 2: the copier** ([`docs/21-copier.md`](docs/21-copier.md), `rugsnipe-long copy`). It copies several wallets on
any venue through Jupiter, so wallet 4's part B (pump coins priced in PUMP, CARDS, USDC ...) is tradeable now. So are
other wallets' coins on Meteora and Raydium. Code, tests, the unit and a paper replay are done. **Nothing has run on a
box** (none exists since Oct 29). Part B copied through Jupiter is weak (`analysis/research/2026-11-02/`): +4.88 on
Oct 23-26, +8.08 on Oct 27 - Nov 1, −6.05 without the best 2. It is off in the 4 SOL plan (`config/copier.example.toml`). The same study
found no rule to pick part-A or part-B launches ourselves.


| | Strategy A: the long copy | Strategy D: the launch copy |
|---|---|---|
| What | copy its **1.45+ SOL buys of coins priced in other tokens** that pump's own programs can route; 1 SOL each; sell at 2.0x / 0.8x / 1790 s / behind its own sell | copy its **launch buys of SOL-priced coins**; sell at create + 12 slots (about 5 s); 20% price bound |
| Its share of wallet 4's profit (Oct 19-27) | part A: **+102 of +355 SOL** | a slice of part D: +29 of +355 |
| Backtest (out of sample Oct 23-27) | **+11.13 SOL** at 4 open (Oct 19-22: +6.73) | +0.22 (P2), +1.48 (live replay); slightly negative without the 2 best coins |
| Live | **paper only**. On the Ohio box Oct 27 16:11 UTC to Oct 28 (old code): 21 closed, 9 won, **+2.4666 SOL** to Oct 28 13:31 UTC (+1.57 at the backtest's costs; all of it 3 graduated coins); checked on chain: nothing missed. On the Frankfurt box: paper 17:58-18:34 UTC, then **real money at 0.1 SOL since Oct 28 18:34 UTC** (wallet `E7KX1hcM...`). **At 0.1 SOL, 18:34-22:04 UTC: 6 closed, 4 won, +0.3146 SOL**, every trade checked on chain, 5 of 7 buys in its own slot. **Since 22:04 UTC: 0.5 SOL × 3 open, daily stop 1.0** (the owner's decision). First night at 0.5: 7 closed, 3 won, +1.08; **13 closed, 7 won, +1.39 SOL since the start**. **Since Oct 29 08:21 UTC: 1 SOL × 3 open, daily stop 3.0** (the owner's decision), 3.2 SOL put in, 4.6 SOL in the wallet | **real money** Oct 26 17:36 → Oct 27 07:50 UTC: **+0.1456** on 77 filled; **about −0.43** with the stuck coin 2RR6sfbi |
| Status | **stopped: the Frankfurt box was deleted by Cherry on Oct 29 ~13:40 UTC for a zero hourly balance, the wallet's only key with it; 4.5 SOL lost** (`03-strategy-A-long-copy/deploy-frankfurt.md`). Before that, live at 1 SOL × 3 on the Frankfurt box (`fra-long`, Cherry VDS, this branch's code) since Oct 29 08:21 UTC, after 0.5 SOL from Oct 28 22:04, 0.1 SOL from 18:34 and 36 minutes of paper; next: watch the book without the best 2, wallet 4's pace and its early-sale rate daily ([the plan](07-rework-2026-10-28/README.md#6-the-plan-how-to-go-live-again-in-order)) | **stopped**: the copy bot is off and its server (fra1) terminated |
| Pages | [`03-strategy-A-long-copy/`](03-strategy-A-long-copy/README.md) | [`04-strategy-D-launch-copy/`](04-strategy-D-launch-copy/README.md) |

**Known problems, read before trusting any number:**
- **The stuck coin 2RR6sfbi** (a D copy): it graduated as we bought, the copy bot failed 405 curve sells, and it cost
  about **0.57 SOL**. Fixed in code, never deployed. → [`05-live/stuck-coin-2RR6sfbi.md`](05-live/stuck-coin-2RR6sfbi.md)
- **check.sh's per-coin "ITS NET" for wallet 4 is wrong coin by coin** (only the total is right), and its "since the
  start" line counts closed trades only (−0.76 while the wallet was −1.41).
- **The Ohio paper run was optimistic:** it filled at the slot it saw the buy and sold on the firing trade; the hardened
  code (on the Frankfurt box) fills and sells a slot later. 4 of 5 of its take profits came within 10 s.
- **Wallet 4 changed:** early sales on 49% of its 1.45+ SOL other-quote buys since Oct 27 (3.5% on Oct 19-22, 13.6% on
  Oct 23-27), confirmed on chain; the copy as tested loses on Oct 27-28 (`07-rework-2026-10-28/`). Its copyable buys fell
  to 11 in the 15 hours of Oct 28. It put 5 SOL into a privacy pool on Oct 27; its predecessor wallet was emptied the
  same way on Oct 17.
- **The paper run's profit is 3 coins** that graduated before wallet 4 sold; the other 18 sum to about zero.
- **The code before Oct 28 evening had 8 bugs that would lose money live** (`07-rework-2026-10-28/code-review.md`):
  fixed on this branch, which is what the Frankfurt box runs.

## A to Z

| Folder | What's in it |
|---|---|
| [`01-who-it-is/`](01-who-it-is/README.md) | wallet 4: how it was found, its +355 SOL, its rule (2.5x / 0.7x / 30 min), bet sizes, coins at once, fees, what's changing |
| [`02-decomposition/`](02-decomposition/README.md) | **where its profit comes from, parts A-F**, over 8 days and in check.sh's window; what we can and can't trade, and why |
| [`03-strategy-A-long-copy/`](03-strategy-A-long-copy/README.md) | the long copy: [rule and code](03-strategy-A-long-copy/README.md), [every backtest](03-strategy-A-long-copy/backtests.md), [the paper run](03-strategy-A-long-copy/paper-run.md), [running it on Ohio](03-strategy-A-long-copy/deploy-ohio.md), [going live](03-strategy-A-long-copy/going-live.md), [changes](03-strategy-A-long-copy/changes.md) |
| [`04-strategy-D-launch-copy/`](04-strategy-D-launch-copy/README.md) | the launch copy: rule, how it was found and tuned, live results, why it made +0.15 while wallet 4 made +2.77 |
| [`04-backtests/`](04-backtests/README.md) | an index of every test, its result, its page and its script |
| [`05-live/`](05-live/README.md) | **check.sh exactly as pasted**, the copy bot's history, the paper history and journal, the stuck coin, the timeline, the money |
| [`06-infrastructure/`](06-infrastructure/README.md) | the boxes (fra1 and Ohio terminated; the Frankfurt box), the code map, deploy files, runbooks, wallets |
| [`07-rework-2026-10-28/`](07-rework-2026-10-28/README.md) | **the Oct 28 rework**: every decision re-examined, the fresh data (P3), the code review and fixes, wallet 4 on chain, where to run it, the plan |
| [`analysis/research/2026-10-29/wallets/`](analysis/research/2026-10-29/wallets/README.md) | **other wallets with wallet 4's edge? (Oct 29)**: 856 coins' early buyers, 24 hours of creates, 6 wallets scored in full: none copyable; wallet 4 is alone in holding its big launch buys |
| `docs/` | the project's original docs: 00-08 (background, mechanics, speed, architecture, deploy, runbook), 19 (copy targets; §11 found wallet 4, §13 strategy D), **20 (the long copy)**, `docs/research/` (the early research), `docs/PROJECT-README.md` (the original repo README) |
| `analysis/research/` | the studies: `2026-10-26/h9/` (D), `2026-10-26/wallets2/` (the search), `2026-10-27/h9long/` (A, 8 days), `2026-10-27/refused/` (refused copies), `2026-10-28/` (decomposition of check.sh's window, the paper chain check, single coins; **`fresh/`** the study on Oct 27-28 data, **`more/`** the skipped trades and copying better, **`wallet/`** the wallet check) |
| `data/datasets/` | the fetched data behind the studies, compressed; see CLAUDE.md "Datasets" |
| [`08-new-box/`](08-new-box/README.md) | **the next box**: both bots, 4 SOL, every step from an empty server to live |
| [`rafinhaaaaaa/`](rafinhaaaaaa/README.md) | **the second copied wallet**: who it is, its rules, its backtests, the analysis pipeline, its data |
| `crates/`, `deploy/`, `config/` | the code (Rust workspace), install and units, config templates (`long.example.toml` the long copy, `copier.example.toml` the copier) |

## The words used

- **curve**: pump.fun's bonding curve, where a new coin trades until it fills; then it **graduates** to a **PumpSwap**
  pool.
- **priced in SOL / in another token**: the curve's quote token. Wallet 4's best coins are quoted in WBTC, PUMP, CARDS ...
- **launch buy**: a buy in the coin's create slot or the next. **slot**: about 0.2 s (211 ms measured on Oct 28; older pages say 0.4 s). **create + 12**: 12 slots after the
  coin's create.
- **route**: how our buy reaches the coin (`multi_hop_swap` from wrapped SOL or a WBTC float, at most 2 hops).
- **paper** (`mode = "log"`): decisions priced on the live curve, nothing sent. **P1 / P2**: Oct 19-22 / Oct 23-27.
- **(+x)** after a result: the same without each period's best 2 trades. **P3**: Oct 27 00:20 → Oct 28 14:54 UTC.
- **Beirut time** = UTC+2 on these dates (check.sh and history tables); docs use UTC.

## Security

This repo is **public**. It has no private keys, API keys or config files with credentials. Wallet addresses are public
chain data. fra1's backup (keys included) was only on the Ohio box and went with it on Oct 28; none of it is in
git. A pre-commit hook
(`.githooks/pre-commit`, enable with `git config core.hooksPath .githooks`) refuses key material.
