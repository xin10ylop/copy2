# Robinhood Chain (Pons): the deep redo of the wallet search (Nov 19)

The owner: "re do the whole process to check that any wallets have been missed, more deeply". The first pass is
`../../2026-11-18/robinhood/` (rh5_direct.py's screen, rh6_engineer.py's grid); the bot is `crates/rh-copier`, live since
Nov 18 22:10 UTC with three wallets (docs/23-rh-copier.md).

## What changed from the first pass

| | First pass (Nov 18) | This redo |
|---|---|---|
| Data | Oct 19 - Nov 18 18:51 UTC | **Oct 9 - Nov 19 00:31 UTC** (rh1_fetch.py, 40 days; it now also splits a range on "log query timed out") |
| Curve | fitted: V0 = 1.75 ETH, the buyer's gross quote added | **exact** (measured Nov 18, docs/23): q·t = 1.68e9, q gains quoteIn - fee - tax, a sale takes quoteOut + fee + tax. The rebuilt reserves equal the chain's on 12 curves (`val_path`, 38-181 trades each) |
| Coins that go quiet | **left out** when the coin's trading stopped within 600 s of the copied buy | **kept**: sold at the last state, as the live bot would. Only buys in the data's last 600 s are left out |
| Who is screened | the buy's recipient, 20+ copies of 0.05+ ETH | the recipient **and the calling contract** (`call:`), 10+ copies of **0.01+ ETH** |
| Test | picked on the newer half, scored on the older | three periods (P1 Oct 9-22, P2 Oct 22 - Nov 5, P3 Nov 5-19): the exit picked on P1+P2 (without the best 2%), scored on P3 |
| Chance | not measured | **a null**: pseudo-wallets of random market buys, the same count in each period, through the same test |
| Groups | wallet by wallet | identities sharing 30%+ of their coins are linked into one group, scored with each coin once |
| Landing | 2, 3, 5 blocks (rh6) | 2, 3, 5 blocks; the finalists also at 5, 8, 12 |

## Run order (DIR = rh1_fetch.py's folder, SD = a scratch folder)
```
python3 -I rhd3_live.py DIR > out/rhd3_live.txt                        # the 3 live wallets, old vs new method
python3 -I rhd1_screen.py DIR SD > out/rhd1_screen.txt                 # the screen and the null (~20 min, 4 cores)
python3 -I rhd4_groups.py DIR SD > out/rhd4_groups.txt                 # groups, callers, own launches
python3 -I rhd5_dump_groups.py SD > SD/groups.json
RH_GROUPS=SD/groups.json python3 -I rhd2_engineer.py DIR ID > out/rhd2_<id>.txt   # the full grid; ID rec:/call:/grp:
LANDB=5,8,12 ...                                                       # later landings; FIX="..." scores given settings
```
(`RH_GROUPS`, not `GROUPS`: bash ignores an assignment to GROUPS.)

## Results

**1. The first pass flattered wallets 1 and 2** (`out/rhd3_live.txt`, the live settings, landing 2/3/5 blocks):

| live wallet | old method | **every coin, exact curve** | coins that went quiet | P1 / P2 / P3 a copy | last 3 days | at 5/8/12 blocks |
|---|---|---|---|---|---|---|
| 1 `0x9a3955a1` | +20.8% (430) | **+14.3%** (515) | 85, −18.8% each | +8.9 / +13.3 / +20.1% | +21.1% | +10.1% |
| 2 `0x5bc235ac` | +11.1% (534) | **+7.8%** (652) | 118, −7.1% each | +6.5 / +14.4 / +6.5% | +14.6% | +5.9% |
| 3 `0xc54d3914` | +26.6% (335) | **+24.6%** (375) | 40, +8.1% each | +22.6 / +22.5 / +38.6% | +33.2% | +20.4% |

All three stay positive in every period. Re-engineered from scratch on the exact model (`out/rhd2_rec_*.txt`), none
needs a change: wallet 1's best setting makes the same total (+1.48 vs +1.47 ETH), wallet 2's (sell pressure off, +8.8%
against +7.8%) does not hold when picked on one half and scored on the other (rank 249,461 of 466,560), wallet 3's is
+24.8% against +24.6%.

**2. The screen** (`out/rhd1_screen.txt`): 43,643 ETH launches; 442,823 first buys of 0.01+ ETH; 7,305 identities
with 10+ (7,200 recipients, 105 callers); 2,336 with 8+ copies in P1+P2 and 4+ in P3. **449 passed; chance alone
passes about 174.** A random market buy loses under every exit (−2% to −16% a copy). Linked into groups
(`out/rhd4_groups.txt`, the 132 passers a random wallet of their size passes in 5% of draws or less: 34 groups).

**3. The finalists, engineered** (`out/rhd2_*.txt`, landing 2/3/5 blocks):

| identity | what it is | copies | a copy | last 7 days | verdict |
|---|---|---|---|---|---|
| **grp `0xe3fdae6c`** (5 wallets: `0xe3fdae6c`, `0x3d31b1e1`, `0x30d81c46`, `0xa8603745`, `0x74b904c6`) | 5 wallets buying the same coins, none of them their own launches | 288 | **+18.3%**; **+13.5% at 5/8/12 blocks** | +31.3% (21) | **add** |
| `call:0xd6d35b56` | a public tool: 144,442 buys into 6,678 wallets | 1,547 | +12.1% | +2.4% (203) | fading: watch |
| grp `0xa9c2de9f` (26 wallets) | wallets buying the same coins | 243 | +14.7% | −7.8% (40) | fading: watch |
| `call:0xf2c69db0` | a contract buying into 180 wallets | 241 | +12.1% | −4.7% (12) | no |
| `rec:0x9e0771d4` | dropped by the first pass as stopped | 174 | +25.8% | none: its copies end Nov 8 | gone |
| grp `0x66e78f65` (45 wallets) | launch 30% of the coins they buy | 449 | +27.4% | none: they end Nov 7 | gone |

The group's setting, the best under both landings (`out/rhd2_grp_0xe3fdae6c_fix*.txt`): its buys of 0.02+ ETH, coins
with under 0.5 ETH in the curve, no price limit, take profit 3.5x, 600 s, no sell pressure, stall 240 s, its early sale
followed: 288 copies, halves +0.59 / +0.47 ETH, P(mean>0) 100%; at 5/8/12 blocks +0.42 / +0.36. About 3 copies a day
lately (21 in the last 7 days). In the bot: the five addresses as five leaders with these settings (one copy per coin).

**The final audit before going live** (`rhd7_group_audit.py`, `out/rhd7_group_audit.txt`, data to Nov 19 11:23 UTC):
the bot copies the first member buy that passes the filters, the research the group's first buy; that adds 5 copies in 41
days (+0.0015 ETH together): 294 copies, +17.5% a copy, against 289 at +17.8%. The last 7 days 22 copies +30.2% a copy,
the last 3 days 11 at +41.3%. Member buys of 0.01+ ETH: 98 in the last 72 h, 41 in 48 h, 7 in the last 24 h (slowing on
Nov 19). Added on the box as wallets 4-8 the same day.

**"He is making much more than us"** (`rhd8_exit_redo.py`, `out/rhd8_exit_redo.txt`, Nov 19 12:04 UTC; the owner, after 15
live trades and 2 wins, and "check if we get rid of the time"). The leader's own result on the coins we copy (its sales
minus its buys, tokens left valued at the last state) against our copy, live settings, landing 2/3/5 blocks:

| wallet | the leader itself | our copy | its sale followed (early / always) | time none | time 900 s | today: leader / us |
|---|---|---|---|---|---|---|
| 1 | +18.5% (521) | **+13.9%** | +4.4% / +1.6% | +7.9% (half 1 −5.3%) | +13.8% | +4.5% / −14.9% (6) |
| 2 | +11.7% (662) | **+7.7%** | +6.7% / +6.3% | +4.8% | +8.0% | +5.7% / −3.2% (10) |
| 3 | +42.7% (383) | **+24.1%** | +22.9% / +22.1% | +23.9% | +23.9% | +92.1% / +5.1% (4) |

We keep 55-75% of each leader's edge: it buys first, we buy after it and the snipers who follow it (1.1-1.2x its price,
plus the launchpad's 9-10% early tax), and it sells into the crowd we are part of. Following its sale loses most of the
edge (wallet 1 sells within seconds, often in its own block: its sale is the drop). No time limit is worse for wallets
1 and 2 and the same for 3. The live settings stay the best by the weaker half. Nov 19 was a weak day for the leaders
themselves (wallets 1, 2: +4.5%, +5.7% on today's coins, against +18.5%, +11.7% over 41 days).

`rh1_fetch.py` now merges `blocks.json` (a short refresh had replaced the 40 days' block times; `rhd7` and `rhd8` re-run
on the rebuilt table).

**Volume and holders** (the owner: "check volume and holders ... on the backtest and live trades"; `rhd9_volume_holders.py`,
`rhd9b_live_features.py`, `rhd10_holders_exit.py`, `out/rhd9*.txt`, `out/rhd10_holders_exit.txt`). As an entry filter:
nothing to filter on for wallets 1-3, which buy in the coin's first second (age 0.1-0.9 s, 1-3 holders, 1-3 trades; on
every live trade the coin had 1 holder and 1 trade at its buy); for the group (10-160 s, 2-9 holders) every holder or
volume filter picked on one half lost on the other. As an exit (T = 60/120/180 s after its buy, sell if fewer than N
holders or under V ETH traded; 42 rules a wallet, picked on one half, scored on the other): 1-3 of 42 rules beat live on
both halves, by +0.000 to +0.033 ETH over 41 days, about what chance gives; the picks on one half lose up to 0.2 ETH on
the other. The live pattern (winner #8 at 24 holders after 60 s, most losers at 3-9) does not hold over the backtest.
Nothing changed.

**The take profits** (the owner: "you sure these are the best and not lower?"; `rhd11_tp.py`, `out/rhd11_tp.txt`): each
live setting with only the take profit changed, 1.5x to none. Lower is worse for every wallet. Wallet 1's 4x, wallet 2's
3.5x and the group's 3.5x are the best on the whole and without the best 2% (higher ones make more for wallet 2 only
from its rare spikes). Wallet 3's 2.5x is not: **3x beats it on both halves** (+1.097 / +0.957 ETH against +0.908 /
+0.940), without the best 2% (+1.733 against +1.606) and in the last 7 days (+39.0% a copy against +36.6%); 3.5-5x make
more in all but less in the second half.

**The time limit, closely** (the owner: "check time really well, look they are still holding a lot of coins";
`rhd12_time.py`, `out/rhd12_time.txt`). Wallet 2 never sells all of a coin on the curve in 84% of its copies, the group in
100%: but held to the end of the data, wallet 2's copies make −1.42 ETH without the best 2% and the group's −17.2% a copy
(the coins die later); "hold while it holds" (its sale, no time limit) is worse for every wallet. By time limit: wallet 1
best at 600 s (longer loses in half 1), wallet 3 indifferent (its other exits come first), **wallet 2 and the group better
at 900 s on both halves** (wallet 2 +0.636 / +0.445 ETH against +0.608 / +0.431; the group +0.603 / +0.502 against +0.583
/ +0.480). Also found (live buy #17, wallet 3): with no price limit set, the bot's 25% slippage on the expected tokens
acted as a ~1.33x limit, which the backtest never had (rhd2: wallet 3 none +25.7 / +23.9% a copy against 1.25x +22.7 /
+22.5%; the group none +14.3 / +13.2% against 1.25x +11.0 / +7.5%). **Applied to `config/rh-copier.example.toml`:** wallet 2
and the group 900 s; wallet 3 tp 3x (`rhd11_tp`); wallet 3 and the group `max_premium = 3.0`.

**Following its sale under conditions** (`rhd13_its_sale_filters.py`; the owner: wallet 4's copy follows its sale under
filters): 14 conditions (age window, price against its price, share of its tokens sold, combinations; wallet 4's own rule
30-290 s under 1.5x among them). None beats "never" on both halves except wallet 3's "under 1.0x and 50%+ sold" (+0.001 /
+0.011 ETH, noise); wallet 4's rule takes wallet 1 from +13.9% to +4.4% a copy. These leaders flip in seconds: their sale
is the drop. The group never sells on the curve: no effect.

**Day by day** (`rhd14_daily.py`, `rhd14b_today.py`; the owner: "backtest yesterday ... close to today but ended up
profitable?"): the settings that ran on Nov 19 morning, all four together: 14 of the last 15 days positive (Nov 18: 56
copies, 23 won, 4 take profits, +0.163 ETH, +14.6% a copy); Nov 19 to 13:09 UTC −0.020 ETH (−3.7% a copy), the first
weak day. Against the bot that day: the model's copies the bot bought and closed −0.0405 ETH, live −0.0644 (late
landings on #15, #19, #22); not bought +0.0308 (the "seen" bug's +77% copy at 00:44, fixed; #17 under the hidden ~1.33x
limit, fixed; the group's +74.5% before it was added). One coin (08:07, 0x3a227ce5) bought by wallets 2 and 3 in one
block: copied under wallet 3's rules (model −31.4%), wallet 2's would have made +77.5% (model).

**Smarter exits** (the owner: "hold for longer if wallet is still holding ... be smart" and "lower take profit when x y
or z changes ... adaptation"; `rhd15_hold_if_holding.py`, `rhd16_adaptive_tp.py`). Each live setting, every variant
picked on one half and scored on the other, kept only if better on both halves and without the best 2%.
(1) Holding past the time limit on a condition (the leader still holds 50%+; price at or above its price / 1.25x; other
traders net buying over 60 s; combinations), capped at 30 min / 1 h / none, out on its sale and/or a 20% drop: 63 a
wallet; 0 pass for wallets 1, 2 and the group, 1 for wallet 3 (+0.013 / +0.019 ETH); the picks lose up to 0.69 ETH on the
other half (wallet 1). (2) An extra, earlier exit: the take profit falling with time, a lower one after its sale, a
trailing stop once up, a lower one under sell pressure, a lock-in: 36 a wallet; 0 pass for wallet 1 and the group, 1 for
wallet 2 (+0.011 / +0.013), 2 for wallet 3 (+0.016 / +0.004 at most): chance-sized. The live exits stay.

**Which wallet is the steadiest** (`rhd17_daily_all.py`, `out/rhd17_daily_all.txt`; live settings, Oct 9 - Nov 19, per UTC
day): wallet 3 34 positive of 38 active days (4 losing, longest losing run 1 day, deepest fall 0.032 ETH, +2.06 ETH);
the group 34 of 42 (8 losing, all small, deepest fall 0.020, +1.10); wallet 1 27 of 39 (12 losing, worst −0.073, deepest
fall 0.086, +1.45); wallet 2 18 of 28 (10 losing, worst −0.106 on Nov 12, +1.05). All four together: 39 of 42 days
positive (losing: Oct 31 −0.078, Nov 15 −0.015, Nov 19 −0.024 to 13:09 UTC), +0.135 ETH a day on average.

**Wallet 2 does not hold** (on chain, Nov 19; `rhd18_w2_real_sales.py`, `out/rhd18_w2_real_sales.txt`): on all 12 of its
coins that day it emptied its position within 11-110 s, on 10 by sending the tokens to 0x65050a9b, a shared sell service
(it sells on 24,769 curves for many users) that sells them on the curve; over the 41 days the service sold on 96% of
wallet 2's coins, and wallet 2's first sale (its own or the service's) came a median 33 s after its buy (90%: 159 s).
Earlier studies saw only its own sales (15%) and called the rest "holding". With its real sales (the service's sales of
its token amount or half, within 1%), following them is worse in every variant: always −0.1% a copy against +8.0%;
wallet 4's rule +4.8%; the best +5.6%. Wallet 2 is a flipper like wallet 1. `rh-copier status` now counts such a sale
as the leader's in its "its pct / it sold" columns.

**Selling before the leader** (the owner: wallet 2 "typically sells after 33 seconds, what if we always sell before?";
`rhd19_short_hold.py`, `out/rhd19_short_hold.txt`): holds of 3-120 s after its buy, with the other exits kept or as a pure
time sale. Worse for wallet 2 (+1.0 to +1.8% a copy at 5-30 s, second half negative, against +7.9%), wallet 1 (+5 to +7%
against +13.9%) and the group (+4 to +7% against +18.9%): our entry pays the early tax and the first seconds are the
snipers' flip. **Wallet 3 better with a pure time sale at 30-60 s**: 45 s +33.3% a copy against +26.9%, halves +1.496 /
+1.066 ETH against +1.098 / +0.965, without the best 2% +1.777 against +1.743 (last 7 days +36.6% against +38.1%); with
its other exits kept, 45 s is worse (+26.5%: sell pressure fires in the window). Applied: wallet 3 sold 45 s after its
buy with no other exit; the daily stop 0.1 ETH (the owner's call).

## rhd20: a low take profit, 1.1x to none (Nov 19; "tp at 1.3x, small profits on more trades")

`rhd20_low_tp.py` (`out/rhd20_low_tp.txt`, landing 2/3/5 blocks; `out/rhd20_low_tp_land8_12_15.txt`, 8/12/15). The take
profit is a multiple of the leader's buy price (the bot's `ratio = price / its price`). Each wallet's setting now, only
the take profit changed. At 1.3x, landing 2/3/5 blocks:

| | live | tp 1.3x | hits at 1.3x | a hit pays us |
|---|---|---|---|---|
| wallet 1 (tp 4) | +13.9% a copy | −1.9% | 59.1% | +11.8% |
| wallet 2 (tp 3.5) | +7.9% | −4.6% | 42.0% | +15.4% |
| wallet 3 (45 s, no tp) | +33.3% | +3.5% | 65.9% | +13.0% |
| group 4-8 (tp 3.5) | +18.9% | +3.7% | 83.6% | +7.0% |

Worse for every wallet, on both halves and without the best 2%; the lower the take profit, the worse, down to 1.1x (a
hit then pays about 0: our buy is 1.1-1.2x its price plus the tax). A low take profit caps the winners that pay for the
losers and does nothing to the losers. At 8/12/15 blocks the same order holds.

## rhd21: a stop loss (Nov 19; "what about a stop loss?")

`rhd21_stop_loss.py` (`out/rhd21_stop_loss.txt`, landing 2/3/5; `out/rhd21_stop_loss_land8_12_15.txt`). Each wallet's
setting now plus a stop on what our coin would sell for (10-60% below what we paid, from the start or after 30/60 s).
Tight stops lose: at −20%, wallet 1 +13.9% → +10.3% a copy, wallet 2 +8.1% → +7.3%, the group +18.9% → +15.2% (coins
that fall 20-30% often come back before the time exit). A −40% stop is a hair better for wallets 1-3 on both halves
(+0.1 to +0.6 points a copy) and nothing for the group: too small to matter, and today's live losses (−20% to −35%)
would not have reached it.

## rhd14c: today with the settings now (Nov 19, data to ~14:35 UTC)

`rhd14c_today_now.py` (`out/rhd14c_today_now.txt`): the model on the 27 coins the bot bought and closed today
(attributing each to either of the wallets that bought it) −2.5 to −3.6 stakes (−0.051 to −0.073 ETH), live −4.6
stakes (−0.092). Today is a losing day in the model too; rhd17's worst model day for the four together was Oct 31,
−0.078 ETH. The rest of the gap: the morning's bugs (fixed), and coins both wallets 2 and 3 bought, sold on wallet 3's
45 s (0x6869cba8: wallet 2's 900 s +54.7% in the model, live −20.1%).

**Is a stop safer?** (`rhd21b_stop_safety.py`, `out/rhd21b_stop_safety.txt`; all four wallets together, 1,863 copies,
Oct 9 - Nov 19, landing 2/3/5.) No: −20% costs 0.65 ETH and makes the deepest fall worse (0.092 against 0.078 ETH) and
adds a losing day (4 against 3); −30% has the same worst day, losing days and deepest fall as no stop, for 0.17 ETH
less. The worst copy is −87% with or without a stop: the big losses come in one trade (a dump), which a stop sells
after.
