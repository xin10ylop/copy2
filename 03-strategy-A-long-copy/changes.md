# Strategy A: how it was built, change by change

All commits are on `xin10ylop/rugsnipe`, branch `claude/eloquent-mayer-264bxk`. This repo is a snapshot at `7184554`.

| When (UTC) | Commit | What changed | Why |
|---|---|---|---|
| Oct 26 23:43 | `807939b` | research `analysis/research/2026-10-26/h9/` and docs/19 §13: where wallet 4's result comes from; its launch copies to create + 12 at 20% (strategy D) | check.sh showed it at +24.56, our copies −0.25 |
| Oct 27 01:15 | `9538f63` | research in progress: wallet 4 over a week, long tapes, copy rules | |
| Oct 27 01:32 | `d413730` | its other-quote buys ≥ 1.5 SOL with TP 2.0 / SL 0.8 / 30 min pass out of sample | the rule (backtests §2) |
| Oct 27 02:25 | `a7fe78a` | **rugsnipe-long**: the bot (codec, `multi_hop_swap` builder, routes, pricing, process, journal, log/on modes), systemd unit, install, keys, floats CLI, check.sh view, docs/20 | |
| Oct 27 02:29 | `ec2463c` | record every sell signature, learn float prices from its own trades, sell through the pool after graduation, keep the coin account after 2 failed sells | hardening before the first paper run (2RR6sfbi came about 2.5 hours later) |
| Oct 27 10:00 | `435723f` | research: bigger stakes (`scale.py`) | grows to 2-3 SOL, breaks at 5 |
| Oct 27 11:07 | `b5839b0` | `examples/scan.rs`: the bot's own detection and route planner over fetched transactions | to check the bot against the chain |
| Oct 27 11:14 / 11:19 | `553ed1d`, `3cbd0d0` | research: by the size of its buy (`band.py`, `route_cls.py`, `full_paths_band.py`); `grid.py` | |
| Oct 27 11:58 | `e9c403a` | failed sells back off and are capped, late buys reopen, graduation in any state, restart reads landed sells | an audit for the hot bot's 2RR6sfbi failure (`05-live/stuck-coin-2RR6sfbi.md`) |
| Oct 27 12:01 | `611dbcb` | research: the smaller buys lose or flip; settings grid, routes and days | the 1.45 floor stays |
| Oct 27 13:02 / 13:48 | `e21e3ca`, `4340cbd` | `deploy/bin/rugsnipe-history`: both bots' history from saved files (check / all / paper) | fra1 was being shut down |
| Oct 27 16:23 | `252e561` | research: take profit from 1.1x (`grid.py tp`) | 2.0 stays best |
| Oct 27 16:27 | `7cc6f5b` | research: the open-position cap (`grid.py cap`), wallet 4's fees and tips | |
| Oct 27 17:18 | `8845447` | research: the big buys we can't route (part B) | not robust, left out |
| Oct 27 18:02 | `f52cee5` | exit **its_sell**: sell behind its own early sale | CkFH2smc (paper): it sold at 14 min and the copy held to 30 |
| Oct 27 18:18 | `67190be` | `scan.rs`: `SCAN_SOL=1` lists the SOL-priced buys too | the check.sh window decomposition |
| Oct 28 00:16 | `0aa4f24` | a paper buy past `max_premium` is refused like the real one (`long paper-refused`), with `examples/curve_path.rs` | 6y9aDagF doubled in 2 s; paper booked fills a real buy never gets |
| Oct 28 00:34 | `2314377` | `max_open = 4` default | `grid.py cap`: best in both periods, nothing past 4 |
| Oct 28 12:55 | `7184554` | a paper buy fills a slot after **we** saw its buy (`paper_land_slots`, default 1), not after its slot; journal `seen at its slot +N` | 4 of 5 paper take profits came within 10 s; paper ignored Ohio's lag. **Not yet deployed on Ohio** |
| Oct 28 evening | this repo (`xin10ylop/copy2`, branch `claude/magical-einstein-k78idp`), the hardening commit | **8 money-losing fixes** (our feed stream carried failed transactions only; a coin graduating during our buy got no exit; the chain check re-read an old failed sell; a missing pool cached forever; the floor dropped on send errors; `buy_senders = []` meant every sender; wide floors; the never-run paths), the chain check every 2.5 s, a blockhash thread, sender keepalive, the RPC copy in parallel, its sell while buying, the daily stop's scope, `reserve_sol`; paper sells a slot later with the event's fee; `follow_its_sell`, `float_stake_sol`; `simulate --buyback --close`, `simulate-sell --graduated`; 6 new engine tests | the live-readiness review before real money (`07-rework-2026-10-28/code-review.md`); mainnet simulations pass. **Ahead of upstream; not yet deployed on Ohio** |
| Oct 29 00:50 UTC | this branch, the floor commit | `min_out` = the curve's quote at `max_premium` over the price its buy left (`pos::buy_min_out`), not our share of its average fill plus the premium | the old floor let its own buy and our size eat into the 25%: about 1.17x at 0.5 SOL, 1.155x at 1 SOL, against the backtest's 1.25x; two real 0.5 SOL buys were refused at about 1.17x (`deploy-frankfurt.md` §6) |

Tests after the Oct 28 evening change: 15 engine tests and 16 library tests pass. Before it: 9 engine tests (`crates/rugsnipe-long/tests/engine_paper.rs`, among them
`its_early_sell_takes_us_out_behind_it`, `a_paper_buy_past_the_price_limit_is_refused`,
`a_paper_buy_fills_a_slot_after_we_saw_its_buy`) and 15 library tests pass: `cargo test -p rugsnipe-long`.
