# Study brief: skip losing copies without skipping the big winners (Nov 15)

Two researchers get this same brief and work alone. Write everything into your own folder
`analysis/research/2026-11-15/skip_filters/<YOUR NAME>/` (the name is given to you with this brief). **Do not read the
other researcher's folder.** Do not `git commit` or `git push`; do not change any file outside your folder. This repo
is public: never print, log or write the RPC URL (read it from the file below; pipe any error text through
`sed -E 's#https?://[^ "]*#<rpc>#g'`), no keys, no IP addresses.

## The question (the owner's words)

"A very digged deep study, on how we may skip some losing copies without skipping the big winning trades."

## Context

We copy one wallet ("wallet 4", `H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg`) on pump.fun coins priced in other
tokens. When it buys 1.45+ SOL of a coin we can route to, our bot buys 0.5 SOL of the same coin in the same block, a
few trades behind it, paying with SOL (through a pool) or with a token we hold as a float (WBTC `3NZ9JMVB...`, PUMP
`pumpCmXq...`, SPCX `SPCXxcqX...`). **The live exit rule:** sell everything at 3.0x the price its buy left; else
sell behind its own sale when that comes 30-290 s after its buy while the price is under 1.5x; else sell at 600 s. No
stop. At most 2 copies open (at most 1 from SOL, PUMP and SPCX each, 2 from WBTC). The buy is refused when our price
would be over 1.25x the price its buy left.

In the backtest about 1 copy in 9 reaches 3x and those make all the profit; most of the others lose 10-40%. Over 23
full days: +37 SOL at 0.5 SOL a copy, 4 losing days, worst day −1.31. The owner wants fewer losing copies **without
losing the winners**. Read first: `analysis/research/2026-11-14/float_exits/README.md` (the exits, the unseen week, the
model against real trades), `analysis/research/2026-11-15/steady/README.md`, `analysis/research/2026-11-15/partial/README.md`.

## Data (already fetched; local files)

`SPD=/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/floatq`
- `SPD/w4tx/<slot>_<sig12>.json`: every landed transaction of wallet 4, Oct 21 18:30 UTC - Nov 15 (RPC `json`
  encoding; about 52,000 files).
- `SPD/scan_hops.out`, `SPD/routable.json`: its 1.45+ SOL buys with the bot's own route verdict (what we pay with,
  hops); `SPD/prices.json` (lamports per raw unit of the tokens it pays with).
- `SPD/paths.json.gz`: for each copyable buy, every trade of the coin from its buy's slot to 31 minutes later, in
  block order: `{ "<slot>_<mint8>": [mint, [ {slot, t, sig, user, buy, q, tok, vt, vq, bps, real}, ... ]] }` (`q` =
  quote amount, `vt` / `vq` = the curve's virtual token / quote reserves after the trade, `bps` = fee, `real` = real
  tokens left, 0 = graduated). The price multiple at a trade is `(vt_ref / vt) ** 2` with `vt_ref` = `vt` after wallet
  4's buy. **A path starts at its buy's slot: nothing before that slot is in it.**
- The copy model: `analysis/research/2026-11-14/float_exits/lib.py` (`load`, `prep`, `model`) and `float_exits.py`
  (its `sim` runs the bot with its slots). Minimal use:

```python
import os, sys, datetime
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp(); os.environ["FE_T0"] = str(T0)
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); sys.argv = ["x", SPD, "0.5"]
import float_exits as F, lib as L          # F.rows (781 buys: slot, mint8, t, sol, anchor, hops, how, key), F.P, F.PREP[key, landing]
RULE = dict(tp=3.0, hold=600, early=(30, 290, 1.5), sl=None)
CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
res = F.sim(F.rows, 4, RULE, caps=CAPS)    # [(row, net SOL, why)] at landing 4; landings: L.LAND = (4, 8, "slot+1")
net, why, held = L.model(F.PREP[row["key"], 4], 0.5, **RULE)   # one copy, no slot limit
```
  Importing `float_exits` takes about a minute and a few GB of memory; the machine has 15 GB and 4 cores and others
  are using it, so load it once per script and avoid more than 4 worker processes.
- Wallet 4's own transaction for a buy is the file in `SPD/w4tx/` whose name starts with the row's slot (match the
  coin by the mint prefix in `meta.postTokenBalances`).
- You may fetch more (a coin's history before the buy, its creator, its holders ...) from the Triton RPC whose URL is
  in `/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/month/.triton_url`. Cache
  every response under `/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/skipq_<YOUR NAME>/`,
  at most 12 requests at once, and only what a filter needs.
- Real trades to check against (the bot's journal, `status --chain`): coin prefix, our net in SOL, exit:
  Ci9Bg1Bx −0.0597 time; BttUQVPM −0.0455 time; 5tePJcGm +0.3531 tp; 7dDprVHP −0.1106 time; 57pQW4mw −0.0124 time;
  Eymbsj8M +0.6228 tp; GZn6HC8d −0.3763 time; GaHAZThn −0.1884 time; 3EKoHX4f −0.0600 time; 6S3iL67j −0.0907 time;
  BUdiaswB +1.3340 tp; GLmWEbqA −0.2837 time; 3a8RGrQg −0.2201 time; BTCmcoKg +0.5786 tp; FAVdiH3q −0.0851 time;
  KgcdZjU4 −0.2493 time; oxbezHbo −0.4291 its sale; EH6yuh4Y −0.4260 time; 4TMzhGzY −0.0310 its sale; 6KpdMXAS −0.2420
  its sale; DHcZRxRX −0.1991 time; 8FE3SQjW −0.0924 its sale; 4A7n9wq8 −0.0703 its sale; BURn1o8x +0.6038 tp (stakes
  0.1 to 1 SOL, older exit rules on the first ones).

## What counts as an answer

1. **Rules the bot can apply at the moment it sees wallet 4's buy** (or, at the latest, at our own fill): only things
   known then. No look-ahead: nothing from after its buy except the trades that land before ours in the block.
   Examples to test, and go further: its buy's size and its size against its own recent buys; what it paid with and
   the route; the coin's curve state at its buy (how far along, reserves, the fee tier `bps`); how much its buy moved
   the price; what else traded in that block before and right after it; the coin's age and history before its buy;
   the creator; the hour and day; wallet 4's own state (how many buys in the last minutes, its results on its last
   coins, a second buy of the coin); our entry premium and the refusal limit; the coin's quote token.
2. A second, separate part if it helps: **bailing out in the first seconds** (a rule on what happens in the first
   10-60 s after our buy) counts as "skipping a loser" only if it is reported apart from the entry filters.
3. For every candidate filter report, on the bot's run (the slots matter: a skipped copy frees a slot): copies kept
   and skipped, **take profits kept and lost** (and the 20 biggest wins kept and lost), losing copies skipped, total
   net, net without the best 5 and best 10 trades, losing days, worst day, deepest fall; all three landings.
4. **Guard against overfitting, hard:** three blocks, A = Oct 21 18:30 - Oct 29 12:02 UTC, B = to Nov 6 05:32 UTC,
   C = after. A filter counts only if it helps in each block (or is picked on two and holds on the third, every way
   round). Say how many filters you tried. Prefer filters with a reason behind them and a smooth threshold over a
   lone sharp cut. Redraw days with replacement to say how sure the gain is. Check the filter on the real trades
   above (which would it have skipped?).
5. If nothing holds up, say so plainly; that is a valid result. If something does, give the exact rule, what it costs
   in winners, and what the bot would need (a config value, or new code and which data it needs at decision time and
   whether that data is available within milliseconds).

## Deliverables in your folder

- `README.md`: the answer first (yes or no, the rule or rules, the numbers), then the evidence in short tables, then
  the run order. Plain words, short sentences.
- The scripts (each with a header saying what it does and how to run it) and their outputs under `out/`.
- Every number in the README must come from a script output in `out/`. Do not invent numbers. Say what you did not
  test.
