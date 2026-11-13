# Wallet 4's buys on Nov 13, 00:30-23:14 UTC: why no 3-hop copy (Nov 13 night)

Run order (`SPD` = a scratchpad folder; Triton URL read from the scratchpad, never printed):
```
python3 -I ../../2026-10-31/since_stop/fetch_w4.py SPD/tx "2026-11-13 00:30"    # 2,097 landed transactions
target/release/examples/scan RPC SPD/tx SPD/prices.json 1.45 > SPD/scan.out       # WBTC at 7,950 lamports a unit
python3 -I unpriced_val.py SPD                    # values the unpriced buys at Jupiter's price, writes prices2.json
target/release/examples/scan RPC SPD/tx SPD/prices2.json 1.45 > SPD/scan2.out     # the same, those tokens priced
```
Results (`out/scan.txt`, `out/scan_priced.txt`):
- 104 buys paid in a token the bot does not price (PUMP `pumpCmXq` 28, `Xsc9qvGR` 23, `TTWofwAg` 19, USDC 12, others 22);
  9 of them worth 1.45+ SOL at today's price (PUMP 5, `Xsc9qvGR` 3, `XspzcW1P` 1).
- With those priced: 20 buys of 1.45+ SOL. 8 routable, all over the 2 hops the journal shows (7 copied: #8-#12,
  #14, #15; the 8th, `oxbezHbo` at 23:02:54 UTC, came after the owner's paste). **12 have no
  route: `NoAnchor`**, their quote token has no PumpSwap pool to SOL or WBTC (PUMP 5, `Xsc9qvGR` 3, `XspzcW1P` 1,
  `EKpQGSJt`, `METvsvVR`, `BArimz1P`). More hops do not help them; only a Jupiter leg would. **No buy needed 3 hops**
  (no `TooLong`); since Oct 29 they came about 2 a day (`2026-10-31/since_stop/out/skipped_groups.txt`: 31 in 14.5 days).

## Wallet 4's own result on the coins we cannot reach (`noanchor_his.py`, `out/noanchor_his.txt`, Nov 13 night)

From data already fetched (no RPC; the owner asked for no more Triton fetches): Oct 29 12:02 UTC to Nov 12 13:38 UTC
(`since_stop` w4tx) and Nov 13 00:30-23:14 UTC (this folder); the 11 hours between are missing. Its 1.45+ SOL buys,
its own SOL in and out per coin (tokens at today's Jupiter price; buy and sale are in the same token minutes apart,
so the % does not hang on that price; coins still held, or traded with another coin in one transaction, left out).
Week 2 from Nov 5 12:00 Beirut.

| group | coins | its spent | its net | % | won | w/o best 2 | week 1 % | week 2 % |
|---|---|---|---|---|---|---|---|---|
| routable (what we copy) | 205 | 372.0 | +58.66 | +15.8% | 93 | +46.60 | +23.1% | +9.6% |
| 3 hops (copied since Nov 13) | 26 | 53.4 | +39.58 | +74.1% | 19 | +27.03 | +75.6% | +70.5% |
| **no pool** (PUMP, `Xsc9qvGR`, `XspzcW1P` and the priced NoAnchor) | 187 | 362.4 | **+86.48** | **+23.9%** | 90 | +70.05 | +38.0% | +18.2% |
| not checked (paid in another token: `SPCXxcqX`, `TTWofwAg`, USDC ...) | 109 | 206.6 | +61.85 | +29.9% | 56 | +47.60 | +38.6% | +24.6% |

By the token it paid with (no pool and not checked): **PUMP `pumpCmXq` 157 coins, +83.11 on 312.1 (+26.6%)**;
`SPCXxcqX` 56, +43.17 (+41.3%); `TTWofwAg` 32, +9.43 (+14.7%); USDC 12, +2.73; `XspzcW1P` 12, +0.56; `A7bdiYdS` 12,
+5.04; `Xsc9qvGR` 8, +2.61; others 7, +1.68. Our copy of them is not modelled (it needs their price paths).

## PUMP's price in SOL, Oct 28 - Nov 13 (`pump_rate.py`, `out/pump_rate.txt`)

From wallet 4's own SOL-PUMP swaps (local data): daily medians 40.9 to 45.7 SOL a million PUMP over 16 days (Nov 4
high, Nov 8 low), the largest day-to-day change −6% (Nov 7 43.5 to Nov 8 40.9). On a 2 SOL PUMP float that is about
±0.1 SOL a day at worst, and it averages out; a SOL-PUMP leg inside every copy (no float) would pay the swap's fee and
spread on each buy and sale for sure.
