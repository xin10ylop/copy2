# Wallet 4 as the reference for a copy (the one copy that won live)

Wallet 4 = `H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg` (this repo's folders `01`-`07`). Every number names its source there.
Times UTC. This page is what a new trader is measured against: how wallet 4 traded, how our copy of it executed,
and the test a candidate has to pass with its own rules and its own stake.

## 1. How wallet 4 traded (the trader)

| | Wallet 4 | Source |
|---|---|---|
| Result | +355 SOL Oct 19-27; the part we could copy (A: its 1.45+ SOL buys of coins priced in another token, routable) +102 SOL on 324 trips | `02-decomposition/README.md` |
| Size | 1.45-1.55 SOL on the copied buys; its smaller buys (under 1.45) lost as a copy | same, floor table |
| Exits | take profit 2.5x, stop 0.7x, a 30-minute timer; 67% of trips held to the timer (Oct 19-27), 39% after Oct 27 | `07-rework-2026-10-28/README.md` §1 |
| Early sales (before 30 min, neither rule) | 3.5% (Oct 19-22), 13.6% (Oct 23-27), 49% (Oct 27-28: it changed) | same |
| Pace | 64-112 copyable buys a day Oct 19-27; 2 an hour by evening, 1 every 2 hours at night on Oct 28-29 | same; `CLAUDE.md` |
| Fees | buys: median 0.0071 SOL fee (p10 0.0035, p90 0.0134) + a 0.00107 SOL tip on 40-55%; sells 0.00001, no tip | `03-strategy-A-long-copy/backtests.md` §11 |
| Landing | a multi-sender bot (Helius, Astralane, Jito, Nozomi ...), one tip per transaction, durable nonces; block index p50 207 on its big buys: **no top-of-block lane** | `07-rework-2026-10-28/wallet-check.md` |
| Failed transactions | 2.4% (495 of 20,476), −2.85 SOL | same |

## 2. How our copy of it executed (live, Oct 28 18:34 → Oct 29 11:52)

`03-strategy-A-long-copy/deploy-frankfurt.md` §6 (commit 1ce94d0, every trade checked on chain):

| | Live |
|---|---|
| Reaction | seen at its slot +0, sent in 3-6 ms (Triton gRPC feed, Nozomi sender, Frankfurt) |
| Landing | in its own slot on 10 of 18 buys, at the top of the next block on 8 (both times its buy sat late in its block) |
| Coin trades between its buy and ours | 1-13, **median 4** |
| Price paid against its price | median +10.7% on the 12 filled at 0.1/0.5 SOL; +13.3%, +13.3%, +12.8% on the three 1 SOL buys (chain, `calib1.py`); 3 refused at 1.25-1.36x by the 25% limit |
| Sells | every one landed on the first try |
| Costs as configured | about 0.003 SOL a round trip (0.001 Nozomi tip + priority); the backtests charge 0.0095 a transaction |
| Result | 16 closed, 7 won, 3 refused, **+1.3459 SOL** (+0.31 at 0.1, +1.08 at 0.5, −0.05 at 1 SOL) |

What this says for other traders: our speed is not the limit. A trader that holds 2 seconds (about 5 slots) still
gets copied in and out inside its hold. What decides a copy is the price 4 trades behind it, our own size against the
pool, and whether its trades are still worth taking after that.

## 3. The model every candidate is scored with (`rescore2.py`, `ownrules.py`)

- **Our buy** fills on the pool after the 4th trade of the coin behind its buy (its own block, then the next blocks);
  **each of our sales** 4 trades behind each of its sales. The pool's curve, virtual reserves included, is fitted from
  its trades (a constant-product curve: every trade keeps (Q + a)(C + b) fixed); our own size moves the price on that
  curve. Pools that don't fit: the price the next trade on our side paid.
- **Checked against wallet 4's live buys** (`calib.py`, `calib1.py`; our own live trades left out of the counted
  sequence, the stake sized as it was live): on 13 buys at 0.1/0.5 SOL the model gives a median +17.7% (K = 4) and
  +17.0% (K = the trades really between) against +16.4% live (the refused three counted at the price they met); at
  1 SOL +13.6%, +13.6%, +7.3% (K = between) against +13.3%, +13.3%, +12.8%. About 1-2 points harsher than live.
- **Checked on another wallet's trips** (G7, 63 trips of 4vw54BmA): the model's K=4 price = 0.998x the chain's pool price
  after the 4th trade, and 1.002x what the next buyer really paid.
- **Costs:** 0.0095 SOL a transaction (buy + up to 3 sales) + 1.25% each way.
- **Its own rules:** per wallet, a grid of buy filters (all, quoted in SOL, in another token, its buy ≥ its median) ×
  take profit {1.3, 1.5, 2, 3, none} × stop {0.7, 0.8, 0.9, none} × timer {its median hold, 300 s, 1790 s, none} ×
  follow its first sale or not × **stake** {0.1, 0.25, 0.5, 1, 2 SOL, half its size, its size (cap 3)}. Prices between
  trades from GMGN 30 s candles; with no rule firing we mirror its sales.

## 4. The test (what wallet 4 passed)

1. Pick its rules and stake on days 1-4 (P1), score on days 5-7 (P2): **positive on P2, and positive without P2's best
   2 trips.**
2. Then every trip of the week (no sampling), and the week before (`END_DAYS_AGO=7`) with the same rules: positive again.
3. Holds no longer than wallet 4's (its 30-minute timer); no multi-day bags.
4. Enough trades to matter: wallet 4 gave about 2 copyable buys an hour.
5. A pass gets its own folder laid out like `rafinhaaaaaa/`, then paper, then 0.1 SOL live, as wallet 4 did.
