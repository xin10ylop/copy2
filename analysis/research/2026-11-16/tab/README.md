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

# Step 2: the full study (Nov 15 night; `fetch_more.py`, `paths.py`, `tab_study.py`, `out/tab_study.txt`)

    RPC_URL=... python3 -I fetch_more.py TXDIR OLD_SIGS.json SIGS.json       # 17,709 landed transactions, Oct 21 - Nov 15
    W=TAB16... FLOATS=<the five> cargo run -q --release -p rugsnipe-long --example scan -- $RPC_URL TXDIR "" 0.5 > scan_all.out
    RPC_URL=... LK=<tab/lk> python3 -I paths.py TXDIR SIGS.json scan_all.out   # 707 more paths (35 minutes)
    python3 -I tab_study.py PATHS scan_all.out W4SCAN 1.0 > out/tab_study.txt

**The data:** 890 copyable first buys of 0.5+ SOL with a path, **all of them from Oct 31 on** (nothing copyable in its
Oct 21-29 transactions): 15 days, 170 in block B and 720 in C. 0.5 SOL a copy, mean of three landings.

**What to copy (part 1, every copy):**
- **Size:** only its 1.3-1.6 SOL buys make money (192 copies, +6.93 SOL with the signals, +7.2% a copy, both blocks).
  Its 0.5-0.75 SOL buys, 493 copies and almost all since Nov 6, lose 3% a copy (−7.29); 1.6-2.0 SOL +0.04; 2-3 SOL −1.00.
- **Kind (1.0+ SOL):** WBTC +4.41 (58 copies, nearly all in block B), PUMP +2.29, SOL +2.21 (block B −1.23, C +3.44);
  TTWO −1.77, HYPE −1.21, SPCX −0.35. No kind is ahead in both blocks by much.
- **Shared with wallet 4:** 62 of the 364 buys of 1.0+ SOL (+1.81); the 302 it buys alone +4.08, +2.7% a copy, +0.42
  without the best 2.

**The exit (part 2; 364 buys of 1.0+ SOL, the bot's run; the noise of one change ±2.86 SOL):**

| setup | total, 15 days | w/o best 5 | losing days | worst day |
|---|---|---|---|---|
| its last live rule (tp 4.0, 600 s, its sale 0-60 s) | +4.60 | −3.56 | 8 of 14 | −1.60 |
| the same with wallet 4's two signals (the reference) | +7.83 | −0.29 | 5 | −1.12 |
| its sale never followed (press, stall, tp 4, 600 s) | +10.45 | +2.25 | 4 | −0.65 |
| its sale followed in its first 30 s only | +11.18 | +2.98 | 4 | −0.16 |
| wallet 4's frozen setup, untouched | +3.08 | −4.39 | 6 | −0.82 |

- **Its own sale:** followed over 0-290 s or at any time −8.65 / −9.10. With its sale never followed, by what it did:
  the 15 copies it sold at 1.5x or more after a minute make +10.75 SOL (+143% a copy, all won) and the 111 it had not
  sold +6.07; **the 86 it sold at 30-60 s under 1.5x lose −10.22 (−24% a copy, 6% won)**, and following it there does
  not save them (its own sale is what drops the price).
- **Take profit:** 2.0 −6.61, 3.0 −1.49, 5.0 +1.97, none +4.73, but nothing more without the best 5: a bet on a few runs.
- **Timer:** 180 s −6.61, 300 s −2.75, 450 s and up the same.
- **The signals:** neither −3.23 (8 losing days); the pressure rule alone +1.82 on the reference, +5.04 on "neither"
  (4 losing days); the stall adds nothing. **Wallet 4's `sell_pressure` rule works on a wallet it was never tuned on.**
- Walk-forward: the best on B makes +3.22 on C; the 10 best +0.69 on average, 8 of 10 ahead.

**What it adds to wallet 4 (part 3, without the shared coins):** the reference +5.60 SOL in 15 days, **+0.37 SOL a day
at 0.5 SOL on 18.8 copies a day, −2.52 without the best 5**, 5 losing days of 14. Wallet 4's backtest on the same
footing: about +3.1 SOL a day, +65.65 of +75.29 without the best 5.

**Verdict:** an edge of 2-3% a copy that disappears without its five best trades is inside what the model can get
wrong on a fill (its 14 real trades at 0.1 SOL lost 0.1665 SOL). Not worth real money now. Worth a paper run: the
unit `rugsnipe-long-tab` in `mode = "log"` with tp 4.0, 600 s, its sale followed in its first 30 s only, the pressure
rule, buys of 1.3+ SOL, for two weeks; it costs nothing and is the only evidence that is not this backtest.
