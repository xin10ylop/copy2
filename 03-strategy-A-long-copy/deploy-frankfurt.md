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
