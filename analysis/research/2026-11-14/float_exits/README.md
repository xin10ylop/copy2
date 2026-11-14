# PUMP and SPCX as floats, and the exits over everything the bot then copies (Nov 14; in progress)

Wallet 4 buys many coins with the PUMP token (`pumpCmXq...`) and the tokenized SpaceX stock (`SPCXxcqX...`). Neither
has a PumpSwap pool to SOL or WBTC, so the bot had no route (`../../2026-11-13/routes_nov13/`). Held as floats, like
WBTC, the coin is bought straight from its curve in one hop.

Run order (`SPD` = a scratchpad folder; the Triton URL is read from the scratchpad, never printed):
```
python3 -I ../../2026-10-31/since_stop/fetch_w4.py SPD/w4tx "2026-10-28 18:30"     # wallet 4's landed transactions
FLOATS=pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn,SPCXxcqXj6e5dJDVNovHN8744zkbhM2bYudU45BimGb \
  target/release/examples/scan RPC SPD/w4tx SPD/prices.json 1.45 > SPD/scan_hops.out   # the bot's own route planner
python3 -I ../../2026-10-31/since_stop/build_rows.py SPD                              # -> routable.json (times)
python3 -I ../../2026-10-31/since_stop/model.py SPD 0.5 4                             # each coin's 31-minute path -> paths.json.gz
python3 -I float_exits.py SPD 0.5 > out/float_exits.txt
python3 -I live_gap_w4.py SPD > out/live_gap_w4.txt
```
`prices.json`: lamports per raw unit (WBTC 7,950; PUMP, SPCX and the others at Jupiter's price of Nov 13,
`../../2026-11-13/routes_nov13/unpriced_val.py`).

- `lib.py`: the rows, the paths and the copy model of `since_stop/exit_final.py` in numpy. Checked against it trade by
  trade on the 232 coins both have (464 comparisons): equal but for a float's own curve route, which pays no pool hop
  here (0.3% each way there), and one coin with no trade after ours.
- `float_exits.py`: what the floats add, and 840 exit rules picked on the first half, scored on the second.
- `live_gap_w4.py`: the model against the bot's 17 real trades of Nov 12-13.

Checked so far (Nov 14):
- **Both mints are Token-2022.** PUMP: no freeze authority, no transfer fee. SPCX: a freeze authority, a permanent
  delegate and a pause switch (its issuer can freeze, pause or take it), no transfer fee.
- **The bot's buy and sell from each float simulate on chain** (`rugsnipe-long simulate --tx SIG --user HOLDER --sol
  0.5 --float MINT --close`): PUMP-paid `6HimP4fi`, route curve, 916-byte buy, round trip −5.30% of the stake (the
  curve's fees); SPCX-paid `9wqXM6pw`, round trip −2.47%.
- **Jupiter, 1 SOL into the float and straight back:** PUMP 0.02% lost, SPCX under 0.01%.
- **The scan with both floats, Oct 28 18:30 - Nov 13 23:21 UTC:** 468 routable 1.45+ SOL buys: SOL-paid 141, WBTC-paid
  115, PUMP-paid 150 (120 one hop, 28 two, 2 three), SPCX-paid 54, others 8. Five buys the earlier 3-hop study counted
  (`TooLong(3)`) have no route: its own route is 3 hops from a token we do not hold.

Results: to come when the paths are fetched.
