# The ladder, audited (Nov 18): the +51% was a model error; the whole bundle sells into its buyers

The owner asked: "is the whole ladder doing that?" Yes, and the check found a bug in the model.

## 1. The bug: the transactions inside a slot were in reverse order

`w5_copy.cpath` (and the older fetchers behind wallet 4's own paths, `allq` / `newq`) sort the signatures by slot
only. `getSignaturesForAddress` lists newest first, so inside a busy slot the transactions came out reversed:
10,953 of 11,164 multi-transaction slots in `allq`, 7,167 of 7,212 in `winners/cpaths` (`slot_order.py` checks it from
the curve's reserves: the state before a trade is the state after the one before it; 579 of 582 test slots chain).

A "slot+1" entry takes the state after the last listed trade of the next slot: with the order reversed, that was the
slot's FIRST state. On the ladder's launches the slot holds two bundled transactions; the model entered at the price
after the first one, and "the next trade" was the second bundle doubling the price.

`c0_flip_audit.py` (old order): first trade after our entry at a median **1.95x** our entry; 67 of 108 copies filled
at 1.5-3x a second after the buy. `c2_flip_fixed.py` (true order, `FIX=1`):

| the frozen flip (ours x1.2, cap 30 s), 108 coins after Nov 17 13:49 UTC | net | a copy | exits at tp / 30 s |
|---|---|---|---|
| reported (`track/PREREG_ladder_flip.md` RESULT) | +27.59 SOL | **+51.1%** | 72 / 35 |
| true in-slot order | −4.21 SOL | **−7.8%** | 13 / 93 |

The live 25 minutes (`forward/out/f1_last25min.txt`: −16.9%, no wins) were right; the backtest was wrong.

**Fixed at the source:** `2026-11-17/winners/w5_copy.py` now reorders every path (`RAW_ORDER=1` for the old order);
`2026-11-17/wallet_hunt/screen.py` takes `FIX=1`. The crew and consensus money tests were restarted on the fix before
they scored anything.

**Wallet 4 is not affected in any way that matters:** the hunt screen rerun in the true order
(`wallet_hunt/out/screen_fixed.txt`) gives wallet 4's copy +82.75 SOL (+10.6% a copy) against +83.89 (+10.8%); the
other wallets move by similar or larger amounts (G9gmk9ms +12.26 → +9.23, sssssyv2 +8.60 → +3.72), no new wallet
appears. Wallet 4's copies land 4 / 8 trades or a slot later, rarely in a bundled slot. The live journal is the judge
of the live bot anyway (84 real trades, +4.79 SOL by Nov 18).

## 2. The whole ladder: a ten-wallet bundle that sells into its buyers

`c3_bundle.py`, the 108 coins, true order. The "ladder" is not three wallets: the launch slot holds **2 bundled
transactions, 10 wallets, 21.1 SOL** (medians), sizes rising (1.54, 2.18, 2.42, 2.62, 2.77, 3.16 | 3.49, 0.81, 1.10,
1.20 ...), lifting the price x2.33 inside the launch slot. In the next 120 s:

| | median per coin |
|---|---|
| the bundle's sales | 72 sales, **22.4 SOL out** (more than the 21.1 in) |
| the bundle's re-buys | 0 |
| the bundle's tokens still held at 120 s | 37% |
| outside buyers | 74 wallets, 22.0 SOL in |
| price over the launch slot's end at 30 s / 120 s / high | x1.01 / x0.98 / x1.09 |

The bundle sold within 120 s on **106 of 108** coins and sold over half its tokens on 74. It drips its launch bag into
the bots and buyers that arrive, holding the price flat; on some coins it dumps everything (x0.35). The edge is the
bundle's, taken from whoever buys after it. Coins where the price rose 1.2x+ in 120 s: 26 of 108; still 1.2x+ at
120 s: 15. That is not enough for a flip that pays 0.0345 SOL a round trip.

## Verdict

The ladder flip is dropped. The rugsnipe-long ladder code (commits 50c8646, 026f828) stays in the tree, off by
default (`[ladder] enabled = false`); it is not to be deployed.

## Files

`slot_order.py` (the fix), `c0_flip_audit.py`, `c1_rungs.py`, `c2_flip_fixed.py`, `c3_bundle.py`, `out/`.
The inputs are t6's: `SP AsDCYFPT:_pm:SP/winners/w13c_res.json 4sgdNABj:_pm:SP/winners/w13_res.json
64Dn57gX:_pm:SP/track/ladder_res.json H2nsBdjF:_pm:SP/track/ladder_res.json EhS8bGVC:_pm:SP/track/ladder_res.json
Gf9gk8sZ:_pm:SP/track/ladder_res.json`, with `NOFETCH=1`.
