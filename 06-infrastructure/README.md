# 06. Infrastructure: boxes, code, deploy, tools

In short: the code here is a snapshot of `xin10ylop/rugsnipe`, branch `claude/eloquent-mayer-264bxk`, at commit
`7184554` (Oct 28). It's the same in the copy1 and copy2 repos. Two boxes were used: **fra1** (Frankfurt bare metal,
user `ops`) ran the copy bot and the first paper run, and was **terminated on Oct 28**. **Ohio** (AWS us-east-2, user
`ubuntu`) was the analytics box, and now runs the long copy in paper mode. It holds the only copy of fra1's backup.

## 1. The boxes

| Box | Was | Now |
|---|---|---|
| **fra1** (Frankfurt bare metal, user `ops`) | the hot role: `rugsnipe-hot` (the copy bot), `rugsnipe-guard`, `shredstream-proxy`, timers (operators, discover, pnl-tg); the long copy's first paper run | **terminated Oct 28**. Everything was stopped at about 12:45 UTC Oct 27, the 40 nonce accounts closed, the SOL sent to the owner's Phantom, the state backed up |
| **Ohio** (AWS us-east-2, user `ubuntu`) | the analytics role (`deploy/aws-ohio-analytics.md`) | `rugsnipe-long` in **paper mode**, no wallet (`03-strategy-A-long-copy/deploy-ohio.md` in copy2); fra1's backup at `/root/backups/fra1-backup.tgz`, unpacked read-only under `/root/fra1` |

**The backup holds wallet private keys and API keys.** Keep it private: not in git, not shared, not in cloud sync. Never
print or copy key contents. AWS **Stop** keeps Ohio's disk, and the backup with it. **Terminate** deletes both.

Why Frankfurt for the copy bot: the launch race is won in milliseconds, close to the block leaders
(`docs/03-speed-infra.md`). The long copy holds for minutes, so Ohio's extra latency (about 0.1 s, 2-3 slots) costs
about 5-10% of its profit (copy2 `03-strategy-A-long-copy/going-live.md`).

**Where to run the long copy, decided Oct 28** ([`07-rework-2026-10-28/infra.md`](../07-rework-2026-10-28/infra.md)): a
**Cherry Servers Frankfurt VDS** (`G2-4-16gb-100nv-ded`, €59 a month or €0.101 an hour, 0.4-0.6 ms from the TeraSwitch
building; hourly for the test week), the **Triton gRPC feed** the owner already pays for (`https://riptide.rpcpool.com`,
the mainnet-shared token in `api-keys.toml`, about $0.2-0.5 a month), Nozomi `fra2` as the one buy sender. Nothing faster
matters for this bot (in-building bare metal gains 0.3-0.5 ms, about 0.002 of a 211 ms slot). Ohio adds about 100 ms on a
European leader (0.27 slot on average, 0.5 on European leaders): measure it against Frankfurt with the journal's
`seen at its slot +N` before deciding (infra.md §9). Keep Ohio for analytics, the paper comparison and the fra1 backup.

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
| the long copy | `24neU6qrWGQyvtVxiziJed6egUyTqe1QLM3K8JYNe93Y` | never funded; not on Ohio |
| the owner's Phantom | `4ZLrCvjc9X739dWrt2pvQ35rNcFDGU46YPFc4DQCkcVK` | 3.8498 SOL on Oct 28 |

## Sources

`docs/03`, `docs/06`, `docs/07`, `docs/08`; `deploy/`; each crate's `Cargo.toml`; session records of Oct 27-28 (shutdown,
withdrawal, backup, Ohio setup).
