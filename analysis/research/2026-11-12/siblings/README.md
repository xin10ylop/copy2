# Does wallet 4's operator trade from other wallets we could copy? (Nov 12)

**Answer: no other trading wallet found.** Three checks, all on chain through the Triton endpoint:

1. **Its fingerprint among everyone on its coins** (`fp_paths.py` → `fp_paths.out`). Every cached transaction on the
   222 routable coins wallet 4 bought Oct 28 - Nov 12 (31 minutes from its buy; `../../2026-10-31/since_stop/`):
   112,331 transactions by 16,326 fee payers. Wallet 4 tips exactly 1,067,000 or 1,010,000 lamports on 331 of its 444
   and starts all 444 with a durable nonce. **No other payer comes close:** 9 used one of those sizes once or twice
   (of 2-88 transactions), and only one of them uses nonces (`3bx6pJVD`), which on a closer look (`deep.py` →
   `deep_candidates.out`) tips 750,000 / 1,000,000 / 2,000,000 and never spends 0.3 SOL in a transaction: not it.
2. **Where its cash-outs go** (`cashout.out`, `dest.out`, `collector.out`). Wallet 4 sent 510 SOL (Oct 30) and 410 SOL
   (Nov 9) to `EXzuWDVba3BQL14UYxSbvz1pZwZNYHXbyQwMBQutPFey`, which swapped them through Jupiter into USDC, a wrapped
   Monero token (`WXMRyR...`) and two others, then sent 36,746 USDC, 210 SOL and the tokens to
   `9jxYUDN9DZd56BmULrMV7eRMwHc2VzMZwU7bKXFSyyug` (27 transactions, Nov 6-10). That wallet staked 40 SOL, swapped the
   rest and sent it out through a cross-chain bridge (the transactions signed by `DbjXAFab...`, the bridge's relayer).
   None of the three trades pump coins; lookalike addresses (`H9kuecgK`, `EXzujfNy`, `EXzuF8ZQ`, `9jxYVg4u` ...) sent
   zero-value transactions to each: address poisoning, not the operator.
3. **Its tip sizes on any coin** (`tipscan.py` → `tipscan.out`): the newest 1,000 payments to each tip account wallet 4
   itself paid; see the result there.

The Oct 29 search (`../../2026-10-29/wallets/`) found no other wallet with its trading edge either.
