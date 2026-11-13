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
- With those priced: 20 buys of 1.45+ SOL. 8 routable, all over the 2 hops the journal shows (all 8 copied or
  refused by max_open/its timing: #8-#10, #11, #12, #14, #15, and `oxbezHbo` at 23:0x after the paste). **12 have no
  route: `NoAnchor`**, their quote token has no PumpSwap pool to SOL or WBTC (PUMP 5, `Xsc9qvGR` 3, `XspzcW1P` 1,
  `EKpQGSJt`, `METvsvVR`, `BArimz1P`). More hops do not help them; only a Jupiter leg would. **No buy needed 3 hops**
  (no `TooLong`); since Oct 29 they came about 2 a day (`2026-10-31/since_stop/out/skipped_groups.txt`: 31 in 14.5 days).
