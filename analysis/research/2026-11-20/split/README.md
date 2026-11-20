# The split, backtested: leg 1 only, leg 2 only, both (Nov 20)

The owner: "on the backtest, check pnl if we run both strategies, if we run first only or second only, all vs each other".

`s1_split.py` (run: `python3 -I s1_split.py SP H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg > out/s1_split.txt`, SP = the
scratchpad holding `allq/ cq/ since_stop/ newq/`). Wallet 4's 1,029 buys of 1.3+ SOL, Oct 21 - Nov 13 (m15f's corpus,
before the 4 days the dip was picked on). Leg 1 = the live copy (`hunt_lib.model`: next slot, 1.5x price limit, tp 4, 600 s,
sell pressure 5/60, stall 180, its early sale); leg 2 = the live dip (10% within 60 s, tp 1.5x our fill, 900 s, float-paid
only). 0.0345 SOL a round trip. Not modelled: max_open, the daily stop.

| scenario | trades | SOL | without best 2% | worst day | days up |
|---|---|---|---|---|---|
| leg 1 only, 1 SOL | 1,029 | +123.23 (+107.28 at 0.050 a trip) | +63.83 (+48.21) | -5.31 | 21 / 25 |
| leg 2 only, 1 SOL | 212 | +37.85 (+34.56) | +32.78 (+29.56) | -1.27 | 18 / 22 |
| both, 0.5 + 0.5 (live) | 1,241 | +62.89 | +27.35 | -3.62 | 20 / 25 |
| leg 1 only, 0.5 SOL | 1,029 | +47.12 | +16.82 | -3.35 | 20 / 25 |
| leg 2 only, 0.5 SOL | 212 | +15.76 | +13.22 | -0.74 | 18 / 22 |

- At 0.5 SOL a trade, float-paid: leg 1 +13.5% a trade (730), leg 2 +14.9% (212). wSOL-paid leg 1: -1.3% a trade (299).
- Leg 2 fires on 212 of the 1,029 buys (21%): alone, the stake sits idle on the rest.
- On the 212 buys where both trade: leg 1 +12.12, leg 2 +15.76 SOL at 0.5; correlation +0.48.
- Caveat: leg 1's exit was picked on data that includes this period (in sample); leg 2's rule was picked on Nov 14-18
  (out of sample here). Leg 1 loses half its total without its best 2% of trades; leg 2 loses about a seventh.
