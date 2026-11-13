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
decoder, path and price model). `tab_cells.py` prints a few cells by landing (same arguments as `tab_grid.py`).

## Results (Nov 13; `out/tab_grid.txt`, `out/tab_cells.txt`; 0.1 SOL, 2 open, raw model)

- **The set:** 12,339 of its 12,378 landed transactions fetched. Its 1.0+ SOL buys: 192 routable, 196 with no pool to
  the quote, 600 paid in an unpriced token. 183 copyable first buys in the two weeks with a path (week 1 53, week 2
  130; the lookalike study's exact check also had 183), none of them 3-hop.
- **Its own sale:** in week 2 the first sale comes 31 / 120 / 180 s after its buy (p25 / median / p75), within 60 s on
  43 of 130.
- **Live rule** (tp 3.0, 300 s, its sale never followed): week 1 +0.043 (−0.316 without the best 2), week 2 +0.309
  (−0.330); corrected +0.568 and +1.278, +1.847 in two weeks at 0.1 SOL. (The lookalike study at 1 SOL: +1.29 and
  +4.63 raw; the fixed 0.0026 SOL a round trip weighs ten times more at 0.1.)
- **Its sale followed when it comes in the first 60 s:** nothing changes in week 1 (+0.017), week 2 goes from +0.309 to
  +0.678, better at each of the three landings. Always following is the worst choice (week 2 −0.733 on average).
- **The grid's pick, third of 588 on week 1 and first on week 2: tp 4.0, 600 s, its sale followed at 0-60 s.** Week 1
  +0.275 (−0.244), week 2 +0.884 (+0.109); corrected +0.793 and +1.841, **+2.635 against +1.847 live**. Better than
  the live rule raw at all six week-landing cells, and without the best 2 at five of six. 12 of 588 rule sets beat
  live in both weeks without the best 2; the top six are this rule's neighbours (0-120 s, under 1.5x, a 0.5 stop).
- A stop at 0.5 changes nothing. Take profits under 2.5 and timers of 60 s or 30 min are the weak ends.
