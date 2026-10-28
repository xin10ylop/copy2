# Wallet 4 on chain: funding, the predecessor, neighbours, creators (Oct 28)

The scripts and their printed outputs (`*.out`, `*.log`) behind [`07-rework-2026-10-28/wallet-check.md`](../../../../07-rework-2026-10-28/wallet-check.md),
which is the report: read it first. The fetched JSON (signature lists, flows, neighbour transactions, about 19 MB) is
in `data/datasets/w4wallet.tar.xz`; it unpacks to `<SP>/wallet/` where `SP` is this session's scratchpad path the
scripts hard-code (CLAUDE.md "Datasets"; change `SPX`/the paths in the scripts to rerun elsewhere). The scripts use the
Triton client `SP/month/tri.py` (its URL file is not included) and read wallet 4's rows from `SP/h9long/H9kuqGKN.jsonl`
(the extended file, in `data/datasets/fresh3.tar.xz` as `fresh3/h9long/`).

| Script | Output | What it gave |
|---|---|---|
| `page_sigs.py` | `page_sigs.log` | the 1,717 signatures before Oct 19, the first transaction |
| `fetch_old.py`, `old_scan.py` | `old_scan.out` | first transactions, plain flows before Oct 19 |
| `netflows.py` | `netflows.out` | every in/out of 0.5 SOL or more since birth |
| `balance.py`, `reconcile.py` | `reconcile.out` | balance points and the split of the rise |
| `failed.py` | `failed.out` | failed transactions: count, fees, errors, per day |
| `nonsigner.py` | `nonsigner.out` | transactions paid by others |
| `funder.py`, `funder2.py`, `walletflows.py` | `funder_8h5eizMg.out`, `hist_8h5eizMg.out` | the funders' flows |
| `pool_sigs.py`, `pool_tx.py` | `pool_tx.out` | privacy pool deposits and withdrawals |
| `profile.py` | `profile_*.out` | quick profiles of counterparties |
| `hxcd_first.py` | `hxcd_first.out`, `hxcd_page.log` | the predecessor's start and sampled flows |
| `fingerprint.py` | `fingerprint.out` | the transaction fingerprint of the three wallets |
| `tipscan.py`, `fpscan.py` | `tipscan.out`, `fpscan_w1.out`, `fpscan_w2.out` | tip-size uniqueness, sibling scans |
| `flash_sigs.py`, `flash_payers.py` | (printed) | FLASHX8D = Axiom's router, not wallet 4's |
| `neighbours.py`, `neigh_an.py`, `copier.py` | `neigh_an.out`, `copier.out` | who trades next to it |
| `infra_rows.py`, `infra_tx.py` | `infra_rows.out`, `infra_tx.out` | fees, tips, versions, block index |
| `creators.py` | `creators.log` | creators, create-slot timing |
| `perday.py` | `perday.out` | activity per day |
