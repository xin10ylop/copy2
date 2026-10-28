# Wallets with wallet 4's edge, found from fresh creates (on-chain scan, Oct 28)

**Question.** Wallet 4 (`H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg`) buys 1.45+ SOL of pump coins priced in
other tokens, in the create slot or the next, and holds up to 30 minutes. Which other wallets do the same? This study
starts from every pump create of the last 24 hours, not from wallet 4's coins.

**Answer: one new candidate, `3dwZP6T8tApEByVMiwYVeMQC7gwjeEVy6HjWWVyvhS6c`.** Over 24 hours (Oct 27 22:51 to Oct 28
22:51 UTC), 64 wallets bought other-quote frenzy coins in the create slot or the next across 5+ creators. 29 of them
made a 1.0+ SOL buy. All but a few sell within seconds (flips). Only wallet 4 and `3dwZP6T8` buy big and hold for
minutes. `DsGJkPzF` and `53DnQU1d` partly hold, and they buy after wallet 4 on the coins they share with it (13 of 16,
15 of 15). Most big launch buys
(4,392 of 5,571) come from launch bundles: 2-5 wallets that buy every coin of one creator in the create slot.
Verdicts are in §8.

## Run order

Data goes to the scratchpad `SPW = /tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallets/creates`
(every RPC response cached there, gzip'd JSON under `cache/`). The Triton URL is read from the old scratchpad's
`month/.triton_url` and is never printed (errors are redacted).

```
python3 -I s1_list.py 24          # every signature on the pump mint authority, 24 h back  -> SPW/s1_sigs.json
python3 -I s2_quotes.py all 48    # each landed create: CreateEvent quote mint, creator     -> SPW/s2_creates.json
python3 -I s2_mix.py              # the quote mix table below
python3 -I s3_frenzy.py 32        # each other-quote coin: its mint's signatures in its first slots -> SPW/s3_coins.json, s3_sigs/
python3 -I s3_check.py 30         # step 3's shortcut against the full paged list on 30 coins
python3 -I s4_trades.py 48 4      # frenzy coins: TradeEvents in slots +0..+3                -> SPW/s4_trades.json
python3 -I s5_rank.py 1.0 20      # rank the wallets that buy at +0/+1                        -> SPW/s5_rank.json
python3 -I s6_holds.py 30 25 32 6anjqMeWigQFo5wpciARAunVQUXTqoat8w8fFWarCkpc EnU1CPeCqFtVnqnYhd1JgfcPrhcDx4ffLZEnV9TnjJ4g
                                  # the top wallets' sales: flip or hold, net on closed trips -> SPW/s6_holds.json
python3 -I s7_overlap.py WALLET ...   # does it buy before or after wallet 4 on shared coins
python3 -I s8_table.py 21 6anjqMeWigQFo5wpciARAunVQUXTqoat8w8fFWarCkpc   # the table of §8
```
Run time on Oct 28 (shared box, Triton): s2 about 28 min (47,194 calls), s3 about 4 min, s4 2.5 min, s6 about 3 min;
a rerun reads the cache (598 MB gzip'd JSON). `python3 -I s3_check.py 30` checks step 3's shortcut.
`crc.py` holds the RPC, the cache and the event decoders (the full layouts of `crates/pump-codec/src/events.rs`).

## 1. The creates (s1_list.py)

The pump mint authority `TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM` is account #1 of both `create` and `create_v2`
(`crates/pump-codec/fixtures/idl/pump.json`; `constants.rs` `MINT_AUTHORITY`), so its signature list is the list of creates.

- **Window: 2026-10-27 22:51:51 to 2026-10-28 22:51:51 UTC** (24.00 h; Beirut 00:51 Oct 28 to 00:51 Oct 29),
  slots 462,246,222 to 462,651,728 (4.693 slots/s, 0.213 s a slot).
- 50,794 signatures, **47,194 landed creates, 1,966 an hour** (lowest hour 05 UTC: 1,157; highest 20 UTC: 2,750).
- Paging the list costs 51 calls of 0.6 s; fetching each create is the cost (about 0.5-0.9 s a call, 48 in parallel).

## 2. Quote of each create (s2_quotes.py, s2_mix.py)

Each landed create was fetched (`getTransaction`, jsonParsed) and its pump `CreateEvent` read (`quote_mint`; SOL coins
carry the all-zero key). 47,003 of the 47,194 have a CreateEvent (191 touch the mint authority without one).

- **Other-quote share: 10,899 of 47,003 = 23.2%** (SOL 36,104 = 76.8%), in 428 quote mints. 9,396 are quoted in a plain
  token (depth 0), 1,426 in a pump coin (depth 1), 77 in a pump coin quoted in a pump coin (depth 2).
- "Frenzy" = 4+ landed transactions on the mint in slots +0..+2 (step 3; the create not counted).

| Quote | Creates | Share of other-quote | Frenzy coins | Frenzy % | Initial virtual quote reserves |
|---|---:|---:|---:|---:|---:|
| PUMP `pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn` | 4,040 | 37.1% | 369 | 9% | 787,936,568,121 |
| SPCX `SPCXxcqXj6e5dJDVNovHN8744zkbhM2bYudU45BimGb` | 677 | 6.2% | 321 | 47% | 22,038,215 |
| `98sMhvDwXj1RQi5c5Mndm3vPe9cBqPrbLaufMXFNMh5g` | 553 | 5.1% | 252 | 46% | 41,187,648,566 |
| DJTu `DJTu7vi8norVzdVAffgvb39VP7wjKeTsgaMBJrzfxvoF` | 477 | 4.4% | 272 | 57% | 550,214,243 |
| `XsDoVfqeBukxuZHWhdvWHBhgEHjGNst4MLodqsJHzoB` (xStock) | 308 | 2.8% | 152 | 49% | 824,156,910 |
| USDC `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | 286 | 2.6% | 25 | 9% | 4,292,000,000 |
| `XsCPL9dNWBMvFtTmwcCA5v3xWPSMEBCszbQdiLLq6aN` (xStock) | 211 | 1.9% | 125 | 59% | 1,016,094,070 |
| A7bd `A7bdiYdS5GjqGFtxf17ppRHtDKPkkRqbKtR27dxvQXaS` | 178 | 1.6% | 80 | 45% | 251,072,563 |
| `CSRRgTwf9o5KLgguS2M16aEAhV5PUUzfshrAAQ8opump` | 151 | 1.4% | 56 | 37% | 645,851,080,143 |
| `DoGEV7LASBkQbibMc5k5vKnTZoMg423GpJ5QtJEGfm7R` | 143 | 1.3% | 71 | 50% | 4,167,167,403,217 |
| `SQQQAa3gUxgnqcEsdjPA4RQNQBgB97TnG2hJhk2WaGE` (xStock) | 133 | 1.2% | 82 | 62% | 89,574,107 |
| `PreweJYECqtQwBtpxHL171nL2K6umo692gTm7Q3rpgF` | 132 | 1.2% | 75 | 57% | 2,185,258,528 |
| WBTC `3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh` | 104 | 1.0% | 42 | 40% | 4,104,195 |
| TTWO `TTWofwAge91oFhZs7kpQdyrVRkmevgM88xijGvQFbKo` | 104 | 1.0% | 52 | 50% | 16,296,788 |
| `Xsc9qvGR1efVDFGLrVsmkzv3qi45LTBjeUKSPmx9qEh` (xStock) | 102 | 0.9% | 47 | 46% | 1,498,919,093 |
| HOUSECOIN `DUKEjskPBoszW4xEowcSWptekuUZpwLFv6nTt5Cmpump` | 96 | 0.9% | 29 | 30% | 23,490,074,937,198 |
| 398 more quote mints (and 14 listed by `s2_mix.py` past this table) | | | | | |

All frenzy coins: **2,915 of 10,899 (26.7%)**. PUMP is the biggest quote but rarely a frenzy (9%); the xStocks, SPCX,
DJTu and 98sM have a frenzy on about half their coins.

**Price per quote unit.** SOL coins all start at 30 SOL virtual (2,195 of 2,195 SOL creates checked, `vsol =
30,000,000,000`), and each quote mint starts at one fixed virtual amount (USDC 4,292 = 30 SOL at a $143 SOL), changed
now and then (PUMP had 724,612,902,473 early in the window and 787,936,568,121 later). So `30 SOL / initial virtual
quote` prices the quote at pump's own setting: WBTC 4,104,195 gives 7.31e-6 SOL per 1e-8 WBTC (the Oct 28 figure
given for this study: about 7.9e-6). Step 5 checks each quote against SOL-funded `multi_hop_swap` buys and corrects it.

## 3. Frenzy coins (s3_frenzy.py)

For each other-quote coin: `getSignaturesForAddress(mint, until=<its create>, before=<a create signature of step 1 at
least 4 slots later>)`. The RPC uses `before` only for its slot, so this returns the launch slots in one call. `s3_check.py` pages the full list from
the newest signature for 30 random frenzy coins: identical on slots +0..+3 for all 30. The first version paged back from the newest signature; it hit an
8-page cap on 63 of its first 2,241 coins (the busiest), whose launch it never reached, so it was replaced.

Landed transactions on the mint in slots +0..+2 (the create not counted), 10,899 coins: 0-4: 8,325; 5-9: 2,085;
10-14: 435; 15-19: 51; 20+: 3. **2,915 coins have 4+** and go to step 4 (25,905 transactions in slots +0..+3).

## 4. The launch trades (s4_trades.py) and the SOL price of each quote

2,915 frenzy coins, 25,905 landed transactions in slots +0..+3, **14,706 pump TradeEvents of those coins** (the rest touch
the mint without trading it). On other-quote coins the TradeEvent's `sol_amount` is 0; the size is `quote_amount`
(before fees) and the reserves are `virtual_quote_reserves`.

**Price check.** 6,085 buys were paid in SOL or WSOL in their own transaction: the buyer's SOL change (when it is the fee
payer, the network fee removed) plus its WSOL spent, its quote token not drawn down, one trade by it in the transaction.
Their median of SOL paid / config-priced size: **plain tokens 1.126, pump-coin quotes 0.892** (152 quotes, 123 with 3+
checks). PUMP 1.136 (767 buys), SPCX 1.113 (643), 98sM 1.121 (578), DJTu 1.116 (489), WBTC 1.130 (95): WBTC comes to
8.26e-6 SOL a unit (7.31e-6 x 1.130), near the 7.9e-6 given for Oct 28. Each quote with 3+ checks gets its own factor,
the rest their class median. The factor includes the buyer's swap cost and tips, so a size is what the buyer paid in SOL.
**Calibration: wallet 4's 1.0+ SOL buys come out at a 1.50 SOL median** (its known buys: 1.45+ SOL).

## 5. Who buys at +0/+1 (s5_rank.py)

**1,510 wallets bought a frenzy coin in its create slot or the next** (the coin's creator excluded), 1,094 of them for
1.0+ SOL. They are of three kinds:

- **Launch bundles: 1,210 wallets** buy the coins of one or two creators only, half or more in the create transaction or
  within 5 transactions after it in its slot. They make **4,392 of the 5,571 coin buys of 1.0+ SOL**. 56 groups (137
  wallets) did it on 10+ coins: 2-5 wallets buy every coin of one creator in the same slot (for example creator
  `5KhMUK6yK6FtDkXVmS5Tdy3Jnkd8yuRuUKWQKmGua1WV`: 53 coins, each bought by `EnU1CPeCqFtVnqnYhd1JgfcPrhcDx4ffLZEnV9TnjJ4g`,
  `6Qa46jFT7NegJRKNGPMQudr9v1aNC73KqFzX7vuvwRcC` and `3tqpS1u2mXkfiGSCKhaEZUeFQa2yfqmpmp85ZTBMZCjk`). These are the
  launch, not a buyer reacting to it; the full list is in `s5_rank.py`'s output.
- **Independent buyers: 64 wallets** buy coins of 5+ creators, under half of them bundled right after the create. 29 made
  a 1.0+ SOL buy (814 coin buys). This is where wallet 4 sits (146 creators).
- 236 others (coins of 2-4 creators, or mixed).

Marks per wallet (frenzy coins only): coins bought at +0/+1 and how many for 1.0+ SOL; median size in SOL; share of its
coins bought in the create slot (+0); the median number of trades by other wallets in its own slot after its buy and
the next 2 slots (the frenzy around it: 0-3 for everyone, it does not separate them); clock hours with a buy (the
window touches 25) and the last buy.

## 6. Flip or hold (s6_holds.py)

For each wallet, its newest 25 coins (fewer if it has fewer): its token account for the coin (from the buy's
`postTokenBalances`), that account's signatures, and each later transaction's token change and the wallet's
TradeEvents. First sale = the first decrease of the account. Net = quote out minus quote in minus pump's fees (fee,
creator fee, buyback fee from the TradeEvents) minus the network fee, priced as in §4, on the trips fully sold on the
curve. Jito tips and the cost of turning the quote back into SOL are not in it.

**Every independent big buyer but a few flips: first sale within 0-7 s (median), within 10 s on nearly all its coins.**
A copy lands a slot or more after the buy, so it would buy what they sell. Their profit (up to +12.68 SOL on 25 coins)
is the frenzy itself. Only wallet 4 (1,800 s median, 23 of 25 at 60 s or more) and `3dwZP6T8` (274 s, 15 of 17) hold;
`DsGJkPzF` (35 s, 6 of 25) and `53DnQU1d` (7 s, 4 of 23) sometimes do. For contrast, the bundle wallet `EnU1CPeC` sells at
18 s (median), +3.91 SOL net on 24 trips.

## 7. Independent of wallet 4? (s7_overlap.py)

On the coins it shares with wallet 4 (both bought at +0/+1), does the wallet buy before or after it?

| Wallet | Coins | Shared with w4 | Before w4 | After w4, same slot | After w4, later slot |
|---|---:|---:|---:|---:|---:|
| `3dwZP6T8` | 17 | 4 (24%) | 0 | 4 | 0 |
| `DsGJkPzF` | 54 | 16 (30%) | 3 | 12 | 1 |
| `53DnQU1d` | 44 | 15 (34%) | 0 | 15 | 0 |
| `6anjqMeW` | 291 | 127 (44%) | 4 | 87 | 36 |
| `AMDEmVoc` | 161 | 33 (20%) | 4 | 27 | 2 |
| `Fhbh1DTU` | 152 | 23 (15%) | 17 | 3 | 3 |
| `9qz7cWBq` | 99 | 16 (16%) | 15 | 1 | 0 |

`6anjqMeW` follows wallet 4 here: after it on 123 of 127 shared coins. `07-rework-2026-10-28/wallet-check.md` (line 240)
found it a fast fixed 0.5 SOL launch buyer with only 15% of its buys on wallet 4's coins. On frenzy coins bought at +0/+1
the share is 44%. The holders `3dwZP6T8`, `DsGJkPzF` and `53DnQU1d` are also after wallet 4 on every shared coin or nearly,
so they may copy wallet 4 on part of their coins. Most of their coins (13 of 17, 38 of 54, 29 of 44) are not wallet 4's.
`wallet-check.md` (lines 243-245) already saw `DsGJkPzF` and `53DnQU1d` buy after wallet 4 on its curves.
`3dwZP6T8` appears in no earlier doc. The flippers are ahead of wallet 4. `Fhbh1DTU`, `9qz7cWBq`, `3yrJE1A8` and
`AMDEmVoc` were already on wallet 4's curves in `wallet-check.md` (line 257).

## 8. Ranking: the top 20 independent buyers and wallet 4 (s8_table.py)

Ordered by coins bought at +0/+1 for 1.0+ SOL (frenzy coins, Oct 27 22:51 to Oct 28 22:51 UTC). Wallet 4 is the
calibration row (rank 3); `6anjqMeW` (rank 23) is added as wallet 4's main co-buyer. "Net" is over the newest closed
trips (§6). Full addresses; "Mark" is the rule in `s8_table.py` (flips: first sale within 10 s on 80%+; holds: at 60 s
or later on 50%+).

| # | Wallet | Coins +0/+1 (1.0+ SOL) | Median SOL | At +0 | First sale (median; <=10 s / >=60 s) | Trades by others within 2 slots | Net SOL, newest closed (won) | Shared with w4 (after w4) | Active (hours; last buy UTC) | Mark |
|---:|---|---:|---:|---:|---|---:|---:|---:|---|---|
| 1 | `Fhbh1DTUDKt6qu9zVg8Q5VgnZa1WWWbxBxG6pCoJoggA` | 152 (137) | 1.89 | 62% | 1 s; 24 / 0 of 24 | 2.0 | +7.50 on 24 (14) | 23 (6) | 25; 22:20 | flips |
| 2 | `9qz7cWBqYBP2TnGfzMmxX64G4PQip7HtogjPBBnMhWpw` | 99 (99) | 1.85 | 78% | 2 s; 22 / 0 of 22 | 2.0 | -1.63 on 22 (3) | 16 (1) | 24; 22:49 | flips |
| 3 | `H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg` | 190 (77) | 0.96 | 64% | 1800 s; 0 / 23 of 25 | 2.0 | +2.80 on 25 (8) | calibration | 25; 22:44 | holds |
| 4 | `4rmuCfy2ea1ZkvJzebbLJkg9BDtX12dUbY14UUKJHLhW` | 45 (45) | 3.14 | 69% | 0 s; 25 / 0 of 25 | 3.0 | +6.03 on 21 (18) | 3 (0) | 19; 22:32 | flips |
| 5 | `HK9K6ZMMozD17ADBVMuoFUNXtr9Z4Bo5zTkQA5mk94iS` | 42 (42) | 3.07 | 17% | 1 s; 25 / 0 of 25 | 0.0 | +7.86 on 25 (6) | 0 (0) | 7; 21:44 | flips |
| 6 | `dKMjeGJ4Mk9S3hxdfTThvZ7exks2xMwWqSM5NvN2CTK` | 38 (38) | 2.88 | 63% | 1 s; 25 / 0 of 25 | 3.0 | +2.35 on 25 (12) | 7 (1) | 17; 22:13 | flips |
| 7 | `3yrJE1A8dgSuy5NLimG5GSYxA6wMkvnAYLD9Y4xR2fjJ` | 74 (37) | 1.34 | 74% | 5 s; 25 / 0 of 25 | 2.0 | -1.05 on 25 (10) | 3 (3) | 21; 22:07 | flips |
| 8 | `FiFawHqxeTVBhv6YbqbLwDVuvokRpPUM1bNwAyxhGc6W` | 36 (36) | 2.00 | 81% | 2 s; 25 / 0 of 25 | 1.5 | +0.55 on 25 (6) | 8 (0) | 15; 22:16 | flips |
| 9 | `D24ipYXuDt6PXEPV6rZqfWb35WJaTJW3gDoXwt7yJCwQ` | 55 (35) | 1.25 | 65% | 0 s; 25 / 0 of 25 | 2.0 | +2.59 on 24 (14) | 0 (0) | 17; 22:30 | flips |
| 10 | `53DnQU1dJZNHfKBpv2Lhsd4EBGNpwsF4tS13Egc1m6Tv` | 44 (31) | 1.52 | 55% | 7 s; 14 / 4 of 23 | 1.0 | +1.59 on 23 (13) | 15 (15) | 17; 22:16 | mixed |
| 11 | `FeCAXCyHwrg3QPkyVrJY2VA1qRQGzjHKhEiteRkqdjSD` | 24 (23) | 2.04 | 58% | 2 s; 22 / 0 of 24 | 3.0 | +7.61 on 24 (13) | 1 (0) | 9; 21:55 | flips |
| 12 | `8ptvshQRZPRaRQBSCRxhHwbJFr6ktyUQ1SATDCLijkBW` | 29 (21) | 1.14 | 62% | 2 s; 25 / 0 of 25 | 3.0 | +1.60 on 25 (10) | 2 (1) | 15; 22:42 | flips |
| 13 | `DbnxpjUpe7h4f4z13rkqKERQZt2wxUjCTvQWsSGwm9Jf` | 23 (21) | 1.90 | 61% | 0 s; 23 / 0 of 23 | 1.0 | +9.04 on 22 (15) | 3 (0) | 9; 22:30 | flips |
| 14 | `9su3UPQW3txjtKDZAkf2Kdimp5tEb9TM6hnJrGC1U7pY` | 286 (20) | 0.31 | 60% | 5 s; 24 / 0 of 24 | 1.0 | +2.25 on 24 (12) | 6 (5) | 25; 22:30 | flips |
| 15 | `DsGJkPzFEQZuwy7JjZzPcJEyEfdC6StV7rarXG4ftRSA` | 54 (20) | 0.54 | 57% | 35 s; 6 / 6 of 25 | 1.0 | +6.06 on 25 (11) | 16 (13) | 22; 22:10 | mixed |
| 16 | `Anubis512ho5t7S6LNSwoxUWdeQmX2kf3RvZ8ApHHF5w` | 99 (18) | 0.06 | 46% | 2 s; 25 / 0 of 25 | 2.0 | +12.68 on 25 (11) | 7 (7) | 16; 22:28 | flips |
| 17 | `CBKgS8Nj714YomoPPxhVLUWos7vSrWnuL2cVKnJqWo2s` | 25 (18) | 1.06 | 56% | 1 s; 25 / 0 of 25 | 0.0 | -0.86 on 25 (6) | 1 (1) | 14; 22:27 | flips |
| 18 | `8pisMPgQvkTc1x6jYtqCubVpASKGHAovN87m7XLtbbd5` | 25 (17) | 1.05 | 64% | 1 s; 25 / 0 of 25 | 1.0 | -0.24 on 25 (6) | 0 (0) | 12; 21:44 | flips |
| 19 | `3dwZP6T8tApEByVMiwYVeMQC7gwjeEVy6HjWWVyvhS6c` | 17 (17) | 1.95 | 18% | 274 s; 1 / 15 of 17 | 1.0 | +4.38 on 17 (4) | 4 (4) | 11; 21:46 | holds |
| 20 | `38uzzLBFhUXTd4i2f55nAGtiQ61bG2nFWah2GMpvdkJj` | 17 (17) | 2.05 | 76% | 3 s; 14 / 0 of 17 | 2.0 | +7.15 on 16 (7) | 1 (0) | 10; 17:58 | flips |
| 21 | `FZU56d9iPqohXM5XBrYYBZLi2UoUnZT4V5Qf2631tEzb` | 9 (9) | 1.22 | 11% | 16 s; 3 / 2 of 9 | 3.0 | -0.55 on 8 (1) | 1 (1) | 7; 22:12 | mixed |
| 23 | `6anjqMeWigQFo5wpciARAunVQUXTqoat8w8fFWarCkpc` | 291 (6) | 0.51 | 52% | 261 s; 7 / 16 of 25 | 1.0 | +0.44 on 25 (5) | 127 (123) | 25; 22:44 | holds |

| # | Wallet | Worth a full scoring? |
|---:|---|---|
| 1 | `Fhbh1DTU...` | No. Big (1.89 SOL) and often (137 coins), but sells within 1 s on 24 of 24: gone before a copy lands. |
| 2 | `9qz7cWBq...` | No. Flips in 2 s; −1.63 SOL net after fees on 22. |
| 3 | `H9kuqGKN...` (wallet 4) | Calibration: 77 coins at 1.0+ SOL, holds (1,800 s), +2.80 on its newest 25 trips, 8 won. |
| 4 | `4rmuCfy2...` | No. Largest buys (3.14 SOL), sold in the same second. |
| 5 | `HK9K6ZMM...` | No. Flips in 1 s, lands late (17% at +0), 7 active hours. |
| 6 | `dKMjeGJ4...` | No. Flips in 1 s. |
| 7 | `3yrJE1A8...` | No. Flips in 5 s; −1.05 net. |
| 8 | `FiFawHqx...` | No. Flips in 2 s; +0.55 net. |
| 9 | `D24ipYXu...` | No. Flips in 0 s. |
| 10 | `53DnQU1d...` | Low priority. 1.52 SOL, routes like wallet 4 (37 of 44 by `multi_hop_swap`), holds a minute on 4 of 23, flips 14; after wallet 4 on all 15 shared coins. Score its own 29 coins only if at all. |
| 11 | `FeCAXCyH...` | No. Flips in 2 s. |
| 12 | `8ptvshQR...` | No. Flips in 2 s. |
| 13 | `DbnxpjUp...` | No. Flips in 0 s. |
| 14 | `9su3UPQW...` | No. Small (0.31 SOL), flips in 5 s. |
| 15 | `DsGJkPzF...` | Maybe. Small (0.54 SOL; 20 coins at 1.0+), mixed (35 s; 6 of 25 held 60 s+), +6.06 net on 25; after wallet 4 on 13 of 16 shared coins. Score its own 38 coins. |
| 16 | `Anubis51...` | No. Median 0.06 SOL, flips in 2 s. |
| 17 | `CBKgS8Nj...` | No. Flips in 1 s; −0.86 net. |
| 18 | `8pisMPgQ...` | No. Flips in 1 s; −0.24 net. |
| 19 | `3dwZP6T8...` | **Yes, the one candidate.** 1.95 SOL median, every coin 1.0+ SOL, holds (274 s; 15 of 17 at 60 s+), +4.38 net on 17 with 4 won (wallet 4's shape: few big wins), active 11 hours. Against it: 17 coins a day (wallet 4: 77), lands late (18% at +0), after wallet 4 on its 4 shared coins. |
| 20 | `38uzzLBF...` | No. Flips in 3 s; last buy 17:58 UTC. |
| 21 | `FZU56d9i...` | No. 9 coins, mixed, −0.55 net. |
| 23 | `6anjqMeW...` | No as a new edge: it follows wallet 4 (123 of 127 shared coins after it), small (0.51 SOL; 6 coins at 1.0+). |

## Limits

- **Frenzy coins only** (4+ landed transactions in slots +0..+2). A wallet that buys big on quiet coins is not seen.
- **One day.** Wallets that were idle on Oct 28 are missed; 7 of the table's 21 were active 12 hours or less.
- **Sizes** use pump's quote setting times the checked factor (§4); a quote with fewer than 3 checks gets its class median.
- **Flip or hold** looks at each wallet's newest 25 coins (the last hours of the window). Net leaves out Jito tips and the
  quote-to-SOL swap, and a coin that graduated while held (sold in the pool) is not "closed".
- The "independent" cut (5+ creators, under half bundled) is a choice; `s5_rank.py` prints every wallet's marks.
- `getSignaturesForAddress` with a foreign `before` was checked on 30 random frenzy coins against the full list (`s3_check.py`).
