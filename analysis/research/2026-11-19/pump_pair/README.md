# One pump.fun trader with two wallets: 8zqsUMty + FDhoU1DE (Nov 19)

Found by `2026-11-17/wallet_hunt/market/m12_clusters.py` (the two buy the same coins within 1 slot): on the 4 days of
Nov 14-18 our copy +19.6% a copy (30 copies), up on the blind days.

- `p1_fetch.py`: both wallets' transactions of the last 30 days (Triton): 2,957 + 3,056, the oldest Nov 10.
- `p2_own.py` (`out/p2_own.txt`): **its own result, as one trader: +47.53 SOL on 422 coins, +24.41 without its best 5,
  up 8 of 10 days** (Nov 10 −3.22, Nov 16 −2.53; best days +15.27, +13.58, +12.64). Both wallets bought 393 of the 422
  coins. Half are SOL coins (213), the rest TTWO 87, PUMP 31, others. Median 1.73 SOL a coin. 1,130 trades in quote
  tokens without a price in the prices file are left out.
- `p3_copy.py` (e14_live_vs_model with its SOL coins included): OUR copy of it, coin by coin, wallet 4's live exits.
- **`p3_copy.py` result (`out/p3_copy_8zqs.txt`): OUR copy of it, Nov 10-19, wallet 4's live exits (0.5 SOL, tp 4, 600 s,
  sell pressure 5/60, stall 180, its early sale), landing 4 / 8 trades or the next slot: 263 copies, −7.92 SOL (−6.0% a
  copy), −14.40 without the best 2%, up on 3 of 10 days** (SOL coins −9.5% a copy on 132, token coins −2.6% on 131). The
  trader made +47.53 SOL itself over the same days. Like m7's daily winners: its edge does not survive the copy.
