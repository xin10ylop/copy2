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
