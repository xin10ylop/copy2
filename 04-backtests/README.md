# 04. Backtests: an index

Every test run on wallet 4, where its numbers are written up, and the script behind it. **P1 = Oct 19-22, P2 = Oct
23-27** (8-day data). For strategy D the periods are P1 Oct 25 18:00 – Oct 26 06:00 UTC, P2 06:00 – 17:44, P3 live.
Numbers in brackets are without each period's best 2.

## Strategy A (the long copy)

| Test | Result (SOL) | Page | Script (`analysis/research/2026-10-27/h9long/`) |
|---|---|---|---|
| first pass: copy every buy / mirror its sell / scalp the copiers | all lose | [A backtests §2](../03-strategy-A-long-copy/backtests.md) | `sim1.py`, `sim2.py`, `score.py` |
| its 1.5-SOL other-quote buys, TP 2.0 / SL 0.8 / 1790 s, strict exits | P1 +39.53 (+35.92), P2 +15.27 (+12.22) | A §2 | `exits_pess.py` |
| the same, SOL-priced coins | P1 −11.12, P2 −2.34 | A §2 | `exits_pess.py` |
| TP at its own 2.45x | P2 +5.0 (+1.6); negative with a 5% haircut | A §2 | `exits_pess.py` |
| **routable only (what is built)** | P1 +10.97 (+8.51), P2 +12.21 (+9.34); 3 open +11.03 | A §3 | `routable.json`, `route_cls.py` |
| by route: wSOL / WBTC multihop / WBTC curve | P2 +1.08 / +10.02 / +1.12 | A §3 | `route_cls.py`, `grid.py` |
| not routable without Jupiter | P1 +28.57, P2 +3.06 (+0.41) | A §3 | `routable.json` |
| smaller buys, by band (0.8 to 1.5 SOL) | every band loses or flips; 1.5+ P1 +6.69 / P2 +10.43 | A §4 | `band.py`, `full_paths_band.py` |
| stake 1 / 1.5 / 2 / 3 / 5 SOL | grows to 2-3 SOL; 5 SOL P1 −3.33 without its best 2 | A §5 | `scale.py` |
| open-position cap 1 to 5, none | **4 best: P1 +6.73, P2 +11.13** | A §6 | `grid.py cap` |
| take profit 1.1x to 2.5x+ | **2.0x best: P1 +5.03, P2 +9.63** | A §7 | `grid.py tp` |
| landing delay 1 to 10 slots | 2 slots −3-6%, 3 −9%, 5 −20%, 10 about half | A §8 | `grid.py` |
| exits grid (129), trailing stops, stops 0.85/0.9, entry premium | built exits rank 5 of 129; trailing never top 15 | A §9 | `grid.py` |
| its early sell followed (`mix`) | 1 of 135 (P1), 8 of 136 (P2), about −0.14 a copy | A §9 | `grid.py mix` |
| part B (paid in tokens we don't hold) | P1 +24.63, P2 +0.43; with A, P2 +7.38 against +9.63 | A §10 | `ROUTES=E grid.py` |

## Strategy D (the launch copy)

| Test | Result (SOL) | Page | Script |
|---|---|---|---|
| second search: wallet 4 at create + 9 | 1st half +1.89, 2nd half +0.48 | [D §2](../04-strategy-D-launch-copy/README.md) | `analysis/research/2026-10-26/wallets2/` (docs/19 §11) |
| replay: create + 9 / 12 / 15 at 5-50% bounds, three periods | **create + 12, 20%: +0.62 / +0.22 / +1.48** | D §2 | `analysis/research/2026-10-26/h9/replay.py` |
| model calibration on 35 real fills | reads 0.0155 SOL a fill high | D §2 | `h9/calib.py` |
| sell one slot after its first sell | doesn't beat create + 12 | D §2 | `h9/replay.py` |
| hold its SOL-coin buys 30 min (long exits) | P1 −11.12, P2 −2.34 | D §3 | `h9long/exits_pess.py` |

## Live checks (not backtests)

| Check | Result | Page |
|---|---|---|
| the copy bot's wallet, every lamport (Oct 26 13:22 – Oct 27 10:07 UTC) | −1.4115 = closed −0.809, 2RR6sfbi −0.510, failed sells −0.092 | [stuck coin](../05-live/stuck-coin-2RR6sfbi.md) |
| check.sh's window split into A-F | +36.92: F +20.16, C +10.68, A +6.02, D +2.87, B +0.06, E −2.76 | [02-decomposition §3](../02-decomposition/README.md) |
| paper long copy against the chain | 21 of 21 entered, nothing missed | [paper run §4](../03-strategy-A-long-copy/paper-run.md) |
