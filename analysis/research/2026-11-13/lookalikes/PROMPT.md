# Find wallets like wallet 4 that we can copy (prompt for a new session)

Repo `xin10ylop/copy2`, branch `claude/magical-einstein-k78idp`. Read `CLAUDE.md` first and follow it (public repo:
no keys, no RPC URLs with keys, no IPs; plain words, tables, Beirut time = UTC+2; every number needs a source; the
owner runs box commands, you can't reach the box). Then read, in this order:
`analysis/research/2026-10-29/wallets/README.md` (the Oct 29 search: six wallets scored, none copyable, and why),
its `score/README.md` (the scoring pipeline, `run.sh`, `marks.py`, `row.py`), `neighbours/` and `creates/`,
`analysis/research/2026-11-12/siblings/README.md` (wallet 4's operator: no other trading wallet),
`analysis/research/2026-10-31/since_stop/README.md` (the current model and the latest results), `01-who-it-is/README.md`,
`docs/20-long-copy.md` §1-3 and `docs/21-copier.md` §1-2.

## The goal

Find one or more Solana wallets that trade like wallet 4 (`H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg`) and that our
bots can copy at a profit **at our real landing**. Score each candidate the same way wallet 4 was scored, and say
plainly: copy it, re-check it later, or no.

## What makes wallet 4 copyable (the profile to match)

- **Big launch buys of pump.fun coins priced in another token** (WBTC, other pump quotes), 1.45+ SOL each (median
  1.60, quartiles 1.5 / 1.6 / 1.98 over Oct 29 - Nov 12; `since_stop/out/size_signal.txt`). Every big buy comes within
  2 s of the coin's create, with under 5 curve trades before it, and it is its only buy of that coin
  (`2026-10-28/more/README.md` §ii).
- **It holds long enough for a copy to ride.** One buy, one sale of everything: take profit near 2.5x the price its
  buy left, otherwise a timer near 30 min; in October 74% were held to the timer (`2026-10-29/wallets/README.md`). It
  now sells earlier more often (all three coins on Nov 12 after 179-303 s; `since_stop/out/his_vs_ours_nov12.txt`).
  About 10-20% of trips reach 2.5x and they carry all the profit.
- **About 100 copyable buys a week**, +10.8% on its own money Nov 5-12 (+21.3 SOL on 196.8), +23.2% the week before
  (`since_stop/out/why_weeks.txt`).
- **It does not win by landing first or by selling into the launch frenzy.** Every rejected wallet on Oct 29 did: they
  sold in the first seconds (flippers, 1-20 s holds) or land ahead of everyone, so a copy buys what they sell.
- Its fingerprint (to tell its operator apart): durable nonce first in every transaction, tips of exactly 1,067,000 or
  1,010,000 lamports. Only `8LBfYVFK...` shares it, and it is a pool volume farmer, not a target.

## Our landing (what a copy gets)

- The long copy (Frankfurt box, Triton Yellowstone gRPC feed, Nozomi `fra2` sender) lands **in the target's own block**:
  Nov 12 live, 3 / 7 / 8 trades on the coin between its buy and ours (`since_stop/out/live_nov12_vs_model.txt`); Oct 28,
  5 of 7 sends in its slot, 2 in the next (`03-strategy-A-long-copy/deploy-frankfurt.md` §6). **Score candidates at
  landing 4 and 8 trades after their buy, and one block late** (`model.py` `n` = 4, 8, `"slot+1"`).
- The copier (Jupiter, any venue) is slower: it waits for a Jupiter quote. It has never sent a live trade; score its
  candidates one block late and two blocks late, and say the landing is unmeasured.
- A buy price limit applies: no buy above 1.25x the price the target's buy left (`max_premium`, `pos::buy_min_out`).
  Wallets whose buys move the price far up (big buys on thin curves) lose more copies to it; count the refusals.

## What we can and can't copy

| Can | Can't (or not with the long copy) |
|---|---|
| Pump.fun curve coins priced in SOL or in a token with a canonical PumpSwap pool against wSOL or WBTC: routes copied / pool+curve / curve, through pump's `multi_hop_swap` (docs/20 §1) | Coins priced in tokens with no canonical pool (PUMP, CARDS, xStocks, USDC ... = wallet 4's "part B"): only the copier, through Jupiter |
| Buys paid from wSOL or from a float we hold (WBTC `3NZ9JMVB...`); a buy paid in another token needs its own float | Buys whose SOL value can't be priced (paid in an unpriced token): skipped |
| Holds of minutes (take profit, timers, the target's own sale) | Holds of seconds: we land after the frenzy and buy their sale |
| Meteora DBC / DAMM v2, Raydium LaunchLab / CPMM, other launchpads: the copier only (Jupiter quotes them; docs/21 §1) | Graduated coins at buy time, if the long copy is meant (the copier can) |
| | Wallets that win by landing first (slot 0 snipers ahead of everyone), bundles, the dev's own buys, wallets with failed-transaction shares far above wallet 4's 2.9% |

## Where to search (not covered yet)

The Oct 29 search covered: early buyers of wallet 4's coins Oct 19-28, and one day of creates with a launch frenzy.
Its README lists the gaps. Search these:

1. **New wallets since Oct 29** on wallet 4's coins: every buyer of 1.45+ SOL within the first ~5 s of each coin wallet
   4 bought Oct 29 - now (the coin list is `since_stop/routable.json`, rebuilt by `build_rows.py`; the cached paths in
   `SPD/cache` and `paths.json.gz` have every trade in the first 31 minutes). Rank by coins shared and by hold time.
2. **Quiet coins too**: a multi-day scan of pump creates priced in another token, without the frenzy filter, listing
   wallets that buy 1+ SOL at create+0..+2 s and **hold 2+ minutes** on most coins.
3. **Other launchpads** for the copier (Meteora DBC, Raydium LaunchLab, letsbonk): the same profile there.
4. **Re-score `3dwZP6T8`** (the nearest on Oct 29: 1.9 SOL launch buys, a 272 s timer; break-even then). Note: it
   started Oct 24; it may have changed.
5. Wallet 4's own coins: wallets that buy within a second of wallet 4 on many of its coins and hold (possible
   followers or the same strategy run elsewhere).

Keep only wallets with **at least 7 days of history and 20+ big buys a day**, and drop flippers early with the cheap
marks before any backtest (`score/README.md` "cheap marks").

## How to score (same yardstick as wallet 4)

- The full pipeline: `score/run.sh W fetch|score|band LO`, `row.py W`; the backtest model `since_stop/model.py`
  (exact constant-product quotes on the trade events, the cautious price model q, 0.3% a pool hop each way, 0.0026 SOL
  a round trip, the buy limit 1.25). Pick rules on the earlier half of the data, score on the later half, and report
  every result **with and without each half's best 2 trades**.
- **The candidate's own real result** from its own transactions (SOL in and out per coin, other tokens at its own swap
  rate; `since_stop/his_week.py` shows how), and the raw model run on the candidate itself at landing 0 behind its own
  sale: the gap between the two is the model's caution for that wallet (9.1 points for wallet 4 Nov 5-12;
  `since_stop/vs_him_week.py`). Report our copy as raw and with that gap added back.
- Our copy at 1 SOL, 2 open, landings 4 / 8 / one block late; exits: hold with take profit 2.5 and 30 min, and sell
  behind its sale; plus the best of a small exit grid picked on the first half only (`since_stop/exit_search.py`).
- Overlap with wallet 4: how many of its buys are the same coins (a second wallet on the same coins adds little).
- Fetching: `analysis/research/2026-10-28/fetch/` uses the public RPC; the Oct 29 search used the Triton endpoint. If
  you need a keyed RPC, ask the owner for it through the environment's secure credential form; never put a key in a
  file, a commit or the chat.

## The deliverable

A folder `analysis/research/2026-11-13/lookalikes/` with the scripts, `out/` files and a README: where you searched,
how many wallets each step kept, the scoring table (wallet 4 as the reference row, the same columns as the Oct 29
table), and a plain verdict per wallet. Commit and push to `claude/magical-einstein-k78idp`. Then tell the owner in a
few lines: found or not, how much a copy would have made a week at 1 SOL (raw and corrected), and what it would take
to run it (long copy or copier, floats needed, stake).
