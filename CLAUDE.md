# CLAUDE.md: guide for agents working in copy2 (wallet 4, Rafinhaaaaaa)

## What this repo is

Two copied wallets, kept apart, and the bots that copy them:
- **Wallet 4** = `H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg`: folders `01`-`07`, `docs/20`, most of `analysis/research/`.
- **Rafinhaaaaaa** = `Hn6vBWWySnxA8XjxRQDEmZEuH5QL7KqosnJGcLcUzFJ6`: everything in `rafinhaaaaaa/` (moved in from the
  private copy3 on Nov 3; the owner chose to keep this repo public, so its wallet and rule are public). It is copied by
  **the copier** (`rugsnipe-long copy`, `crates/rugsnipe-long/src/copier.rs` + `jup.rs`, `docs/21-copier.md`,
  `config/copier.example.toml`, unit `rugsnipe-copier`), which trades any venue through Jupiter.
- **The next box** (`08-new-box/`): both bots, 4 SOL. The long copy runs wallet 4's part A at 1 SOL with 2 open. The
  copier runs Rafinhaaaaaa at 1 SOL with 1 open. Prepared Nov 3, not started; the owner says when to deploy live.
- **Robinhood Chain** (chain 4663, Pons V2 launchpad): three wallets, and since Nov 19 11:51 UTC a group of five (wallets
  4-8, `analysis/research/2026-11-19/rh_deep/`), copied by `crates/rh-copier` from ONE wallet at
  0.02 ETH a copy, no paper phase (the owner's call, Nov 18); `docs/23-rh-copier.md`, unit `rh-copier`, check command
  `www`; research `analysis/research/2026-11-18/robinhood/`. **Live since Nov 18 22:10 UTC**, on `fra-long` until Nov 19 ~14:00 UTC and since Nov 19 14:17 UTC on a Cherry Chicago box (`root@eth`; the Frankfurt unit is disabled, never run both) (wallet `0x35bb5c55...`, funded 0.15 ETH from 3.8 SOL
  of wallet 4's bot wallet; the first start crashed on a TLS-engine panic, fixed in `3e1b321`, nothing was sent).
- Keep them apart: a wallet's study, docs and data go in its own folder; shared code stays in `crates/`, `deploy/`,
  `config/`, `docs/`.

Wallet 4's strategies:
- **Strategy A, the long copy:** `crates/rugsnipe-long`. **Live again since Nov 12 01:23 UTC** on a Vultr Frankfurt box
  (`fra-long`, user `ops`, prompt `ops@fra-long`): since Nov 15 18:48 UTC 0.5 SOL × 2 (0.7 from 14:12 to 18:48; its buys of 1.3+ SOL since 14:47), take profit 4.0
  (since Nov 15 19:29 UTC, with the exit signals `sell_pressure = [5, 60, 30]` and `stall_s = 180`;
  `analysis/research/2026-11-16/signals/`; **the exit is frozen since Nov 15 night, the owner's rule: no change until
  about 50 real trades or two weeks have judged it**, `2026-11-16/final_exit/`), no stop, 600 s, daily stop 1.0, the early-sale rule (`follow_early_s = [30, 290]`), 3-hop routes (v0), floats WBTC, PUMP, SPCX, TTWO,
  DJT, HYPE and AAPLx (Apple, since Nov 15 21:38 UTC) (`float_min_frac = 0.5`; `float level MINT SOL` once a day; `analysis/research/2026-11-14/float_exits/`,
  `2026-11-15/all_tokens/`), every fee tier copied (`min_fee_bps = 0`: the 125 bps floor ran Nov 15 13:08 to 15:14 UTC
  and was removed on the owner's call, for fear of overfitting; `2026-11-15/skip_filters/`); the second
  unit `rugsnipe-long-tab` (TAB16RxX) ran live Nov 18 03:52 to ~11:00 UTC on wallet 4's wallet and was removed (31 real,
  −0.88 SOL; README, Nov 18). Since Nov 18 ~11:00 UTC wallet 4's unit: 1.3+ SOL, `max_premium 0.5`, wSOL and floats. Wallet
  `Eao8T2Pk...` (its key copied to the owner's Mac first). Before that, **stopped on Oct 29 ~13:40 UTC: Cherry deleted the hourly
  Frankfurt box (`fra-long`) for a zero balance, and the wallet's only key file with it; 4.5 SOL at `E7KX1hcM...` are
  lost** (`03-strategy-A-long-copy/deploy-frankfurt.md`, top). It had run live Oct 28 18:34 to Oct 29 11:52 UTC at 0.1,
  0.5 and 1 SOL: 13 closed, 7 won, +1.39 SOL before the 1 SOL hours. Ohio and fra1 are terminated too. **Any new box:
  monthly billing or auto-recharge, the wallet file copied off with scp before any SOL goes in.**
- **Since Nov 19 22:53 UTC the unit runs the split** (`dip_stake_sol`, docs/20 §3): leg 1 = the copy above; leg 2 = the
  dip entry, tp 1.5x our fill, 900 s, floats only (`dip_float_only`), its own `max_open`. Daily stop 1.5 over both.
  **Since Nov 20 01:09 UTC: leg 1 at 1.0 SOL, leg 2 at 0.25** (the owner's call after `analysis/research/2026-11-20/split/`:
  leg 1 alone beats the 0.5 + 0.5 split; it was 0.75 before the split). **Floats since Nov 20 ~01:20 UTC: WBTC, PUMP, SPCX,
  TTWO, DJT, HYPE** (AAPLx and USDC sold and removed), each kept at 1.15 SOL by the box's `rugsnipe-float-level` timer
  (every 5 min, sizes in `/etc/rugsnipe/float-levels`: **change that file whenever the floats change**, or the timer
  buys a removed float back, as it did with AAPLx at 01:12:38 UTC). **Since Nov 20 13:23 UTC leg 2 is off** (`dip_drop = 0`, the
  owner will fund its own wallet; floats and the timer's file back to 1.0 SOL). **Since Nov 20 13:32 UTC the unit
  `rugsnipe-tape` records the pump.fun tape on the box** (`/var/lib/rugsnipe-tape`, 14 days) for the wallet search.
  **Since Nov 21 ~13:57 UTC the box is a new Cherry Premium VDS 2 (Frankfurt, monthly billing, same name `fra-long`,
  same wallet and settings: `config/long.live.example.toml`); Vultr was suspended unpaid and given up with its tape;
  the tape restarts 13:59 UTC Nov 21, 60 days kept.**
  **Since Nov 22: floats WBTC, PUMP, SPCX, TTWO, HYPE** (DJT sold and removed, the owner: low on SOL; back once the
  book is up). **Since Nov 23: HYPE swapped for hSOL** (`he1iusmf...`, Helius staked SOL; the owner's call after
  `analysis/research/2026-11-23/w4_floats/`: wallet 4's TTWO coins stopped after Nov 19, it paid with hSOL for 12 buys of
  1.3+ SOL on Nov 21-22, HYPE for none in 6 days), in both units' floats and the timer's file.
  **Since Nov 23: a PAID float** (`98kfF7rm...`, a pump meme coin, 0.6 SOL: one copy; the owner's call after
  `analysis/research/2026-11-20/tape_screen/out_w3/CqCAzte8_uncopied.txt`: CqCAzte8 paid with PAID for 11 buys of 0.5+ SOL
  on Nov 12-20, our replayed copy +65.6% a copy; price risk: a meme coin).
  **Since Nov 22 (the owner's call, no paper phase): wallet 4's unit at 0.5 SOL a copy, and a second unit `rugsnipe-long-cq`
  copying CqCAzte8 on the same wallet** (0.5 SOL, its buys of 0.5+ SOL, tp 3x, 420 s, stall 240, no sell pressure, its sale
  never; `config/long-cq.live.example.toml`; the strict test in `analysis/research/2026-11-20/tape_screen/`; the units skip
  each other's coins; check command `www` on the Frankfurt box since Nov 23, `ccc` still works). Its SOL-priced coins are copied too since `copy_sol_coins` (Nov 22, that unit only), with their own exits
  (`sol_exits`: tp 2x, 120 s; its token coins keep tp 3x, 420 s, stall 240).
  **Since Nov 23 (the owner's call, 0.5 SOL, no paper phase): a third unit `rugsnipe-long-cgy` copying CgyPomTG on the same
  wallet** (its buys of 0.5+ SOL, any coin, tp 3x, 420 s, stall 240, no sell pressure, its sale never; its SOL coins with
  the SAME exit, `sol_exits = false`; `config/long-cgy.live.example.toml`; the test in
  `analysis/research/2026-11-20/tape_screen/` README: it fails the 48-setting pick, passes the pick on all coins, and the
  fixed exit is +12.1% a copy blind; the three units skip each other's coins; check command `eee`, `ggg` still works). **On the Frankfurt box: `qqq` =
  wallet 4, `www` = CqCAzte8, `eee` = CgyPomTG, `rrr` = 3XeFcZKS, `ttt` = 6LwMLkCe, `yyy` = 6nNzEg86, `uuu` = GqWfqfG6, `iii` = FatoU1bj, `ooo` = HtHkKxYN, `ppp` = 3SiQo8MJ, `pnl` = every unit's result in
  one line each and the total (`deploy/bin/rugsnipe-pnl`), `sss` = the weekly wallet screen; on the Chicago box `www` is still
  the Robinhood copier.**
  **Since Nov 23 (the owner's call, 0.5 SOL, no paper phase): units 4 and 5, `rugsnipe-long-3xe` (3XeFcZKS, `rrr`) and
  `rugsnipe-long-6lw` (6LwMLkCe, `ttt`), same wallet, their TOKEN coins only (`copy_sol_coins = false`), tp 3x, 420 s,
  stall 240** (`config/long-3xe.live.example.toml`, `long-6lw`; the test in the tape_screen README: 3XeFcZKS passes both
  pick versions, 6LwMLkCe the strict one; both buy alone, 1.00-1.01x). The five units skip each other's coins.
  **Since Nov 24 (the owner's call, 0.5 SOL): unit 6, `rugsnipe-long-6nn` (6nNzEg86, `yyy`), its TOKEN coins only, tp 3x,
  420 s, stall 240** (`config/long-6nn.live.example.toml`; passes both pick versions, 1.02x; its token coins +17.2% a copy
  but positive only in its last two blocks, Nov 20-24). The six units skip each other's coins.
  **Since Nov 24 (the owner's call, 0.5 SOL): unit 7, `rugsnipe-long-gqw` (GqWfqfG6, `uuu`), all its coins, tp 3x, 420 s,
  stall 240, SOL coins on the same exit** (`config/long-gqw.live.example.toml`; passes both pick versions, +20.5% a copy in
  4 of 4 blocks, 1.00x; about 7 buys a day). **And an NVDAx float** (`Xsc9qvGR...`, NVIDIA xStock, 0.6 SOL; GqWfqfG6's 10
  NVDAx-paid copies +28.2%, 6nNzEg86's 7 +2.5%, the earlier mix in `2026-11-23/w4_floats/`). The seven units skip each
  other's coins.
  **Since Nov 24 evening (the owner's call: "0.1 SOL for 20 trades then raise"): unit 8, `rugsnipe-long-fat` (FatoU1bj,
  `iii`), a 20-second flipper, its SOL coins, 0.1 SOL, its own exit: tp 1.5x, 15 s, behind its sale (`follow_its_sell =
  true`), daily stop 0.3; since Nov 25 max_open 4 (its first 21 trades -0.34 SOL, luck in which coins; judge at ~100)** (`config/long-fat.live.example.toml`; `analysis/research/2026-11-24/fatou_exit/`: +11.8% a copy
  at 1 SOL on 256 buys, our sale 2 slots behind its own; +1.5% on 33 later buys; nearly all its buys on Nov 23). The eight
  units skip each other's coins.
  **Since Nov 25 (the owner's call, 0.5 SOL): units 9 and 10, `rugsnipe-long-htk` (HtHkKxYN, `ooo`), all its coins, tp 3x,
  420 s, stall 240, no sell pressure, and `rugsnipe-long-3si` (3SiQo8MJ, `ppp`), its token coins, tp 2x, 120 s, sell
  pressure 5/60, no stall** (`config/long-htk.live.example.toml`, `long-3si`; the Nov 25 screen with the consistency
  ranking, `analysis/research/2026-11-20/tape_screen/README.md`: HtHkKxYN +7.2% a copy in 4 of 4 blocks with the fixed
  exit, 1.09x; 3SiQo8MJ passes the strict test, +5.1% in 3 of 4, 1.03x, +36 SOL itself in 12 days). The ten units skip
  each other's coins.
  **Since Nov 25 evening: wallet 4's unit back at 1.0 SOL a copy** (the owner's call; daily stop 1.5 unchanged; its float-paid
  copies are as big as the float allows, down to half the stake).
  **Since Nov 24 night: TTWO float 1.5 SOL, WBTC 0.3** (the timer's file, `config/float-levels.live`; the owner's call
  after `analysis/research/2026-11-24/uncopied/`: copyable buys paid with each over 7 days, all units: TTWO 239, hSOL 77,
  PUMP 36, NVDAx 34, SPCX 19, PAID 14, WBTC 7). No new float: no unheld token has the buys or the copy result.
- **Strategy D, the launch copy:** the hot copy bot `crates/rugsnipe`, with a `copy_more` entry. It is stopped.

Read `README.md` (status, A-Z index), then `02-decomposition/` (why A and not the rest), then the strategy folder you work
on. The original project docs are in `docs/` (00-08 background, 19, 20). The sister repo **copy1** holds operator 1
("him", AHwJSnFN) and the other copied wallets. The code is identical in both repos.

**Upstream:** the live code is developed in `xin10ylop/rugsnipe`, branch `claude/eloquent-mayer-264bxk`. This repo was a
snapshot at `7184554` (Oct 28); **since Oct 28 evening this repo's `crates/rugsnipe-long` is ahead of upstream** (the
hardening, `07-rework-2026-10-28/`). The Frankfurt box builds from this repo and branch (`~/rugsnipe` on it is a clone
of `claude/magical-einstein-k78idp`). A code change meant to run on the box goes here, then
`03-strategy-A-long-copy/deploy-frankfurt.md` §3 on the box. **The next box builds from the same branch**
(`08-new-box/` §4). The branch `copier` is the copier's first push, now merged into it.

## The owner and how to work with them

- **The Frankfurt box's clock is EET (UTC+2, the same as Beirut; `date` checked Nov 23).** Its `journalctl` times are
  Beirut times. The status tables (`qqq`, `www`, ... `bought`) are UTC: `status` prints UTC unless given `--tz`.
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
cargo test -p rh-copier                         # Robinhood copier: 19 engine tests
cargo test -p rugsnipe-long                     # 32 engine tests + 71 library tests (23 of them the copier's)
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
- **Rafinhaaaaaa:** its data is plain JSON in `rafinhaaaaaa/data/` (about 0.8 MB), and its pipeline is in
  `rafinhaaaaaa/analysis/final/`. The pipeline needs `GMGN_API_KEY` from the environment, and it hard-codes the Nov 1
  scratchpad paths (`rafinhaaaaaa/README.md`, end).

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
2. **The 0.1 SOL mechanics test passed on Oct 28 evening** (7 sends: 5 in its own slot, 2 in the next, every sell
   landed first try, one buy refused by the premium floor, journal = chain on every trade;
   `03-strategy-A-long-copy/deploy-frankfurt.md` §6). Still unseen: a coin that graduates while we hold it (the pool
   sell is simulated only). **Since 22:04 UTC: 0.5 SOL × 3, daily stop 1.0** (the owner's call; the plan said 0.3 × 3).
3. **1 SOL × 3 since Oct 29 08:21 UTC** (the owner's call at 13 closed, +1.39, positive without the best 2; the plan
   said 40). Watch daily: the book without the best 2, wallet 4's copyable buys a day (2 an hour by evening, 1 every
   2 hours at night on Oct 28-29), its early-sale rate; stop at once if it goes quiet 3 hours or sends 10+ SOL out. Check every trade on chain as `deploy-frankfurt.md` §6 does; the
   backtest under the live conditions is `analysis/research/2026-10-28/fresh/land_cond.py`.
4. Not built: an alarm when wallet 4 goes quiet or sends SOL out (its predecessor was emptied in one evening); a
   successor scan by its fingerprint (`07-rework-2026-10-28/wallet-check.md` §7); the "can wait" list of the code
   review. (3-hop routes: built and live Nov 13, docs/20 §3.)
   **Other wallets to copy: searched Oct 29, none found** (`analysis/research/2026-10-29/wallets/README.md`: six scored
   in full, all flip or sell on short timers; the nearest, `3dwZP6T8`, is worth re-scoring after a week).
5. Strategy D stays stopped. If the hot bot ever runs again, deploy the graduation fix `af681ad` first.
