# TAB16RxX with wallet 4's method, step 1: what is already on disk (Nov 15 night)

The owner: "can we do all of that for the second wallet, I think doing a proper setup for it will result in it being
also very profitable and add trades". TAB16RxX = `TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3` (the unit
`rugsnipe-long-tab`, paused Nov 14 after 14 real trades at 0.1 SOL, −0.1665 SOL). Step 1 uses no new fetch: the 183
copyable 1.0+ SOL first buys of Nov 1-12 with a path (`../../2026-11-13/tab_exits/`: SOL 128, WBTC 55), 0.5 SOL, 2
open, mean of three landings.

    python3 -I tab_now.py PATHS SCAN W4SCAN > out/tab_now.txt     # PATHS = tab/lk/paths, SCAN = tab_exits/out/scan_tab.txt, W4SCAN = allq/scan.out
    python3 -I overlap.py PATHS SCAN W4SCAN > out/overlap.txt

- **Its edge is small and rests on a few trades.** Its last live rule (tp 4.0, 600 s, its sale followed 0-60 s): +7.61
  SOL in 12 days (halves +2.80 / +4.81), +3.83 without the best 2, **−0.50 without the best 5**, 4 losing days of 10.
  Wallet 4 on the same measure: +75.29 in 24 days, +65.65 without the best 5, 3 losing days of 24.
- **Wallet 4's frozen setup, untouched, does worse on it:** +2.86 (−4.75; redrawn days [−11.7, +1.7]). The reason is
  one part: its own sale. TAB16RxX sells almost every coin within minutes (94 of 172 copies have its sale at 30-290 s
  under 1.5x), so its sale is routine, not the "it gave up" message wallet 4's is; following it there loses 16% a copy.
  With its sale followed only at 0-60 s, the same setup makes +8.36; never followed +7.03.
- **The two signals:** +0.75 on top of its live rule (noise at this size); +1.90 on the 30-290 s variant.
- **It does add trades:** wallet 4 bought the same coin with 1.3+ SOL within 30 minutes on 35 of the 183 (30 in the
  same slot). Those 35 make +0.24 SOL; the 148 it buys alone make +6.54 (+8.8% a copy, +2.85 without the best 2;
  `out/overlap.txt`, every copy).
- **What the floats would add** (the scan rerun with PUMP, SPCX, TTWO, DJT, HYPE): 274 routable at 1.0+ SOL (192
  before), 530 at 0.5+; 600 of its buys stay unpriced (paid in tokens with no SOL value in the event).

Step 2 (not run: a large Triton fetch): its transactions since Nov 13, the paths of the float-paid and the smaller
buys (about 440 coins), then the same study as wallet 4's: sizes, kinds, exits one part at a time, the noise, walk-forward.
