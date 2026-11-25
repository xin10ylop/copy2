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

**A bug in steps 1 and 4: with a type filter, Helius returns short pages; `r1_transfers.py` and `r3_venues.py` stopped
at the first short page, so they read one page (one to a few days), not five.** Their accounts and venues stand; their
counts are too low. `r4_venue_pnl.py` pages on (and follows Helius's "continue from" hint) to 14 days.

5. **Each wallet's own result by venue, 14-17 days (`r4_venue_pnl.py`, `out/venue_pnl.txt`;** Helius SWAP type, which
   mostly leaves out plain pump.fun curve buys; a coin counts under the venue of its first buy there, sold out only).
   Buys of 0.5+ SOL a day and its own result on them: HtHkKxYN PumpSwap 0.8 a day, -1.79 SOL (2 of 9 days up),
   LaunchLab 0.3, +2.59 (3 of 4); CqCAzte8 LaunchLab 0.1, +3.26 (2 coins); CgyPomTG LaunchLab 0.6, -8.14 (no winner in 11),
   PumpSwap 1 coin +12.10; 3SiQo8MJ Jupiter 0.3 (most of its 1,135 swaps move more than one coin); 6LwMLkCe PumpSwap 0.9,
   -8.21 (2 of 9); **3XeFcZKS PumpSwap 2.4 a day, +12.51 SOL on 23 coins (5 of 11 days up)**, Jupiter 0.5, +6.27;
   GqWfqfG6 PumpSwap 0.4, -8.25. **The venues the units don't copy add 0.1-2.4 buys a day a wallet, and on most of them
   the wallet itself loses.** Not worth a new venue copier now; 3XeFcZKS on PumpSwap is the one to re-check.
