# What the winners have in common, and what sets them apart from the losers (wallet 4, Nov 16)

The owner: "analyze all the winning coins, and see what they have different than the losers, what they have in common".
The 1,238 buys of `../signals/` (seven kinds, 1.3+ SOL, Oct 21 - Nov 15), each copied with the live setup, 0.5 SOL, every
copy, mean of three landings; 1,163 copied (75 refused at landing 4). A trait counts only if its groups rank the same
way in all three blocks and the gap between its best and worst group stays when the days are drawn again.

    python3 -I winners.py CQ ALL TABSCAN W4SCAN > out/winners.txt      # TABSCAN = tab2/scan_all.out, W4SCAN = allq/scan.out

## The shape of it

| group | copies | net | a copy |
|---|---|---|---|
| took profit at 4x | 51 (4.4%) | +60.56 SOL | +237.5% |
| other winners | 343 (29.5%) | +73.39 | +42.8% |
| small losses (to −20%) | 549 (47.2%) | −28.31 | −10.3% |
| big losses (over −20%) | 220 (18.9%) | −35.58 | −32.3% |

All +70.05 SOL; **the best 5% of the copies (58) make +72.39**, as much as everything.

## Known when we buy: three traits hold, all weak

| trait | best group | worst group | holds? |
|---|---|---|---|
| **the coin's size** (its curve's quote reserve in SOL) | 49.9+ SOL: +22.8% a copy, 44% won | under 31.6 SOL: +1.1%, 23% won (+1.1 / +8.5 / +15.8 / +22.8 by quarter) | yes |
| **the route** | 1 hop (bought with a float straight from the curve): +19.3% | 2 hops: +5.9% | yes |
| **its pace** | 0-1 copyable buys in the hour before: +16.0% | 5-12: +7.6% (and under 6 minutes since its last buy: +8.3%) | yes |
| its bet size | 1.77+ SOL: +22.6% | 1.46-1.5 SOL: +2.0% | no (block A the other way) |
| paid with | SPCX +23.0%, HYPE +21.7%, DJT +17.8%, PUMP +17.5%, TTWO +15.2%, WBTC +11.0% | SOL +3.7% | no (the order changes by block) |
| fee tier | 317-395 bps: +18.5% | 145-300: +8.8% (1-130: +10.9%) | no |
| our price against its, the hour, the weekday, its last 5 copies, the creator's earlier coins | | | no |
| TAB16RxX bought the coin in the same slot | +10.8% (157 copies) | did not: +11.7% | no difference |

Winners are more often coins that already had money in them, bought straight from a float, at a moment when wallet 4
was not buying one coin after another. None of the weak groups loses: the smallest quarter still makes +1.65 SOL.

## The first 30 seconds: here they separate

| in the first 30 s after its buy | copies | won | a copy | net |
|---|---|---|---|---|
| the price 17%+ above ours | 290 | 76% | +60.0% | +87.04 |
| the price under ours by 2%+ | 291 | 14% | −15.9% | −23.13 |
| 16+ more buys than sells | 284 | 65% | +50.6% | +71.86 |
| no more buys than sells | 480 | 12% | −8.2% | −19.60 |
| 53+ trades by others | 283 | 56% | +42.4% | +59.97 |
| 1 trade or none | 312 | 12% | −3.7% | −5.83 |

All three hold in every block. **A winner is busy, bought and up within half a minute; a loser is a coin nobody else
touched.**

## Can it be used? No (`out/winners.txt`, the end; the bot's run against the live setup, +75.29)

- **At the buy, skipping the weak group:** coins under 31.6 SOL of reserve −4.21; the smaller half −17.21; 5+ buys in
  the hour before −12.30; under 6 minutes since its last buy −13.69; the 2-hop routes −22.09; the SOL-paid coins −7.72.
  The weak groups make less, not nothing, and they hold some of the 51 take profits.
- **A checkpoint 30 / 45 / 60 s after its buy,** out if the price is under 0.9-1.1x ours, if buys minus sells is 0 or
  less, or if nobody else traded: 21 settings, −0.66 to −20.32. The coins that look dead at 30 s lose little when kept
  (−3.7% a copy for the untouched ones: there is nobody to sell to at a better price) and one in a hundred of them still
  goes to 4x.

**So:** which copy will win cannot be told when we buy; half a minute later it mostly can, and by then the live exits
are already doing what can be done with it (out behind its early sale, out on a minute of net selling). The profit is
a few big runs among many small losses, and every way of avoiding the losses also drops some of the runs.
