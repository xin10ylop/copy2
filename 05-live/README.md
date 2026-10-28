# 05. Live: what ran, what it made, the raw outputs

In short: **strategy D** (the copy bot's launch copies of wallet 4) ran on real money from Oct 26 17:36 UTC to Oct 27
07:50 UTC. It netted **+0.1456 SOL** on 77 filled copies, or about **−0.43** counting the stuck coin 2RR6sfbi
(−0.57). **Strategy A** (the long copy) has only run on paper, **+2.4666 SOL** on 21 closed positions to Oct 28 15:31
Beirut (+1.57 at the backtest's costs; all of it 3 coins that graduated; `07-rework-2026-10-28/`). The copy bot as a whole lost **−5.13 SOL** over Oct 22-27. It is stopped, its server fra1 terminated, and its
remaining SOL returned to the owner's Phantom wallet.

## Files here

| File | What it is |
|---|---|
| [`check-sh-2026-10-27.txt`](check-sh-2026-10-27.txt) | `bash ~/check.sh` on fra1, Oct 27 11:45 Beirut, **exactly as pasted** (with the config edits run just before it). The copy bot's full view: totals, tip test, last 10 trades, by wallet, every launch buy of each wallet, open positions, the daily stop. Wallet 4 is section `== 4 H9kuqGKN`. |
| [`copy-bot-history-2026-10-28.txt`](copy-bot-history-2026-10-28.txt) | `history.py --root /root/fra1` on Ohio, Oct 28: the copy bot from fra1's backup (all time and since the start, by day), plus the long copy's paper book at fra1's shutdown |
| [`long-paper-history-and-journal-2026-10-28.txt`](long-paper-history-and-journal-2026-10-28.txt) | `history.py paper` on Ohio, Oct 28: the 22 paper positions, then the journal's skip / paper-buy / paper-refused / feed lines since Oct 27 16:00 UTC (the SSH reconnect banner removed) |
| [`stuck-coin-2RR6sfbi.md`](stuck-coin-2RR6sfbi.md) | **the stuck coin**: a D copy that graduated at our buy, 405 failed sells, −0.57 SOL, what was fixed |

## Timeline (UTC; Beirut = UTC+2 on these dates)

| When | What |
|---|---|
| Oct 22 00:21 | first trade in the copy bot's saved database (fra1's `state.db`): its own launch-buy rule (copy1 repo, strategies S1-S2) |
| Oct 25-26 | it moves to copies: him (operator 1) first, then `copy_more` wallets (copy1 repo) |
| Oct 26 13:00 | check.sh's window starts ("since the start", Oct 26 15:00 Beirut); wallet balance 1.7192 SOL |
| Oct 26 17:36 | **wallet 4 added** to `copy_more` at create + 9, 5% bound (strategy D live) |
| Oct 26 ~23:50 | wallet 4 at create + 12, 20% bound (`807939b`) |
| Oct 27 morning | the long copy (strategy A) installed on fra1 in paper mode |
| Oct 27 04:55 | **2RR6sfbi** bought (a D copy); its curve completes; sells start failing |
| Oct 27 07:50 | **daily-loss kill**: the day's marked-to-market loss −1.207 SOL ≤ −1 SOL stop; copy bot stops buying |
| Oct 27 ~09:40 | wallets 5 (CxyKYmQo) and 3 (JBokzLFR) removed from the copy config and erased from check.sh (`6c7a9a4`) |
| Oct 27 09:45 | the check.sh paste above (11:45 Beirut, right after those edits) |
| Oct 27 ~10:45 | the user raises the `[risk]` daily stop to 2 SOL and unkills; then stops `rugsnipe-hot` and `rugsnipe-guard` for good, and sells 2RR6sfbi by hand (0.029 SOL) |
| Oct 27 10:29 | the long copy's first paper trade on fra1 (PePEwjLD) |
| Oct 27 ~12:45 | every rugsnipe unit on fra1 stopped; nonce accounts closed; SOL withdrawn; backup made and copied to Ohio |
| Oct 27 16:11 | the long copy restarts in paper mode on Ohio |
| Oct 28 | fra1 terminated; the long copy keeps running on Ohio (paper) until the evening |
| Oct 28 17:58 UTC | the long copy starts in paper on the Frankfurt box (`fra-long`, this branch's code, `follow_its_sell = false`) |
| Oct 28 evening | Ohio terminated by the owner; its paper book after 13:31 UTC and fra1's backup are gone |
| Oct 28 18:34 UTC | the long copy goes **real at 0.1 SOL** on the Frankfurt box (wallet `E7KX1hcM...`, 1 open, daily stop 0.3); paper there ends |
| Oct 28 18:35:51 UTC | **the first real trade**: FUN1RZrj, our buy one slot behind its buy at the top of the block (3 coin trades between), take profit 3 s later, **+0.0927 SOL** on 0.1; the chain equals the journal (`03-strategy-A-long-copy/deploy-frankfurt.md` §6) |
| Oct 28 19:20:43 UTC | the second real buy, E3hauBDZ, **refused by the 25% premium floor** on chain (`ExceededSlippage`): same slot as its buy, 7 coin trades ahead of us had moved the price to 1.36x; cost 0.0004 SOL |
| Oct 28 19:28-21:22 UTC | four more real trades (EMJs7igZ +0.1028, GUcG2eK2 +0.0818, 6TrDECwR −0.0334 on the stop, JAckzYTT +0.1074), all checked on chain; **the evening: 5 closed, 4 won, +0.3513 SOL on 0.1 SOL stakes**, wallet 0.7 → 1.046 SOL (`03-strategy-A-long-copy/deploy-frankfurt.md` §6) |

## Money

- **The copy bot's wallet** went from 1.7192 to 0.3081 SOL over check.sh's window (−1.4110, every lamport in
  `stuck-coin-2RR6sfbi.md`). All time (Oct 22-27, `copy-bot-history`): 989 trades, 988 closed, 281 won; on the curve
  +2.4081, tips and fees −6.5287, 757 refused buys −1.00866: **NET −5.1292 SOL**. By day: Oct 22 −0.46, Oct 23 −1.88,
  Oct 24 −1.48, Oct 25 −0.54, Oct 26 +1.07, Oct 27 −1.85.
- **Withdrawn Oct 27** to the owner's Phantom (`4ZLrCvjc9X739dWrt2pvQ35rNcFDGU46YPFc4DQCkcVK`): 0.335094 SOL from the bot
  wallet and 0.0423 SOL from 40 nonce accounts (32 buy + 8 sell, 0.00106 each). Phantom then held **3.8498 SOL**. Both bot
  wallets are at 0. One empty token account for 2RR6sfbi keeps about 0.0015 SOL of rent.
- **The long copy's old wallet** (`24neU6qr...`) was never funded; its key was on fra1 only. **Its new wallet**
  `E7KX1hcMCXg9qUpGE5hXaotRTxv8itSbdo4b8LHmYbyc` (made on the Frankfurt box Oct 28) received 0.7 SOL from the owner's Phantom
  on Oct 28; 0.15 of it was swapped into WBTC (18,841 units). The 0.1 SOL test trades from it since 18:34 UTC.

## Reading check.sh (`check-sh-2026-10-27.txt`)

- **TRADING:** whether the bot buys, and why not (here, the daily-loss kill and how to clear it).
- **results since the start:** closed trades only. It leaves out open positions and failed-sell fees, which is why it
  said −0.76 while the wallet was −1.41.
- **TIP TEST:** our two tip bids (3.0M, 8.0M lamports) by wallet: copies, filled, failed, landed in its slot, net.
- **BY WALLET:** each copied wallet's own net (ITS NET) against our copies of it (OUR NET). Then where its net came from:
  coins we copied, skipped, didn't see, from before we watched it, and its failed transactions.
- **One table per wallet:** each of its launch buys. *the bot*: COPIED, skip: why, copied but not sent, not seen,
  not watched yet. *result*: filled, refused (the price bound: fee only), not landed. *landed*: in its slot or +N.
  *behind*: block positions after its buy. *held*: slots held.
- **For wallet 4, ITS NET per coin is wrong coin by coin** (a coin sold into its quote token shows the profit on the
  quote token's row, e.g. pumpCmXq, DJTu7vi8, DoGEV7LA). Only its total is right. The decomposition
  (`../02-decomposition`) reclassifies every row.
- check.sh needs fra1's live bot (journal, config, database), so it no longer runs anywhere. `history.py` (check mode)
  rebuilds its totals from the backup.

## Sources

The four files above; `deploy/bin/rugsnipe-check`, `deploy/bin/rugsnipe-trades` (check.sh's code);
`deploy/bin/rugsnipe-history`; session records of Oct 27-28 (the kill, the withdrawal, the backup, fra1's shutdown).
