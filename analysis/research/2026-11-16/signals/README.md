# Sell on what the other traders do (Nov 15 evening)

The owner: "analyze top 10 holders, if they sell", "test timing, how fast it drops and rises, along with holders and
who is buying and selling". The paths start at wallet 4's buy, so the bags held before it are not known; every trade
after it is (who, buy or sell, tokens, SOL). A sell of 2-5% of the 1B supply is a top-10 holder's size. Data: 1,238
buys (seven kinds, 1.3+ SOL, every fee tier, Oct 21 - Nov 15 13:04 UTC), 0.5 SOL, 2 open, caps, mean of three
landings; the live rule tp 3.0, 600 s, early 30-290 s. Blocks A / B / C as before.

    python3 -I signals.py  CQ ALL > out/signals.txt    # round 1: big sells, sell clusters, SOL flow, drain (112)
    python3 -I signals2.py CQ ALL > out/signals2.txt   # round 2: trails 40-70%, speed of falls, stalls, who sells,
                                                       #   sellers vs buyers, a longer timer while buying is strong;
                                                       #   each at tp 3.0 / 4.0 / none (354)
    python3 -I robust.py   CQ ALL > out/robust.txt     # the leaders day by day, by landing, redrawn days, neighbours
    python3 -I combo.py    CQ ALL > out/combo.txt      # the two leaders together, at each tp

**Round 1 (`out/signals.txt`): nothing.** A single sell of 5%+ of the supply after 30 s under 1.5x +57.57 against
+56.63; picked on two blocks −1.59 SOL on the third. They do calm the days ("a sell of 2%+ after 30 s": worst day −0.92
instead of −2.41) but cost 8 SOL.

**Round 2 (`out/signals2.txt`):** at tp 3.0, by family (settings ahead of live / all): trail 4/20 (best +0.34), how
fast it falls 0/32, **no new high for T s 11/16**, a holder from before our buy sells 1/8, a later buyer sells 4/8,
their sums 0/12, **more sells than buys 10/18**, hold to 1200 s on strong buying 1/3. Picked out of all 354 on two
blocks and scored on the third: +2.94 / +1.90 / +2.11 (+6.94 SOL), each held-out block ahead.

**The two leaders under harder tests (`out/robust.txt`, `out/combo.txt`):**
- **5+ more sells than buys (by others) in the last 60 s:** +6.52 at tp 3.0; 16 days ahead, 8 behind; ahead in 91-93%
  of redrawn days. The neighbours: any N from 2 to 10 over 60-120 s is ahead (+2.3 to +11.4); over 10 s it loses
  (−1.2 to −13.0): a short burst of sells is noise, a minute of them is not.
- **No new high for 180 s (from our buy):** +6.47; 18 days ahead, 6 behind; ahead in 99.2% of draws; T 90-240 s all
  +4.8 to +6.5, 300 s +2.2, 400 s −1.8.
- **tp 4.0 or no tp alone** lead too (+12.12 / +15.41), on this wider data even without the best 5 (+59.06 / +54.35
  against +48.46). On the 781 buys of Nov 14 (`../../2026-11-14/float_exits/`) tp 4.0 lost without each block's best 5,
  and was withdrawn; the wider set (1.3-1.45 SOL, TTWO, DJT, HYPE, Nov 14-15) says otherwise.

| rule (0.5 SOL, 24 days) | total | A / B / C | w/o best 5 | losing days | worst day | deepest fall | ahead in draws |
|---|---|---|---|---|---|---|---|
| live (tp 3.0) | +56.63 | +11.10 / +24.30 / +21.24 | +48.46 | 6 | −2.41 | −2.41 | |
| both signals, tp 3.0 | +65.35 | +13.27 / +29.99 / +22.09 | +57.29 | 3 | −1.70 | −1.70 | 96.7% |
| live, tp 4.0 | +68.75 | +13.91 / +27.92 / +26.92 | +59.06 | 4 | −1.94 | −1.94 | 97.9% |
| **both signals, tp 4.0** | **+75.29** | **+15.66 / +33.96 / +25.66** | **+65.65** | **3** | **−1.23** | **−1.23** | **99.9%** |

Caution: picked out of about 470 rules on these same days; the two-block test and the wide plateaus are what speak for
it. The bot can see both: it already receives every transaction of a coin it holds (`feed.rs`, the "mints" filter);
"no new high" needs only the price. Neither is built.

## Round 3: is there more of the same kind? (`round3.py`, `out/round3.txt`, Nov 15 night)

The owner: "you sure there are no other stuff like the 2 signals?" 75 rules of ten families not tried before, each
**added to the live setup** (both signals, tp 4.0, 600 s: +75.29 SOL), so a gain is a gain on top:

| family | ahead of live | best | what it shows |
|---|---|---|---|
| more selling wallets than buying (wallets, not trades) | 5 of 12 | +0.70 | the trade count already says it |
| sells 2-3x the buys | 2 of 8 | +0.17 | the same |
| net tokens dumped over 1-2 min (2-8% of supply) | 0 of 8 | −7.01 | big dumps are followed by bounces: −7 to −21 |
| no buy by anyone else for 30-180 s | 4 of 5 | +0.92 | the stall rule already covers a coin nobody buys |
| under 2-5 trades in a minute | 0 of 3 | −2.78 | |
| a stop that waits (under 0.5-0.8x after 1-5 min) | 3 of 16 | +0.07 | |
| the coin's creator sells | 0 of 2 | −1.52 | the creator known for all 1,238 |
| wallet 4's sale followed more widely | 0 of 7 | −0.64 | above 1.5x or at any time: −8 to −23; never: −0.94 |
| timer 300-1790 s | 1 of 5 | +0.55 (900 s) | 300 s −7.68; 450-1790 s within ±1.6 |
| the two live signals with other values | 2 of 9 | +1.76 (stall 240 s) | 5 in 60 s and 180 s sit on a flat top |

Picked on two blocks and scored on the third: −0.12 / −0.23 / −0.69 (**−1.04 SOL**). **Nothing adds to the live setup;**
its neighbours are all within about ±2 SOL of it, which is what a setup that is not a lucky pick looks like. Not
testable from this data: what the top holders held before wallet 4's buy (the paths start at its buy; it would need
each coin's full history from its creation).
