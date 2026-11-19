# 23. rh-copier: three Pons traders on Robinhood Chain, one wallet

`rh-copier` (code: `crates/rh-copier`; config: `config/rh-copier.example.toml`; unit: `deploy/systemd/rh-copier.service`).
Built Nov 18, 2026. The research is in `analysis/research/2026-11-18/robinhood/README.md`. **No paper phase: the owner's
call on Nov 18** ("no paper, last 3 days, behaved as it should? if yes, build"; the last 3 days were positive for all
three, `out/rh11_*.txt`). The stake is 0.02 ETH a copy ("ok so well do 0.02 stakes for now").

## 1. What it copies

One wallet copies all three. Each has its own engineered settings (`out/rh6b_*.txt`: every combination of buy size, coin
type, price limit, tp, hold, sell pressure, stall and its sale, with our buy landing 2, 3 and 5 blocks after its buy).

| wallet | address | copied buys | price limit | exits | backtest a copy | last 3 days (rh11, 0.05 ETH) |
|---|---|---|---|---|---|---|
| 1 | 0x9a3955a1... | 0.1+ ETH, coins under 0.5 ETH in the curve | 1.5x | tp 4, 600 s | +24.2% (339) | +26.5% (45, 15 a day) |
| 2 | 0x5bc235ac... | 0.05+ ETH, any coin | 1.5x | tp 3.5, 600 s, sell pressure 10/30 s from 30 s | +12.5% (514) | +21.1% (71, 24 a day) |
| 3 | 0xc54d3914... | 0.03+ ETH, any coin | none (3x bound) | tp 2.5, 300 s, sell pressure 8/60 s from 30 s, stall 240 s | +26.7% (190) | +39.2% (19, 6 a day) |

Their own sales are ignored (`its_sale = "never"` won for all three). The full addresses are in the example config.

## 2. How it works

| Step | What it does |
|---|---|
| Feed | PublicNode's WebSocket (`eth_subscribe` logs), every Pons CurveBuy and CurveSell. A drop reconnects in 1 s; 180 s with no message counts as a drop. A `heartbeat` line every 10 min gives the trades seen. |
| Signal | A copied wallet's buy, acted on the moment the feed brings it (CurveBuy's recipient) of at least `min_its_eth`. One copy per coin within an hour; `max_open` (4); `daily_stop_eth` (0.06); the `KILL` file. |
| Its price | From its buy alone, no read: an ETH curve keeps virtual ETH × virtual tokens = 1.68e9 exactly, and its buy moves the ETH by quoteIn − fee − tax, so the curve right after its buy follows from its two numbers (checked on 20 real buys: equal to the chain's reserve). A buy that does not fit (a coin priced in USDG, cbBTC or a stock) is not copied. The coin type is the ETH in the curve before its buy. |
| Buy | `buy(quoteIn, minTokensOut, recipient)` with value = the stake. `minTokensOut` is what the stake buys at the price limit (1.5x its price), so a buy that would fill higher reverts on chain. With no limit (wallet 3), the expected amount less 25%. No buy when the price is already over the limit, or the curve holds 3.8+ ETH (it graduates at 4.2 into a Uniswap v4 pool the bot does not trade). |
| Approve | `approve(curve, max)` on the coin goes out right behind the buy (the next nonce), so the sale is ready at once. |
| Exits, first one wins | graduation guard (3.8 ETH in the curve), take profit, sell pressure (other wallets' sales minus buys over the window, after `from` s), stall (no new high for `stall_s`), time (`hold_s` after its buy). All measured against its price, as the research did. |
| Sale | `sell(balance, minQuoteOut, us)`: sells the wallet's exact token balance; minimum = the expected ETH less 30%, then half that, then 0. Three failed tries: retried 5 s later, again and again. |
| Sends | Signed here (EIP-1559, chain 4663, the fee cap 3x the gas price); each goes to PublicNode and the official RPC; the receipt confirms it. Gas on Nov 18: 0.02 gwei, a buy ~100k gas, a sale ~80k: about 0.000003 ETH a trade. |
| Lag | Each fill logs `lag N blocks behind its buy` (our buy's block minus its buy's); `status` shows it per trade. The backtest assumed 2, 3 and 5. |
| Book | `/var/lib/rh-copier`: `state.json` (open positions, kept across restarts), `closed.jsonl`, `failed.jsonl`, `its.json`. |

Checked on Nov 18 against the chain: our buy call simulated on a live curve (6.07M tokens for 0.02 ETH; a too-high
minimum reverts); our sale call simulated one block before two real sales gave their exact ETH out; every RPC method on
both nodes. A 7-minute log-mode run on the live feed (two very active bots added as test wallets) copied 2 buys and
closed both. The official RPC ran 7-10 blocks behind PublicNode, so reads and receipts use PublicNode
(`rpc_url`) and history the official RPC (`logs_url`). Engine tests: `cargo test -p rh-copier` (14).

## 3. Risks, said plainly

- **Live since Nov 18 22:10 UTC** on `fra-long`, wallet `0x35bb5c55a531d14213380fd978a501f0e239a77e`, 0.15 ETH (bridged from 3.8 SOL
  of wallet 4's bot wallet). The first start (22:03) crashed before sending anything: the workspace build gave rustls two
  crypto engines and it panicked on the first TLS connection; fixed in `3e1b321`. The first real trades are its mechanics test: check them on chain (Blockscout),
  as `03-strategy-A-long-copy/deploy-frankfurt.md` §6 did for wallet 4.
- Other copy bots already follow wallets 1 and 2 within 2 blocks (`out/rh8_cobuyers.txt`). The backtest landed us 2,
  3 and 5 blocks late; the feed adds about 1 s (10 blocks) at worst on a slow moment. The price limit protects the buy.
- Coins that graduate while held are sold at 3.8 ETH by the guard; the pool is not traded.
- Nov 15 shows almost no copies for all three: a quiet day or a gap in the fetched data (not checked yet).
- PublicNode's free endpoints are the only live feed found (no key). If they fail for long, nothing is copied (open
  positions still exit on the clock, and reserves are re-read every 15 s).

## 3b. The first real trades (Nov 19, checked on chain)

| # | wallet | lag | our price / its price | exit | net |
|---|---|---|---|---|---|
| 1 | 1 | 2 blocks, 0 s | 1.18x | time, 600 s (peak 1.49x) | +0.001065 ETH (+5.3%) |
| 2 | 3 | **10 blocks, 1 s** (the send took 1,157 ms, the others ~300) | 1.21x | stall at 253 s (peak 1.86x early) | −0.000455 ETH (−2.3%) |
| 3 | 1 | 3 blocks, 0 s | 1.10x | (open at the check) | |

Journal = chain on every token and wei; 8 transactions, all landed first try; our buys paid 9-10% fee + tax on young
coins (the launchpad's snipe tax; the backtest charges each trade's own). **A bug, fixed the same morning:** at 00:44 UTC
wallets 1 and 3 bought one coin in one block; wallet 1's buy was over its coin-type limit and marked the coin seen, so
wallet 3's qualifying buy was dropped. A coin now counts as seen only once it is copied (engine test
`a_wallet_skipped_by_its_own_filter_does_not_hide_another_wallets_copy`). Also added: each send logs every node's answer
time, and each signal logs how many blocks behind the node's head it arrived (`rh signal ... (+N blocks)`).

**The stuck sale (Nov 19 08:33-10:22 UTC), my bug:** coin #6's sale landed at 08:33:03 (nonce 17, 0.015316 ETH back, the
stall exit of wallet 3), but the bot did not see its receipt in time and counted it as failed. With the coin gone, the
code fell back to selling the fill's token count, which can only revert, and retried every 5 s for two hours: about
3,140 reverted transactions, about 0.0032 ETH of gas, and probably the one failed buy (#7) from the nonce turmoil. The
owner stopped the bot. Fixed: every sale try re-reads the wallet's balance of the coin, and a zero balance closes the
position with our sale found on chain (`my_sale`, the official node's logs; checked on coin #6: 0.015316 ETH); the
receipt wait asks every node in turn; a node's "already known" is waited for; a failing sale backs off 5, 10, 20, 40,
then 60 s (engine test `a_failing_sale_backs_off_to_a_minute`). The ten trades of Nov 19 to 10:22 UTC on chain: 2 won,
−0.01554 ETH before gas.

**The first 13 closed trades against the model (Nov 19, `analysis/research/2026-11-19/rh_deep/out/rhd6_live_vs_model.txt`):**
live −0.0311 ETH (−12.0% a copy, 2 won); the backtest model on the same 13 coins at our real landing −0.0304, at its own
2/3/5 blocks −0.0335. Execution matches the model trade by trade; the coins were bad (13 backtest copies in this mix lose
this much in 3.9% of draws; 2 or fewer winners in 6.9%). Every exit audited from the chain: the time exits at 600 s
(wallets 1, 2), wallet 2's sell pressure never reached 10 (correct), wallet 3's stalls on time. **One wrong exit:** coin
#4 (wallet 3) sold by sell pressure at 61.5 s on a clock tick, when ~13 snipers' buys of second 1 aged out of the 60 s
window and left their sales of second 6 inside: −2 at 61.0 s, +12 half a second later, with no new trade. The backtest
judges sell pressure on trades only; the engine now does too (test `sell_pressure_is_judged_on_trades_not_when_old_buys_age_out`;
the engine replayed on the coin's chain trades now holds and leaves by stall at 242 s). Also: a refused send now logs
the node's reason.

**Why #6's sale was missed (its journal, 08:32-08:34 UTC):** both nodes failed at once. PublicNode answered every send
with "failed to call backend endpoint" (2.1 s), the official node took 5-33 s, and the bot logged each try as "not sent";
yet the first try (nonce 17) landed at 08:33:03, and the last refusal was "nonce too low ... tx 18 state 19". Now a send
is one try of at most 4 s per node (to every node at once), and after any error but a definite refusal (nonce too low,
no funds) the bot waits 15 s for the transaction's own hash (known before sending) before calling it unsent.

**Nov 19 11:51 UTC: the 5-wallet group added as wallets 4-8** (`config/rh-copier.example.toml`, the deep redo's
`rhd7_group_audit`); the box's journal: `rh start ... 8 leaders`. The book before it: 14 closed, 2 won, −0.0364 ETH.

**Nov 19 afternoon, settings changed** (`analysis/research/2026-11-19/rh_deep/`, rhd11 and rhd12): wallet 3 take profit
2.5x → 3x; wallet 2 and the group 600 → 900 s; wallet 3 and the group `max_premium = 3.0`, since a wallet without a limit
got the 25% slippage as a hidden ~1.33x limit the backtest never had (live buy #17 reverted on it). Wallet 1 unchanged.

## 4. Running it (the box, `ops@fra-long`)

Build and install (the same as every update; the unit is installed but not enabled):
```
cd ~/rugsnipe
git pull -q --ff-only origin claude/magical-einstein-k78idp && git log --oneline -1
sudo bash deploy/install.sh --role hot --force
```
The wallet, copied off before any ETH goes in (then on your computer `scp ops@BOX:rh-wallet.key ~/rugsnipe-wallets/`,
then `rm ~/rh-wallet.key` on the box):
```
sudo /opt/rugsnipe/bin/rh-copier keygen /etc/rugsnipe/keys/rh-wallet.key
sudo install -m 0600 -o ops /etc/rugsnipe/keys/rh-wallet.key ~/
```
The key file is one line, a hex private key: a wallet app (Rabby, MetaMask) can import it, which is the way to reach the
funds without the box. Fund it with ETH on Robinhood Chain (chain 4663): the official bridge from Ethereum
(docs.robinhood.com/chain/bridging/, about 10 minutes) or Across. Then the config and the start:
```
sudo install -m 0640 -o root -g rugsnipe ~/rugsnipe/config/rh-copier.example.toml /etc/rugsnipe/rh-copier.toml
sudo systemctl enable --now rh-copier && sleep 10 && sudo journalctl -u rh-copier -n 8 --no-pager
```
Reading it: `www` (the same as `qqq`; wallet column 1-3, each wallet's result and the total). Stop new buys:
`sudo touch /var/lib/rh-copier/KILL` (exits continue). Stop all: `sudo systemctl stop rh-copier` (open coins stay in
the wallet; a restart picks them up from `state.json`).
