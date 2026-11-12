# 08. The new box: wallet 4's part A and Rafinhaaaaaa, 4 SOL

Prepared Nov 3, 2026. **Nothing is running yet.** No box has existed since Cherry deleted `fra-long` on Oct 29
(`../03-strategy-A-long-copy/deploy-frankfurt.md`, top). This page is the whole path from an empty server to live
trading. Each step is one block to paste, and it says what it should print. Times are UTC unless marked; Beirut = UTC+2.

## 1. What runs, and with how much

| | Bot 1: the long copy | Bot 2: the copier |
|---|---|---|
| Copies | wallet 4's 1.45+ SOL buys of coins priced in other tokens that pump routes (part A) | Rafinhaaaaaa's 5.0+ SOL buys, on any venue |
| Unit | `rugsnipe-long` (`rugsnipe-long run`) | `rugsnipe-copier` (`rugsnipe-long copy`) |
| Config | `/etc/rugsnipe/long.toml` | `/etc/rugsnipe/copier.toml` |
| Wallet | `/etc/rugsnipe/keys/long-wallet.json` | `/etc/rugsnipe/keys/copier-wallet.json` |
| Stake, open at once | 1 SOL, 2 | 1 SOL, 1 |
| Daily stop | 1.0 SOL | 0.5 SOL |
| SOL to put in | **2.8**, of which about 1.0 goes into the WBTC float (some of its coins are bought with WBTC) | **1.6** (Nov 4: a buy needs 1 + 0.05 kept + the tip, so 1.2 would stop buying after −0.15; 1.6 = the stake + the 0.5 daily stop + 0.1) |
| Docs | `../docs/20-long-copy.md`, `../03-strategy-A-long-copy/` | `../docs/21-copier.md`, `../rafinhaaaaaa/` |

**Two wallets.** Each bot trades from its own wallet, and SOL does not move between them by itself. With the copier at
1.6 SOL (Nov 4) the two take 4.4 SOL; with 4 SOL in all, one of them gets 0.4 less (the owner decides).

**What to expect, per day at these stakes:**

| | Backtest | Per day | Without the 2 best trades |
|---|---|---|---|
| Rafinhaaaaaa, 1 SOL, its 5.0+ buys, Oct 4-25 (out of sample), our buy at the end of the slot after its buy / two slots after | +11.48 on 45 / +5.66 | +0.55 / +0.27 | +0.16 / −0.11 |
| Rafinhaaaaaa, the same, Oct 25 - Nov 1 | +13.37 on 21 / +9.70 | +1.91 / +1.39 | +0.63 / +0.32 |
| Rafinhaaaaaa, the same, Nov 1-4 (3.75 days) | +0.18 on 8 / −0.20 | +0.05 / −0.05 | −0.61 / −0.63 |
| Part A, 1 SOL, 2 open, Oct 19-27 (`config/long.example.toml`, the `max_open` grid) | +6.5 and +8.1 over 9 days | +1.6 | — |
| Part A, 1 SOL, 2 open, Oct 29 - Nov 4 (5.9 days, the model, `../analysis/research/2026-10-31/since_stop/`) | +1.79 with the 0.8 stop; **+6.92 with no stop** | +0.3; **+1.2** | about −0.2 as built; +2.2 with no stop (by half) |
| Part A after wallet 4 changed on Oct 27 | −2.02 on Oct 27-28 (4 open, `../07-rework-2026-10-28/`); live +1.345 on 16, Oct 28-29 | about 0 to +1 | — |

Expect the low half: part A's flow has halved since Oct 27 (7-18 copyable buys a day,
`../analysis/research/2026-11-02/w4rev/`). Sources for Rafinhaaaaaa: `../rafinhaaaaaa/04-check-nov04/` (the landing
table). The copier asks Jupiter for a quote and a swap before it sends (0.35 s), so it lands about a slot later than the
long copy did; where it lands is read from its journal (`lag_slots`) in §8 step 2.

## 2. The rules from Oct 29 (not optional)

- **Billing:** monthly billing, or hourly with auto-recharge and a balance alert.
- **Copy each wallet file off the box before any SOL goes in** (§6). The box is never the only copy of anything.
- **Use new keys:** the Triton token and the Nozomi key were on the wiped disk, and the Triton token was also pasted in
  chat on Oct 28. Rotate both in their dashboards before step 5.
- **`rugsnipe-hot` is installed by the role, but it is never enabled on this box.**

## 3. The server

The same plan as `fra-long`: Cherry Servers **Cloud VDS 2 (Gen 2)**, `G2-4-16gb-100nv-ded`, Frankfurt, €59 a month
(`../03-strategy-A-long-copy/deploy-frankfurt.md` §1). It is 0.17-0.45 ms from Jito, Nozomi and Triton. Then follow
that page's §2 steps 1-3:

1. Root password and full upgrade.
2. The four pings: every average must be under 1 ms.
3. An `ops` user with SSH-key login only.

**If Cherry Frankfurt is out of stock** (every Cherry Frankfurt VDS was on Nov 12): **Vultr Frankfurt**, measured
0.66-0.69 ms from TeraSwitch FRA on Oct 28 (`../07-rework-2026-10-28/infra.md` §6). In stock on Nov 12 (Vultr's
public API, region `fra`): `vhp-4c-8gb-amd` High Performance, 4 vCPU, 8 GB, 180 GB NVMe, **$48 a month**; or
`voc-c-4c-8gb-75s-amd` CPU Optimized (dedicated cores), 4 vCPU, 8 GB, **$80 a month**. Ubuntu 24.04, a card as the
payment method. Nothing else changes: Nozomi stays `fra2`, the four pings must stay under 1 ms. Vultr's default user
is `root` as at Cherry, so §3's steps apply as written.

From here on, every block runs on the box as `ops`.

## 4. Code and install (on the box)

```
git clone -b claude/magical-einstein-k78idp https://github.com/xin10ylop/copy2.git ~/rugsnipe
cd ~/rugsnipe && git log --oneline -1
sudo bash deploy/install.sh --role hot --dry-run
sudo bash deploy/install.sh --role hot --force
```

- **`git log`:** prints the branch's latest commit.
- **The dry run:** lists `rugsnipe-long.service` and `rugsnipe-copier.service`.
- **The install** takes about 2 minutes and ends without an error. It logs
  `config: created /etc/rugsnipe/long.toml ... (mode = log: paper)` and the same line for `copier.toml`.
- **Both configs start in paper.**

## 5. Keys and the hot config (on the box)

```
sudo nano /etc/rugsnipe/keys/api-keys.toml
sudo chmod 0400 /etc/rugsnipe/keys/api-keys.toml
sudo nano /etc/rugsnipe/rugsnipe.toml
```

**`api-keys.toml`:** three lines, typed in from the dashboards. Never paste them in a chat.

```
GRPC_TOKEN = "..."   # the Triton gRPC token
NOZOMI_KEY = "..."
RPC_URL = "..."      # the Triton RPC URL with its token
```

**`rugsnipe.toml`:** set these three lines, under `[feeds]` and `[senders]`:

```
grpc = { enabled = true, url = "https://riptide.rpcpool.com", x_token = "GRPC_TOKEN", stale_ms = 2_000, bundle_run = true }
nozomi = { enabled = true, url = "http://fra2.nozomi.temporal.xyz", key = "NOZOMI_KEY", min_tip = 1_000_000 }
jito = { enabled = true, regions = ["frankfurt", "amsterdam"], max_rps = 1 }
```

The long copy sends through Nozomi. The copier sends through Jito, because Jupiter's swap carries a Jito tip; it needs no
key. Check:

```
sudo grep -nE '^(grpc|nozomi|jito) = ' /etc/rugsnipe/rugsnipe.toml
```

This prints the three lines, each with `enabled = true`.

## 6. The two wallets, copied off before any SOL (box, then your computer)

On the box:

```
sudo /opt/rugsnipe/bin/rugsnipe-long keygen --out /etc/rugsnipe/keys/long-wallet.json
sudo /opt/rugsnipe/bin/rugsnipe-long keygen --out /etc/rugsnipe/keys/copier-wallet.json
sudo install -m 0600 -o ops /etc/rugsnipe/keys/long-wallet.json /etc/rugsnipe/keys/copier-wallet.json ~/
ls -l ~/long-wallet.json ~/copier-wallet.json
```

- **Each `keygen`** prints one address and nothing else. Write both addresses down: one long wallet, one copier wallet.
- **`ls`** shows two files, owned by `ops`, `-rw-------`.

On your computer (Terminal, not the box). Replace `BOX` with the box's address:

```
mkdir -p ~/rugsnipe-wallets && chmod 700 ~/rugsnipe-wallets
scp ops@BOX:long-wallet.json ops@BOX:copier-wallet.json ~/rugsnipe-wallets/
ls -l ~/rugsnipe-wallets
```

`ls` shows the two files. Keep a second copy, such as an encrypted USB stick or a password manager's file vault. Never
open or print them.

Back on the box, delete the home copies:

```
rm ~/long-wallet.json ~/copier-wallet.json
```

## 7. The plan's settings, then paper for a day (on the box)

```
sudo sed -i -E 's/^max_open[[:space:]]*=.*/max_open = 2/; s/^daily_stop_sol[[:space:]]*=.*/daily_stop_sol = 1.0/; s/^cu_limit[[:space:]]*=.*/cu_limit = 200000/; s/^follow_its_sell[[:space:]]*=.*/follow_its_sell = false/; s/^stop[[:space:]]*=.*/stop = 0.0/; s/^take_profit[[:space:]]*=.*/take_profit = 2.5/' /etc/rugsnipe/long.toml
sudo grep -nE '^(mode|stake_sol|max_open|daily_stop_sol|cu_limit|follow_its_sell|stop|take_profit) ' /etc/rugsnipe/long.toml
sudo sed -i -E 's/^min_sol[[:space:]]*=[[:space:]]*5\.1[[:space:]]*$/min_sol = 5.0/' /etc/rugsnipe/copier.toml
sudo grep -nE '^(mode|daily_stop_sol|senders|jito_tip_lamports|name|min_sol|stake_sol|max_open) ' /etc/rugsnipe/copier.toml
sudo systemctl enable --now rugsnipe-long rugsnipe-copier
sleep 20; sudo journalctl -u rugsnipe-long -u rugsnipe-copier -n 12 --no-pager
```

**The long config** (first grep):

| Key | Should read |
|---|---|
| `mode` | `"log"` |
| `stake_sol` | `1.0` |
| `max_open` | `2` |
| `daily_stop_sol` | `1.0` |
| `cu_limit` | `200000` |
| `follow_its_sell` | `false` |
| `stop` | `0.0` (no stop, since Nov 4) |
| `take_profit` | `2.5` (since Nov 12) |

`cu_limit` and `follow_its_sell` are as `fra-long` ran them. **`stop = 0.0`** turns the 0.8 stop off (it needs the
code from Nov 4, `stop = 0 means no stop`): since Oct 30 wallet 4 sells most of its big buys early, and the stop sold
into its sale. Oct 29 - Nov 4 at 1 SOL × 2, landing 4 trades behind it: +1.79 SOL with the stop, +6.92 without;
better at every landing and in both halves, neutral on Oct 19-28 (`../analysis/research/2026-10-31/since_stop/`).
**`take_profit = 2.5`** (Nov 12, `optimize.py`): over Oct 29 - Nov 12 at 1 SOL × 2 it beats 2.0 at every landing from 2 to
7 and in both weeks, raw and corrected (landing 4: +11.26 against +4.91 raw, +31.83 against +27.38 corrected). On the
older Oct 19-28 data 2.0 was better; wallet 4 has changed since, and the two weeks since agree.

**The copier config** (second grep):

| Key | Should read |
|---|---|
| `mode` | `"log"` |
| `daily_stop_sol` | `0.5` |
| `senders` | `["jito"]` |
| `jito_tip_lamports` | `1000000` |
| `max_open` (all wallets) | `6` |
| target | `name = "rafinha"`, `min_sol = 5.0`, `stake_sol = 1.0`, `max_open = 1` |

`min_sol = 5.0` since Nov 4: its 5 SOL swaps read 5.05 or 5.10 by its tip, and the old 5.1 skipped the 5.05 ones. The
`sed` changes a file made from the older example and leaves a 5.0 alone.

**The journal** ends with these lines:

- `long start: mode Log ... stake 1 SOL ... max_open 2 ...`
- `long feed connected`
- `copier start: mode Log ...`
- `copier feed {"up":true}`

An empty hour after that is normal.

**Read it during the day:**

```
sudo /opt/rugsnipe/bin/rugsnipe-long status --config /etc/rugsnipe/long.toml --tz +0200
sudo /opt/rugsnipe/bin/rugsnipe-long copy-status --config /etc/rugsnipe/copier.toml --tz +0200
```

Paste both after about a day. I check every paper trade against the chain and against the model, then we go live.

## 8. Going live (when you say so)

**Step 1: fund the wallets, and fill the WBTC float.** Send **2.8 SOL** to the long wallet and **1.6 SOL** to the copier
wallet from Phantom (§1: 1.2 would stop the copier's buys after −0.15 SOL). Then on the box:

```
sudo /opt/rugsnipe/bin/rugsnipe-long status --config /etc/rugsnipe/long.toml --chain
sudo /opt/rugsnipe/bin/rugsnipe-long float buy 3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh 1.0 --config /etc/rugsnipe/long.toml
sudo /opt/rugsnipe/bin/rugsnipe-long status --config /etc/rugsnipe/long.toml --chain
```

- The first `status` shows `wallet 2.8000 SOL`.
- The float buy lands one Jupiter swap.
- The second `status` shows about 1.8 SOL plus the float, about 1.0 SOL of WBTC.

**Step 2: the first live hours at a small stake.** This is a new box and the copier's first real money, so the first
trades are small: long 0.1 SOL, copier 0.3 SOL. I check each trade on chain, as `deploy-frankfurt.md` §6 did.

```
sudo sed -i -E 's/^mode[[:space:]]*=.*/mode = "on"/; s/^stake_sol[[:space:]]*=.*/stake_sol = 0.1/' /etc/rugsnipe/long.toml
sudo sed -i -E 's/^mode[[:space:]]*=.*/mode = "on"/; s/^stake_sol[[:space:]]*=.*/stake_sol = 0.3/' /etc/rugsnipe/copier.toml
sudo grep -nE '^(mode|stake_sol) ' /etc/rugsnipe/long.toml /etc/rugsnipe/copier.toml
sudo systemctl restart rugsnipe-long rugsnipe-copier
sleep 20; sudo journalctl -u rugsnipe-long -u rugsnipe-copier -n 12 --no-pager
```

- The grep shows `mode = "on"` in both files, `stake_sol = 0.1` in the long config and `stake_sol = 0.3` in the copier
  config.
- The journal shows `long start: mode On wallet ... stake 0.1 SOL` and
  `copier start: mode On wallet ... senders ["jito"] + rpc`.
- The copier's `copier start` line also lists Rafinhaaaaaa's target with its stake.

**The copier's go/no-go at 0.3 SOL:** its `buy` and `sell` journal lines carry `lag_slots` (the slot our swap landed in,
minus its slot). Paste them after its first 5 copies:

```
sudo grep -E '"ev":"(buy|sell)"' /var/lib/rugsnipe-copier/copier.jsonl | grep -o '"lag_slots":-\?[0-9]*' | sort | uniq -c
```

- Most at **0 or 1**: the rule holds there (`../rafinhaaaaaa/04-check-nov04/`). Go to step 3.
- Most at **2 or more**: stay at 0.3 SOL. At that landing it was luck on Oct 4-25 (−2.33 without the best 2). Then
  the next step is to build its venues' swaps ourselves, to land sooner.

**Step 3: the plan's stake (1 SOL each), after the first few trades check out on chain.**

```
sudo sed -i -E 's/^stake_sol[[:space:]]*=.*/stake_sol = 1.0/' /etc/rugsnipe/long.toml /etc/rugsnipe/copier.toml
sudo grep -nE '^stake_sol ' /etc/rugsnipe/long.toml /etc/rugsnipe/copier.toml
sudo systemctl restart rugsnipe-long rugsnipe-copier
```

The grep shows `stake_sol = 1.0` twice. Open positions survive a restart.

## 9. Every day, and when to stop

- **Paste both `status` blocks of §7 once a day.** I check every trade on chain.
- **Stop new buys** (exits continue):

  ```
  sudo touch /var/lib/rugsnipe-long/KILL /var/lib/rugsnipe-copier/KILL
  ```

  Remove the files to resume.
- **Stop at once if:**
  - wallet 4 goes quiet for 3 hours, or sends 10+ SOL out (`../07-rework-2026-10-28/README.md` §6);
  - a real sale fails to land;
  - the chain disagrees with the journal.
- **Rafinhaaaaaa: re-score it every week.** Stop it if a week turns negative without the best 2.
- **After a crash loop:** run `sudo systemctl reset-failed rugsnipe-long rugsnipe-copier` before a restart.
- **The configs are root-only.** Use `sudo grep` on `/etc/rugsnipe`, never a bare `grep`.

## 10. What changes on the box when the code changes

```
cd ~/rugsnipe && git pull -q --ff-only origin claude/magical-einstein-k78idp && git log --oneline -1
sudo bash deploy/install.sh --role hot --force
sudo systemctl restart rugsnipe-long rugsnipe-copier
```

The installer never overwrites `/etc/rugsnipe/*.toml`. A changed default must be edited into the box's file as well.
