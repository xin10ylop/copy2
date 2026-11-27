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
