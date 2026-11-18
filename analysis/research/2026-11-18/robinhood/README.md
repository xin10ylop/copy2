# Robinhood Chain: wallet 4's look-alikes on the Pons launchpad (Nov 18)

The owner: "search on Robinhood, properly", with the public RPC. Robinhood Chain (chain 4663) is an Arbitrum Orbit L2
with ~0.1 s blocks. Its biggest memecoin launchpad, **Pons V2**, is pump.fun's design: one bonding curve per coin, 1B
supply, graduation at 4.2 ETH into a Uniswap v4 pool; coins quoted in ETH (10,175 of 11,828 launches in two weeks),
USDG, cbBTC or tokenized stocks (docs.bitquery.io, Pons Launchpad API). The official RPC
(`rpc.mainnet.chain.robinhood.com`) serves logs at least 36 days back, 30,000 blocks and 10,000 logs a request;
PublicNode's free endpoint does not (archive needs a token).

Run order (DIR = a scratchpad folder; no keys):
```
python3 -I rh1_fetch.py DIR 30                       # CurveBuy / CurveSell / TokenLaunched / LaunchSwept, 30 days (~15 min)
python3 -I rh2_profile.py DIR 0.05 > out/rh2_profile.txt        # every wallet's own trading, wallet-4-like filters
python3 -I rh3_curve_fit.py DIR                      # the curve: constant product, V0 = 1.75 ETH, fee on top (0.57% error)
SPLIT=1793788260 MINC=20 python3 -I rh5_direct.py DIR > out/rh5_direct.txt   # OUR copy of every wallet with 20+ buys
SPLIT=1793788260 [LANDB=2,3,5] python3 -I rh6_engineer.py DIR WALLET > out/rh6[b]_<w>.txt   # the full engineering
python3 -I rh7_check.py DIR WALLETS...; python3 -I rh8_cobuyers.py DIR WALLETS...; python3 -I rh9_real_copiers.py DIR COPIER:LEADER...
```
Data: Oct 19 - Nov 18 2026, ~1.5 million curve trades. Our copy: 0.02 ETH, 0.00004 ETH gas a round trip, the curve
fee and snipe tax as each landing trade paid them (the snipe tax is inside CurveBuy's fee field), a coin that
graduates sold at its last curve price (the v4 pool is not read). Halves: Oct 19 - Nov 4 / Nov 4 - Nov 18.

**The direct screen** (`out/rh5_direct.txt`): 534 wallets with 20+ copyable buys, four exits fixed before looking,
picked on the newer half and scored on the older: 0x9a3955a1, 0x5bc235ac, 0x9e0771d4, 0xc54d3914 pass, most under all
four exits. 0x9689992f (the best of the profile screen) fails with every coin (older half −4.5% a copy).

**The full engineering** (`out/rh6b_*.txt`: buy size, coin type = ETH in the curve at its buy, price limit, tp,
time, sell pressure, stall, its sale, every combination; our buy landing 2, 3 and 5 blocks after its buy):

| wallet | copies | settings positive on both halves | the choice | a copy | w/o 2% | picked on one half, rank on the other |
|---|---|---|---|---|---|---|
| 0x9a3955a1 | 339 | 230,935 of 311,040 | 0.1+ ETH buys, coins under 0.5 ETH in the curve, limit 1.5x, tp 4, 600 s | +24.2% | +1.26 ETH | 328 / 1,049 |
| 0x5bc235ac | 514 | 214,984 of 233,280 | 0.05+ ETH, any coin, limit 1.5x, tp 3.5, 600 s, sp 10/30 | +12.5% | +0.81 | 584 / 26,437 |
| 0xc54d3914 | 190 | 155,520 of 155,520 | 0.03+ ETH, tp 2.5, 300 s, sp 8/60, stall 240 | +26.7% | +0.90 | 15 / 4,868 |
| 0x9e0771d4 | 134 | 233,190 of 233,280 | tp 2.5, 600 s (Nov 1-8 only) | +38.9% | +0.94 | - |
| 0x9689992f | 372 | 137,813 of 544,320 | coins under 0.5 ETH in the curve only | +6.8% | +0.26 | 275,091 / 501,189 |

**Who they are** (`out/rh7_check.txt`, `out/rh8_cobuyers.txt`): none bought its own launch, each traded coins of
hundreds of creators; median hold 70 s (0x9a3955a1), 130 s (0xc54d3914), 94 s (0x9689992f); 0x5bc235ac sells only
98 of 630 coins on the curve and 0x9e0771d4 none (they hold into the pool or never sell). After their buys come 10-35
other wallets and 0.24-1.3 ETH in 5 minutes (a random buy: 5 and 0.09). The frequent co-buyers are mostly big bots
that buy thousands of other coins (0x92475293, 0xe4a727d2); dedicated copy bots follow two of them within 2 blocks
(0x840672e7 → 0x9a3955a1, 0xff335b2c → 0x5bc235ac). 0x9e0771d4's coins are bought by four wallets that buy nothing
else (a group), and it stopped on Nov 8: dropped.

**Real money** (`out/rh9_real_copiers.txt`): the bot copying 0x9a3955a1 within 2 blocks made +0.66 ETH on 235 of
its coins in the newer half (won 48%; −0.08 on 48 in the older). The other two copiers' sales are not seen on the
curve (0-6% won), so their results are not readable here.

**Their stakes** (`rh10_sizes.py`, `out/rh10_sizes.txt`): one buy a coin each; median 0.100 ETH (0x9a3955a1, 56.4 ETH
put in over 30 days), 0.050 (0x5bc235ac, 35.3 ETH), 0.042 (0xc54d3914, 13.7 ETH).

**The last 3 days** (`rh11_days.py`, `out/rh11_*.txt`; STAKE=0.05, LANDB=2,3,5, each wallet's chosen setting):

| wallet | before the last 3 days | the last 3 days |
|---|---|---|
| 0x9a3955a1 | 294 copies, +22.8% a copy, won 51% | 45 copies (15 a day), +26.5% a copy, won 60% |
| 0x5bc235ac | 443 copies, +10.5% a copy, won 33% | 71 copies (24 a day), +21.1% a copy, won 46% |
| 0xc54d3914 | 178 copies, +25.2% a copy, won 60% | 19 copies (6 a day), +39.2% a copy, won 68% |

All three behaved as before, so the owner had the bot built with no paper phase: `crates/rh-copier`, `docs/23-rh-copier.md`.
