# Part sales: sell x% at y, the rest by the live rule (Nov 15)

The owner's question: sell part of the position at a lower price (1.2x to 2.9x, every 0.1), from 10% to 90% of it,
and the rest by the live rule (tp 3.0, 600 s, his sale followed 30-290 s under 1.5x, no stop); also with the rest's
take profit at 4.0 or none (the timer). `partial.py` over the 781 buys of the four live kinds (SOL, WBTC, PUMP, SPCX),
Oct 21 - Nov 14, in three blocks (A = Oct 21-29, unseen when the live rule was picked; B; C). 0.5 SOL, 2 open, raw,
mean of landings 4 / 8 / one block late. The model (`../../2026-11-14/float_exits/lib.py` `model_partial`): the part
sold on the trade after the price first reaches y, valued as its own position of its share of the stake, one more
sell transaction (0.0013 SOL).

    python3 -I partial.py SPD > out/partial.txt

**Results (`out/partial.txt`).** Selling everything at 3.0: +36.23 SOL (+29.23 without each block's best 2). Every
part sale at 2.8x or lower makes less, and the lower and the larger, the worse (without the best 2): 10% at 1.5x
+27.18, 50% at 1.5x +19.46, 50% at 2.0x +25.25, 50% at 2.5x +27.67. Only parts at 2.9x come out a little ahead
(+29.47 to +30.21), which is the take profit moved from 3.0 to 2.9, not a part sale; 2 of 162 part sales beat
selling all at once in all three blocks, both at 2.9x. With the rest's take profit at 4.0 none does; with no take
profit, the best are 70-90% sold at 2.9x (again a take profit just under 3.0).

Why: the profit is the coins that reach 3x (55 take profits made +49.57 SOL against −15.24 for all the other copies,
`../../2026-11-14/float_exits/out/tp_daily.txt`); a part sold at 1.5x or 2x is a part of those winners sold early,
and the coins that turn back after 1.5x-2x are mostly sold behind his early sale or on the timer anyway.
**The live rule stays: everything at 3.0.**

A bug found on the way: the first run charged a second transaction's cost (0.0026 SOL) on every copy that never
reached the part price; fixed before the results above.
