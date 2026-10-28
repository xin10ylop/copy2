# Other wallets with wallet 4's edge? (Oct 29, three searches)

In short: **none found.** Two searches from two directions produced six candidates; the full scoring (the same pipeline
that measured wallet 4, run on each wallet's whole history) rejects all six. The nearest, `3dwZP6T8`, started on Oct 24,
buys 1.9 SOL of other-token coins at launch 20-30 times a day, but sells on a 272 s timer; our copy on its buys is
about break-even at best. Re-score it after another week. Wallet 4 stays the only wallet whose big launch buys of
other-token coins are **held** long enough for a copy to ride.

| Folder | What it did | Result |
|---|---|---|
| [`neighbours/`](neighbours/README.md) | every early buyer of the 856 coins wallet 4 bought Oct 19-28, read from each coin's create (1,008 wallets; 23 on 10+ coins) | one pass of the screen, `6anjqMeW`; everyone else lands **ahead** of wallet 4 with 2-4 SOL and sells 1-2 s later, or flips in seconds |
| [`creates/`](creates/README.md) | 24 hours of pump creates (Oct 27 22:51 to Oct 28 22:51 UTC): 47,194 coins, 23% priced in another token, 2,915 with a launch frenzy; who buys them big at create+0/+1 (64 independent wallets, 1,210 launch bundles) | one new name, `3dwZP6T8`: the only independent 1+ SOL buyer besides wallet 4 that holds minutes |
| [`score/`](score/README.md) | the seven marks of the profile plus our copy's backtest, on 6 wallets, wallet 4 as the reference row | none copyable (table below) |

## The scoring table

P1 Oct 19-22 / P2 Oct 23-27 00:20 UTC / P3 to each wallet's last row; brackets without each period's best 2. "Our copy"
is strategy A as built (1 SOL, TP 2.0 / 0.8 / 1790 s, 4 open, q + lift, the backtest's costs, landing at slot +1).

| wallet | 1.45+ other-token launch buys a day | its rule | early sales | failed | routable | own result | our copy, 4 open (copies) |
|---|---|---|---|---|---|---|---|
| **wallet 4** (reference) | 100 / 74 / 34 | 2.5x / 0.7x / 30 min; 74% held to the timer | 3.5% / 13.6% / 49% | 2.9% | 48% | +249 (+227) / +112 (+98) / +82 (+59) | +5.19 (+3.22), 153 / +12.27 (+9.62), 161 / −2.98 (−4.70), 30 |
| 6anjqMeW | none at 1.45+; 535 / 267 / 361 at 0.45+ | sold in parts 0-10 s after the buy, or 240-740 s timers; 1% reach 30 min | 92-95% | 8.5% | 19% | +33 / +33 / +17 | at a 0.45 floor: −11.60 / −17.81 / −8.48 |
| 3dwZP6T8 (since Oct 24) | — / 33 / 22 | a 272 s timer; the first sale near 2x on runs | — / 99% / 97% | 35.6% | 53% | — / +20.6 (+12.5) / +19.7 (+11.9) | — / −3.21 (−5.29), 49 / +1.78 (−0.38), 17 |
| DsGJkPzF | 0.45+: 103 / 33 / 36 | a 20 s timer at about 1.0x | 86-96% | 5.3% | 20% | pump coins −2.5 / −2.5 / +2.9 | at 0.45: −1.42 / −0.88 / −1.99 |
| AMDEmVoc | 0.5+: 140 / 190 / 152 | 6 s median hold | 95-97% | 3.2% | 28% | +27 / +55 / +17 | not run: a flipper |
| Fhbh1DTU | 96 / 65 / 61 | 1 s median hold; lands ahead of wallet 4 on 94% of shared coins | 95-99% | 86% | 40% | +125 / +160 / +60 (plus +1,778 from tokens held before) | not run: a flipper |
| dKMjeGJ4 | 15 / 53 / 51 | sells in parts within seconds | 92-100% | 47% | 11% | +391 / +290 / +69, nearly all on SOL coins | not run: a flipper |

The pattern behind every rejection: these wallets make their money in the first seconds of a launch, by landing first
or by selling the first part of a position into the frenzy, and keep the leftovers. A copy lands a slot later and buys
what they sell. Wallet 4 is the opposite: its one-sale coins make its money, and three quarters of them are held to its
30-minute timer. That is what makes it copyable, and on Oct 29 it is alone in that.

What this does not cover: wallets that buy big on quiet coins (the creates scan kept coins with a launch frenzy only),
wallets outside wallet 4's coins over more than one day, and any wallet that starts after Oct 29. The successor scan by
fingerprint (`07-rework-2026-10-28/wallet-check.md` §7) is still not built. To re-score a wallet: `score/README.md`
(`bash run.sh W fetch`, `bash run.sh W score`, `bash run.sh W band LO`, `python3 -I row.py W`).

## Sources

The three folders' READMEs and `out/` files; the Triton endpoint for the fetches (Oct 29, not in the repo); the
fresh3 dataset (`data/datasets/`, CLAUDE.md "Datasets") for wallet 4's row.
