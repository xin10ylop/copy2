# Strategy D: the launch copy (the copy bot's copies of wallet 4's SOL-coin launch buys)

In short: the copy bot (rugsnipe-hot, on fra1) bought right behind wallet 4's **launch buys of SOL-priced pump coins**
and sold at **create + 12 slots** (about 5 seconds), with a **20%** price bound. It ran on **real money** from Oct 26
17:36 UTC until the bot's daily-loss kill on Oct 27 07:50 UTC (09:50 Beirut). Over check.sh's window it sent 93 copies,
filled 77, had 14 refused. **Our copies netted +0.1456 SOL** while wallet 4 made +2.77 on the same 96 coins. It was the
only copied wallet making money. But that number leaves out **2RR6sfbi**, a D copy that couldn't be sold (−0.57 SOL). With
it, D lost about **−0.43 SOL**. Nothing tested makes this slice reliably profitable. The copy bot is stopped, and fra1 is
gone.

| | |
|---|---|
| Status | **stopped.** Live Oct 26 17:36 UTC → Oct 27 07:50 UTC; hot bot stopped and disabled Oct 27; fra1 terminated Oct 28 |
| Part of the decomposition | a slice of part D (SOL-priced coins, +29 SOL for wallet 4 over 8 days; [02-decomposition](../02-decomposition/README.md)) |
| Code | the hot copy bot: `crates/rugsnipe/` (`entry.copy_more`, the hot loop, exits), `crates/rugsnipe-tx/` (transactions, senders) |
| Config (live, from the check.sh paste) | `copy_more = [..., { wallet = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg", max_premium = 0.2, hold_to_create_slots = 12 }, ...]` in `/etc/rugsnipe/rugsnipe.toml` |
| Source docs | [`docs/19-copy-targets-and-dip-buys.md`](../docs/19-copy-targets-and-dip-buys.md) §5 (copy_more), §11 (found), §12 (check.sh), §13 (wallet 4 live, the exit and bound) |
| Research | [`analysis/research/2026-10-26/h9/`](../analysis/research/2026-10-26/h9/README.md) (`coins.py`, `land.py`, `replay.py`, `calib.py`, `why.py`) |
| Live outputs | [`05-live/check-sh-2026-10-27.txt`](../05-live/check-sh-2026-10-27.txt) (section `== 4 H9kuqGKN`), [`05-live/copy-bot-history-2026-10-28.txt`](../05-live/copy-bot-history-2026-10-28.txt) |

## 1. The rule

- **Trigger:** wallet 4's landed buy in a coin's create slot or the next one (a *launch buy*), of a coin the bot's class
  covers: `create_v2`, not mayhem, not cashback, **priced in SOL**. Its later buys aren't copied: they lose for wallet 4
  itself (37 coins, −11.65 SOL). Coins priced in other tokens are invisible to this bot (check.sh "not seen").
- **Any size.** Unlike wallet 2 (3yrJE1A8, `min_sol = 1.5`), wallet 4 has no `min_sol`.
- **Our buy:** the copy bot's stake (0.51 SOL on 2RR6sfbi; each copy's size follows from check.sh's OUR NET and our %
  columns), sent through its senders with a tip bid of 3.0M or
  8.0M lamports (the tip test, §4). Refused on chain if the price is more than **20%** over its price
  (`copy_more[].max_premium = 0.2`, its own bound; him and 3yrJE1A8 keep the global 5%).
- **Exit:** sell at **create + 12 slots** (`hold_to_create_slots = 12`), about 5 seconds after the launch. Wallet 4
  itself holds up to 30 minutes.
- Shared with every copied wallet: one wallet (`4g49xGbg...`), the daily stop (`max_daily_loss_lamports`, 1 SOL, marked
  to market), the kill latch, the guard process.

## 2. How it was found and tuned

1. **Oct 26 evening, the second search** (docs/19 §11): wallet 4 passed at create + 9: 79 launch buys, first half +1.89,
   second half +0.48 (+0.017 a copy), positive at every hold from +3 to +12 in both halves; our sale first on 76 of 79.
   It went live at 17:36 UTC at create + 9 with the global 5% bound.
2. **Oct 26 night** (docs/19 §13, `h9/`): at 22:45 UTC check.sh showed wallet 4 at +24.56 itself and our copies at
   −0.25. Most of its result was never ours to copy:

   | part | its own net |
   |---|---|
   | coins before the bot watched it (45; pumpCmXq, the PUMP token itself, alone +8.48) | +19.30 |
   | coins outside the bot's class (25: priced in other tokens, or not pump.fun launches) | +2.36 |
   | skipped (6; mostly Jmy7SAPy +2.10, which a refused copy of wallet 3 had already claimed) | +2.43 |
   | the 47 coins we copied | +0.56 (of which +2.10 on the 11 the 5% bound refused; −1.59 on the 36 we filled, against our −0.25) |

3. **The replay** on 160-slot tapes of its 154 in-class launch buys, with our real landings (21 of our first 35 live
   fills landed a slot after its buy, because it buys late in the block), corrected by the 0.0155 SOL a fill that the
   model reads high against our real fills (`calib.py`):

   | setting | P1: Oct 25 18:00 – Oct 26 06:00 UTC, 67 coins | P2: 06:00 – 17:44, 38 | P3: live, 49 |
   |---|---|---|---|
   | create + 9, 5% (as it ran) | +0.21 | −0.18 | −0.13 |
   | create + 12, 5% | +0.48 | −0.24 | +0.69 |
   | create + 12, 15% | +0.55 | +0.22 | +1.37 |
   | **create + 12, 20% (chosen)** | **+0.62** | **+0.22** | **+1.48** |
   | create + 12, 30% / 50% | +0.25 / +0.22 | +0.22 / +0.26 | +1.47 / +1.47 |
   | create + 15, 20% | +1.19 | −0.45 | +2.18 |

   - Create + 12 at 20% was picked on P1 + P2 and is positive in all three periods. A looser bound adds nothing past 20%.
     Create + 15 loses in P2.
   - Selling one slot after its first sell (capped at create + 40) doesn't beat create + 12 on P1 + P2. Not built.
   - **The profit rests on a few coins.** Without each period's 2 best coins, every setting is slightly negative.
4. **Built** (`807939b`, Oct 26 23:43 UTC): `copy_more[].max_premium`, a wallet's own price bound. Wallet 4 set to
   `hold_to_create_slots = 12, max_premium = 0.2`. In check.sh's table the slots held go from 6-10 to 11-14 from about
   01:50 Beirut (23:50 UTC), when the new setting took effect.

## 3. Holding it longer: tested, doesn't help

- Create + 15 loses in one of the three periods (above).
- Holding its big SOL-coin buys up to 30 minutes with the long copy's exits (TP 2.0 / SL 0.8 / 1790 s): −11.12 on
  Oct 19-22 (73 copies), −2.34 on Oct 23-27 (31) (`h9long/exits_pess.py`).
- Wallet 4's own edge on SOL coins is only about +0.02 SOL a coin over 8 days (+29 on 1,439 coins), less than a copy's
  costs. SOL launches are crowded with faster bots, and a copy buys at a worse price than wallet 4 and pays more fees.

## 4. Live (check.sh window: Oct 26 15:00 → Oct 27 11:45 Beirut)

From the `BY WALLET` table:

| | |
|---|---|
| wallet 4's own net, all 212 of its coins | **+36.9199** |
| our net on its copies | **+0.1456** (2RR6sfbi not included: still open) |
| sent / filled / refused / won | 93 / 77 / 14 / 32 of 76 closed |
| its net on the coins we copied | +2.7742 (96 coins) |
| on coins the bot skipped | +0.3268 (5) |
| on coins the bot didn't see | +10.5774 (66) |
| before the bot watched it | +23.3643 (45) |
| its failed transactions | −0.1229 (43) |

The **tip test** (`TIP TEST` table, since Oct 26 18:20 Beirut, by our bid):

| our bid | copies | filled | failed | in its slot | net SOL | per copy |
|---|---|---|---|---|---|---|
| 3.0M | 37 | 27 | 10 | 21 | −0.1416 | −0.0038 |
| 8.0M | 56 | 49 | 7 | 31 | +0.2874 | +0.0051 |

**Why it made +0.15 while it made +2.77**, on the 76 closed copies:

| | wallet 4 (holds up to 30 min) | us (sold after about 5 s) |
|---|---|---|
| its 5 best coins (5qW5yNnZ +3.79, E2757ksn +2.66, GrLZAMXj +1.14 ...) | **+9.47** | −0.12 |
| the other 71 | **−7.66** | +0.26 |

Selling after 5 seconds avoids its big losers but misses the few coins that run for minutes and carry all of its profit.
Another +2.09 of its profit was on the 14 coins the 20% bound refused.

**2RR6sfbi**, bought Oct 27 06:55:32 Beirut as a copy of its 0.160 SOL launch buy, graduated at our buy. 405 curve sells
failed, and it was sold by hand for 0.029 SOL: about **−0.57 SOL** with the failed-sell fees
([`05-live/stuck-coin-2RR6sfbi.md`](../05-live/stuck-coin-2RR6sfbi.md)). It also pushed the day's marked-to-market loss
past the 1 SOL stop. That **stopped the whole copy bot at 09:50:35 Beirut**, every copied wallet included.

**The bot as a whole** (`copy-bot-history-2026-10-28.txt`): since the start (Oct 26 15:00 Beirut) 417 trades, net
**−0.7628** (wallets 3 and 5 lost about −0.93, and the copies paid 2.91 SOL of tips and fees against +2.15 on the price
moves). All time (Oct 22-27): 989 trades, **−5.1292**, mostly its own launch-buying rule on Oct 22-25, before it
switched to copies only. The wallet went from 1.7192 to 0.3081 SOL: −1.41, of which 2RR6sfbi −0.51 and its failed sells
−0.09.

## 5. Verdict

- **Stopped, not to be restarted as is.** D's live result (+0.15, or about −0.43 with 2RR6sfbi) sits on a few coins.
  Every tested setting is slightly negative without each period's 2 best coins.
- If it is ever run again: it needs a box close to the leaders (the launch race is speed-bound; fra1 was Frankfurt bare
  metal), the graduation fix `af681ad` deployed (`sudo bash deploy/install.sh --role hot`), and a check.sh that counts
  open positions and failed-sell fees.
- Wallet 4's money is in part A. That's [strategy A](../03-strategy-A-long-copy/README.md).

## Sources

- `docs/19-copy-targets-and-dip-buys.md` §5, §11-§13; `analysis/research/2026-10-26/h9/README.md`.
- `05-live/check-sh-2026-10-27.txt` (`BY WALLET`, `TIP TEST`, `== 4 H9kuqGKN`, `open now`, the kill line);
  `05-live/copy-bot-history-2026-10-28.txt`; `05-live/stuck-coin-2RR6sfbi.md`.
- `analysis/research/2026-10-27/h9long/README.md` (the 30-minute test on SOL coins).
- Session analyses of Oct 27-28 (the 5-best split, why the copy bot wasn't positive).
