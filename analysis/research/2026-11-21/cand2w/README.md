# Two weeks of one wallet, the whole process (Nov 21)

The owner: "take the best wallet in the recorder for now and do a 2 week backtest, unseen, seen, the whole process, fast".
64hJxoZz (`64hJxoZzjoL6MW4uwdKDkaBiZdk87ZxmthHnLwaAKUgS`): in the box's first screen (Nov 20, 10.4 h of tape) the wallet
with the most copies up on both halves (21 / 7, its 300 s hold +13.0% / +17.3%). Run: `candidates/c1_fetch.py`
(SUB=cand_64hJxoZz, 14 days: 6,345 transactions, 2,118 coins bought, 1,584 first buys of 0.5+ SOL), `b1_paths.py` /
`b1b_resume.py` (150 of them at random, each coin's 31 minutes from its buy), `b2_grid.py` (`out/b2_64hJxoZz.txt`;
`out/b2_64hJxoZz_livecost.txt` at the bot's real cost, 0.0064 a round trip). AggdaT4F was started too and stopped
(the owner asked for one wallet).

**Result: not copyable.** It holds a median 4 s (80% of its coins sold within 20 s): a speed trader, the kind the screen
now leaves out. Our copy at 1 SOL, 148 copies, week 1 (Nov 7-14) 82, week 2 (Nov 14-21) 66:
- wallet 4's live exit on every copy: week 1 -15.75 SOL, week 2 -4.77 (at the real cost -13.48 / -2.95);
- the best of 188,160 settings on week 1 (0.5+ SOL coins, tp 1.5x, 120 s, its sale followed) is itself -4.69, and -1.15
  in week 2; the top 1% of week 1: week 2 median -1.15; 5% of all settings up in week 2 (16% at the real cost).

## J3MxZcfV (Nov 21, the next wallet that holds longer)

Holding checked on 1-2 days of five candidates of the first screen (`SP/holdcheck*`): 5D6Ms4cP median 1 s, 7q15WZ4i 6 s,
BxnANx8P 20 s (49% under 20 s), FF9PekJ4 too many transactions to read (a bot), **J3MxZcfV 64 s (18% under 20 s)**. Its
history is new: first trade Nov 19 (61 transactions Nov 19, 282 Nov 20, 22 Nov 21 to ~01:00 UTC; 36 coins). Run on the
17 coins fetched (the owner: "run the test on the 16 coins"; `MIN_SEEN=6 MIN_UNSEEN=5`, `out/b2_J3MxZcfV_16.txt`):
holding on these 30 s median, 41% under 20 s; halves Nov 19 21:46 - Nov 20 ~09:50 (9) and to Nov 20 21:51 UTC (8).
Wallet 4's live exit on every copy: -2.71 / -0.81 SOL. The best setting of the first half is itself -0.78 on 6 copies
(0.5+ token coins, tp 1.5x, sp 8/30, its early sale) and +1.92 on 6 in the second; 59% of all settings up in the second
half. **Too few copies to judge either way (6 a half: about +/-50% a copy of noise); followed on the tape.**
All 28 coins with a path (`out/b2_J3MxZcfV.txt`, `MIN_SEEN=8 MIN_UNSEEN=8`; halves 10 / 18 copies): holding 34 s median,
29% under 20 s. Wallet 4's live exit -2.64 / -2.67 SOL; the best first-half setting -1.74 on 10 and +2.12 on 18 in the
second (+11.8% a copy, w/o 2% +1.09); all settings' second-half median -1.54, 41% up. Still undecided; followed on the tape.

## HANcjmXU, 10 days (Nov 21; the owner: "test him for 10 days, the regular workflow")

Closest to wallet 4 in the 21 h screen (holds minutes, 1.5+ SOL buys, part TTWO coins; wallet 4's exit +7% a copy on its
tape copies). 10 days of history: 12,792 transactions, about 1,350 coins (38-208 a day), 1,116 first buys of 0.5+ SOL; 250
of them at random. On the first 169 with a path (Nov 11 20:22 - Nov 19 00:33 UTC; halves 105 / 64; `out/b2_HANcjmXU_174.txt`):
**it holds a median 153 s (5% under 20 s): copyable in style, and our copies lose.** Wallet 4's live exit -5.07 / -6.57 SOL;
the best setting of the first half (1.5+ SOL token coins, tp 2.5x, 450 s, stall 300) +3.30 on 22 -> -6.73 on 29 (-23.2% a
copy); the top 1% of the first half: second-half median -4.98; 17% of all settings up. At the bot's real cost: the best
first-half setting +6.96 on 75 -> -6.57 on 50.
