# Robinhood: live against the backtest, trade by trade (Nov 20)

The owner: "we are so far from these results, you are not finding what is wrong". `g1_reconcile.py` (run:
`python3 -I g1_reconcile.py <rh1_fetch DIR> <rhd groups.json> > out/g1_reconcile.txt`), data to Nov 20 15:40 UTC, from
the Chicago box's start (Nov 19 14:17 UTC): every copy the backtest counts (landing 2 blocks, the live exit of each
wallet; wallet 2 until 17:00 UTC Nov 19) against every buy of our wallet on chain. Results in % of the stake, summed.

| | copies | sum |
|---|---|---|
| the backtest over the window | 26 | +680% |
| of which the bot took | 18 | model +19.5%, **live -58.6%** |
| of which the bot never took | 8 | **+660.5%** (0x2a624ed0 wallet 3 +535.5%, 0x7a9079f3 wallet 2 +202.2%, six losers) |

- **Execution is right:** on the coins the bot took, the model at the bot's ACTUAL landing equals live within a few
  points on every trade (w1 -4.4% / -3.9%, w2 -10.3% / -11.0%, group +45.0% / +41.7%).
- **Wallet 3 lands late:** 6, 21, 4 and 11 blocks behind its buy (the others 1-3). Its 45 s sale makes the first second
  decisive: the model at 2 blocks +10.9% a copy on those, at our landing -11.0% (0x0df8e9ac +95.7% -> +30.5% at 21 blocks).
- **The backtest's profit in the window is two coins the bot did not buy, both refused by the daily stop** (the box's
  journal, Nov 20): `rh skip ... daily stop` for every copy from 15:00:03 to 15:23:22 UTC Nov 19 (0x7a9079f3 wallet 2
  +202.2%, 0x2a624ed0 wallet 3 +535.5%, and four losers); the restart at 15:23:55 UTC ran with `daily stop 0`. The two
  wallet 2 copies at 16:27-16:29 UTC were not missed: wallet 2 was off from the 16:16 UTC restart (its buys then fall
  under `min_its_eth`, not journaled); the script's 17:00 cut was too late.

**Where wallet 3's landing time goes** (the box's journal, Nov 20; `g2_crowd.py`, `out/g2_crowd.txt`):
- the feed is not late: `signal 0xc54d3914 buy at block 119137137: the node was at 119137137 when it arrived (+0 blocks)`;
  every signal since Nov 20 morning +0 or +1 block (one +12, one +3, both wallet 2);
- our buy is sent at once (#47: 97 ms, #40: 112 ms) and then waits to be included: #47 landed 11 blocks after its buy
  (the chain makes ~10 blocks a second: 119137137 at 14:58:00, 119168875 at 15:50:55 UTC), #40 21;
- not a crowd on the coin: 3 other trades between its buy and ours on #47, 1 on #37, 8 on #40; the 12 copies of the
  other wallets since Nov 19 14:17 UTC landed 1-3 blocks behind with up to 9 trades between.
The chain is Arbitrum Orbit (Nitro): the sequencer takes transactions first come, first served; a higher fee buys no place.
