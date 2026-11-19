# m16's candidates on their own histories (Nov 19)

`m16_wallet_styles.py` picked, per wallet, an entry style and an exit on Nov 14-15 that also held on Nov 16-17. Here
each one's style is frozen and run on its own history since Nov 1 (`c1_fetch.py`, Triton), on the days m16 never saw:
before Nov 14 01:07 and after Nov 18 01:07 UTC (`c2_style.py`; NS=150, a random sample of its 0.5+ SOL first buys:
these wallets buy 1,330-4,329 coins in 19 days, too many paths to fetch all).

| wallet | style, exit | before the 4 days | the 4 days | after | by week |
|---|---|---|---|---|---|
| 6Kj5ChEZ | plain, tp x1.5 / 900 s | 57 trades −14.2% | 53 −14.9% | 18 −25.6% | +0.64, −2.08, −6.56, −2.30 |
| kurtzsJg | dip 5% in 60 s, tp x1.5 / 60 s / trail | 52 −8.6% (plain −11.4%) | 17 −19.2% | 9 −8.7% | every week down |
| 29yFzeBZ (+ GTnbqqrY, Gg3ska7S: one trader) | plain, tp x1.5 / 60 s / trail | 88 −14.4% | 26 −18.3% | 8 −10.2% | every week down |
| F8YceN5V | dip 10% in 60 s, tp x2 / 60 s | none (its buys start Nov 11) | 17 −1.0% | 48 −14.9% | −0.08, −3.58 |

All four fail out of sample, and lose even on the sampled buys of the 4 days themselves: m16's per-wallet picks (520
styles x exits each, on 6-30 trades) were luck. The dip helps where it is tried (kurtzsJg, F8YceN5V lose less than their
plain copy), but only wallet 4's coins keep rising after its buy.
