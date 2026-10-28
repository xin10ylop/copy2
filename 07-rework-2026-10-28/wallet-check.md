# Wallet 4 (H9kuqGKN) on chain: who it is, who it is linked to (Oct 28 2026)

Wallet 4 = `H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg`. Checked Oct 28, about 15:00-15:45 UTC, through the Triton
RPC. Times are UTC, with Beirut beside them at UTC+2, the repo's convention. Lebanon's summer time (UTC+3) ran until
Sunday Oct 25, so for Oct 17-24 a Beirut wall clock showed one hour more than the Beirut column here.

Scripts and their printed outputs are in `analysis/research/2026-10-28/wallet/ (data: data/datasets/w4wallet.tar.xz)`
(below: `wallet/`). Each number names the script that printed it and the output file (`*.out`).

## The answer first

**Is it one independent bot? It is one bot, but it is not a new, unconnected trader.** Wallet 4 is very likely the
next wallet of an older bot wallet, `HxcdEi6C`. That wallet traded from Jul 27 to Oct 17 (62,231 signatures). The same
operator emptied it on Oct 17, moved 60 SOL through a public privacy pool, and started wallet 4 the same evening. The
pool hides the direct link on purpose. The evidence for a link is circumstantial but strong:

| Evidence | Detail |
|---|---|
| Money and timing | HxcdEi6C put **10 + 50 = 60 SOL** into the pool at 17:14 and 17:20 UTC on Oct 17. Between 17:18 and 22:43 the pool paid out **10 + 10 + 20 SOL to 8h5eizMg** (wallet 4's first funder) and **20 SOL to wallet 4**: 60 SOL as well. HxcdEi6C stopped trading at 15:18 that day and was empty by 23:58. |
| The same software | All three wallets start most transactions with a durable nonce and pay the same two tip sizes, **1,067,000 and 1,010,000 lamports**, to the same set of senders (Helius, Speedlanding, Astralane, Jito, Nozomi). They also use the same instruction sequence. None of 113 other wallets trading next to wallet 4 used those tip sizes, and neither did 303 other tippers or 249 pool recipients. |
| The same trading | HxcdEi6C bought pump coins, mostly coins priced in other tokens, in about 1.0 and 1.5 SOL sizes (median 1.003, p90 1.523), like wallet 4. |

Around HxcdEi6C the operator's other wallets are plain to see: a funding wallet `GEcF6sHy` (still holds 95.2 SOL) and a
"bank" wallet `MCquEenF`. On Oct 17 HxcdEi6C sent out 288.8 SOL: 60 into the privacy pool, 39.2 to three exchange deposit
addresses, 140 through a cross-chain swap, and 49.6 to MEXC through an intermediate. The same evening MCquEenF sent out
190 SOL: 100 to GEcF6sHy, 50 to a new wallet that staked it, 11.2 to an exchange, 10 to MEXC and 18.8 elsewhere.

**Other answers:**

| Question | Answer |
|---|---|
| A sibling trading the same rule now? | **None found.** No wallet near its buys, among pool recipients or in a tip sample has its fingerprint. |
| Does it follow a leader? | **No.** On 50 random other-token coins it bought in the coin's **create slot (25 of 47 measured) or the next slot (22 of 47)**. Its 1.45+ SOL buys come at a median **1.08x** the launch price. The buyer just before it is a different wallet almost every time. Nobody we could copy instead sits in front of it. |
| Wash trading with coin creators? | **No sign.** It never created a coin (0 of 4,998 buys). The coins it buys have 3,109 different creators. It never sent SOL or tokens to anyone except the privacy pool. The sampled creators are funded from exchanges (Binance, KuCoin). |
| A shared funding hub with our other targets? | **No.** Its whole funding is the privacy pool chain. None of the wallets in docs/19 appears in it. |
| Copiers of it? | Fast buyers land right behind it. **6anjqMeW** traded on 30 of 40 sampled coins and bought in its slot or the next on 27 of them. It is not a pure copier: only 15% of its buys are wallet 4's coins. AMDEmVoc traded on 11 of 40. |
| Is it winding down? | **Its copyable buys are falling.** Its 1.45+ SOL other-token buys ran at 56-112 a day on Oct 19-25, then 35 (Oct 26), 32 (Oct 27) and 11 in the 15 hours of Oct 28. On Oct 27 13:59 UTC it put **5 SOL back into the privacy pool**. That is its only withdrawal ever. Its predecessor's last days looked like this too: big withdrawals, then a switch to a fresh wallet. |

**Red flags for copying:**
1. **Hidden funding by design.** The operator uses a privacy pool to rotate wallets.
2. **Rotation risk.** Wallet 4 may be replaced the way HxcdEi6C was, with no warning on chain, and the 5 SOL into the pool
   may be a first step. We would then copy a wallet that has stopped.
3. **Its copyable flow halved after Oct 25.**

**What this changes for strategy A:**
- **Watch for a rotation.** Alert when wallet 4 makes no 1.45+ SOL other-token buy for a few hours, or sends large
  amounts out (to the pool `4AV2Qzp3`, or to anything else).
- **A successor can probably be found by its fingerprint:** a durable nonce first, tips of exactly 1,067,000 or
  1,010,000 lamports, and about 1.5 SOL buys of other-token coins in the create slot or the next. A scan for that
  fingerprint among early buyers of such coins could find the next wallet. This is not built yet.
- **There is no leader to copy instead, and no sibling to add.**
- **Competition at entry:** 6anjqMeW and others land in its slot or the next. Our Ohio copy fills after them, so the paper
  fills are optimistic, as already known.

## 1. Funding history (since its first transaction)

**Its whole history is short:** 1,717 signatures from Oct 17 19:22:57 to Oct 18 23:59:52 UTC, plus 20,476 from Oct 19
to Oct 28 14:54, so **22,193 in all**. No sampling was needed. Everything was read.
(`page_sigs.py` → `page_sigs.log`: "1717 ... END: short page"; one more call before the oldest signature returned 0.)

**First transaction:** Oct 17 2026 19:22:57 UTC (21:22:57 Beirut), sig
`5MtwbJvhEFcreyY8zDUw2wwStvHepsZYPBmqaPSJ6m7q7UhAsLTKx1eRDtTmLvGvaWbKhsDMs1g4fUPxy4sz5rgW`:
**39.52008 SOL** from `8h5eizMgJ14dpEht6YfcMwYhZwiD2q88BFM4FNPdSbsx` (balance 0 → 39.52008; `old_scan.py` → `old_scan.out`).

**Every SOL movement in or out of 0.5 SOL or more, since the beginning.** This counts any route: the wallet's SOL plus
wSOL changed by 0.5 or more while no other token moved (`netflows.py` → `netflows.out`, 3 transactions):

| UTC (Beirut) | In/out | SOL | Counterparty | Sig |
|---|---|---|---|---|
| Oct 17 19:22:57 (21:22) | in | 39.5201 | 8h5eizMg (plain transfer) | `5MtwbJvh...4sz5rgW` |
| Oct 17 22:43:28 (Oct 18 00:43) | in | 19.924 (20.0 less the pool fee) | privacy pool `4AV2Qzp3N4c9RfzyEbNZs2wqWfW4EwKnnxFAZCndvfGh`, program `9fhQBbumKEFuXtMBDw8AaQyAjCorLGJQiS3skWZdQyQD`, relayer `W97m2N12NdSgWu3bppYCPHdXNwz15SDUZNoD5jNFaqH` paid the fee | `2JjAMgbHXS1nSG827fHw9xTogj1KDgzyQgnABavKqbBx3etqcitEARhcjazmgamGbTC1DDPrHXs7NjS4BZQi914h` |
| Oct 27 13:59:22 (15:59) | out | 5.0 (5.0016 with rent and fee) | into the same privacy pool, signed by wallet 4 | `375CX8sjWJWjBu6KDvK1MyVHPFfc7fxdUZboRUSrJSw58pERS3W3Ks3BUtnKXtR8bg8apEBa2n8NgLMNbvqnYLGD` |

- **Totals: in 59.444 SOL (39.520 + 19.924), out 5.0 SOL.** Nothing else of 0.5 SOL or more, either way, ever.
- Since Oct 19 there is only one other plain SOL transfer of 0.01 SOL or more: **+0.0537 SOL** from
  `BuTGxbmwW3ZB7qnyjCXfkeAXsU7RvA78jopcybYtopMm` on Oct 27 01:51:42 UTC (dust; sig `5e4BwbRywjcWauNB8VEGv9AV...`). The
  other 268 plain transactions with a gain of 0.01 or more are wallet 4 closing its own token accounts (25 of 25 sampled
  are `CloseAccount`; `cand_sol.json`).
- Before Oct 19, small transfers came in from 4 other addresses (8ZM6RgmJ, DSEd1cTM, BxkkMvLG, 31BEsfbj), each under
  0.05 SOL (dust).
- The privacy pool program's name is not in the repo's labels. Its transactions log `Instruction: Transact`, create
  2 nullifier accounts each and pay withdrawals through one relayer. I believe it is the "Privacy Cash" pool, but that
  is my recognition only and was not verified.

**Counterparties over 5 SOL:**

| Counterparty | What it is | Funds other pump bots like wallet 4? |
|---|---|---|
| **8h5eizMg** | A one-day wallet with **114 signatures, all on Oct 17, 17:18-19:25 UTC**. It was funded only from the privacy pool (9.959 + 9.959 + 19.924 SOL at 17:18, 17:30 and 17:38; sigs `eze2qsa2hhebB4cfSLCqiWtp8HoCYh5MBKDzHw5fD5R81FapbaX5qmokMy6msoxKTTDSy9t1f6PgjmA4u6c8U2Z`, `4bgFgnh6jEFbMG4pH9nYZniccr2adyHCnaSfcdDSmYLZCFLo2eUdmh7GLb2Eppik3gHmmuPzU6ZLogaQ5vbokbEt`, `4oeMz3duaZUCtxfXKsgFUQXU8EZekEZUtdx4aGqcqJk82UNG8S5pETxizqoQpLRWURvyCTcD7TyDQpLAY5QujoSx`). It **traded pump coins itself from 17:57 to 18:52** (PumpSwap SellV2, multi-hop curve swaps, Jupiter; buys of 1.5 / 1.6667 / 0.75 SOL). Then it sent everything, 39.52 SOL, to wallet 4. Balance now 0.0064. (`walletflows.py 8h5eizMg`, `funder.py` → `funder_8h5eizMg.out`, `hist_8h5eizMg.out`) | **No.** Its only plain transfer out is the 39.52 SOL to wallet 4. It is a test wallet of the same bot (same fingerprint, §4a). |
| **Privacy pool 4AV2Qzp3** | A public pool. About 10,000 transactions from Oct 16 13:12 to Oct 28 (`pool_sigs.py` → `sigs_4AV2Qzp3.json`). In my two windows: 455 deposits and 733 withdrawals, every withdrawal paid by the relayer W97m2N12 (`pool_tx.py` → `pool_tx.out`). Deposits go up to 383 SOL. | Not as a hub. It pays everyone. Its recipients were checked for wallet 4's fingerprint (§4a): none matched. |

## 2. The 10 days (Oct 19 00:00 → Oct 28 14:54 UTC) in detail

**SOL and token transfers, all 19,981 landed rows plus 495 failed transactions:**

| What | Count | SOL to wallet 4 | Source |
|---|---|---|---|
| Plain SOL deposits | **0** | 0 | `netflows.out` |
| Withdrawals | **1** (privacy pool, Oct 27 13:59) | −5.002 | `netflows.out` |
| pump.fun `DistributeFeeToHolders` payouts (fee payer pump's distributor `HckQ93Xqjjo8mwt5pNPWvyCTZXQZ858rvzmm7ZRrZg9t`; tokens too: WBTC 593, PUMP 431, CARDS 118 ...) | 1,891 | +0.755 | `nonsigner.py` → `nonsigner.out` |
| Spam with no balance change (program BYdq7NJX, all on Oct 27, paid by `DeFG8i8zoJ3hN155nmvLq266ZVxWmNgRaTz5KQVHfe2S`) | 1,270 | 0 | `nonsigner.out` |
| Dust SOL: 14 txs from 14 different addresses (one of them the 0.0537 above), and 2 txs through program 6keGXHZ6 from `7fWGS4jL` | 16 | +0.073 | `nonsigner.out` |
| Tokens received by plain transfer: airdrops (NTRND..., C5xph2yL..., SAto..., GGHv... from `A219A8AXwq9Jbqy4ckxn87eEhouc5MYfcCvErCNkHodL`; 6Sij6nZ4 from CPgPrxLx; DyczZx86; Hw9s2Si2), and 0.1225 DJTu from 8zWrsZPo | 20 | 0 | `cand_tok.json` (script output in the session) |
| cNFT/offer spam (Bubblegum, CcmRKTuZ `MakeOffer`), memo spam | 13 | 0 | `nonsigner.out` |
| **Tokens sent to another wallet** | **0** | | all 20 plain token rows are receipts |

Nobody else ever paid for one of wallet 4's trades: 0 of the 3,210 transactions paid by others contain a trade by wallet 4.

**Its SOL balance** (native SOL only; the tokens it holds are not valued; `balance.py`, `reconcile.py` → `reconcile.out`):

| Point | SOL |
|---|---|
| Oct 17 19:22:57 after funding | 39.520 (+19.924 at 22:43) |
| Oct 19 00:00 UTC | **57.871** |
| Oct 27 00:40 UTC | **467.683** (the docs' 467.7 ✓) |
| Oct 28 00:00 UTC | 495.452 |
| Oct 28 14:54:39 UTC (its last row, chain post-balance) | **569.533** (rows plus failed fees rebuild it exactly) |
| Oct 28 15:13:33 UTC getBalance | 564.382 (the brief's 570.379 at ~15:00 is a nearby reading; it moves with open positions) |

**What moved it from Oct 19 00:00 to Oct 28 14:54 (+511.662 SOL):**

| Part | SOL |
|---|---|
| Its trading and everything else it signed (native; includes turning held tokens into SOL) | +505.833 |
| Rent back from closing its own token accounts | +12.857 |
| pump holder-fee payouts and dust (paid by others) | +0.828 |
| Fees of its 495 failed transactions | −2.854 |
| 5 SOL into the privacy pool | −5.002 |
| **Total** | **+511.662** |

**So: no deposits at all since Oct 19. All of the rise is trading, and 5 SOL went out.**

Two corrections to the docs:
- The "+11.9 deposited" in 01-who-it-is is **not deposits**. It is the rent back from closing token accounts, plus
  holder-fee payouts. That is the ledger's `xfer` list: 231 of its 257 rows were signed by wallet 4 itself.
- The docs' "+412 native" counts landed transactions only (+412.22 to Oct 27 00:40). The chain's change is +409.81,
  because 433 failed transactions cost 2.41 SOL.

Since birth: 59.44 SOL in and 5.0 out, and 569.53 SOL at Oct 28 14:54. On Oct 17-18 its balance was about flat
(59.44 → 57.87).

## 3. The router program: wallet 4 does **not** use FLASHX8D

- `FLASHX8DrLbgeR8FcfNV1F5krxYcYMUdBkrP1EPBtxB9` appears in **0 of wallet 4's 19,981 rows** and in **0 of the 1,218
  transactions** in the earlier fetch (`w4live/tx`). The brief's premise is wrong. The README note on FLASHX8D is about
  other traders' transactions in the coin tapes (e.g. `coins/6y9aDagF/`), not wallet 4's.
- **What FLASHX8D is:** Axiom Trade's router. In 400 random transactions from its last 5,000 signatures (5,000 in
  196 s, Oct 28 15:16-15:19 UTC), **391 carry a `jitodontfront…TradeWithAxiomDotTrade` account**. There were **287
  distinct fee payers in 400 transactions**, 360 of them touching pump or PumpSwap. It is a public retail terminal.
  Wallet 4 appears in 0 of them. (`flash_sigs.py`, `flash_payers.py`; only this 3-minute window was measured, not a
  per-hour count.)
- **What wallet 4 actually calls** (programs per row, `progs`): pump.fun directly (11,654 rows), Jupiter v6
  `JUP6LkbZ...` (4,274), PumpSwap (2,695), and other AMMs through Jupiter (Whirlpool, Meteora ...). No terminal's router
  or marker account was seen, so it builds its own transactions.

## 4. Siblings and neighbours

### 4a. Shared funders, shared destinations, and the wallets behind the pool

**The chain on Oct 17 2026** (UTC, Beirut = +2; `walletflows.py`, `profile.py`, `hxcd_first.py`, `pool_tx.out`):

| UTC | Beirut | Event | Sig (start) |
|---|---|---|---|
| 15:18:44 | 17:18 | HxcdEi6C's last swap. It stops trading. | `5q7m5RN6PAC9h18kj9sx` |
| 17:14:03 | 19:14 | HxcdEi6C → privacy pool **10 SOL** (signed from a Phantom-style wallet: the Lighthouse program L2TExMFK is in the tx) | `33tz9oP4vhtivrWB4ihR` |
| 17:18:39 | 19:18 | pool → 8h5eizMg **10** (9.959) | `eze2qsa2hhebB4cfSLCq` |
| 17:20:54 | 19:20 | HxcdEi6C → pool **50 SOL** | `38oEpCQKFhfimJpawzjB` |
| 17:30:51 / 17:38:09 | 19:30 / 19:38 | pool → 8h5eizMg **10** and **20** | `4bgFgnh6...`, `4oeMz3du...` |
| 17:57-18:52 | 19:57-20:52 | 8h5eizMg trades pump coins | |
| 18:38-18:44 | 20:38-20:44 | HxcdEi6C → 3 exchange deposit addresses 11.21 / 11.20 / 16.80 SOL (they forward to collection wallet `5yASLjtNssGXDv6bR9e71WXKxRymDiUzbgkGPqkQNgRn`, unlabelled) | `mfZjp7Tg...`, `34AFQwNK...`, `2FFVYt6w...` |
| 19:22:57 | 21:22 | 8h5eizMg → **wallet 4, 39.52 SOL** | `5MtwbJvh...` |
| 19:24:57-19:25:06 | 21:24-21:25 | wallet 4 creates **12 durable-nonce accounts** | e.g. `5oBxFLHU8pBjNGvrm1iE` |
| 19:33:30 | 21:33 | wallet 4's first swap | `2UXhzfCrQ9xr7nv7BH7o` |
| 21:48 / 21:53 | 23:48 / 23:53 | HxcdEi6C → 50 + 90 SOL through a cross-chain swap program (J88B7gma, `XSwapNative`; to 3tJ67qa2, a busy solver vault) | `4MunAtQA...`, `wh2vUqbs...` |
| 22:43:28 | 00:43 Oct 18 | pool → **wallet 4, 20** (19.924) | `2JjAMgbH...` |
| 23:45 / 23:58:51 | 01:45 / 01:58 Oct 18 | HxcdEi6C → 25 + 24.57 SOL to 8DapbAzh, which forwards to **MEXC** hot wallet ASTyfSim (labels: "MEXC 1"). HxcdEi6C is empty. | `sTVK1avM...`, `5Sezfo8E...` |

Between HxcdEi6C's deposits and 17:40 UTC, the only pool withdrawals of 9 SOL or more were the three to 8h5eizMg. But in
the same minutes HqrBi21i deposited 10 + 5 SOL, and GhuZyj7c withdrew 39.7 SOL in eight pieces of 2.9-7.0 SOL
(`pool_tx.out`). So the amount match is suggestive, not unique. The fingerprint is what makes the link strong.

**The fingerprint, compared** (`fingerprint.py 300 ...` → `fingerprint.out`; random own transactions; wallet 4 from its
newest 3,000 signatures, HxcdEi6C from its last 2,000, 8h5eizMg all):

| | wallet 4 | 8h5eizMg | HxcdEi6C |
|---|---|---|---|
| Own transactions in the sample | 180 | 91 | 287 |
| AdvanceNonceAccount first (durable nonce) | 101 | 36 | 215 |
| Tip of exactly 1,067,000 lamports | 40 | 18 | 78 |
| Tip of exactly 1,010,000 lamports | 32 | 7 | 52 |
| Tip senders | Speedlanding 27, Helius 19, Jito 18, Astralane 12 ... | Helius 8, Speedlanding 7, Astralane 6 ... | Helius 62, Speedlanding 52, Astralane 20, Jito 8, Nozomi 7 ... |
| Most common top-level sequence | System ×3, Token, pump (30) | same (14) | same (49) |
| Most common CU limit | 6,159 (13) | 7,809 (6) | 6,159 (17) |

**How rare those tip sizes are:**
- 0 of 113 other fee payers (448 transactions) on the 40 curves next to wallet 4's buys (script output in the session,
  from `neigh.json`).
- 0 of 303 payers in 684 recent tips to 18 Helius, Astralane and Jito tip accounts (a 1-minute window; `tipscan.py` →
  `tipscan.out`).
- 0 of 249 privacy-pool recipients (`fpscan.py` → `fpscan_w1.out`, `fpscan_w2.out`).

Durable nonces by themselves are common; the tip sizes are not.

**The operator's other wallets (the HxcdEi6C side):**

| Wallet | Role | Facts |
|---|---|---|
| `HxcdEi6CWzQtPCmM8E2maEZ3oYVGZxESqCWU1iPzmhVW` | **wallet 4's probable predecessor** (bot) | 62,231 signatures, Jul 27 16:20:16 → Oct 17 23:58:51. Funded with 0.6 SOL by GEcF6sHy (`31awAVDUu3nPs7qb7hQd...`) and trading pump 7 minutes later. 163.6 SOL on Oct 15 22:30. Sent 190 SOL to MCquEenF on Oct 14 (`3kCXQd9T...`). Balance now 0. (`pool_sigs.py` → `hxcd_page.log`; `hxcd_first.out`; `walletflows.py`) |
| `MCquEenFvqN2YGu4bfnen7hUVqXfSSqsdR9DbLaT4GD` | the operator's "bank" | 43 signatures, Sep 2 → Oct 17. Got 264 SOL from HxcdEi6C (6, 7, 8, 15, 8, 30, 190). Sent 168.0 SOL to GEcF6sHy over Sep 24 → Oct 17 (100 of it on Oct 17, `j7j9q8Nn...`) and 6 back to HxcdEi6C. On Oct 17 it also sent 11.2 SOL to an exchange deposit address (→ 5yASLjtN), 50 to a new wallet that staked it (BJjTnf2B), 10 via 8DapbAzh to MEXC, and 18.8 to 6SWyKzv5. Balance 0. |
| `GEcF6sHyGDLrJ6NYzj2uEv2hRbSpwvLmmvm1k8A9VGhc` | personal / root wallet | 6,819 signatures since Mar 24. Makes micro pump buys (0.002-0.027 SOL, SOL-priced coins) and sends 1-10 SOL to many addresses through a Phantom-style wallet. **Holds 95.22 SOL now.** Last active Oct 25 16:02. **Not a copy target:** different strategy. |

**Wallets sharing a funder or a destination with wallet 4 itself:** none, besides the chain above. 8h5eizMg funded only
wallet 4. Wallet 4's only destination is the privacy pool.

**Did the 5 SOL wallet 4 put in the pool on Oct 27 fund a new bot?** It is not visible. The 99 recipients of 3 SOL or
more in the following 25 hours show no wallet-4 tip size in their newest 15 own transactions (`fpscan_w2.out`).
Withdrawals of exactly 5.0 SOL went to 3yU2oNff (a 2 SOL buyer using GMGN), 49L8nFU4 and 3K4MJK9b (no pump trading)
(`profile_pool.out`). Some of the 150 recipients on the funding day (Oct 17 15:00 → Oct 18 03:00) use nonces and trade
pump, but none uses wallet 4's tips (`fpscan_w1.out`).

### 4b. Who trades next to it

**The sample:** 40 of its 618 buys of 1.45+ SOL in other-token coins, 4 a day from Oct 19 to Oct 28 (seed 5). For each,
I read every transaction on the coin's bonding curve in slots S−2 … S+2, where S is its buy slot: getSignaturesForAddress
before the first signature of block S+3, then getTransaction (`neighbours.py` → `neigh.json`, `neighbours.log`;
`neigh_an.py` → `neigh_an.out`). Wallet 4's own transaction was found on all 40.

**Other buys, by position against wallet 4's buy:**

| slot −2 | slot −1 | same slot, before it | same slot, after it | slot +1 | slot +2 |
|---|---|---|---|---|---|
| 0 | 28 | 39 | 58 | 21 | 5 |

There were 97 distinct buyer wallets: 13 bought on more than one of the 40 coins, 84 on one only.

**The wallets on 2 or more of the 40 coins:**

| Wallet | Coins | slot −1 | same slot before | same slot after | +1 | +2 | Nonce | Tips (lamports) | What it is |
|---|---|---|---|---|---|---|---|---|---|
| `6anjqMeWigQFo5wpciARAunVQUXTqoat8w8fFWarCkpc` | 28 | 0 | 1 | 16 | 11 | 0 | 28/28 | 1,000,000 ×14, 1,400,000 ×9 | A fast launch buyer, fixed 0.5 SOL, own program `satasbJp`. Only **15%** of its buys (19 of 126) are wallet 4's coins; on those it lands after wallet 4 14 times, before it 2 times (`copier.py` → `copier.out`). On 16 of the 16 sampled coins Oct 25-28. Studied before (docs/19 §11). |
| `AMDEmVocLtN5ji2gBY7BrmSHEyM5vt6TGszBbg4crMXg` | 11 | 0 | 2 | 9 | 0 | 0 | 11/11 | 1,010,001 ×10 | 0.6 SOL buys, program `DDDDUigG`. 5% overlap with wallet 4's coins. |
| `Fhbh1DTUDKt6qu9zVg8Q5VgnZa1WWWbxBxG6pCoJoggA` | 5 | 1 | 3 | 0 | 1 | 0 | 5/5 | mixed | A micro-buy bot (0.002-0.003 SOL buys, about 2,000 txs in 2.5 h). Often just before wallet 4, but not a leader: its buys are dust. |
| DsGJkPzF, C5EMTGGE | 3 each | | | 3 | | | 3/3 | 1,020,000 | after it |
| BGMfeBCJ | 3 | | | 2 | 1 | | 3/3 | 5,000 | after it |
| CKii77zz, 42dqmewc, 53DnQU1d, 69d6eAno | 2 each | | | 1-2 | 0-1 | | | ~1,200,000 / 1,000,000 | after it |
| GTW4HfwbJ | 2 | | | | 1 | 1 | 2/2 | 200,000 | after it |
| J6YSoAhz (a creator of 21 of its coins) | 2 | 1 | 1 | | | | 0/2 | none | a dev buying its own coin |
| 9qz7cWBq (docs/19 §11) | 2 | 1 | 1 | | | | 2/2 | none | before it on 2 coins |

**Is there a leader it follows?** No.
- The buys before it are 67 in all. 10 are the coin's creator (dev buys). The other 57 are spread over many wallets,
  almost all appearing once (script output in the session).
- It buys at create+0 or +1 (§6), at a median 1.08x the launch price (p10 1.01, p90 1.56; 618 buys).
- It reacts to the launch, not to another wallet's buy.

**Copiers:** a median of 2 other buys land in its slot after it or in the next 2 slots (p25 1, p75 3, max 9; zero on 4
coins). Docs/19 wallets seen anywhere on the 40 curves: 6anjqMeW 30, AMDEmVoc 11, 9qz7cWBq 4, 3yrJE1A8 1. Operator 1
(AHwJSnFN) and the others: none.

## 5. Infrastructure

From the rows (`infra_rows.py` → `infra_rows.out`) and fetched samples (`infra_tx.py` → `infra_tx.out`; `failed.py` →
`failed.out`):

| | Value |
|---|---|
| Signatures per transaction | always 1 (150 of 150); the nonce authority is wallet 4 itself |
| Durable nonce first | 63 of 100 random own transactions; 12 nonce accounts, all created Oct 17 19:24:57-19:25:06 |
| Tip | **exactly one tip per transaction** (200 of 200 tipped) |
| Tip senders (200 tipped transactions, Oct 19-28) | Helius 109 (54%), Astralane 34, Jito 24, Nozomi 20, Speedlanding 9, NextBlock 2, Soyas 1, BlockRazor 1. The newest 3,000 signatures lean more to Speedlanding (fingerprint sample). |
| Tip amounts (lamports) | 1,067,000 ×94, 5,000 ×43 (all Helius), 1,010,000 ×36, 31,670,000 ×9, 10,000,000 ×3 |
| Share tipped | all own 27%; curve buys 51%; 1.45+ other-token buys 49%; sells 34% |
| Tip SOL p10/50/90 | buys 0.00107 / 0.00107 / 0.0165; 1.45+ other-token buys 0.00107 / 0.00107 / 0.011; sells 0.00001 / 0.00101 / 0.00101 |
| Fee, base plus priority, SOL p10/50/90 | 1.45+ other-token buys 0.00618 / 0.00804 / 0.01534; SOL-coin buys 0.00258 / 0.00304 / 0.02; sells 0.00001 / 0.00001 / 0.00029 |
| Priority fee (`transactionConfig.priorityFee`, lamports) p10/50/90 | 418 / 3,325,833 / 19,947,598 (63 of 100 sampled); CU limit p10/50/90 6,159 / 60,317 / 174,127 |
| Transaction version | v1 on 99 of 100. **Not a fingerprint:** 397 of 400 Axiom-router transactions are v1 too. |
| Block index p10/50/90 | curve buys 24 / 221 / 775; 1.45+ other-token buys 24 / 207 / 728; sells 40 / 230 / 789. **No top-of-block lane.** It is a multi-sender bot, not a bundle buyer. |
| Failed | **495 of 20,476 (2.4%)** since Oct 19, 489 paid by it, −2.854 SOL. By day 1.6-3.0%, 5.3% on Oct 26. |
| Top errors (code meanings as I read them) | Token-2022 `IncorrectProgramId` 143; Jupiter 6001 (slippage exceeded) 71; PumpSwap 3012 (Anchor AccountNotInitialized) 67; pump 6005 (curve complete, i.e. graduated) 61; System 0 (account already in use) 50; Jupiter compute budget exceeded 37; Jupiter ProgramFailedToComplete 24 |
| Other | Each landed transaction tips exactly one sender, and the sender varies. With a durable nonce, this fits a bot that sends one variant per sender and lets the first one land; that is an inference, not seen directly. A lookalike address `H9kupvjWtN4VbUsoFnKBw4rUtjqduMpqvDUc7yjqjDg` sent 0 SOL to 8h5eizMg (address poisoning: someone watches this bot). |

## 6. Creators

- **It never created a coin:** creator == wallet 4 on 0 of 4,998 curve buys.
- Its 3,349 other-token curve buys have **3,109 different creators**. The top ones made 25, 24 and 21 of its coins
  (`EkvdsXpS...`, `J1AYySZJ...`, `J6YSoAhz...`).
- In its own buy transactions it is the only trader (3,349 of 3,349): no bundle with the creator.
- **SOL to creators:** the sender side was checked.
  - Wallet 4, 8h5eizMg and MCquEenF were read in full; HxcdEi6C (first 400, last 2,000, random 1,500 of 62,231) and
    GEcF6sHy (newest 1,500 of 6,819) were sampled.
  - None of them sent SOL to any of the 4,594 creators of wallet 4's coins (overlap 0; script output in the session).
- **50 random other-token coins** (`creators.py` → `creators.log`, `creators.json`):
  - Wallet 4 bought in the **create slot on 25** and **the next slot on 22**; 3 not measured (the curve has more than
    5,000 signatures).
  - Its buy was the curve's very first trade on 138 of its 3,349 other-token buys.
  - Creators' visible funders are exchanges: Binance 1 (`5tzFkiKs`) funded 6 of them and KuCoin 2 (`BmFdpraQ`) 6
    (labels file).
  - The 2 "hits" on wallet 4 were pump's holder-fee payouts *to* wallet 4 (payer HckQ93Xq), not transfers to a creator.

## 7. Verdict

- **One bot, one operator, and not a fresh independent trader.** Wallet 4 is the Oct 17 continuation of HxcdEi6C, an
  82-day bot wallet. The operator swapped it through a privacy pool. This is a probable link, from money timing plus a
  matching transaction fingerprint; the pool means it can never be proven by a transfer.
- **No sibling trading now, and no leader.** It snipes other-token launches (create+0/+1) on its own. The wallets around
  it are faster or slower snipers and copiers (6anjqMeW, AMDEmVoc). None is worth copying instead.
- **No wash trading or insider signs** with creators.
- **Red flags:** hidden funding by design; wallet rotation (the predecessor was emptied in one evening: 60 SOL into the
  pool, 228.8 SOL to exchanges, a cross-chain swap and MEXC); 5 SOL back into the pool on Oct 27; copyable buys down to
  about a third of the Oct 19-25 pace.
- **To do for strategy A:**
  1. Alarm when wallet 4 goes quiet, or sends large amounts out.
  2. If it stops, look for the successor by fingerprint: durable nonce, 1,067,000 / 1,010,000-lamport tips, about 1.5 SOL
     other-token buys at create+0/+1.
  3. Keep in mind that our fills come behind 6anjqMeW-type buyers.

## Not checked

- HxcdEi6C's trading rule (2.5x / 0.7x / 30 min) and its profit. Only its buy sizes and quote mix were sampled.
- The full histories of HxcdEi6C (sampled 3,900 of 62,231) and GEcF6sHy (newest 1,500 of 6,819).
- The first funders of 6anjqMeW, AMDEmVoc and Fhbh1DTU.
- The names of programs 9fhQBbum (privacy pool), J88B7gma (cross-chain swap), BYdq7NJX (spam), satasbJp and DDDDUigG
  (neighbours' routers). The unlabelled exchange behind collection wallet 5yASLjtN is not identified.
- Pool withdrawals after Oct 28 ~15:00 UTC, and any successor wallet funded by routes other than this pool.
- The uniqueness of the tip sizes comes from samples (113 neighbour payers, 303 tip payers in 1 minute, 249 pool
  recipients), not from the whole chain.
- FLASHX8D's distinct payers per hour: only a 196-second window was measured.

## Sources (all in `wallet/`)

| Script | Output | What it gave |
|---|---|---|
| `page_sigs.py` | `page_sigs.log`, `w4_oldsigs.jsonl` | the 1,717 signatures before Oct 19; first tx |
| `fetch_old.py`, `old_scan.py` | `old_scan.out`, `old_flows.json` | first transactions, plain flows before Oct 19 |
| `netflows.py` | `netflows.out` | every in/out of 0.5 SOL or more since birth |
| `balance.py`, `reconcile.py` | `reconcile.out` | balance points and the split of the rise |
| `failed.py` | `failed.out` | failed transactions: count, fees, errors, per day |
| `nonsigner.py` | `nonsigner.out` | transactions paid by others |
| `funder.py`, `funder2.py`, `walletflows.py` | `funder_8h5eizMg.out`, `hist_8h5eizMg.out`, `flows_*.json` | funders' flows |
| `pool_sigs.py`, `pool_tx.py` | `sigs_4AV2Qzp3.json`, `pool_tx.out`, `pool_events.json` | privacy pool deposits and withdrawals |
| `profile.py` | `profile_pool.out`, `profile_hxcd_out.out`, `profile_up.out`, `profile_bank_out.out`, `profile_neigh.out` | quick profiles |
| `hxcd_first.py` | `hxcd_first.out`, `hxcd_page.log` | the predecessor's start and sampled flows |
| `fingerprint.py` | `fingerprint.out` | the transaction fingerprint of the three wallets |
| `tipscan.py`, `fpscan.py` | `tipscan.out`, `fpscan_w1.out`, `fpscan_w2.out`, `fpscan_exch.json` | tip-size uniqueness, sibling scans |
| `flash_sigs.py`, `flash_payers.py` | (printed) | FLASHX8D = Axiom |
| `neighbours.py`, `neigh_an.py`, `copier.py` | `neigh.json`, `neigh_an.out`, `copier.out` | neighbours and copiers |
| `infra_rows.py`, `infra_tx.py` | `infra_rows.out`, `infra_tx.out` | fees, tips, versions, index |
| `creators.py` | `creators.log`, `creators.json` | creators, create-slot timing |
| `perday.py` | `perday.out` | activity per day |

**Activity per day** (`perday.out`; Oct 17 covers 19:22-24:00, Oct 28 covers 00:00-14:54):

| Day | Signatures | Failed | Other-token curve buys | 1.45+ SOL other-token buys | SOL-coin buys |
|---|---|---|---|---|---|
| Oct 17 | 317 | 4 | | | |
| Oct 18 | 1,400 | 32 | | | |
| Oct 19 | 2,116 | 45 | 372 | 64 | 189 |
| Oct 20 | 2,800 | 44 | 511 | 78 | 231 |
| Oct 21 | 2,409 | 67 | 484 | 80 | 236 |
| Oct 22 | 2,339 | 43 | 466 | 77 | 203 |
| Oct 23 | 1,996 | 60 | 328 | 73 | 213 |
| Oct 24 | 2,270 | 54 | 348 | 56 | 131 |
| Oct 25 | 1,928 | 47 | 315 | 112 | 111 |
| Oct 26 | 1,390 | 73 | 222 | 35 | 121 |
| Oct 27 | 2,580 | 45 | 192 | 32 | 144 |
| Oct 28 (14.9 h) | 648 | 17 | 110 | 11 | 70 |
