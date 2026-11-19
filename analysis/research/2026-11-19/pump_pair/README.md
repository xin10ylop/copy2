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
- **`p4_exits.py` (`out/p4_exits.txt`): the exit engineered.** 14,580 exits (take profit 1.5x-none x hold 10-600 s x sell
  pressure x stall x its sale never / early / always) x 5 entry filters (all, SOL coins, token coins, its 1+ SOL, its 2+
  SOL), picked on Nov 10-14 and scored on Nov 15-19 and the reverse: **0 exits positive on both halves and without the
  best 2%, under every filter.** Even the best exit in hindsight loses on both halves (all coins: −2.99 / −2.91 SOL). Not a
  wallet to copy.
- **`p5_where.py` (`out/p5_where.txt`), where the money goes:** our entry is a median 1.03x its price (90%: 1.12x), so
  landing late is not the problem. The CEILING (each copy sold at its best moment, hindsight) is +68.68 SOL (+52.4% a
  copy, both halves), but the best fixed exit is −4.73 SOL, and −0.79 even at its own price. Premium limits 1.05-1.5x:
  no exit positive on the other half.
- **`p6_mirror.py` / `p6b_before.py`: mirroring its sales** (selling the fraction of our tokens it sells, 1-3 blocks
  after each of its sales; a median 2 sales a coin, 90% 8): −8.58 to −9.15 SOL (−6.5% to −7.0% a copy), both halves
  negative. Even selling just BEFORE each of its sales (impossible live) −4.01 SOL (−3.1%): at 0.0345 SOL a round trip
  (6.9% of a 0.5 SOL copy) nothing of its timing is left for a follower. Not a wallet to copy, by any exit.
