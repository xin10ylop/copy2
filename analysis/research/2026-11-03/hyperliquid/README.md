# Nov 3: Hyperliquid traders and vaults we could copy

The owner's ask: from Hyperliquid's top traders of the last 7 days, find who we can copy: a clear strategy, not luck,
very profitable. The ask was widened mid-way to any profitable wallet trading anything (crypto, stocks, commodities),
then to following emptied wallets to where their money went. Everything comes from Hyperliquid's public API (no key):

- the leaderboard (`stats-data.hyperliquid.xyz/Mainnet/leaderboard`, 48,300 accounts);
- each account's portfolio history, fills, positions, ledger and sub-accounts;
- the vault list (9,478 vaults);
- BTC/ETH/HYPE candles.

Times UTC; the data is of Nov 3 about 13:00.

## Run order

The data folder is the session scratchpad's `hl/data/`. The leaderboard (40 MB) and the vault list (14 MB) are left
out; the scripts fetch them again.

```
python3 -I fetch.py DATA 100 30      # the top 100 by week PnL among accounts with $1M+ of weekly volume
python3 -I analyze2.py DATA          # their mirror copy by period, beta to BTC          -> out/top100_mirror.txt
python3 -I history.py DATA           # their whole history: BTC-up vs BTC-down steps      -> out/top100_history.txt
python3 -I scan.py DATA              # the whole leaderboard's candidates (535) and their portfolios
python3 -I rank.py DATA              # picked on the past, copyable, scored on 28 days    -> out/rank.txt, rank.json
python3 -I finalists.py DATA 15      # the 15 funded, active finalists: fills, positions  -> out/finalists.txt
python3 -I track.py DATA             # wallet tracking: sub-accounts, vaults, transfers    -> out/links.json
LINKS=1 python3 -I rank.py DATA      # the 249 linked addresses through the same tests
python3 -I vaults.py DATA            # the 35 open vaults ($500k+, 180+ days)             -> out/vaults.txt
```

## The method

- **Mirror copy:** we hold its positions scaled to our equity. Over a period we make its perp PnL (realized and
  unrealized, its fees and funding included) less our extra cost on its volume: a taker fee of 4.5 bp plus 5 bp of
  slippage, minus the fee it paid itself (0 where unknown, which is conservative).
- **Picked on its history before the last 28 days:**
  - at least 180 days of history;
  - money made both in the 10-day steps when BTC rose and in those when it fell;
  - at least 60% of its 30-day blocks positive.
- **Copyable:**
  - its month's PnL per traded dollar at least 3× our cost (30 bp);
  - weekly volume at most 50× its equity.
- **Scored on the last 28 days, week by week:** also without the best 2 days, and against its deepest drawdown.

## What was found

| Group | Result |
|---|---|
| The top 100 of the week | The biggest are leveraged **shorts** in a falling market. BTC fell in each of the last 5 periods (−3.5%, −0.5%, −2.3%, −1.4%, −2.9%). Their beta to BTC is −3 to −3.7, and over their whole histories they lose heavily in rallies. Example, BobbyBigSize `0x7fdafde5`: −$98.7M in BTC-up steps, +$240.2M in BTC-down steps. Many others are market makers (10,000 fills in hours), or big holders with no trading at all. |
| The whole leaderboard (535 candidates) | 97 pass the history pick and 52 are also copyable. Most are emptied accounts, or one lucky bet: without the best 2 days, little is left. |
| Wallet tracking (249 linked addresses) | No successor found. The emptied accounts withdrew to their own chain address, or went through the system bridges (`0x2000…`, `0x2222…`) or exchange-like addresses. Sub-accounts and receivers are empty; the one funded receiver lost 17% in 28 days. |
| Funded, active finalists | See below. Most have drawdowns a copy would not survive. |
| Vaults (35 open, $500k+, 180+ days) | 12 pass the history pick; the best are below. |

**Traders (mirror copy; % of its equity; 5 bp slip):**

| Address | History | All-time perp | Deepest drawdown | Last 4 weeks (without best 2 days) | Strategy |
|---|---|---|---|---|---|
| `0xaf0fdd39e5d92499b0ed9f68693da99c0ec1e92e` | since May 2024 | +$6.42M | −41% | +50.4% (+13.1%) | HYPE 63%, BTC 19%; 97% maker (limit orders), 112 fills a day; long and short; 3.8× leverage now |
| `0x541e077ac38c56d7bf590924d249c60b0c80071d` | since Dec 2024 | +$2.32M | −22% (worst 10 days −64%) | +135.3% (+80.0%) | 60% stocks (GOOGL, NVDA) and 40% crypto; short-biased; **9.8× leverage now** (BTC short $7.1M at 40×) |
| `0x888e000c78b8f1aada5b3c99f880794907b76d77` | since Jan 2025 | +$5.41M | **−124%** | +123.0% (+45.5%) | BNB short, Brazil ETF (EWZ); short-biased |
| `0x3c363e96d22c056d748f199fb728fc80d70e461a` | since Jun 2025 | +$2.06M | −80% (worst 10 days −142%) | +69.8% (+40.8%) | XRP, BTC; long and short; 5.9× |

**Vaults (copy by depositing; after the leader's 10%):**

| Vault | TVL | Age | All-time | A year | Deepest drawdown | Last 28 days |
|---|---|---|---|---|---|---|
| AceVault Hyper01 `0x9e02aca9865e1859bb7865f6f64801e804a173df` | $0.91M | 442 d | +$0.94M | +24% | −9% | +7.3% |
| Growi HF | $12.56M | 848 d | +$2.85M | +28% | −11% | −0.7% |
| HLP (Hyperliquid's own, no fee) | $150M | 1,279 d | +$138.6M | +18% | −6% | +0.0% |

Near misses with stronger recent months failed the pre-set 60% blocks bar:

- Systemic Strategies ♾️ Hyper: +19.1% in 28 days, −34% drawdown, 6 of 12 blocks positive.
- Long HYPE & BTC | Short Garbage: +11.7%, −19%, 10 of 17.

**Caveats:**

- **Coarse points:** the portfolio series are a point every ~10 days (all time) or ~16 hours (month), so a short
  sharp loss between points is missed.
- **Slippage:** our slippage is assumed, not measured.
- **Leverage:** a mirror copy takes on the trader's leverage. Copying at a lower ratio cuts both the return and the
  drawdown.
