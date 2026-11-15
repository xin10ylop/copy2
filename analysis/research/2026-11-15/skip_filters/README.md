# Skipping losing copies without skipping the winners (Nov 15): two studies, one brief

The owner asked for a deep study and for a second researcher (an Opus 5.5 agent) to do the same from the same brief
(`PROMPT.md`), each alone: `fable/` (the session's own) and `opus/` (the agent's). Each folder has its README, scripts
and outputs.

**They agree on the one rule worth anything:** skip a coin whose fee tier (protocol + creator fee in wallet 4's own
buy event) is under 125 basis points. These are coins priced in another coin whose creator set a fee of 1% or less
instead of the usual 3%: 98 of the 781 buys of Oct 21 - Nov 14 (the fees seen: 30 and 100 bps for 85 of them).

| | `fable` | `opus` |
|---|---|---|
| The rule | fee tier <= 100 bps (96 buys) | fee tier < 125 bps (98 buys) |
| The bot's run, 0.5 SOL, 23.5 days | +41.00 SOL against +36.23 | +41.18 against +36.23 |
| Blocks A / B / C | +10.45 / +20.26 / +10.30 (against +8.79 / +19.43 / +8.02) | +10.48 / +20.26 / +10.44 |
| Take profits lost (of 66) | 2.7, 65.3 kept through freed slots | 2.7 lost, 2.0 new |
| Losing days of 23, worst day, deepest fall | 3.3, −0.49, −2.21 (against 5.3, −1.31, −2.86) | 1, −0.13, −2.20 |
| Days drawn again | ahead in 98.8% | ahead in 99.1% |
| Guard against luck | 4% of shuffles find as much among 66,430 rules | 1 of 200 shuffles among 150 filters |
| Real trades it would have skipped | 8, all losers, −2.1515 SOL | 9, all losers, −2.26 SOL |
| Rules tried | 66,430 entry rules, 57 bail-outs | 427 (150 entry filters, 145 second filters, 36 fitted models, 81 bail-outs) |
| Anything else that holds | no | no |

`opus` adds a reason: the low-fee coins draw fewer traders in their first minute (10 against 20) and run less (3x
reached by 4.1% against 13.5%); wallet 4 itself does worse on them.

**Where they differ:** `fable` also ran the rule on the buys after the data ended (Nov 14 17:39 - Nov 15 12:54
Beirut; `fable/out/fresh_check.txt`): **10 low-fee copies, +3.91 SOL in the model, two of them big wins** (3vhbd6FN,
Bip1Z2Qc). The rule would have skipped both. With them the low-fee copies stand at 105 copies, −0.96 SOL (−1.8% a
copy) against +11.3% for the rest: the weak group, no longer a losing one. `opus` did not have that check.

**Decision (Nov 15): built, off.** `min_fee_bps` in `long.toml` (0 = off; `docs/20-long-copy.md` §3), and each buy
line now ends with `fee N bps`, so the low-fee copies can be counted as they come. To be looked at again after about
50 more of them. Neither study found an early bail-out worth having.
