# The bot's skipped buys of wallet 4 (Nov 18)

The owner's journal, Nov 15 13:00 - Nov 18 00:15 UTC (about 59 h): the bot copied 62 buys (30 paid with TTWO, 15 with
SOL through a route, 10 SPCX, 5 PUMP, 2 3NZ9JMVB) and skipped 187: **180 "its buy has no SOL value (paid in an unpriced
token)"**, 5 with no route (2 BPxxfRCX), 1 float under the stake, 1 under the fee floor. No "max_open" skip.

**The 180 unpriced skips** (`u1_match.py`, `out/u1_match.txt`), matched to wallet 4's own buys (178 of 180): **13 were
1.3+ SOL** at Jupiter's price of Nov 18 (USDC 3, GTA6ot7g 2, one each of A7bdiYdS, ERiM8NiC, pSo1f9nQ, Xs7ZdzSH,
B62fkmVt, GwZaMuX8, H2jKD3Pe); the other 165 were small (median about 0.5 SOL), under the 1.3 SOL floor anyway. So the
unpriced gap is about 5 copyable buys a day. Correction: the earlier estimate from the history's own valuation (Xsc9qvGR
6.4 big buys a day) was wrong; all 14 Xsc9qvGR skips were under 1.3 SOL.

**The SOL-priced coins** wallet 4 buys (59 of 1.3+ SOL in the same 59 h) are left out by design (`detect.rs`: `SolBuy`,
"not copied"): the copy loses on them (`docs/20-long-copy.md`, backtests −11.1 / −2.3; `02-decomposition/`). Not a gap.
