# The coin at its buy as a filter, on the six new wallets (Nov 24)

The owner: "have you tried to analyze holders, bonding curve progress, market cap, top 10 holders ...?" For wallet 4 this
was done on Nov 15-16 (`../../2026-11-15/skip_filters/`: 427 rules, among them curve progress and market cap, only the fee
rule held and it was removed; `../../2026-11-16/holders/`: 33 holder rules, all lose). Not for the six wallets added since.

**Answer: no measure of the coin at its buy separates their losing copies from their winners. Every group of every measure
makes money, the rule picked on the first half of the days loses 32.6 SOL on the second half, and luck alone does as well
92% of the time. No filter.**

## Run

```
SP=<scratchpad>; mkdir -p $SP/cf/out; cd $SP/cf      # hist_<W8> links to each wallet's 14-day history (Nov 9-24)
LK=$SP/lk COST=0.0064 python3 -I f1_rows.py $SP/cf WALLET out/<W8>.json     # each wallet; the coin paths are cached
python3 -I f2_filters.py out > out/f2.txt
```
`f1_rows.py`: w3_robust.py's copies (its first buys of 0.5+ SOL, our copy at the end of the slot after its buy, 1 SOL, 0.0064
SOL a round trip) with what the bot knows when its buy lands, from its own trade event and the trades in its slot before
it: curve progress, market cap in SOL, fee tier, its buy in SOL, its buy over the curve's quote, buyers in its slot before
it. No Helius credits (3 paths fetched by RPC). `f2_filters.py`: each unit's own coins and live exit (CqCAzte8 all coins,
SOL coins tp 2x / 120 s; CgyPomTG, GqWfqfG6 all coins; 3XeFcZKS, 6LwMLkCe, 6nNzEg86 token coins; tp 3x / 420 s / stall 240),
each wallet's copies cut in 4 time blocks. 921 copies, +13.3% a copy, +122.46 SOL at 1 SOL.

## Results (`out/f2.txt`)

**1. Each measure in 5 equal groups**, % a copy, wallets where the group is positive:

| Measure | lowest fifth | 2 | 3 | 4 | highest fifth |
|---|---|---|---|---|---|
| curve progress (cuts 0.19 / 0.36 / 0.51 / 0.67) | +10.7% 6/6 | +21.0% 6/6 | +12.6% 6/6 | +8.8% 4/4 | +13.5% 3/4 |
| market cap, SOL (cuts 50 / 69 / 92 / 136) | +11.0% 5/6 | +16.7% 6/6 | +19.5% 5/5 | +1.3% 3/5 | +17.9% 4/4 |
| its buy, SOL (cuts 0.73 / 0.98 / 1.58 / 2.04) | +21.9% | +9.7% | +9.8% | +9.5% | +15.6% |
| its buy / curve quote | +15.5% | +20.5% | +8.0% | +9.6% | +12.9% |

Fee tier: under 125 bps +53.3% (61 copies, 5 of 5 wallets), 125 bps +9.9% (596), 195+ bps +11.7% (264): the low-fee coins
are the best here, the opposite of wallet 4. Buyers in its slot before it: none on 670 (+12.5%), some on 251 (+15.4%).
Every group is positive; a skip throws profit away.

**2. 48 skip rules** (each measure, skip its lowest or highest 10-40%), picked on blocks 1-2 of every wallet, scored once
on blocks 3-4: the pick, skip the lowest 30% of curve progress (+3.13 SOL seen), **loses 32.64 SOL blind** (the skipped
copies made +28.4% a copy) and loses on 6 of 6 wallets. 1 rule of 48 gains blind (+0.24 SOL, skip the highest 10% fee
tier); none gains both seen and blind.

**3. Luck:** the same pick on shuffled measures: blind median -13.76 SOL; chance beats the real pick 92% of the time.

## Not tested

- **Holders and top 10 holders at its buy.** The cached paths start at its buy; holders need the coin's trades from its
  launch. The box's tape has them since Nov 21 13:59 UTC (no credits); fetching them for 921 coins would cost a large share
  of the Helius key. Given part 1 (every group of every measure positive), it is unlikely to change the answer; worth a
  look on the tape once it holds a week of these wallets' buys.
- The measures as a choice of exit (rather than a skip), and wallet 4 (done Nov 15-16).
