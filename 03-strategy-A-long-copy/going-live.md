# Strategy A: going live (the plan, not yet started)

**Superseded on Oct 28 evening by [`07-rework-2026-10-28/README.md`](../07-rework-2026-10-28/README.md) §6** (the hardened
code, a Frankfurt box, 2-3 days of paper that decide, then the 0.1 SOL test). The steps below still hold for the test
itself, with these corrections: fund **at least 0.16 SOL** (`reserve_sol` 0.05 + the 0.1 stake + fees + rent), run the two
mainnet simulations in docs/20 §4 first, and run the test on the Frankfurt box, not Ohio.

In short: the long copy has never sent a real transaction. The plan is three steps: **(1)** 2-3 days of paper on Ohio;
**(2)** a small real test, 0.1 SOL a trade, 1 position, about 5 trades, to check that real money moves correctly;
**(3)** 1 SOL a trade, 4 open, about 4.1 SOL in the wallet, only if both look right. Ohio can run it live, because the
strategy holds for minutes and a slot or two of extra latency costs about 5-10% of the profit. A cheap Frankfurt server
would land closer.

## 1. Can it run on Ohio? Yes

fra1 was expensive bare metal because the old copy bot raced other bots for the first spot at a launch. The long copy
buys behind wallet 4 and holds for up to 30 minutes. From the landing-delay backtest (backtests.md §8): 2 slots late
costs 3-6% of the profit, 3 slots about 9%, 5 slots about 20%. Ohio is expected to land about 2-3 slots behind wallet 4.
At 1 SOL stakes that's on the order of 0.1 SOL a day, if it performs like the backtest. After `7184554` is deployed,
the journal's `seen at its slot +N` measures Ohio's real lag.

**Alternative:** a small virtual server in Frankfurt (for example at Cherry Servers) would land about a slot behind
wallet 4, as fra1 did. One process with a live feed needs only about 2 cores and 4 GB. Check current prices and
locations before choosing.

## 2. Why the small test first, though it can't make money

At small stakes this strategy doesn't make money. The backtest charges about **0.0345 SOL of fixed costs a trade**
(0.0095 SOL a transaction for the buy and the sell, plus the 0.0155 SOL that real fills came out worse than the model).
That's about 3.5% of 1 SOL, enough of the edge survives at 1 SOL, it ate the whole edge at 0.5 SOL, and at 0.1 SOL it
would be about a third of the stake. So the 0.1 SOL run is a test, not a profit run. It checks what paper can't:
- Does our buy land, through the WBTC routes too?
- Does the sell go through, including the PumpSwap sell after a coin graduates? A position that can't be sold is a
  full loss of its stake (see `../05-live/stuck-coin-2RR6sfbi.md`: that cost 0.57 SOL on the copy bot).
- Does the bot's chain-true accounting match the wallet?
- What do our fees really cost, and where do our buys land at 0.0016 SOL? That tells whether the backtest's 0.0345 a
  trade is right, too harsh or too kind.

**Its cost:** about 0.003 SOL of fees a trade with the current settings, plus the price result on 0.1 SOL, usually a few
percent either way. If all 5 trades hit the 0.8x stop, about −0.12 SOL. Realistically a few hundredths of a SOL. With
1 position at a time, at most 0.1 SOL is ever in a trade.

## 3. Steps for the real test (on Ohio)

1. **A wallet for it:** `sudo /opt/rugsnipe/bin/rugsnipe-long keygen --out /etc/rugsnipe/keys/long-wallet.json` (prints
   the new address). Put the `long-wallet` credential back into the unit: install the repo's
   `deploy/systemd/rugsnipe-long.service` with only the api-keys path changed (Ohio's unit had the `long-wallet`
   lines deleted to force paper mode).
2. **The sender:** `long.toml`'s `buy_senders` / `sell_senders` (`nozomi`) come from the hot config's `[senders]`. Point
   them at Temporal's (Nozomi's) **US** endpoint instead of Frankfurt's in `/etc/rugsnipe/fra1-hot.toml`.
3. **Fund it:** a little over 0.1 SOL plus fees, then a small WBTC float for the WBTC routes:
   `sudo /opt/rugsnipe/bin/rugsnipe-long float buy 3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh <SOL> --config /etc/rugsnipe/long.toml`.
   WBTC-routed copies earned about +0.12 SOL a copy in the backtest, against +0.02 from SOL.
4. **Settings for the test:** `stake_sol = 0.1`, `max_open = 1`, `mode = "on"`; restart.
5. **Watch:** `rugsnipe-long status --config /etc/rugsnipe/long.toml --chain` (the book against the chain), the journal,
   and the wallet balance. Stop new buys any time with `sudo touch /var/lib/rugsnipe-long/KILL`.
6. **After about 5 trades:** compare each trade's chain result with the journal. Check where the buys landed (slots behind
   wallet 4). Check every sell went through. If buys land more than about 3 slots behind it, raise the buy fee.

## 4. Then 1 SOL

- `stake_sol = 1.0`, `max_open = 4`: about **4.1 SOL** in the wallet with fees (at 1.5 SOL a copy, about 6.1). With
  less money, keep `max_open = 3` (P1 +5.03 / P2 +9.63 instead of +6.73 / +11.13).
- `daily_stop_sol = 3.0` stays: no new buys once the UTC day's realized result is −3 SOL or worse.
- Move to a Frankfurt server if Ohio's measured landings cost more than the server would.
- Floats back to SOL when stopping: `rugsnipe-long float sell 3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh all --config ...`.

## 5. What would stop the plan

- Paper turning negative over 2-3 days, once its fills follow Ohio's real lag (`7184554`).
- Wallet 4's early sells staying near 40% (the rule was tested at 3-6%): re-test on fresh data first.
- Any real sell that fails to land, or a chain result that doesn't match the journal.

Money: the user's Phantom wallet held 3.8498 SOL on Oct 28, after both bot wallets were emptied into it.

## Sources

- Session answers of Oct 27-28 (Ohio vs a Frankfurt server, small stakes, fees, the test's cost); backtests.md §5, §6,
  §8, §11; `docs/20-long-copy.md` §4 (runbook: keygen, float buy, mode on).
