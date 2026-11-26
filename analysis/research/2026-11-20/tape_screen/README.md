# The wallet screen on the pump tape (Nov 20)

`s1_screen.py TAPE_DIR [MIN_SOL] [MIN_COPIES]`: one pass over the recorder's files (`../../2026-11-19/tape/`, the box's
unit `rugsnipe-tape`). For every wallet's first buy of a coin of MIN_SOL+ SOL: our copy (0.5 SOL in the slot after its
buy, refused over 1.5x, 0.0345 a round trip) under five fixed exits (wallet 4's live exit, its sale, tp 2x / 120 s,
held 300 s, tp 1.5x / 60 s); per wallet the exit best on the tape's first half, scored on the second (blind); the pooled
mean of all copies (a random wallet) as the bar.

Tested on the 2.5 h of tape recorded in the cloud session (Nov 19 17:22 - 20:17 UTC; `out_nov19_test.txt`): 514,038
trades, 11,335 copies, 15 s. Every copy pooled: -9.7% to -14.1% a copy by exit (our late entry and the costs: a random
wallet loses). 124 wallets with 8+ copies, 6 up on both halves; too short to mean anything, it shows the screen works.
On the box (two days of tape): `sudo systemd-run --scope -p MemoryMax=2G nice -n 19 /opt/rugsnipe/venv/bin/python -I
.../s1_screen.py /var/lib/rugsnipe-tape 0.5 20`.

**Each wallet tuned (Nov 21; the owner: "each wallet can be tweaked, min SOL, floats or not"):** per wallet, the choice
on half 1 of its buy floor (0.5 / 1 / 1.5 / 2 SOL) x the coins (all / SOL-quoted / token-quoted) x the five exits (60
choices, 5+ copies in each half), scored on half 2. The chance line gives the pseudo-wallets the same 60 choices (they
keep the real wallet's sizes and coin kinds), so the freedom to tune is priced in. Which floats we would need is stage 2.

**Audit against the live bot (`a1_audit.py`, `out_a1_audit.txt`):** three coins the bot traded on Nov 19 are on the cloud
tape. The model's triggers fire when the bot's did (its sale 179 s / 179 s; sell pressure 106 s / 105 s and 64 s / 63 s),
our landing 1.075-1.082x its price (the bot's journal: +10.2% on #138). The results are lower than live (-45.1% / -38.5%;
-23.8% / -9.1%; 0.0% / +10.7%): mostly the cost convention, 0.0345 SOL a round trip = 6.9% of a 0.5 SOL stake, where the
bot pays ~0.0064 (1.3%); the rest is the sale on the trade after the trigger in a falling coin. `COST=0.0064` gives the
live cost (the pooled bar on the Nov 19 tape: -4.0% to -8.5% a copy instead of -9.7% to -14.1%); the ranking is the same.

**Speed traders left out (Nov 21; the owner: "exclude the ones that sell after ~10 s, they rely on speed"):** a wallet
whose median holding (its buy to its first sale) is under MIN_HOLD seconds (env, default 20) is dropped before the tuning;
the list shows each wallet's median holding. On the Nov 19 tape 110 of 142 wallets with 8+ copies are such traders.

## The box, Nov 21 (21.1 h of tape, Nov 20 13:32 - Nov 21 ~10:40 UTC; the owner's paste)

`COST=0.0064 MIN_HOLD=20`, 20+ copies: 3,895,292 trades, 151,229 copies of first buys of 0.5+ SOL; every copy pooled
-7.1% to -13.9% a copy by exit. 554 wallets with 20+ copies left out as speed traders; **of the 359 left, 64 up on both
halves, against 48 by chance (five draws 31-57)**; the 30th best second half +9.7% against chance's +11.5%. A little above
chance, not enough to name a wallet. Wallet 4: 19 copies of its 0.5+ buys, -1.6% to -7.2% a copy by exit.
- **Two pairs of linked wallets, both of each pair in the top 20:** FT6LnH4J + FyRmQ8oS (61 coins in common of 64 / 62:
  one trader; 1.0+ SOL coins, held 300 s +42.5% / +41.4% and its sale +30.6% / +20.0%; both hold a median 50 s) and
  4cRLV1fw + 6nWLPrww (54 of 59 / 72; 1.0+ / 1.5+ SOL coins, held 300 s +30.3% / +25.3% and +75.0% / +20.2%; 29 s / 37 s).
  Both buy SOL-quoted coins (the long copy does not copy those). STorreSu + G9gmk9ms (1,045 / 681 coins) buy nearly
  everything (wallet 4 shares 68 coins with STorreSu).
- 6ua7w2Gv again (59 copies, 114 s): studied Oct-Nov (its holdout).

**Nov 21, the owner: "I thought this would be directly on the command on the recorder; don't exhaust Triton unless it's
cheap."** The screen (`s1_screen.py`) reads only the box's tape: no Triton. `s2_history.py` calls Triton (the wallet's
own transactions, then NCOPY coins' paths); it is run only on the final few wallets, with the owner's go, its own-result
part first. The run on the five best of the 21 h screen was stopped before any result.

**The box, Nov 21 ~12:40 UTC (22.4 h, the cautious ranking; the owner's paste):** 97,670 copies against 151,229 an hour
earlier on less tape: most likely Jupiter's price fetch failed (HTTP 429) and every token coin was left out; the screen
now retries, keeps the last good prices in `PRICE_CACHE` (/tmp/tape_prices.json) and prints how many tokens it priced.
On that run: 319 speed traders out; **17 of 182 up on both halves, chance 16 (12-21): nothing above chance**. Five wallets
(H2nsBdjF, FbWwk6eh, 7ThMFKUF, 6hFo8UYX, ...) share all 97 coins, never sell and every copy is ~0: bundle wallets on coins
that never move; such "flat" wallets are now left out. Best by the cautious score: 4S5L64Va (19 / 59 copies, its sale
+6.0% / +12.3%, score +5.7%, holds 23 s), then DGapgQYU (33 / 36, held 300 s -5.9% / +15.2%, score +1.8%).

**The box, Nov 21 ~12:45 UTC, the fixed run (22.5 h; prices 199 of 200 tokens; the owner's paste):** 154,760 copies;
571 speed traders and 20 flat bundles out; **53 of 373 up on both halves against 39 by chance (draws 32-43): above every
draw**, while the 30th best second half is still chance-sized (+7.0% against +8.2%). **The one that stands out:
4S5L64Va** (`4S5L64Va88JUPGTXaw5GvEdmm5hZrSGaYvcA7DrqKjjt`): 80 copies (19 / 61), its sale followed +6.0% / +13.6%, score
+6.8% (the next +2.0%), positive under four of the five fixed exits over all its copies (wallet 4's +9%, its sale +12%,
held 300 s +21%, tp 1.5x / 60 s +5%; tp 2x / 120 s -3%), buys of 3.16 SOL median, holds 24 s (just over the speed cut).
Next: DGapgQYU (69 copies, score +2.0%), then nothing above +0.6%.

**4S5L64Va, its own history (s2, `ONLY_OWN=1`, `out_s2_4S5L64Va_own.txt`; 2,925 transactions, a few cents of Triton):**
a new wallet (first trade Nov 19): 266 coins in 3 days, one buy a coin of 3.16 SOL median (844 SOL bought, 806 sold), its
last sale a median 116 s after its buy. **It loses itself: -37.47 SOL (Nov 19 +0.11, Nov 20 -28.65, Nov 21 -8.93); on its
236 coins sold out -43.22 SOL, 96 won, median -0.30 SOL a coin; 30 still held.** Dropped by the rule (it must make money
itself on most days), so no copy test. Our copies on the tape were up because its 3 SOL buy moves the coin and we sell
earlier than it does: an edge that ends when a wallet losing ~20 SOL a day stops.

**Protection added after 4S5L64Va (Nov 21), from the tape, free:** each wallet's own result on its sold-out coins of the
tape (`own SOL`; a wallet under OWN_MIN, default 0, is left out: it pays for the moves, it does not read them) and how far
its own buy moved the price (`impact`, median; a large one means the move after its buy may be its own doing). Its age
(a wallet seen for the first time days ago) is the history check's, on the final few.

**The box, Nov 21 ~13:20 UTC, with the own-result check (23.1 h; the owner's paste):** 156,535 copies; out: 582 speed
traders, 19 flat bundles, **288 that lose money themselves** (4S5L64Va among them). **45 of 233 up on both halves against
33 by chance (draws 23-40)**; the 30th best second half +6.0% against chance's +5.9%. No wallet's cautious score above
+1.0% yet. Worth following (own result on the tape, all-exit pattern): AZ1eJ671 (+13.07 SOL own, wallet 4's exit +7%,
holds 54 s), FyRmQ8oS (+5.64, pair A, its sale +22.2% / +9.4%), 3orcPHLt (+1.39, holds 135 s, every exit up +8% to +21%
on 26 copies), 5Y5nsbGf (+20.51, holds 119 s, 41 copies), GYhRMtoD (+106.15, 99 copies, every exit +2% to +5%; its buys
move the price +11.8%; buys the same 97 coins as AjSHVErb and AB797pqG: a group). sssssyv2 makes +272.87 itself on 570
coins and its copies lose: the profit is its speed.

**GYhRMtoD, its own history (s2, `ONLY_OWN=1`, `out_s2_GYhRMtoD_own.txt`; 2,727 transactions, a few cents of Triton):**
+249.94 SOL over 5 days (Nov 17 +1.54, Nov 18 +40.00, Nov 19 +71.72, Nov 20 +64.46, Nov 21 +72.21), up every day; 219
coins, all SOL-quoted, **215 won**, median +1.22 SOL a coin; without its best 5 +232.04. Every first buy is the same
2.18 SOL (p25 = p75); its last sale a median 47 s after its buy; 31 coins still held (counted as losses at their cost).
**It is a launch bundle, not a trader.** On the local Nov 19 tape (14 of its coins) it buys in the coin's create slot
on 13 of them, with 10-16 buys of 21.1-21.4 SOL in all in that slot, the same wallets each time (AjSHVErb, EEgAM69n,
4G3HtW63, 8FJmuXU7, GtJuY3Jc, 8eAScSkR, 9fxcdiWp, AB797pqG: 13 of 13 coins each), and it first sells 61-73 slots later
(about 25-30 s; 116 once). Its profit is the create slot, which a copy cannot reach: we would buy at slot+1 on top of
the group's ~21 SOL and sell into its exit. The screen's +2% to +5% on its 99 copies is the move the group's own
buying leaves behind, which lasts only while the group keeps launching. Not a candidate. A new screen rule follows:
a wallet whose first buys are mostly in the coin's create slot, with the same co-buyers, is a bundle.

**The chance line, corrected (Nov 21, the owner: "how are you scoring chance").** Each real wallet in the final list
gets a pseudo-wallet with the same copy counts a half, its sizes and coin kinds kept (so the same 15 tuning choices),
the copies drawn at random; the same pick on half 1 and score on half 2 runs, and the count "up on both halves" is
compared. Until now the copies were drawn from every copy of the tape, including the speed traders' and the losers'
(the pooled mean is -4% to -9% a copy), which set chance too low and made the real list look better than it is. Now
they are drawn from the copies of the wallets that passed the filters, 20 draws (`NULL_DRAWS`), and the line prints
the range and how many draws reach the real count. Local Nov 19 tape (2.5 h, 8+ copies): 4 of 21 up on both halves,
chance 4 (range 1-7), 11 of 20 draws reach it: nothing found, as expected on 2.5 hours.
**The box, Nov 21, with the corrected chance (23.6 h, 158,442 copies; the owner's paste):** out 586 speed traders, 19
flat, 299 losing themselves; **42 of 234 up on both halves against chance 33 (range 24-40; 0 of 20 draws reach 42)**;
the 30th best second half +6.0% against chance's +4.6%. The first time the list beats chance, by about 9 wallets, which
are not named by it (most of the 42 are still chance), and launch bundles like GYhRMtoD may be part of the excess.

**The bundle filter (Nov 21, after GYhRMtoD), from the tape, free:** a coin's create slot is its first slot on the tape
when the curve was still untouched (virtual tokens before that trade 1.0725e15 or more; pump starts at 1.073e15). A
wallet with half or more of its copies bought in the create slot (`BUNDLE`, default 0.5) is left out as a launch
bundle: its profit is a slot a copy can't reach. Local Nov 19 tape: 10 wallets left out (the 5 "flat" ones among them),
4 of 20 up on both halves against chance 4 (range 2-7).

**The watch list's own histories (s2, `ONLY_OWN=1`, `out_s2_watch4_own.txt`, Nov 21; a few cents of Triton).** Own
result over its days in the last 14 (token coins at Jupiter's price now; coins still held count at their cost):

| Wallet | Own result | Days up | SOL coins: won, median a coin, without the best 5 | Buy size p10-p90 | Its buy price / pump's start price (median) | First sale (median) |
|---|---|---|---|---|---|---|
| 5Y5nsbGf | +139.39 SOL, 14 days | 13 of 14 | 64%, +0.099, +53.9 (of +73.4) | 1.33-1.58 SOL | 1.67x | 71 s |
| AZ1eJ671 | +59.10 SOL, 5 days | 4 of 5 | 30%, -0.021, +21.3 (of +58.5) | 0.65-1.53 SOL | 1.13x | 41 s |
| FyRmQ8oS | -141.23 SOL, 8 days | 1 of 8 | dropped | | | |
| 3orcPHLt | -48.79 SOL, 13 days | 2 of 13 | dropped | | | |
| (GYhRMtoD, for comparison) | +249.94 SOL, 5 days | 5 of 5 | 98%, +1.223, +232.0 | 2.18 SOL every time | 1.71x every time | 13 s |

FyRmQ8oS and 3orcPHLt lose themselves: dropped by the own-result rule. AZ1eJ671 buys at 1.03-1.31x pump's start
price: the coin's first buy, most likely its creator's (a launcher, not a reader), and its profit leans on a few coins.
5Y5nsbGf is the one left: up 13 of 14 days, sizes that vary, no fixed pattern, but it too buys early on the curve
(1.27-2.68x the start price), so a copy enters after it on a young coin; the full copy test (part 2) would say whether
that entry still pays.

**5Y5nsbGf, the staged copy test (`s3_staged.py`, `out_s3_5Y5nsbGf.txt`, Nov 21; COST 0.0064, 1 SOL a copy, slot+1,
refused over 1.5x): stopped at the seen half.** Its 575 past first buys (Nov 8-21) split in time; on 18 copies of the
older half (2 refused) every exit loses: w4 -4.0%, its -20.7% then -10.9%, tp2 -13.6%, held 300 s -41.7%, scalp -3.2%
(the best, not above 0), so the newer half was never fetched. 10,354 coin trades fetched in all (each coin to 640 s
after its buy). Its own +139 SOL comes from buying first on young coins (1.7x pump's start price, median); a copy a
slot later buys into the coins it then sells. Not copyable. 18 copies is a small sample (a copy's spread is about 58
points), but no exit is positive and holding loses 42% a copy.

**Six more own histories (`out_s2_six_own.txt`, Nov 21 evening; cents of Triton): none worth the copy test.** The first
tape's top five that were never checked (their run was stopped this morning) and 3dwZP6T8 (Oct 29: re-score after a week):
DGapgQYU -206.54 SOL (1 of 5 days up), FT6LnH4J (pair A) -151.31 (4 of 13), 449LVsaM -56.67 (3 of 15), ACHz1zp8 -40.35
(1 of 6), 4cRLV1fw (pair B) +6.12 (7 of 10), 3dwZP6T8 no pump trade in 14 days. 4cRLV1fw's plus is on its token coins
(valued at Jupiter's price now); on its 196 SOL coins it is -3.43 SOL, 35% won, -18.39 without its best 5, so no copy
test. Of the eleven recorder wallets checked today, two make money themselves (GYhRMtoD, a bundle; 5Y5nsbGf, failed the
copy test) and none is copyable: the Nov 26 screen on 5 days of tape, with the own-result and bundle filters, is next.

**The new box's tape, first screen (Nov 21 ~21:50 UTC; the owner's paste; 7.9 h, 9 files, 335 MB, disk 6% used):**
1,624,414 trades, 66,284 copies (4,604 refused over 1.5x); 10+ copies a wallet; out 529 speed traders, 71 launch
bundles (the new filter), 275 losing themselves, 2 flat. **39 of 148 up on both halves against chance 36 (range 26-41;
5 of 20 draws reach 39)**, the 30th best half 2 +6.1% against +5.9%: nothing above chance on 8 hours, as expected.
Top by score: Be6s18aT (5 / 5 copies), 9rThNMRn, 4vw54BmA (14 / 16, its buys 2.93 SOL, holds 81 s, own +33.78 SOL on the
tape, impact +10.7%: its own buy moves the coin, as 4S5L64Va's did), G1aToexm. 6nWLPrww (pair B; 4cRLV1fw's own history
was -3.43 on SOL coins) is back at -1.1%.

**Bought data instead of the tape? Checked Nov 21, not taken (the owner: "just continue recording, it's the cleanest").**
Bitquery's Data Store sells every pump curve trade as Parquet ($300 the latest month, $1,500 six, $3,000 twelve; T+1):
its free sample (486 trades, 50 slots) has slot, position in the block, signature, trader, both amounts and the quote
mint, but no curve reserves, which our copy model needs; they could be rebuilt from the curve constant (our tape: 57% of
SOL-coin trades on pump's standard curve, virtual SOL x tokens = 30 x 1,073M), with each coin's fee tier unknown. Dune's
docs show no pump.fun curve table. Helius `getTransactionsForAddress` filters to successful transactions only (for
flooded wallets like 4vw54BmA; Developer plan). The recorder stays the source; one wallet is read from it with WALLET=.

**The hot hand (`STREAK=1`, Nov 22, the box's tape: 10.8 h, 94,536 copies): no.** At each copy, a wallet is "hot" when
its last 3 or 5 copies already closed (within 2 or 6 h) averaged over 0% or 20%; speed traders optionally out. 80 rules
(5 exits x 2 looks x 2 k x 2 thresholds x speed in/out): hot wallets' next copies are 1-4 points better than the rest's
in most rows, but **not one row is positive on either half** (the best: scalp, 2 h, k 5, over 20%: -2.4% / -8.0% on
826 / 1,057 copies; tp2, 6 h, k 5, over 0%, speed out: -4.8% / -7.4%; the rest at -6.7% / -8.4% and -8.1% / -11.6%).
A streak says a little about the next copy, far from enough to pay for the slot-late entry.

**The new tape's top 20, own histories (Nov 22 ~01:00 UTC; `out_s2_top20_own.txt`; the screen on 10.9 h: 40 of 178 up
on both halves against chance 32, range 23-45, 1 of 20 draws reaching 40).** The 20 up on both halves and not already
known, 14 days each, `MAXPAGES=30`. Losing themselves (dropped): BuZdtPyH -25.06, 5gR8zqCr -10.34, HgExUFKQ -26.52,
5AmLiWon -15.42, 7q2RycsP -10.83, 3LHFZQrF -100.66, 6FJhAwzt -194.35, 91VbDHW5 -91.04, 6ACyUAvL -7.50; flat: 2SSNK22o
+0.65, 68xaw2jz -0.08; Bi4rd5FH no pump trade read. Making money: 6ua7w2Gv +191.75 (12 of 15 days) and 7djZvJGN +10.10,
both tested in depth Nov 17-18 and failed with more data (docs/22); **to the staged copy test: 8KwpTZNY +64.05 (12 of
14 days; its buy at 1.11x pump's start price, median: the coin's first buyer, maybe its creator), 2pLugeBD +35.87 (11 of
15; first sale 403 s, median: a long holder), 6HpWkb1D +26.99 (11 of 15), 7hnXt9cK +21.74 (9 of 13), Dctam1na +17.00
(6 of 8)**; GYFFxWSN +9.89 on 4 days, token coins only, left for later.

**The five, staged copy test (Nov 22; `out_s3_8Kw_2pL.txt`, `out_s3_6HpWkb1D.txt`, `out_s3_7hnXt9cK.txt`,
`out_s3_Dctam1na.txt`; COST 0.0064, 1 SOL a copy, slot+1, refused over 1.5x): none copyable.**

| Wallet | Seen half: the exit picked | Unseen half, blind | Without its best 2 | Verdict |
|---|---|---|---|---|
| 8KwpTZNY | tp2 +5.1% (19) | +2.9% (18) | -7.3% | too thin; a coin's first buyer |
| 2pLugeBD | held +42.6% (9; 11 of 20 refused) | held -18.4% (3; 7 of 10 refused) | | stopped; its coins jump past 1.5x before we land |
| 6HpWkb1D | w4 -2.8% (19) | | | stopped at the seen half |
| 7hnXt9cK | tp2 +18.2% (18) | -2.3% (20) | -11.6% | fails |
| Dctam1na | **w4 (our live exit) +10.2% (34)** | **+2.1% (33)** | -9.0% | fades; its 68 buys since Nov 13 all tested |

**Speed (Nov 22):** the coin replay batched on Triton (`23c39dd`: one coin 9.5 s -> 2.0 s) and then read from Helius's
`getTransactionsForAddress` (`0a5bdd6`, `HELIUS_URL`: 0.7 s, the same trades, the true block order). Dctam1na's 68
coins (14 new) took 15 s. A wallet test is now seconds, and about 10 credits per 100 transactions on Helius.

**The top 60 + TOPOWN 60 through `w2_grid.py` (Nov 22 ~01:35-02:20 UTC; 103 wallets after duplicates; Helius; outputs in
`out_w2/`, the list in `out_w2/_wallets_tested.txt`).** The screen on 11.6 h: 32 of 182 up on both halves, chance 32.

| Outcome | Wallets |
|---|---|
| stopped: loses money itself, or up on under half its days | 51 |
| stopped: the smoothed seen pick not above 0 / under 10 seen copies | 5 / 3 |
| failed the blind half | 33 |
| no result (Jupiter returned no SOL price) | 2 |
| passed the blind half, positive also without its best 2% | 9 |

The nine (seen pick -> blind, per copy; "live" = wallet 4's live settings on the same blind copies):

| Wallet | Own history | Seen pick | Seen | Blind | Blind w/o best 2% | Live, blind |
|---|---|---|---|---|---|---|
| 4MzQcBVN | +107.56, 6 of 7 days | tp 3.2, 420 s, sp 15/60, stall 240, its sale never; 1.3+ SOL, all, limit 1.5 | +11.2% (56) | **+6.1% (57)** | +1.51 SOL | +2.41 SOL (57) |
| HUqA7h6t | +60.85, 12 of 14 | tp 2.4, 150 s, sp off, stall 240, never; 0.5+, token coins, limit 2 | +19.7% (30) | **+9.3% (34)** | +1.80 | -0.34 (1) |
| 6ua7w2Gv | +191.75, 12 of 15 | tp 4.0, 420 s, sp off, stall 300, its sale 0-120 s; 0.5+, all, 1.25 | +17.2% (60) | +5.9% (60) | +0.81 | -1.83 (3) |
| 37nt6zYZ | +90.85, 8 of 9 | tp 1.8, 60 s, sp 10/30, stall off, 30-290 s; 0.5+, token, 1.25 | +10.9% (17) | +2.8% (33) | +0.14 | +3.47 (16) |
| 6t5G5f1i | +39.50, 1 day | tp 1.7, 60 s, sp 5/30, its sale 0-120 s; 0.5+, all, 1.5 | +31.9% (36) | +36.4% (36) | +8.73 | none |
| 67Tw9tF3 | +9.80, 2 days | tp 1.5, 210 s, sp 5/120, stall 180, 30-290 s; 0.5+, all, 1.25 | +19.5% (11) | +19.3% (12) | +1.71 | +1.23 (10) |
| G1aToexm | +12.73, 2 days | tp 1.8, 150 s, sp 15/30, stall 120, 0-120 s; 0.5+, all, 1.25 | +7.4% (15) | +7.6% (16) | +0.54 | +3.14 (6) |
| 7Np3cHU4 | +3.56, 4 days | tp 1.3, 300 s, sp 15/30, stall 300, 0-60 s; 1.0+, all, 1.25 | +6.8% (12) | +2.3% (14) | +0.02 | -1.41 (14) |
| 4vw54BmA (1 day, capped) | +4.48 | tp 2.2, 120 s, sp 3/30, stall 60, 30-290 s <1.5x | +21.0% (10) | +14.3% (10) | +0.38 | +0.78 (10) |

**4vw54BmA on 5 days (`out_w2/4vw54BmA_5days.txt`; 476,418 successful transactions, ~47,600 credits): FAIL.** Own +121.72
SOL (4 of 5 days up); seen pick tp 2.8, 90 s, its token coins +8.3% a copy on 83, blind **-0.1% on 77** (-2.57 without its
best 2%); wallet 4's live settings -15.87 seen, -0.08 blind on 149. Its one-day pass was luck.

Caveat: 103 wallets were tested, so a few blind passes are expected by luck alone (4vw54BmA showed how a short history
flatters). The ones with weeks of history and 30-60 blind copies (4MzQcBVN, HUqA7h6t, 6ua7w2Gv) are the candidates; each
needs a second blind check: its buys after Nov 22, from the tape (free), before any money. Credits: own histories
1,080,483 transactions (~108,000 credits) plus the coin replays.

**The three, under the stricter test (`w3_robust.py`, Nov 22; `out_w2/w3_*.txt`): all fail.** 48 settings fixed before
the data (8 exits x quote all/SOL/token x its buy 0.5+/1.3+, limit 1.5x), all first buys of 0.5+ SOL (6ua7w2Gv: 700 of
2,079 at random), 4 blocks in time, 3 rolling blind blocks, and a luck baseline (the same pick on copies with each
setting's mean taken out).

| Wallet | Copies | Blind blocks (% a copy, n) | All blind | Without best 2% | Positive blocks |
|---|---|---|---|---|---|
| 4MzQcBVN | 328 | -8.1 (22), +26.7 (24), -7.0 (41) | +2.0% (87) | -2.01 SOL | 1 of 3 |
| HUqA7h6t | 603 | +2.0 (77), -11.3 (73), +2.7 (104) | -1.5% (254) | -11.00 SOL | 2 of 3 |
| 6ua7w2Gv | 700 | -2.8 (175), +1.4 (175), +2.2 (175) | +0.3% (525) | -15.12 SOL | 2 of 3 |

On the seen blocks the picks did no better than the luck baseline (4MzQcBVN +24.8 / +12.4 / +16.5% against luck +27.8 /
+15.3 / +19.5%). The w2_grid passes (+6.1%, +9.3%, +5.9% blind on 57 / 34 / 60) came from the 24.5-million-setting pick
and the 60-buy samples. All three make money themselves (+60 to +192 SOL in 1-2 weeks); a copy a slot later does not.

**The new screen (Nov 22 ~04:25 UTC; 17.1 h of tape, 133,514 copies; TOPMEAN = the 5 fixed exits' mean, can't-copy
filters only) and the strict test (`w3_robust.py` with gate 1; `out_w3/`).** The batch of the 60 new wallets was stopped
after 4 (Helius bills about 100 credits per `getTransactionsForAddress` request, not 10 per 100 transactions: today
~7,200 requests, ~800,000 of the free plan's 1,000,000 credits). GrFVXkgm: gate 1 fails (-45.0 / -37.0 / -14.4%). Two
chosen by hand from the screen:
- **6t5G5f1i** (71 tape copies, the 5 exits' mean +9.9%; own +39.50 on its one day): gate 1 passes (+5.0 / -18.4 / +24.0),
  the picks blind -14.0 / -12.5 / +24.2% (18 each): -0.8% a copy on 54, -10.28 without the best 2%: **FAIL**.
- **CqCAzte8** (24 tape copies, +19.3%; own +11.93 SOL over 15 days, up on 9): **PASS.** Gate 1 (the 8 exits' mean, no
  pick) **+7.0 / +8.9 / +13.1%** on the 3 blind blocks; the picks (tp 2x / 120 s SOL coins, then tp 3x / 420 s / stall 240
  all coins) seen +14.4 / +11.2 / +11.2% against luck +6.4 / +3.4 / +8.1%, **blind +8.0 / +6.1 / +19.9% (27 / 25 / 37):
  +12.4% a copy on 89, +7.37 SOL without the best 2%, 3 of 3 blocks.** 150 of its 270 first buys of 0.5+ SOL (Nov 8 - 22).
  Its profile: not a bundle (7% of its SOL buys the same size; 0.48 / 0.96 / 2.43 SOL p10/50/90), not a first buyer (2.81x
  pump's start price, median), first sale 36 s after its buy (median; p25 16 s); 11 to 52 first buys a day (all sizes);
  239 SOL coins and 149 token coins (TTWO 26, PUMP 9, WBTC 8, SPCX 4 of them our floats). Next: its buys after Nov 22 on
  the tape with the settings frozen (free), then paper.
CqCAzte8's exits on its blind blocks (`out_w3/CqCAzte8_table.txt`, `w3_sp_check.py`; 112 copies): every menu exit
positive; tp 3x / 420 s / stall 240 the best (+7.8 / +19.3 / +19.9 = +15.6%, +13.74 SOL without the best 2%), its token
coins +29.7% (36) against SOL coins +8.9% (76); following its sale the weakest. Sell pressure on top of it (3-15 sells
over 30-120 s): +8.9% to +12.6%, steadier in the first blind block (+6.5 to +13.9 against +7.8), lower in all: within
the noise of one another (about 5.5 points either way on 112 copies).

**CqCAzte8 on ALL its buys (Nov 22; `out_w3/CqCAzte8_all.txt`, `w3_kind_table.py`): still PASS.** The 150-buy samples
moved between runs (a sample drawn from a list that changes with the day's token prices: the SOL coins read +8.9% on
one draw, +1.1% on the next), so every one of its 268 first buys of 0.5+ SOL was replayed. Gate 1 +5.7 / +6.3 / +16.8%;
the rolling picks blind +2.1 / +5.9 / +20.8% (41 / 67 / 30): +8.0% a copy on 138, +5.90 SOL without the best 2%, 3 of
3 blocks. tp 3x / 420 s / stall 240 by kind, at 1 SOL a copy, the three blind blocks (67 copies each):

| Coins | Block 2 | Block 3 | Block 4 | All blind | Without its best 2 |
|---|---|---|---|---|---|
| token-priced | 26: +9.18 SOL (+35.3%) | 20: +4.46 (+22.3%) | 30: +6.26 (+20.9%) | 76: **+19.90 SOL (+26.2%)** | +16.16 |
| SOL-priced | 41: -4.90 (-12.0%) | 47: +5.92 (+12.6%) | 37: +9.43 (+25.5%) | 125: **+10.45 SOL (+8.4%)** | +5.49 |
| all | 67: +4.28 (+6.4%) | 67: +10.39 (+15.5%) | 67: +15.69 (+23.4%) | 201: **+30.35 SOL (+15.1%)** | +21.31 (w/o 4) |

**Three more from the screen's top (Nov 22; `out_w3/`, `w3_robust.py`, 80 buys for 2xKDETTh): none.** CULikuY6 -24.87
SOL itself over 13 days (3 up) and 897GsVaF -77.71 (1 up): stopped at their own history. 2xKDETTh +6.68 (8 of 14 up),
gate 1 -8.4 / +3.4 / +14.9% (passes), the rolling picks fail the blind blocks: FAIL.

**The Nov 22 evening read (30.7 h of tape; `own_only.py`, `out_own/`, `out_w3/`).** The screen's TOPMEAN60 and TOPOWN60
(the 10 jumpy left out): 62 never tested before. Their own history (Helius, MAXPAGES 10, about 22k credits): 42 lose
money themselves, 20 make it. Six of the 20 deep-tested on 80 buys each (`w3_robust.py ... 80`):

| Wallet | Its own result | Gate 1 (menu mean, blocks 2/3/4) | Blind picks, % a copy (n) | W/o best 2% | Result |
|---|---|---|---|---|---|
| 2hntf9Ud | +52.0 SOL, 14 of 15 days up | +12.6 / +18.3 / +20.7% | +3.4 / +18.1 / +27.0 = **+18.1%** (52) | +6.93 SOL | PASS, 3 of 3 |
| G3PMGr5q | +16.1, 8 of 14 | -13.5 / +13.4 / +11.4% | -6.4 / +35.6 / +36.4 = +21.5% (38) | +5.38 | PASS, 2 of 3 |
| afi1ee2X | +26.2, 10 of 14 | +4.5 / +14.8 / -3.8% | +9.0 / +27.7 / -1.0 = +9.1% (42) | +1.54 | PASS, 2 of 3 |
| 9QAEGBhQ | +150.9, 14 of 14 | +11.0 / +9.6 / +8.7% | +0.4 / +4.1 / +10.7 = +5.1% (60) | +0.35 | PASS, 3 of 3 (thin) |
| 3SiQo8MJ | +23.6, 8 of 10 | +4.9 / +4.6 / +28.2% | +1.2 / -1.2 / +8.2 = +2.7% (60) | +1.11 | PASS, 2 of 3 (thin) |
| 3PwXa9BR | +121.1, 12 of 14 | -8.7 / +6.3 / -21.4% | +1.8 / -0.8 / -12.7 = -4.2% (57) | -4.14 | FAIL (gate 1) |

80 buys is a sample: CqCAzte8's 80-buy pass held on all its buys, others moved between samples. Next: all buys of
2hntf9Ud (176) and G3PMGr5q (236); the coins already replayed are cached.

**All buys (Nov 22; `out_w3/2hntf9Ud_all.txt`, `out_w3/G3PMGr5q_all.txt`, TABLE=1).**
- **G3PMGr5q: FAIL on its 237 buys** (gate 1 +0.2 / -14.1 / +9.2%; the picks blind -10.7% a copy, 0 of 3 blocks). Its
  80-buy pass was luck.
- **2hntf9Ud: PASS on its 177 buys** (gate 1 +6.3 / +0.4 / +15.1%; the picks blind +10.4% a copy on 132, +7.58 SOL
  without the best 2%, 2 of 3 blocks). tp 3x / 420 s / stall 240 alone: +14.0 / +7.5 / +24.5 = +15.3% (132), +13.32 SOL
  without the best 2%; its token coins +24.3% (53), SOL coins +9.3% (79).
- **But 2hntf9Ud is CqCAzte8's twin**: 266 of its 281 coins are CqCAzte8's, 246 of them bought in the same slot, the
  same size (median ratio 1.00), and mostly sold in the same slot; the same hours (14:00-03:00 UTC). One operator, two
  wallets. Nothing new to copy (the live `rugsnipe-long-cq` already holds those coins), but an independent second
  confirmation of CqCAzte8's edge with the same exit, and a spare wallet if CqCAzte8 goes quiet.
- **afi1ee2X: FAIL on its 215 buys** (`out_w3/afi1ee2X_all.txt`): gate 1 +3.7 / +8.8 / +0.5% (passes), the rolling picks
  blind -9.3 / -2.7 / -13.8% (-8.6% a copy on 83, 0 of 3 blocks): each block's pick (token coins held 300 s, SOL coins
  live without its sale) was the noise of the blocks before it. Of note, not a pass: CqCAzte8's exit, fixed before this
  wallet was seen (tp 3x / 420 s / stall 240, all coins), +5.7 / +10.9 / +4.4 = +7.0% (161), +4.78 SOL without the best
  2%. On the watch list for a forward check on the tape, with that exit frozen.

**Why afi1ee2X and G3PMGr5q reached the deep test (Nov 22, the owner: "did you do the screening correctly?").** The
screen ranks 1,907 wallets on 30.7 h of tape, most with 10-30 copies there, every copy's mean -9.3%: its top 60 is
mostly the lucky tail, a shortlist and not a verdict. The 80-buy stage was too weak to sort it: 5 of 6 passed, and 2 of
the 3 then run on all their buys failed. From now on: own history, then all buys, no 80-buy stage.
A check from cache (`PICK_ALL=1`: the pick among the 8 exits on all coins only, no SOL/token or 1.3 split;
`out_w3/*_pickall.txt`), to see whether the 48-setting menu caused the fails. It did not:
| Wallet | Gate 1 | Blind, % a copy (n) | W/o best 2% | Result |
|---|---|---|---|---|
| CqCAzte8 | +3.1 / +6.5 / +17.8% | +4.5 / +6.4 / +12.6 = +7.8% (197) | +10.49 SOL | PASS, 3 of 3 |
| 2hntf9Ud | +6.3 / +0.4 / +15.1% | -0.7 / -5.1 / +24.5 = +6.3% (132) | +2.46 | FAIL, 1 of 3 |
| afi1ee2X | +3.7 / +8.8 / +0.5% | +10.1 / +2.2 / -4.0 = +2.8% (161) | -6.74 | FAIL |
| G3PMGr5q | -0.7 / -14.1 / +9.2% | +3.2 / -18.6 / -1.6 = -5.7% (177) | -20.85 | FAIL (gate 1) |
afi1ee2X's small edge on simple exits rests on a few big wins (negative without its best 2% either way). CqCAzte8 passes
both ways; its twin's pass depends on the rule (its block 3 is weak), so CqCAzte8 stays the one copied.

**A stop loss for CqCAzte8's live exits? No (Nov 23; `w3_stop.py`, `out_w3/CqCAzte8_stop.txt`).** The owner, after a
-70% SOL-coin copy on its first live day (10 closed, -0.217 SOL at 0.5 SOL a copy): "test if we should add a stop loss,
because there is no sell pressure". All 263 first buys of 0.5+ SOL, the live exits, the stop as the bot has it (the
price at or under STOP x its buy price, sold at the next trade), % a copy at 1 SOL, its buys in 4 time blocks:

| Stop | Token coins (93), all | W/o best 2% | SOL coins (170), all | W/o best 2% |
|---|---|---|---|---|
| none (live) | +15.9% | +11.07 SOL | +9.2% | +11.92 SOL |
| 0.9x | +10.5% | +6.07 | -3.5% | -8.85 |
| 0.8x | +10.1% | +5.62 | +1.8% | -0.68 |
| 0.7x | +16.6% | +11.70 | +5.6% | +5.67 |
| 0.6x | +16.0% | +11.16 | +7.7% | +9.34 |
| 0.5x | +16.5% | +11.60 | +9.3% | +12.08 |

Three in four of its copies dip under 0.9x before the exit and a third under 0.7x, and most come back: a tight stop
sells them at the low. 0.5x and lower changes almost nothing (6-7% of copies reach it). No stop. The first live day is
within the noise: a copy's result swings 57 points (sd), and 20% of 10-copy stretches in its history are at or under
-4.3% (the worst -26.4%).

**Screen of Nov 22, 31.4 h, MIN_COPIES 20:** 22 wallets not tested before; 10 lose money themselves, 12 make it. Twins
(same coins, same slot): DEdwtjvC = BWiJ8aqk (741 shared, 737 same slot; both sell in a median 19 s: too fast) and
2pLugeBD = 3GzBLpxT (313 / 309). Deep-tested: 8NdJBkpc (up 15 of 15 days, 250 of its 633 buys at random) and
AmeY3DxM (up 12 of 13, all 224).
- **8NdJBkpc: FAIL** (`out_w3/8NdJBkpc_all.txt`, 250 of its 634 buys at random): gate 1 +0.0 / -11.1 / +3.8%; every
  exit on all coins -1.3 to -4.7% a copy blind. Up on all 15 days itself, but its copies lose: what it makes, it makes
  in the seconds a copy lands after it.
- **AmeY3DxM: FAIL** (`out_w3/AmeY3DxM_all.txt`, all 224): gate 1 +1.2 / -1.9 / +5.1%; the picks +1.3% a copy, 3 of 3
  blocks, but -0.06 SOL without the best 2%. Too thin to pay.

**How alike are the twins? (Nov 23; the owner: "are you sure the twins only trade on the same coins?")** Over the hours
both histories cover:

| Pair | Coins each | Shared | Only the first | Only the second | Same buy slot | Same size (±10%) | Same first-sale slot |
|---|---|---|---|---|---|---|---|
| CqCAzte8 / 2hntf9Ud | 369 / 276 | 269 | 100 (about 7 a day) | 7 | 246 of 269 | 253 | 206 of 262 (2hntf9Ud first on 45, CqCAzte8 on 11) |
| DEdwtjvC / BWiJ8aqk | 745 / 741 | 741 | 4 | 0 | 737 | 215 (median ratio 0.87) | 719 of 732 |
| 2pLugeBD / 3GzBLpxT | 320 / 320 | 313 | 7 | 7 | 309 | 311 | 258 of 286 |

The buys are one operator's; the sales differ more. On their shared SOL-priced coins CqCAzte8's own result is +5.89 SOL,
2hntf9Ud's +38.99, and 2pLugeBD +17.95 against 3GzBLpxT -6.82: the same entries, sold differently (the cq unit never
follows its sale, so this does not touch our copies). CqCAzte8 is the one to copy: its 100 coins the twin does not buy
are copies the twin would miss; the twin's own 7 (+1.57 SOL on 6 SOL-priced) are about one every two days.

**Is the cq unit getting all it can from CqCAzte8? (Nov 23; `w3_small.py`, `out_w3/CqCAzte8_uncopied.txt`)** Fresh
history (Nov 8-22, 374 first buys). What the unit copies (0.5+ SOL, paid in SOL or our floats): 212, +8.1% a copy at 1
SOL. What it leaves: buys of 0.3-0.5 SOL, +0.7% a copy on 64 (the 0.5 floor is right); under 0.3, 10; buys paid in
mihao (4CxjZyMN), 10 copies +53.3% but 9 of them Nov 10-13, it stopped; in PAID (98kfF7rm), 11 copies +65.6% (+5.37
SOL without the best), 10 in the newer half, none since Nov 20. max_open 2 was never full when it bought. Off the pump
curve it mostly sells (pumpswap after graduation); its buys there are about one a day.

**Screen of Nov 23, 34.2 h (Nov 23 ~02:30 UTC):** 13 wallets not tested before (`out_own/_untested_nov23_34h.txt`), not
checked: the Helius key answered "max usage reached" (its credits are spent). Check them when credits are back.

**Screen of Nov 23, 48.9 h (a new Helius key):** 39 wallets not tested before (the 13 of the 34 h screen among them).
Own history: 22 lose money themselves (among them DNio5ket, E8B7Edi7, BtHnhjh8 and 7bwGevcZ, the 100+ copy wallets
near the screen's top: -66 to -115 SOL themselves), 17 make it. Twins again (same coins, same slot): GoJM9nYG =
DTru6k9o (242 of 247), 965Nk2u3 = H8w4pyiU = 2vt36ruE (344-349 of 355), HCq8h5ad = GXRNpTLc (859 of 868), CmnzeFCA =
4DH3hwDs. Deep-tested: GoJM9nYG (the screen's #1), 43E8Uor7 (up 14 of 14 days), CgyPomTG (13 of 15), all their buys;
HCq8h5ad (15 of 15, holds a median 120 s) on 250 of 828 at random.

| Wallet | Gate 1 | The 48-setting pick, blind (n), w/o best 2% | The pick on all coins only (`PICK_ALL`) | tp 3x / 420 s / stall 240 alone (CqCAzte8's exit) |
|---|---|---|---|---|
| GoJM9nYG (all 213) | -5.1 / -6.0 / +16.4% | -6.8% (53), -5.05 | | |
| 43E8Uor7 (all 253) | +1.9 / -1.2 / +6.0% | +4.0% (84), +0.32: PASS | +1.5% (189), -4.56: FAIL | +3.6 / +1.7 / +10.6 = +5.3%, +1.60 |
| **CgyPomTG** (242 of 244) | +13.7 / +1.4 / +10.5% | +4.4% (149), -1.65: FAIL | **+7.7% (181), +3.78: PASS** | **+13.1 / +11.0 / +12.3 = +12.1% (181), +12.04** |
| HCq8h5ad (250 of 828) | -10.5 / -7.8 / -17.3% | +2.2% (61), -1.61: FAIL | | -20.3% |

43E8Uor7 passes one way and fails the other, both thin. **CgyPomTG**: fails the 48-setting pick (it chased the 1.3+ SOL
slice), passes the pick on all coins, and CqCAzte8's exit, fixed before this wallet was seen, is positive in all three
blind blocks with +12.04 SOL on 181 copies without the best 2%. Its own: +55.07 SOL over 15 days, 13 up; 22 coins a day
(SOL 189, TTWO 42, USDC 24, SPCX 10, hSOL 8 of its first buys), its hours 12-02 UTC; median hold to its first sale 40 s.
Independent: 24 coins shared with CqCAzte8, 17 with wallet 4, none in the same slot.

**CgyPomTG's setup (Nov 23; `w3_setup.py`, `out_w3/CgyPomTG_setup.txt`):** coin kind x its buy size x the 8 exits, no
pick, the 4 time blocks of its 242 copies at 1 SOL; trusted only if positive in 4 of 4 blocks and without the best 2%.

| Coins, its buy | Exit | Blocks 1 / 2 / 3 / 4 | All (n) | W/o best 2% |
|---|---|---|---|---|
| **all, 0.5+ SOL** | **tp 3x / 420 s / stall 240** | +9.0 / +13.1 / +11.0 / +12.3% | **+11.4% (242)** | **+15.52 SOL** (the best cell) |
| all, 0.5+ | held 300 s | +11.3 / +14.1 / +10.5 / +12.0% | +12.0% (242) | +10.38 |
| SOL coins, 0.5+ | tp 3x / 420 s / stall 240 | +9.6 / +18.8 / +12.9 / +11.2% | +12.9% (136) | +11.55 |
| SOL coins, 0.5+ | tp 2x / 120 s (the cq unit's SOL exit) | +5.5 / +7.4 / -2.3 / +11.1% | +5.5% (136) | +3.24 |
| token coins, 0.5+ | tp 3x / 420 s / stall 240 | +7.8 / +6.3 / +9.1 / +13.7% | +9.3% (106) | +4.05 |
| all, 1.3+ | tp 3x / 420 s / stall 240 | +14.9 / +15.4 / +10.8 / +1.7% | +10.5% (188) | +9.90 |
| all, 0.5-1.3 | tp 3x / 420 s / stall 240 | -1.4 / +3.6 / +12.0 / +54.8% | +14.2% (54) | +5.74 (one block) |

The setup: every buy of 0.5+ SOL, any coin, the one exit tp 3x / 420 s / stall 240, SOL coins included and with that same
exit (not the cq unit's tp 2x / 120 s, which is half as good here and negative in one block). No size or kind filter: the
splits are smaller and no steadier.
Sell pressure on top of it (`w3_sp_check.py`, `out_w3/CgyPomTG_sp.txt`, the 3 blind blocks, 181 copies): none is best,
+13.1 / +11.0 / +12.3 = +12.1%, +12.05 SOL without the best 2%. Wallet 4's 5/60 s: +9.5% (+7.59), its block 3 -0.7%;
8/60 s +11.9% (+11.90), no better. No sell pressure.
- **965Nk2u3 (= H8w4pyiU = 2vt36ruE): FAIL** (`out_w3/965Nk2u3_all.txt`, all 334): gate 1 +0.1 / -10.7 / -5.4%; 7 of the
  8 exits lose on its copies (its sale +3.9%, negative without the best 2%). +123 SOL itself, up on 12 of 12 days.

**Where the edge goes (Nov 23; `w3_entry.py`, `out_w3/*_entry.txt`; the owner: "a totally different way to profit?").**
Our copy at 1 SOL entered right behind its buy (its own slot, the best any copier could do) against as the bot lands
(the end of the next slot), and the price we pay over its own:

| Wallet | tp 3x / 420 / stall 240: behind it / as we land | its sale: behind / land | Our price over its own (median) | Buyers in its slot before it |
|---|---|---|---|---|
| 965Nk2u3 | **+13.3% / -7.9%** | +28.9% / +4.9% | **1.32x** (over 1.2x on 87%) | its twins (2vt36ruE on 227 of 334), D4HZgnoP 88 |
| HCq8h5ad | -0.4% / -15.0% | +11.4% / -4.6% | **1.29x** (80%) | 6FWhUybW on 290 of 400, its twin GXRNpTLc 241 |
| CqCAzte8 | +16.9% / +15.0% | +7.8% / +6.0% | 1.02x (2%) | its twin 2hntf9Ud 94; none on 44% |
| CgyPomTG | +10.4% / +11.4% | +3.9% / +5.1% | 1.00x (1%) | none on 70% |

965Nk2u3 and HCq8h5ad buy inside a crowd that lands in the same block (their twins, 6FWhUybW, D4HZgnoP: one group
buying together; 965Nk2u3 at 32 SOL in the curve, a coin's first moments). The price rises about 30% inside that one
block; the edge is there and nowhere after it. Copying the leader lands the same block late; buying in their block
needs knowing the coin before it is bought (an insider's launch). Not reachable. The two we copy buy alone, so the
price waits for us (1.00-1.02x). A copyable wallet's mark: a median premium near 1.0x.

**The screen's late filter (Nov 23, the owner: "add it"; `s1_screen.py`, `MAX_PREM`, default 1.15).** A wallet whose
copies pay a median over 1.15x its own price (a refused copy counts as 1.5x) is left out as late, after the jumpy filter
and before both lists: its edge is inside its block (`w3_entry.py`). The run prints the late count with the best ten by
their own result and their price, the median price for wallet 4's, CqCAzte8's and CgyPomTG's copies when they are on
the tape, and a price column in the top 15 by the 5-exit mean. Checked on a made-up tape (a crowd of 8 buyers in each
coin's first block: the late ones left out, 1.20-1.36x; the rest listed with 1.06-1.13x).

**Screen of Nov 23 evening, 50.3 h, with the late filter (`run_screen.sh`, `sss`):** 137 wallets left out as late (among
them 965Nk2u3 and its twins, 1.24-1.38x); the copied three at 1.04x (wallet 4), 1.04x (CqCAzte8), 1.01x (CgyPomTG). 20
wallets not tested before: 11 lose money themselves, 9 make it; no twins. Deep-tested on all their buys:

| Wallet | Strict pick (48), blind | Pick on all coins | Price | Token coins, tp 3x / 420 / stall 240 (4 blocks) | Result |
|---|---|---|---|---|---|
| **3XeFcZKS** | +6.8% (89), +3.34 w/o 2%: PASS | +5.0% (203), +5.97: PASS | 1.00x, alone 99% | +8.4 / +5.5 / +13.1 / +17.3 = +10.9% (81), +5.07 | **passes both; token coins** |
| **6LwMLkCe** | +14.9% (107), +6.82: PASS | +5.6% (201), -0.96: FAIL | 1.01x | +2.5 / +9.0 / +6.6 / +14.9 = +8.2% (137), +2.87 (held 300 s +17.8%, +11.15) | passes the strict one; token coins |
| 7g5CJ754 | gate 1 -5.3 / -2.7 / -6.7% | | | every exit -2.6 to -6.4% | FAIL |

Both are their token coins' wallets: their SOL coins are noise (3XeFcZKS's at 32 SOL in the curve, a coin's first
moments). 3XeFcZKS: 23 coins a day, holds a median 159 s, token coins paid in TTWO 24, Xsc9qvGR 13, PUMP 9, SPCX 8.
6LwMLkCe: 24 a day, 42 s, its token coins paid in TTWO 84 of about 137. Independent of the copied three (2-33 shared
coins, never in the same slot).

**Sell pressure, all four new units (Nov 23 evening; `w3_sp_check.py` on each one's latest history, `out_w3/*_sp_nov23.txt`;
the owner: "you sure it is well studied on the other wallets?").** tp 3x / 420 / stall 240 with sell pressure off or 9
kinds, the 3 blind blocks, % a copy (w/o best 2% in SOL), on the coins each unit copies:

| Unit, coins | No sell pressure | Wallet 4's 5/60 s | The best kind | Verdict |
|---|---|---|---|---|
| CqCAzte8, token | +39.7 / +11.1 / +30.2 = **+25.5%** (+15.16) | +19.5% (+11.25) | 15/120 s +27.9% (+16.81) | none |
| CqCAzte8, all | **+17.4%** (+24.47) | +11.7% (+14.85) | none is best | none |
| CgyPomTG, all | +13.1 / +11.0 / +12.3 = **+12.2%** (+12.05) | +9.5% (+7.59) | none is best | none |
| 3XeFcZKS, token | +5.5 / +13.1 / +17.3 = **+11.8%** (+5.09) | +11.0% (+4.57) | 5/120 s +12.2% (+5.32) | none (no difference) |
| 6LwMLkCe, token | +9.0 / +6.6 / +14.9 = **+9.1%** (+4.51) | +10.5% (+6.23) | 5/30 s +13.0% (+9.20; blocks +2.0 / +14.2 / +28.7) | none, watch |

Sell pressure is never clearly better on these wallets: on three it costs, on 3XeFcZKS it changes nothing, and on
6LwMLkCe the higher means come from its last block (with sell pressure most kinds are near zero or negative in its first
block, without it every block is positive). Wallet 4 is the other way (`../../2026-11-23/w4_exit/`: without it its last
block is -14.5% against -2.9%): its coins dump on sellers, these wallets' coins come back.
How big against chance (`w3_sp_noise.py`, `out_w3/sp_noise_nov23.txt`): the same copies both ways, the gain a copy, its
standard error, and the share of 2,000 bootstrap reshuffles where it stays above 0 (9 kinds tried, so one kind near 90%
is what luck alone gives):
- 6LwMLkCe token (119): the best kind (5/30 s) +3.9 points, give or take 4.5; above 0 in 81%. Not shown.
- 3XeFcZKS token (59): every kind -2.7 to +0.4 points. Nothing.
- CqCAzte8 token (67): 8 of 9 kinds cost 2 to 8.5 points (above 0 in 6-30%); the gentlest, 15/120 s, +2.5 give or take
  1.3, above 0 in 98%: the one possible gain, on about 5 token copies a day; tried after seeing it, so re-checked on
  the live copies before any change.

**Screen of Nov 24 morning, 65.4 h:** 173 left out as late; the copied three at 1.01-1.04x. 41 wallets not tested
before: 23 lose money themselves, 18 make it. Deep-tested four:

| Wallet | Strict pick, blind | Pick on all coins | Price | Token coins, tp 3x / 420 / stall 240 (4 blocks) | Result |
|---|---|---|---|---|---|
| **6nNzEg86** (191, all) | +13.4% (62), +6.19 w/o 2%: PASS | +7.6% (143), +4.97: PASS, 3 of 3 | 1.02x, alone 84% | -3.7 / -5.9 / +32.7 / +26.5 = +17.2% (115), +15.80 | **passes both; token coins, but only its last two blocks** |
| 5xLpFzjY (300 of 519) | gate 1 -2.9 / -11.1 / +8.2% | | | | FAIL |
| edcow7o5 (133) | gate 1 -14.5 / +3.5 / -8.2% | | | | FAIL |
| 8TZqB7dw (86) | gate 1 -9.1 / -6.5 / -15.1% | | | | FAIL |

6nNzEg86: 28 coins a day, holds a median 61 s; pays with SOL 104, PUMP 41, TTWO 35, PAID 20, hSOL 15, mihao 11, SPCX
10, NVDAx 8 of its 374 first buys; its SOL coins lose (-6.4% with that exit); sell pressure costs (token coins without
+21.9% in the 3 blind blocks, with 5/60 s +13.0%); independent of the copied five (never the same slot).

**Three more from the Nov 24 screen (all their buys; 2pLugeBD 250 of 325):** 2pLugeBD FAIL (gate 1 +2.9 / -3.0 / -1.2%),
ETScS45a FAIL (gate 1 -5.6 / -1.6 / -10.1%, 0 of 3 blocks). **GqWfqfG6 passes both pick versions, the strongest yet:**
gate 1 +5.3 / +21.9 / +17.9%; the strict pick +19.4% a copy blind (55), +6.68 SOL w/o best 2%, 3 of 3; the pick on
all coins +26.4% (69), +14.25, 3 of 3. tp 3x / 420 / stall 240 on all coins, its 4 blocks: +4.8 / +1.1 / +40.3 / +35.5 =
+20.5% (92), +14.93 w/o best 2%, 4 of 4; its SOL coins +16.9% (60), token coins +27.2% (32). Price 1.00x, alone 96%.
Sell pressure 5/60 s halves it (+12.2% against +25.7%). Independent of the six copied (1-8 shared coins, never the same
slot). Small: 92 first buys of 0.5+ SOL over 13 days (about 7 a day), most at 10:00-23:00 Beirut; pays with SOL 77,
TTWO 15, NVDAx 10, SPCX 5 of its 116 first buys.

**Screen of Nov 24 evening, 75.7 h of tape (`sss`).** The owner: "Fatou is interesting". A fix first: the "left out as
jumpy" line printed the top of the kept wallets by their own result, not the jumpy ones (FatoU1bj was listed there but
was kept, and is 3rd in TOPMEAN); `s1_screen.py` lists the jumpy wallets now.
- **FatoU1bj (`out_w3/FatoU1bj_all.txt`, all 256 first buys of 0.5+ SOL; history capped at 10,000 transactions, Nov 17
  15:38 - Nov 23 15:13 UTC; paths by RPC): PASS on paper, not deployable.** Own +219.31 SOL (+50.58 Nov 22, +171.07 Nov 23).
  Gate 1 -14.2 / +8.4 / +12.2%; the pick (its sale, to 600 s) +15.2 / +17.4 / +9.7% blind, +14.1% a copy, +17.50 SOL
  without the best 2%. But: its buys of 0.5+ SOL are 15 on Nov 21 and 243 on Nov 23 (none Nov 17-18 or 22): the three
  blind blocks are one day, Nov 23 08:09-14:58 UTC, a day the screen also saw. It holds a median 22 s (95% under 30 s,
  none over 120 s; all its buys 12 s), all SOL coins; only following its sale works (+14.1%) or tp 1.5x / 60 s (+16.0%,
  -1.50 without the best 2%); the units' exit tp 3x / 420 s / stall 240 is -2.0%, wallet 4's -3.1%. To trust it: days
  after Nov 24 (blind to the screen) and our sale landing within seconds of its own.
- **The rest of the Nov 24 TOPMEAN top 15:** 5AmLiWon (1st) lost -15.42 SOL itself over 14 days (Nov 22, above);
  G3PMGr5q (2nd) failed on all its buys (Nov 22, above); 3T9ggLTE, 45JhwE8F, kzvoB9aZ, GJA1HEbx, 6UcanEPg, AvcwFK7Q lose
  themselves over 14-15 days (`out_own/`, Nov 22-23); the five 20-copy wallets lose themselves on the tape. **J8bMromU
  (`out_w3/J8bMromU_all.txt`, refetched Nov 24): own +13.14 SOL over 6 days, up on 5 (a wallet active since Nov 18), its
  53 copies: FAIL** (gate 1 -6.0 / -5.6 / +25.6%; blind -5.7% a copy, 1 of 3 blocks).

**`sss` runs in the background since Nov 25 late** (`run_screen.sh` + `screen_job.sh`): the screen is a service (`rugsnipe-screen`, 8 GB cap), not tied to the SSH session, which froze or dropped during ~25 silent minutes. It prints a line a minute; `sss` again follows a running screen, `sss show` reprints the last result (`/var/lib/rugsnipe-screen/screen.txt`).

**Screen of Nov 25, 92.8 h of tape (`sss`; the first run with the jumpy line fixed and an 8 GB cap).** TOPMEAN's top 15:
FatoU1bj copied already; G3PMGr5q and 6t5G5f1i failed before; 4Y4bWfBS, 45JhwE8F, E5thTmUh, 8BbPASYJ and the five
21-copy wallets lose (or barely make) money themselves. Own histories (Helius, MAXPAGES 10): Bing35WC -14.80 SOL over 13
days (STOP); 5AmLiWon +11.33 over 15 days, up on 10 (it lost -7.44 on Nov 11-13, +18.10 on Nov 22-24); 3SiQo8MJ +36.07
over 12 days, up on 11. Deep tests on all their buys (`out_w3/*_all_nov25.txt`, `*_setup_nov25.txt`):
- **3SiQo8MJ: PASS** (249 buys, all token coins; gate 1 -7.5 / +12.9 / +11.5%; the picks, tp 2x / 120 s each time, blind
  -1.3 / +11.5 / +6.7%, +5.7% a copy, +6.21 SOL without the best 2%, 2 of 3 blocks). In 4 blocks: tp 2x / 120 s +3.7 /
  -1.4 / +11.5 / +6.7% = +5.1% a copy (250), +7.34 without the best 2%, 3 of 4; wallet 4's exit +5.2%, -1.59; tp 3x / 420 s
  / stall 240 +1.5%, -7.08. A real but small edge, about half the units' tests (+11 to +21%).
- **5AmLiWon: FAIL** (275 buys; the rolling picks blind -5.8 / -2.0 / +19.4%, 1 of 3 blocks). Its SOL coins with tp 3x /
  420 s / stall 240: -11.7 / +10.0 / +21.9 / +19.4% = +9.5% (197), +8.49 without the best 2%, 3 of 4; its token coins lose
  (-18.8%). Picking that cell after the table is a choice on seen data; its own result turned only on Nov 22: re-test later.

**The second Nov 25 screen (93.3 h; the consistency ranking and the benchmark, `s1_screen.py`).** The benchmark: wallet 4
left out as a launch bundle (its token coins of 1.3+ SOL: 91 copies, up 3 of 5 days, +2.9%); GqWfqfG6 #25 by the mean,
#23 by consistency (up 4 of 5 days, +13.1%); FatoU1bj #3 by the mean but #77 by consistency (-9.0% without its best 2%);
CqCAzte8 #91 / #293. The consistency ranking demotes the one-burst wallet that failed live and keeps the steady one:
better than the mean. Launch-slot buyers now get their own list (TOPLAUNCH) instead of none. TOPCONS's top 15, own
histories (Helius, MAXPAGES 10, `../../../../` scratchpad `w3out/own_*_nov25.txt`): 3SiQo8MJ (tested above), Bing35WC
-14.80; 3F1rF4kp -19.04, FecLfkDA -2.08, 8vmMQXGq -42.02, 7Rqv6UJV -32.87, GZeeyMsV -23.87, 2Mcjmq3U -15.72 (STOP);
HbriciZm, 9WpU9vd9 lost before; 2z2q5gk8, 7mj1FuYw, 63qcMxrU barely make money on the tape. Four days of tape can't
judge a wallet: most "steady" ones lose over their whole history. Passed: HtHkKxYN +21.91 over 15 days (up 9),
Crs7Q1k2 +1.65 over 5 days. Deep tests (`out_w3/*_all_nov25.txt`, `*_setup_nov25.txt`):
- **HtHkKxYN: PASS** (195 copies; gate 1 +1.9 / +1.3 / +11.9%; picks blind -8.3 / +1.3 / +14.3%, +5.0% a copy, +2.06
  without the best 2%, 2 of 3). **The units' fixed exit (tp 3x / 420 s / stall 240), all coins, no pick: +0.1 / +13.1 /
  +1.3 / +14.3% = +7.2% a copy, +6.16 SOL without the best 2%, 4 of 4 blocks.** Price 1.09x. About 13 buys a day.
- **Crs7Q1k2: FAIL** (48 copies, blind -6.2% a copy, 1 of 3 blocks).

**The screen of Nov 25 evening (96.7 h, `sss` in the background) and the owner's "deep check" of its new names (Nov 25
late; `out_w3/{FecLfkDA,Bing35WC}_{all,setup}_nov25.txt`; NOSTOP=1: copies tested although both lose themselves).** A bug
first: Helius refuses JSON-RPC batches, and `cmodel.path` cached each refused coin as empty, so the first run replayed 5 of
FecLfkDA's 79 buys; fixed (`e0749e0`), the empty coins deleted, the rerun on Helius's getTransactionsForAddress.
- **FecLfkDA: FAIL** (79 copies; gate 1 +1.7 / -2.7 / -5.6%; picks blind -4.8% a copy, 0 of 3 blocks; the units' exit
  -4.4%). Own -2.11 SOL over 15 days, up on 5.
- **Bing35WC: PASS** (75 copies; gate 1 +19.6 / +4.7 / +11.7%; picks blind +12.7% a copy, +4.51 SOL without the best 2%,
  3 of 3 blocks). **The units' fixed exit (tp 3x / 420 s / stall 240), all coins, no pick: -10.7 / +33.1 / +10.5 / +18.5%
  = +12.8% a copy (75), +5.84 SOL without the best 2%, 3 of 4 blocks**; its SOL coins +14.5% (67), its 1.3+ SOL buys
  +14.9% (61). Price 1.02x on the tape. Against it: it loses -14.83 SOL itself over 13 days (up on 5), its first block
  (Nov 12-19) loses, and 75 buys in 13 days is few (about 6 a day).
- 5AmLiWon: FAIL earlier the same day (above).

**The screen of Nov 25 night (103.6 h) and the deep check of its new names (Nov 26; `out_w3/*_nov26.txt`, NOSTOP=1).**
- **5dvLgwVb and DVbLPphR: FAIL, and they are one operator** (the same coins in the same blocks: 59 and 60 buys, the same
  rolling picks; own +13.75 and +15.47 SOL over 13 days, up on all 13). Picks blind +9.3% / +9.0% a copy but 1 of 3 blocks
  and negative without the best 2%. The units' fixed exit, all coins: +5.4% (59), +0.92 without the best 2%, 2 of 4. tp 2x
  / 120 s on all coins: +7.9% (59), +3.57, 4 of 4 (DVbLPphR +6.2%, +2.73, 4 of 4): a cell picked after seeing the table, on
  about 4.5 buys a day.
- **BSPdKsA3: FAIL** (122 copies; gate 1 -7.2 / -1.9 / +10.0%; blind -4.3% a copy, 1 of 3). Own -13.15 SOL over 12 days.
- **EtwpENJ2: FAIL** (208 copies; gate 1 -5.0 / -2.3 / +20.9%; blind -3.3% a copy, 0 of 3). Own +16.14 over 14 days, up on
  13, but its copies make money in one block only (Nov 23-25, the block the screen saw).

**The screen of Nov 26 (106 h) and its new names, deep-checked (Nov 26; `out_w3/{6kPn3FEA,7kyv4fyC}_*_nov26.txt`, the fresh
14-day histories `hist26_`).**
- **6kPn3FEA: a weak PASS** (96 copies; gate 1 -2.6 / +5.3 / +4.9%; the picks, held 300 s each time, blind -7.9 / +14.0 /
  +8.2%, +4.8% a copy, +0.51 SOL without the best 2%, 2 of 3). The units' fixed exit, all coins: +33.9 / -9.3 / +8.4 / +0.6%
  = +8.4% (96), +4.20 without the best 2%, 3 of 4, its first block carrying it. It loses -29.39 SOL itself over 14 days, up
  on 5. Weaker than Bing35WC (+12.7% blind, 3 of 3): not added.
- **7kyv4fyC: FAIL** (350 copies; blind -6.6% a copy, 1 of 3; the fixed exit -4.6%). It lost -174.63 SOL itself over 15 days
  and was up on none of them: the screen's 4 days of tape saw its small winners only.

**The screen of Nov 26 midday (117.5 h) and its new names, deep-checked (Nov 26; `out_w3/*_nov26.txt`, 14-day histories).**
- **E2XwSeqe: PASS** (118 copies over 10 days; gate 1 +6.1 / +8.2 / +4.5%; picks blind +13.7% a copy, +5.85 SOL without the
  best 2%, 2 of 3). The units' fixed exit, all coins: -3.6 / +10.0 / +13.2 / +13.6% = +8.2% (118), +5.58, 3 of 4; its SOL
  coins +16.5% (71), +9.60, 4 of 4. Own +3.67 SOL over 10 days, up on 5. About 12 buys a day.
- **E5CLHHz6: PASS** (55 copies over 11 days; gate 1 +17.9 / +6.4 / +6.5%; blind +13.5% a copy, +2.22, 3 of 3). The fixed
  exit, all coins: -10.9 / +25.7 / +9.3 / +27.1% = +12.5% (55), +3.59, 3 of 4. Own +0.07 SOL. About 5 buys a day.
- **E5thTmUh: a weak PASS** (342 buys; blind +3.7% a copy on 116, +1.96, 3 of 3; the fixed exit +5.3% on 325, +5.06, 3 of 4).
  Own -34.93 SOL over 15 days, up on 4.
- **6xJwQ5m9: FAIL** (a 2-day-old wallet; blind -17.6% a copy).

**Fast traders (Nov 25; the owner: "maybe we can copy fast traders too, and make more money"; the screen's TOPFAST,
93.9 h).** The 2,120 wallets holding a median under 20 s, copied realistically (out at 1.5x its price, in the first trade
2 slots after its sale, or 15 s): every copy's mean **-6.5%**. The top 15 by consistency are positive on their 3-4 days;
own histories (Helius): 7NLyXFc2 +25.61 SOL over 9 days (9 up), 4bL2mY7s +22.71 over 12 (9 up), 6iFupNYb +8.26 over 3,
Cf4dxUu7 capped at 2 days (10,000 transactions), 21RfcpSh -1.97 (STOP). Their copies on their whole histories with the
fixed fast exits, no pick (`../../2026-11-24/fatou_exit/x1_exit.py` with FAST_W, its SOL coins, `out_w3/*_fast.txt`):
- 7NLyXFc2 (57, 9 refused over 1.5x): tp 1.5 / 15 s / its sale + 2 slots -3.7 / -4.8 / +18.2 / +9.8% = +4.8%, +2.02 SOL
  without the best 2%, 2 of 4 blocks.
- 4bL2mY7s (79): -2.6%, 1 of 4; every fixed exit negative.
- 6iFupNYb (90, 3 days): +9.9%, 3 of 4, but +2.36 without the best 2% (two copies carry most of it).
No fast trader copies for clearly more than the units do; FatoU1bj (live at 0.1 SOL) is the test that stays.

**Sell pressure on the two candidates (Nov 25; the owner: "also no sell pressure?"; `w3_sp_check2.py`, the base exit from
SPBASE, the 3 blind blocks, `out_w3/*_sp_nov25.txt`).** HtHkKxYN, all coins, tp 3x / 420 s / stall 240: none +9.5% a copy
(146), +7.97 SOL without the best 2%; every one of the 9 sell-pressure kinds lower (+1.4 to +5.4%, -3.26 to +2.35): **no
sell pressure.** 3SiQo8MJ, token coins, tp 2x / 120 s: none +5.3% (186), +5.46; 8 of 9 kinds a little higher, wallet 4's
5/60 s +6.1%, +7.05 (block 1 -1.4 -> +0.1%): about one point, within the noise, never worse without the best 2%.
