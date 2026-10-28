# Strategy A: the paper run (Oct 27-28)

In short: 22 paper positions from Oct 27 12:29 to Oct 28 10:40 Beirut. 20 closed, 9 won, **+2.6541 SOL**; 2 refused by
the price limit. Every trade followed its rules. A chain check from the Ohio start (Oct 27 16:11 UTC) to Oct 28 13:14
UTC found **every** qualifying buy of wallet 4 entered and nothing missed. Two things differ from the backtest, and both
make paper look better than real money would: wallet 4 sells early far more often (8 of 20), and the profit rests on take
profits within 1-10 seconds, where our real speed matters most. Paper means nothing is sent: the bot prices its
decisions on the live curve.

The raw output: [`../05-live/long-paper-history-and-journal-2026-10-28.txt`](../05-live/long-paper-history-and-journal-2026-10-28.txt)
(`history.py paper`, then the journal's skip / paper-buy / paper-refused / feed lines). Times in the history table are
Beirut time (UTC+2 on these dates); journal times are UTC.

## 1. Where it ran

| When (UTC) | Where | What |
|---|---|---|
| Oct 27 morning to 12:45 | fra1 (Frankfurt) | first paper run, 1 trade (PePEwjLD). Stopped with every rugsnipe unit before fra1's backup |
| Oct 27 16:11 | Ohio | started on Ohio in paper mode with fra1's feed settings, no wallet (`long: no wallet ... paper only`). PePEwjLD's record carried over |
| Oct 27 18:08, Oct 28 00:26 and 00:35 | Ohio | restarts for updates (`f52cee5`; `0aa4f24`; `max_open = 4` + `2314377`); down about 1-2 s each |
| Oct 28 12:53:21 | Ohio | one feed disconnect, reconnected 1 s later |

On fra1 the only trade was PePEwjLD (bought 10:29:41 UTC). CkFH2smc (16:14:35 UTC) was the first trade on Ohio. Ohio saw
its buy in the same second wallet 4 made it.

## 2. The 22 positions (from the history paste)

| # | bought (Beirut) | its SOL | route | exit | peak | held | net SOL |
|---|---|---|---|---|---|---|---|
| 0 | Oct 27 12:29:41 | 1.500 | copied | time | 1.04x | 1790s | −0.0230 |
| 1 | Oct 27 18:14:35 | 1.500 | copied | time | 1.56x | 1790s | −0.1843 |
| 2 | Oct 27 20:25:35 | 1.500 | copied | time | 1.05x | 1790s | −0.1277 |
| 3 | Oct 27 21:07:16 | 1.502 | copied | **tp** | 2.04x | 1s | **+0.8377** |
| 4 | Oct 27 21:49:24 | 1.500 | copied | its_sell | 1.24x | 197s | −0.2958 |
| 5 | Oct 27 22:09:03 | 1.493 | copied | its_sell | 1.73x | 7s | −0.1756 |
| 6 | Oct 27 23:02:24 | 1.500 | copied | its_sell | 1.25x | 475s | −0.2468 |
| 7 | Oct 27 23:31:01 | 1.500 | copied | **tp** | 2.05x | 124s | **+0.9869** |
| 8 | Oct 27 23:39:24 | 1.500 | copied | stop | 1.27x | 23s | −0.3124 |
| 9 | Oct 27 23:46:28 | 1.502 | copied | **tp** | 2.01x | 4s | **+0.8769** |
| 10 | Oct 28 01:10:20 | 1.500 | copied | time | 1.21x | 1790s | −0.0973 |
| 11 | Oct 28 02:24:51 | 1.457 | curve | its_sell | 1.60x | 286s | +0.1038 |
| 12 | Oct 28 03:04:23 | 1.500 | copied | its_sell | 1.06x | 141s | −0.3031 |
| 13 | Oct 28 03:10:37 | 1.500 | copied | **tp** | 2.01x | 10s | **+0.7511** |
| 14 | Oct 28 03:15:19 | 1.500 | copied | time | 1.04x | 1790s | −0.2238 |
| 15 | Oct 28 03:27:36 | 1.500 | copied | **tp** | 2.02x | 2s | **+0.8557** |
| 16 | Oct 28 03:31:36 | 1.500 | copied | its_sell | 1.99x | 3s | −0.0623 |
| 17 | Oct 28 04:23:47 | 1.500 | copied | refused (price limit) | | | fee only |
| 18 | Oct 28 04:27:39 | 1.501 | copied | time | 1.07x | 1790s | +0.0087 |
| 19 | Oct 28 04:41:16 | 1.500 | copied | its_sell | 1.55x | 907s | +0.1424 |
| 20 | Oct 28 08:49:59 | 1.502 | copied | its_sell | 1.46x | 1360s | +0.1429 |
| 21 | Oct 28 10:40:06 | 1.500 | copied | refused (price limit) | | | fee only |

"copied" = wallet 4's own route copied (from wrapped SOL); "curve" = a direct curve buy behind the quote's pool.

**By exit** (they add up to the +2.6541):

| exit | trades | net SOL |
|---|---|---|
| take profit at 2.0x | 5 | +4.31 |
| time (1790 s) | 6 | −0.65 |
| stop (0.8x) | 1 | −0.31 |
| behind its own sell | 8 | −0.69 |
| refused by the price limit | 2 | fee only |

## 3. Did it behave as it should? Yes

- **Entries:** all 22 were wallet 4's buys of 1.45 SOL or more (1.457-1.502) of coins priced in other tokens, at 1 SOL
  each.
- **The 2 failed (#17 5a7nDZcR, #21 EwsKTHxB)** were the price limit. By the time the paper buy would have filled, the
  price was already 1.518x (#17) and 1.321x (#21) wallet 4's, over the 25% limit. The journal says `long paper-refused`.
  In paper mode this is the only way a buy can fail.
- **Take profits:** all 5 fired at 2.0x (peaks 2.01-2.05x).
- **Time exits:** all 6 sold at 1790 s. Nothing was held longer.
- **Stop:** the 1 stop fired when the price fell through 0.8x. It shows −31% because it fell fast.
- **Its own sell first:** each of the 8 followed one of wallet 4's own sales.
- **Open at once:** never more than the cap (4 since Oct 28 00:35 UTC).
- **Restarts:** the open position was kept and closed normally.

## 4. Did it enter everything it should have? Yes, checked on chain

From the Ohio start (Oct 27 16:11 UTC) to Oct 28 13:14 UTC, the chain shows wallet 4 making **94 buys on 93 coins**
that were either 1.45 SOL or more or paid in a token we can't price. All of them were run through the bot's own detection
(`examples/scan.rs`) and compared with the journal, coin by coin
(`analysis/research/2026-10-28/verify/`: `w4fetchlive.py` → `scan.out`, `journal.txt`):

| On chain | Coins | In the journal |
|---|---|---|
| qualifying and routable | 21 | **all 21 entered** (#1-#21, including the 2 the price limit refused) |
| 1.45+ SOL with no route | 5 | all 5 skipped: "no route" (A7bdiYdS, 6GmAFSYs, WXMRyRZh) or "3 hops" (AvcwGFaF, 2FSWwQwj) |
| paid in an unpriced token | 67 | all 67 skipped as unpriced (PUMP, CARDS ...) |

- No buy on chain is missing from the journal, and no journal entry is missing from the chain.
- The three restarts and the 1-second feed disconnect cost nothing: no wallet 4 buy landed in those seconds.
- No buy was lost to the open-position cap, the daily stop, the kill file, or a coin we already held.
- On fra1 (09:00-13:00 UTC Oct 27, 157 of its transactions): PePEwjLD was the only qualifying buy. The rest were 3 buys
  at 1.423-1.427 SOL (under the floor), 8 between 1.0 and 1.25, 3 paid in tokens it can't value, and 14 SOL-priced
  coins. In the same 4 hours of the 8 backtest days there were 0 to 9 qualifying buys. Whole days averaged about 34
  copies (21 to 45).

## 5. What differs from the backtest (watch these)

1. **Wallet 4 sells early much more often:** 8 of 20 trades (40%), against 3-6% in the Oct 19-27 data. Some are its stop
   firing in a crash, where ours would have fired too (6DS5ErwH, BPhav4G4, both around −30%). Others are very fast:
   ChonQdJ8 after 7 seconds (checked on chain: it sold everything, losing 10% itself), and DJXThGNt after 3 seconds at
   1.99x, just short of our 2.0x. If this goes on for a few days, its behaviour has changed and the rule needs re-testing
   on fresh data.
2. **The profit rests on take profits within seconds.** 4 of the 5 came 1-10 s after its buy (#3 1 s, #9 4 s, #13 10 s,
   #15 2 s), on coins that doubled while other bots piled in. Those 4 made +3.32; without them the run is −0.67. They are
   exactly the trades where our real speed matters most. On 6y9aDagF (#3) the price was 1.2x 1 s after its buy and over
   2.0x after 2 s (`coins/6y9a.path`, from `examples/curve_path.rs`).
3. **Paper's landing was optimistic until `7184554`.** Paper filled at wallet 4's slot + 1, whenever Ohio actually saw
   the buy. Since `7184554` it fills at the end of the slot after the one Ohio saw it in. Each `paper-buy` journal line
   ends with `seen at its slot +N`, so Ohio's lag is measured. **That commit wasn't yet deployed on Ohio at the time of
   this paste** (see deploy-ohio.md §4).
4. **Real fills will be worse than paper.** From Ohio a real buy probably lands 2-4 slots after wallet 4's. On frenzy
   coins the price moves a lot in that time.

## 6. The fixes this run produced

| What the run showed | Fix | Commit |
|---|---|---|
| CkFH2smc: wallet 4 sold after 14 minutes, and the copy held to 30. The backtest sells right behind it | exit `its_sell`: out behind its own sale | `f52cee5` |
| A paper buy filled at any price, but a real one is refused above 25% over its price, and coins double in 2 s | paper refuses like the real buy (`long paper-refused`), fee only | `0aa4f24` |
| The cap of 3 skipped about 15% of copies; 4 was best in both periods | `max_open = 4` (repo default; set on Ohio by `sed`) | `2314377` |
| Paper filled at its slot + 1 whatever Ohio's lag | fill a slot after Ohio saw the buy; journal records the lag | `7184554` |

## 7. How to read it yourself

```
sudo python3 -I ~/history.py paper                                    # every position, by day
sudo /opt/rugsnipe/bin/rugsnipe-long status --config /etc/rugsnipe/long.toml --last 30
sudo journalctl -u rugsnipe-long --since "2026-10-28 00:00" --no-pager | grep -E 'long (skip|paper-buy|paper-refused|its-sell)|feed'
```
Journal lines: `long paper-buy #N <coin> its X SOL route ... (; seen at its slot +N, fills at the end of +M)`,
`long paper-refused #N <coin>: at 1.518x its price, ... tokens under min_out ...`, `long its-sell #N <coin>: out behind
it`, `long skip <coin> its X SOL (...): <reason>`.

## Sources

- `05-live/long-paper-history-and-journal-2026-10-28.txt` (the history and journal as pasted on Oct 28).
- `analysis/research/2026-10-28/verify/` (the chain check), `analysis/research/2026-10-28/coins/` (6y9aDagF, ChonQdJ8).
- Session reviews of the paper run, Oct 27-28; commits `f52cee5`, `0aa4f24`, `2314377`, `7184554`.
