# An exit for FatoU1bj (Nov 24)

The owner, after its deep test (`../../2026-11-20/tape_screen/README.md`, Nov 24 evening: PASS, but one day of buys and a
20-second holder): "let's run it, but engineer a super good exit, re-analyze his trades well; 0.1 SOL for 20 trades then
raise".

    LK=SP/lk RPC_URL=... COST=0.0064 python3 -I x1_exit.py SP SP/hist_FatoU1bj SP/hist_Fatou_new > out/x1.txt

Its first buys of 0.5+ SOL (all SOL coins): 256 to Nov 23 15:13 UTC (the deep test's history) and 33 after (a new fetch,
Nov 23 06:28 - Nov 24 13:01 UTC; unseen by the pick). It holds a median 22 s to its first sale (10% 4 s, 90% 28 s).
It trades in sessions: Nov 23 06:00-15:00 UTC (243 buys of 0.5+ SOL), Nov 24 10:00-12:00 UTC (27), little else.

**The menu, fixed before any result:** follow its sale (our sale in the first trade D slots after its own: D = 0 is the
next trade, 1-3 about 0.4-1.2 s later) or never, x a hold cap from its buy (15-300 s) x a take profit (none, 1.2-3x its
price). Picked at D = 2 (the live bot sees its sale in its slot and lands one or two slots later) on the old data, the
most SOL without the best 2%.

**The pick: out at 1.5x its price, 15 s after its buy, or 2 slots behind its sale, whichever comes first.** Old: +13.3 /
+16.6 / +6.9 / +10.3% by block, +11.8% a copy at 1 SOL, +19.87 SOL without the best 2%. New (33): +1.5%, -0.83 without
the best 2%. All copies at each landing (`out/x1.txt` part 2): our sale D = 1 / 2 / 3: +10.9 / +10.6 / +10.0%; our buy
one slot later too (slot+2): +7.7 / +7.5 / +6.9%.

What matters most: **how fast we sell behind its sale.** Without the take profit, selling in the next trade after its
sale makes +16.1% (cap 15 s) and one slot later +7.2%: its sale crashes the price. The take profit at 1.5x catches most
of the run before it sells and makes the exit far less sensitive to that delay. Its neighbours (tp 1.5, cap 30-300 s:
+9.3% old, +9.3% new) are close; tp 1.3 is weaker (+5%), no take profit with no sale-follow loses (+3.4%, -12.8 without
the best 2%). The units' tp 3x / 420 s / stall 240 is -2.0% on these copies.

At 0.1 SOL the fixed costs (0.0064 a round trip) are 6.4% of the stake: +11.8% at 1 SOL is about +6% a copy at 0.1.

**Live from Nov 24 (`rugsnipe-long-fat`, check `iii`, `config/long-fat.live.example.toml`):** 0.1 SOL a copy, its buys of
0.5+ SOL, tp 1.5, max_hold_s 15, follow_its_sell = true, no stall or sell pressure, SOL coins on the same exit, max_open 2,
daily stop 0.3; the owner raises it after 20 trades. To check after the 20: each trade's sale slot against its sale slot
(the D the backtest assumed), and the result against the model on the same coins.
