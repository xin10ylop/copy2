# Nov 8: Rafinhaaaaaa since the Nov 4 check, before going live

The owner's ask (Nov 8, 16:30 UTC): is it still running, and what would we have made since the last check? The owner
goes live tomorrow if all is good. Sources:

- its own transactions to Nov 8 13:42 UTC (`../analysis/nov04/flows.py`, `coins.py`);
- the backtest pipeline on Nov 4 18:05 → Nov 8 16:33 UTC (`../analysis/nov04/nov08.sh`, then `simslot.py`, `coin_slots.py`).

Rule: its buys of 5.0 SOL or more, 1 SOL, sold 300 s after our buy or right behind its first sale. Times UTC;
Beirut = UTC+2.

## The answers

| Question | Answer |
|---|---|
| Still running? | **It has paused.** Its last trade was a sale on Nov 6 at 22:47; then nothing for 42 hours. Its later transactions are other wallets' spam, plus two USDC transfers of its own. |
| Did it move? | **No new trading wallet.** It sent 50 USDC (Nov 7 16:24) and 8,400 USDC (Nov 8 13:39) to two fresh addresses. One fee payer (`G8QC9ACQ...`) swept both onward within a minute, which is how an exchange collects deposits: profit taken off. Its 472.58 SOL has not moved since Nov 6 (`out/balance.txt`). The helper `BwBWFMFX...` (`../04-check-nov04/wallets.md`) bought one coin in 14 small buys on Nov 6 and passed them to the main wallet; it has been quiet since Nov 7. |
| Its own result | +9.8 SOL on 11 coins by its own fills, Nov 4 18:05 → Nov 6 (`out/coins_nov04-08.txt`; the coin it bought with its helper is left out). |
| **Our copy** | **7 copies, −0.97 SOL** with our buy at the end of the slot after its buy; −0.16 at the old model (2 trades behind); −1.78 without the best 2 (`out/landing_by_slot.txt`). |

## Our copy, coin by coin

| Coin | Its buy | 2 trades behind | End of its slot | Slot +1 | Slot +2 |
|---|---|---|---|---|---|
| `HEb2dwDN` (Raydium CPMM) | 10.10 | −0.728 | −0.747 | −0.756 | −0.755 |
| `BpWuEs3x` (Meteora DBC) | 10.10 | +0.529 | +0.311 | +0.225 | +0.225 |
| `C57Woifm` (Raydium LaunchLab) | 6.10 | −0.361 | −0.437 | −0.485 | −0.458 |
| `2HtyE1W7` (PumpSwap) | 10.05 | −0.030 | +0.007 | −0.103 | −0.200 |
| `D6EPcNsX` (pump curve) | 6.10 | +0.781 | +0.826 | +0.579 | +0.557 |
| `A8GcRwoR` (Meteora DBC) | 6.02 | −0.207 | −0.228 | −0.290 | −0.309 |
| `4Ns9x1JC` (PumpSwap) | 10.05 | −0.142 | −0.135 | −0.141 | −0.122 |
| **Total (7)** | | **−0.16** | **−0.40** | **−0.97** | **−1.06** |

New since Nov 4: its swaps of **6 SOL** (6.02-6.10 with its tip). The 5.0 floor takes them.

## November so far

| Period | Copies | Slot +1 | Without the best 2 | 2 trades behind |
|---|---|---|---|---|
| Oct 4-25 (out of sample) | 45 | +11.48 | +3.32 | +17.38 (47) |
| Oct 25 - Nov 1 | 21 | +13.37 | +4.39 | +16.77 (22) |
| Nov 1 - Nov 4 18:05 | 8 | +0.18 | −2.30 | +1.99 |
| Nov 4 18:05 - Nov 8 | 7 | −0.97 | −1.78 | −0.16 |
| **Nov 1 - Nov 8 (7.7 days)** | **15** | **−0.79** | **−3.27** | **+1.83 (−1.53 without the best 2)** |

Our stop rule (`../README.md`, next steps): stop if a week out of sample turns negative without the best 2. **Nov 1-8
fails it**, at every landing. It still makes money by its own fills, which land first. A copy one slot behind it does
not, so far in November.

## What to do

- **Do not put SOL in tomorrow.** It is paused, and its last 15 copies lose.
- **Run the copier in paper** on the new box (`../../08-new-box/` §7). This costs nothing, and the journal shows
  where our quotes land (`lag_slots`) when it trades again.
- **Go to 0.3 SOL only if** it trades again and a week of its copies is positive at slot +1, also without the best 2.
