# Nov 4 evening: did Rafinhaaaaaa move to another wallet?

The owner's ask (Nov 4, about 21:00 UTC). Sources:

- its own 591 transactions, Oct 25 00:00 → Nov 4 20:37 UTC (public RPC; `../analysis/nov04/flows.py`);
- the wallets it moves SOL with (`linked.py`, `side.py`).

Times UTC; Beirut = UTC+2.

## The answer

**Not moved: its main wallet still trades and still holds its money. But a new wallet with its exact fingerprint started
trading at 20:15 tonight, funded from its money.**

| | |
|---|---|
| Main wallet `Hn6vBWWy...` | Bought 5 coins on Nov 4 (6 buys, 16:43 to 18:58), last sale 20:11, last transaction 20:37. Holds **461.1 SOL + about 8,523 USDC**: at 20:28 it changed 90 SOL into USDC (70 through Jupiter's RFQ, 20 through Jupiter). Its balance by day: Oct 25 516 → Oct 26 89 (parked) → Oct 29 487 → Nov 3 536.5 → Nov 4 461.1. |
| New wallet `BwBWFMFXBQx9yRJteFW5y6jVsMGWeURKXwg3GjLNgxNV` | Created Nov 3 12:45:21, funded with 23.079 SOL from `Ax6kRBe8` and 27.114 SOL from `Grze52kd`, in the same minute the main wallet sent each of those 20 SOL. On Nov 4 at 17:18-17:19 it funded the 4 side wallets (4.32 SOL each). **At 20:14-20:16 it bought one coin (`4W9nejfS`, PumpSwap) three times: 5.048, 5.045 and 1.045 SOL, through the Axiom router with a 0.045 SOL tip.** That is the main wallet's setup: a 5 SOL swap plus its 0.045 tip reads 5.05. It sold at 20:23 (+4.99 SOL). 28.75 SOL left, 18 transactions in all. |

So far it is one coin in one hour. It may be a second wallet run beside the main one, or the start of a move.

## The wallets around it

| Wallet | What it is | Now |
|---|---|---|
| `8Y73DUNGmT2mQJMXf2jALYA2qsjvK5YTNuwMgaWo1yhc` | A parking wallet: 516 SOL out on Oct 26 03:41, then back and forth, 1,264 out / 1,271 in, all back by Oct 29 | 0 SOL, quiet since Oct 29 17:09 |
| `F1u7GNFd...`, `HLJasqj9...`, `2XKszG74...`, `7CyCtLfk...` | 4 side wallets, all created Oct 13 13:50 in the same minute; Axiom trades on Meteora DAMM v2 and DBC. On Oct 23 they sold coin `B52GDsR1` that was sent to them. On Nov 4 at 18:52:37 they bought coin `BpWuEs3x` (1.2-1.5 SOL each), 10 s before the main wallet's 10.1 SOL buy of it. At 20:11:26 their coins left them, and 4 s later the main wallet sold 85.3M of the coin, 38.6M more than it had bought. At 20:12:04 they sent their SOL to the main wallet (2.85-3.09 SOL each) | 0 SOL each |
| `Ax6kRBe88NErj6oCK9KBE9aG3cep2b9W5Uh1Ztmco7sU` | Active since May; got 127.6 SOL from the main wallet on Nov 2-3 and sent 65.4 back | 11.95 SOL, quiet since Nov 3 14:28 |
| `Grze52kdfP5cxZvB6RXb3r15g6SafjdSg9fTrKLSWv6X` | Active since March; its own trades go through the Axiom router with a 0.045 tip, on Meteora DAMM v2 | 4.05 SOL, quiet since Nov 3 12:47 |
| `6mox95bj...`, `8ht8K97u...`, `Cs6vrQJZ...` | One-off payments out: 30, 4.24 and 4.49 SOL | — |

**Address poisoning.** `8Y7hNU8B...1yhc`, `Ax6kTPS8...o7sU`, `Grze4juv...Wv6X`, `2XKsJnRT...tzCr`, `7CyC8BaF...2xFv` and
`BwBLS5vV...gxNV` copy the first and last characters of the wallets above, and send the main or the new wallet 0 SOL
or 0 USDC. That is spam aimed at a mistyped copy-paste, not the operator.

## What it means for the copier

- The copier follows the main wallet only. If the main wallet goes quiet and the new one keeps trading, our copier
  sees nothing.
- The copier takes several `[[target]]`s. Adding `BwBWFMFX...` is one more block with the same rule (5.0+ SOL, 1 SOL,
  300 s or behind its first sale, `max_open = 1`). Not added yet: one coin is not a record.
- Check again in a day: what each of the two wallets trades, and whether the main wallet's SOL or USDC leaves.

## Run order

```
python3 -I flows.py TX_DIR Hn6vBWWySnxA8XjxRQDEmZEuH5QL7KqosnJGcLcUzFJ6     # its SOL transfers and balance by day
python3 -I linked.py ADDR...                                              # each wallet: SOL now, activity, its trades' fingerprint
python3 -I side.py ROWS_JSON ADDR...                                      # a wallet's trades beside the main wallet's
```
