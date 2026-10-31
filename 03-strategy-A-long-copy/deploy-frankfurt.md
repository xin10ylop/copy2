# Strategy A: running it on the Frankfurt box (`fra-long`)

**Oct 29, about 13:40 UTC: the box was deleted by Cherry Servers, and the wallet with it.** The server was on hourly
billing with a few euros of credit and no auto-recharge; when the balance reached zero Cherry suspended and then
permanently wiped the server the same day (their chat support, Oct 29: "once the server is wiped its data can no longer
be recovered"; three emails were sent: low balance, balance at zero, termination). The wallet's key file existed only on
that disk, never copied off (the copy was offered on Oct 28 and called optional). **3.13 SOL and 1.4 SOL of WBTC at
`E7KX1hcM...` are unreachable for good.** Checked afterwards, all empty: the owner's Mac (shell history, iTerm logs,
Terminal saved state), the repo, the journal, the installer and keygen code (the secret was never printed), Cherry's
backups (VM Backups is a paid product, Lithuania-region only, never enabled), the recovery firms (all need a file, a
drive, a partial phrase or a password). The bot had made +1.39 SOL in its 11 hours at 0.1 and 0.5 SOL and about −0.05
in the 3.5 hours at 1 SOL before the box died (the last transaction 11:52 UTC; no position was open).

**Rules for the next box, not optional:** monthly billing, or hourly with auto-recharge and a balance alert; the wallet
file copied to the owner's machine with `scp` right after `keygen`, before any SOL is sent, and never shown on a screen;
the box is never the only copy of anything; the Triton token and Nozomi key rotated after the loss (both were on the
wiped disk). The rest of this page describes the setup as it was.

In short: the long copy runs in paper mode on a Cherry Servers Frankfurt virtual server since **Oct 28 17:58 UTC**
(19:58 Beirut time), on this repo's branch (`claude/magical-einstein-k78idp`, the hardened code), with the Triton gRPC
feed and Nozomi `fra2` configured, `follow_its_sell = false`, and **no wallet** (nothing can be sent). It is the only
box: fra1 and Ohio are terminated. The setup follows `07-rework-2026-10-28/infra.md` §9; this page records what was
actually done and the three things that went wrong.

All commands run on the box as `ops`: the prompt reads `ops@fra-long:~/rugsnipe$`. The address and the root password
are in the Cherry portal, not here. The repo is cloned at `~/rugsnipe`.

## 1. The box

| | |
|---|---|
| Plan | Cherry Servers **Cloud VDS 2 (Gen 2)**, `G2-4-16gb-100nv-ded`, Frankfurt, €0.1 an hour (€59 a month) |
| OS | Ubuntu 26.04 (what the portal offered; the installer needs `--force` for it) |
| Hostname | `fra-long` |
| Latency, Oct 28 (infra.md §9 test 1, averages of 50 pings) | Jito FRA 0.42 ms, Helius fra-sender 0.45 ms, Nozomi `fra2` 0.17 ms, Triton Riptide 0.17 ms |
| Users | `root` (password from the portal, changed at first login), `ops` (sudo, SSH key only; password login off) |
| Code | `~/rugsnipe` = this repo at `claude/magical-einstein-k78idp`, installed to `/opt/rugsnipe` with `--role hot --force` |
| Units | `rugsnipe-long` enabled and running; `rugsnipe-hot` installed by the role, **never enabled** (strategy D is stopped) |
| Keys | `/etc/rugsnipe/keys/api-keys.toml` (root, 0400): `GRPC_TOKEN` (Triton), `NOZOMI_KEY`, `RPC_URL` (Triton, with its token). Typed in from the dashboards; never printed, never in git |
| Hot config | `/etc/rugsnipe/rugsnipe.toml`: `[feeds] grpc = { enabled = true, url = "https://riptide.rpcpool.com", x_token = "GRPC_TOKEN", stale_ms = 2_000, bundle_run = true }`; `[senders] nozomi = { enabled = true, url = "http://fra2.nozomi.temporal.xyz", key = "NOZOMI_KEY", min_tip = 1_000_000 }` |
| Long config | `/etc/rugsnipe/long.toml`: `mode = "log"`, `rpc_url = "cred:RPC_URL"`, `hot_config = "/etc/rugsnipe/rugsnipe.toml"`, `cu_limit = 200000`, `follow_its_sell = false`; the rest as `config/long.example.toml` |

The start line of Oct 28 17:58 UTC: `long start: mode Log wallet 1111...1111 copy H9ku...jDg min_sol 1.45 stake 1 SOL
tp 2x stop 0.8x hold 1790s max_open 4 floats ["3NZ9...qmJh"] buy senders [] sell senders [] feed
https://riptide.rpcpool.com/...`, then `long feed connected`. The empty sender lists are right: the senders are built
only in `mode = "on"` (`src/main.rs`), so the Nozomi key is first used at the switch. `long: no wallet ... paper only`
is right too.

## 2. First setup (done Oct 28; the order, to redo it on a new box)

1. Portal: order the plan above, hourly, Ubuntu 26.04. Log in as root, `passwd`, `apt update && apt full-upgrade -y`
   (at the `sshd_config` prompt keep the local version), `hostnamectl set-hostname fra-long`, reboot.
2. The four pings (infra.md §9 test 1). Pass: every average under 1 ms.
3. `adduser ops`, `usermod -aG sudo ops`, put the laptop's public key in `/home/ops/.ssh/authorized_keys` (from the
   laptop: `cat ~/.ssh/id_ed25519.pub | ssh root@<box> 'mkdir -p /home/ops/.ssh && cat > /home/ops/.ssh/authorized_keys
   && chown -R ops:ops /home/ops/.ssh && chmod 700 /home/ops/.ssh && chmod 600 /home/ops/.ssh/authorized_keys'`), then
   `PasswordAuthentication no` in `sshd_config` and restart sshd. Log in as `ops` from then on.
4. As `ops`: `git clone -b claude/magical-einstein-k78idp https://github.com/xin10ylop/copy2.git ~/rugsnipe && cd
   ~/rugsnipe && git log --oneline -1`, then `sudo bash deploy/install.sh --role hot --dry-run`, then
   `sudo bash deploy/install.sh --role hot --force` (the build takes about 2 minutes on this plan).
5. `sudo nano /etc/rugsnipe/keys/api-keys.toml` with the three keys, `sudo chmod 0400` it. Edit
   `/etc/rugsnipe/rugsnipe.toml` (feed and sender lines above) and `/etc/rugsnipe/long.toml` (`mode = "log"`,
   `rpc_url`, `hot_config`, `cu_limit`, `follow_its_sell = false`).
6. `sudo systemctl enable --now rugsnipe-long`, then §4's check. **Never** `enable` `rugsnipe-hot` on this box.

## 3. Updating the code

```
cd ~/rugsnipe
git pull -q --ff-only origin claude/magical-einstein-k78idp && git log --oneline -1
sudo bash deploy/install.sh --role hot --force
sudo systemctl restart rugsnipe-long && sleep 15 && sudo journalctl -u rugsnipe-long -n 4 --no-pager
```
`git log` prints the branch's latest commit; the installer ends without an error; the journal ends with
`long start: mode Log ...` and `long feed connected`. Open positions and the paper record (`positions.json`,
`closed.jsonl` under `/var/lib/rugsnipe-long`) survive a restart. The installer never overwrites `/etc/rugsnipe/*.toml`,
so a new repo default must be edited into the box's file as well:
```
sudo sed -i -E 's/^max_open[[:space:]]*=.*/max_open = 4/' /etc/rugsnipe/long.toml
sudo grep -n '^max_open' /etc/rugsnipe/long.toml
```

## 4. Reading it

```
sudo systemctl status rugsnipe-long --no-pager | head -5
sudo journalctl -u rugsnipe-long --since today --no-pager | grep -E 'paper-|its-sell|skip'
sudo python3 -I ~/rugsnipe/deploy/bin/rugsnipe-history paper
sudo journalctl -u rugsnipe-long -f          # live; Ctrl+C stops watching, not the bot
```
The journal lines that matter: `long paper-buy #N ... seen at its slot +N` (a copy, and this box's lag behind wallet
4's buy), `long paper-refused` (its price already 25% higher), `long paper-sell` / `long paper-closed ... net X SOL`,
`long its-sell #N ... not followed (would make X SOL)` (wallet 4 sold early; we hold to our exits and record what
following would have made; `its_sell_net` on the record in `closed.jsonl`). The history script prints the paper book
by day with totals, in Beirut time. Both are empty until wallet 4 makes a 1.45+ SOL buy of a coin priced in another
token (11 in the 15 hours of Oct 28), so an empty hour is normal.

## 5. What went wrong on Oct 28 (and the fix)

| Symptom | Cause | Fix |
|---|---|---|
| `install.sh` refuses the OS | Ubuntu 26.04 is newer than the installer's list | `--force` |
| `rugsnipe-long` exits 2, journal `TOML parse error ... follow_its_sell ... duplicate key` | the config is root-only, so an unprivileged `grep -q ... \|\| tee -a` could not read it and appended the key a second time | `sudo sed -i '/^follow_its_sell = /d' /etc/rugsnipe/long.toml && echo 'follow_its_sell = false' \| sudo tee -a /etc/rugsnipe/long.toml`; always `sudo grep` on `/etc/rugsnipe` |
| after the fix, `restart` fails with `Start request repeated too quickly` and nothing in the journal | the crash loop used the unit's 20 starts in 300 s (`StartLimitBurst`), so systemd refused the restart without running the bot | `sudo systemctl reset-failed rugsnipe-long` then `restart` |

## 6. The 0.1 SOL test (started Oct 28 18:34 UTC, 20:34 Beirut)

Done in this order, each output as the owner pasted it:
1. `keygen --out /etc/rugsnipe/keys/long-wallet.json` (the file was absent; the hot role does not create it):
   wallet **`E7KX1hcMCXg9qUpGE5hXaotRTxv8itSbdo4b8LHmYbyc`**, file 0400 root. The file exists only on this box.
2. 0.7 SOL sent from the owner's Phantom. `status --chain` showed `wallet 0.7000 SOL`, and that the paper bot held one
   paper position (#0, bought 18:29 UTC). `float buy 3NZ9... 0.15` through Jupiter: 18,842 WBTC units, landed in slot
   462579094 (the wallet's first real transaction).
3. The two simulations of `docs/20-long-copy.md` §4 step 3 from the box, with the box's RPC URL read into a shell
   variable (`RPC_URL=$(sudo awk -F'"' '/^RPC_URL/{print $2}' /etc/rugsnipe/keys/api-keys.toml)`, never printed):
   our 0.1 SOL copy of wallet 4's WBTC-routed buy of 3j9ex53k, `buy: err null`, `round trip ... err null`; our pool
   sell of the graduated 9UinFHHj as one of its holders, `sell ... err null`.
4. `long.toml`: `mode = "on"`, `stake_sol = 0.1`, `max_open = 1`, `daily_stop_sol = 0.3` (the rest unchanged:
   `follow_its_sell = false`, `buy_senders = ["nozomi"]`, `sell_senders = ["nozomi"]`, `reserve_sol = 0.05`). Restart;
   the journal: `long start: mode On wallet E7KX... stake 0.1 SOL ... max_open 1 ... buy senders ["nozomi"] sell senders
   ["nozomi"]`, `long wallet E7KX... SOL 0.5441 floats [3NZ9JMVB 18841 (0.149 SOL)]`, `long recover: 1 live position(s)`
   (the paper coin, which closes as paper: the cap and the daily stop count paper and real apart, `engine.rs`
   `on_trigger`), `long feed connected`.

**The first real trade, 75 s after the switch (Oct 28 18:35:51 UTC), checked on chain from the Triton endpoint:**

| | Journal | Chain |
|---|---|---|
| its buy | FUN1RZrj, 1.498 SOL, seen at its slot +0 | slot 462579900, position 545 of 585, 3 coin trades before it in the block |
| our buy | `long buy #1 ... in 12605 of 3NZ9JMVB ... sent in 6 ms`, `fill ... (vs its price +6.6%)` | slot 462579901 (its slot +1), **position 24 of 491, first coin trade of its block**; 3 coin trades between its buy and ours (the rest of its block); −12,605 WBTC units, +1,838,789 coins; −0.0043 SOL (tip, fees, the coin account's rent) |
| our sell | `take_profit at 2.05x try 0 sent in 3 ms`, 3 s later | slot 462579914, +24,783 WBTC units, coins to 0, +0.0003 SOL (rent back minus tip and fees) |
| result | `closed ... net +0.0927 SOL (+92.7%) peak 2.14x` | +12,178 WBTC units = +0.0963 SOL at the float's price, minus 0.004 SOL of fees: **+0.092** |

So the first copy landed a slot behind its buy but at the top of that block, with only the 3 trades that followed its
buy inside its own block ahead of us: in the terms of `fresh/land_pos.py` that is the "30 positions behind" row, not
the "+1 slot" row the backtests assume. Received 17% above the floor (`min_out`). Two 5,000-lamport transactions to
the wallet a minute earlier (slots 462579268 and 462579290) are a third party's dust (1,000 lamports and a USDC token
account), not ours.

**The second real buy, refused by the floor (Oct 28 19:20:43 UTC), checked on chain:** E3hauBDZ, its 1.5 SOL buy at slot
462592485 position 142 (the block's first trade of the coin); ours **in the same slot**, position 402, with 7 trades of
the coin between (positions 143-401). Those 7 trades had moved the price to about 1.36x its price, above the 25%
`max_premium`, so the program refused ours: `ExceededSlippage` (6004), 3,382,585,462,822 tokens offered against our
`min_out` 3,673,345,739,972. Cost 0.000405 SOL (the base and priority fee; a failed transaction pays no tip). The journal:
`long buy #2 ... sent in 6 ms; seen at its slot +0`, then `long buy-failed #2 E3hauBDZ cost -0.0004`. That is the rule
working as built (`backtests.md` §9: a tighter or looser premium limit loses out of sample); it also shows that landing
in its slot is not enough on its own: the copiers that got in ahead of us inside the slot are what the position fight
is about (`07-rework-2026-10-28/README.md` §5).

**The first evening, Oct 28 18:34-21:32 UTC (20:34-23:32 Beirut), every trade checked on chain** (`getTransaction`,
`getBlock` with `transactionDetails: accounts`, from the Triton endpoint):

| # | coin | route | its buy (slot, position) | our buy | coin trades between | paid vs its price | exit | net SOL |
|---|---|---|---|---|---|---|---|---|
| 1 | FUN1RZrj | WBTC | 462579900, 545 | +1 slot, position 24 | 3 | +6.6% | take profit 2.05x, 3 s | +0.0927 |
| 2 | E3hauBDZ | SOL | 462592485, 142 | same slot, 402 | 7 | 1.36x: refused (6004) | | −0.0004 |
| 3 | EMJs7igZ | SOL | 462594566, 33 | same slot, 172 | 6 | +9.2% | take profit 2.05x, 32 s | +0.1028 |
| 4 | GUcG2eK2 | WBTC | 462606663, 271 | same slot, 364 | 5 | +19.2% | take profit 2.20x, 240 s | +0.0818 |
| 5 | 6TrDECwR | SOL | 462618422, 442 | +1 slot, position 51 | 3 | +17.9% | stop 0.78x, 205 s (peak 1.63x) | −0.0334 |
| 6 | JAckzYTT | SOL | 462623753, 287 | same slot, 455 | 5 | +1.5% | take profit 2.06x, 588 s | +0.1074 |
| 7 | E61exR62 | SOL | 462633652, 34 | same slot, 141 | 13 | (under 25%) | stop, 4 s (18 slots) | −0.0366 |
| 8 | Fawdfdv9 (0.5 SOL from here) | SOL | 462646439, 180 | +1 slot, 4 | 2 | 1.253x: refused by the old floor (0.2%) | | −0.0004 |
| 9 | 2HuAFrTr | SOL | 462648378, 135 | same slot, 235 | 5 | 1.36x: refused | | −0.0004 |
| 10 | 96jEWfbD (the fixed floor from here) | SOL | 462657546, 258 | +1 slot, 217 | 4 | +11.6% | stop 0.77x, 51 s (peak 1.54x) | −0.1392 |
| 11 | DyNxDFcT | pool+curve | 462662465, 105 | +1 slot, 34 | 2 | +7.9% | take profit 2.02x, 58 s | +0.4683 |
| 12 | QkhZhyUK | WBTC | 462664317, 14 | same slot, 94 | 4 | +9.8% | timer at 1.08x (peak 1.21x) | −0.0136 |
| 14 | 6xQijdyc (13 was a skip: float under the stake) | WBTC | (sold slot 462684078) | | | +9.4% | timer at 1.03x (peak 1.24x) | −0.0385 |
| 15 | AVsYL8K3 | curve (WBTC quote, 1 hop) | 462728771, 140 | +1 slot, 220 | 7 | +16.4% | timer at 0.97x (peak 1.11x) | −0.0769 |
| 16 | 7YLdWetK | SOL | 462742123, 242 | +1 slot, 117 | 4 | +11.5% | take profit 2.02x, 9 s | +0.4780 |
| 17 | FqDzSqvf | SOL | 462759986, 145 | +1 slot, 259 | 2 | +17.5% | take profit 2.02x, 216 s | +0.3995 |
| 18 | iNE6pSzD (1 SOL from here) | SOL | bought slot 462827815, 09:18:39 UTC | | | | timer, sold 09:48:30 (slot 462836209) | +0.0142 |
| 19 | HotHTmeY | SOL | bought slot 462840672, 10:04:26 UTC | | | | timer, sold 10:34:16 (slot 462849042) | −0.0424 |
| 20 | 3NWyukFy | SOL | bought slot 462862476, 11:22:10 UTC | | | | timer, sold 11:52:00 (slot 462870833) | −0.0190 |

Trades 18-20 are rebuilt from the wallet's own transactions (SOL in and out per coin, `getTransaction`), since no
journal paste exists after 10:21 Beirut on Oct 29; their landing positions were not checked. **The whole live run,
Oct 28 18:34 to Oct 29 11:52 UTC: 16 closed, 7 won, 3 refused, +1.3459 SOL** (+0.3146 at 0.1, +1.0776 at 0.5,
−0.0472 at 1 SOL); every trade's net equals the chain. The box was deleted about two hours after the last sale.

Six sends, all `sent in 3-6 ms; seen at its slot +0`; four landed in its slot, two in the next (both times its buy sat
near the end of its block); every sell landed on the first try; no `sell-failed`, `WARNING` or `CRITICAL`. The journal's
net per trade equals the chain's SOL and WBTC deltas (the WBTC trips valued at the float's price). **Real at 0.1 SOL: 6 closed,
4 won, +0.3146 SOL** (+0.10 without the best 2; trade 7, a stop 4 s after a buy that sat behind 13 trades of the coin in
its slot, came after the owner's paste); the wallet went from 0.7 to **1.010 SOL** (0.6773 SOL + 41,658 WBTC units;
the 0.006 gap is the float swap's costs). Skips in the same hours: 19 buys paid in unpriced tokens
(part B) and 2 in xStocks quotes (`no anchor reaches NVDAVuiB` / `XsoCS1Tf`), all as the rule says. Copyable buys came
at about 2 an hour. Not yet seen: a coin that graduates while we hold it (the pool sell is simulated only). The stop and
the take profit are multiples of **its** price, so #5 bought 17.9% above it and sold at 0.78x of it: −33% of the stake.
An empty cbBTC token account (a hop of #4's route) holds 0.002 SOL of rent.

**Oct 28 22:04 UTC (Oct 29 00:04 Beirut): the stake raised to 0.5 SOL, three at once, daily stop 1.0 SOL** (the owner's
decision after the evening above; the plan's step was 0.3 × 3). 1.5 SOL more from Phantom (the wallet's money is now
2.2 SOL), `float buy 3NZ9... 0.5` (63,154 units, landed in slot 462638281; the float 104,811 units = 0.832 SOL),
`stake_sol = 0.5`, `max_open = 3`, `daily_stop_sol = 1.0`; the restart's journal: `long start: mode On ... stake 0.5
SOL ... max_open 3`, `long wallet ... SOL 1.6765 floats [3NZ9JMVB 104811 (0.832 SOL)]`, `long feed connected`. The
wallet then held 2.508 SOL in all, every lamport accounted for on chain (`getSignaturesForAddress` over its 21
transactions: 2.2 in, 0.6567 into the two float swaps and their costs, +0.3143 from the seven trades, three dust
transfers from a stranger).

**The first night at 0.5 SOL × 3 (Oct 28 22:04 to Oct 29 05:21 UTC), every trade checked on chain:** 7 closed, 3 take
profits (+1.35), 1 stop (−0.14), 3 timers (−0.13): **+1.08 SOL**; the book since the start 13 closed, 7 won, **+1.39 SOL**,
the wallet 2.874 SOL + 0.33 SOL of WBTC against 2.2 put in. Every route type has now run live (copied from wSOL and from
the WBTC float, pool+curve, a direct curve buy of a WBTC-quoted coin). Wallet 4 slowed to 30-60 transactions an hour
after 23:00 UTC, its usual night pace; 3 copyable buys in 7 hours. The WBTC float (0.33 SOL after a position takes
0.5) skipped one WBTC-routed buy (`float under the stake`); a `float buy 0.7` would cover two at once.

**Oct 29 08:21 UTC (10:21 Beirut): the stake raised to 1 SOL, three at once, daily stop 3.0 SOL** (the owner's decision at
13 closed, +1.39, positive without the best 2; the plan said 40 closed). 1.0 SOL more from Phantom (3.2 SOL put in since
Oct 28), `float buy 3NZ9... 0.7` (87,674 units, landed in slot 462811572; the float 177,315 units, about 1.4 SOL), the
restart's journal: `long start: mode On ... stake 1 SOL ... max_open 3`, `long wallet ... SOL 3.1740 floats [3NZ9JMVB
177315]`, `long feed connected`. Exposure: up to 3 SOL open, a stop-out about 0.35 SOL, new buys stop at −3 SOL realized
in a UTC day.

**Oct 28 22:33 and 22:39 UTC: the first two 0.5 SOL buys refused on chain** (Fawdfdv9: our buy at its slot +1, position
4 of the block, 2 trades of the coin between, refused by 0.2%; 2HuAFrTr: its slot, 5 trades between, price 1.36x,
refused by 8.2%; `ExceededSlippage` both, 0.0004 SOL each). The first one showed the floor was not the tested rule: the
bot computed `min_out` as our share of **its average fill** plus 25%, so its own 1.5 SOL buy (about 5% between its
average and the price it left on a fresh curve) and our own impact (about 2% at 0.5 SOL, 3% at 1 SOL) ate into the
margin, and the real limit was about 1.17x the price its buy left at 0.5 SOL (1.155x at 1 SOL), against the 1.25x of
`grid.py premium`. **Fixed Oct 29** (`pos::buy_min_out`: the curve's own quote at 1.25x the price its buy left;
engine test `the_price_limit_is_against_the_price_its_buy_left`); deployed with §3.

The paper run on this box ended there (one box runs one bot). What the test must show, over 5-10 trades: buys landing
at its slot +1 or better (`long buy ... seen at its slot +N`, then `long fill ... paid X (vs its price +N%)`: that
percentage is where in its slot we landed, `07-rework-2026-10-28/README.md` §5), every sell landing (a pool sell after
a graduation included), the chain equal to the journal. Then `max_open = 4` at 0.1 SOL for the deciding days, then
1 SOL only if both pass (plan §6 step 3). `sudo touch /var/lib/rugsnipe-long/KILL` stops new buys; never
`systemctl stop` while a coin is held. The Triton token and the Nozomi key that were pasted into the chat on Oct 28 should be rotated
in their portals and the box's `api-keys.toml` updated.

## Sources

The owner's pasted outputs of Oct 28 (the Cherry order and server pages, the pings, the install log, the journal);
`07-rework-2026-10-28/infra.md` §9; `deploy/install.sh`; `deploy/systemd/rugsnipe-long.service`; `src/main.rs`.
