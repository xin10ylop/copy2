# The stuck coin: 2RR6sfbi (Oct 27), 0.51 SOL lost on one copy that could not be sold

In short: on Oct 27 the copy bot (rugsnipe-hot) bought 2RR6sfbi for 0.51 SOL as a copy of wallet 4's launch buy. The
coin's bonding curve completed ("graduated") right as we bought. Trading then moved to its PumpSwap pool. The bot only
knew how to sell on the curve. It retried that dead curve sell **405 times in about five hours**, and every attempt
failed. While it retried, the coin fell about 95%. We sold it by hand the same day for **0.029 SOL**. In all, the coin cost
about **0.57 SOL**: 0.48 of the 0.51 stake, plus 0.09 SOL of fees on the failed sells. The bug is fixed in the code, in
both bots, but the copy bot's fix was never deployed: the bot was stopped and its server (fra1) terminated.

This page is the same in both repos (copy1: operator 1 "him"; copy2: wallet 4). The coin was a wallet 4 copy, but it
sat in the one wallet all the copies shared. It drove the daily-loss kill that stopped every copy, his included, and the
same bug could have hit any copied coin.

| | |
|---|---|
| Coin | `2RR6sfbiMbySH2b6Bwo4ZxUiByn29uhxfTSMY98Xpump` |
| Copied wallet | wallet 4, `H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg` (its buy: 0.160 SOL, tip 1.1M; its own result on the coin −0.1524) |
| Our buy | Oct 27 06:55:32 Beirut (04:55:32 UTC), our bid 8.0M, landed 1 slot after its buy, fees 0.0080 (check.sh row) |
| Bot wallet | `4g49xGbgHZk3QYR1o6QSfDUbHmJZFwN6iDp6Vco1skff` (the hot copy bot's wallet, shared by every copied wallet) |
| Failed sells | 405, each failing with `BondingCurveComplete` (pump error 6005), about 04:55 to 10:07 UTC |
| Sold by hand | Oct 27, through Jupiter: 1,236,340,723,216 raw token units in, 29,026,684 lamports (0.0290 SOL) out, tx `2Dsz4eiFRfQwUmuVwFEWjAQizHiXcZGVztW9dE9wpzygo9TbKS5q2qXEriSjuNgsZnRtmVCvpjA6GcrWDHTKyX42` |
| Cost | stake −0.51 + 0.029 back = −0.48; failed-sell fees −0.092; total about −0.57 SOL |
| Left over | one empty token account for the coin, about 0.0015 SOL of rent, not worth closing |

## What you saw

In the check.sh paste (`check-sh-2026-10-27.txt`, taken at 11:45 Beirut):
- `== open now  1  2RR6sfbi`. The coin never closed.
- Wallet 4's table: `06:55:32  2RR6sfbi  -0.1524  OPEN  COPIED  0.160  1.1M  +0  filled  +1 slot  8.0M  0.0080`.
- `TRADING: NO: stopped by the daily_loss kill` at 09:50:35 Beirut, `daily P&L marked to market -1207492396 lamports`.
  "Marked to market" counts the open position at its current price, so the collapsing 2RR6sfbi pushed the day past
  the 1 SOL stop (`max_daily_loss_lamports`).
- `results since the start ... net_sol -0.7628`, while the wallet went from 1.7192 to 0.3081 SOL (−1.4110). check.sh
  counts closed trades only. The 0.51 in the stuck coin and the failed-sell fees were not in its −0.76.

## Where the wallet's −1.41 SOL went (every lamport, from the chain)

`analysis/research/2026-10-27/h9long/own_ledger.py` (in copy2; copy1 has it at
`analysis/research/2026-10-27/own_ledger/own_ledger.py`) classifies every transaction of the bot wallet from Oct 26
13:22 to Oct 27 10:07 UTC, 1,326 in all. The total matches the balance change exactly (−1.4115), and nothing was withdrawn:

| Where it went | SOL |
|---|---|
| 416 closed trades | −0.809 |
| 2RR6sfbi, bought for 0.51 and still held | −0.510 |
| 405 failed attempts to sell 2RR6sfbi (fees) | −0.092 |
| 83 failed buys (fees) | −0.001 |
| **Total** | **−1.4115** |

Without the stuck coin, the copies themselves lost about 0.8 to 0.9 SOL over the window.

## Why it happened

- A pump.fun coin trades on its bonding curve until the curve fills. Then it "graduates": the curve is closed and
  trading moves to a PumpSwap pool. A curve sell after that fails with `BondingCurveComplete` (6005).
- The hot bot's exit engine could switch a position to the pool, but the live loop never told it the coin had
  graduated, and the real sell path built curve sells only. So every exit attempt was another curve sell.
- The hot loop also handed the stuck sell to the guard process, which can only sell on the curve. It retried too.
- It is rare: a coin has to graduate during the few seconds we hold it. But when it happens, the position can't be sold at
  all, and every retry costs a fee.

## The fixes

**Copy bot (rugsnipe-hot), commit `af681ad`** (in both repos' code; never deployed, because the bot stayed stopped):
- The first sell that fails with 6005 switches the coin to its PumpSwap pool (`HotIn::CurveComplete` →
  `ExitEvent::Complete`, venue PumpSwap). Pending orders are re-sent.
- It reads the pool's real reserves (`LaneCmd::Pool` → `HotIn::PoolState`) and sends a real pool sell
  (`Templates::amm_sell`, the pool's `sell_v2`, 120k compute units).
- It reads our own pool sale from the transaction's balances (`own_pool_sell`; a pool sale has no curve trade event).
- It never hands a graduated coin to the curve-only guard.
- Tests: `crates/rugsnipe/tests/sell_lifetime.rs` (curve sell fails with 6005 → pool sell → pool reserves → the sale
  closes the position) and `crates/rugsnipe/tests/graduation.rs` (the pool sale parser and pool vaults, on a real
  mainnet sell of 2RR6sfbi, fixture `tests/fixtures/pool_sell_2RR6sfbi.json`).
- `crates/rugsnipe-tx/examples/amm_sell_tx.rs`: the pool sell transaction, simulated on mainnet from our wallet with its
  real 2RR6sfbi tokens: success, 70,286 compute units, +0.0277 SOL.
- To deploy, if the hot bot ever runs again: `cd ~/rugsnipe && git pull && sudo bash deploy/install.sh --role hot`.

**Long copy (rugsnipe-long), commits `ec2463c` and `e9c403a`** (audited for the same class of failure; in the build
that runs on Ohio):
- A coin whose curve completes, in any state (even with a sell already out), sells on its canonical PumpSwap pool, as it
  also does after 3 failed sells when the pool exists. `examples/sim_pool_sell.rs` simulated it on mainnet from real
  holders (C5xph2yL and EJAxERvK into WBTC: success).
- A sell that keeps failing no longer goes out on every tick (about 0.0003 SOL each, up to about 0.5 SOL an hour). It
  goes 3 times at once (the floor drops each time), then waits 5 s, 30 s, 2 min. Once its failed fees on the position
  pass `max_sell_fail_sol` (0.01), it tries every 10 min. It never gives up, and the journal says
  `long CRITICAL sells of #N ... keep failing`.
- A buy given up as dropped that lands later reopens the position (`long late-fill`), also when it landed while the bot
  was down. Statuses search the whole history, so a sell that landed during downtime is not sold again.

## How it was sold by hand (for the next time)

The hot bot and the guard were stopped first, so nothing competed with the sale. Then the long bot's
sell-through-Jupiter command was pointed at the hot wallet for this one sale:
```
sudo systemctl stop rugsnipe-hot rugsnipe-guard
sudo sed 's#^wallet_file = .*#wallet_file = "/etc/rugsnipe/keys/probe-keypair.json"#' /etc/rugsnipe/long.toml | sudo tee /etc/rugsnipe/sell-once.toml >/dev/null
sudo /opt/rugsnipe/bin/rugsnipe-long float sell 2RR6sfbiMbySH2b6Bwo4ZxUiByn29uhxfTSMY98Xpump all --config /etc/rugsnipe/sell-once.toml
sudo rm /etc/rugsnipe/sell-once.toml
```
Output: `quote: "1236340723216" 2RR6sfbi -> "29026684" So111111 ... sent 2Dsz4eiF... landed in slot 46204042`.

## Lessons kept

1. **Any position that can't be sold is a full loss of its stake.** Before any real money, test the exit on every
   venue a coin can end up on (curve, pool after graduation, multi-hop routes), not only the entry.
2. **A failing sell must back off and alert, not retry forever.** 405 retries cost 0.09 SOL on their own.
3. **check.sh must count open positions and failed-sell fees.** Its "since the start" line said −0.76 while the wallet
   was −1.41. Still open: check.sh was not changed, so read the wallet balance line or run `own_ledger.py`.
4. **One shared wallet for every copied wallet means one wallet's bad coin stops all the others**, through the daily
   stop.
5. **This is the reason for the small real test before scaling the long copy** (0.1 SOL, 1 position, about 5
   trades): at 0.1 SOL a bug like this costs 0.1, not 1.

## Sources

- `check-sh-2026-10-27.txt` (this folder): the open position, wallet 4's row, the kill line, the balance.
- `analysis/research/2026-10-27/h9long/own_ledger.py`, commit `51f1454` (the ledger).
- Commits `af681ad` (hot fix), `ec2463c` and `e9c403a` (long copy), with their messages; `docs/07-deploy.md` (the
  hot fix's deploy note); `docs/20-long-copy.md` §3 "When things fail".
- The session of Oct 27: the user's sell output (quote, signature, slot) and the ledger table.
