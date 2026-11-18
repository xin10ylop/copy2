# The bundle wait, pre-registered Nov 18 02:18 UTC, before any money of it is computed

`out/b0_coins.txt` (counts only): the launch bundle's first sale comes a median 5-6 s after the launch; 60% / 38% of
coins (before / after Nov 17 13:49 UTC) have no bundle sale by 5 s, 17% / 13% by 10 s.

**The trade:** on a ladder coin (2+ bundle wallets at the ladder sizes in the create slot), wait X s after the launch;
if no bundle wallet has sold by then, buy 0.5 SOL at the first trade after launch + X s (any price), else skip.
Exit at the first of: a bundle wallet's sale (sell at the next trade), our entry x tp, cap s after our entry, the curve
completing. 0.0345 SOL a round trip; the sale valued on the curve with our buy's weight (as c2/k3).
**Grid:** X in {5, 10, 20}; tp in {1.2, 1.5, 2, none}; cap in {60, 120, 300}.
**Pick** the best mean a trade on the coins before Nov 17 13:49 UTC (458 coins; the week the ladder was found, never
used to pick this rule); **score once** on the 108 coins after it. **Pass:** positive; positive without the best 2%;
bootstrap P(mean > 0) 95%+; at least 10 trades (the after-set is small: a pass is a lead for a forward check, not a go).

## RESULT (Nov 18 ~02:25 UTC): FAIL

`out/b1_money.txt`. Before the cutoff every one of the 36 settings loses about 10% a trade (77 coins at X=10, 276 at
X=5): the bundle starts selling right after we buy. Picked X=20 tp=2 cap=300 → after: 7 trades, +5.8%, negative
without the best 2%, P(mean > 0) 66.4%. The "after" positives at tp=none (+15% / +40%) are one coin. The ladder is closed.
