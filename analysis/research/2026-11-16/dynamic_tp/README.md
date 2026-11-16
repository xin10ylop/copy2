# A take profit that follows the coin (Nov 16)

The owner, after #66 `GTa6uKEz` reached 4x in 15 s: "set a max timer for that x seconds ... start adjusting tp depending
on how the coin behaves, and test this behaviour with several logical metrics", then "also test for lowering tp ... to
catch some profits from coins that don't go to 3 or 4x". This model (`dynamic_tp.py`) gives +73.72 SOL for the live setup
where `../final_exit/` gives +75.29: it sells one trade later than the timer when a signal fires on the trade before it.
Every gain below is against its own +73.72. Checked on the three blocks, redrawn days, walk-forward, and wallet 4's
newest days (Nov 15 13:04 - Nov 16 14:25, `../new_days/`), which no study had used.

    python3 -I dynamic_tp.py CQ ALL NEW > out/dynamic_tp.txt     # raising it for the strong coins, the fast runners (162)
    python3 -I lower_tp.py   CQ ALL NEW > out/lower_tp.txt       # lowering it for the weak ones, or with time (60)

**Raising it (`out/dynamic_tp.txt`)** — a copy is strong at 30 or 60 s by its price, its net buying or its trades:
- 40 of 162 settings ahead of live, 8 in all three blocks. The best: a coin that reaches 4x within 30 s keeps no take
  profit (out on the other exits): **+4.49**, but without the best 5 trades behind live (+62.95 against +64.09) and 4
  losing days against 3: a few bigger runs. Busy coins (50+ trades by others in the first 60 s) get tp 6, the rest 4:
  **+4.17**, better without the best 5 (+65.55), 87% of redrawn days ahead.
- Walk-forward: the best on A+B (that one) +0.37 on C; the 10 best on A+B +0.18 on C on average, 8 of 10 ahead. Newest
  days: +0.54 for it, +0.00 for the fast-runner rule (no coin reached 4x within 30 s there).
- #66 itself (`../live_checks/out/after_exit_66.txt`): after our sale at 4.06x (15 s) it reached 5.92x at 58 s and was
  at 3.85x at the timer.
- **Not beyond the noise (±3.4 SOL) by enough to change a frozen setup:** a candidate for the review at about trade #88.

**Lowering it (`out/lower_tp.txt`): every one of the 60 settings loses.**
- For the weak coins only (weak at 30 or 60 s), tp 1.3: −11.06 to −30.14; 1.5: −8.42 to −24.38; 2.0: −6.22 to −18.14;
  2.5: −3.93 to −10.61. None ahead.
- For every copy after 2 / 3 / 5 minutes: −5.31 to −23.14. Walk-forward: the 10 best on A+B −1.87 on C, none ahead.
- A coin that looks weak at a minute and is at 2x is not done more often than it is; selling it there cuts the runs, and
  the coins that peak at 1.5-2.5x and fall back are already sold near their top by the pressure and stall rules.
