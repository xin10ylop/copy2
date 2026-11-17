# VIP hypothesis H1, frozen Nov 17 ~21:10 UTC, before its test data was fetched

Found by `tg_vip_scan.py` (5 survivors of 1,770 tests on 914 calls: a hypothesis, not a result).

- **Calls:** SolHouse VIP "New Solana Gem Alert", tier **Diamond**, the post's Age **above 0 and at most 1 minute**, pool
  Pump.fun (on the curve).
- **Trade:** buy at the first trade 1 s or more after the post (refused past 1.25x the post's price), 0.5 SOL; sell at
  2x our entry price or 60 minutes after the buy; no stop. A coin that graduates while held: 0.8x the curve's end price.
- **Test data:** the Diamond calls of that age in the VIP export that no script has priced yet (`vip_h1/`, the rest of
  `vip_rest` not fetched before this file). Same 8 days as the scan (Nov 10-17), other calls.
- **It passes only if**, on 150+ copies: the mean a copy is above 0 at 0.0345 SOL a round trip, the total without the
  best 5 is positive, and both halves of the days are positive. Otherwise it is dropped, with no second version.
- **If it passes:** the next test is out of time, on calls posted after Nov 17, before any size.

## Result (Nov 17, 21:30 UTC): FAILED, dropped

On its test calls (`vip_h1`, 215 fetched, 163 copies): **−21.3% a copy** at 0.01 SOL costs (−26.2% at 0.0345), won 31%,
halves −21.0% / −21.7%, without the best 5 −20.30 SOL (`vip_h1_result.txt`). The scan's +10.1% on 90 copies was one of
5 survivors of 1,770 tests: chance. The Nov 1-6 test (`vip_h1b`) was stopped at 40 of 297 calls (11 copies, −31% a copy)
once this one had failed. No second version.
