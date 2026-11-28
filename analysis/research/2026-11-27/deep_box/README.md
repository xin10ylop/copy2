# The deep test on the box (Nov 27)

The owner: "please on this sss, pick wallets carefully, but that doesnt mean dont pick, that means knowing what to pick,
also do the same treatment for qqq, for each wallet". Each candidate gets the full work wallet 4's exit had, before any SOL:
the blind rolling pick (`w3_robust.py`), the coin kind x size x exit table (`w3_setup.py`), the exit grid of 12,960 settings
on the copies it would take and on those it would not (`../exits_all/x1_grid.py`), the exit and rule search (`x2_analyze.py`,
`x4_rules.py`: floor, coin kind, price limit, a token exit and a SOL exit, walk-forward), then a verdict by fixed rules
(`x5_verdict.py`). It runs on the Frankfurt box (`deep`, `run_deep.sh` -> `deep_job.sh`, a background service like `sss`),
with a Helius key kept in a root-only file there: this session's container lost its key on a reset (Helius takes the key only
in the URL, so the environment's header secrets cannot carry it).

**The rules (x5_verdict.py), fixed before any of the candidates below was tested:** R1 the standard exit over 14 days over +3% a
copy, positive without its best 2%, positive in 3 of 4 blocks; R3 40+ copies. **A worst-block floor was tried and dropped:** on
the wallets we know, a -10% floor would have cut www (-11.0%) and fff (-10.9%), which lost live, and also iii (Bing35WC, -10.7%),
our best live unit. So the guard against a www is the stake and a stop set in advance: a PASS starts at 0.25 SOL, daily stop 0.5,
stopped at -1.0 SOL in all or if negative after 20 trades.

**The candidates from the Nov 27 20:25 screen** (rules written first: the top 15 of the method test's winner, consistency std,
and the top 15 by consistency; 20+ copies, own result positive, over +2% a copy without its best 2%, not tested before; CNQQuavw,
a near miss on Nov 26, retested): CNQQuavw, ArB1vFG6, AmyhpdFR, wik1TBPz, 4uhwfQ9J, HSCtp6n1, Daune5i3, 2z2q5gk8, 54CjYyES,
9tYFSP8X. Left out: JAmx4Wsh, HzmDQnd5, 58PzAPMz, 5CcHnagY (they lose themselves), 6CtBXhwk (+1.3% a copy without its best 2%).

## Results (Nov 27 19:11-23:26 UTC; `out/candidates.txt`, `out/ours.txt`, the files per wallet in `out/`)

The candidates: **PASS CNQQuavw** (+6.8% a copy on 221, 4 of 4, +6.85 SOL at 1 SOL without the best 2%, the blind pick PASS; the
rule search: its buys of 1.0+ SOL, +1.98 stakes in 14 days, 4 of 4; it loses itself, -61.69 SOL over 15 days) and **wik1TBPz**
(+9.4% on 107, 3 of 4, +4.00; the blind pick FAIL; own +18.12 SOL). FAIL: ArB1vFG6, AmyhpdFR, 4uhwfQ9J, HSCtp6n1 (negative on the
standard exit; three of them lose heavily themselves), Daune5i3, 2z2q5gk8, 54CjYyES, 9tYFSP8X (under 40 copies; they looked strong
on the 6-day tape, 20-27 copies).

Our running units (all their coins of 0.5+ SOL, the standard exit): PASS iii, eee, jjj (thin: +1.10 without the best 2%, the blind
pick FAIL), ttt, rrr, ooo, uuu; **FAIL ddd** (2 of 4 blocks, -0.41 without the best 2%: stopped Nov 27 night) and hhh (37 copies,
R3 only; +16.1%, 3 of 4); yyy fails on all its coins (2 of 4 blocks) but copies its token coins only, and its rule search keeps
exactly that (SOL coins dropped), as the Nov 27 exit study did (+18.4%, 3 of 4).

## The Nov 28 screen (11:05 box time; run Nov 28 09:29-10:35 UTC; `out/screen1128_part1.txt`)

The candidates by the same rules as Nov 27 (the method test's winner and the consistency list, not tested before): 8x1q3VeN,
7ESujFzt, HTYho9io, CCDvgAh1, HLZ3wicH, 45JhwE8F, 6xJwQ5m9. **The Helius key ran out of credits during the run** ("max usage
reached"): the first two read cached histories, HTYho9io's coin paths failed half-way, the last four got no history.
`deep_job.sh` now runs with RPC_URL alone (the public node or Triton, slower); the four rerun that way.

- **PASS 7ESujFzt**: the standard exit +13.0% a copy on 45 (blocks -16.4 / +13.9 / +24.5 / +32.7, 3 of 4), +3.50 SOL at 1 SOL
  without the best 2%; the blind rolling pick PASS (+7.5% a copy on 21, 3 of 3); own +3.58 SOL over 13 days, up on 8. Its SOL
  coins carry it (+26.2% on 28; its token coins -8.8% on 17), and the rule search keeps all its coins (dropping the SOL coins
  -7.35 stakes; no rule beats live blind, 0 of 3). The exit search: B, one change, 180 s (+14.9% against +12.8%, 3 of 4, +3.5
  points without the best 2%). Unit 18, `rugsnipe-long-7es` (`zzz`): 0.25 SOL, tp 3x / 180 s / stall 240, daily stop 0.5,
  stopped at -1.0 SOL in all or if negative after 20 trades. Thin: 45 copies is about 3 a day, so 20 trades take about a week.
- **FAIL 8x1q3VeN**: +5.2% a copy on 100 but 2 of 4 blocks (-11.0 / +3.9 / -0.6 / +28.5), the blind pick FAIL, though it made
  +34.16 SOL itself over 8 days, up on all 8. The rule search's one change, its buys of 1.3+ SOL only, passes B: a name to retest
  with more days, not to run now.
- **FAIL HTYho9io**: it loses -236.71 SOL itself over 10 days, up on 1 (83 buys of 0.5+ SOL); no copy test needed.

## Days and hours (Nov 28; the owner: "not trade on Fridays, Saturdays, Sundays, or any day of the week?")

The deep test's copies of 11 of our wallets (1,756 over Nov 13-27, the standard exit, from the cand_*.npz grids), by UTC weekday
and 6-hour block, each split into the first and the second week: **every weekday and every block is positive in both weeks.**
Weekdays: Mon +8.9%, Tue +3.7%, Wed +10.6%, Thu +8.6%, Fri +3.6%, Sat +4.3%, Sun +17.3% a copy (the weeks: Fri +4.1 / +3.1, Sat
+1.6 / +7.0). Hours UTC: 00-06 +12.5%, 06-12 +2.8% (+3.1 / +2.5: the weakest, steady), 12-18 +11.3%, 18-24 +6.8%. No day or hours
lose; leaving any out would only give up copies that make money. Two weeks are two samples a weekday: recheck when the tape is longer.
