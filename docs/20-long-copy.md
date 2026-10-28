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
