# Strategy A: running it on the Frankfurt box (`fra-long`)

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
