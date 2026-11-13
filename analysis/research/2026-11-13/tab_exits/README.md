# TAB16RxX's exits on exactly the buys the bot takes (Nov 13)

TAB16RxX = `TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3`, copied by the unit `rugsnipe-long-tab` since Nov 12 (paper)
and Nov 13 11:48 UTC (0.1 SOL). The lookalike study (branch `claude/dreamy-dijkstra-ln0wdk`,
`analysis/research/2026-11-13/lookalikes/`) picked tp 3.0 + 300 s on a small grid. This folder redoes the exit choice
on a wider grid, on the bot's own set (its detection and route planner, 3-hop routes in).

Run order (the RPC from the environment, never in a file):

```
RPC_URL=... python3 -I fetch_all.py                      # ./tx/*.json and ./sigs.json: its landed transactions since Oct 29
W=TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3 cargo run -q --release -p rugsnipe-long --example scan -- $RPC_URL tx "" 1.0 > out/scan_tab.txt
RPC_URL=... LK=<cache dir> python3 -I tab_grid.py tx sigs.json out/scan_tab.txt > out/tab_grid.txt
```

`cmodel.py` and `lib.py` are the lookalike study's copies of `since_stop/model.py` for any wallet (the same trade
decoder, path and price model). Results: `out/` (added when the run finishes).
