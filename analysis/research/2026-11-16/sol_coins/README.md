# Copying wallet 4's SOL-priced coins? (Nov 16-17)

The owner, Nov 16: "why dont we copy these?" then "study now". The bot copies only coins whose curve is quoted in
another token (`docs/20-long-copy.md` §3, Trigger). Wallet 4 also trades SOL-priced coins, heavily.

**Answer: no.** Copied with today's exits, its 1.3+ SOL buys of SOL-priced coins lose: −1.97 SOL on 235 copies
(−1.7% a copy), **−9.66 without the best 5**; drawn again, the mean a copy is −9.0% to +5.2% (5% / 95%), against +13.6%
for the coins we copy now. Its own edge on these coins is too thin (+4.5% on the same coins, against about +17% on the
other-token coins) to pay a copy's later price and fees. The Oct 28 study found the same with the old exits
(`../../2026-10-28/more/README.md` §E: −11.12 and −2.34). Not built.

## Run order

```
python3 -I collect.py $S/solq $S/w4all/tx $S/newq/w4tx $S/w4eve2/w4tx        # -> sol_buys.json, every SOL-priced coin it traded
RPC_URL=... LK=$S/solq/lk python3 -I paths.py $S/solq 1.3 $S/w4all/tx $S/newq/w4tx $S/w4eve2/w4tx   # 12 min of trades a coin
python3 -I sol_model.py $S/solq $S/solq/lk/paths > out/sol_model.txt
```

## Results

**What it trades** (`collect.py`, over 55,310 of its transactions, Oct 21 18:39 to Nov 16 19:36 UTC): 8,456 SOL-priced
coins, from about 100 to 350-780 a day. By its first buy: 0-0.5 SOL 3,898 coins (its net −18.00), 0.5-1.0 3,145
(−14.27), 1.0-1.3 801 (+32.80), 1.3+ 612 (+52.05 on 929 SOL in, +5.6%).

**Our copy** (`sol_model.py`, `out/sol_model.txt`): the paths of 253 of the 612 coins were fetched, in random order (a
fair sample of the days; the owner stopped the fetch on Nov 17 once the answer was clear), 248 usable. The live setup:
tp 4.0, its sale followed 30-290 s under 1.5x, sell_pressure [5, 60, 30], stall 180 s, 600 s, refused past 1.25x; 0.5
SOL, every copy (no slot limit), mean of the three landings (4 / 8 trades, the next slot).

| | copies | net SOL | a copy | won | w/o best 5 |
|---|---|---|---|---|---|
| all | 235 | −1.97 | −1.7% | 29% | −9.66 |
| its buy 1.3-1.5 | 133 | −2.97 | −4.5% | 26% | −8.93 |

Every other exit tried on the same copies loses too (tp 2 and 3, no signals, its sale never followed, a 300 s timer;
`out/sol_model.txt`). Within the 2 open slots a SOL-coin copy would also take the place of an other-token copy, so the
real cost is higher than the table. The 2.0-3.0 SOL band is positive on few copies and loses without its best 5: noise.

**Correction:** `../decomp/README.md` said "No SOL-priced coin (part D) since Oct 29". Wrong: that study's data left
them out; wallet 4 trades 350-780 a day (above).
