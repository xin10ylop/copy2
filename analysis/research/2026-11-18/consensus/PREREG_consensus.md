# Consensus of pickers: the money test, pre-registered Nov 18 ~02:30 UTC, before any price path is read

`out/k2_clean.txt`: on coins outside the 48 h the pickers were chosen on, graduation by the number of distinct pickers
buying within 300 s: before (Nov 3-14) 4.7% / 9.4% / 13.0% / 17.9% / 35.5% for 1 / 2-3 / 4-5 / 6-8 / 9+; after (Nov 17
on) 3.7% / 4.8% / 10.7% / 15.8% / 31.8%. Base 1.83%.

**The trade:** trigger on the k-th distinct picker's first buy within 300 s of the first; enter at the first curve trade
in a later slot, 0.5 SOL, any price; SOL curves only. Exits, all from OUR entry price: sell at the next trade; take profit
x1.2 / x1.5 / x2 / x3 with a time cap of 60 / 300 / 600 s; the cap alone. A completed curve sells at its last curve
trade. 0.0345 SOL a round trip.
**Picked on the coins of Nov 3-14** (k in {4, 6, 9} and the exit), **scored once on Nov 17 01:07 on.**
**Pass:** positive; positive without the best 2%; bootstrap P(mean > 0) 95%+; 30+ trades.
Sample (fetch cost): Nov 3-14, all coins with 6+ pickers and a random 600 (seed 7) of those with 4-5; Nov 17 on, all 4+.

## RESULT (Nov 18, ~02:30 UTC): FAIL (partial run, the owner's call to use what was fetched)

`out/k3_money_partial.txt`: about half the 1,388 coins had a path (the rest unfetched; true in-slot order). Picked on
Nov 3-14: k=9, take profit 1.2, cap 600 s (30 trades, +7.1%) → **Nov 17 on: 16 trades, −11.9%, P(mean > 0) 10.7%**.
Every k=4 and k=6 setting loses after Nov 17 (−1.9% to −18.5% a trade, 95-291 trades); before, only k=4 with a 300 s
hold is positive (+2.7%), and negative without the best 2%. More pickers raise the graduation rate, but by the 4th
picker the price has already moved. The fetch was stopped.
