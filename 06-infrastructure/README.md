# 06. Infrastructure: boxes, code, deploy, tools

In short: the code here is a snapshot of `xin10ylop/rugsnipe`, branch `claude/eloquent-mayer-264bxk`, at commit
`7184554` (Oct 28), ahead of it since Oct 28 evening (`crates/rugsnipe-long`). Three boxes: **fra1** (Frankfurt bare
metal, user `ops`) ran the copy bot and the first paper run, **terminated Oct 28**. **Ohio** (AWS us-east-2, user
`ubuntu`) was the analytics box and ran the long copy's paper from Oct 27 16:11 UTC; **terminated Oct 28 evening**, fra1's
backup with it. **The Frankfurt box** (`fra-long`, Cherry Cloud VDS 2, user `ops`) runs the long copy in paper mode on
this branch's code since Oct 28 17:58 UTC ([`03-strategy-A-long-copy/deploy-frankfurt.md`](../03-strategy-A-long-copy/deploy-frankfurt.md)).

## 1. The boxes

| Box | Was | Now |
|---|---|---|
| **fra1** (Frankfurt bare metal, user `ops`) | the hot role: `rugsnipe-hot` (the copy bot), `rugsnipe-guard`, `shredstream-proxy`, timers (operators, discover, pnl-tg); the long copy's first paper run | **terminated Oct 28**. Everything was stopped at about 12:45 UTC Oct 27, the 40 nonce accounts closed, the SOL sent to the owner's Phantom, the state backed up |
| **Ohio** (AWS us-east-2, user `ubuntu`) | the analytics role (`deploy/aws-ohio-analytics.md`); `rugsnipe-long` in paper mode Oct 27 16:11 UTC to Oct 28, no wallet (`03-strategy-A-long-copy/deploy-ohio.md`); fra1's backup | **terminated Oct 28 evening**. Its paper book to Oct 28 13:31 UTC is saved in `05-live/`; the backup is gone (its wallet was empty) |
| **the Frankfurt box** (`fra-long`, Cherry Cloud VDS 2 Gen 2, Ubuntu 26.04, user `ops`) | ordered Oct 28, hourly | `rugsnipe-long` in **paper mode** on this branch's code since Oct 28 17:58 UTC, Triton gRPC feed, Nozomi `fra2`, no wallet yet (`03-strategy-A-long-copy/deploy-frankfurt.md`). `rugsnipe-hot` installed, never enabled |

**The backup held wallet private keys and API keys.** It was only on Ohio and went with it. The wallet in it had been
emptied on Oct 27 (05-live, Money); its API keys (Alchemy, Helius, Nozomi, Triton) should be rotated. The Frankfurt box
has its own keys file (`/etc/rugsnipe/keys/api-keys.toml`, root, 0400), typed in from the dashboards; never print it.

Why Frankfurt for the copy bot: the launch race is won in milliseconds, close to the block leaders
(`docs/03-speed-infra.md`). The long copy holds for minutes, so a US box's extra latency (about 0.1 s, 2-3 slots) costs
about 5-10% of its profit (copy2 `03-strategy-A-long-copy/going-live.md`).

**Where to run the long copy, decided Oct 28** ([`07-rework-2026-10-28/infra.md`](../07-rework-2026-10-28/infra.md)): a
**Cherry Servers Frankfurt VDS** (`G2-4-16gb-100nv-ded`, €59 a month or €0.101 an hour, 0.4-0.6 ms from the TeraSwitch
building; hourly for the test week), the **Triton gRPC feed** the owner already pays for (`https://riptide.rpcpool.com`,
the mainnet-shared token in `api-keys.toml`, about $0.2-0.5 a month), Nozomi `fra2` as the one buy sender. Nothing faster
matters for this bot (in-building bare metal gains 0.3-0.5 ms, about 0.002 of a 211 ms slot). Ohio adds about 100 ms on a
European leader (0.27 slot on average, 0.5 on European leaders). Ohio was terminated on Oct 28 evening, so the lag is
read from the Frankfurt journal alone (`seen at its slot +N`). The box's four latency pings on Oct 28 (infra.md §9
test 1): Jito FRA 0.42 ms, Helius fra-sender 0.45 ms, Nozomi fra2 0.17 ms, Triton Riptide 0.17 ms (averages of 50).

## 2. The code (`crates/`, Rust workspace)

| Crate | What it is |
|---|---|
| `pump-codec` | pure-byte codec for pump.fun's bonding curve and PumpSwap: constants, PDAs, curve math, events, instructions; `multihop.rs` = PumpSwap's `multi_hop_swap` (the long copy's route) |
| `rugsnipe-core` | config and validation, modes, the signed ArmSet, risk gate, rslog records |
| `rugsnipe-feed` | feed adapters (websocket logs, PumpPortal, collector relay, replay) and cross-feed dedup |
| `rugsnipe-tx` | buy/sell transaction templates, the durable-nonce pool with the no-double-buy rule, the senders (Nozomi, Helius, Jito ...) |
| `rugsnipe-exit` | the exit engine: position state machine, exit triggers, sell bounds, retry schedule |
| `rugsnipe-state` | the hot box's SQLite state (`state.db`): intents, sends, fills, positions, ledger |
| `rugsnipe-sim` | template legality, compute and loaded-bytes checks by simulation |
| `rugsnipe` | the binaries: **`rugsnipe-hot`** (the copy bot's hot loop: `entry.copy`, `entry.copy_more`, follow, tweet feed ...), replay, guard |
| `rugsnipe-ctl` | operator CLI: config validate, nonce create, `unkill` |
| `rugsnipe-long` | **the long copy** (copy2's strategy A); hardened Oct 28 evening on this branch, ahead of upstream (`07-rework-2026-10-28/code-review.md`) |

Python: `analysis/rugsnipe_analysis/` (the validation and discovery package), `analysis/research/<date>/<topic>/`
(every study, each with a README), `analysis/scripts/`. Architecture in full: `docs/06-architecture.md`.

Build and test: `cargo build --release` (the toolchain is pinned in `rust-toolchain.toml`), `cargo test -p rugsnipe-long`,
`cargo test -p rugsnipe`. The box build is `sudo bash deploy/install.sh --role hot|analytics` (dry-run first, idempotent,
`docs/07-deploy.md` §5).

## 3. Deploy files (`deploy/`)

| Path | What |
|---|---|
| `install.sh` | installs binaries to `/opt/rugsnipe/bin`, units, config templates (never overwrites an existing `/etc/rugsnipe/*.toml`) |
| `systemd/` | `rugsnipe-hot`, `rugsnipe-guard`, `rugsnipe-long`, `shredstream-proxy`, the operator / discover / pnl-tg timers, `rugsnipe.target` |
| `bin/rugsnipe-check` | **check.sh** (`cp deploy/bin/rugsnipe-check ~/check.sh`; `bash ~/check.sh [start HH:MM]`): the copy bot's live view on the hot box. Ends with `bin/rugsnipe-trades` (per wallet, Beirut time) |
| `bin/rugsnipe-history` | both bots' whole history from saved files (`check` / `all` / `paper`, `--root` for a backup); works without the live bot |
| `bin/rugsnipe-pnl-tg`, `bin/rugsnipe-vs-him`, `bin/rugsnipe-why`, `bin/rugsnipe-follow-merge`, `bin/rugsnipe-toml-set`, `bin/rugsnipe-pyrun` | Telegram P&L, comparisons against him, skip reasons, follow-table merge, config edits, Python runner |
| `aws-ohio-analytics.md`, `aws-create-fra1.sh`, `frankfurt-checklist.md`, `tune-hot.sh`, `latency_probe.sh`, `selftest.sh` | box setup and checks |

Config templates in `config/` (`rugsnipe.example.toml` = the hot bot, `long.example.toml` = the long copy). Real files
live in `/etc/rugsnipe/` (0640, never in git). Keys live in `/etc/rugsnipe/keys/` and are handed to services as systemd
credentials.

## 4. Runbooks

- `docs/07-deploy.md`: topology, install and update, the kill latch (`/run/rugsnipe/KILL`, `rugsnipe-ctl unkill`), automatic
  kill triggers (daily loss, send errors, feed stale ...), alerts, the graduation fix's deploy note.
- `docs/08-runbook.md`: from an empty server to a go/no-go answer (shadow, probe, stage A/B).
- **Clearing the daily-loss kill** (as check.sh prints it):
  `sudo systemctl stop rugsnipe-hot && sudo rm -f /run/rugsnipe/KILL && sudo -u rugsnipe /opt/rugsnipe/bin/rugsnipe-ctl unkill --state /var/lib/rugsnipe/state.db && sudo systemctl start rugsnipe-hot`.
  In probe mode the stop is the lower of `[risk] max_daily_loss_lamports` and the probe stage's own
  `max_daily_loss_lamports` (both must be raised).

## 5. Wallets (public addresses only)

| Wallet | Address | State |
|---|---|---|
| the copy bot (hot, "probe") | `4g49xGbgHZk3QYR1o6QSfDUbHmJZFwN6iDp6Vco1skff` | emptied Oct 27 |
| the long copy, old | `24neU6qrWGQyvtVxiziJed6egUyTqe1QLM3K8JYNe93Y` | never funded; its key was on fra1 only (gone) |
| **the long copy** (the Frankfurt box) | `E7KX1hcMCXg9qUpGE5hXaotRTxv8itSbdo4b8LHmYbyc` | made Oct 28 by `keygen`; 0.7 SOL in, 0.15 of it as WBTC; trading at 0.1 SOL since Oct 28 18:34 UTC |
| the owner's Phantom | `4ZLrCvjc9X739dWrt2pvQ35rNcFDGU46YPFc4DQCkcVK` | 3.8498 SOL on Oct 28 |

## Sources

`docs/03`, `docs/06`, `docs/07`, `docs/08`; `deploy/`; each crate's `Cargo.toml`; session records of Oct 27-28 (shutdown,
withdrawal, backup, Ohio setup, the Frankfurt box's setup and Ohio's termination).
