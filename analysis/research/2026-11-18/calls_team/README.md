# calls.team: copying public Telegram calls, scored on chain (Nov 18)

The owner: "go deep on calls.team". calls.team lists public Telegram caller channels' calls (time, coin, order among
callers). Its hit rates use only "measured" calls (solearlytrending: 188 of 2,095 a week) and a call's best-case peak
on 15-minute candles, so they say nothing about a follower's result. This study scores what WE would make.

Run order (SP = scratchpad; RPC_URL from the environment, never printed):
```
python3 -I ct1_fetch_calls.py SP kolsignal solearlytrending solhousesignal alphax100callers gemsmineeth klevercalls onchainalphatrench pnuthiddengems pumpdotfunalert seekrtrending
RPC_URL=... [DELAY=3] [PAGES=60] python3 -I ct2_score_calls.py SP > out/ct2.txt
```
- `ct1`: each caller page shows its latest 50 calls (no pagination): 490 calls on 372 coins, Nov 15 21:26 - Nov 18
  11:17 UTC, the ten callers that most often call first. Read for reference, a pause between pages.
- `ct2`: for each call on a pump coin at least 1,000 s old, the coin's trades from 2 min before to 16 min after the
  call: on its bonding curve, or in its PumpSwap pool when it had graduated (`2026-11-18/pools/p1_fetch.py`'s reader,
  a pool row put in the curve's constant-product form, 30 bps a trade). Our 0.5 SOL buy DELAY s after the call, landing
  4 / 8 trades later or in the next slot (their mean), 0.0345 SOL a round trip; every exit of e8 with no "its sale"
  (12,960 settings with the price limit). Halves by time.

**Result** (`out/ct2.txt`; 229 of 401 calls modelled: 88 had no trade near the call on the curve or the SOL pool,
84 are priced in another token, the busiest coins included with deep paging):

| calls | copies | settings positive on both halves | best with hindsight |
|---|---|---|---|
| all | 229 | 0 of 12,960 | −6.10 SOL (−5.3% a copy) |
| called first (#1) | 113 | 152 (1.2%) | +0.94 SOL (+1.7%), w/o 2% −1.28, P 65% |
| called later (#2+) | 116 | 0 | −4.07 SOL |
| on the curve at the call | 128 | 0 | −2.25 SOL |
| in the pool at the call | 101 | 0 | −1.18 SOL |

The reaction delay hardly matters (`out/ct2_delay.txt`, before the busy coins: first calls best +1.80 at 0 s, +0.83 at
10 s, +1.50 at 30 s, all negative w/o 2%). The first call is slightly better than the rest; every later call buys from
those earlier. No copyable edge in these callers.
