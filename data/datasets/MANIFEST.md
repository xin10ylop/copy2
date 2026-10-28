# Datasets

The scratchpad folders behind `analysis/research/`, as they were on Oct 28, compressed: the fetched data (raw RPC
transactions, signature lists, account reads, tapes, caches) and the scripts and helper modules kept beside it, which
several studies import or `chdir` into. Logs, `*.tok`, `*.toml`, `*.sh`, `.triton_url` and `live/` are left out. Every
file was scanned for API keys, tokens and keypairs before packing; none are included. Each archive unpacks to
`<SP>/<name>/`, where `SP` is the scratchpad path the scripts hard-code (see CLAUDE.md "Datasets").

```
bash data/datasets/unpack.sh                 # check SHA256SUMS, unpack everything into SP
bash data/datasets/unpack.sh dec ext         # some
SP=/elsewhere bash data/datasets/unpack.sh   # another place (then change SP in the scripts you run)
```
Archives over 95 MB are split into `.part-NN` files (GitHub's 100 MB limit); `unpack.sh` joins them. Study folders are
under `analysis/research/`.

| archive | parts | compressed | unpacked | files | what uses it |
|---|---|---|---|---|---|
| `coins` | 1 | 2.5M | 22.9M | 1,097 | used by 2026-10-28/coins (6y9aDagF, ChonQdJ8) |
| `dec` | 1 | 65.4M | 465.2M | 30,303 | used by 2026-10-25/five (copy, exact), follow; 2026-10-26/fails, flush, h9, holders, oprule, speed, wallets; 2026-10-27/refused |
| `h9` | 1 | 1004.7K | 4.6M | 501 | used by 2026-10-26/h9; 2026-10-27/h9long |
| `h9long` | 1 | 7.7M | 54.6M | 25 | used by 2026-10-27/h9long, own_ledger (our wallet's ledger `4g49xGbg_own.jsonl`); 2026-10-28 |
| `helpers` | 1 | 12.9K | 39.6K | 15 | the helper libraries `month/tri.py` (Triton client: its URL file `month/.triton_url` is not included) and `rivalpnl/*.py` (pump parsers, Helius client: its key file `live/rivals2.py` is not included); also plain in `analysis/research/_helpers/` |
| `month` | 1 | 15.5M | 86.5M | 1,779 | used by 2026-10-24 (+corrected, tweets); 2026-10-25/five, follow; 2026-10-26/fails, flush, h9, holders, oprule, six, w3, wallets; 2026-10-27/h9long, own_ledger, refused. His and 6anjqMe's month of transactions, `pull_month.py`, the Triton cache |
| `oos` | 1 | 9.4M | 49.2M | 5,608 | used by 2026-10-26/flush, holders, wallets, wallets2; 2026-10-27/refused |
| `refused` | 1 | 4.6M | 24.4M | 2,049 | used by 2026-10-27/refused |
| `w4live` | 1 | 1.3M | 10.3M | 1,220 | used by 2026-10-28/verify |
| `w4scan` | 1 | 115.4K | 791.1K | 96 | wallet 4 fetches checked with `examples/scan.rs` (2026-10-28/fetch/w4fetch*.py) |
| `w4scan2` | 1 | 175.6K | 1.2M | 157 | the same |
| `w4scan3` | 1 | 185.4K | 1.4M | 161 | the same |
| `w4win` | 1 | 943.0K | 9.7M | 1,598 | used by 2026-10-28/decomp |
| `fresh3` | 1 | 6.6M | 65M | 60 | **Oct 28, the extended study**: `fresh3/h9long/` = the `h9long` folder with wallet 4's transactions to Oct 28 14:54 UTC (20,476 signatures, 19,981 rows) and every derived file regenerated with P3 (`H9kuqGKN_fpaths.json` with the Oct 27-28 trips and the graduated coins' paths). Used by 2026-10-28/fresh and 2026-10-28/more (`DATA=fresh3`) |
| `more` | 1 | 324K | 1.4M | 10 | used by 2026-10-28/more: the fetched pools, routes, skips, quotes, coin ages and the curve paths after its early sales. Unpacks to `<SP>/more/`; the scripts' `SPX` must point there |
| `w4wallet` | 1 | 6.4M | 19M | 37 | used by 2026-10-28/wallet: signature lists, flows, pool events, neighbour transactions (the scripts and printed outputs are in the study folder). Unpacks to `<SP>/wallet/` |
