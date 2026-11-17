# Wallet hunt, Nov 17: another wallet to copy besides wallet 4?

The owner asked for this on Nov 17: "a wallet that knows how to pick coins ... dont do the mistakes of the wallets we found
before ... in an efficient way", and later: "search on the chain with filters ... not check leaderboards with thousands of
copiers".

**Result: none found.** Two independent searches gave 83 candidates: 31 from wallet 4's coins and 52 from the whole
market. Not one passes. Every wallet tested on enough of its own coins loses money without its best 5. Wallet 4 is still
the only wallet that passes.

## The rule, fixed before looking

These are the lessons of Oct 29 (`2026-10-29/wallets/`) and of TAB16RxX:

- **Behaviour (step 1):** 20+ buys of 0.9+ SOL over 8+ days. Under 50% of them in wallet 4's slot or the next one, because
  racing is speed, not picking. Median first sale 45+ s after its buy, and under 40% sold within 30 s, because a flipper
  is out before we land.
- **Our copy:** the frozen live setup with the candidate as the leader (`hunt_lib.py`).
  - Landing 4 / 8 trades, or the next slot after its buy; refused past 1.25x.
  - tp 4.0, its sale followed at 30-290 s under 1.5x, sell_pressure [5, 60, 30], stall 180 s, 600 s, 0.5 SOL.
  - 0.0026 SOL a round trip, and 0.3% a pool hop each way.
  - The exits are never tuned per wallet.
- **Pass:** positive without its best 5, and positive in both halves by time, on all of its own coins. A sample of 15-40
  coins only decides who goes to the full test.

## Search 1: the wallets on wallet 4's own coins

| Step | Script | What | Result |
|---|---|---|---|
| 1 | `screen.py` | Every wallet's 0.9+ SOL first buys on 1,559 of wallet 4's coins, Oct 21 to Nov 16 | 12,207 wallets, 112 with 20+ buys (`out/screen.txt`) |
| 2 | `pick.py` | The behaviour rule, plus our copy on wallet 4's coins ≥ 0 | 31 candidates (`out/pick.txt`) |
| 3 | `fetch_cands.py`, `w4_mints.py`, `step2_scan.py` | Each candidate's own history since Nov 3 (newest 6,000 transactions), with the bot's detection run over it | `out/step2_scan.txt` |
| 4 | `step2_model.py` | Our copy on 40 random coins (seed 7) of each one's own coins, mostly coins wallet 4 never traded | 29 tested: `out/step2_first9.txt`, `out/step2_rest20.txt` |
| 5 | `step2_model.py` (all), `deep.py`, `tp_check.py` | The full test on the two that looked good | both fail, below |

- **FZU56d9i:** +3.27 on 39 coins. On all 188: +1.46 SOL (+1.6% a copy), −3.38 without the best 5, and its second
  half −0.77 (`out/step2_fzu_all.txt`).
- **649ot18f:** +1.91 on 21 coins, +0.31 without the best 5. On all 270 routable buys since Oct 21: −2.02 SOL, −6.80
  without the best 5, losing 13 days of 22 (`out/deep_649ot18f.txt`). Every take profit from 1.5x to none loses, and
  every one is negative without the best 5 (`out/tp_649ot18f.txt`).

## Search 2: the whole market, independent of wallet 4 (`market/`)

| Step | Script | What | Result |
|---|---|---|---|
| 1-3 | `market/m1_launches.py` | Every pump launch of 48 h, from pump's mint authority; the other-token coins and their first 2,400 s | |
| 4 | `market/m2_trades.py` | A discovery pass: half the live coins (random, seed 7), each coin's first 300 transactions | 3,024 live coins with a path |
| 5 | `market/m3_screen.py` | Every wallet's 0.9+ SOL first buys. Rule: 10+ buys on 8+ coins from 4+ creators, under half at launch, the same hold rule as above | 7,027 wallets, 58 kept (`out/market_screen.txt`) |
| 6 | | 8 dropped that lose in both searches (GG5ATPW7, abcdEvoX, 9kojcBF2, 58iikVha, 3Xtu99Js, CnTeYCBA, F9i1wAMb, 6MVboLQD; `out/screen.txt` and `out/market_screen.txt`) | 52 → 44 new (`out/market_candidates*.json`) |
| 7 | `fetch_cands.py`, `step2_scan.py` | Their own history since Nov 3 | `out/step2_scan_all.txt` |
| 8 | `step2_model.py SP 15 <44>` | Our copy on 15 random coins of each | `out/step2_market44.txt` |
| 9 | `step2_model.py SP 999 <4>` | All coins since Nov 3 for the 4 wallets positive in both halves | `out/step2_market4_all.txt` |

- **Step 7:** 8 of the 44 had nothing to test. They make 6,000 transactions in hours or minutes, with no 0.9+ SOL buys
  in that time.
- **Step 8:** 36 tested. 13 were positive and 23 negative, about −1.4 SOL all together. **Every one was negative without
  its best 5.** The best 5 by net: 5QQ5Xi9i +2.98, EqiFgyNw +1.80, SQHK48QT +1.69, 57XcaxB6 +1.31, 2rioswXV +0.80.
  Each one's profit comes from 1 or 2 big coins. Among 36 wallets, that is what luck alone shows on 15 coins.
- **Step 9: the full test of the 4 positive in both halves:**

| Wallet | Coins | Net | A copy | Without its best 5 | 1st half / 2nd half |
|---|---|---|---|---|---|
| 5QQ5Xi9i | 102 | +3.50 | +7.0% | −3.05 | +3.59 / −0.09 |
| EqiFgyNw | 62 | +1.36 | +5.2% | −1.68 | +0.40 / +0.96 |
| 2rioswXV | 68 | −0.05 | −0.1% | −2.51 | +0.48 / −0.52 |
| 57XcaxB6 | 91 | −1.74 | −3.8% | −4.78 | −0.56 / −1.17 |

All four fail. 5QQ5Xi9i's whole profit is its best few coins, and they all fall in the first half. EqiFgyNw is positive
in both halves, but −1.68 without its best 5 on only 62 coins over 6 days.

## Also tried and dropped

- `kol/`: the kolscan leaderboard (`kol/leaderboard_nov17.json`, `out/kol_activity.txt`). It was dropped at the owner's
  request: thousands of copiers race those wallets. `kol/fetch_decode.py` was left unfinished.
- FzVQSzj8, 9kXTVj6x and 85jmgEf6 have the same buys and the same stats: they are one trader.

## Why wallet 4 is different

On the same model, wallet 4's copy on its own coins is +83.89 SOL over 1,559 buys, and +74.68 without the best 5
(`out/screen.txt`, first line). Its profit is spread over many coins. Every candidate's profit sits in a few coins.

## Run

The paths are as on Nov 17. `SP` is the session scratchpad, `LK=SP/hunt/lk` caches the paths, and the RPC URL comes from
`RPC_URL` and is never printed. Each script's header gives its exact command line.
