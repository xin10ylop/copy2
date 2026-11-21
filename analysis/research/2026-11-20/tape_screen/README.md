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
