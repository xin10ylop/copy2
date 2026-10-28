# Code review: `rugsnipe-long` before real money (2026-10-28)

Scope: `crates/rugsnipe-long/src/*`, `crates/pump-codec/src/{multihop,pda}.rs`, the senders and signer in
`crates/rugsnipe-tx`, the engine tests, the examples, `deploy/systemd/rugsnipe-long.service`, `config/long.example.toml`,
and the strategy docs. The code is the copy2 snapshot (`7184554`). I read it line by line. I ran no build and no test.
Two small scratch calculations back the numbers (scratchpad `slack.py`, `papercost.py`). The Yellowstone filter rules were
checked in the reference code (`yellowstone-grpc-proto` 6.1.0, `src/plugin/filter/filter.rs`).

**Verdict: not ready for the 0.1 SOL test as it is.** The real buy and sell path has never run (paper on Ohio had no wallet,
so the code's real-mode branches never ran live). I found 8 problems that can lose money or leave a coin with nobody
managing it. Most are small code changes. The worst one is a feed filter. With it, the bot never sees its own successful
transactions on its "ours" stream (row 1).

Severity words: **money-losing** (can lose stake or fees, or leave coins unmanaged), **correctness** (a wrong book or a
wrong decision), **latency**, **paper-optimism** (paper looks better than real), **robustness**, **security**, **nit**.

## 1. Findings, ranked

| # | Severity | Where | What goes wrong (inputs → outcome) | Fix |
|---|---|---|---|---|
| 1 | **money-losing** | `feed.rs:61-64,70`; `engine.rs:1005-1006,931-940` | The "ours" filter is sent with `failed: Some(true)`. In Yellowstone that means **only failed** transactions (`filter.rs:762-766`: `if is_failed != meta.err.is_some() { drop }`). The hot feed builds it correctly: `(!failed).then_some(false)` (`rugsnipe-feed/src/grpc/mod.rs:363`). So our successful buys and sells arrive only through the "mints" filter, which only holds coins of live positions (`engine.rs:141`). **Scenario:** the bot restarts while a buy is in flight. `recover()` sets `buy_sent_ms = 0`. On the first tick `chase` sees it not landed yet, and `age = now − 0 ≥ 90 s`, so it marks it `dropped`. The coin leaves the watch set. The buy lands a second later. Nothing delivers it, so the `late-fill` never happens. The coins sit in the wallet with no stop, no take profit and no time exit. `recover()` re-reads dropped buys only at the *next* start, and only within 10 min (`engine.rs:1017-1030`). Restarts are routine: 3 on Oct 27-28 (paper-run §1). | `failed: if failed { None } else { Some(false) }`. In `recover()`, keep the stored `buy_sent_ms` and only force an early chase (e.g. a `chase_now` flag), so the 90 s drop counts from the real send time. Add an engine test: a successful own tx arriving as `Src::Ours` for an unwatched coin reopens it. |
| 2 | **money-losing** | `engine.rs:195-201`, `engine.rs:780-784` | A completing trade sets `graduated = true` in any state. It sets `reason = Complete` only when the position is `Open`. **Scenario (2RR6sfbi's exact case, "it graduated as we bought"):** our buy lands just before the completing trade. The feed shows the completing trade while we are still `Buying`. After the fill we are `Open` with no reason. The curve has no more trades, so `p.vt` is frozen. TP and stop can never fire. The coin is held to the 1790 s time exit while it trades on the pool. Only then does the pool sell go out. Paper has the same gap. | In `on_tick`: `State::Open if p.graduated => Exit(Reason::Complete)` (before `exit_due`). Same in `on_ours` on a fill: if `graduated`, set `reason = Complete`. Add an engine test. |
| 3 | **money-losing** | `engine.rs:907-929` | `chase` asks the chain for *all* of a position's sell signatures, then re-applies **the first one that landed**. That is usually an earlier failed sell that was already counted. That second pass adds its fee again (`:647,650`), sets `Selling → Open`, adds a try (`:655-657`) and returns. It never reads the newer sell. Once any signature has landed, the drop branch (`:930-950`) can't be reached. **Scenario:** sell #1 fails on its floor. Sell #2 goes out and succeeds, but its update is lost (feed reconnect, or the engine stalls >15 s). From then on every chase re-reads #1. Each new sell fails with "insufficient funds". The fees go on every 10 min forever, `CRITICAL` fires, one `max_open` slot is lost for good, and the profit is never booked. | Keep `applied: Vec<String>` (signatures already applied) per position. In `chase`, skip applied signatures, apply every unapplied landed one, and take a landed-OK one first. This also fixes row 9. |
| 4 | **money-losing** | `chain.rs:72-81`; `engine.rs:565`; `txlite.rs:66` | `Rpc::cached` stores "account missing" forever. The coin's pool is checked only after 3 failed sells. **Scenario:** the completing trade is missed (feed gap or restart), and when that check runs the pool doesn't exist yet (migration lag: *not verified* how long it is for these coins). The miss is cached for the process's life. Every later sell is a curve sell that fails with `BondingCurveComplete` (6005), slowing to one every 10 min (`pos.rs:145`) and never switching to the pool. That is the 2RR6sfbi failure again. `TxLite` keeps only `err: bool`, so the 6005 code is never read. | Never cache a missing pool (or give misses a 10 s TTL). Keep the instruction error in `TxLite` (Yellowstone `meta.err` / RPC `meta.err.InstructionError`). Treat pump's 6005 on our sell as `graduated = true`. |
| 5 | **money-losing** | `engine.rs:547-553`, `:894-898`, `:942-943` | The sell floor drops by `sell_tries`: a slack of 0.7 from try 2 and 0.999 from try 4. But `sell_tries` also goes up when the **send** fails (for example when `getLatestBlockhash` errors, `:471`) and when a sell is **dropped** unseen. **Scenario:** the RPC fails for about 4 s during a stop (1 s minimum backoff, `:898`). Then the sell goes out with a floor of 0.1% of expected, though no price problem ever happened. | Count only *landed* failures caused by the floor (`ExceededSlippage`-type program errors, once row 4 keeps the code). Use a separate counter for send errors and drops. Never escalate past 0.5 except after graduation, where the curve state is stale. |
| 6 | **money-losing** | `config.rs:168`; `send.rs:30`; `engine.rs:474-481,534` | Confirmed: one signed copy per sender, each with its own tip account, gives different signatures. Two listed buy senders are rejected in mode on (`config.rs:168`). But **an empty `buy_senders = []` is accepted**, and `Out::build` reads it as *every enabled sender*. That gives N buys that can all land. Only the first signature is tracked (`:534`). The extra tokens are unmanaged. The sell's coin-account close then fails twice (non-zero balance) and leaves them stranded. | `if self.mode == Mode::On && self.buy_senders.len() != 1 { bad(...) }`. Add a config test. |
| 7 | **money-losing** (potential) | `engine.rs:547-553`, `config.rs:116-117`, `engine.rs:326` | The floors are wide. In money (§3 table): at a 2.0x TP the expected return is about 1.96 SOL, and the 0.30 slack accepts down to 1.37 SOL (+0.37 instead of +0.96). At the 0.8x stop the expected is 0.78 and the 0.50 slack accepts down to 0.39 (−0.61 instead of −0.22). At a 1.0x time exit it accepts down to −0.51. Retries at 0.7 accept a **TP at −0.41**, and at 0.999 any price. The buy's floor is wallet 4's fill +25%, whatever the price is now. If the price is still near its fill, a sandwich can push our buy up to the cap, about 20% of the stake. *Not verified* how often our transactions would be sandwiched (a Nozomi copy plus a public `sendTransaction` copy). | TP slack 0.10-0.15 (a missed TP is re-checked on the next trade anyway). Stop, time and its-sell at 0.20-0.25 on the fresh curve state. Escalate only per row 5. Measure in the 0.1 SOL test: log expected vs received on every sell, and fill vs its price on every buy. |
| 8 | **money-losing** (untested) | `examples/sim_pool_sell.rs:45-55`; `main.rs:131-183`; `multihop_fixtures.rs:108,139`; `engine.rs:518-519,600-601` | Never run on chain: (a) the **2-hop pool+pool sell into wSOL after graduation**. 20 of the 21 paper buys on Ohio were 2-hop copied routes (journal), and the documented simulation was C5xph2yL / EJAxERvK *into WBTC* (stuck-coin page). (b) A sell that **closes the coin account**: both simulators pass `close_coin = false`. (c) **Buyback recipients 1-7**: the fixtures and simulators use index 0, but the engine rotates 1, 2, 3 ... If a recipient has no account for the outer mint (wSOL, WBTC), those transactions fail. *Not verified* either way. | Before the test, simulate on mainnet: the 2-hop pool+pool sell into wSOL and into WBTC, a sell with `close_coin = true`, and a buy and a sell at each index 0-7 for wSOL and WBTC. Or pin the index wallet 4 itself uses. |
| 9 | **correctness** | `engine.rs:647` | `on_ours` adds the lamport and float change *before* any state check. Any second delivery of the same transaction counts it again. **Scenario:** the engine thread blocks for more than 20 s (row 12), and the feed buffers our fill (unbounded channel, `feed.rs:182`). The chase reads the fill by RPC, then the buffered copy arrives. The fill's −1 SOL is booked twice. `realized_today` can then trip the daily stop, and `closed.jsonl` is wrong. | The same `applied` set as row 3: return early if the signature is already applied. |
| 10 | **correctness** | `engine.rs:224-229` | Wallet 4's sell is acted on only when we are `Open`. While we are `Buying` it is only printed. **Scenario:** our fill update is late (chase after 20 s), or it sells within seconds (ChonQdJ8 sold after 7 s). We then hold behind a seller up to 30 min. | Keep an `its_sold` flag in any state and set `reason = ItsSell` at the fill. |
| 11 | **correctness** | `engine.rs:40,389-397`; `going-live.md` §3 step 3 | `SOL_RESERVE` is 0.05 SOL. A wSOL buy needs `stake + 0.05` in the wallet. The plan funds "a little over 0.1 SOL plus fees". With 0.12 SOL, **every buy is skipped** ("SOL balance ... under the stake + reserve"). | Fund at least ~0.16 SOL (0.1 stake + 0.05 reserve + fees + ~0.002 coin-account rent). Or make the reserve a config value. |
| 12 | **latency / robustness** | `engine.rs:774-779,915`; `feed.rs:79` | `chase` has no rate limit. It runs on **every tick** while a buy is unseen for more than 20 s or a sell for more than 15 s, up to 90 s. Every message triggers a tick. The default slot filter alone sends processed + confirmed + finalized, 3 messages a slot (`filter.rs:640-647`), so about 7.5 a second. Each chase is a blocking `getSignatureStatuses(searchTransactionHistory)`. One dropped transaction means hundreds of blocking calls. The engine thread spends its time waiting on the RPC, the feed backs up, exits of other positions are late, and the RPC may rate-limit. Paper never chases, so this never ran. | A `next_chase_ms` per position (every 2-3 s). Better, chase on a worker thread. Use `filter_by_commitment: Some(true)` for slots, as the hot feed does (`grpc/mod.rs:394-397`). |
| 13 | **latency** | `engine.rs:452-461,488-499`; `providers.rs:134,229`; `crates/rugsnipe/src/sender.rs:536-540` | The send path is cold for almost every buy. The blockhash is fetched only on demand (cache 20 s, and triggers come about once an hour), on a pooled TLS connection that has gone idle. The sender connection is never kept alive (the hot bot renews it every 20 s; the long bot never calls `keepalive`), and providers close idle sockets after about a minute (`http.rs:150-153` comment). The RPC copy goes out only after the Nozomi call returns. The default Nozomi endpoint is Frankfurt (`http://fra2...`). **Estimate** (round trips, RTT): blockhash ≈ 3 RTT_rpc cold, Nozomi ≈ 2 RTT cold, RPC copy +1 RTT_rpc after that. From Ohio to Frankfurt (~100-105 ms RTT, `deploy/aws-ohio-analytics.md:5,133`), Nozomi gets the buy about 0.5 s after we see the trigger (more than a slot), and the RPC copy about 0.6 s. With US endpoints (RTT *not measured*; assume ~15 ms): about 75 ms. Warm, with the blockhash prefetched: 1 RTT, about 15 ms. A TP within seconds of the buy reuses warm connections; time and stop exits are cold again. | (a) Refresh the blockhash every 2-5 s on a timer thread. (b) Call `Sender::keepalive()` every 20 s, as the hot bot does. (c) Send the RPC copy in the same `thread::scope` as the senders. (d) Don't wait for send replies on the engine thread. (e) Use Nozomi's US endpoint (going-live §3 step 2). (f) Prefetch pool existence for the known quote tokens. Measure with `deploy/latency_probe.sh`. |
| 14 | **latency / robustness** | `engine.rs:756-758,955-974`; `rpc.rs:37`; `providers.rs:229`; `http.rs:194-203` | Every chain read runs on the engine thread: `refresh()` (2 calls every 30 s, *before* the exits in `on_tick`), chase, and `getTransaction`. `RpcClient` has a 20 s timeout. The HTTP senders have 1.5 s connect and read timeouts, with one retry. A slow RPC freezes all exits for up to 20 s per call. | Move `refresh` and chase to a worker that posts results back over the channel. Use a short RPC timeout (2 s) on the decision path. |
| 15 | **robustness** | `chain.rs:139-148`; `engine.rs:488-499,933` | No rebroadcast. Each transaction goes out once per sender, plus one `sendTransaction` with `maxRetries: 0`. A dropped sell waits **90 s** before it is retried, which is long during a stop. A sell that *no path accepted* (sender error, RPC error) still goes to `Selling` and waits. | Re-send the same signed bytes every ~1.5 s until it lands or about 40 s pass (same signature, so it can't double). If no copy was accepted, treat it as a send error and retry in 1 s. |
| 16 | **paper-optimism** | `engine.rs:791,851-853,35` | Paper's costs are much lighter than the backtest's. Paper: 0.00321 SOL fixed a round trip, plus the 1.25% curve fee each way. Backtest: 0.0345 fixed (2 × 0.0095 + the 0.0155 bias measured on real copies) plus a 5.13% route cost (`grid.py:15-16`). **Re-costing the 20 closed paper trades with the backtest's costs: +2.65 → +1.39 SOL**, about 0.063 SOL a trade (`papercost.py`). Which model is right is unknown. The simulated 3% round trip supports paper's percentage part. Nothing in paper covers the 0.0155 bias (−0.31 over 20 trades on its own). | The 0.1 SOL test decides. Report paper next to a "backtest-cost" column in `history.py`. |
| 17 | **paper-optimism** | `engine.rs:155-165,844-856` | Paper sells at the curve state of **the trade that fired the rule**. The backtest (`exits_pess.py`) fills on the next trade of a later slot. A real sell lands 1-3 slots later. On the frenzy take profits (4 of 5 within 1-10 s) and on fast stops (#8: −31% at the firing trade), real fills will be worse. *Size not measured.* | Paper: fill exits at the end of the slot after the firing one, like the entry (`paper_land_slots`). |
| 18 | **paper-optimism** | `engine.rs:374`; backtests.md §8 | Paper's entry fills at the end of seen-slot +1. Real from Ohio: the send leaves 0.1-0.6 s after the trigger (row 13) and lands about seen +1 to +3. The backtest: 2 slots late costs 3-6% of profit, 3 slots about 9%, 5 slots about 20%. | Set `paper_land_slots = 2` once `7184554`'s `seen at its slot +N` shows Ohio's lag. |
| 19 | **paper-optimism** | `engine.rs:797-799,849-850` | On a wSOL → pool(X) → curve route, paper converts at **wallet 4's all-in rate**, both on the buy and on the sell. It ignores: (a) the pool move from wallet 4's own 1.5 SOL just before ours. On a constant-product pool our rate is worse by about (1.5 + 1)/x, where x is the pool's SOL reserve: 2.5% at 100 SOL, 8% at 30 SOL. (b) X's own price change over the hold (X is a memecoin: CSRRgTwf, NTRNDMqQ, C5xph2yL ... from `verify/scan.out`). (c) The pool fee and buyback fee on the way out. X's pool depths were *not measured*. | Read the X pool's reserves at the trigger. Price the pool hop in paper with `cp_out` both ways, at the live reserves on the sell. |
| 20 | **paper-optimism** | `engine.rs:35,799,849`; `events.rs:87`; docs/02 §Fees | The curve fee is fixed at 125 bps. Coins priced in other tokens can carry creator fees up to 300 bps (3.95% a side). The trade event carries `fee_basis_points` and `creator_fee_basis_points`. Also, the event's quote amount is "before fees" (`events.rs:87`), so paper's buy takes the fee off twice: about 1.25% pessimistic on the buy. The net effect per coin is unknown. | Read both bps from wallet 4's trade into `Trigger`, use them in the paper fill, the paper sell and `sell_min_out`, and don't charge the fee again on the buy's quote. |
| 21 | **paper-optimism** | `engine.rs:425-426`; `feed.rs:211-219` | A new coin joins the feed only after the trigger, through a re-subscribe. Its trades before the new filter takes effect are missed. If no later trade in the fill slot is seen, the paper fill uses wallet 4's post-trade state, which is too cheap on frenzy coins. (A re-subscribe replaces the filters. Yellowstone doesn't replay, and held coins stay in the new set, so their exits have no gap; implementation-dependent, *not verified* on Ohio's provider.) | Paper only: read the bonding-curve account when the fill slot ends. |
| 22 | **paper-optimism** | `engine.rs:793-828,848-877` | Paper can fail only on the price limit. No drops, no failed sells, no retries. On graduation it sells at once at the final curve price. Real must wait for the pool, pays the pool fee (1.25% below 420 SOL market cap, docs/02) and meets a thinner pool. | Keep in mind. The 0.1 test measures it. |
| 23 | **correctness** | `engine.rs:629-647`; `oracle.rs:49-54` | If the oracle has no price, a float's change is valued at `unwrap_or(0.0)`. Within one run this can't happen after a WBTC buy, because the buy needed a fresh price and entries are never removed. **After a restart** before the first Jupiter fetch (or with the API down), a WBTC position's sell books its WBTC at 0. That is a −100% close in `closed.jsonl`, and `realized_today` can trip the daily stop. | If there's no price, store the raw anchor change and value it when a price arrives. |
| 24 | **correctness** | `engine.rs:133,751,766-835` | `save()` prunes the book. `on_tick` collects actions by **index**, then a chase → `on_ours` → `save()` can remove an old closed position mid-loop. The later actions then hit the wrong position (sell the wrong coin) or index out of range (a panic, which with `panic = "abort"` kills the process). Rare: an old position must pass 3 days within that tick. | Act by position id, or prune once at the start of `on_tick`. |
| 25 | **correctness** | `engine.rs:691-695,541-545` | If our fill has no curve trade with `user == me`, `quote_in` is overwritten with 0. The sell rate becomes 1.0, mixing X units with lamports, and the floor is nonsense (too high: sells fail until try 4; too low: no floor). | Keep the trigger's estimate when the trade isn't found, and log it. |
| 26 | **correctness** | `pos.rs:299-308`; `engine.rs:591` | The daily stop counts `Closed` only: failed-buy fees, failed-sell fees on open positions and open losses (a stuck coin) don't count. That is the stuck-coin lesson 3. After 2 failed sells the coin account is no longer closed, and its ~0.0021 SOL rent stays locked (2% of a 0.1 SOL stake). | Count Failed fees and live positions' `costs`. Close empty coin accounts later in a sweep, or sell the on-chain balance and always close. |
| 27 | **robustness** | `pos.rs:276-292`; `engine.rs:88`; `rugsnipe-long.service:16-17,28-29` | A corrupt `positions.json`, a typo in `long.toml` or a missing credential makes the process exit at start. `Restart=always` with `RestartSec=2` and `StartLimitBurst=20` in 300 s: after about 40 s systemd stops trying, and **open positions are left alone**. `save` renames without fsync. | Keep `positions.json.bak` and fall back to it. Add `rugsnipe-long check --config` to run before every restart. Alert on unit failure (OnFailure=). |
| 28 | **robustness** | `engine.rs:262-265`; `engine.rs:649-654,1017-1030` | `its_bought` lives in memory only: after a restart, its second buy of a coin bought before the restart is copied. `recover()` re-reads a landed-failed dropped buy at every restart within 10 min, because the error branch doesn't clear `dropped`, so its fee is counted again. | Rebuild `its_bought` from the book. Clear `dropped` on a landed failure. |
| 29 | **security** | `main.rs:568-609` | `float buy/sell` signs whatever the Jupiter lite API returns, without checking it. Nothing checks the fee payer, the accounts or the balance changes. The trust rests only on HTTPS to `lite-api.jup.ag`. | Simulate before sending, and refuse if anything other than our SOL and float balances changes, or if the out amount is under the quote's minimum. |
| 30 | **security** (low) | `http.rs:26-28`; `providers.rs:555` | The sender client speaks **plain HTTP only**, with the key in the URL (`/api/sendBatch?c=KEY`). From Ohio to Frankfurt it crosses the internet in clear text. It's a send-only key. | Accept, or put a TLS proxy (or WireGuard) in front. Don't reuse the key elsewhere. |
| 31 | nit | `config.rs:115`; README §3 | `cu_limit` 300k against 166k measured on a 2-hop buy. The priority fee is charged on the limit: 0.0006 instead of ~0.0004 SOL a buy (0.2% of a 0.1 SOL stake). | Measure the graduated 2-pool sell's units in row 8, then set ~220k. |
| 32 | nit | `send.rs:66` | The tip always goes to the sender's first tip account (write-lock contention with everyone else doing the same). | Rotate tip accounts. |
| 33 | nit | `main.rs:382-411`; going-live §3 step 5 | `status --chain` prints the SOL and float balances only. It doesn't compare the book with the chain (the doc says it does). | Print each live position's on-chain coin balance and any stray token accounts. |
| 34 | nit | `engine.rs:256-260` | `oracle.set` from its Jupiter leg includes its tips and rent (about 0.1-0.3% high), with no sanity band against the API price. | Accept only within ±3% of the last API price. |
| 35 | nit | `engine.rs:547-552`; docs/20 §3 | The doc says "the floor drops each time". It drops at try 2 and try 4 only. A TP sell that fails, after which the price falls under 2.0x, isn't retried (`exit_due` is re-checked). | Fix the doc, or say this is intended. |

## 2. Must change before the 0.1 SOL real test

1. **Feed filter** `failed: None` for "ours" (row 1), and `recover()` dropping by the real send age (row 1).
2. **Graduation during the buy** exits at once (row 2).
3. **`applied` signature set:** chase reads only unapplied signatures, and `on_ours` is idempotent (rows 3, 9).
4. **Chase every 2-3 s,** not every tick (row 12).
5. **No cached "pool missing",** and read error 6005 as graduation (row 4).
6. **Floor escalation only on landed slippage failures,** not on send errors or drops (row 5).
7. **`buy_senders` must have exactly one entry** in mode on (row 6).
8. **Fund ≥ 0.16 SOL,** or lower `SOL_RESERVE` for the test (row 11).
9. **Mainnet simulations:** the 2-hop pool+pool sell into wSOL and WBTC, a sell with `close_coin = true`, and buyback indexes 0-7 (or pin one) (row 8).
10. **Send path:** Nozomi US endpoint, sender keepalive every 20 s, blockhash on a timer, RPC copy in parallel (row 13). Without these, the test measures a cold path to Frankfurt, not the bot.
11. **Its sell while `Buying`** applied at the fill (row 10). It's small.
12. Engine tests for 1-7 and 11, plus a line each in `docs/20-long-copy.md` §3 (CLAUDE.md conventions).

## 3. Can wait (until before 1 SOL × 4)

- Tighter floors (row 7): decide from the test's logged expected vs received.
- Rebroadcast and the no-path-accepted case (row 15); RPC off the engine thread (row 14).
- The book: oracle-less valuation (23), prune by id (24), `quote_in` fallback (25), daily-stop scope and the locked rent (26),
  `positions.json.bak` and a `check` command (27), `its_bought` and recover (28).
- Paper fidelity: exit fills a slot later (17), `paper_land_slots` from the measured lag (18), the pool hop priced live
  (19), real fee bps (20), the curve read at the paper fill (21). Also the cost-model question (16).
- `float` simulation check (29), sender TLS (30), nits 31-35.

## 4. Short answers to the eight questions

**1. The real path.**
- **Instruction order is right** (`txb.rs:58-90,112-139`). The order is budget, then the wSOL account created, the stake transferred in, `SyncNative`, the coin account created, the swap, the wSOL account closed, and **the tip last**. A failed swap reverts the tip: the transaction is atomic and the tip comes after the swap.
- **The RPC copy carries the same bytes as sender 0's copy** (`engine.rs:495-496`), so it has the same signature and can't double-fill. Confirmed.
- **Two buy senders mean two signatures**, which can double the position. Confirmed. Validation catches 2 senders but not `[]` (row 6).
- **The rewrite after graduation is right in direction and accounts** (`engine.rs:572-589`). For example, curve(coin/X) + pool(X/wSOL) reversed becomes pool(coin/X) then pool(X/wSOL). Both sell their base. The pool vaults are the pool's ATAs under the coin's program and the quote's program. The `TOKEN_2022` fallback applies only to records without `quote_program` (`serde(default)`). A new position always stores it (`detect.rs:134-136`), and if it were wrong the buy itself would have failed.
- **The buy's `min_out`.** When our anchor differs from its input, `share = stake / its SOL value` (`engine.rs:320-324`). Its SOL value is its Jupiter spend × the used share (`detect.rs:118-124`). So our wSOL → X pool hop is assumed to match its Jupiter rate. A worse pool hop only shrinks the 25% budget, which means more refusals, never a worse fill than +25%.
- **Compute:** 300k against 166k (row 31).
- **Blockhash:** 20 s cache (row 13).
- **Waits and drops:** a 20 s and 15 s wait, then a chase (row 12). The 90 s drop is safe for double-spending, but slow for sells (row 15). The late-fill reopen works only from `recover()`, not at runtime (row 1).

**2. Accounting.**
- **Oracle missing:** row 23.
- **Paper per round trip:** 2 × (5,000 + 600,000) + 2 × 1,000,000 = **3,210,000 lamports**. Real: buy 1,605,000 + sell 1,305,000 = **2,910,000**. Paper overcharges 0.0003 SOL, because it prices the sell at the buy's CU price. Real also locks ~0.0021 SOL of coin-account rent until the close (computed for a 170-byte Token-2022 account, not read from the chain).
- **Refused buys:** the paper `refused_fee` (605,000) equals what a real refused buy pays.
- **Daily stop:** `realized_today` ignores refused and failed fees and open positions (row 26).

**3. Exits.**
- **The price formula is right** (`multihop.rs:363-369`): `(vt_ref / (vt + ours))²` is exact for pump's curve, because the fees are outside the reserves.
- **There is no 250 ms delay.** `on_tick` runs after **every** message (`engine.rs:154-166`), so a TP is built microseconds after the trade that fired it. Only a due `refresh()` (every 30 s) or chase in the same tick adds round trips first.
- **After the TP fires,** only `min_out` protects the sell (row 7).
- **`ItsSell`:** the backtest kept only coins with exactly one buy and one sell (`grid.py:24`, `len(x["tr"]) != 2`). Partial sells and rebuys were never scored. The bot follows the first sell, partial or not. That's consistent, but untested.
- **Same-slot trades:** the `>= last_slot` rule lets the last-delivered trade of a slot win. That's fine if Yellowstone delivers in execution order (*not verified*).
- **`its_bought`:** in memory only (row 28).

**4. Latency.** Rows 12-14. The engine's own work (detect, plan, about 5 PDA derivations, signing) is about a millisecond or less. Network round trips are everything.

**5. Paper fidelity.** Rows 16-22. By size, roughly:
- Costs: about 6% of a 1 SOL trade against the backtest's model, if the backtest's model is right.
- Entry lag: 3-9% of the profit.
- The pool hop: 2.5-8% of the stake on the buy, if the X pool holds 30-100 SOL (not measured).
- Exit timing: not measured.
- Fees: ±1-3% a side.

**6. Robustness.**
- **No panic found on odd transactions.** `txlite`, `detect` and the engine's slices are all guarded. Signatures are always 64-byte base58. Mints are ≥ 32 characters. `txs` is never empty (`engine.rs:474`).
- **Panics and restarts:** `panic = "abort"` (Cargo.toml) plus `Restart=always` restarts the process after any panic.
- **Oracle down:** WBTC routes and float-paid triggers are skipped after 120 s (`engine.rs:314-317`, `oracle.rs:44`).
- **The book:** KILL, `max_open` and the 3-day prune are fine apart from row 24. `Book::save` uses an atomic rename without fsync (row 27).

**7. main.rs.**
- **`float`:** Jupiter lite swap v1, 50 bps slippage, priority capped at 0.002 SOL. It signs blind (row 29). The key is loaded only to sign.
- **`keygen`:** `/dev/urandom` seed, `create_new`, mode 0400, and a reload check. Fine.
- **`status --chain`:** row 33.
- **`simulate`:** index 0 and no close only (row 8).

**8. Security.**
- **Keys are handled well.** `HotSigner` zeroizes, and its Debug shows only the public key. `ApiKeys` Debug shows only names. The feed URL is redacted in the start line. The wallet comes in through systemd credentials.
- **Leak risks:** the plain-HTTP sender keys (row 30) and the blind Jupiter signing (row 29). No path prints the RPC URL except a ureq "bad URI" error on a malformed URL (*not verified*).

## 5. The numbers behind the rows

**Fees (from `long.example.toml`):**

| | lamports | SOL |
|---|---|---|
| buy: 5,000 + 300,000 × 2,000,000 / 1e6 + tip 1,000,000 | 1,605,000 | 0.0016 |
| sell: 5,000 + 300,000 × 1,000,000 / 1e6 + tip 1,000,000 | 1,305,000 | 0.0013 |
| round trip, real | 2,910,000 | 0.0029 |
| round trip, paper `exit()` | 3,210,000 | 0.0032 |
| refused buy (real = paper) | 605,000 | 0.0006 |
| failed sell | 305,000 | 0.0003 |
| coin account rent, locked until close (Token-2022, 170 bytes: 298 × 6,960) | 2,074,080 | 0.0021 |

**What the sell floor accepts, 1 SOL stake** (`slack.py`):
- The model: a curve priced in SOL terms, entry at its price, the 1.25% fee each way. The route's pool hop is not included.
- The results are nearly the same for curve quote reserves of 40, 80 and 150.

| exit | expected back | slack | worst accepted back | worst net |
|---|---|---|---|---|
| TP 2.0x | 1.96 | 0.30 | 1.37 | +0.37 |
| TP 2.0x, try 2-3 | 1.96 | 0.70 | 0.59 | −0.41 |
| time 1.0x | 0.975 | 0.50 | 0.49 | −0.51 |
| stop 0.8x | 0.78 | 0.50 | 0.39 | −0.61 |
| any, try ≥ 4 | — | 0.999 | ~0 | ~−1.0 |

**Paper re-costed** (`papercost.py`):
- The inputs are the 20 closed nets in paper-run.md §2 (sum +2.6528, against +2.6541 in the doc after rounding and the 2 refused fees).
- With the backtest's costs instead (COST 0.9487 on gross, 2 × 0.0095, the 0.0155 bias), the total is **+1.39 SOL**.
- Paper with only the 0.0155 bias added: +2.34.

**Send-path latency** (row 13): N round trips. The Ohio → Frankfurt RTT is the documented ~100-105 ms. The US RTT is an assumption to measure with `deploy/latency_probe.sh`.

| case | before Nozomi has the buy | RPC copy |
|---|---|---|
| now, Frankfurt endpoints, cold | ~3 RTT_rpc + 2 RTT ≈ 0.5 s | ≈ 0.6 s |
| US endpoints, cold | ≈ 5 × 15 ms ≈ 75 ms | ≈ 90 ms |
| prefetched blockhash, warm sockets, parallel RPC copy | 1 RTT ≈ 15 ms | ≈ 15 ms |

## 6. Checked and right

- Tip placement and atomicity.
- The RPC copy (same signature).
- wSOL wrap and unwrap, and the ATA create/close order.
- The price ratio formula, and that paper leaves our tokens out of the price.
- The direction and accounts of the graduated-sell rewrite.
- The refused fee.
- Exits evaluated right after each trade.
- The backoff schedule (`pos.rs:144-154`), apart from what counts as a try (row 5).
- KILL and `max_open`.
- Secret handling (`keys.rs`, `signer.rs`).
- No panics on malformed transactions.
- The hot unit's feed builds the failed filter correctly. Only the long bot's `feed.rs` has the bug.
