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
