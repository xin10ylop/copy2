# 01. Who wallet 4 is: H9kuqGKN

In short: wallet 4 (`H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg`) made **+355 SOL in 8 days** (Oct 19 to Oct 27),
positive every day. Most of it comes from pump.fun coins priced in **other tokens** (WBTC, PUMP, TTWO, CARDS,
xStocks ...), which the copy bot could not see. It trades one simple rule: one buy, then sell everything at **2.5x**,
**0.7x** or after **30 minutes**. About 10% of its trips reach 2.5x, and those carry all the profit. We trade it two ways:
strategy **A**, the long copy of its 1.5-SOL buys of other-token coins (paper, on Ohio), and strategy **D**, the copy
bot's copies of its SOL-coin launch buys (real money, Oct 26 19:36 to Oct 27 09:50 Beirut, now stopped).

| | |
|---|---|
| Address | `H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg` |
| Called | "wallet 4" (its number in check.sh and in the copy bot's `copy_more` list) |
| Found | Oct 26 evening, the second copy-target search (`analysis/research/2026-10-26/wallets2/`, docs/19 §11) |
| Copied live from | Oct 26 17:36 UTC (19:36 Beirut), launch buys only, by the copy bot (strategy D) |
| Paper long copy from | Oct 27 10:29 UTC on fra1, then Oct 27 16:11 UTC on Ohio (strategy A) |
| Its balance | 467.7 SOL on Oct 27 00:40 UTC, 569.5 at Oct 28 14:54 UTC. **No deposits since Oct 19** (the "+11.9 deposited" in the first version of this page was rent back from closing token accounts plus pump's holder-fee payouts); 5.0 SOL went out into a privacy pool on Oct 27 ([`07-rework-2026-10-28/wallet-check.md`](../07-rework-2026-10-28/wallet-check.md)) |

## 1. How it was found

The copy bot was looking for more wallets to copy beside him (operator 1, AHwJSnFN). The second search (Oct 26 evening)
scored every launch buyer on the fetched tapes and put eight candidates through the full process: their own trades
pulled, the exit picked on Oct 25 18:00 to Oct 26 06:00 UTC, scored on 06:00 to 17:15 (docs/19 §11):

| wallet | launch buys | exit | 1st half | 2nd half | verdict |
|---|---|---|---|---|---|
| **H9kuqGKN** | 79 | create + 9 | +1.89 | +0.48 (+0.017 a copy) | **passes**: positive at every hold (+3 .. +12) in both halves; our sale comes first on 76 of 79 |

- A *launch buy* is a buy in the coin's create slot or the next one (a *slot* is about 0.4 s).
- It does not fund the creators of the coins it buys.
- Its buys **after** launch on SOL coins lose for it (37 coins, −11.65 SOL, 6 wins), so the copy bot copies only its
  launch buys (docs/19 §11).
- Against what a copy keeps: on the SOL tapes (Oct 25 18:00 to Oct 26 17:40) it made +6.93 itself and +2.37 as a copy,
  among the best kept of the 30 top earners (docs/19 §11, `ownvscopy.py`).

Then the night of Oct 26 showed the real picture: check.sh had wallet 4 at **+24.56** itself and our copies at **−0.25**,
and most of its result was never in the copy bot's reach (docs/19 §13). That led to the 8-day study of where its money
comes from (`analysis/research/2026-10-27/h9long/`, docs/20), and to strategy A.

## 2. Its result (Oct 19 00:00 to Oct 27 00:40 UTC)

From its full ledger: 17,278 signatures since Oct 19, 16,845 landed. Every venue and quote counted. A coin sold for its
quote token is valued at that token's price at the time (`h9long/ledger.py`, h9long README):

| Where | Coins | Its net |
|---|---|---|
| Pump coins priced in another token | 3,056 | +278 |
| Pump coins priced in SOL | 1,439 | +28.9 |
| PumpSwap-only tokens (CARDS +13.5) | | +17.3 |
| The quote tokens it holds between trades | | +28.6 |
| **Total** | | **+355** |

The split by what we can copy (parts A to F) is in [`02-decomposition`](../02-decomposition/README.md).

## 3. Its rule

- **One buy, one sell of everything** (`trips.py`, `behave.py`, `exitrule.py`):
  - take profit when the curve price reaches **2.5x** the price its buy left;
  - stop at **0.7x**;
  - otherwise sell after **30 minutes** (77% of its trips end this way).
- **About 10% of trips hit the take profit and carry all of the profit.** Bigger buys hit it more often: its buys of
  1.5 SOL or more hit it 22.7% of the time on Oct 19-22 and 9.8% on Oct 23-27.
- **Buy sizes:** tiers of about 0.9, 1.13 and 1.5 SOL (median 1.1). On the coins strategy A copies, all 324 buys were
  1.45 to 1.55 SOL, typically 1.50, never more than 1.53 (docs/20 §1; session, Oct 28).
- **The price** on a pump curve is about 1/vt² whatever the quote token (vt = the curve's virtual token reserve), so a
  multiple of its entry price reads the same on a WBTC-priced coin as on a SOL-priced one.

## 4. How many coins it holds at once

Every position is held at most 30 minutes (`grid.py cap`, h9long README; session, Oct 28):

| What is counted | Usually (median) | 90% of the time | At most |
|---|---|---|---|
| All its coins | 89 | | 169 |
| Its 1.45+ SOL buys of other-token coins | 4 | 7 | 17 |
| Of those, the ones we can route (part A) | 2 | 4 | 11 |

On the 324 part-A buys, open at once when it bought (counting the new one): 1: 106, 2: 101, 3: 68, 4: 27, 5: 13, 6: 4,
7: 1, 8 or more: 4. A cap of 3 skips about 15% of copies, 4 about 7%, 5 about 3%. That's why strategy A runs with
`max_open = 4`.

## 5. What it pays

On its part-A buys (`grid.py cap`, h9long README):
- **Buy:** a median 0.0071 SOL fee, base plus priority (10%: 0.0035, 90%: 0.0134), and a 0.00107 SOL tip on 40-55% of
  them. That's about 0.5% of its 1.5 SOL. On Oct 27 it was typically about 0.005, and 0.02 at the top (PePEwjLD).
- **Sell:** a median 0.00001 SOL and no tip. Its sells come on a timer or at 2.5x, so it isn't racing anyone.

## 6. What changes over time (watch these)

- **Its rule changed on Oct 27** (checked on chain, `analysis/research/2026-10-28/fresh/` §2): on its 1.45+ SOL other-quote
  buys it sold early (before 30 minutes, neither at its 2.5x nor its 0.7x) on 3.5% of trips on Oct 19-22, 13.6% on
  Oct 23-27 and **49% on Oct 27-28**; only 39% ran to its timer (67% before). It still made +82 SOL in those 38 hours.
- **Its copyable buys are thinning:** 1.45+ SOL other-token buys a day 64, 78, 80, 77, 73, 56, 112 (Oct 19-25), then 35,
  32, and 11 in the 15 hours of Oct 28 (`wallet-check.md`, `perday.out`).
- **The edge is shrinking.** Its big buys hit 2.5x 29% of the time on Oct 19, and about 10% by Oct 27. On Oct 23-27 it
  made about +4 SOL a day this way, against +10 before (docs/20 §2).
- **It sells early more often.** In the paper run on Oct 27-28 it sold before 30 minutes on 8 of 20 copies (40%),
  against 3-6% in the Oct 19-27 data. Some were its stop in a crash; others were very fast (ChonQdJ8 after 7 s, DJXThGNt
  after 3 s at 1.99x). If this goes on for days, re-test on fresh data
  ([`03-strategy-A-long-copy/paper-run.md`](../03-strategy-A-long-copy/paper-run.md)).
- **Frenzy coins.** Some coins it buys double within seconds as other bots pile in: 6y9aDagF was 1.2x after 1 s and 2.0x
  after 2 s.

## 8. Where it came from, and who is around it (Oct 28, `07-rework-2026-10-28/wallet-check.md`)

- **Born Oct 17 19:22 UTC**: 39.52 SOL from a one-day test wallet (`8h5eizMg`), then 19.92 SOL from a public privacy
  pool. The same evening an 82-day bot wallet, `HxcdEi6C` (62,231 signatures since Jul 27, the same 1.0 / 1.5 SOL buys
  of other-token coins), stopped, put 60 SOL into the same pool and sent 229 SOL to exchanges. All three wallets use a
  durable nonce first and the same two exact tip sizes (1,067,000 and 1,010,000 lamports), which no other sampled wallet
  uses. **Wallet 4 is very probably its successor.** The pool hides the direct link on purpose.
- **One bot, no siblings, no leader, no wash trading:** it buys at the coin's create slot or the next (47 of 47 measured)
  at a median 1.08x the launch price; the buyer before it is a different wallet almost every time; it never created a
  coin and never paid any of the 4,594 creators of its coins. Fast launch buyers (`6anjqMeW`, 0.5 SOL) land in its slot or
  the next on 27 of 40 sampled coins: our fills come behind them.
- **Its infrastructure:** one tip a transaction (Helius 54%, Astralane 17%, Jito 12%, Nozomi 10%), a median block
  position of about 220 (no top-of-block lane), 2.4% failed transactions, its own transaction builder (no retail router).
- **Red flags:** hidden funding by design; the operator rotates wallets; 5 SOL back into the pool on Oct 27; the copyable
  flow down to a third. An alarm for it going quiet, and a successor scan by its fingerprint, are not built.

## 7. Reading check.sh for this wallet

- check.sh's per-coin "ITS NET" for wallet 4 is **wrong coin by coin**: a coin sold into its quote token shows its
  profit on the quote token's row (for example the PUMP, DJTU and DOGE rows). Only its total is right (docs/20 §1).
- check.sh's "not seen" means the copy bot did not see the buy: a coin priced in another token, or its first buy came
  after create + 1. "not watched yet" means before the wallet was added (Oct 26 19:36 Beirut).

## Sources

- docs/19 §11 (the search) and §13 (the Oct 26 night); docs/20 §1-2.
- `analysis/research/2026-10-27/h9long/README.md` and its scripts (`sigs.py`, `pull.py`, `ledger.py`, `groups.py`,
  `trips.py`, `behave.py`, `exitrule.py`, `grid.py`).
- `05-live/check-sh-2026-10-27.txt`; `05-live/long-paper-history-and-journal-2026-10-28.txt`.
- Session analyses of Oct 27-28 (positions at once, bet sizes, fees), recorded in the h9long README's last sections.
