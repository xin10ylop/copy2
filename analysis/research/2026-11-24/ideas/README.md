# Anything to make each wallet better? (Nov 24)

The owner: "for all the wallets we have, for each, individually, check if there is anything to make it better ... buy
pressure, or the dip thing for wallet 4 ... also if some coins revive after we sell". FatoU1bj left out (its exit was
built the same day, `../fatou_exit/`).

`e1_ideas.py` (run order and settings in its header): each wallet's first buys from its 14-day history, our copy at the
end of the slot after its buy, 1 SOL, 0.0064 a round trip, refused over 1.5x; the unit's live exit as the baseline (it
reproduces the earlier tests: GqWfqfG6 +21.8% here, +20.5% in w3; CqCAzte8 +13.7% / +13.4%). A menu fixed before any
result: P buy pressure (wait 3-20 s, enter only if others bought 3-10 more than they sold; 12), D the dip entry (10-30%
under its price within 60 s; with the live exit or wallet 4's dip-leg exit; 6), T a trailing stop on the live exit (armed
at 1.5x / 2x its price, out 25% / 40% under the peak; 4), R a re-buy after a non-tp exit when the price passes the high we
held through. Each variant against the baseline, copy by copy, in 4 time blocks and without the best 2%.

**The coin paths:** the Helius paths cached for the earlier tests stop 1,750 slots (~375 s) after its buy (slots run ~0.21 s
now): the earlier tests' 420 s and 600 s holds were in effect ~375 s, and revival after that is out of view. For wallet 4
the paths were fetched again out to 5,000 slots (~18 min; Helius, ~430 coins; `ANCHOR_S`, `PATH_SLOTS`, `FETCH=1`).
Wallet 4's sample is its 1.3+ SOL buys of TOKEN coins (what its unit copies: 2,152 of its first buys Nov 17-23 were SOL
coins, which the unit does not copy; a first run that mixed them in is not used).

## Results (`out/*.txt`)

| Wallet (copies) | Baseline, % a copy | Buy pressure | Dip entry | Trailing stop | Re-buy on revival |
|---|---|---|---|---|---|
| CqCAzte8 (257) | +13.7% | all 12 worse (-9 to -25 SOL) | all 6 worse | 2x/-25%: +1.94, 3 of 4 | +1.90, 3 of 4 |
| CgyPomTG (238) | +11.6% | all worse | all worse | 2x/-25%: +0.37, 3 of 4 | -0.67 |
| GqWfqfG6 (88) | +21.8% | all worse | all worse | 2x/-25%: +1.20, 3 of 4 | 0 |
| 3XeFcZKS (75) | +12.5% | all worse | all worse | best +0.26, 1 of 4 | 0 |
| 6LwMLkCe (135) | +8.6% | all worse | all worse | all worse (2x/-25%: -6.36) | +0.19 |
| 6nNzEg86 (114) | +17.7% | all worse | best +5.84, 2 of 4 | all worse (2x/-25%: -4.15) | -0.18 |
| wallet 4, Nov 17-23 (325) | +6.1% | all worse (0-1 of 4) | mixed (10%: +7.5, 3 of 4, -2.8 without the best 2%) | 1.5x/-40%: +4.32; 2x/-25%: +6.82; 2x/-40%: +5.37 (each 3 of 4) | -2.77 |
| wallet 4, Nov 23-24, unseen (50) | +7.9% | +0.5 to +1.2 (small) | all worse | **1.5x/-40%: +0.84, 3 of 4**; 2x/-25%: -0.16; 2x/-40%: +0.28 | +0.59 |

- **Buy pressure and the dip entry make every new wallet worse:** waiting costs the price, and most coins never dip 10% in
  the first minute (the dip skips the winners).
- **The trailing stop is noise on the new wallets** (a little better on three, clearly worse on two). **On wallet 4,
  1.5x / -40% is better in 3 of 4 blocks on both its older copies (+4.32 SOL) and its unseen days (+0.84), without the
  best 2% too**: about +1.4 points a copy over 375 copies. The engine has no trailing stop (a code change), and wallet 4's
  exit is frozen until about 50 real trades or two weeks (the owner's rule; 50 reached Nov 24).
- **Revival:** after our non-tp exits, wallet 4's coins later reach 1.5x our sale price within ~18 min on 24% (older) and
  20% (unseen), 2x on 14% / 10%; CqCAzte8's within ~6 min on 25% / 8% (mostly its SOL coins, sold at 120 s); the others
  0-7%. But the re-buy rule that would catch them does not pay (wallet 4 -2.77 / +0.59), and holding CqCAzte8's SOL coins
  longer (tp 2x at 180 / 240 / 300 s: +11.7 / +14.3 / +11.1% against +9.0% at 120 s on Nov 8-22) fails on its unseen
  buys (Nov 23-24, 33: -1.7% at 120 s, -10.0% / -10.3% / -12.2% longer). Coins do come back after we sell, but which ones
  can't be told in advance.

## The dip as an EXTRA leg (Nov 24, later; the owner: "remember the dip thing?")

The table above judges the dip as a replacement for the copy. Wallet 4's dip ran as a second leg beside the copy
(Nov 19 22:53 - Nov 20 13:23 UTC), so its own trades are what count (`e1_ideas.py` now prints them, "extra leg"):

| Wallet | 10% dip, the copy's exit | 10% dip, wallet 4's dip exit (tp 1.5x our fill) | Unseen days |
|---|---|---|---|
| CqCAzte8 (Nov 8-22) | 168 trades, +15.1% a trade, +25.35 SOL, w/o 2% +19.26; blocks +7.2 / +16.1 / +13.2 / +24.0% | +9.8%, blocks +9.2 / +13.1 / +5.4 / +12.1% | Nov 23-24 (its bad days), 31 trades: +4.4% (copy's exit), +10.3% (dip exit) |
| 6nNzEg86 (Nov 10-24) | 52 trades, +49.4% a trade, blocks +29.8 / +38.4 / +64.2 / +88.3% | +24.6% | 1 trade (-37%): nothing to judge |
| GqWfqfG6 | 27 trades, +5.0%, one block negative | +7.5% | - |
| wallet 4 (token coins) | - | Nov 17-23, 170 trades: +5.8% a trade (w/o 2% +1.94) | Nov 23-24, 27 trades: -2.1% |
| CgyPomTG, 3XeFcZKS, 6LwMLkCe | +0.4%, -15.7%, -5.3% (10% dip leg) | | |

The paths stop ~375 s after its buy (wallet 4's ~18 min): the dip exits' long holds are cut there.
