# The sell-pressure audit (Nov 20)

The owner: "you sure sell pressure is the most optimal? how we are using it? audit it". The live exit was picked on
Oct 21 - Nov 15 (`../../2026-11-16/signals/`) and frozen Nov 15 19:29 UTC. Here it is scored on what came after.

Run: `candidates/c1_fetch.py` (SUB=w4since, 5.15 days of wallet 4), Jupiter prices into `SP/w4since/prices.json`, then
`RPC_URL=... LK=SP/lk python3 -I f1_paths.py SP > out/f1_paths.txt` (148 coins, ~30 min) and
`LK=SP/lk python3 -I e1_exits.py SP > out/e1_exits.txt`.

**The code** (`crates/rugsnipe-long/src/pos.rs` `signal_due`, `engine.rs` the flow): the backtest's rule exactly: the
other traders' trades after our fill (ours and wallet 4's left out), sells minus buys over the 60 s before the latest
trade, from 30 s after its buy, at 5 or more. It counts trades, not their size, and fires at any price.

**Out of sample: wallet 4's 146 token-coin buys of 1.3+ SOL, Nov 15 19:56 - Nov 20 17:12 UTC, 1 SOL a copy:**

| exit | SOL | a copy | w/o best 2% | halves | thirds |
|---|---|---|---|---|---|
| live (sp 5/60, stall 180, its early sale, tp 4, 600 s) | +5.42 | +3.7% | -1.52 | +5.53 / -0.11 | +5.06 / +3.66 / -3.30 |
| no sell pressure | +5.11 | +3.5% | -2.61 | +5.85 / -0.74 | |
| no sell pressure, no stall | +2.89 | +2.0% | -4.84 | | |
| sp 10/60 | +5.97 | +4.1% | -1.03 | +4.51 / +1.46 | |
| sp only under our fill | +6.64 | +4.5% | -1.09 | +7.64 / -1.00 | |
| its sale always followed | +7.31 | +5.0% | +0.38 | +5.11 / +2.21 | |
| **its sale always, no sp** | **+8.88** | **+6.1%** | **+1.89** | **+4.77 / +4.11** | **+4.72 / +2.92 / +1.24** |
| tp 2 / tp 3 / no tp | -4.52 / +1.37 / +5.92 | | | | |

- **Sell pressure is neutral here:** it changed the exit on 99 of 146 copies for +0.31 SOL in all (helped 72: +8.18,
  hurt 27: -7.87). It is not what lost money; it is not what makes it either.
- **Following wallet 4's sale at any time is the only change ahead in both halves and without the best 2%,** and the
  lead comes from the last days: by day +0.91 / +6.64 / +2.43 / +2.62 / -2.10 against live +0.25 / +7.29 / +3.35 /
  -1.51 / -2.43 (Nov 16-20); Nov 19 alone +4.13. It fits wallet 4's change: 80-89% of its big buys now get their first
  sale within 290 s (`../w4_today/`). On Oct 21 - Nov 15 the same rule lost 8-23 SOL (`signals/` round 3).
- Picked out of 25 variants on these 146 copies; the model fills in the slot after its buy and has no max_open.

## Longer, and every combination picked on seen weeks (Nov 20; the owner: "do the backtest on longer ... 2 weeks seen
then 2 weeks unseen ... all the combinations, in all increments")

`e4_long.py` (`out/e4_long.txt`): the same model over **1,175 copies, Oct 21 - Nov 14 01:07 and Nov 15 19:56 - Nov 20
17:12 UTC** (the research corpus as `market/m15f` loads it, plus f1's coins). **Over 25 days the live exit makes +131.16
SOL (w/o 2% +64.13); following its sale at any time without sell pressure +64.80 (+4.41): half.** Its lead is the last
5 days only (+8.88 against +5.42); by week, Oct 21 / 28 / Nov 4 / 11 / 18: live +16.92 / +68.14 / +20.24 / +26.45 / -0.59,
it +3.10 / +35.91 / +4.04 / +18.81 / +2.94. Without sell pressure (its early sale kept): +131.52, the same as live.

`g1_grid.py` (`out/g1_grid.txt`): 282,240 settings (take profit 1.5-8 or none x timer 120-1200 s x sell pressure off or
3-15 sells over 30-120 s x stall off-300 s x its sale never / early / always x price limit 1.25x-none x its buy 1.3+ /
1.5+ / 2+), picked on the seen weeks by the SOL without the best 2%:

| split | live: seen -> unseen | live's rank unseen | the 10 best on seen, unseen | top 1% seen, unseen median | all settings, unseen median |
|---|---|---|---|---|---|
| A: seen Oct 21 - Nov 4, unseen Nov 4 - 20 (658 / 517) | +85.06 -> **+46.10** (w/o 2% +17.47) | 3,476 of 282,240 | +35.86 to +42.67 | +37.96 | +25.97 |
| B: seen Oct 31 - Nov 14, unseen Nov 15 - 20 (529 / 146) | +72.55 -> **+5.42** (w/o 2% -1.52) | 92,677 | -0.76 to +0.70 | +0.03 | +4.37 |

- **Re-picking on the seen weeks does worse on the unseen weeks than keeping the live exit, in both splits.**
- Each part alone (mean over all other settings, unseen A | B): take profit 4-5 best (4: +28.7 | +5.0; 1.5: +16.0 |
  +1.3); its sale "always" the worst in A (+22.8 against +27.4 early) and the best only in B (+5.0 against +3.5); sell
  pressure 5/60 among the better in A (+27.8, off +25.7), about neutral in B (+3.7, off +3.3); stall and timer flat; the
  price limit 1.5x-none the same; its buy 1.3+ the most SOL.
