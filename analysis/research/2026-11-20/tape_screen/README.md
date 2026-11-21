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
