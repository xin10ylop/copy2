# Wallet 4's neighbours: who else buys its coins in the create slot or the next (run Oct 28 evening UTC)

**Question.** Strategy A copies wallet 4 (`H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg`): 1.45+ SOL buys of pump coins
priced in other tokens, at the coin's create slot or the next, held up to 30 minutes. Which other wallets buy the same
coins that early, how big, how long they hold, and is any of them worth scoring as a second copy target?

**Status: done (Oct 28, 23:20 UTC).** Results below.

## Data and assumptions

- **Coins:** the 856 coins of wallet 4's trips with a first buy of 1.45+ SOL in `fresh3/h9long` (Oct 19 → Oct 28 14:54 UTC):
  the 847 closed one-buy one-sell trips of `full_paths.py` (`_fpaths.json`: 741 priced in another token, 106 in SOL)
  and the 9 coins that graduated before it sold (`_gpaths.json`).
- **Why a new fetch.** `_fpaths.json` starts *after* wallet 4's buy (`getSignaturesForAddress(until = its buy)`) and is
  sampled above 40 transactions, so it holds neither the create slot nor the buyers ahead of wallet 4, and its rows
  carry 8-character prefixes only. `fetch.py` reads, for every coin, each transaction on the bonding curve from the
  create to slot `max(C + 3, S + 2)` (landed; failed ones up to `C + 1`; the first 103 coins of the first run also hold later failed ones, which `rank.py` ignores), with full addresses. Wallet 4's own buy is
  known from its trips and is not re-read.
- **Create slot C** = the slot of the transaction that carries the coin's `CreateEvent` (found on all 856);
  **S** = wallet 4's buy slot. "Early" = a buy landed in slot C or C + 1. The create transaction's own trades (the
  dev buy) are left out.
- **Buy size in SOL** = K × (1/v_after − 1/v_before), v = the curve's virtual token reserves, with K calibrated on the
  same coin from wallet 4's buy: K = its SOL value / (1/vt_after − 1/vt_before). Check on the SOL-priced coins: K is
  1.0139× the curve's own 30 SOL × 1,073M tokens (wallet 4's SOL value includes about 1.4% fees), so sizes include fees
  the same way.
- **Hold** = time from its first early buy to its first sale of the coin: from the fetched window (complete to its
  end), then from wallet 4's path (`_fpaths.json`, by prefix; sampled above 40 transactions, so a sale can be missed),
  which ends at wallet 4's own sale. "Flip" = sold within 5 s. A wallet that has not sold by wallet 4's sale is counted
  as "held past" only where the path is complete.
- **Win** (an estimate, gross of fees): the average price of its first sale over its average early buy price > 1. When
  no sale is seen, the marginal price at wallet 4's sale over its average buy price (marked, `m`).
- **Frenzy** = other traders' landed buys in the 2 slots after its buy (b+1, b+2); wallet 4's own number on the same
  coins is the baseline.
- **Failed** = its failed transactions on these curves in slots up to C + 1, over all its transactions there.
- **Late** = coins whose wallet 4 buy is on Oct 27-28 UTC.

## Run order

```
cd analysis/research/2026-10-29/wallets/neighbours
python3 -I fetch.py                 # -> SCRATCH/wallets/neighbours/win.json (+ cache/, every response gzipped)
python3 -I rank.py 10 > out/rank.txt   # every early buyer on 10+ coins, the top 15 by coins with 0.45+ SOL buys, the named four
python3 -I activity.py > out/activity.txt   # each listed wallet's newest 1,000 signatures, read at run time
python3 -I verdict.py > out/verdict.txt
python3 -I tiers.py > out/tiers.txt     # 6anjqMeW, AMDEmVoc, DsGJkPzF, C5EMTGGE, 53DnQU1d by size, period, quote; hold histogram
```
SCRATCH = `/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad`. The RPC URL is read from the
old session's `month/.triton_url` (never printed or written here). `GAP` (seconds between calls) and `THREADS` set the pace.

## Results (fetch finished Oct 28 23:13 UTC; activity read 23:14 UTC; Beirut = UTC+2)

**Status: done.** Outputs: `out/rank.txt`, `out/activity.txt`, `out/verdict.txt`, `out/tiers.txt`.

### In short

1. **One wallet passes the profile screen: `6anjqMeWigQFo5wpciARAunVQUXTqoat8w8fFWarCkpc`.** It bought early on
   **547 of wallet 4's 856 coins** (484 of them priced in another token), in fixed sizes of 0.25 / 0.5 / 0.7 / 1.0 SOL,
   and it **holds minutes on fixed timers**: its first sales cluster at 60, 240, 480 and 740 s (median 480 s), and it
   sells everything at once on 314 of 357. It lands **after wallet 4** (before it on 1% of coins), with 0 failed of
   550 transactions in the early slots, and it is still active (52 coins on Oct 27-28; 211 signatures an hour on Oct 28).
   But on these coins it does not beat wallet 4: its first sale beat its buy price on only 128 of 357 (36%), and the
   rough gross return is +0.186 against wallet 4's own +0.193 on the same coins with fees. **Worth a full scoring on its
   own coins** (wallet-check.md: only 15% of its buys are wallet 4's coins), not as a better source for these coins.
2. **Every big early buyer that lands before wallet 4 is a flipper.** Fhbh1DTU, 9qz7cWBq, FiFawHqx, dKMjeGJ4 and
   CUQqcZZG buy 2.0-3.6 SOL (median) at create+0/+1, land ahead of wallet 4 on 90-100% of their coins, and sell 1-2 s
   later (median) into the buyers behind them, wallet 4 included. Their first sale beats their buy on 54 of 56, 37 of 37,
   27 of 27, 14 of 15 and 8 of 8. 8ptvshQR (1.34 SOL, ahead on 53%) does the same, 6 of 9. A copy cannot get that: by
   the time it lands they are out.
3. **The rest flip in seconds too:** AMDEmVoc (0.6 SOL, median hold 7 s), DsGJkPzF (0.25-1.0 SOL, 27 s), C5EMTGGE
   (0.77 SOL, 11 s), 53DnQU1d (1.0 SOL, 13 s), 9su3UPQW (0.37 SOL, 4 s), Anubis51 (1.49 SOL, after wallet 4, 2 s).
4. **No leader.** Nobody but the flippers sits ahead of wallet 4 often, as wallet-check.md §4b found on 40 coins.
5. **The frenzy test separates nothing:** after wallet 4's buy, other traders' buys in the next 2 slots are median 0
   (mean 1.18, p75 1) on these coins. After the listed wallets' buys the median is 0-5 (mean 0.78-7.18).

### Setup numbers (`out/rank.txt`)

| | |
|---|---|
| coins read | 856 of 856 (750 priced in another token, 106 in SOL), none skipped |
| create slot from the CreateEvent | 856 of 856 |
| wallet 4's buy slot − create slot | +0 on 457, +1 on 391, +2 on 4, +3 or more on 4 |
| size calibration (SOL-priced coins) | K = 1.0139× (median; p10 1.0139, p90 1.0146; 106 coins) the curve's 30 SOL × 1,073M tokens |
| early buyers (C+0/C+1, dev buy left out) | 1,008 wallets on 1+ coin; 23 on 10+ coins |
| wallet 4 on the same coins | 58 coins on Oct 27-28 (6.8%); its SOL out / SOL in − 1 = +0.193 over its 847 closed trips (fees in) |

Note: the coins are 750 priced in another token and 106 in SOL (`rank.py` prints `other 750`). The sizes come out
at round values (6anjqMeW 0.25 / 0.5 / 0.7 / 1.0, AMDEmVoc 0.6 / 0.8 / 1.2 / 1.4), which checks the calibration.

### 1. Every wallet that bought early on 10+ of the 856 coins (`out/rank.txt`)

Columns: coins (other-quote, with a first early buy ≥ 0.45 SOL); share at C+0; share landed before wallet 4's buy;
median first early buy in SOL (p90); failed / all its transactions on these curves up to C+1; median frenzy; first
sales seen (of them within 5 s); median hold to the first sale; won at the first sale (+ marked won when no sale seen);
coins on Oct 27-28.

| wallet | coins | at C+0 | before W4 | SOL (p90) | failed | frenzy | sales (≤5 s) | hold s | won | Oct 27-28 |
|---|---|---|---|---|---|---|---|---|---|---|
| 6anjqMeW | 547 (484, 363) | 42% | 1% | 0.500 (1.001) | 0/550 | 0 | 357 (21) | 480 | 128/357 +105/190m | 52 |
| AMDEmVoc | 135 (118, 126) | 50% | 18% | 0.601 (1.210) | 1/138 | 1 | 85 (31) | 7 | 53/85 +27/50m | 10 |
| DsGJkPzF | 65 (64, 33) | 58% | 18% | 0.651 (1.005) | 0/65 | 0 | 43 (1) | 27 | 29/43 +14/22m | 2 |
| Fhbh1DTU | 62 (62, 62) | 66% | 94% | 2.979 (5.154) | 511/598 | 0 | 56 (48) | 1 | 54/56 +5/6m | 4 |
| 9su3UPQW | 48 (48, 20) | 40% | 23% | 0.374 (1.002) | 0/48 | 0 | 32 (23) | 4 | 20/32 +10/16m | 0 |
| 9qz7cWBq | 44 (36, 44) | 75% | 93% | 2.976 (8.011) | 0/53 | 1 | 37 (33) | 2 | 37/37 +3/7m | 5 |
| FiFawHqx | 33 (33, 33) | 82% | 97% | 2.004 (6.013) | 0/39 | 1 | 27 (24) | 2 | 27/27 +3/6m | 4 |
| C5EMTGGE | 32 (32, 27) | 41% | 19% | 0.770 (0.810) | 0/32 | 1 | 21 (5) | 11 | 13/21 +5/11m | 1 |
| 53DnQU1d | 26 (19, 25) | 42% | 12% | 0.994 (1.493) | 0/26 | 1 | 16 (8) | 13 | 11/16 +6/10m | 7 |
| Anubis51 | 24 (11, 23) | 33% | 0% | 1.486 (2.243) | 0/25 | 1 | 8 (8) | 2 | 5/8 +13/16m | 2 |
| vcwCRZjr | 24 (23, 0) | 0% | 0% | 0.198 (0.241) | 0/24 | 1 | 19 (19) | 2 | 12/19 +4/5m | 3 |
| dKMjeGJ4 | 21 (11, 21) | 57% | 90% | 3.605 (8.017) | 0/23 | 2 | 15 (13) | 2 | 14/15 +4/6m | 2 |
| BGMfeBCJ | 20 (18, 0) | 20% | 0% | 0.061 (0.120) | 0/20 | 0 | 10 (5) | 7 | 0/10 +7/10m | 4 |
| 8ptvshQR | 15 (9, 15) | 47% | 53% | 1.337 (1.908) | 0/15 | 1 | 9 (9) | 2 | 6/9 +4/6m | 1 |
| GCfEnwFt | 13 (8, 0) | 15% | 0% | 0.050 (0.198) | 0/14 | 0 | 5 (0) | 480 | 1/5 +4/8m | 0 |
| CRkdFUJM | 12 (12, 1) | 67% | 25% | 0.250 (0.409) | 0/13 | 0 | 9 (6) | 3 | 8/9 +1/3m | 0 |
| 69d6eAno | 12 (12, 0) | 33% | 0% | 0.099 (0.100) | 0/12 | 0 | 11 (2) | 13 | 6/11 +1/1m | 7 |
| G8gTguf7 | 11 (0, 0) | 18% | 0% | 0.250 (0.251) | 0/19 | 4 | 4 (4) | 1 | 3/4 +4/7m | 0 |
| G9sQPg9E | 11 (0, 11) | 64% | 45% | 1.001 (1.002) | 0/11 | 5 | 2 (2) | 1 | 2/2 +5/9m | 0 |
| HVE8996r | 11 (0, 0) | 36% | 0% | 0.045 (0.093) | 0/11 | 1 | 5 (0) | 88 | 1/5 +3/6m | 0 |
| AEgTuy8L | 10 (6, 10) | 60% | 40% | 1.053 (3.024) | 0/10 | 3 | 7 (5) | 1 | 4/7 +2/3m | 0 |
| 8fN6NyEP | 10 (0, 1) | 0% | 0% | 0.351 (0.501) | 0/10 | 2 | 7 (1) | 32 | 2/7 +0/3m | 0 |
| 5xFhXswZ | 10 (0, 0) | 0% | 0% | 0.050 (0.050) | 0/10 | 0 | 5 (0) | 7 | 2/5 +2/5m | 0 |

The median slot gap to wallet 4's buy is 0 for all but 5xFhXswZ (+1): they land in its slot.

### 2-3. The top 15 by coins with a 0.45+ SOL early buy, full addresses, and the verdict (`out/verdict.txt`)

Criteria (`verdict.py`): (a) 20+ other-quote coins with a 0.45+ SOL early buy and a median early buy of 0.45+ SOL;
(b) median hold ≥ 60 s and at most 25% of sales within 5 s; (c) median frenzy ≥ wallet 4's (0); (d) failed ≤ 15% on
these curves and in its newest 1,000 signatures; (e) its share of coins on Oct 27-28 at least half wallet 4's (6.8%),
and a signature within 6 h of the activity read. Worth a full scoring = a, b, d and e. "ret" = the rough gross
return (`rank.py`, no fees; wallet 4's own is +0.193 with fees). "live" = failed share of its newest 1,000 signatures.

| wallet | coins (0.45+ other) | SOL | hold s | flips | frenzy | failed / live | Oct 27-28 | ret | verdict |
|---|---|---|---|---|---|---|---|---|---|
| `6anjqMeWigQFo5wpciARAunVQUXTqoat8w8fFWarCkpc` | 547 (314) | 0.50 | 480 | 6% | 0 | 0% / 2% | 52 | +0.186 | **worth a full scoring**: all five; timers 60/240/480/740 s; lands after wallet 4 |
| `AMDEmVocLtN5ji2gBY7BrmSHEyM5vt6TGszBbg4crMXg` | 135 (109) | 0.60 | 7 | 36% | 1 | 1% / 1% | 10 | +0.232 | no (b): sells in seconds |
| `Fhbh1DTUDKt6qu9zVg8Q5VgnZa1WWWbxBxG6pCoJoggA` | 62 (62) | 2.98 | 1 | 86% | 0 | 85% / 81% | 4 | +0.460 | no (b, d): 3 SOL front-runner, flips, spams failed sends |
| `9qz7cWBqYBP2TnGfzMmxX64G4PQip7HtogjPBBnMhWpw` | 44 (36) | 2.98 | 2 | 89% | 1 | 0% / 24% | 5 | +0.353 | no (b, d): front-runner, flips |
| `DsGJkPzFEQZuwy7JjZzPcJEyEfdC6StV7rarXG4ftRSA` | 65 (33) | 0.65 | 27 | 2% | 0 | 0% / 4% | 2 | +0.451 | no (b, e): sells at 20-45 s; 2 coins late |
| `FiFawHqxeTVBhv6YbqbLwDVuvokRpPUM1bNwAyxhGc6W` | 33 (33) | 2.00 | 2 | 89% | 1 | 0% / 4% | 4 | +0.384 | no (b): front-runner, flips |
| `C5EMTGGE87SqLyuvhShLDMj2jUBwqBLJAZF6ybK8Jyqw` | 32 (27) | 0.77 | 11 | 24% | 1 | 0% / 6% | 1 | +0.168 | no (b, e) |
| `53DnQU1dJZNHfKBpv2Lhsd4EBGNpwsF4tS13Egc1m6Tv` | 26 (18) | 0.99 | 13 | 50% | 1 | 0% / 2% | 7 | +0.171 | no (a, b) |
| `Anubis512ho5t7S6LNSwoxUWdeQmX2kf3RvZ8ApHHF5w` | 24 (11) | 1.49 | 2 | 100% | 1 | 0% / 2% | 2 | +0.598 | no (a, b): flips |
| `dKMjeGJ4Mk9S3hxdfTThvZ7exks2xMwWqSM5NvN2CTK` | 21 (11) | 3.60 | 2 | 87% | 2 | 0% / 0% | 2 | +0.232 | no (a, b): 3.6 SOL front-runner, flips |
| `9su3UPQW3txjtKDZAkf2Kdimp5tEb9TM6hnJrGC1U7pY` | 48 (20) | 0.37 | 4 | 72% | 0 | 0% / 2% | 0 | +0.186 | no (a, b, e) |
| `8ptvshQRZPRaRQBSCRxhHwbJFr6ktyUQ1SATDCLijkBW` | 15 (9) | 1.34 | 2 | 100% | 1 | 0% / 8% | 1 | +0.353 | no (a, b) |
| `G9sQPg9Eimkwe72w1xH1tPUc9RFNuK6Ufw5AyWy6j7ob` | 11 (0) | 1.00 | 1 | 100% | 5 | 0% / 1% | 0 | +0.497 | no (a, b, e): SOL-priced coins only |
| `AEgTuy8Lg4wfnjm285mk3P2k1p39ofqNXk8b5VtYhdCs` | 10 (6) | 1.05 | 1 | 71% | 3 | 0% / 22% | 0 | +0.137 | no (a, b, d, e) |
| `CUQqcZZGr8QLjEzMpxUZyiZirBujE2Y9yZDyfCRw1CAB` | 9 (7) | 3.00 | 2 | 100% | 2 | 0% / 4% | 0 | +0.438 | no (a, b, e): quiet since Oct 20 07:31 UTC |

(The "coins (0.45+ other)" column is `verdict.py`'s `big`: other-quote coins with a 0.45+ SOL early buy.)

### The four named in wallet-check.md

| wallet | coins | at C+0 / C+1 / later first buy | in wallet 4's path | before W4 | SOL | hold s | won | verdict |
|---|---|---|---|---|---|---|---|---|
| 6anjqMeW | 547 | 230 / 317 / 51 (C+2..4+) | 601 coins | 1% | 0.50 | 480 | 128/357 | above |
| AMDEmVoc | 135 | 67 / 68 / 5 | 129 | 18% | 0.60 | 7 | 53/85 | flipper |
| Fhbh1DTU | 62 | 41 / 21 / 2 | 70 | 94% | 2.98 | 1 | 54/56 | front-runner flipper; 85% of its transactions on these curves failed |
| dKMjeGJ4 | 21 | 12 / 9 / 0 | 13 | 90% | 3.60 | 2 | 14/15 | front-runner flipper |

Fhbh1DTU was called "a micro-buy bot (0.002-0.003 SOL buys)" in wallet-check.md §4b. On these 62 coins its early
buys are 2.98 SOL (median) and its first sale comes 1 s later. Its micro buys are elsewhere.

### 6anjqMeW in detail (`out/tiers.txt`)

| split | coins | sales seen | won | median hold s | gross return |
|---|---|---|---|---|---|
| buys < 0.45 SOL | 184 | 107 | 41% | 740 | +0.185 |
| 0.45-0.8 SOL | 233 | 155 | 35% | 480 | +0.238 |
| 0.8-1.5 SOL | 130 | 95 | 31% | 480 | +0.137 |
| P1 (Oct 19-22) | 318 | 221 | 30% | 480 | +0.184 |
| P2 (Oct 23 → 27 00:20) | 180 | 105 | 43% | 740 | +0.150 |
| P3 (to Oct 28 14:54) | 49 | 31 | 55% | 110 | +0.333 |
| other quote | 484 | 332 | 36% | 480 | +0.219 |
| SOL quote | 63 | 25 | 28% | 249 | −0.034 |

First-sale holds: 0-6 s 21, 6-60 s 30, 60-300 s 92, 300-900 s 170, 900-1,800 s 44, over 1,800 s 0. Most common:
480 s (40), 740 s (39), 240 s (31), 60 s (15).

## Limits

- **Sales after the window come from wallet 4's path**, which is sampled on 330 of the 741 other-quote coins and ends at
  wallet 4's sale. A sale can be missed. So "sales seen" undercounts, and for the flippers most "no sale seen" coins
  are probably missed sales, not holds (AMDEmVoc: 50 not seen, only 6 on a complete path).
- **The win and return figures are gross estimates**, no fees, and a partial first sale counts as a full one. The marked
  part uses wallet 4's exit price, which is not the wallet's own exit. They rank wallets roughly; they are not P&L.
- **Only wallet 4's coins are seen.** A wallet's own strategy on its other coins (6anjqMeW: 85% of its buys,
  wallet-check.md §4b) is not measured here. That is the full scoring.
- The quote names in `rank.txt` come from `_quote.json`; `?` = not listed there (SOL-priced coins and some others).
- Activity (`out/activity.txt`) is one page of 1,000 signatures read Oct 28 ~23:14 UTC; it counts every signature
  touching the wallet, not only its trades.
