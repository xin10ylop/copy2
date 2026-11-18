# The direct screen (Nov 18): every wallet's copy scored at once, then confirmed outside the screen

`m4_direct.py` on 2,380 of the 6,049 live other-token coins of the 48 h (fetched in full, true in-slot order; the
fetch was stopped on the owner's call, a random sample by mint): 679 wallets with 6+ copies, 3 positive on both days
and without the best 2% (BCyNgSB1 out: one creator). Wallet 4's 1.45+ SOL buys: +46.2% a copy (9 copies).
On wallet 4's 27 days of coins (`screen.py FIX=1`, at 0.0345 SOL), 17 wallets pass; 4 buy in wallet 4's own slot.

`m5_confirm.py` (NS=150 random buys, seed 7; wallet 4's live model; 0.0345 SOL) — every candidate FAILS:

| wallet | test | copies | a copy | w/o 2% | P(mean>0) |
|---|---|---|---|---|---|
| 5mWe9kLZ | outside the screen, other-token coins | 69 | −8.7% | −4.43 | 6.8% |
| Z6BLE1zw | outside the screen, other-token coins | 46 | −11.6% | −2.92 | 0.0% |
| EcrMBga8 | coins wallet 4 never bought | 133 | −11.0% | −9.29 | 0.0% |
| Fhbh1DTU | coins wallet 4 never bought | 111 | −19.6% | −13.39 | 0.0% |
| 8ptvshQR | coins wallet 4 never bought | 24 | −21.6% | −3.12 | 0.3% |
| DsGJkPzF | coins wallet 4 never bought | 106 | −5.6% | −6.23 | 13.5% |

The same-slot wallets make money only on wallet 4's coins: the edge is wallet 4's CHOICE of coins, not the timing.
They follow no one (`2026-11-18/leaders/l1_leaders.py`: no wallet leads 3+ of their buys): launch-feed snipers.

## The full screen (5,337 coins of 6,049; Nov 18)

`../out/m4_direct.txt`: 1,869 wallets with 6+ copies; 15 positive on both days and without the best 2%; all 1,869
pooled: −2,618 SOL on 35,858 copies. Wallet 4's 1.45+ SOL buys: +25.2% a copy (19 copies). Out by the lessons: 4
single-creator launch buyers (DnkLKQtY, F5XvCe42, A9H4qn1L, rNAUS5wm), BCyNgSB1 (4 creators, 90% at launch), TAB16RxX
(paused Nov 14), 5mWe9kLZ (failed above). The 8 others go to m5 (NS=100, Triton).

## Triton refused this machine for ~15 minutes (Nov 18 ~03:00 UTC)

HTTP 403 "Your IP or provider is blocked from this endpoint", right after the ~1M-transaction refetch burst; it answered
again ~15 min later. Triton documents per-IP blocks for sources that generate many 403/429 errors, extra filters on
data-centre ranges and proxies (this machine goes out through a data-centre egress proxy), and a stop of service at a
zero pay-as-you-go balance (the balance was ~$5 before the burst). From now on: no Triton bursts; batches, a few
fetchers, and Alchemy for the bulk.

## The 8 confirmed, then engineered like wallet 4 (Nov 18, `m5_confirm.py`, `e1_exits.py`)

NS=100 random buys outside the screen, wallet 4's live model: AMDEmVoc −11.4% (30 other-token copies), 8TPkrBcR +0.8%,
3P3XSWAA +4.8%, 8Y3segeZ +1.9%, H1xshmCR +3.5%, HjuSthan −9.3% (all negative without the best 2%); 7djZvJGN +22.7%
and CzsxDQz6 +14.4% (21 copies each). The exit engineering (23 exits x 16 coin/size filters, picked on the 1st half)
passes none; AMDEmVoc loses under every exit.

**7djZvJGN and CzsxDQz6 on their other-token buys** (OTHER_ONLY, 127 and 130 of their 339 / 350 copies, the fetch
stopped there to save Triton; `../out/m5_other_partial_*.txt`, `../out/e1_exits_other_partial.txt`): +0.6% and −0.3% a
copy under wallet 4's live model, −3.23 / −4.09 without the best 2%. The 21-copy results were luck. Engineered: every
mechanical exit (time, take profit, sell pressure, stall) loses on both halves; the exits built on ITS sale are the
only positive ones (7djZvJGN "its sale + tp 4x": 1st half +13.2%, 2nd +2.7%, w/o 2% −0.36; the filter "tradable now,
its 1.0+ SOL": 2nd half +4.7% / +5.9% on 21 copies, negative w/o 2%). Its sale carries information; the copy is about
break-even at 0.0345 SOL a round trip. Not a wallet 4.
