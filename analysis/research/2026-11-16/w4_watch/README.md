# The daily check on wallet 4 (from Nov 16)

The owner: "track him every day, if he is using a new wallet". Run order (`SPD` = the float study's data folder):
```
python3 -I ../../2026-10-31/since_stop/fetch_w4.py SPD/w4tx "<yesterday> 00:00"    # its newest transactions (Triton)
python3 -I w4_watch.py SPD 10 > out/w4_watch_<date>.txt     # gaps, balance, buys and results by day, money moved out
python3 -I dest_check.py <address prefixes> > out/dest_check_<date>.txt          # who received it, if anything new
```

## Nov 16 (checked Nov 15 16:15 Beirut; `out/w4_watch_nov16.txt`, `out/dest_check_nov16.txt`)

- **Still the same wallet, still trading.** Its last transaction 3 minutes before the check; no gap of 3 hours or more in
  10 days. Coin buys a day 497-1,623 (Nov 5-14), 582 on Nov 15 to 16:12; its 1.45+ SOL buys 75 on Nov 14 and 39 on
  Nov 15 to 16:12, against 103-216 a day on Nov 5-13 (tokens at today's price).
- **Its money:** 45.90 SOL and tokens worth 219.4 SOL (USDC 124.9 SOL of it), at SOL $72.20.
- **Money out, last 10 days:** Nov 9 03:17 Beirut 410 SOL, Nov 13 03:46-03:58 15,200 USDC, all to `EXzuWDVb...` (its
  cash-out wallet since Oct 30). `EXzuWDVb` passes it on: to `9jxYUDN9DZd56BmULrMV7eRMwHc2VzMZwU7bKXFSyyug` (created Nov 6,
  27 transactions, 5.94 SOL, its USDC and other tokens; no pump trade in its last 30) and to `FV1Uw92p...` (6
  transactions, all paid by `EXzuWDVb`: a pass-through). **No trading wallet among them: no successor.**
- **Its own result per coin by day** (every coin of 0.05+ SOL it closed, all sizes): −5.4% to +6.4%, near zero; the
  copy depends on the few coins that run, not on its average.
