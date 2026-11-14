# PUMP and SPCX as floats, and the exits over everything the bot then copies (Nov 14)

Wallet 4 buys many coins with the PUMP token (`pumpCmXq...`) and the tokenized SpaceX stock (`SPCXxcqX...`). Neither
has a PumpSwap pool to SOL or WBTC, so the bot had no route (`../../2026-11-13/routes_nov13/`). Held as floats, like
WBTC, the coin is bought straight from its curve in one hop.

Run order (`SPD` = a scratchpad folder; the Triton URL is read from the scratchpad, never printed):
```
python3 -I ../../2026-10-31/since_stop/fetch_w4.py SPD/w4tx "2026-10-28 18:30"     # wallet 4's landed transactions
FLOATS=pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn,SPCXxcqXj6e5dJDVNovHN8744zkbhM2bYudU45BimGb \
  target/release/examples/scan RPC SPD/w4tx SPD/prices.json 1.45 > SPD/scan_hops.out   # the bot's own route planner
python3 -I ../../2026-10-31/since_stop/build_rows.py SPD                              # -> routable.json (times)
python3 -I ../../2026-10-31/since_stop/model.py SPD 0.5 4                             # each coin's 31-minute path -> paths.json.gz
python3 -I float_exits.py SPD 0.5 > out/float_exits.txt
python3 -I live_gap_w4.py SPD > out/live_gap_w4.txt
```
`prices.json`: lamports per raw unit (WBTC 7,950; PUMP, SPCX and the others at Jupiter's price of Nov 13,
`../../2026-11-13/routes_nov13/unpriced_val.py`).

- `lib.py`: the rows, the paths and the copy model of `since_stop/exit_final.py` in numpy. Checked against it trade by
  trade on the 232 coins both have (464 comparisons): equal but for a float's own curve route, which pays no pool hop
  here (0.3% each way there), and one coin with no trade after ours.
- `float_exits.py`: what the floats add, and 840 exit rules picked on the first half, scored on the second.
- `live_gap_w4.py`: the model against the bot's 17 real trades of Nov 12-13.

Checked so far (Nov 14):
- **Both mints are Token-2022.** PUMP: no freeze authority, no transfer fee. SPCX: a freeze authority, a permanent
  delegate and a pause switch (its issuer can freeze, pause or take it), no transfer fee.
- **The bot's buy and sell from each float simulate on chain** (`rugsnipe-long simulate --tx SIG --user HOLDER --sol
  0.5 --float MINT --close`): PUMP-paid `6HimP4fi`, route curve, 916-byte buy, round trip −5.30% of the stake (the
  curve's fees); SPCX-paid `9wqXM6pw`, round trip −2.47%.
- **Jupiter, 1 SOL into the float and straight back:** PUMP 0.02% lost, SPCX under 0.01%.
- **The scan with both floats, Oct 28 18:30 - Nov 13 23:21 UTC:** 468 routable 1.45+ SOL buys: SOL-paid 141, WBTC-paid
  115, PUMP-paid 150 (120 one hop, 28 two, 2 three), SPCX-paid 54, others 8. Five buys the earlier 3-hop study counted
  (`TooLong(3)`) have no route: its own route is 3 hops from a token we do not hold.

## Results (Nov 14; `out/*.txt`; SPD = 443 copyable buys, Oct 29 12:02 UTC - Nov 13 23:02 UTC, 15.5 days)

Run after the above: `tp_check.py`, `early_check.py`, `tp_fine.py`, `hold_check.py`, `caps_check.py`, `risk_check.py`,
`decode_check.py` (each `python3 -I X.py SPD 0.5 > out/X.txt`). All raw model, 0.5 SOL, 2 open, mean of landings
4 / 8 / one block late unless said; brackets = without each half's best 2.

**The model reads the new coins right** (`decode_check.py`): wallet 4's own result from the path's events equals its
token balances on all 110 PUMP-paid and 50 SPCX-paid coins it bought once and sold out (difference 0.00 points a coin).

**What each kind of coin makes, every copy, live rule** (`float_exits.txt` §1): SOL-paid 135 copies −1.71 (−4.84),
WBTC-paid 110 +10.13 (+6.31), **PUMP-paid 145 +8.51 (+5.15), SPCX-paid 53 +5.01 (+2.19)**; PUMP and SPCX positive in
both halves.

**The bot's run, live rule** (§2): SOL + WBTC routes (live now) +8.82 (+4.91), second half −0.94; with PUMP and SPCX
(1 open from each) **+22.92 (+18.78)**, second half +6.09. Corrected by the model's Oct 28-29 miss: +20.04 against
+42.41.

**The model against the bot's 17 real trades** (`live_gap_w4.txt`): 16 found; real +0.0990 SOL, model −1.3690 at
landing 4. Timer exits (12): real over the model by +4.5 points of the stake (median); take profits (3): +160 (median;
+32, +160, +192); the one sale behind its sale −11.6. The raw model stays the lower bound.

**Exits** (§3, `tp_fine.txt`, `tp_check.txt`, `early_check.txt`, `hold_check.txt`):
- **Take profit 3.0 over 2.4**: +30.36 (+24.02) against +23.44 (+19.30) (early 30-290, 1790 s); better in both halves,
  in each third of the period, at each landing, without the best 2 and the best 5. The scan is smooth: 2.4 +23.44,
  2.6 +24.40, 2.8 +27.24, 3.0 +30.36, 3.2 +30.87, 3.4 +30.12, then noisy (3.6 +27.47, 4.0 +31.70 with fewer and
  bigger wins: without the best 5 it falls from +17.54 at 3.0 to +14.60). Of 96 copies that reached 2.4x, 63 reached
  3.0x (66%; PUMP 73%, SPCX 74%, WBTC 61%, SOL 52%). SOL-paid coins alone prefer 2.4; the bot has one setting.
- **The early-sale window 30-290 s** (was 30-180), still under 1.5x: better in both halves at tp 2.4 and 3.0
  (+30.36 against +28.55 at 3.0). Wallet 4 sells 62 of 443 coins at 300-309 s (its own timer); following those is
  worse (30-310: +27.83), so the window ends before them.
- **The timer, 1200 s** (was 1790): the owner's question, are the wins in by 600 s? Mostly: of 60 take profits at 3.0,
  50 come within 600 s. But the 10 later ones earn +6.21 SOL and waiting costs −4.60 on the rest: 600 s +28.12
  (+23.18), 1200 s **+31.14 (+26.19)**, 1790 s +30.51 (+24.17). 1200 s is as good as 1790 s or a little better at
  both rules, each landing, and frees the money a third sooner.
- **No stop**: 0.4x and 0.5x change nothing (§3 means: +14.24 / +3.31 without, +14.37 / +3.34 and +14.12 / +3.29 with).

**How many at once from each** (`caps_check.txt`): a second WBTC slot is worth about +4.4 SOL (first half only); a
second SOL, PUMP or SPCX slot nothing. SOL 1, WBTC 2, PUMP 1, SPCX 1 needs about 2.55 SOL; one from each, 2.05.

**The rule chosen** (tp 3.0, 1200 s, early 30-290 under 1.5x, no stop; SOL 1, WBTC 2, PUMP 1, SPCX 1;
`risk_check.txt`): +31.14 (+26.19), first half +20.75 (+18.34), second +10.38 (+7.85). Landing 4 by UTC day: 15 of 16
up, worst −0.44, median +1.87, best +6.84; the best 3 days +16.58 of +34.32. Deepest fall from a high −2.0 to −2.3 SOL
(Nov 6-8), with or without the 1.0 SOL daily stop. By what we pay with: WBTC 105 copies +11.47, PUMP 125 +13.44,
SPCX 47 +9.31, SOL 125 +0.09.

## The owner's two remarks after the switch (`him_vs_us.py`, `follow_300.py`, Nov 14)

- **"All our wins would have been losses at tp 3.0": no.** `status` shows the peak while we held; each of the four
  coins went on: 5tePJcGm 5.96x (3.0x at 473 s), Eymbsj8M 10.00x (389 s), BUdiaswB 3.62x (643 s), BTCmcoKg 4.75x (29 s).
- **"He loses much less than us and even profits on trades we lose": true, and a copy cannot have his result.** On
  the 18 real trades (`status --chain`): the 14 we lost, us −35.2% a trade, him −16.9%; the 4 we won, us +215%, him
  +125%; all 18, us +20.4%, him +14.7%. On the 443 coins our buy pays +5.9% over the price his buy left (median), and
  his first sale moves the price −7.4% (he sells at 1.02x, the next seller at 0.95x).
- **Selling behind more of his sales** (coin by coin, every copy, tp 3.0, 1200 s, against the window 30-290 s): also
  290-330 s: first half −2.02 SOL on 35 copies (16 better, 15 worse), second half −0.03 (30 better, 10 worse); every
  sale under 1.5x: −1.26 and −2.67; every sale at any price: −5.86 and −4.67 (17 and 13 take profits cut). Most copies
  get a little better, a few that run after his sale get much worse.
- **Our 16 real trades in the model** (landing 4, real stakes): the rule live then −1.3690 SOL (real +0.0990), his
  every sale followed −0.5393, the new rule −0.1808.
- The WBTC-paid buys are valued at 7,950 lamports a unit here (about 8,820 on Nov 14), so a few just over 1.45 SOL
  (BTCmcoKg, 1.499) are missing from the study.

## Do the take profits come every day, from every kind of copy? (`tp_daily.py`, `out/tp_daily.txt`, Nov 14)

The run at the live rule, landing 4, by Beirut day (17 days, the first and last partial): 378 copies, **55 take
profits, 1 in 6.9 copies, 3.2 a day; at least one on 16 of 17 days.** Net +34.33 SOL = the take profits +49.57, every
other copy together −15.24. By kind: SOL 11 in 117 copies (1 in 10.6; on 6 of 17 days); WBTC 12 in 97 (1 in 8.1; 9
days); PUMP 18 in 118 (1 in 6.6; 12 days); SPCX 14 in 46 (1 in 3.3; 9 days); 3-hop routes 3 in 21 (2 days). Between
one take profit and the next: 5.2 hours (median), 25.2 at most; the longest run of copies without one, 47.

## Its own exits for each kind of copy? (`per_class.py`, `out/per_class.txt`, Nov 14)

The owner's question. 64 rules a kind (tp 2.0 / 2.4 / 3.0 / 4.0 x timer 300 / 600 / 1200 / 1790 s x his sale followed
never / 30-180 / 30-290 s / always), each kind's best picked on one half and scored on the other, both ways:
- **The bot's run with each kind on its own picked rule, on the half it was not picked on: +0.30 SOL against +10.38
  for the one rule (picked on the first half, scored on the second), and +16.10 against +20.75 (the other way).**
  Worse by −10.09 and −4.65 SOL.
- A kind's best rule on one half ranks 54th to 58th of 64 on the other half for SOL, WBTC and PUMP (SPCX: 36th one
  way, 2nd the other). The picks contradict each other: PUMP tp 4.0 / 300 s then tp 3.0 / 600 s; WBTC tp 3.0 / 1200 s
  then tp 2.0 / 300 s; SPCX tp 2.0 / 300 s then tp 4.0 / 600 s.
- One setting at a time (the rest as the one rule): no kind has a setting that wins in both halves by more than
  about 1 SOL, except SOL-paid copies with a 300 s timer (−1.27 / −3.30 against −2.26 / −3.06: better in one half only).
Each kind has 23 to 73 copies a half and about 1 take profit in 7 copies, so a half holds 5 to 10 take profits a
kind: too few to tune on. The one rule stays.
