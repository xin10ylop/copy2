# CLAUDE.md: guide for agents working in copy2 (wallet 4)

## What this repo is

The wallet-4 half of the rugsnipe project. Wallet 4 = `H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg`.
- **Strategy A, the long copy:** `crates/rugsnipe-long`. It runs in paper mode on the owner's Frankfurt box
  (`fra-long`, Cherry Cloud VDS 2, user `ops`) since Oct 28 17:58 UTC. Ohio and fra1 are terminated.
- **Strategy D, the launch copy:** the hot copy bot `crates/rugsnipe`, with a `copy_more` entry. It is stopped.

Read `README.md` (status, A-Z index), then `02-decomposition/` (why A and not the rest), then the strategy folder you work
on. The original project docs are in `docs/` (00-08 background, 19, 20). The sister repo **copy1** holds operator 1
("him", AHwJSnFN) and the other copied wallets. The code is identical in both repos.

**Upstream:** the live code is developed in `xin10ylop/rugsnipe`, branch `claude/eloquent-mayer-264bxk`. This repo was a
snapshot at `7184554` (Oct 28); **since Oct 28 evening this repo's `crates/rugsnipe-long` is ahead of upstream** (the
hardening, `07-rework-2026-10-28/`). The Frankfurt box builds from this repo and branch (`~/rugsnipe` on it is a clone
of `claude/magical-einstein-k78idp`). A code change meant to run on the box goes here, then
`03-strategy-A-long-copy/deploy-frankfurt.md` §3 on the box.

## The owner and how to work with them

- The owner runs every command on the boxes themselves and pastes the output back. You can't reach the boxes.
  Give one copy-paste block, say what each line should print, and say which machine it runs on
  (`ops@fra-long:~/rugsnipe$` = the Frankfurt box; the old `ubuntu@ip-...` prompt was Ohio, gone). Begin blocks with
  `cd ~/rugsnipe` when they use repo paths. A dropped SSH session lands in `~` (that caused the empty "masked" unit on
  Oct 27). The box's config files are root-only: `sudo grep`, never a bare `grep` (a bare `grep -q || tee -a` appended
  a key twice on Oct 28). After a crash loop, `sudo systemctl reset-failed rugsnipe-long` before the restart.
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
- fra1's backup (wallet and API keys inside) was only on Ohio and is gone with it (Oct 28). None of it is in git; never
  rebuild it on the Frankfurt box. The box's own keys file (`/etc/rugsnipe/keys/api-keys.toml`, root, 0400) never leaves it.
- Don't publish the owner's IP, local username or server addresses in new files.

## Build and test

```
cargo build --release -p rugsnipe-long          # toolchain pinned in rust-toolchain.toml
cargo test -p rugsnipe-long                     # 15 engine tests + 16 library tests
cargo run --release -p rugsnipe-long -- simulate --rpc RPC_URL --tx SIG --user WALLET --sol 0.1 --buyback 3 --close   # our buy + round trip, simulated
cargo run --release -p rugsnipe-long -- simulate-sell --rpc RPC_URL --mint MINT --quote QUOTE --user HOLDER --graduated --close
cargo test -p pump-codec                        # the route codec (multihop fixtures byte-equal to wallet 4's own)
cargo run -p rugsnipe-long --example scan -- RPC_URL DIR      # the bot's detection over fetched transactions
cargo run -p rugsnipe-long --example curve_path -- DIR MINT WALLET
```
On the box: `sudo bash deploy/install.sh --role hot --force` (`--force` because Ubuntu 26.04 is newer than the installer
knows; `rugsnipe-hot` is installed by that role but must never be enabled there). The installer never
overwrites `/etc/rugsnipe/long.toml`. A changed default (like `max_open`) also needs the box's file edited
(`03-strategy-A-long-copy/deploy-frankfurt.md` §3).

## Datasets

The research scripts (`analysis/research/<date>/<topic>/*.py`) were run in the session scratchpad, and they still
hard-code it: `SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"`. The fetched
data is in `data/datasets/` as `.tar.xz` archives, split into parts under 95 MB. `data/datasets/MANIFEST.md` lists each
archive, what it backs and its checksum.
```
bash data/datasets/unpack.sh            # unpacks every archive into the SP path above, so the scripts run unchanged
bash data/datasets/unpack.sh h9long     # one archive
```
- `fresh3` (the study extended to Oct 28 14:54 UTC, with P3), `more` and `w4wallet` were added on Oct 28 evening; the
  `2026-10-28/fresh/` scripts read `SP/fresh3/h9long/`, the `more/` and `wallet/` scripts their own `SPX` path.
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

## Open items (Oct 28, evening; the plan is `07-rework-2026-10-28/README.md` §6)

1. **Done Oct 28 evening: the Frankfurt box** (`fra-long`, Cherry Cloud VDS 2, hourly; `03-strategy-A-long-copy/deploy-frankfurt.md`)
   runs this branch's hardened `rugsnipe-long` in paper (`mode = "log"`, `follow_its_sell = false`, so the journal
   records both exit policies) on the Triton gRPC feed since 17:58 UTC. **Ohio was terminated the same evening** (the
   owner's decision): no comparison box, and fra1's backup is gone. The box's lag is read from its own journal
   (`long paper-buy ... seen at its slot +N`).
2. **2-3 days of paper that decide** (the plan's conditions): positive without the best 2 at the backtest's costs,
   wallet 4 at 25+ copyable buys a day, its early-sale rate, buys seen at its slot +1 or better on most copies.
3. **The 0.1 SOL mechanics test** on Frankfurt (≥ 0.16 SOL in the wallet, a small WBTC float, the two simulations in
   docs/20 §4 first), then 1 SOL × 3-4 only if both pass.
4. Not built: an alarm when wallet 4 goes quiet or sends SOL out (its predecessor was emptied in one evening); a
   successor scan by its fingerprint (`07-rework-2026-10-28/wallet-check.md` §7); 3-hop routes via a v0 transaction
   (about +0.1 SOL a day); the "can wait" list of the code review.
5. Strategy D stays stopped. If the hot bot ever runs again, deploy the graduation fix `af681ad` first.
