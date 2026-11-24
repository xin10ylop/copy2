# Live check of the six new units against the model (Nov 24 evening)

The owner, after `pnl` (wallet 4 +2.46 SOL over 50 trades; CqCAzte8 -0.15 over 50, CgyPomTG -0.01 over 11, 3XeFcZKS
-0.11 over 3, 6LwMLkCe -0.26 over 1, 6nNzEg86 none, GqWfqfG6 -0.33 over 4): "none of the wallets are making money,
double check your pick".

Run: each wallet's trades of Nov 21-24 fetched anew (`../../2026-11-19/candidates/c1_fetch.py`, 3 days, Helius), the
copies built with `NOSTOP=1 ../coin_filters/f1_rows.py` (99 coin paths by RPC), then `python3 -I l1_live_vs_model.py`
(`out/l1.txt`).

**Answer: the bots copy as the model says they should; the days since they started were poor for these copies.**
- The model on the same buys since each unit started gives what live gives: CqCAzte8 +0.18 SOL (66 copies) against
  -0.15 live (50), CgyPomTG -0.09 / -0.01, 3XeFcZKS -0.10 / -0.11, GqWfqfG6 -0.50 / -0.33. 6LwMLkCe's model -0.62 and
  6nNzEg86's -0.33 are on buys the units missed (the price fault fixed today) or skipped.
- By chance alone, with the test's copies: CqCAzte8's 50 at or under 0 happens 5% of the time; the others' 1-11 trades
  34-69%. CqCAzte8 is the one real warning: it lost 14.67 SOL itself on Nov 23 and 2.06 on Nov 24; its copies +1.2% a copy
  since its unit started against +13.4% in the test.
- By day (part 2 of `out/l1.txt`), the six wallets' copies together: every 3-day window since Nov 10 positive (+7.5 to
  +16.3% a copy, +3.0 to +12.3% without the best 2%); Nov 24 (35 copies) -8%, the worst day; Nov 13 was -1%. The units
  started at the end of the best run (Nov 20-23, +16 to +25% a day) and ran into the worst day.

**www trade by trade (`l2_www_match.py`, `out/l2_www.txt`; the box's closed book pasted, 51 trades Nov 22 16:39 - Nov 24
17:30 UTC).** The first part's window started at 08:00 UTC; the unit's first trade was 16:39.
- The 49 trades the model also has: **live +0.190 SOL, model -0.415**; live is better on 37 of 49 (+0.012 SOL a trade,
  median +0.009): the model's costs and landing are cautious. Token coins 6 (live -0.437), SOL coins 43 (live +0.628).
- 2 live trades after the fetch's end (Nov 24 17:14 and 17:30 UTC): -0.308.
- 17 first buys of 0.5+ SOL in the live window that the unit did not take, 16 of them token coins: +0.592 SOL in the model
  (AQ11zGbA alone +0.889; the others +0.36 to -0.32). Why each was skipped is in the unit's journal (asked of the owner).
