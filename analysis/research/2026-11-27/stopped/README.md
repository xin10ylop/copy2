# The three stopped units: did their wallets recover after we stopped? (Nov 27)

The owner: "check these too if they recovered or if it was a goood decision to remove them". Each wallet's last 3 days
(Helius, `histstop_<wallet>`), our copy replayed with the unit's live exit on its buys AFTER the stop only, 1 SOL a copy.
- www (CqCAzte8, stopped Nov 26 00:15 UTC): `../../2026-11-24/ideas/e1_ideas.py` UNIT=cq, T_MIN Nov 26 00:00 -> `www_since.txt`.
- fff (E5CLHHz6, its last copy Nov 27 10:32 UTC): UNIT=all, T_MIN Nov 27 10:40 -> `fff_since.txt`.
- fat (FatoU1bj, stopped Nov 25 night): `../../2026-11-24/fatou_exit/x1_exit.py` with its history cut at Nov 26 00:00 UTC as
  OLD (`histcut_`), the rest NEW -> `fat_since.txt` (its live exit: its sale +2 slots, tp 1.5x, 15 s).

| Unit | Since the stop | Its own result | Our copy, the unit's exit | Verdict |
|---|---|---|---|---|
| www CqCAzte8 | Nov 26-27 | +5.10, +3.75 SOL | **+11.3% a copy on 39, +4.40 SOL at 1 SOL (+3.33 without the best 2%), 4 of 4 blocks** | recovered: the stop cost about +2.2 SOL at its 0.5 stake |
| fat FatoU1bj | Nov 26-27 (352 buys) | **+60.16 SOL** (433 coins) | **-2.2% a copy, -21.86 SOL at 1 SOL without the best 2%** | right: its edge is its speed, our copy a slot later loses |
| fff E5CLHHz6 | Nov 27 10:40 on (2 buys) | -0.72 SOL on Nov 27 | -9.3% on 2 | too early; still losing |

## www (CqCAzte8): should it come back? (the owner: "check deeply if we should add it back, check how it stands on sss too")

- **The deep test, 14 fresh days** (`../../2026-11-20/tape_screen/out_w3/CqCAzte8_*_nov27.txt`, 293 buys of 0.5+ SOL): the rolling
  pick FAILS (blind +3.4% a copy, -2.73 SOL without the best 2%, 1 of 3), the picks unstable; but the fixed exits hold up:
  tp 3x / 420 s / stall 240 on all coins **+10.5% a copy (293), +17.93 SOL at 1 SOL without the best 2%, 3 of 4 blocks**; tp 2x /
  120 s +7.1%, 4 of 4. Its own result -11.30 SOL over 15 days, up on 7 (Bing35WC, our best, loses too).
- **The exit and rule search** (`../exits_all/out/www.txt`, `www_rules.txt`): the standard exit stays (the walk-forward +9.6%
  against +9.7%); **its SOL coins do better on the standard exit than on their own** (the live unit ran tp 2x / 120 s on them:
  the SOL-coin exit picked blind +14.37 stakes against +22.01 with the standard exit); its buys of 0.1-0.5 SOL add +12.24 stakes in
  14 days, 3 of 4 blocks, +9.73 without the best 2% (67 such buys: rule B).
- **Live against the backtest of the same days** (Nov 22 07:35 to Nov 26 00:15 UTC): live 83 trades -0.6648 SOL (-1.6% a copy);
  the replay of its 125 copies of those days with the live rule -0.5% a copy. The bot did what the model says; it ran through
  the wallet's worst days (its own -13.91 on Nov 23, -7.72 on Nov 25). Before: +16.3% a copy (128); after: +11.2% (40).
- **sss, Nov 27 15:03**: #51 of 4,349 by the mean, #71 of 1,517 by consistency, all its copies up 5 of 7 days, +4.4% (+1.2%
  without the best 2%): mid-pack among ours (behind iii, ppp, uuu, rrr; ahead of ooo, ttt, yyy, eee).
- **Verdict:** back at 0.25 SOL, its SOL coins on the standard exit (`sol_exits = false`), floor 0.1 SOL, daily stop 0.5.

## www back on, then off again (Nov 27 evening)

Re-enabled at 0.5 SOL in the afternoon; by 18:20 UTC 5 real copies closed, -1.1226 SOL (pnl), the daily stop reached. On chain
(public RPC, both wallets since 13:00 UTC): CqCAzte8 itself lost on all 5 coins (218CbTVj -10%, AmRK6MMZ -11%, GmeML5Tq -26%,
2aakMixm -2%, 3NSUeHQX -8%), selling 31-84 s after its buy on 4; our exit held to the stall and lost -26% to -69% (-0.153, -0.347,
-0.308, -0.130, -0.187 SOL). The bot followed its rules; the wallet had a bad session, as its 14-day block 3 (-11.5%) and its own
-13.91 SOL day show it can. The owner: "lets jsut remove it". 88 real in all, -1.7875 SOL.
