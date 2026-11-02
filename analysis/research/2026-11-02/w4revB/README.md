# Wallet 4's part B, bought at launch ourselves (Nov 1-2)

Question: can we trade wallet 4's "part B" ourselves, by picking the same launches at launch time instead of copying
its buys, and how would we pay for them? Wallet 4 = `H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg`. Part B = pump coins
priced in a token with no canonical PumpSwap pool against wSOL or WBTC (`multi_hop_swap` refuses them, `OnlyPumpPools`).
P1 = creates of Oct 19 00:00 to Oct 22 24:00 UTC (where rules are picked), P2 = Oct 23 00:00 to Oct 27 00:00 (scored),
P3 = Oct 27 00:00 to Nov 1 23:00 (fresh). (+x) = the period's total without its best 2 trades. Times UTC.

## Answer in short

1. **A pick rule exists, but it only finds the kind of coin, not the coin.** Visible at create: a dev buy in the create
   transaction, the creator's first coin since Oct 19, a hand-made create transaction (ATA + compute budget + pump, no
   launch-bot program). That rule (R2) passes 2,192 of P2's 42,521 part-B creates at 16.8% precision and 49% recall
   (base rate 1.8%); the best tree reaches 25-27% precision at 26-33% recall. For its 1.45+ SOL picks nothing gets past
   2-4% precision except one launcher's metadata host.
2. **Buying those coins at launch loses.** R2 at 1 SOL, float: P1 −189.32 on 4,084 trades, P2 −7.33. Every narrower
   rule loses on both periods. Every launch of the active quotes: P1 −2,636.67, P2 −1,360.48. The R2 coins wallet 4 did
   not buy carry the loss (P1 −155.63 on 3,071).
3. **Wallet 4's own selection is where the money is**, and no create-time feature reproduces it: its 1.45+ SOL picks,
   bought by us at launch, make P1 +48.78 and P2 +12.07 (+9.89) at 1 SOL as a float; +35.32 and +4.88 (+2.68) through
   Jupiter. Knowing its pick before it buys is not possible from what we tested.
4. **It is mostly not a quote rotation.** Its best quote changes almost daily (CARDS, PUMP, 86j9yoVz, ZEC, TTWO,
   Pren1F ...), and buying every launch of the quotes positive on P1 loses on P2 (−25.58). The one thing that passed P2
   is R2 restricted to the quotes where R2 was positive on P1: P2 +6.70 (+2.50) float, +12.08 (+5.65) Jupiter, carried
   by USDC (+7.48 on 25 sampled trades). **On P3 (Oct 27 - Nov 1) it loses:** −5.63 (P1's quotes) and −31.65 (P2's
   quotes) as a float, −5.81 / −34.73 through Jupiter.
5. **Execution:** Jupiter's quote leg is nearly free for the main quotes now (0.00-0.15% round trip at 1 SOL; Pre*
   tokens about 2.3%; thin pump-coin quotes 3-17%); what costs is the slot later. Floats would need dozens of tokens and
   up to 45 SOL of PUMP alone (R2 at 1 SOL, P1), with 12-22% drawdowns on PUMP, CARDS and XMR over the 8 days.
6. **Verdict: no.** Buying part-B launches by our own pick loses out of sample; only wallet 4's own picks pay (P3 as a
   float +70.86, +34.50 without the best 2; through Jupiter +26.71, −8.00 without them), and those cannot be known
   before it buys. Don't build it.

## Run order

Scratchpad `/tmp/claude-0/-home-user/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/gmgn-out/w4revB/`. The Triton
client is the scan agent's `../agents/scan/bin/crc.py` (URL never printed), paced at 0.06 s, at most 8 threads.
`blib.py` reads the part-A agent's cache (`../w4rev/cache`) and the scan agent's cache read-only, and writes only to its
own `cache/`. **The disk filled up during the run** (the volume is capped near 40 GB; this folder's share was 21 MB), so
`cache/`, `tapes/`, `out/universe.json`, `out/table.json` and `out/fresh_table.json` are symlinks into
`/dev/shm/w4revB/` (RAM, lost on reboot; every file there is rebuilt by the scripts below).

```
python3 -I prices.py                  # quote prices in SOL from wallet 4's own swaps (h9long/ledger.py's source) -> out/tokp.json
python3 -I u1_universe.py             # part-B universe from the part-A agent's quote-control read; picks; by quote and day
python3 -I u1b_usdc.py                # USDC creates mostly skip the quote-control PDA: estimate from a mint-authority sample
python3 -I f1_table.py                # create-time features of the 98,453 part-B creates; pick rates by feature
python3 -I f2_rule.py pick|big        # rules picked on P1, scored on P2 (precision, recall)
python3 -I f3_rotation.py             # wallet 4's own net by quote and day
python3 -I t0_sample.py; python3 -I t0b_subsample.py 0.5   # the backtest sample and its weights
python3 -I j1_jup.py sample           # Jupiter round trip SOL -> quote -> SOL at 0.1 and 1 SOL per quote (Nov 1)
python3 -I p1_run.py out/coins_all.json 8 40 30 12 20      # tapes (t1_tapes.py) + simulation (sim.py) -> out/sim.json
RESIM=1 python3 -I p1_run.py out/coins_all.json 8 40 30 12 20   # again once jup.json covers every quote
python3 -I score.py table             # the backtest by selection; score.by_quote / score.qpick for the quote tables
python3 -I f4_slot.py                 # the create slot's bundle buys as a feature (sampled coins)
python3 -I fl_risk.py; python3 -I c1_capital.py            # float price risk; positions open at once
python3 -I u2_fresh.py; python3 -I w1_recent.py 2000; python3 -I u3_fresh_sample.py 150
FRESH=1 python3 -I p1_run.py out/coins_fresh2.json 8 40 30 12 20; python3 -I s9_fresh.py   # §4
```
Triton calls: 91,844 for the main pass, 9,662 for the re-simulation (stopped at its 10-minute limit after 2,800 coins;
the rest, all in the 44 quotes the first pass already priced, kept their first-pass results), 21,876 for P3, 2,012 for
wallet 4's recent sample, plus a few thousand in tests and the first, interrupted fetch (logs in `out/*.log`).

## 1. The universe (`u1_universe.py`, `u1b_usdc.py`)

The part-A agent read every landed signature of pump's quote-control PDA (account #19 of a `create_v2` with a quote
tail) for Oct 19 00:00 - Oct 27 00:00: 114,104 creates. Each quote is classed as `rugsnipe-long`'s `route.rs` would
find it (canonical pool against wSOL or WBTC, state of Nov 1): class E (part B) 98,453, A 10,202, C (WBTC) 2,970,
B 2,457. Part B spans **1,476 quote mints** (92,092 plain tokens, 5,813 pump-coin quotes, 548 quoted two levels deep;
the last can be 3 hops from wSOL, 6 of its 1.45+ picks).

**Wallet 4's launch picks** (its buy in the create slot or the next, `../w4rev/out/picks.json` from h9long's trips):
2,177 of the 98,453 (2.2%), 368 at 1.45+ SOL; 16 more bought later. Its net on them (trip net, h9long):

| | creates | its launch picks | share | 1.45+ picks | its net, all | its net, 1.45+ |
|---|---|---|---|---|---|---|
| P1 Oct 19-22 | 55,932 | 1,431 | 2.6% | 242 | +59.46 | +93.37 |
| P2 Oct 23-26 | 42,521 | 746 | 1.8% | 126 | +69.31 | +26.02 |

The brief's +77.13 (204) / +14.94 (101) are its 1.5+ SOL class-E buys (`routable.json`); this study's 1.45+ set adds
the 1.45-1.5 tier (P1 37 coins +14.03, P2 28 coins +12.49); on 1.5+ the same coins come out at +77.13 (204) and
+13.53 (98 of the 101; 3 fall on Oct 27 00:00-00:40 or outside the launch window).

**By quote token** (creates / its launch picks (share) / 1.45+ picks / its net on all its picks):

| quote | P1 creates | picks | share | 1.45+ | its net | P2 creates | picks | share | 1.45+ | its net |
|---|---|---|---|---|---|---|---|---|---|---|
| CARDS | 2,855 | 485 | 17.0% | 77 | −4.73 | 277 | 16 | 5.8% | 0 | +1.57 |
| PUMP | 28,621 | 226 | 0.8% | 34 | +9.29 | 22,300 | 140 | 0.6% | 21 | +12.01 |
| TTWO | 1,956 | 119 | 6.1% | 10 | +8.39 | 1,249 | 98 | 7.8% | 5 | +15.82 |
| XMR (WXMR) | 1,037 | 83 | 8.0% | 9 | −0.71 | 474 | 31 | 6.5% | 6 | +2.09 |
| ZEC (A7bd) | 559 | 31 | 5.5% | 7 | +3.05 | 872 | 46 | 5.3% | 16 | +6.98 |
| SPCX | 3,790 | 26 | 0.7% | 6 | +0.49 | 2,709 | 42 | 1.6% | 7 | +0.47 |
| 98sMhvDw | 194 | 57 | 29.4% | 2 | −5.75 | 138 | 9 | 6.5% | 3 | −1.48 |
| Pren1F | 746 | 38 | 5.1% | 8 | +2.39 | 825 | 22 | 2.7% | 2 | +7.08 |
| DJTu | 1,628 | 7 | 0.4% | 0 | −1.31 | 2,243 | 33 | 1.5% | 7 | +5.72 |
| XsoCS1Tf (xStock) | 199 | 16 | 8.0% | 4 | −6.80 | 247 | 27 | 10.9% | 2 | −1.25 |
| Xsc9qvGR (xStock) | 1,255 | 34 | 2.7% | 5 | −5.75 | 494 | 5 | 1.0% | 1 | −0.68 |
| USDC (quote-control part only) | 221 | 12 | 5.4% | 7 | +5.79 | 305 | 5 | 1.6% | 2 | +2.14 |
| 86j9yoVz (a pump coin on PUMP) | 206 | 15 | 7.3% | 12 | +25.89 | 2 | 0 | 0% | 0 | 0 |
| CrAr4RRJ | 6 | 0 | 0% | 0 | 0 | 224 | 12 | 5.4% | 2 | +3.82 |
| all part B | 55,932 | 1,431 | 2.6% | 242 | +59.46 | 42,521 | 746 | 1.8% | 126 | +69.31 |

161 quotes had a launch pick. **No major quote is trivial**: it takes 0.4-17% of a quote's launches (29% of 98sMhvDw's
in P1, mostly 51 picks on Oct 19). Only tiny quotes come close to "all of them" (BZFYNPeQ 6 of 7 and 5 of 10,
8x5VqbHA 5 of 8). Per day (creates / picks / 1.45+), the rotation is visible: CARDS 1,734 / 239 / 47 on Oct 20, then
115 / 12 / 0 on Oct 23 and 20 / 0 / 0 on Oct 25; XMR 879 / 72 / 6 on Oct 22 only; PUMP steady at 3,572-7,849 creates
and 21-85 picks a day (`out/u1.log`).

**USDC** creates mostly skip the quote-control PDA (11 of the 15 USDC creates in a seeded sample of 1,500 landed
mint-authority signatures), so the table holds only part of them: about **3,789** USDC creates in Oct 19-26 (95%
2,300-6,228; 378,945 landed mint-authority signatures), 21 of them its launch picks (about 0.55%), its net +7.28.

## 2. Its picks: is there a rule? (`f1_table.py`, `f2_rule.py`, `f3_rotation.py`, `f4_slot.py`)

Features from the create transaction (what a bot landing in the create slot sees): quote, dev buy (count, SOL at pump's
config price, share of supply), creator fee, depth, metadata host, name and symbol traits, hour, the programs called,
fee, compute; the creator's earlier creates since Oct 19 (all quotes); the quote's creates in the hour before.

**Pick rates by feature (P1 | P2):** dev buy in the create tx 6.6% | 4.0% against 0.3% | 0.2% without; dev buy 0.5-1 SOL
15.0% | 9.8%, 1-2 SOL 12.7% | 8.1%, 2+ SOL 1.3-3.0%; the creator's first coin 17.3% | 11.0% (20+ earlier coins: 0.0-0.7%);
create tx "ata+cb+pump" 21.3% | 12.4%, "cb+pump+sys" and "pump" alone (launch bots) 0.0%; creator fee 200 bps 27.6% |
22.2%, 250 bps 45.2% | 21.4%, 300 bps 0.6% | 0.6%; metadata on ipfs.io 6.2% | 3.9%, j7tracker 0.4% | 0.1%.

**Rules picked on P1, scored on P2** (its launch picks, any size):

| rule | P1 passes | precision | recall | P2 passes | precision | recall |
|---|---|---|---|---|---|---|
| R0 dev buy in the create tx | 20,151 | 6.6% | 93.4% | 17,240 | 4.0% | 92.8% |
| R1 + the creator's first coin | 5,556 | 19.5% | 75.8% | 2,852 | 13.8% | 52.9% |
| **R2** + hand-made create tx (ata[+cb]+pump[+sys]) | 4,097 | 24.8% | 71.1% | 2,192 | **16.8%** | **49.3%** |
| R3 R2 + dev buy 0.1-2 SOL | 2,701 | 28.3% | 53.5% | 1,412 | 19.1% | 36.2% |
| R4 R2 + dev buy 0.5-2 SOL | 1,923 | 33.0% | 44.4% | 928 | 22.3% | 27.7% |
| R5 R3 + creator fee 150-250 | 626 | 45.0% | 19.7% | 344 | 25.6% | 11.8% |
| tree depth 3 (leaves ≥ 30% on P1) | 1,791 | 36.6% | 45.8% | 829 | 25.3% | 28.2% |
| tree depth 4 (leaves ≥ 30%) | 1,429 | 42.4% | 42.3% | 716 | 27.4% | 26.3% |
| quote alone (its P1 share ≥ 5%, 10+ picks) | 8,335 | 10.5% | 61.3% | 4,754 | 5.8% | 37.1% |

The depth-3 tree is R2's core: creator's first coin, `ata+cb+pump`, dev buy over 0.47 SOL (37% on P1). Precision falls
from P1 to P2 everywhere. **Its 1.45+ SOL picks** cannot be told apart: R2 2.0% precision on P2, R4 2.5%; the only sharp
leaf is one metadata host (`meta.notrandom.fun`) with at most 5 creates in the day before: 22 of 64 on P1, 15 of 59 on
P2. **The create slot** (`f4_slot.py`, buys within 5 transactions of the create by other wallets, counted before its own
buy): pick rate 2.8% | 2.0% with none, 11.1% | 3.8% with 1, 1.6% | 1.1% with 2-3, 12.9% | 5.7% with 4+; inside R2 26.0% |
17.5% with none, 46.6% | 25.9% with 4+ (52 and 27 sampled coins). Not a usable separator.

**Its own net by quote and day** (`f3_rotation.py`, all sizes): the best quote changes almost daily.

| day | its part-B launch net | best quote | worst quote |
|---|---|---|---|
| Oct 19 | +30.46 (271) | CARDS +15.23 | 98sMhvDw −4.38 |
| Oct 20 | +31.35 (431) | CARDS +11.65 | 6eukYbG1 −1.27 |
| Oct 21 | −6.90 (378) | PUMP +10.80 | CARDS −23.73 |
| Oct 22 | +4.57 (351) | 86j9yoVz +25.89 | PUMP −11.15 |
| Oct 23 | +12.90 (231) | ZEC +6.89 | XsoCS1Tf −2.19 |
| Oct 24 | +15.95 (179) | TTWO +5.93 | Pren1F −0.87 |
| Oct 25 | +8.96 (181) | 28ZdKbDw +4.73 | Prewe −1.41 |
| Oct 26 | +31.50 (155) | Pren1F +8.24 | ZEC −1.94 |

Per pick, P1 → P2: PUMP +0.041 → +0.086, TTWO +0.071 → +0.161, ZEC +0.098 → +0.152, Pren1F +0.063 → +0.322 held their
sign; CARDS −0.010 → +0.098 on 16, XMR −0.009 → +0.067, XsoCS1Tf −0.425 → −0.046, 6p6xgHyF +0.262 → −0.094 did not.

## 3. Buying at launch ourselves (`t0_sample.py`, `t1_tapes.py`, `sim.py`, `score.py`)

**Sample** (weights in `out/sample.json`): its 368 1.45+ picks (all), 904 of its 1,809 smaller picks (a seeded half,
weight 2), 600 a period of the R2 coins it did not pick (weight 5.12 / 3.04), and 2,260 other launches of the 44 active
quotes (5+ picks over the 8 days; per quote and period, weight = pool / sampled). 4,732 coins.

**Price path:** the coin's own pump TradeEvents (virtual reserves), every transaction of slots +0..+2, then up to 30
transactions to create + 1,800 s (the first 12 and 20 spread over the rest), more read where an exit fires
(at most 40 a coin). The part-A agent's tape and fill code (`../w4rev/tape.py`, `s5_sim.py`), extended. Check against
wallet 4's own exits on its 1.45+ picks (filled after its buy slot): of its 70 take profits, 58 are take profits in our
run; of its 33 stops, 31 stops; of its 219 timer sales, 199 timer sales.

**Models:**
- **float:** we hold the quote. Fill after the last trade of the create slot or of the next (half and half by coin).
- **jup:** one transaction SOL → quote (Jupiter) → coin, one slot later: after slot +1 or +2. The quote leg costs half
  the measured Jupiter round trip each way (`j1_jup.py`, Nov 1, at our stake; fees and impact).
- Our own impact at 1 SOL (also 0.1); later recorded states shifted by our quote (the cautious model). Exits on the
  price our buy left: **its** 2.5x / 0.7x / 30 min, **ours** 2.0x / 0.8x / 30 min; a take profit fills 1% under the
  trade that crosses it. Pump's fee 1.25% each side, 0.003 SOL a round trip. P&L in SOL counts the quote's own price
  move during the hold (its own-swap price at the fill and at the exit); "no move" holds it fixed.

**Results at 1 SOL** (`out/score_table.log`; n = sampled trades, N = trades they stand for; P2 needs both the total and
the total without the best 2 above zero):

| selection | model, exits | P1 N | P1 total | P1 median | P2 N | P2 total (w/o best 2) | P2 median |
|---|---|---|---|---|---|---|---|
| its 1.45+ picks (not knowable at launch) | float, ours | 242 | **+48.78** | −0.099 | 126 | **+12.07 (+9.89)** | −0.123 |
| | float, its | 242 | +52.79 | −0.119 | 126 | +10.83 (+7.25) | −0.128 |
| | jup, ours | 242 | +35.32 | −0.169 | 126 | +4.88 (+2.68) | −0.163 |
| | jup, its | 242 | +30.97 | −0.185 | 126 | +3.88 (+0.56) | −0.171 |
| its picks, all sizes | float, ours | 1,431 | +15.08 (−2.58) | −0.144 | 746 | +31.61 (+28.02) | −0.105 |
| | jup, ours | 1,431 | −37.20 | −0.176 | 746 | +11.23 (+7.59) | −0.122 |
| its picks under 1.45 SOL | float, ours | 1,189 | −33.69 | −0.145 | 620 | +19.55 (+14.95) | −0.103 |
| **R2** (its picks and not) | float, ours | 4,084 | **−189.32** | −0.082 | 2,190 | −7.33 (−13.39) | −0.055 |
| | float, its | 4,084 | −137.89 | −0.081 | 2,190 | +28.81 (+15.74) | −0.056 |
| | jup, ours | 4,068 | −257.97 | −0.098 | 2,181 | −23.00 (−27.71) | −0.065 |
| R2, not its picks | float, ours | 3,071 | −155.63 | −0.068 | 1,822 | −9.75 (−16.64) | −0.047 |
| R3 (R2, dev 0.1-2) | float, ours | 2,706 | −122.57 | −0.085 | 1,424 | −17.02 (−23.54) | −0.079 |
| R4 (R2, dev 0.5-2) | float, ours | 1,845 | −112.75 | −0.111 | 918 | −22.03 (−28.26) | −0.095 |
| tree3 | float, ours | 1,472 | −101.70 | −0.127 | 659 | −18.72 (−24.32) | −0.096 |
| every launch, 44 active quotes | float, ours | 49,502 | −2,636.67 | −0.028 | 36,999 | −1,360.48 | −0.028 |
| | jup, ours | 49,502 | −3,021.56 | −0.028 | 36,999 | −1,457.67 | −0.028 |

At 0.1 SOL the signs are the same (R2 float ours −29.91 / −5.30; its 1.45+ picks +4.47 / +1.30). The quote's own move
during the hold is small: the "no move" totals differ by 0.1-1.1 SOL on the pick and rule selections above, and by
13.5 on every launch (−2,650.21 against −2,636.67, P1). **No rule picked on P1 can pass:** every create-time selection is negative on P1. R2 with
its exits is positive on P2 (+28.81, +15.74 without the best 2) but −137.89 on P1, so it would never be picked.

**By quote, float, our exits, 1 SOL** (P1 total (sampled trades) | P2 total [w/o best 2]; `out/score_quote.log`):

| quote | its 1.45+ picks | its picks, all | R2 | every launch | its own net P1 / P2 |
|---|---|---|---|---|---|
| CARDS | +5.31 (77) \| 0 (0) | −17.53 (285) \| +1.36 (10) | −54.52 (331) \| −10.20 | −133.99 \| −20.26 | −4.73 / +1.57 |
| PUMP | +4.73 (34) \| +2.68 [+0.75] | +3.95 (130) \| +10.87 [+6.47] | −69.99 (195) \| −8.13 | −991.28 \| −687.62 | +9.29 / +12.01 |
| TTWO | +3.49 (10) \| −0.40 | −0.11 (59) \| +11.74 [+7.71] | −10.25 (53) \| +10.76 [+4.67] | −208.12 \| +102.80 [+97.50] | +8.39 / +15.82 |
| XMR | +5.31 (9) \| −0.18 | −0.10 (47) \| −4.41 | −15.23 (69) \| −6.77 | −90.20 \| −27.90 | −0.71 / +2.09 |
| ZEC | +1.29 (7) \| +3.15 [+1.14] | +3.68 (15) \| +4.01 [+2.01] | −0.40 (26) \| +2.33 [−3.71] | −61.78 \| −71.29 | +3.05 / +6.98 |
| SPCX | +1.38 (6) \| −0.19 | +1.77 (13) \| −0.96 | −17.39 (45) \| −5.48 | −542.50 \| −132.09 | +0.49 / +0.47 |
| 98sMhvDw | −0.47 (2) \| +0.41 | −7.58 (29) \| −0.54 | −7.01 (35) \| +3.59 [−2.06] | −12.79 \| −7.53 | −5.75 / −1.48 |
| Pren1F | +2.25 (8) \| 0 | +5.28 (25) \| +2.41 [−0.27] | −4.29 (15) \| +1.32 [−4.63] | −63.98 \| +57.80 [−2.45] | +2.39 / +7.08 |
| USDC | +3.48 (7) \| +1.84 | +4.68 (10) \| +1.39 | +6.07 (19) \| +7.48 [+3.29] | −4.86 \| −23.69 | +5.79 / +2.14 |
| 86j9yoVz | +8.78 (12) \| 0 | +10.18 (15) \| 0 | +8.58 (12) \| 0 | +4.23 \| −0.47 | +25.89 / 0 |

TTWO's every-launch P2 +102.80 rests on 4 sampled base coins that hit the take profit, each standing for 45.9 launches
(+80.86 of it from the base sample; without its best 2 the other two keep it at +97.50); P1 −208.12.

**The rotation test** (`score.qpick`): per selection, keep the quotes where it was positive on P1 (5+ sampled trades),
score them on P2.

| selection, model | quotes kept | P1 | P2 (w/o best 2) |
|---|---|---|---|
| every launch, float ours | 8 of 40 | +40.85 | **−25.58 (−35.53)** |
| every launch, jup ours | 5 of 40 | +24.74 | −13.37 (−22.25) |
| R2, float ours | 9 of 33 | +50.96 | +6.70 (+2.50) PASS |
| R2, jup ours | 8 of 33 | +45.07 | +12.08 (+5.65) PASS |
| R2, float its | 10 of 33 | +91.84 | +8.31 (−2.20) |
| R2 not its picks, float ours | 9 of 27 | +41.87 | +10.44 (+4.30) PASS |
| its 1.45+ picks, float ours | 10 of 10 | +36.54 | +6.62 (+4.62) PASS |

The R2 pass rests on USDC (P2 +7.48 on 25 sampled trades, +3.29 without its best 2; P1 +6.07 but +0.01 without its
best 2) and XsqE9cRR (+3.53, −1.09); 6p6xgHyF, the best on P1 (+19.66), made −1.61 on P2. Re-picked on P2 the set is
different (98sMhvDw, DOGE, HiMSSzzw, Pren1F, TTWO, USDC, WETH, XspzcW1P, XsqE9cRR, ZEC, oreoU2P8): only USDC and
XsqE9cRR are in both. USDC is also the quote this universe under-covers (§1).

**Capital and floats** (`c1_capital.py`, `fl_risk.py`; every hold counted as 30 min, an upper bound, though 76% of the
simulated R2 trades do run the full 30 min): R2 at 1 SOL holds a median 24 positions at once on P1 (90%: 41, max 75)
and 13 on P2 (max 33); the float a quote needs is its most open at once: PUMP 45 SOL, CARDS 26, TTWO 23, XMR 22
(P1). Its 1.45+ picks: median 3 / 2 open, max 10-11. Each float's own price over the 8 days, from its own swaps:

| token | P1 change | P2 change | worst fall | 1 SOL float, P1 / P2 |
|---|---|---|---|---|
| CARDS | +17.0% | −1.7% | −12.2% (to Oct 26) | +0.170 / −0.017 |
| PUMP | +4.7% | −2.0% | −12.5% (to Oct 26) | +0.047 / −0.020 |
| TTWO | +1.9% | +0.7% | −3.6% | +0.019 / +0.007 |
| XMR | +1.9% | +1.1% | −22.1% (to Oct 24) | +0.019 / +0.011 |
| ZEC | +6.9% | +3.2% | −8.5% | +0.069 / +0.032 |
| SPCX | +4.3% | +2.4% | −3.5% | +0.043 / +0.024 |
| Prewe | −0.6% | −9.9% | −15.0% (to Oct 26) | −0.006 / −0.099 |
| USDC | +1.2% | +2.2% | −4.3% | +0.012 / +0.022 |

Many small quotes have under 10 own swaps (86j9yoVz, CokrQHPj, GYFGHK9e ...): no price series; the backtest values them
at pump's own config price, with no move.

**Jupiter's quote leg, round trip at 1 SOL (Nov 1):** USDC, CARDS, PUMP, ZEC, 98sMhvDw, Xsc9qvGR, WETH, TTWO, XsoCS1Tf
0.00-0.03%; SPCX 0.06%, XsqE9cRR 0.09%, XMR 0.15%; Pren1F 2.30%, Prewe 2.36%; CrAr4RRJ 1.24%; 86j9yoVz 9.08%, GYFGHK9e
8.31%, CokrQHPj 6.60%, D42TjMjz 17.14% (thin pump-coin quotes). 204 of the 210 quotes in the sample have a route; 6
have none. The jup model loses against float mostly from the later fill, not the swap.

## 4. Fresh check, P3 (Oct 27 00:00 - Nov 1 23:00) (`u2_fresh.py`, `w1_recent.py`, `u3_fresh_sample.py`, `s9_fresh.py`)

**The market:** the part-A agent's quote-control read of the window (60,251 creates) holds **52,794 part-B creates**
(10,342 / 9,479 / 11,071 / 9,536 / 6,698 / 5,668 a day, Oct 27 to Nov 1), 2,821 of them R2 (333-676 a day). By creates:
PUMP 20,951, 98sMhvDw 4,160, SPCX 4,061, DJTu 1,943, DOGE 1,247, EVcoZp3P 968, SQQQAa3g 850; in R2: 98sMhvDw 629, PUMP
421, CARDS 225, SPCX 166, Xsc9qvGR 90, ZEC 82, USDC 73.

**Wallet 4 since Oct 27 00:00:** 14,224 signatures (13,917 landed) to Nov 2 02:12. From a seeded sample of 2,000 of them
(scaled by day): its part-B launch buys 86, 123, 213, 308, 228, 116 a day (Oct 27 to Nov 1), of them 1.45+ SOL 14, 0,
21, 40, 21, 7 (each sampled buy stands for about 7, so these are rough). Its part-B quotes lately: PUMP, 98sMhvDw, SPCX,
DJTu, XMR, XsbEhLAt, ZEC, and CARDS on Oct 30 only.

**The rotation rule** (the one P2 pass: R2 inside the quotes positive on the previous period), every P3 R2 coin of
those quotes (98sMhvDw sampled 150 of 629), 1 SOL:

| model, exits | quote set | Oct 27 - Nov 1: N | total (w/o best 2) | median | Oct 28 - Nov 1 total (w/o best 2) |
|---|---|---|---|---|---|
| float, ours | A: positive on P1 (9 quotes) | 144 | **−5.63 (−7.68)** | −0.039 | −2.97 (−4.92) |
| float, ours | B: positive on P2 (11 quotes) | 964 | **−31.65 (−40.97)** | −0.076 | −28.60 (−37.92) |
| jup, ours | A (8 quotes) | 213 | −5.81 (−7.93) | −0.043 | −5.15 (−7.22) |
| jup, ours | B (11 quotes) | 959 | −34.73 (−41.62) | −0.077 | −32.79 (−39.64) |
| float, its | A | 131 | −2.64 (−6.09) | −0.039 | −1.59 (−4.90) |
| float, its | B | 976 | −15.24 (−25.18) | −0.076 | −11.82 (−21.73) |

USDC, which carried P2, made −4.57 on its 73 P3 R2 coins (float); 98sMhvDw −27.43 (N 629); ZEC +1.75 (−0.32 without its
best 2); 6p6xgHyF +1.84 (−0.02). **It fails out of sample.**

**Wallet 4's own part-B launch buys** (the coins of its sampled transactions, weight = 1 / sampling rate; perfect
selection, not knowable at launch), bought by us at launch, 1 SOL, quote price held:

| its buys | model, exits | Oct 27 - Nov 1: N | total (w/o best 2) | Oct 28 - Nov 1: total (w/o best 2) |
|---|---|---|---|---|
| all sizes | float, ours | 1,067 | +70.86 (+34.50) | +42.29 (+23.68) |
| all sizes | jup, ours | 969 | +26.71 (−8.00) | +2.33 (−13.25) |
| 1.45+ SOL | float, ours | 103 (15 sampled) | +16.55 (+2.31) | +20.13 (+5.89) |
| 1.45+ SOL | jup, ours | 103 | +8.08 (−6.05) | +11.57 (−2.57) |

By quote (float, ours, all sizes): DJTu +43.40 on 9 sampled (+9.04 without its best 2), ZEC +12.65 (−0.06), XsDoVfqe
+9.23, PUMP +6.92 (−8.94), 98sMhvDw +2.69 (−11.13), CARDS −15.93, XMR −8.95. Its own choice still pays when we fill as
a float right behind the create; through Jupiter, one slot later, it does not survive removing the best 2.

## Verdict

- **Pick rule:** yes for the kind of coin, no for the coin. Create-time features find its picks at 17-27% precision
  (P2), but the other 75-83% of what the rule passes lose more than its picks make: R2 −189.32 (P1) / −7.33 (P2) at 1 SOL.
  Nothing tells its 1.45+ picks apart (2-4% precision).
- **Rotation:** wallet 4's best quote changes daily, but following last period's good quotes loses (P2 −25.58 on every
  launch; the rotation rule −5.63 / −31.65 on P3). The edge is its coin choice inside a quote.
- **Execution:** Jupiter (one transaction SOL → quote → coin) routes 204 of 210 quotes, at 0.00-0.15% round trip for the
  main ones (Nov 1), but lands a slot later and that costs most of the result. Floats fill earlier but need dozens of
  tokens (the main ones: PUMP, 98sMhvDw, SPCX, TTWO, ZEC, XMR, USDC, CARDS, DJTu, xStocks) and tens of SOL each, with
  12-22% drawdowns.
- **Buying at launch by our own pick does not make money out of sample.** Only its own picks do, and we cannot know them
  before it buys. Don't build it. What it would take: a signal that separates its picks from the R2 crowd (the create
  transaction and the create slot's bundle buys don't), and floats of the active quotes or a Jupiter path that lands in
  the create slot's next slot.

## Notes

- Pools and Jupiter costs are as of Nov 1, not as they were on each day. Quote prices come from wallet 4's own swaps
  (h9long/ledger.py's way) and end Oct 27 00:40: P3 coins are priced at the last of them, with no move.
- The universe is the quote-control list; USDC is under-covered (§1). The R2 rule uses "the creator's first coin since
  Oct 19": with a longer history the rule would be stricter.
- Weighted samples: the base and R2 non-pick totals are estimates (weights 3-60 a sampled coin); the "w/o best 2" column
  removes the two best sampled trades with their weights.
- Every number here is printed by a script in this folder (`out/*.log`).
