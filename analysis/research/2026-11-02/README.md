# Nov 2, 2026: can we pick wallet 4's launches ourselves, and is part B worth copying through Jupiter?

Two studies, run Nov 1-2 in the session scratchpad (`gmgn-out/w4rev/`, `gmgn-out/w4revB/`), saved here with their
scripts and every output under 1 MB. The large tables, tapes and caches are left out; the scripts rebuild them.
`_helpers/crc.py` is the RPC client both import as `../agents/scan/bin/crc.py`. It reads a Triton URL from the old
scratchpad's `month/.triton_url`, never prints it, and redacts it in errors. No key is in this folder.

| Study | Question | Answer |
|---|---|---|
| [`w4rev/`](w4rev/README.md) | Part A: pick its launches from the create, buy them at launch ourselves? | **No.** A rule catches 55-64% of its picks at 24-30% precision; the money is on the coins wallet 4 itself buys, and it fails at copy2's usual costs, at 0.1 SOL and a slot late. |
| [`w4revB/`](w4revB/README.md) | Part B (quotes with no canonical pool): the same, and its own picks bought through Jupiter? | **No pick rule** (every create-time rule loses on Oct 19-22; the one rotation rule that passed Oct 23-26 loses Oct 27 - Nov 1). **Its own 1.45+ SOL picks through Jupiter, a slot or two after the create, at 1 SOL, exits on our price:** +35.32 (Oct 19-22), +4.88 (+2.68 without the best 2) (Oct 23-26), +8.08 (**−6.05**) (Oct 27 - Nov 1, 15 sampled trades for 103). |

What it means for the copier (docs/21 §6): copying part B is positive in total in all three periods but not without
the best 2 on the fresh one, and the copier lands no sooner than this study's Jupiter model. It runs as a mechanics
test at 0.1 SOL, with the study's exits (2.0x / 0.8x of our price, 30 min).
