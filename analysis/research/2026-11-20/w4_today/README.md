# Wallet 4, Nov 18 22:55 - Nov 20 20:17 UTC: its own trades (Nov 20)

The owner: "what is happening today with wallet 4? check his trades". `d1_days.py` (run order: `candidates/c1_fetch.py`
with `SUB=w4today WALLETS=H9kuqGKN... 1.9`, Jupiter prices of every quote token into `SP/w4today/prices.json`, then
`python3 -I d1_days.py SP > out/d1_days.txt`). Its own pump curve trades, priced in SOL at the quote tokens' rate on Nov 20
~20:30 UTC: a coin quoted in a volatile token (B34nXKzC, 5Kjxg6X1: pump coins themselves) can fall under 1.3 SOL here
although the bot saw 1.4+ at the time; its % per coin does not depend on the rate.

| UTC day | coins | its result | copyable (1.3+ SOL) | its result on them | first sale under 290 s |
|---|---|---|---|---|---|
| Nov 19 | 583 | +55.20 SOL (+11.8% a coin, median -4.5%) | 64 | +23.79 SOL (+18.9%, median +0.4%) | 80% |
| Nov 20 to 20:17 | 376 | +34.40 SOL (+10.7%, median -3.9%) | 37 | +7.92 SOL (+14.2%, median +0.7%) | 89% |

By the coin's quote, copyable: Nov 19 SOL coins 21, -1.78 SOL; token coins 43, +25.57. Nov 20 SOL coins 22, +4.03;
token coins 14, +3.88. The bot copies token coins only (a buy on a SOL curve is `Seen::SolBuy`, never a trigger;
`02-decomposition`: its SOL-coin buys after launch lost for itself in October).
