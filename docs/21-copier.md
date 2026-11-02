# 21. The copier: several wallets, any venue, through Jupiter

`rugsnipe-long copy` (code: `crates/rugsnipe-long/src/copier.rs`, `jup.rs`; config: `config/copier.example.toml`; unit:
`deploy/systemd/rugsnipe-copier.service`). Built Nov 1-2, 2026. **Paper-tested only: nothing has been sent from it.**

## 1. Why it exists

The long copy (`rugsnipe-long run`, docs/20) builds pump's own `multi_hop_swap`. That is fast, but it reaches only the
pump curve and canonical PumpSwap pools. Two kinds of trades are out of its reach:

| What | Why the long copy can't trade it | The copier |
|---|---|---|
| Wallet 4's **part B**: its 1.45+ SOL buys of pump coins priced in PUMP, CARDS, TTWO, USDC, ZEC, xStocks ... (372 buys, +116 SOL to it; `02-decomposition/README.md`) | `multi_hop_swap` takes canonical pump pools only (`OnlyPumpPools`, error 6078, simulated on mainnet), and none of these quote tokens has one against wSOL or WBTC | Jupiter routes SOL → the quote token → the coin (a replay routed wallet 4's buy as Whirlpool > GoonFi V2 > Pump.fun) |
| Wallets that trade on Meteora DBC and DAMM v2, Raydium LaunchLab and CPMM | no code for those venues | Jupiter quotes all of them (checked Nov 1 with real quotes) |

Wallet 4's **part A** stays in the long copy: it is faster there, and the copier skips those coins itself
(`coins = "pump_unroutable"`, §2).

## 2. How it works

| Step | What it does |
|---|---|
| Feed | The hot config's gRPC feed, filtered to every `[[target]]` wallet. No new buys while the feed is down. |
| Detect | From the copied wallet's own balance changes, so no venue decoder is needed. On pump coins its pump trade events decide. Elsewhere, one coin up while SOL (or a stable) goes down is a buy, and a coin down is a sale. |
| Value its buy | Its whole SOL change (fees and tip included) plus any token it paid with, at that token's Jupiter price. This is how the backtests valued it. |
| Filter | `min_sol` ≤ its buy ≤ `max_sol`. `coins = "pump_unroutable"` keeps only pump curves priced in a token pump's own route cannot reach (WBTC, or a quote with a canonical pool against wSOL or WBTC, counts as reachable; an RPC error counts as reachable). `quotes_deny` drops chosen quote tokens. |
| Stake | `stake_sol`, or `stake_frac` × its buy, capped at `stake_cap_sol`. |
| Premium cap | `max_premium`: no buy when Jupiter's quote prices the coin more than this over its buy price. |
| Exits, first one wins | `max_hold_s` after our buy; right behind its own first sale of the coin (`follow_sell`); a take profit or a stop. |
| TP and stop | Our tokens are valued with a Jupiter sell quote every `poll_ms`. The levels are multiples of its buy price (`exit_basis = "its"`, the long copy's way) or of what we paid (`"ours"`). |
| Paper (`mode = "log"`) | Fills at a live Jupiter quote and charges `paper_side_cost_lamports` a side. |
| Live (`mode = "on"`) | Asks Jupiter for the swap with a Jito tip inside, signs it and sends the same transaction to our RPC and to Jito. It waits until the swap lands or its blockhash expires, then books the chain's own SOL and token changes. |
| Sell retries | A sale that fails is retried, with gaps of 2 s × tries up to 30 s, until it lands. A sale first checks the tokens we actually hold. |
| Book | Every event is a JSON line in `journal`. Open positions and today's closed ones are in `state`, so a restart picks them up. |
| Guards | `daily_stop_sol` (today's realized UTC result); `max_open` per wallet and for all wallets together; no second position in a coin we hold; `min_wallet_sol` kept back; the `kill_file`. Exits always continue. |

**One sender.** The swap goes to our RPC and to Jito only, and it is one signed transaction, so it can land only once.
The tip Jupiter adds goes to a Jito tip account, so no other sender would accept it; the config refuses any other
sender. `senders = []` with `jito_tip_lamports = 0` sends through our RPC alone, with a priority fee capped at
`priority_max_lamports`.

**Jupiter's free API** refuses bursts (HTTP 429). Calls are spaced `jupiter_gap_ms` apart. After a 429 the copier
cools down for 10 s. Value polls give way during the cool-down; buys and sells retry up to 3 times.

## 3. Its config

`config/copier.example.toml` is commented line by line. It has the first-test stakes, a tenth of the backtests':

| Target | Rule | Stake |
|---|---|---|
| `w4b`: wallet 4's part B | its 1.45+ SOL buys of `pump_unroutable` coins; take profit 2.0x, stop 0.8x of its price, 1790 s, behind its sale; no buy 30% over its price | 0.1 SOL, 3 open |
| Others | one `[[target]]` each, from that wallet's own study. A template is at the end of the file. A wallet whose study is private keeps its block in its private repo; it is added on the box. | |

- `max_premium = 0.3` on `w4b` matches the long copy's limit.
  - The long copy refuses a fill 25% over the price wallet 4's buy left (`long.toml`, `max_premium`).
  - Its average price sits below that price by its own impact: 2-5% for a 1.5 SOL buy on a curve of 30-80 virtual SOL.
  - So the long copy's limit is 1.25 × 1.02-1.05 = 1.28-1.31 times its average price, about 0.3.
- The whole book is capped by `max_open = 6` and `daily_stop_sol = 0.5`.

## 4. Commands

```
rugsnipe-long copy --config /etc/rugsnipe/copier.toml          # the service runs this
rugsnipe-long copy-status --config /etc/rugsnipe/copier.toml --tz +0200 --last 15
rugsnipe-long copy-replay --config FILE --rpc URL|@FILE --tick-s 30 SIG...   # paper: replay its transactions now
```

`copy-status` prints each wallet's buys, failed buys, closed trades, wins, net SOL and today's result. Then it lists the
open positions and the last closed trades, in the given time zone. A paper replay of the final code ran on Nov 2,
01:40 UTC, with the box's config: the example file plus one private target. Its prices were those of Nov 2, not the
trades' own days.

What the replay showed:

- A 5.046 SOL DBC buy was skipped under a 5.1 floor.
- A 10.1 SOL pump buy was copied at 0.3 SOL.
- Wallet 4's part-B buy was routed through 3 hops and copied at 0.1 SOL.
- That position's stop fired at once, which is correct: the coin had fallen far under wallet 4's price since its buy.

## 5. On a box

The box runs the hot role's install (docs/07). Every line below runs on the box; the owner runs them.

```
cd ~/rugsnipe
sudo bash deploy/install.sh --role hot --dry-run      # lists rugsnipe-copier.service and /etc/rugsnipe/copier.toml
sudo bash deploy/install.sh --role hot                # "config: created /etc/rugsnipe/copier.toml ... (mode = log: paper)"
sudo /opt/rugsnipe/bin/rugsnipe-long keygen --out /etc/rugsnipe/keys/copier-wallet.json   # prints the address only
sudo grep -n "^jito" /etc/rugsnipe/rugsnipe.toml      # must say enabled = true (the copier refuses to start otherwise)
sudo systemctl enable --now rugsnipe-copier
journalctl -u rugsnipe-copier -n 20 --no-pager        # "copier start: mode Log ..." then copier feed {"up":true}
```

**Before any SOL goes in, copy the wallet file off the box.** A box can vanish with its only key (Oct 29). The file is
root-only:

1. On the box: `sudo install -m 0600 -o "$USER" /etc/rugsnipe/keys/copier-wallet.json ~/copier-wallet.json`.
2. From your own machine: `scp` that file down.
3. On the box: `rm ~/copier-wallet.json`.

Never print the file.

The long copy and the copier each open their own gRPC stream on the same feed. Check that the feed plan allows two
streams.

Other wallets' private `[[target]]` blocks are appended to `/etc/rugsnipe/copier.toml` by hand, and the service is then
restarted. To go live, set `mode = "on"` once the paper journal looks right, then
`sudo systemctl restart rugsnipe-copier`. To stop new buys: `sudo touch /var/lib/rugsnipe-copier/KILL`.

## 6. What it is worth, and what is not known

**Wallet 4's part B has not been backtested through the copier's route.** The evidence so far (`02-decomposition/`,
`analysis/research/2026-10-28/more/` §A) priced it as if we held each quote token at no risk:

| Period | Result |
|---|---|
| Oct 19-22 | +24.63 on 189 copies |
| Oct 23-27 | +0.43 on 94 (PUMP −1.32) |
| Oct 27-28 | +4.85 on 17 (+2.65 without the best 2) |

The same buys counted by route (305 that need Jupiter: direct buys of other quotes, PUMP floats, 3+ hops) made
+28.57 on Oct 19-22 and +3.06 (+0.41 without the best 2) on Oct 23-27 (h9long README).

**It fell apart after Oct 22.** The copier also pays one more hop each way than "held at no risk": SOL to the quote
token, about 0.3% a hop. A separate study (Nov 2) is scoring part B through Jupiter's actual routes. Until it reports,
treat `w4b` as a mechanics test at 0.1 SOL, not as an edge.

**Speed.** The copier asks Jupiter for a quote and a swap over HTTP before it sends, which the long copy does not.
Expect it to land later than the long copy's 47% in its slot and 53% the next (copy2, 15 sends). A wallet's study must
hold up a few trades later than K = 2 before it goes here.

## 7. Known limits

- **It is one thread.** While a swap is waiting to land (usually 1-2 s, at most until its blockhash expires, about
  60-90 s), feed events queue. A sale of the copied wallet seen in that time is acted on late.
- **A crash between the send and the book** leaves the position unbooked. The journal shows the buy without a
  position. Check the wallet for that coin and sell it by hand.
- **Paper is pessimistic on thin pools.** A paper sale is quoted without our own buy's tokens in the pool.
- **A part-B coin that graduates** is sold wherever Jupiter routes it. This is not checked live.
- **The TP/stop value is a sell quote** (after impact and fees), not the curve's spot price. That is a little stricter
  than the long copy on a take profit and a little looser on a stop.

## 8. Tests

`cargo test -p rugsnipe-long` (42 library tests, 20 of them the copier's; 16 engine tests). The detection tests run
on real transactions. One is wallet 4's part-B buy and its sale back into PUMP. The other four are a SOL-coin wallet's
buys and sale on DBC, LaunchLab and the pump curve; they are made anonymous (`tests/fixtures/w2_*.json`: the wallet,
its accounts, the coins and the signatures are stand-ins).

The engine tests cover:

- a tier under the floor skipped;
- the exit behind its sale;
- the timer;
- part B's filter and stop;
- the take profit, both bases;
- the premium cap;
- sale retries;
- `max_open`, a held coin and the daily stop;
- feed down;
- the kill file;
- a restart;
- config refusals;
- the example config.
