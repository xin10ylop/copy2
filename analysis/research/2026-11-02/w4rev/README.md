# Can we pick wallet 4's part-A launches ourselves? (w4rev, Nov 1-2, 2026)

**Question.** Wallet 4 (`H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg`) buys pump coins priced in another token, in the
create slot or the next, and holds them up to 30 min (2.5x / 0.7x / 30 min). Could we pick the same launches from what
the create shows, and buy them at launch ourselves instead of copying its buys?

**Answer.**
- **A pick rule exists, but it only partly separates its picks.** Wallet 4 buys 5.4% of the routable other-quote
  creates. Rule W (below), picked on Oct 19-22, catches 55% of its picks on Oct 23-26 at 24% precision, and 64% at 30%
  on Oct 28 - Nov 1.
- **Buying W's coins at launch is positive at 1 SOL with this study's costs:** Oct 23-26 +24.98 SOL (+19.24 without the
  best 2), Oct 28 - Nov 1 +16.71 (+7.83).
- **But the money is on the coins wallet 4 itself buys.** The coins W passes and wallet 4 skipped lose or are about
  zero in every period (−12.20, −3.36, −0.74).
- **It does not survive harder conditions:**
  - copy2's usual costs (0.0095 SOL a transaction and the 0.0155 SOL fill bias): −7.21 on Oct 23-26, −9.34 on Oct 28 - Nov 1;
  - a 0.1 SOL stake;
  - always landing a slot late: Oct 28 - Nov 1 +4.04 (−4.74 without the best 2).
- The narrower rule N (notrandom.fun launches only) looked best on Oct 23-26 but fails the fresh check without its
  best 2.
- **Verdict: not a strategy of its own.** The edge is wallet 4's own selection, which a create-time rule reproduces at
  24-30% precision out of sample.

Times are UTC. P1 = Oct 19-22 (where every rule was picked), P2 = Oct 23-26 (out of sample), P3 = Oct 28 00:00 -
Nov 1 21:30 (fresh). A launch pick = a buy by wallet 4 in the coin's create slot or the next (+0/+1).

## Run order

Scripts and data live in this folder; outputs go to `out/`. Every RPC call goes to Triton. The URL is read from the old
scratchpad's `month/.triton_url` by `../agents/scan/bin/crc.py`; it is never printed, and errors are redacted. No GMGN.

```
python3 -I s1_list.py              # pump mint-authority signatures Oct 19 00:00 - Oct 29 00:00   -> out/s1_sigs.json
python3 -I s1b_picks.py 8          # wallet 4's 3,053 other-quote buys tied to their creates      -> out/picks.json
python3 -I s1f_picks_routes.py     # their route class from the quote mint (routes.py)            -> out/picks_cls.json, out/s1f.out
python3 -I s1c_qc_list.py          # pump quote-control signatures, now back to Oct 19            -> out/qc_sigs.json
python3 -I s2_check.py 1500        # is the quote-control list the list of other-quote creates?   -> out/s2_check.json
python3 -I s2_qc_fetch.py 16 0.025 # all 115,147 quote-control creates of Oct 19-26, decoded      -> out/qc_creates_1792368000_1793059200.json
python3 -I s6_table.py             # feature table of the 15,629 routable creates, labelled       -> out/table.json, out/s6_table.out
python3 -I s6b_activity.py 12      # each coin's landed transactions in its first 60 s            -> out/act60.json
python3 -I s6c_prior_act.py        # the creator's earlier coins and how they did (into the table)-> out/s6c.out
python3 -I s7a_univar.py           # pick rate by single feature                                  -> out/s7a.out
python3 -I s7_rule.py pick 3 40    # P1 decision trees (also: pick 4 40, big 3 40; PRIORACT=1)   -> out/s7_*.out
python3 -I s7b_rules.py            # rules W, W1, N written out; 10% baseline                     -> out/rule_*.json, out/s7b.out
python3 -I s4_paths.py out/coins_picks.json 8 0.03   # launch tapes + 30-min paths (also coins_W, coins_base) -> out/tapes/
python3 -I s5_sim.py out/coins_picks.json 120 6      # our launch buys, gaps refined (also coins_W, coins_base) -> out/sim_*.json
python3 -I s5b_check.py 25         # sampled vs fully read paths on 25 picks                      -> out/s5b.out
python3 -I s6d_slot0.py            # create-slot bundle buys vs its picks (baseline tapes)       -> out/s6d.out
python3 -I s8_score.py out/sim_picks.json pick       # (and big; sim_W.json rule:W, rule:W&pick, rule:W&skip, rule:W1,
                                   #  rule:N...; sim_base.json all / pick / nonpick)              -> out/s8_*.out
python3 -I s8b_split.py out/sim_W.json W            # by day and by part (also N; sim_fresh.json WF, NF) -> out/s8b_*.out
python3 -I s2_qc_fetch.py 10 0.04 1793059200 1793574000   # quote-control creates Oct 27 - Nov 1 23:00
python3 -I s9b_w4_fresh.py 8       # wallet 4's buys Oct 28 - Nov 1 21:30 from its signatures     -> out/w4_fresh.json
python3 -I s9_fresh_table.py       # fresh feature table, labelled                                -> out/table_fresh.json, out/s9_table.out
python3 -I s9c_fresh_rules.py      # the same rules on it, unchanged                              -> out/rule_*F.json, out/coins_fresh.json, out/s9c.out
python3 -I s4_paths.py out/coins_fresh.json 10 0.025; python3 -I s5_sim.py out/coins_fresh.json 120 8
python3 -I s8c_fresh_score.py      # P3 scores                                                    -> out/s8c_fresh.out
python3 -I s8d_costs.py            # everything again at copy2's usual costs                      -> out/s8d_costs.out
python3 -I s1g_counts.py           # small counts quoted here (class totals, create-slot share, F0 - F1) -> out/s1g.out
```
Helpers: `lib.py` (the Triton client, the canonical-pool PDA), `tape.py` (time cursors, listings, TradeEvents),
`routes.py` (route class from the quote mint), `feat.py` (features), `s1b_crow.py` (the create decoder).

**Incident.** The disk filled at about 23:50 UTC on Nov 1 with this study's raw-response cache (the volume had 1.8 GB
free once it was gone). I deleted only that cache (`cache/`). `lib.py` caches nothing since then. Every output the full
disk had broken was redone: 1,071 tapes, the activity counts and the fresh fetch. The decoded rows in `out/` are the
record.

## 1. The universe

**All creates.** The pump mint authority (`TSLvdd1p...`, account #1 of create and create_v2) has 580,316 signatures
from Oct 19 00:00 to Oct 28 23:59 UTC, 480,267 of them landed. Of those, 378,945 landed creates fall on Oct 19-26.

| day | 10-19 | 10-20 | 10-21 | 10-22 | 10-23 | 10-24 | 10-25 | 10-26 | 10-27 | 10-28 |
|---|---|---|---|---|---|---|---|---|---|---|
| landed | 52,514 | 51,076 | 50,330 | 46,663 | 48,973 | 42,142 | 40,384 | 46,863 | 54,631 | 46,691 |

**The other-quote creates, in full, not a sample.** Every create_v2 with a token quote carries pump's quote-control
PDA (`6z6GDdfb2AjR9ZhJmAUQ5cipJCVxQvLJhB2H8mCwTFBP`). Its signature list has 248,789 signatures, 176,042 landed, from
Oct 19 00:00 to Nov 1 22:47. `s2_check.py` checked it against 1,500 random landed creates of Oct 19-26:

| sampled creates | in the quote-control list | not in it |
|---|---|---|
| SOL-quoted (1,039) | 0 | 1,039 |
| other-quote (456) | 445 | 11, all USDC (route class E) |
| no CreateEvent (5) | 0 | 5 |
| of the other-quote ones: route A 42, B 7, C 13 | all 62 | 0 |

So every routable create is in the list. All 115,147 landed quote-control signatures of Oct 19-26 were read: 114,104
creates and 1,043 other transactions. Each was classed by its quote mint with copy2's `route_q.py` rule:
- C: the quote is WBTC;
- A: the quote has a canonical PumpSwap pool against wSOL;
- B: the quote has a canonical PumpSwap pool against WBTC only;
- E: neither.

Pool existence was checked as of Nov 1. On wallet 4's own 598 big buys this class agrees with h9long's
`routable.json` on 598 of 598.

**Routable creates (A/B/C) and wallet 4's launch picks among them** (`s6_table.out`, `s7a.out`):

| day | routable creates | its launch picks | share | of which 1.45+ SOL | share |
|---|---|---|---|---|---|
| 10-19 | 2,108 | 98 | 4.6% | 36 | 1.7% |
| 10-20 | 1,893 | 78 | 4.1% | 34 | 1.8% |
| 10-21 | 2,578 | 101 | 3.9% | 38 | 1.5% |
| 10-22 | 1,661 | 111 | 6.7% | 48 | 2.9% |
| 10-23 | 1,347 | 95 | 7.1% | 45 | 3.3% |
| 10-24 | 1,581 | 162 | 10.2% | 37 | 2.3% |
| 10-25 | 2,792 | 129 | 4.6% | 59 | 2.1% |
| 10-26 | 1,669 | 66 | 4.0% | 20 | 1.2% |
| **Oct 19-26** | **15,629** (A 10,202, B 2,457, C 2,970; `s1g.out`) | **840** | **5.4%** | **317** | **2.0%** |
| P3 Oct 28 - Nov 1 21:30 | 5,487 | 385 | 7.0% | 68 | 1.2% |

**Selection is not trivial: it buys 5.4% of the routable launches, and its 1.45+ SOL buys (part A proper) are 2.0%.**
Its net on these picks: P1 +92.69 SOL (+49.32 on the 1.45+), P2 +60.87 (+49.30).

**Wallet 4's buys.** Its 3,053 other-quote buys of Oct 19 - Oct 27 00:40 (`s1b_picks.py`) come at these slots after
the create: +0 1,739, +1 1,289, +2 11, +3 6, +4 2, +5 4, +8 1, +10 1. Of them, 841 were routable launch buys:

| route | launch buys | of which 1.45+ | its net (under 1.45 / 1.45+) |
|---|---|---|---|
| A | 446 | 189 | +39.71 / +51.01 |
| B | 252 | 99 | +8.91 / +29.24 |
| C | 143 | 29 | +6.36 / +18.38 |

Their main quotes: `C5xph2yL` (B) 235, `NTRNDMqQ` (A) 148, WBTC (C) 143, `CSocnzcR` (A) 54 (`s1f.out`).

## 2. Decoding its picks

**Single features** (`s7a.out`: P1 / P2 pick rate, against 4.7% / 6.1% overall):

| feature | value | P1 | P2 |
|---|---|---|---|
| metadata host | `meta.notrandom.fun` | 114 of 192 (59.4%) | 96 of 180 (53.3%) |
| | `ipfs.io` (pump's own upload) | 6.0% | 6.6% |
| | `metadata.j7tracker.io` | 0.6% | 1.5% |
| creator fee | 0 bps | 0.8% | 1.7% |
| | 300 bps | 8.1% | 10.9% |
| signer's creates in the 24 h before | 0 | 250 of 1,960 (12.8%) | 218 of 1,805 (12.1%) |
| | 5 or more | 1.7% | 3.0% |
| top-level programs | pump + ATA + ComputeBudget | 16.0% | 20.0% |
| | launcher `6Vo324...` | 0 of 1,002 | 0 of 1,209 |
| dev buy (SOL-equivalent) | 0.5-1 | 14.0% | 10.0% |
| | under 0.001 | 1.6% | 3.4% |
| quote | `NTRNDMqQ` | 59.9% | 44.7% |
| | `C5xph2yL` | 12.0% | 10.8% |

Hour of day, symbol length, and whether the creator is the signer barely move it.

**The creator's earlier coins** (`s6c.out`):

| the signer's earlier routable coins | P1 pick rate | P2 pick rate |
|---|---|---|
| none | 9.9% | 11.5% |
| some, none with 20+ transactions in their first 60 s | 1.6% | 4.2% |
| some, one with 20+ in 60 s | 3.5% | 4.7% |

Adding these to the tree does not change it (`s7_pick3_prioract.out`).

**Create-slot bundles** (`s6d.out`, 10% baseline of 1,543 coins; wallet 4's own trade excluded): 3+ bundle buys after
the create in the create slot give a pick rate of 0.0-6.8%, and one buy gives 13.1% / 18.0%. So it skips heavily bundled
launches. One or two next-slot buys also go with its picks (17.6-20.0%), but wallet 4 lands in the create slot on
1,739 of its 3,028 launch buys (57.4%, `s1g.out`) and its followers trade right behind it, so a rule cannot use them.

**The rule, from a decision tree fit on P1 only** (`s7_pick3.out`; depth 3, leaves of 40+):

- **W** = host `meta.notrandom.fun`, OR (the signer made no other quote-control create in the 24 h before AND the
  creator fee is above 0). This is the union of the tree's leaves with a P1 pick rate of 10% or more.
- **W1** = host `meta.notrandom.fun` AND dev buy over 0.141 SOL-equivalent (the tree's two high-precision leaves).
- **N** = host `meta.notrandom.fun` alone (W's first branch). **N is not a clean out-of-sample pick**: it was chosen
  after the backtest of W by part, whose output also showed P2. P3 is its only clean test.

| rule | target | P1 passes | P1 precision | P1 recall | P2 passes | P2 precision | P2 recall | P3 passes | P3 precision | P3 recall |
|---|---|---|---|---|---|---|---|---|---|---|
| W | any pick | 1,072 | 27.0% | 74.5% | 1,022 | 24.4% | 55.1% | 828 | 29.8% | 64.2% |
| W | 1.45+ | | 10.8% | 74.4% | | 10.1% | 64.0% | | 5.2% | 63.2% |
| W1 | any pick | 118 | 75.4% | 22.9% | 90 | 53.3% | 10.6% | 59 | 79.7% | 12.2% |
| N | any pick | 192 | 59.4% | 29.4% | 180 | 53.3% | 21.2% | 189 | 45.5% | 22.3% |

The deeper trees and the 1.45+ target (`s7_pick4.out`, `s7_big3.out`) do no better out of sample. For example, the
depth-4 tree at a 20% leaf rate gives P2 precision 27.9% and recall 54.4%.

## 3. Buying at launch ourselves (`s4_paths.py`, `s5_sim.py`, `s8_score.py`)

**The model:**
- **Path.** The coin's own pump TradeEvents, 30 min from the create. Every transaction of the create slot and the next
  is read. After them, all of them if there are 100 or fewer; otherwise the first 30, 50 evenly spaced, and the last
  one before 1800 s. Then every gap where an exit fires (or a gap whose ends come near a level) is read, up to 120
  extra reads a coin.
- **Accuracy check.** On 25 picks with 120-400 transactions, the sampled-and-refined result equals the fully read one
  within 0.07 SOL in total, with a different exit on 1 of 25 (`s5b.out`).
- **Fill.** After the last trade of the create slot (F0) or of the next slot (F1). "mix" = each coin's own draw,
  F = hash(mint) mod 2. The coin's create state counts as a trade when there is no dev buy.
- **Our buy.** Our stake is converted at pump's own quote price (30 SOL / initial virtual quote) times the checked
  factor (WBTC 1.130, pump-coin quotes 0.892), less 0.30% for the extra hop (routes A and B), then 1.25% curve fee.
- **The path after us.** Each later state is shifted by our quote ("cautious" model).
- **Exits**, on the price our buy left:
  - its own: 2.5x / 0.7x / 30 min;
  - ours: 2.0x / 0.8x / 30 min;
  - a take profit sells on the crossing trade's state, 1% under;
  - a stop sells on the crossing state.
- **Costs.** The sale pays 1.25% and the hop back; 0.003 SOL fixed a round trip.
- 3 coins failed with a division by zero (missing initial virtual quote) and are left out (`s1g.out`).

Tables: total SOL, and in brackets the total without the period's best 2 trades. Full tables, with the medians, win
counts and take-profit shares, are in `out/s8_*.out`.

**3a. Wallet 4's own launch picks, bought by us** (the imitation ceiling; `s8_picks.out`, `s8_big.out`):

| set | config | P1 n | P1 | P2 n | P2 |
|---|---|---|---|---|---|
| all picks | ours 1 SOL, mix | 387 | +34.09 (+31.33) | 452 | +16.22 (+10.47) |
| | ours 1 SOL, F0 | | +45.92 (+43.16) | | +33.11 (+27.36) |
| | ours 1 SOL, F1 | | +16.92 (+14.14) | | +4.22 (−0.95) |
| | its 1 SOL, mix | | +28.48 (+24.47) | | +17.53 (+11.78) |
| | ours 0.1 SOL, mix | | +2.48 (+2.20) | | +0.91 (+0.29) |
| 1.45+ picks | ours 1 SOL, mix | 156 | +19.77 (+17.00) | 161 | +17.58 (+12.46) |
| | its 1 SOL, mix | | +15.76 (+12.38) | | +20.18 (+14.57) |

**3b. Rule W, and its picked and skipped coins** (`s8_W.out`):

| set | config | P1 n | P1 | P2 n | P2 |
|---|---|---|---|---|---|
| **W, all** | ours 1 SOL, mix | 1,070 | +15.26 (+2.83) | 1,022 | **+24.98 (+19.24)** |
| | its 1 SOL, mix | | +9.01 (−4.17) | | +34.38 (+27.65) |
| | ours 1 SOL, F0 | | +29.18 (+16.75) | | +37.17 (+31.42) |
| | ours 1 SOL, F1 | | −0.10 (−12.52) | | +15.01 (+9.82) |
| | ours 0.1 SOL, mix | | −1.32 (−2.73) | | +0.21 (−0.41) |
| | its 0.1 SOL, mix | | −1.21 (−2.70) | | +1.12 (+0.39) |
| W and wallet 4 bought | ours 1 SOL, mix | 288 | +27.46 (+24.93) | 249 | +28.35 (+22.60) |
| **W and wallet 4 skipped** | ours 1 SOL, mix | 782 | **−12.20 (−24.63)** | 773 | **−3.36 (−5.64)** |
| | its 1 SOL, mix | | −14.43 (−27.20) | | +2.97 (−1.62) |

W by day (ours 1 SOL, mix; all / wallet 4 bought / skipped; `s8b_W.out`):

| day | all | bought | skipped |
|---|---|---|---|
| 10-19 | +11.55 | +7.29 | +4.26 |
| 10-20 | +1.29 | +7.92 | −6.63 |
| 10-21 | −6.84 | +4.09 | −10.93 |
| 10-22 | +9.26 | +8.16 | +1.10 |
| 10-23 | +4.59 | +4.68 | −0.09 |
| 10-24 | +0.17 | +2.25 | −2.07 |
| 10-25 | +20.29 | +20.00 | +0.29 |
| 10-26 | −0.07 | +1.42 | −1.49 |

W by part: the notrandom.fun branch made P1 +12.88 on 191 and P2 +25.55 on 180; the other branch (first create in
24 h, fee above 0) made P1 +2.37 on 879 and P2 −0.57 on 842.

**3c. W1 and N** (`s8_W.out`, `s8_N.out`, `s8b_N.out`):

| set | config | P1 n | P1 | P2 n | P2 |
|---|---|---|---|---|---|
| W1 | ours 1 SOL, mix | 118 | +3.99 (+1.78) | 90 | +12.38 (+7.27) |
| N | ours 1 SOL, mix | 191 | +12.88 (+10.59) | 180 | +25.55 (+20.42) |
| N | its 1 SOL, mix | | +12.51 (+9.41) | | +30.73 (+25.17) |
| N | ours 1 SOL, F1 | | +6.80 (+4.51) | | +22.81 (+17.64) |
| N | ours 0.1 SOL, mix | | +0.78 (+0.55) | | +2.20 (+1.64) |
| N, wallet 4 skipped | ours 1 SOL, mix | 77 | +4.06 (+1.94) | 84 | +7.30 (+5.30) |

N was positive on all 8 days, Oct 19-26: +1.80, +1.06, +4.84, +5.18, +1.83, +4.81, +15.85, +3.06.

**3d. The baseline: a seeded 10% of every routable launch** (`s8_base.out`):

| set | config | P1 n | P1 | P2 n | P2 |
|---|---|---|---|---|---|
| all | ours 1 SOL, mix | 800 | −31.59 (−33.97) | 743 | −14.28 (−17.12) |
| all | its 1 SOL, mix | | −46.05 (−51.52) | | −24.18 (−28.85) |
| all | ours 0.1 SOL, mix | | −5.16 (−5.41) | | −3.37 (−3.67) |
| not wallet 4's | ours 1 SOL, mix | 768 | −36.81 (−39.18) | 699 | −14.82 (−17.10) |

**3e. At copy2's usual costs** (0.0095 SOL a transaction × 2 + 0.0155 SOL fill bias = 0.0315 SOL a trade more;
`s8d_costs.out`; ours 1 SOL, mix):

| set | P1 | P2 | P3 |
|---|---|---|---|
| W | −18.45 (−30.81) | −7.21 (−12.89) | −9.34 (−18.16) |
| W1 | +0.27 (−1.87) | +9.55 (+4.49) | −2.72 (−4.57) |
| N | +6.87 (+4.64) | +19.88 (+14.81) | +0.50 (−7.69) |
| wallet 4's picks | +21.90 (+19.20) | +1.98 (−3.71) | |
| baseline | −56.79 (−59.11) | −37.68 (−40.47) | −36.00 (−38.01) |

**Step-3 verdict (the bar: P2 positive, and still positive without its best 2).**
- W passes at 1 SOL with the study's costs, under both exit sets.
- It fails at 0.1 SOL with ours (+0.21, −0.41 without the best 2) and fails at copy2's costs.
- Its P2 profit comes from the coins wallet 4 bought; the coins it skipped lose.
- N passes at both stakes with both cost models, but see §4.

## 4. Fresh check, Oct 28 00:00 - Nov 1 21:30 (P3)

The same rules, unchanged, on the 5,487 routable creates of P3. Wallet 4's launch picks there came from its own
signatures: 10,815 landed transactions, 2,413 coins bought (`s9b_w4_fresh.py`).
- Its routable launch picks: 385, of which 68 at 1.45+ SOL. By day 75, 45, 73, 94, 98 (1.45+: 18, 10, 7, 17, 16).
- Its 1.45+ SOL routable launch buys are down to 7-18 a day (Oct 19-26: 20-59).

| set | config | n | P3 | wallet 4 bought: n, total | skipped: n, total |
|---|---|---|---|---|---|
| **W** | ours 1 SOL, mix | 827 | **+16.71 (+7.83)** | 246, +17.45 | 581, −0.74 |
| | its 1 SOL, mix | | +33.41 (+20.82) | 246, +26.16 | 581, +7.25 |
| | ours 1 SOL, F0 | | +30.13 (+20.90) | | |
| | ours 1 SOL, F1 | | +4.04 (−4.74) | | |
| | ours 0.1 SOL, mix | | −0.37 (−1.36) | | |
| W1 | ours 1 SOL, mix | 59 | −0.86 (−2.77) | | |
| **N** | ours 1 SOL, mix | 189 | **+6.45 (−1.80)** | 86, +2.51 | 103, +3.95 |
| | its 1 SOL, mix | | +6.28 (−2.42) | | |
| | ours 1 SOL, F0 | | +11.79 (+3.13) | | |
| | ours 1 SOL, F1 | | +1.59 (−6.92) | | |
| baseline (10%, 581) | ours 1 SOL, mix | 581 | −17.70 (−19.77) | 49, +0.97 | 532, −18.67 |

W by day in P3 (ours 1 SOL, mix): +3.48, +0.78, +4.81, +5.05, +2.59. Its two branches swapped: notrandom.fun +6.45 on
189, the other branch +10.26 on 638 (`s8b_WF.out`, `s8c_fresh.out`).

## 5. Verdict

1. **Pick rule: yes, partly.** A three-feature create-time rule (W) passes 13.0-15.1% of the routable launches
   (`s1g.out`). It keeps precision at 24-30% and recall at 55-64% out of sample (P2, P3), against base rates of
   6.1% and 7.0%. Wallet 4 favours
   first-time creators who set a creator fee, pump's own metadata upload, and the notrandom.fun launcher. It avoids
   serial launchers, zero-fee launches, j7tracker / `6Vo324` launchers and heavily bundled creates. Most of its
   choice stays unexplained.
2. **Profit: thin, and borrowed.** W at 1 SOL clears the bar in P2 (+24.98, +19.24 without the best 2) and P3 (+16.71,
   +7.83) with the light costs set for this study. But:
   - the coins it passes that wallet 4 skipped make −12.20, −3.36 and −0.74 (P1, P2, P3);
   - it turns negative at copy2's usual costs in all three periods;
   - at 0.1 SOL it fails: P2 +0.21 (−0.41 without the best 2), P3 −0.37;
   - landing a slot late every time gives P1 −0.10, P2 +15.01 (+9.82), P3 +4.04 (−4.74 without the best 2);
   - all its profit sits on the coins wallet 4 buys, where wallet 4's own 1-1.5 SOL buy and the bots that follow it
     lift the price after a create-slot fill. On W, F0 against F1 is +29.18 against −0.10 (P1), +37.17 against
     +15.01 (P2) and +30.13 against +4.04 (P3) (`s1g.out`).
3. **N** (notrandom.fun launches only) was the best on P2 and positive on all 8 days. On the fresh P3 it is +6.45 but
   −1.80 without its best 2, so it fails. It was also not a clean pick.
4. **Plain answer:** we cannot replace the copy with our own launch picking. The rule's profit comes from the coins
   wallet 4 also buys. The coins it passes that wallet 4 skipped (precision is only 24-30%) make no money. Without
   wallet 4 behind those coins there is no evidence of an edge.

## What it would take to go further

- A rule with a much higher precision. The creator's other history (SOL creates, funding, social links in the
  metadata JSON, which needs an HTTP fetch of the URI) is not in this table.
- Or a fill test on wallet 4's own picks at our live latency, which is the long copy's question again.
- The 30-min paths are sampled and refined, not fully read: totals agree within 0.07 SOL on 25 checked coins.
- Pool existence is as of Nov 1.
- The quote's SOL price is pump's own setting times one factor per class.
