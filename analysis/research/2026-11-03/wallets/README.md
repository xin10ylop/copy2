# Nov 3: the last untested wallets, without Triton

The wallet search's queues (the scratchpad `gmgn-out/final/`, the pipeline in `rafinhaaaaaa/analysis/final/`) still held
31 wallets with no result. All 31 were screened on Nov 3, 08:46-11:25 UTC, on the window Oct 27 08:46 → Nov 3 08:46 UTC.
The trades come from GMGN; the chain reads went through the public mainnet RPC instead of Triton (the owner's call).
The pipeline's RPC client, `rescore2.py`, now defaults to `https://api.mainnet-beta.solana.com`: it is archival and
serves version-1 transactions. Calls are spaced 0.28 s apart, and refusals (HTTP 429) back off. `USE_TRITON=1` restores
the old client.

**Result: none qualifies.** The qualified wallets are still wallet 4 and Rafinhaaaaaa.

| Result | n | Wallets |
|---|---|---|
| Dormant: no trades in 7 days, 0-20 GMGN trades ever (e.g. 7KTbFYUT's last transaction: Sep 14) | 19 | 7KTbFYUT HcSfDfGi 2dhubYdo EUuH8qkj F1daPktJ CVvJnDPc 9yGxZ43n F3a7jQ5d H8zBkUzu 56svZZLF 2Ux6d7Xc FfyLxGLJ H7D7jLCq HBhAU9J4 FmoS824x 82ujqioh 9g7T6sZX E9TB8WCE J6YEZsmT |
| The copy loses (the quick screen, Oct 31) | 7 | 3VUNtVtj, 8NVkytV1, AimUs5An, B1ZMARC6, GgbCFRHH, HB3Gebzs (−6.87 to −11.08 without the best 2); Dv32u9mv (11 trades, −3.58) |
| Coin launchers: they buy their own coins in the create transaction (pump `CreateV2`), so there is no pool to copy behind | 3 | 9ncm3Mfx (159 of 162 trades unpriced, "no pool"), CzbN6T1g, AqsW2qxw |
| Active on chain, few GMGN trades | 1 | DuQabFqd (1,000 transactions in 20 hours, 5 trades on GMGN) |
| Full test fails | 1 | 3i8rCH9v |

**3i8rCH9v in detail:**

- **Its own trading:** 4,598 trades in 7 days; first sale a median 6 s after its buy; its own trade's median +19.1%.
- **Its rule, picked on days 1-4:** coins priced in other tokens, take profit 1.3x, a 300 s timer.
  - Days 1-4: +2.43 on 27 trades.
  - Days 5-7: **−4.37 on 44 trades, −7.03 without the best 2**.
  - Landing 1, 4 or 7 trades behind instead of 2: days 5-7 −3.24, −7.17 and −5.82.
- **Simply following its sales:** −15.59 on days 5-7.

Sources: `gmgn-out/final/nov03.log`, `quick.log`, `final.log`, `out/sim_<wallet>.txt` in the session scratchpad.
The driver is `nov03.sh`.
