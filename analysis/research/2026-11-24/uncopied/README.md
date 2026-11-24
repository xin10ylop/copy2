# What the copied wallets trade that we don't copy, and floats to add (Nov 24)

The owner: "for the remaining wallets, check if they are taking other trades that we don't take and making them money,
except for qqq", and "check if there are any important floats we should add".

1. `u1_groups.py` (`out/<wallet>.txt`): each wallet's coins (14-day history plus the Nov 24 fetch) grouped by its first
   buy as its unit judges it: copied / its buy under 0.5 SOL / SOL coins (the token-only units) / paid with a token we
   don't hold; the wallet's own result per group (coins it sold out of; token quotes at Jupiter's price now).
2. Our copy replayed on the groups where the wallet makes money (`../ideas/e1_ideas.py` with MINSOL / BAND / QUOTE, the
   unit's live exit; FatoU1bj with `../fatou_exit/x1_exit.py` MINSOL / MAXSOL; Helius paths), `out/replays.txt`.
3. `u2_floats.py` (`out/floats.txt`): the tokens we don't hold that the wallets pay with on buys big enough for their
   units (wallet 4: 1.3+ SOL), and the use of the floats we hold over the last 7 days.

## Results

| Wallet | Where it makes money that we don't copy (its own result) | Our copy of it | Verdict |
|---|---|---|---|
| 3XeFcZKS | SOL coins: 219 coins, +37.73 SOL, 11 of 15 days up | +1.3% a copy (190), -4.17 SOL without the best 2% (`tape_screen/out_w3/3XeFcZKS_setup.txt`) | no: its edge is in buying first |
| 6LwMLkCe | SOL coins: 147 coins, +26.25 SOL | +4.0% (131), -0.47 without the best 2% (`6LwMLkCe_setup.txt`) | no |
| CqCAzte8 | its buys of 0.25-0.5 SOL: 64 coins, +5.47 SOL, 13 of 16 days | +3.9% (76), -0.33 without the best 2%, 2 of 4 blocks; its latest 7: -24.7% | no |
| 6nNzEg86 | token coins of 0.25-0.5 SOL: 42 coins, +4.22 SOL | +11.4% (63), +4.47 without the best 2%; blocks +6.4 / -5.1 / +2.3 / +44.2% | weak (one block) |
| CgyPomTG | coins priced in USDC: 24 buys, +5.02 SOL on its 1.3+ ones | +4.0% (24), -1.09 without the best 2% | no |
| FatoU1bj | its buys of 0.25-0.5 SOL: 518 coins, +66.25 SOL | its exit: +1.8% (518), -23.85 without the best 2% | no |
| GqWfqfG6 | little outside what we copy (+1.48 under 0.5, +1.50 unheld tokens) | - | - |

**Floats to add: none.** The unheld tokens on copyable buys, ~14 days, all wallets: USDC 30 (CgyPomTG 24; its copies
+4.0%, negative without the best 2%), ANT (Anthropic, Backpack) 10, HYPE 9 (copies: 8 replayed, about +9% a copy, negative
without the best), FIONA 8 (wallet 4's 5: -0.7%), mihao 8 (mixed), DJT 6. None has the buys or the copy result.

**The floats we hold, copyable buys paid with each, Nov 17 18:00 - Nov 24 UTC:** TTWO 239 (wallet 4 75, 6LwMLkCe 73,
CgyPomTG 27, 6nNzEg86 21, 3XeFcZKS 20, CqCAzte8 15, GqWfqfG6 8), hSOL 77, PUMP 36, NVDAx 34, SPCX 19, PAID 14, WBTC 7.
TTWO and hSOL (1.0 SOL each) carry two 0.5 SOL copies at once among eight units; a float short of the stake skips the
buy ("float ... under the stake" in the journal).
