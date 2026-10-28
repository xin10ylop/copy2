# Wallet 4's neighbours: who else buys its coins in the create slot or the next (Oct 29)

**Question.** Strategy A copies wallet 4 (`H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg`): 1.45+ SOL buys of pump coins
priced in other tokens, at the coin's create slot or the next, held up to 30 minutes. Which other wallets buy the same
coins that early, how big, how long they hold, and is any of them worth scoring as a second copy target?

**Status: in progress.** Results are filled in below as each step finishes.

## Data and assumptions

- **Coins:** the 856 coins of wallet 4's trips with a first buy of 1.45+ SOL in `fresh3/h9long` (Oct 19 → Oct 28 14:54 UTC):
  the 847 closed one-buy one-sell trips of `full_paths.py` (`_fpaths.json`: 741 priced in another token, 106 in SOL)
  and the 9 coins that graduated before it sold (`_gpaths.json`).
- **Why a new fetch.** `_fpaths.json` starts *after* wallet 4's buy (`getSignaturesForAddress(until = its buy)`) and is
  sampled above 40 transactions, so it holds neither the create slot nor the buyers ahead of wallet 4, and its rows
  carry 8-character prefixes only. `fetch.py` reads, for every coin, each transaction on the bonding curve from the
  create to slot `max(C + 3, S + 2)` (landed; failed ones up to `C + 1`), with full addresses. Wallet 4's own buy is
  known from its trips and is not re-read.
- **Create slot C** = the slot of the transaction that carries the coin's `CreateEvent` (found on every coin so far);
  **S** = wallet 4's buy slot. "Early" = a buy landed in slot C or C + 1. The create transaction's own trades (the
  dev buy) are left out.
- **Buy size in SOL** = K × (1/v_after − 1/v_before), v = the curve's virtual token reserves, with K calibrated on the
  same coin from wallet 4's buy: K = its SOL value / (1/vt_after − 1/vt_before). Check on the SOL-priced coins: K is
  1.0139× the curve's own 30 SOL × 1,073M tokens (wallet 4's SOL value includes about 1.4% fees), so sizes include fees
  the same way.
- **Hold** = time from its first early buy to its first sale of the coin: from the fetched window (complete to its
  end), then from wallet 4's path (`_fpaths.json`, by prefix; sampled above 40 transactions, so a sale can be missed),
  which ends at wallet 4's own sale. "Flip" = sold within 5 s. A wallet that has not sold by wallet 4's sale is counted
  as "held past" only where the path is complete.
- **Win** (an estimate, gross of fees): the average price of its first sale over its average early buy price > 1. When
  no sale is seen, the marginal price at wallet 4's sale over its average buy price (marked, `m`).
- **Frenzy** = other traders' landed buys in the 2 slots after its buy (b+1, b+2); wallet 4's own number on the same
  coins is the baseline.
- **Failed** = its failed transactions on these curves in slots up to C + 1, over all its transactions there.
- **Late** = coins whose wallet 4 buy is on Oct 27-28 UTC.

## Run order

```
cd analysis/research/2026-10-29/wallets/neighbours
python3 -I fetch.py                 # -> SCRATCH/wallets/neighbours/win.json (+ cache/, every response gzipped)
python3 -I rank.py 5 > out/rank.txt # every early buyer on 5+ coins, the top 15 by coins with 0.45+ SOL buys, the named four
python3 -I activity.py > out/activity.txt   # each listed wallet's newest 1,000 signatures, read at run time
python3 -I verdict.py > out/verdict.txt
```
SCRATCH = `/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad`. The RPC URL is read from the
old session's `month/.triton_url` (never printed or written here). `GAP` (seconds between calls) and `THREADS` set the pace.

## Results

(pending)
