# 02. The decomposition: where wallet 4's profit comes from, and what we can and can't trade

In short: of wallet 4's **+355 SOL** over Oct 19-27, only part **A** (+102 SOL, its 1.45+ SOL buys of other-token coins
that pump's own programs can route) is both copyable and positive in both test periods. That's **strategy A, the long
copy** (paper). Part **D** (SOL-priced coins, +29) is what the copy bot traded live, as **strategy D**, and it roughly
broke even. B, C, E and F are out, each for a tested reason. In check.sh's window (Oct 26 15:00 to Oct 27 11:45 Beirut)
its **+36.92** splits the same way: more than half (+20.16) was F, its tokens going up in price, which isn't a trade.

**Name clash, read first.** Parts A-F on this page are a split of the *wallet's profit*. The research scripts also use
letters for *route classes* (`grid.py ROUTES=`, `routable.json`): route A = multihop from wSOL, B = multihop from WBTC,
C = a curve quoted in WBTC (all three are inside part A here), E = not routable (part B here). Different things.

## 1. The 8 days, Oct 19 to Oct 27 (every coin counted once)

Some pump.fun coins are priced in SOL: you buy them with SOL. Others are priced in another token (WBTC, PUMP, CARDS,
TTWO, USDC, xStocks, graduated pump coins): the curve takes that token. That split matters most.

| Part | What it is | Coins | Its profit | Do we trade it? |
|---|---|---|---|---|
| **A** | priced in another token, its buy is **1.45 SOL or more**, and **we can build the route** | 324 | **+102** | **Yes: strategy A, the long copy (paper on Ohio)** |
| B | priced in another token, 1.45+ SOL, paid in a token we don't hold (PUMP +45.6 on 88, CARDS +23.8 on 79, TTWO +10.4 on 23, USDC, xStocks ...) | 372 | +116 | No |
| C | priced in another token, smaller buys (under 1.45 SOL) | 2,360 | +60 | No |
| **D** | priced in **SOL** | 1,439 | **+29** | **The copy bot traded its launch slice live: strategy D** |
| E | tokens traded only on PumpSwap (graduated coins, non-pump tokens; CARDS +13.5) | | +17 | No |
| F | price gains on the tokens it keeps between trades (WBTC, PUMP ...) | | +29 | No: not a trade |

A + B together are its 696 big other-token buys, +218 SOL, about 70% of its trading profit.

## 2. Why each part is in or out

**A: in.** We can buy these the way wallet 4 does: `multi_hop_swap` from wrapped SOL, or from WBTC we hold, or behind
the quote's canonical PumpSwap pool. The backtest is positive in both periods: +5.03 SOL on Oct 19-22 and +9.63 on
Oct 23-27 at 1 SOL stakes, 3 open (4 open: +6.73 / +11.13). We make much less than wallet 4 on the same coins, about
+15-17 against its +82 over the 8 days, for four reasons:
- we buy after it, so its 1.5 SOL buy has already pushed the price up;
- our own buy pushes it up again;
- we pay about 5% in curve fees for the round trip, plus about 0.03 SOL fixed per trade;
- we have to sell at 2.0x, because its own 2.5x sale would hit first.

**B: out.** To copy these we'd have to hold PUMP, CARDS, TTWO and the rest, and their prices can fall while we hold
them. Tested as if we held every one of those tokens at no risk (`ROUTES=E grid.py`): Oct 19-22 +24.63 on 189 copies;
Oct 23-27 +0.43 on 94 (PUMP −1.32). It fell apart in the later period. Mixed in with A (3 open) they make Oct 23-27 worse,
+7.38 against +9.63, because they take the open slots. Counted by route instead, the 305 big buys that need Jupiter
(direct buys of other quotes, PUMP floats, 3+ hops) made +28.57 on Oct 19-22 and +3.06 (+0.41 without the best 2) on
Oct 23-27 (h9long README, "What rugsnipe-long can route").

**C: out.** Copying its smaller buys loses or flips between periods (routable only, no cap, cautious model q / path
model v, `band.py`):

| its buy | copies | Oct 19-22 | Oct 23-27 |
|---|---|---|---|
| 0.8-1.0 SOL | 199 | −1.40 / −0.49 | −2.39 / −1.62 |
| 1.0-1.25 SOL | 162 | +5.62 / +6.97 | −6.46 / −6.32 |
| 1.25-1.45 SOL | 56 | −1.84 / −1.82 | −0.92 / −0.66 |
| 1.45-1.5 SOL | 28 | −1.54 / −1.58 | +0.54 / +0.78 |
| **1.5+ SOL** | 295 | **+6.69 / +9.11** | **+10.43 / +12.91** |

The fixed cost per trade is the same, but these buys reach 2.5x less often. The floor stays at 1.45.

**D: traded live, but no version of it makes money reliably.**
- The copy bot copied its **launch** buys of SOL coins (create slot or the next) and sold at create + 12, about
  5 seconds later. That's a small slice of D. Over check.sh's window: wallet 4 made +2.77 on the 96 coins we copied, and
  our copies made +0.15 (section 4; strategy D page).
- Copying its big SOL-coin buys and holding them the long copy's way loses: −11.12 on Oct 19-22 (73 copies) and −2.34 on
  Oct 23-27 (31) (`exits_pess.py`).
- Its buys after launch on SOL coins lose for wallet 4 itself (37 coins, −11.65), so they were never copied.
- Wallet 4's own edge here is only about +0.02 SOL a coin, less than a copy's costs.

**E and F: out.** E aren't curve trades our bots follow (and in check.sh's window wallet 4 lost on them, −2.76). F isn't
a trade at all.

## 3. Check.sh's window: Oct 26 15:00 to Oct 27 11:45 Beirut (+36.92)

All 212 of wallet 4's coins in `05-live/check-sh-2026-10-27.txt`, each classified on chain: by the bot's own detection
code (`crates/rugsnipe-long/examples/scan.rs`) for coins after Oct 27 00:19 UTC, and by the backtest data before that.
The parts add back up to the +36.92 (`analysis/research/2026-10-28/decomp/decomp.py`):

| Part | Coins | Its profit | What the copy bot did | Can we trade it? |
|---|---|---|---|---|
| **F** tokens it pays with and keeps (DJTU +8.97, PUMP +7.24, DOGE +2.17, an xStock +1.78) | 5 | **+20.16** | 4 "not watched", 1 "not seen" | **No.** These are price gains on tokens it holds. |
| **C** other-token coins, buys under 1.45 SOL | 47 | **+10.68** | 38 "not seen", 9 "not watched" | Could, but tested as losing. 4 coins made +8.55 of it (48HkZ7XF +3.12, REtaGvoE +2.69, HjkHEADH +1.54, EnVSD3QE +1.20). |
| **A** other-token, 1.45+ SOL, routable | 15 | **+6.02** | 12 "not seen", 3 "not watched" | **Yes: strategy A.** The copy bot can't see these at all. One coin, CCci2Fr6, made +6.09; the other 14 together about −0.07. |
| **D** SOL-priced | 127 | **+2.87** | **96 copied** (+2.77 for it, **+0.15 for us**), 5 skipped, 3 "not seen" (+1.86, its buys after launch), 23 "not watched" (−2.09) | **Yes: strategy D**, the copy bot. |
| B other-token, 1.45+, no route for us | 1 | +0.06 | not seen | No route. |
| E coins already graduated to the PumpSwap pool | 17 | **−2.76** | 11 "not seen", 6 "not watched" | Neither bot handles them, and wallet 4 lost on them. |
| its failed transactions | | −0.12 | | |

- check.sh's "not seen" column (66 coins, +10.58) = other-token coins (A + B + C) +9.86, the xStock +1.78, SOL buys after
  launch +1.86, graduated coins −2.93.
- check.sh's "not watched" column (45 coins, +23.36) was mostly its tokens rising in value: DJTU, PUMP and DOGE together
  +18.38.
- check.sh's per-coin numbers for this wallet are wrong coin by coin (a coin sold into its quote token shows its profit
  on the quote token's row; docs/20 §1). That's why F shows up as "coins" here. Only the total is right.

## 4. Why our D copies made +0.15 while it made +2.77

The 76 copies that filled, over check.sh's window:

| | Wallet 4 (holds up to 30 min) | Us (sold after about 5 s) |
|---|---|---|
| Its 5 best coins (5qW5yNnZ +3.79, E2757ksn +2.66, GrLZAMXj +1.14 ...) | **+9.47** | −0.12 |
| The other 71 coins | **−7.66** | +0.26 |

- Selling after 5 seconds avoids its big losers, but it also misses the few coins that run for minutes and carry all of
  its profit.
- Another +2.09 of its profit was on 14 coins the 20% price bound refused, so we never got in.
- Holding longer doesn't save it: create + 15 lost in one of the three test periods (docs/19 §13), holding 30 minutes
  with the long copy's exits lost (section 2), and every setting is slightly negative without each period's 2 best coins.

## 5. What we can and can't trade, in one table

| Part | Its profit, 8 days | Its profit, check.sh window | Tradeable? | Why | Where |
|---|---|---|---|---|---|
| **A** | +102 | +6.02 | **Yes** | routable through pump's own programs; positive in both periods | [strategy A](../03-strategy-A-long-copy/README.md) |
| B | +116 | +0.06 | No | paid in tokens we don't hold; tested +24.6 then +0.4; takes A's slots | §2 |
| C | +60 | +10.68 | No | smaller buys lose or flip between periods | §2 |
| **D** | +29 | +2.87 | **Yes (traded live)** | SOL coins, launch slice; ours +0.15 against its +2.77 | [strategy D](../04-strategy-D-launch-copy/README.md) |
| E | +17 | −2.76 | No | PumpSwap-only; neither bot follows them | §2 |
| F | +29 | +20.16 | No | not a trade (its tokens' price) | §2 |

## 6. How it was computed

- **8 days:** `analysis/research/2026-10-27/h9long/` (`sigs.py` → `pull.py` → `ledger.py` → `groups.py`; the routes in
  `route_cls.py` / `routable.json`; the copy tests in `exits_pess.py`, `grid.py`, `band.py`). Read its README first.
- **check.sh's window:** `analysis/research/2026-10-28/decomp/`: `check_w4.tsv` (the 212 wallet-4 rows typed from the
  check.sh paste: time, coin, its net, its SOL, the bot's status), `kind_trips.json` (each coin's kind from the 8-day
  data), `w4fetchwin.py` (its transactions in the window, public RPC), `scan.out` (the bot's detection on them, from
  `cargo run -p rugsnipe-long --example scan`), and `decomp.py` (the table above).
- **The datasets** (transactions as fetched) are in `data/datasets/` as compressed archives; see CLAUDE.md "Datasets".

## Sources

- `analysis/research/2026-10-27/h9long/README.md` (results, routes, bands, the B test).
- `docs/20-long-copy.md` §1-2; `docs/19-copy-targets-and-dip-buys.md` §11, §13.
- `05-live/check-sh-2026-10-27.txt`; `analysis/research/2026-10-28/decomp/`.
- Session analyses of Oct 27-28 (the A-F tables, the check.sh window, the 5-best split).
