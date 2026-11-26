# The coins our units do not copy, by the rule that stops them (Nov 26)

The owner: "check each one the coins we dont copy either by size or floats or sol or 3 step routes". The ten copied
wallets' 14-day histories (Helius, Nov 11-25), each coin in one group by the wallet's first buy, as its unit judges it since
the router fix (`b90c446`, any payment valued): copied; priced in a token no route reaches; a SOL coin (the token-only
units); its buy under the unit's floor. Curve trades only (PumpSwap buys are not in these histories).

Run order (scratchpad SP, `env_helius.sh`):
1. `c1_fetch.py` (`../../2026-11-19/candidates/`) with `SUB=hist26_<wallet>`, 14 days, MAXPAGES 15.
2. `cargo run --release -p rugsnipe-long --example quote_route -- RPC FILE` with the floats: each quote token is a float
   (7), joined to wSOL or a float by a PumpSwap pool (77, the "pool+curve" plan, our 3-hop routes), or unreachable (264).
   **Wrong: corrected by `u6_routes.py`** (below): the one-by-one lookups read a refused request as "no pool".
3. `u3_groups.py` per wallet (`out/<wallet>.txt`), `u4_tokens.py` (`out/tokens.txt`): the groups at the unit's floor
   and the unreachable tokens ranked by the coins a float would open.
4. Our copy replayed on the groups where the wallet makes money (`../../2026-11-24/ideas/e1_ideas.py`, HIST_PREFIX=hist26_,
   FETCH=1, the unit's exit, 1 SOL, COST 0.0064, Helius paths to ~375 s): `out/replay_*.txt`.

## Results

**What the wallets make on coins we don't copy (their own result, at the unit's floor):** SOL coins for the token-only
units (wallet 4 262 coins +66.29 SOL, 3XeFcZKS 183 +45.47, 6LwMLkCe 140 +22.76, 6nNzEg86 56 +3.50), smaller buys (wallet 4's
0.25-1.3 SOL token coins 894 +103.33), and tokens no route reaches (3SiQo8MJ 69 +11.41, wallet 4 68 +43.18). Their own
result is not ours: the replays decide.

| Group (our copy, the unit's exit) | Copies | % a copy | Without the best 2% | Blocks | Verdict |
|---|---|---|---|---|---|
| 3XeFcZKS, its SOL coins | 152 | +5.6% | +2.93 SOL | -2.0 / +3.6 / +6.8 / +13.8 | the only candidate (Nov 24: +1.3%, -4.17) |
| 6nNzEg86, token coins 0.25-0.5 SOL | 48 | +21.0% | +7.26 | -1.6 / +2.7 / +78.7 / +4.2 | one block (Nov 24: the same) |
| wallet 4, token coins 0.25-1.3 SOL (Nov 22-25) | 377 | +3.0% | -10.51 | -1.1 / +0.6 / +6.1 / +6.6 | no |
| wallet 4, SOL coins 1.3+ (Nov 20-25) | 197 | +0.0% | -10.92 | +11.2 / -6.1 / -10.4 / +5.4 | no |
| 6LwMLkCe, its SOL coins | 140 | +1.2% | -4.18 | +9.1 / +2.6 / +8.8 / -15.5 | no |
| 6nNzEg86, its SOL coins | 59 | -2.3% | -3.39 | | no |
| HtHkKxYN, 0.25-0.5 SOL | 32 | -2.0% | -2.55 | | no |
| CqCAzte8, 0.25-0.5 SOL | 64 | -2.1% | -2.98 | | no |
| GqWfqfG6, 0.25-0.5 SOL | 23 | -11.9% | -3.08 | | no |

**Floats:** no unreachable token opens enough copyable coins: USDC 51 over 14 days (the wallets' own +0.074 SOL a coin, up 5
of 13 days; CgyPomTG's USDC copies were +4.0%, negative without the best 2%, Nov 24), ANT 21, GTA6 20 (2 days), TSLAx 14,
the rest under 12 each. **Routes:** the 3-hop "pool+curve" routes already copy what they reach (wallet 4 5, 3XeFcZKS 3,
6LwMLkCe 4, 3SiQo8MJ 2 coins in 14 days); the 264 unreachable tokens have no PumpSwap pool to wSOL or a float, so a longer
route of ours cannot reach them either.

## Floats (Nov 26; the owner: "no lets add floats, and the floats balances, review them, we have 7 sol free")

`u5_floats.py SP 7` (`out/floats7b.txt`): every copyable coin of the last 7 days priced in each token, the units' stakes as
they run (qqq and uuu 1.0, the rest 0.5), each copy holding the float's SOL for its unit's longest hold (an upper bound).

| Float | Copies a day | Most SOL at once | Skipped / shrunk in 7 days: old size | new size |
|---|---|---|---|---|
| TTWO | 30.0 | 4.5 | 1.5 SOL: 20 / 8 | 2.5: 5 / 2 |
| hSOL | 13.9 | 3.0 | 1.0: 35 / 4 | 2.0: 6 / 0 |
| PUMP | 7.9 | 1.5 | 0.6: 6 / 14 | 1.0: 0 / 1 |
| NVDAx | 7.3 | 3.5 | 0.6: 18 / 14 | 1.5: 7 / 4 |
| SPCX | 4.3 | 1.5 | 0.6: 4 / 9 | 1.0: 1 / 0 |
| USDC (new) | 3.3 | 1.0 | none: 23 / 0 | 1.0: 0 / 0 |
| PAID | 1.9 | 1.5 | 0.6: 5 / 1 | kept (a meme coin) |
| WBTC | 1.7 | 1.0 | 0.3: 3 / 9 | 0.5: 2 / 1 |

The candidates replayed (`out/fl/`, e1_ideas.py with QUOTE, each wallet's unit exit, pooled): **USDC +7.4% a copy on 49,
+1.57 SOL without the best 2%** (ppp +14.5%, www +23.8%, eee +4.0%, qqq -6.4% on 6); B34nXKzC +20.7% on 9 (too few, an unknown
token); GTA6 +1.1% on 19, -1.17 without the best 2%; ANT -2.8% on 17; TSLAx -5.5% on 11. Added: USDC. SOL coins paid with SOL
tied up at most 3.0 SOL at once over the 7 days (more than 2.0 SOL on 4 copies), so ~2 SOL is kept free of floats.

## Correction: the routes (Nov 26, later), and FIONA

The owner on B34nXKzC: "dig deep". It is **FIONA (Fiona the Hippo)**, a pump.fun meme coin (created Nov 17 18:58 UTC, graduated
Nov 19 20:53 UTC to the PumpSwap pool `DjbLtX1H...` with SOL; Jupiter, Nov 26: market cap $2.06M, liquidity $279k, 10,409
holders, -29.6% in 24 h, the top holders 14.6%, mint and freeze authority off; its creator launched 1,614 coins). Coins are
priced in it as in TTWO or PUMP. **Its pool to wSOL exists, so our routes reach it (pool+curve): it was never "no route".**
`quote_route` looked up each pool one request at a time; under ~2,400 quick lookups Helius refused some, and a refused
lookup reads as "no pool" (`Rpc::cached` returns None on an error). Two paced reruns still disagreed on 57 tokens.
`u6_routes.py` checks the same pool addresses (`quote_route` PDAS_ONLY=1) in batches of 100 with retries: two runs agree,
**8 anchors (USDC now a float), 194 reached through a pool, 146 unreachable** (not 264). The groups and `out/tokens.txt`
are rerun with `out/routes.txt`: the not-copied "no route" coins at the units' floors drop (wallet 4 68 -> 52, ppp 69 ->
37, eee 43 -> 15); the unreachable tokens left with the most copyable coins are ANT 21, GTA6 20, TSLAx 14, all replayed flat
or negative. FIONA-priced coins (12 in 7 days; our replayed copy +20.7% on 9) are copied through its pool already: no
float needed, and holding a meme coin that fell 30% in a day is a risk with no gain.

The live bot looks pools up the same way (`route::plan` -> `pool_exists` -> `Rpc::cached`): a refused request at a
trigger skips the copy as "no anchor reaches". The box's own RPC is a paid one and asks a few accounts a trigger, so it
should be rare; its journal can tell (`grep "no anchor reaches"`, each token checked against `out/routes.txt`).

## 3SiQo8MJ (`ppp`): where it made its money on Nov 25-26, and its small buys (Nov 26)

The owner on "that came from coins we don't copy": "so why we dont copy". `u3_groups.py` with T_MIN = Nov 25 00:00 UTC on a
fresh history (`histp_3SiQo8MJ`): the 11 coins its unit copies, its own -0.08 SOL; its buys of 0.25-0.5 SOL, 19 coins
+0.75; under 0.25 SOL, 28 coins +0.75; tokens no route reaches, 11 coins +0.27. Our copy of its smaller buys over 14 days
(`e1_ideas.py`, BASEX = ppp's exit tp 2x / 120 s / sell pressure 5/60, 1 SOL; `out/replay_3SiQo8MJ_*.txt`):

| Its first buy | Copies | % a copy | Without the best 2% | Blocks |
|---|---|---|---|---|
| 0.1-0.25 SOL | 168 | **+10.6%** | **+14.63 SOL** | +8.9 / +17.2 / +15.8 / +0.4 |
| 0.25-0.5 SOL | 169 | +1.2% | -1.03 | +6.3 / -3.9 / +0.3 / +2.0 |

The 0.1-0.25 band is the one group of small buys that replays well (the others: HtHkKxYN, CqCAzte8, GqWfqfG6 negative), picked
after seeing it, and its last block is flat. The unit has a floor (`min_sol`) but no ceiling: `min_sol = 0.1` takes the
flat 0.25-0.5 band too.
