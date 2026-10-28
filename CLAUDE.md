# CLAUDE.md: guide for agents working in copy2 (wallet 4)

## What this repo is

The wallet-4 half of the rugsnipe project. Wallet 4 = `H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg`.
- **Strategy A, the long copy:** `crates/rugsnipe-long`. It runs in paper mode on the owner's Ohio box.
- **Strategy D, the launch copy:** the hot copy bot `crates/rugsnipe`, with a `copy_more` entry. It is stopped.

Read `README.md` (status, A-Z index), then `02-decomposition/` (why A and not the rest), then the strategy folder you work
on. The original project docs are in `docs/` (00-08 background, 19, 20). The sister repo **copy1** holds operator 1
("him", AHwJSnFN) and the other copied wallets. The code is identical in both repos.

**Upstream:** the live code is developed in `xin10ylop/rugsnipe`, branch `claude/eloquent-mayer-264bxk`. This repo is a
snapshot at `7184554` (Oct 28). The Ohio box pulls and builds from upstream, not from here. A code change meant to run on
the box goes to upstream (or the box gets pointed at this repo); say which you did.

## The owner and how to work with them

- The owner runs every command on the boxes themselves and pastes the output back. You can't reach the boxes.
  Give one copy-paste block, say what each line should print, and say which machine it runs on
  (`ubuntu@ip-172-31-17-131` = Ohio). Begin blocks with `cd ~/rugsnipe` when they use repo paths. A dropped SSH session
  lands in `~` (that caused the empty "masked" unit on Oct 27).
- **Answer the question asked, directly.** "Did it behave as it should" means "did it follow its rules", not
  "is it the same as the backtest". Lead with yes or no, then the evidence.
- Plain words, short sentences, tables. Times: the owner reads Beirut time (UTC+2 on these dates); say which zone.
- **Never invent numbers.** Every figure in these docs has a source (a doc §, a research script, a pasted output). Keep
  it that way. When a paste and a doc disagree, the chain decides. Fetch it and check (`analysis/research/2026-10-28/`
  shows how).
- Be honest about losses and your own bugs. The copy bot lost −5.13 SOL live. The stuck coin was a code bug.

## Security (hard rules)

- **This repo is public.** Never commit private keys, API keys, RPC URLs with keys, `/etc/rugsnipe/*.toml` from a box,
  `*.tok` files, or the fra1 backup. Enable the hook: `git config core.hooksPath .githooks` (it refuses key material).
- Never print or ask for the contents of a key file. The SSH key (`~/.ssh/<...>.pem`) is the owner's; never ask for it or
  display it.
- fra1's backup (`/root/backups/fra1-backup.tgz` on Ohio, wallet and API keys inside) stays private: not in git, not
  shared, not in cloud sync.
- Don't publish the owner's IP, local username or server addresses in new files.

## Build and test

```
cargo build --release -p rugsnipe-long          # toolchain pinned in rust-toolchain.toml
cargo test -p rugsnipe-long                     # 9 engine tests + 15 library tests
cargo test -p pump-codec                        # the route codec (multihop fixtures byte-equal to wallet 4's own)
cargo run -p rugsnipe-long --example scan -- RPC_URL DIR      # the bot's detection over fetched transactions
cargo run -p rugsnipe-long --example curve_path -- DIR MINT WALLET
```
On a box: `sudo bash deploy/install.sh --role analytics` (Ohio) or `--role hot` (a Frankfurt box). The installer never
overwrites `/etc/rugsnipe/long.toml`. A changed default (like `max_open`) also needs the box's file edited
(`03-strategy-A-long-copy/deploy-ohio.md` §3).

## Datasets

The research scripts (`analysis/research/<date>/<topic>/*.py`) were run in the session scratchpad, and they still
hard-code it: `SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"`. The fetched
data is in `data/datasets/` as `.tar.xz` archives, split into parts under 95 MB. `data/datasets/MANIFEST.md` lists each
archive, what it backs and its checksum.
```
bash data/datasets/unpack.sh            # unpacks every archive into the SP path above, so the scripts run unchanged
bash data/datasets/unpack.sh h9long     # one archive
```
- Each archive is a scratchpad folder as it was on Oct 28: the data plus the scripts and helper modules kept beside it
  (several studies import `SP/month/*.py` and `SP/rivalpnl/*.py`, or `chdir` into `SP/dec/copy`). Logs, `*.tok`,
  `*.toml`, `.triton_url` and `live/` are left out. `analysis/research/_helpers/` has the two helper libraries
  (`month/tri.py`, `rivalpnl/*.py`) as plain files for reading.
- Many scripts also put `/home/user/rugsnipe/analysis` on `sys.path` (the upstream checkout). To run them from this repo:
  `[ -e /home/user/rugsnipe ] || ln -s "$PWD" /home/user/rugsnipe`.
- **Keys are not included.** `month/tri.py` reads a Triton URL from `month/.triton_url`, and `rivalpnl/common.py` a
  Helius key from `live/rivals2.py`. To fetch anew, supply your own. Cached responses (`month/tricache/` ...) let many
  scripts rerun offline. The Oct 28 fetchers (copy2 `analysis/research/2026-10-28/fetch/`) use the public RPC.

## Conventions

- Research: one folder per study, `analysis/research/<date>/<topic>/`, with a README that gives the run order and the
  results. Pick on **P1 (Oct 19-22)**, score on **P2 (Oct 23-27)**, and report results without each period's best 2 as
  well. Use the strict exit model (`exits_pess.py`) and the cautious price model (q). Charge 0.0095 SOL a transaction
  and the 0.0155 SOL a fill bias.
- Code: match the surrounding Rust (comment density, naming). Every behaviour change gets an engine test in
  `crates/rugsnipe-long/tests/engine_paper.rs` and a line in `docs/20-long-copy.md` §3.
- Commits: one topic each, the message says what and why (see `git log` upstream).
- Docs here: update the curated page (`03-strategy-A-long-copy/*.md` etc.), add sources, keep the README status
  table current.

## Open items (Oct 28)

1. **Deploy `7184554` on Ohio** (paper fills follow Ohio's real lag; journal `seen at its slot +N`). Then measure
   the lag and how much it costs.
2. Watch 2-3 days of paper: the win rate, wallet 4's early-sell rate (8 of 20 so far, against 3-6% in the data), and
   take profits within seconds.
3. If paper stays positive, the **0.1 SOL real test** (`03-strategy-A-long-copy/going-live.md`): real buys,
   WBTC routes, the pool sell after graduation, chain-true accounting, real fees and landing.
4. Re-run the 8-day study on fresh data (from Oct 27) if wallet 4's behaviour keeps changing (`h9long/` in order).
5. check.sh / history: count open positions and failed-sell fees (the stuck-coin lesson). Not done.
6. Strategy D stays stopped. If the hot bot ever runs again, deploy the graduation fix `af681ad` first.
