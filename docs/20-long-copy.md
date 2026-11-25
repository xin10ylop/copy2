# 20. The long copy: wallet 4's big buys of coins priced in other tokens (Oct 27)

`rugsnipe-long`, its own process and wallet beside the hot unit. Research in
`analysis/research/2026-10-27/h9long/`, code in `crates/rugsnipe-long/` and `crates/pump-codec/src/multihop.rs`.

## 1. How H9kuqGKN makes its money

- **+355 SOL in 8 days** (Oct 19 to Oct 27; its SOL rose +412 with +11.9 deposited, 467 SOL now). Every day positive.
- **Where:** pump coins priced in other tokens (WBTC, PUMP, TTWO, USDC, xStocks, graduated pump coins): +278 on 3,056
  coins. SOL-priced pump coins +29, PumpSwap-only tokens +17, the quote tokens it holds +29.
- **Its rule:** one buy (tiers of about 0.9, 1.13 and 1.5 SOL), one sell of everything at **2.5x** the price its buy
  left, at **0.7x**, or after **30 minutes** (77% of its trips). About 10% of trips reach 2.5x; they carry all the
  profit. Its 1.5-SOL buys reach it about twice as often as the small ones.
- **The check view's per-coin numbers for this wallet are wrong coin by coin** (a coin sold into its quote token shows
  its profit on the quote token's row); only its total is right.

## 2. The copy, and the test it passed

Copy its 1.5-SOL buys of coins priced in other tokens, 1 SOL each, landing in its slot or the next; sell at **2.0x**
its price, **0.8x**, or **29:50**. Picked on Oct 19-22, scored on Oct 23-27, worst-case fees (0.0095 SOL a
transaction), the replay's 0.0155 SOL bias off every fill, **its own sale placed ahead of ours whenever the two are
within a slot** (`exits_pess.py`):

| | Oct 19-22 | Oct 23-27 (out of sample) |
|---|---|---|
| all its 1.5-SOL other-quote buys | +39.5 (+35.9 without the best 2) | +15.3 (+12.2) |
| **the ones pump's own programs can route (what is built)** | +11.0 (+8.5) | **+12.2 (+9.3); at most 3 open: +11.0 (+8.2)** |
| SOL-priced coins | -11.1 | -2.3 |

- **2.0x and not its 2.5x:** its sale is as fast as ours and big enough to move the price. At 2.45x its sale came first
  on 83 of 126 take-profits; at 2.0x on 8.
- **We don't take its profit:** our buy lifts the price by our own tokens (about 6%, 8.5% at 2x) and our sell takes
  exactly that back out; once we are out the curve is where it would be without us.
- **Risks:** the edge is shrinking (its big buys hit 2.5x 29% of the time on Oct 19, about 10% now; about +4 SOL a
  day on Oct 23-27 against +10 before); a few take-profits carry everything; Oct 23-27 rests on WBTC-routed coins
  (+10.0 of +12.2).

## 3. How it trades (`crates/rugsnipe-long`)

- **Feed:** a Yellowstone stream of its own (the hot config's `[feeds] grpc`): wallet 4's landed transactions, every
  transaction of ours (failed too), every transaction on a coin we hold, slots.
- **Trigger:** its buy of a pump coin whose curve quote is not SOL, valued at **1.45 SOL or more** (its 1.5 tier):
  wrapped SOL into its `multi_hop_swap`, or the share of what it sent Jupiter that the buy used (it sends 5/3 SOL and
  keeps about a tenth), or a held token at the oracle price. Its second buy of a coin, a coin already ours, a complete
  curve, `max_open`, the daily stop and a `KILL` file in the state dir are skips.
- **The dip entry** (Nov 19, `dip_drop` / `dip_within_s`, the unit `rugsnipe-long-dip` with its own wallet and
  `config/long-dip.example.toml`): its buy, past every skip above, is watched instead of copied; the first trade of a
  later slot at or under (1 - `dip_drop`) x the price its buy left, within `dip_within_s`, buys (the skips run again),
  with that state as the reference; no dip in time, no trade. Research `analysis/research/2026-11-17/wallet_hunt/
  market/m14-m15d` (10% within 60 s, tp x1.5 over our fill or 900 s: +12.1% a trade on Oct 21 - Nov 13 out of sample,
  up every week). Tests: `the_dip_unit_watches_its_buy_and_buys_only_on_the_dip`, `a_dip_watch_ends_after_its_time_
  without_a_trade`, `without_dip_drop_the_copy_buys_at_once_as_before`.
  The dip leg's exits are its own (`dip_take_profit` over our fill, default 1.5; `dip_max_hold_s`, default 900; no stop,
  no sell pressure, no stall, its sale not followed), and it has its own `max_open` count.
- **The split** (Nov 19, the owner: "from the same bot ... we split 0.5, 0.5, and if it works we do a separate bot"):
  `dip_stake_sol > 0` in the main unit keeps the copy (leg 1, bought at once with `stake_sol`, its exits unchanged) and
  adds the dip leg (leg 2, `dip_stake_sol`) on the same buy of its: at most one of each per coin; the dip watch is parked
  even when leg 1 is full; a sale never closes the coin's account while the other leg still holds it. `status` shows
  one row per buy of its with `exit1 held1 pct1 net1` and `exit2 held2 pct2 net2` (pct = net over that leg's own
  stake), and each leg's totals. Tests: `the_split_buys_the_copy_at_once_and_the_dip_leg_on_the_dip`,
  `the_dip_leg_takes_its_own_profit_and_the_copy_leg_holds`, `the_dip_leg_ends_on_its_own_hold_and_ignores_the_signals`,
  `its_early_sale_takes_out_the_copy_leg_only`, `each_leg_has_its_own_max_open` (the account rule is real-mode only).
  `dip_float_only` (Nov 19, the owner: "only keep floats"): the dip leg only when our route pays with a float, since
  wSOL-paid dips made +3.1% a trade and lost over their last 2 weeks against +15.9% float-paid (m15f); the copy leg keeps
  wSOL. The route is now planned before the `max_open` check. Test:
  `the_float_only_dip_leg_skips_a_wsol_paid_buy_and_the_copy_still_buys`.
  Nov 20: leg 2 off in the main unit (`dip_drop = 0`; the owner will run it from its own wallet). `status` shows the
  two-leg table only while the split runs; otherwise the one-leg table as before, the old dip legs left out of its rows and
  counted in one line above the totals.
- **Route:** PumpSwap's `multi_hop_swap` (16 accounts + 5 a hop), byte-equal to wallet 4's own (`tests/multihop_fixtures.rs`).
  Its own route is copied when it starts from wrapped SOL or a float we hold (WBTC); a direct curve buy goes behind its
  quote's canonical pool against wSOL or WBTC. Wrapped SOL is wrapped and unwrapped inside the transaction. At most 2
  hops (a 3-hop transaction is over 1,232 bytes); no Jupiter leg (that part made +0.4 out of sample).
- **Buy:** one transaction, one sender (two landing would double the position) plus the same bytes by
  `sendTransaction`; `min_out` is the curve's own quote at `max_premium` (25%) over the price its buy left (the
  backtest's limit; our own impact is inside the quote, so the floor does not tighten with the stake; until Oct 29 it
  was its average price plus the premium, about 7% tighter at 0.5 SOL, and two real buys were refused at about 1.17x).
  A paper buy fills on the curve at the end of `paper_land_slots` (1) slots after the slot our feed saw its buy
  in (journal `seen at its slot +N`: our feed's lag; before 2026-10-28 it filled after its own slot +1) and is
  refused by the same `min_out`
  (journal `long paper-refused #N`, state failed, the fee a landed failure pays): 2026-10-27, coins it buys can
  double within 2 seconds (6y9aDagF: 1.2x after 1 s, 2.0x after 2 s), and a paper fill past the limit would
  book a trade the real buy never gets.
- **Exits:** on every trade of the coin, the curve price against the price its buy left, **without our own tokens**:
  take profit 2.0x, stop 0.8x, 1790 s after its buy, the curve completing, or **its own sell** when it leaves first
  (2026-10-27, CkFH2smc: it sold after 14 minutes and the copy held to 30; the backtest's price path ends at its sale,
  so its copies sell right behind it: `grid.py mix`, 1 of 135 copies on P1 and 8 of 136 on P2; journal
  `long its-sell #N <mint>: out behind it`, exit `its_sell`). The sell goes back along the route,
  closes the wSOL and coin accounts (their rent comes back), and is retried with a lower floor if it fails or drops.
- **When things fail** (2026-10-27, after the hot bot's 2RR6sfbi): a sell that lands and fails goes again at once 3
  times (the floor drops each time), then waits 5 s, 30 s, 2 min, and past `max_sell_fail_sol` (0.01) of failed fees
  on the position every 10 min; never given up (journal `long CRITICAL sells of #N ... keep failing`). A coin whose
  curve completes in any state (a sell already out included) sells on its canonical PumpSwap pool, as after 3 failed
  sells when the pool exists (simulated on mainnet: C5xph2yL and EJAxERvK into WBTC, `examples/sim_pool_sell.rs`). A
  buy not seen in 90 s is given up as dropped; if it lands after all (`long late-fill`), the position reopens on its
  tokens, also when it landed while the bot was down. Statuses search the whole history, so a sell that landed while
  the bot was down closes the position instead of being sold again.
- **Hardened before real money (2026-10-28, the live-readiness review, `07-rework-2026-10-28/code-review.md`):**
  our own feed stream carries successes too (the filter said failed-only, so a buy given up as dropped that landed
  after all was never seen); a coin whose curve completes while our buy is out sells on the pool at the fill (the
  exit reason was set on open positions only: 2RR6sfbi's case, the price frozen, held to the timer); every
  transaction of ours is booked once (`applied`), and a chain check reads the unbooked signatures, successes first
  (it re-read the first landed one, an old failed sell, on every pass); a chain check every 2.5 s, not every
  message; a missing account (a coin's pool before migration) is remembered 30 s, not forever; after a landed
  failed sell the curve is read, and a complete one sends the next sell to the pool; the floor drops only after
  landed failures (2: half, 4: almost any price), never after send errors or drops (`send_fails`); the defaults
  are 15% under the expected output on a take profit and 30% otherwise (were 30% / 50%); `buy_senders` must name
  exactly one sender in mode on (an empty list meant every enabled sender: several buys); `reserve_sol` (0.05) is a
  setting, so a 0.1 SOL test wallet needs about 0.16 SOL; the blockhash is refreshed every 3 s on its own thread,
  the senders' connections are kept alive every 20 s and the RPC copy goes out beside the sender's, not after
  (the buy was built on a cold path: about 0.5 s from Ohio to Frankfurt); a send that no path accepted is an
  error and retried in 1-5 s; its sell while our buy is out takes us out at the fill (`its_sold`); a restart
  checks a transaction in flight at once but drops it only by its real age; the day's result for the daily stop
  counts refused buys' fees and the live positions' failed-sell fees; the book is pruned once per tick; a float
  leg without a price is booked at 0 with a warning; its buys we copied are rebuilt from the book at start;
  the journal says how long a buy or sell took to send (`sent ... in N ms`) and at what feed lag (`seen at its
  slot +N`). **Simulated on mainnet** (`rugsnipe-long simulate --buyback N --close`, `simulate-sell --graduated`):
  the 2-hop buy from wSOL and from WBTC, the closing round trip, and the 2-hop pool sell after graduation into
  wSOL and into WBTC, at buyback indexes 0-7 (a sell now creates the float's account too, idempotently).
- **Paper, honest about fills and fees (2026-10-28):** a paper sell fills at the end of `paper_land_slots` after the
  trade that fired the exit, like a paper buy (it closed on the firing trade's own state, which a real sell never
  gets; the journal line is `long paper-sell`); the curve fee is the one in its trade event (protocol plus creator
  basis points), and the buy's quote is not charged the fee twice (the event reports it before fees).
- **Two switches for the next paper test (2026-10-28):** `follow_its_sell = false` keeps our own exits when it sells
  early and records what selling behind it would have made (`its_sell_px`, `its_sell_net` on the record; journal
  `long its-sell #N ... not followed (would make X SOL)`): it sells early on half of its 1.45+ SOL buys since Oct 27,
  against 3.5% on Oct 19-22, and on Oct 27-28 holding to our exits scored +3.10 against -0.51 behind it, on Oct
  19-27 about even (`analysis/research/2026-10-28/more/`). `float_stake_sol` stakes more on WBTC-routed copies
  (about +0.12 SOL a copy against +0.02 from wSOL).
- **`send TO SOL`** (Nov 13): a plain SOL transfer from the long wallet (to fund another bot's wallet, such as
  `rugsnipe-long-tab`'s), refused if it would leave under 0.1 SOL; waits for it to land.
- **`float_min_frac`** (Nov 14, default 1.0 = as before): a float that holds less than the stake (a losing trade is paid
  back in it) still buys, with all it holds and the stake scaled down with it, when that is at least this share of
  the stake; under it the buy is skipped (`float ... under the stake`). For several small floats (PUMP, SPCX), which
  would otherwise stop copying after one loss until topped up. `status --chain` shows each float's SOL value.
  `examples/scan.rs` takes `FLOATS=MINT,...` and prints each route's hops and kind.
- **`float_only`** (Nov 18, default false): wrapped SOL is not an anchor, so no route starts from SOL and a coin whose
  quote is reached only through a pool from SOL is skipped. For `rugsnipe-long-tab`: TAB16RxX's wSOL-paid copies lost
  9.4% a copy on Oct 31 - Nov 14 (467), its float-paid ones made +5.6% over 18 days (370;
  `analysis/research/2026-11-17/wallet_hunt/market/README_direct.md`).
- **Two units on one wallet, `other_state_dirs`** (Nov 18): `rugsnipe-long-tab` (TAB16RxX) trades from the main long
  wallet. Each config lists the other's state dir; a coin the other unit holds (live, or seen in the last hour) is
  skipped (`coin held by the other unit on this wallet`), and a sale never closes the coin's token account while the
  other unit still holds it (`pos::close_on_sale`): the close would fail on the other's tokens and cost the sale a try.
  Their overlapping copies made nothing (`analysis/research/2026-11-16/tab/`: +0.24 SOL on 35 coins).
- **`copy_sol_coins`** (Nov 22, default false; on for the CqCAzte8 unit): the copied wallet's buys of SOL-priced
  coins are copied too (`detect::Seen::SolBuy` carries a trigger with wrapped SOL as quote and input, `sol_coin` set;
  its SOL value is the curve's SOL plus the curve's fee). The position is a `sol_curve` one (`how = "sol curve"`), bought
  and sold with native SOL on the curve (`txb::sol_buy_ixs` / `sol_sell_ixs`, the ladder flip's code), with the same
  guards and exits as a copy. Off, a SOL-coin buy is still skipped silently, as wallet 4's unit always has. Engine test
  `a_sol_coin_buy_is_copied_only_with_copy_sol_coins` (CqCAzte8's real buy of 48tDqrzN); `simulate-sol` on three live
  SOL curves Nov 22: buy and round trip simulate, -2.74% of a 0.5 SOL stake.
- **`sol_exits`** (Nov 22, default false; on for the CqCAzte8 unit): the SOL-coin copies (`sol_curve`) take their own
  exits, `sol_take_profit`, `sol_max_hold_s`, `sol_sell_pressure`, `sol_stall_s`; the stop and its sale stay the
  unit's. CqCAzte8's blind blocks: its SOL coins made the most with tp 2x / 120 s (+11.06 SOL on 124 at 1 SOL, positive
  in all three), its token coins with tp 3x / 420 s / stall 240 (+19.53 on 77). Engine test
  `sol_coin_copies_take_their_own_exits_with_sol_exits`.
- **`float level MINT SOL`** (Nov 14): brings a float to a SOL value through Jupiter, buying what is missing or selling
  the excess (nothing within 5% of the target or 0.02 SOL); the daily rebalance with three floats (wins and losses
  stay in the float the trade was paid from).
- **`min_fee_bps`** (Nov 15, default 0 = off): its buy is skipped when the coin's fee tier (protocol + creator fee in its
  own buy event, basis points) is under it (`fee tier N bps under min_fee_bps`); a fee of 0 (not in the event) is
  never skipped. The `long buy` and `long paper-buy` lines now end with `fee N bps`. Two studies apart found the
  same rule (under 125 bps: 98 of 781 copies, 4 take profits, the bot's run +41 SOL against +36 over Oct 21 - Nov 14,
  our 9 real trades of that kind all lost); the 10 such copies after the data made +3.9 SOL in the model, so it stays
  off until more are seen (`analysis/research/2026-11-15/skip_filters/`).
- **Two exit signals: `sell_pressure` and `stall_s`** (Nov 15, both off by default). `sell_pressure = [n, w, from]`:
  out (`sell_pressure`) when the other traders' sells on the coin outnumber their buys by `n` or more over the `w`
  seconds up to their latest trade, from `from` seconds after its buy (wallet 4's own trades and ours are not counted;
  the feed already carries every transaction of a held coin). `stall_s`: out (`stall`) when the price has made no new
  high for that many seconds, once it has been back at our fill price (the high and its time are tracked from our
  fill; `entry_px`, `hi`, `hi_ms` in the book). Both come after take profit, stop and the timer. Oct 21 - Nov 15,
  1,238 buys at 0.5 SOL: `[5, 60, 30]` +6.5 SOL, `180` +6.5, together with `take_profit = 4.0` +75.3 against +56.6,
  3 losing days of 24 against 6, worst day −1.23 against −2.41; picked on two blocks, ahead on the third each time
  (`analysis/research/2026-11-16/signals/`). Trailing stops and "a top holder sells" were tested too and do not help.
- **The floats levelled by themselves** (Nov 15): `deploy/bin/rugsnipe-float-level`, started every 5 minutes by
  `rugsnipe-float-level.timer` (10 until Nov 17: a run that fell while a copy was open left the float short 10 more minutes), runs `float level MINT SOL` for each line of `/etc/rugsnipe/float-levels` ("MINT SOL"),
  only while the book has no copy open (a float with a copy out looks short), and stops if one opens meanwhile. A float
  is topped up only if the wallet keeps `SOL_FLOOR` SOL after it (default 0.6, Nov 16); the excess is always sold. One
  journal line a float (`journalctl -u rugsnipe-float-level`). Before it a float that lost twice bought smaller copies
  (or none under `float_min_frac`) until the owner's daily level, and one that won sat above its size.
- **Holder fees paid into a float** (Nov 14): pump distributes fees to a coin's holders in the coin's quote token
  (`DistributeFeeToHolders`, sent by `HckQ93Xq...`; the coins "airdropped" on Nov 12-13 were these). For a coin priced
  in a float they land in the float itself, and the trade's journal does not see them. `float book SIG` now adds the
  floats that came in that transaction, at the price API's rate, to the SOL change it books.
- **`send-token MINT TO AMOUNT|all`** (Nov 16): a token from the long wallet to TO (AMOUNT in whole tokens), TO's token
  account created if missing (about 0.002 SOL). First use: 1 USDT to a payee, bought with `float buy`. Checked by
  simulation from a USDT holder before it was used.
- **`send TO all`** (Nov 14): empties the wallet, for a bot paused for good (TAB16RxX's): closes its empty token
  accounts and any wrapped SOL (10 a transaction; their rent comes back; a close that fails is reported and skipped),
  lists accounts still holding tokens (sell them first with `float sell MINT all`), then sends every lamport but the
  5,000-lamport fee. Run it with the bot's unit stopped.
- **3-hop routes** (Nov 13, `route.rs` `MAX_OUR_HOPS = 3`): a transaction too long for legacy (a 3-hop buy or sell,
  about 1,270 bytes) is sent as v0 with pump's mainnet lookup table (`txb::sign`, `rugsnipe_tx::msg::compile_signed_v0`;
  the table is read from the chain at start: `long lookup table Hyif6eWb: 184 addresses`). Tests: the v0 round trip
  (`msg.rs`), a 3-hop buy and sell against the real table (`txb.rs`, `tests/fixtures/pump_alt.bin`), the 3-hop route
  plan (`route.rs`). Simulated on mainnet Nov 13 from our wallet: wallet 4's 3-hop buys from wSOL (FLu13NTF, 1,221
  bytes) and from WBTC (7tXqe2dn, 7tqLdWRf, 1,182 bytes): buy and round trip `err null`. Why: Oct 29 - Nov 12 its 31
  3-hop buys made +41.44 SOL on 55.6 (+74.5%; `analysis/research/2026-10-31/since_stop/skipped_groups.py`).
- **An early sale is followed even when its sales are not** (Nov 12, `follow_early_s = [from, to]`,
  `follow_early_below`): with `follow_its_sell = false`, a sale of it `from`-`to` seconds after its buy (timed from
  when we saw its buy) while the price is under `follow_early_below` takes us out behind it. Backtest Oct 29 - Nov 12
  (`analysis/research/2026-10-31/since_stop/follow_when.py`, 198 windows picked on week 1): [30, 180] and 1.5 beat
  never following in both weeks; on the copies it changes, +1.47 and +2.67 SOL raw, +0.82 and +1.49 after the live
  calibration, 24 of 32 better. Test `an_early_sale_under_the_price_is_followed_when_its_sales_are_not`.
- **`status --chain` puts each trade next to the copied wallet's own** (Nov 12): its result on the coin (`its pct`,
  from its transactions on its own token account of the coin, read from its buy: wallet 4 does not use the
  associated token account, WBTC at the price API's rate; `?` when a token had no price)
  and when it sold (`it sold`, seconds from its buy, or `holding`); also each result and the totals in dollars at the
  current SOL price. Finished coins are cached in `<state_dir>/its.json`. `examples/its_trip.rs` runs the same
  calculation on saved transactions (5tePJcGm: +113.3%, sold after 224 s, as the chain gives).
- **Airdropped coins sold count in `status`** (Nov 12): `float sell` of a mint that is not a float books our SOL change
  in `<state_dir>/extra.jsonl` (`float book SIG` books a sale already made); `status` prints the airdrop sales today and
  in all, and trades plus airdrops. Two coins sent to the wallet on Nov 12 sold for +0.26 SOL.
- **`follow_its_sell = false` holds through every sale of it** (Nov 12): before, a second sale event of the same coin
  (or the same one delivered twice) fell through to the following branch and sold us behind it; wallet 4 sold in one
  piece on all 222 trips of Oct 28 - Nov 12, and no live trade took that path. The record keeps its first sale.
- **`join_others`: a unit may buy a coin another unit on the wallet holds** (Nov 25, off by default). The skip
  ("coin held by the other unit") throws away the trades where two of our wallets agree: over Nov 8-24 a copy of a coin
  another of our wallets had bought in the hour before made +16.7% a copy (189) against +10.8% alone (803), higher on 5
  of 6 wallets (`analysis/research/2026-11-25/consensus/`). With it both units hold the coin; each sells its own tokens,
  and the shared account stays open while either holds it (`pos::close_on_sale`, as before). The journal says
  `long join ...`. Test `join_others_buys_a_coin_the_other_unit_holds_and_keeps_the_account_open`.
- **The units on one wallet share one price fetch** (Nov 24, `oracle.rs`): seven units each asking Jupiter's price API
  every 20 s from the box drew HTTP 429 on most requests (since 10:20 Beirut on Nov 24: 543 refusals on wallet 4's unit,
  43-510 on the others), so a buy paid with a float found no price under 2 minutes old and was skipped as "its buy has
  no SOL value" (8 of wallet 4's buys, 5 of 6LwMLkCe's, 3 of 6nNzEg86's in about 3 hours). Each unit now writes its
  answer to `<state_dir>/prices.json`, and a unit that finds another's (from `other_state_dirs`) under 20 s old, asked
  for every float it needs, uses it instead of asking: about 3 requests a minute in all. Each unit asks at a phase of
  its own, a price is used up to 10 minutes old (was 2), and refusals are logged once a minute with a count. Test
  `a_fresh_answer_of_another_unit_is_used_and_a_stale_or_narrow_one_is_not`.
- **`stop = 0` means no stop** (Nov 4): the trip ends at the take profit or the hold. Since Oct 30 wallet 4 has dropped
  its 30-minute timer and sells two thirds of its big buys early, and the 0.8 stop sold into its sale; over Oct 29 - Nov 4
  at 1 SOL × 3 the copy makes +1.79 with the stop and +6.26 without, better at every landing and in both halves, and
  neutral on Oct 19-28 (`analysis/research/2026-10-31/since_stop`). The worst single trip grows from −0.5 to −0.8.
- **Accounting is chain-true:** a position's result is the sum of our wallet's lamport changes over its transactions,
  plus a float's token change at the oracle price. Paper (`mode = "log"`) prices the same decisions on the live curve.
- **Measured on mainnet** (simulation from our wallet, a 2-hop wSOL route): buy 1,088 bytes, 166k compute units; buy
  and sell back in one transaction 1,158 bytes; the round trip costs about 3% at 1 SOL (the backtest charged 5.1%).

## 4. Runbook (fra1)

```
cd ~/rugsnipe && git pull && sudo bash deploy/install.sh --role hot
sudo /opt/rugsnipe/bin/rugsnipe-long keygen --out /etc/rugsnipe/keys/long-wallet.json   # prints the new address
```

1. **Paper first.** `/etc/rugsnipe/long.toml` is created with `mode = "log"`. Set `rpc_url = "cred:RPC_URL"` to a line of
   the api-keys file that holds your RPC URL, then `sudo systemctl enable --now rugsnipe-long`. The journal shows each
   of its buys, our paper buy and close; `bash ~/check.sh` shows the book at the end.
2. **Fund the wallet** (the address keygen printed): `max_open` x `stake_sol` + about 0.1 SOL for fees, split between
   SOL (routes from wrapped SOL) and the WBTC float: `sudo /opt/rugsnipe/bin/rugsnipe-long float buy
   3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh 3.0 --config /etc/rugsnipe/long.toml` (through Jupiter).
3. **Before real:** simulate the paths that never ran, from the box, with a recent buy of wallet 4
   (`SIG`) and a graduated coin someone holds (`MINT`, its `QUOTE`, a `HOLDER` with SOL): nothing is sent.
   ```
   sudo /opt/rugsnipe/bin/rugsnipe-long simulate --rpc "$RPC_URL" --tx SIG --user H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg --sol 0.1 --float 3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh --buyback 3 --close
   sudo /opt/rugsnipe/bin/rugsnipe-long simulate-sell --rpc "$RPC_URL" --mint MINT --quote QUOTE --user HOLDER --float 3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh --graduated --close
   ```
   Both print `err null`. (Oct 28: both passed on mainnet for wSOL and WBTC routes.)
4. **Real:** `mode = "on"` in long.toml, `sudo systemctl restart rugsnipe-long`.
- **Stop new buys:** `sudo touch /var/lib/rugsnipe-long/KILL` (exits continue); remove it to resume.
- **The book:** `sudo /opt/rugsnipe/bin/rugsnipe-long status --config /etc/rugsnipe/long.toml --chain`.
- **Floats back to SOL:** `... float sell 3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh all --config ...`.
