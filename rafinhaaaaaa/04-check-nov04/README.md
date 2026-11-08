# Nov 4: Rafinhaaaaaa checked again before the copier goes live

The owner's ask (Nov 4): leave wallet 4 to the other session, focus on Rafinhaaaaaa and get it right. Sources:

- its own transactions from the chain (public RPC, Oct 25 00:00 → Nov 4 17:41 UTC);
- the backtest pipeline of `../analysis/final/` (GMGN trips, the chain's blocks), re-run for Nov 1 00:09 → Nov 4 18:05;
- Jupiter's free API, asked from this session.

Times UTC; Beirut = UTC+2.

## The answers

| Question | Answer |
|---|---|
| Still trading? | **Yes.** 577 transactions since Oct 25; it traded every day but Nov 1. Since Nov 1: 12 coins, **+57.0 SOL by its own fills**, +40.7 of it on one coin (`out/coins_nov01-04.txt`). |
| Did its rule change? | **Not in a way the data can show.** Its swaps are still 3, 5 and 10 SOL; since Nov 1 more of them are 3 SOL (10 of its 20 buys; 9 of 5 SOL or more). Its holds are as before: in Oct 4-25 already, 13 of its 49 first sales came within 2 s (`out/by_day.txt`). |
| Our floor | **5.0 SOL, not 5.1.** The 5.1 floor was picking its buys by its tip (below). |
| Would the copy have made money since Nov 1? | **About nothing:** 8 buys of 5.0+, +1.99 SOL two trades behind it, **+0.18** with our buy at the end of the slot after its buy, −2.30 without the best 2. Eight trades say little either way. |
| Does it matter how fast we land? | **Yes, it decides it** (the landing table). |
| Can Jupiter trade its coins? | **Yes:** a real 1 SOL swap built and simulated on 14 of 16 coins (every venue it uses), and coins 2-20 s old are quoted (`out/swap_simulations.txt`, `out/fresh_probe.txt`). |
| Is the copier's live code safe? | **Now, yes for what was found.** An independent review found three bugs that could leave unsold coins or book a false loss; all are fixed and tested (`../../docs/21-copier.md` §2). |

## Its sizes are swap + tip: the 5.1 floor was a tip filter

Every buy since Oct 25 (`out/sizes_and_tips.txt`; whole SOL change = swap + tip + fee):

| It swaps | Tip 0.045 SOL | Tip 0.1 SOL | Tip 0.6 SOL |
|---|---|---|---|
| 3.0 SOL | reads 3.05 (10 buys) | reads 3.10 (5) | — |
| 5.0 SOL | reads **5.05** (9) | reads **5.10** (8) | — |
| 10.0 SOL | reads 10.05 (4) | reads 10.10 (17) | reads 10.80 (3) |

So "5.1 SOL or more" meant "its 5 SOL swaps when it tipped 0.1, and its 10 SOL swaps". It used the 0.045 tip more
often from Nov 2, so the old floor skipped most of its 5 SOL buys, its +40.7 SOL coin among them. A 5.0 floor takes
all its 5 and 10 SOL swaps (`out/floors.txt`, 1 SOL, two trades behind it):

| Floor | Oct 4-25 (out of sample) | without the best 2 | Oct 25 - Nov 1 (the rule's week) | without the best 2 | Nov 1-4 | without the best 2 |
|---|---|---|---|---|---|---|
| 5.1 | +14.91 (35) | +6.75 | +16.45 (19) | +6.71 | +0.20 (3) | −0.51 |
| **5.0** | **+17.38 (47)** | **+9.22** | **+16.77 (22)** | **+7.02** | +1.99 (8) | −1.37 |
| 2.9 (its 3 SOL buys too) | +17.26 (76) | +8.53 | +16.22 (32) | +6.48 | not fetched | — |

The 5.0 floor is chosen for the reason above, not by these results; it is better in both earlier periods. Taking its
3 SOL buys too adds trades and nothing else. No copy overlaps another at 5.0 once ours sells behind its first sale, so
one position at a time loses nothing.

## How fast we land decides it

The old backtest placed our buy and our sale K trades behind its own. The copier asks Jupiter for a quote and a swap
before it sends (0.35 s from here: quote 0.16 s, swap 0.18 s, `out/quote_then_swap.txt`). So it lands about a slot
later than the long copy did live (47% in its slot, 53% the next). `addslot.py` prices our buy and our sale at the
**end** of a slot instead: after every trade on the pool in its slot (slot +0) and in the n slots after it. Landing
inside slot +n lies between the +(n−1) and +n columns. Same pricing, costs and exits as before
(`out/landing_by_slot.txt`, floor 5.0, 1 SOL):

| Period | 2 trades behind | End of its slot | End of slot +1 | End of slot +2 | End of slot +3 |
|---|---|---|---|---|---|
| Oct 4-25 | +17.38 (47) | +17.20 (45) | +11.48 (45) | +5.66 (43) | +5.44 (42) |
| without the best 2 | +9.22 | +8.50 | **+3.32** | **−2.33** | −2.54 |
| Oct 25 - Nov 1 | +16.77 (22) | +18.88 (22) | +13.37 (21) | +9.70 (19) | +5.24 (17) |
| without the best 2 | +7.02 | +7.49 | +4.39 | +2.25 | +0.71 |
| Nov 1-4 | +1.99 (8) | +1.50 (8) | +0.18 (8) | −0.20 (8) | −1.35 (7) |
| without the best 2 | −1.37 | −1.44 | −2.30 | −2.37 | −2.79 |

On the same trips at every landing (the second block of each period in `out/landing_by_slot.txt`) the decline is the
same: Oct 25 - Nov 1, 18 trips, +16.38 → +11.55 → +9.26 → +5.24. A slot of delay costs 0.13-0.27 SOL a trade.

- **Landing in the slot after its buy:** the rule holds in both earlier periods, also without the best 2.
- **Two slots after:** it is luck on Oct 4-25 (negative without the best 2).
- **Where the copier lands is not measured yet.** It reacts to its buy as the long copy did, plus 0.35 s of HTTP, so
  most likely in slot +1 or +2. The journal now records it (`its_slot`, `our_slot`, `lag_slots` on every buy and sale;
  paper: the slot Jupiter's quote was priced on, live: the slot our swap landed in). The runbook's first live hours at
  0.3 SOL decide it (`../../08-new-box/` §8).
- **The way to land sooner** is to build its main venues' swaps ourselves, as the long copy does for pump: the pump
  curve and PumpSwap (31 of its 79 buys of 5.0+ since Oct 4, the builders exist), then Meteora DBC (26 of 79). Not
  built.

Per coin since Nov 1 (`coin_slots.py`): its +40.7 coin `Bj3zX42q` gives us +1.89 two trades behind and +1.38 at slot +1.
We sell behind its first sale, 6 s in, and it sold 17 times.

## Jupiter on its coins

- **Swaps simulated** (`simswap.py`; Jupiter's real swap as the copier asks for it, 1 SOL, the 0.001 SOL Jito tip
  inside, paid by a funded wallet that never held the coin, simulated on mainnet): 14 of 16 build and run without
  error (10 of its 12 coins since Nov 1, and 4 coins trading at the time). That covers the pump curve, PumpSwap, Meteora DBC, DAMM v2, Raydium CPMM, and a route through Manifest. They
  use 37,000-92,000 compute units. The 2 others come back `TOKEN_NOT_TRADABLE`. One is a Token-2022 coin with a
  transfer hook (Jupiter never trades those; a 1.07 SOL buy, not a copy). The other is a dead test coin ("testing
  testing", one holder left), asked hours later. Sales were not simulated: the public RPC refused the holder lookups
  (429). A sale is the same swap the other way, on the same pools.
- **Fresh coins** (`fresh_probe.py`, Nov 4 18:00-18:04): of 154 coins quoted 2-20 s after their first pool, 151 had a
  route (3 had none yet, at 2.8, 5.9 and 15.6 s); 12 more asks were refused (429). A quote takes 0.17 s (p50).

## The copier's code (review and fixes)

An independent review of the live path (`mode = "on"`, never run) found, and this session fixed:

| Found | Fix |
|---|---|
| A buy that landed could be journaled as failed (its transaction not readable in 5 s, or the status read at processed) and its coins never sold | wait for confirmed; a confirmed or unknown buy is booked from the wallet's balance when its transaction cannot be read |
| A zero balance read (a node a few slots behind, or a sale that landed while its wait failed) closed the position at −1 SOL | the zero is read again at confirmed, and our own transactions are searched for that sale before closing |
| A coin that cannot be sold held Rafinhaaaaaa's only slot forever | after 20 failed sales it is stuck: retried every 5 min, its slot freed, counted as lost in the daily stop |
| A buy queued behind a slow swap was copied late, into its sale | skipped when more than 10 slots behind the feed (`max_lag_slots`) |
| A swap was sent once | re-sent every 2 s until it lands or expires; not sent when Jupiter's own simulation failed or we are not the fee payer |
| Also | its sale closes every matching position; a failed state write is printed; `copy-replay` no longer writes the service's journal and state |

Not changed: the coin account's rent (about 0.002 SOL a coin, booked as cost), the one thread (a sale seen during a
swap's wait is acted on after it).

**The wallet's balance is a stop too:** a buy needs the stake + 0.05 kept + the tip, so 1.2 SOL for 1 SOL stakes
stops buying after about −0.15 SOL. Fund the copier wallet with the stake + the daily stop + 0.1: **1.6 SOL**.

## Run order

The scripts are in `../analysis/nov04/`. `SPX` is a scratch folder. `addslot.py`, `simslot.py`, `venue_split.py`,
`coin_slots.py` and `nov05.sh` run in the `analysis/final/` scratchpad folder: they import `reprice.py` and its
helpers, and read `chain/` and `paths/`.

```
python3 -I sigs.py Hn6vBWWySnxA8XjxRQDEmZEuH5QL7KqosnJGcLcUzFJ6 1792886400 SPX/sigs.json   # its signatures since Oct 25
python3 -I txsp.py SPX/sigs.json SPX/tx 5                       # its 569 landed transactions
python3 -I behav.py SPX/tx SPX/rows.json > out/by_day.txt       # its buys and sales by day (rows = ../data/<wallet>/chain_rows_oct25-nov04.json)
python3 -I coins.py SPX/rows.json 1793491797 > out/coins_nov01-04.txt
bash nov05.sh 1793815529                                        # the backtest pipeline on Nov 1 00:09 -> Nov 4 18:05 (GMGN key)
python3 -I addslot.py s3q2/WALLET.json 3 5.0                    # slot landings; also .oos3w.json and .nov05.json
FIXRULE="buy>=5.00|None|None|300|1.0" python3 -I simslot.py s3q2/WALLET.json      # SAME=1: the same trips at every landing
FIXRULE="buy>=5.00|None|None|300|1.0" python3 -I sim_g1.py s3q2/WALLET.json       # the floors (5.10 / 5.00 / 2.90)
python3 -I coin_slots.py s3q2/WALLET.nov05.json                 # per coin at every landing
python3 -I fresh_probe.py 240 SPX/fresh_probe.json              # Jupiter on coins 2-20 s old
python3 -I simswap.py PAYER MINT...                             # PAYER: any funded wallet; simulated, nothing sent
python3 -I burst.py PAYER                                       # a quote then its swap, back to back
```
