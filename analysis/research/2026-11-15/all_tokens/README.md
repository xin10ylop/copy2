# More floats: which of the tokens wallet 4 pays with are worth holding (Nov 15)

The owner: "fix all the tokens". With every token it pays with held as a float, wallet 4's 1.45+ SOL buys that have a
route go from about 28 to about 50 a day (`token_table.py`, `out/token_table.txt`, Oct 29 - Nov 15, 17.0 days). Four
tokens besides the floats live now (WBTC, PUMP, SPCX) carry most of the rest:

| token | what | buys a day | its own result |
|---|---|---|---|
| `TTWofwAge91oFhZs7kpQdyrVRkmevgM88xijGvQFbKo` | Take-Two (TTWO), Backpack tokenized stock | 3.0 | +18.8% |
| `98sMhvDwXj1RQi5c5Mndm3vPe9cBqPrbLaufMXFNMh5g` | HYPE | 1.9 | +25.6% |
| `DJTu7vi8norVzdVAffgvb39VP7wjKeTsgaMBJrzfxvoF` | Trump Media (DJT), Backpack tokenized stock | 1.6 | +21.5% |
| `XsbEhLAtcf6HdfpFZ5xEMdqW8nfAvcsP5bdudRLJzJp` | Apple xStock (AAPLx) | 1.4 | +53.2% |

The others are under 1.2 a day or it loses on them (USDC +6.9%, `AMD8XwJX` −12.4%, `Pren1FvF` −89.8%).

Run order (`SPD` = the float study's folder, `ALL` = a new one with `w4tx` and `cache` linked to it):
```
python3 -I price_tokens.py SPD                     # every paying token at Jupiter's price -> prices_full.json
FLOATS=<all of them> target/release/examples/scan RPC SPD/w4tx SPD/prices_full2.json 1.45 > SPD/scan_all.out
python3 -I token_table.py SPD > out/token_table.txt
# ALL/scan_hops.out = the scan_all.out lines of the eight kinds; build_rows.py ALL; model.py ALL 0.5 4 (the paths)
python3 -I copy_all.py ALL > out/copy_all.txt
python3 -I subsets.py ALL > out/subsets.txt
```

**Checked on chain (Nov 15):** the bot's buy and its sell back simulate from each of the four floats (`rugsnipe-long
simulate --float MINT`, route curve, one hop; round trip −3.83% of the stake for the three stock tokens, −6.15% for
HYPE: the curve's fees). Jupiter, 0.5 SOL in and straight back: TTWO 0.01% lost, HYPE 0.00%, AAPLx 0.08%, DJT 0.43%.
TTWO, DJT and AAPLx are Token-2022 with a freeze authority, a pause switch and a permanent delegate (the issuer can
freeze, pause or take them, as with SPCX); HYPE is a plain SPL token with none.

**Our copy (`out/copy_all.txt`, `out/subsets.txt`; 975 buys, Oct 21 - Nov 15, 24.7 days; the live rule, 0.5 SOL, raw,
mean of three landings).** Every copy of each kind alone: TTWO 78 copies +3.92 SOL (9 take profits), HYPE 53 +2.82
(8), DJT 36 +3.84 (7), AAPLx 26 +3.05 (5); each is carried by one block (B) and thin without it. The bot's run, 2
open, blocks A | B | C | all (without each block's best 2):

| floats | A | B | C | all |
|---|---|---|---|---|
| live now | +7.42 | +14.08 | +13.44 | +34.94 (+26.63) |
| + TTWO | +8.68 | +13.24 | +16.91 | +38.83 (+30.52) |
| + DJT | +7.69 | +18.39 | +13.05 | +39.12 (+30.61) |
| + AAPLx | +7.22 | +16.89 | +13.83 | +37.94 (+29.63) |
| + HYPE | +7.15 | +18.74 | +12.49 | +38.39 (+29.65) |
| **+ TTWO + DJT** | +8.95 | +17.55 | +16.52 | **+43.02 (+34.50)** |
| + TTWO + DJT + AAPLx | +8.75 | +20.36 | +16.91 | +46.02 (+37.50) |
| + all four | +8.48 | +24.38 | +15.96 | +48.83 (+39.99) |

TTWO + DJT, and those two with AAPLx, are ahead of the live setup in each of the three blocks; HYPE adds only in B
(it costs a little in A and C). A third open slot adds about +1.5 to +2 SOL on top. Leaving the SOL routes out to
fund a float costs about 7 SOL here (`out/subsets.txt`), so they stay.

**Caveat:** the tokens are valued at the Nov 15 price for the whole period. Wallet 4's buys sit near the 1.45 SOL
floor, so the count per kind moves with the price used (PUMP-paid buys: 192 at the Nov 13 price, 118 at the Nov 15
one). The bot uses the price of the moment.

**Recommended (Nov 15):** add TTWO and DJT as floats at 0.5 SOL each now (the wallet has about 1.4 SOL beyond one SOL
copy); AAPLx when another 0.5 SOL is spare; HYPE not yet.
