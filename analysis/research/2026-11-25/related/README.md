# Related wallets and where our wallets trade (Nov 25)

The owner: "I feel we have too few trades, please check every single wallet we have, if they have any other wallet
related trading with, on chain tracking". Helius (Enhanced Transactions and RPC), about 5,000 credits.

1. `r1_transfers.py` (`out/transfers.txt`): each copied wallet's plain SOL transfers of 0.05+ SOL (5 pages of TRANSFER
   transactions, newest first: one to three days for most), summed by counterparty. The one-off "out" transfers of
   0.5-3 SOL to many accounts are its own buys (pump.fun's curve is paid by a SOL transfer). The repeat two-way ones:
   CgyPomTG / Ag1azuQr (in 46.48, out 75.05, x63), 6nNzEg86 / EPp21PTD (17.42 / 16.38, x79), GqWfqfG6 / NiDu8Pdi
   (26.21 / 26.77, x40), HtHkKxYN / FZEX4GZ9 (10.33 / 8.46, x25), 6LwMLkCe / DeNcJZcQ (7.28 / 30.76, x24), CqCAzte8 /
   BHBEtpr6 (6.34 / 5.97, x21); plain sends: HtHkKxYN -> CosutyCy 20.00 (5.45 back), CgyPomTG -> GDQnERSc 16.79 (x4).
2. `r2_hubs.py` (`out/hubs.txt`): those accounts. All repeat two-way ones are closed accounts (no owner, 0 SOL) seen
   in Raydium LaunchLab and PumpSwap swaps: venue accounts, not people. ErmHTSod (paid by both GqWfqfG6 and HtHkKxYN) is a
   pump.fun program account. Two plain wallets: CosutyCy (13.35 SOL, trades LaunchLab and PumpSwap) and GDQnERSc (23.90
   SOL, PumpSwap only); HBbXwsQt (wallet 4) is a token account.
3. Their own results (`own_only.py`, `out/own_siblings.txt`): CosutyCy +3.50 SOL over 15 days, up on 7 (STOP);
   GDQnERSc no pump.fun curve trades (our history reader counts curve trades only). **No sibling worth copying.**
4. `r3_venues.py` (`out/venues.txt`): each wallet's latest swaps by venue (Helius's SWAP type; it does not list plain
   pump.fun curve buys, so it shows what is outside them). HtHkKxYN: 19 Raydium LaunchLab swaps in 24.5 h (8 buys of 0.5+
   SOL), 6 PumpSwap; CqCAzte8: 23 LaunchLab over ~11 days (3 of 0.5+); CgyPomTG: 12 PumpSwap, 8 LaunchLab (4 of 0.5+);
   3SiQo8MJ: 13 PumpSwap buys of 0.5+ in 9.3 h; 6LwMLkCe: 40 Jupiter, 11 PumpSwap in 9.7 h; 3XeFcZKS 26 PumpSwap in 4.4 h.
   **Part of the wallets' trading is on venues the units do not copy (LaunchLab, PumpSwap buys of graduated coins), and
   that the tape and the histories do not record.** Whether copying it would pay is not measured.
