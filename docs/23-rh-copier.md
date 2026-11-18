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
| Signal | A copied wallet's buy (CurveBuy's recipient) of at least `min_its_eth`. One copy per coin within an hour; `max_open` (4); `daily_stop_eth` (0.06); the `KILL` file. |
| Its price | The curve's reserves at the end of its buy's block (eth_call at that block). The coin type is the ETH that was in the curve before its buy. |
| Buy | `buy(quoteIn, minTokensOut, recipient)` with value = the stake. `minTokensOut` is what the stake buys at the price limit (1.5x its price), so a buy that would fill higher reverts on chain. With no limit (wallet 3), the expected amount less 25%. No buy when the price is already over the limit, or the curve holds 3.8+ ETH (it graduates at 4.2 into a Uniswap v4 pool the bot does not trade). |
| Approve | `approve(curve, max)` on the coin goes out right behind the buy (the next nonce), so the sale is ready at once. |
| Exits, first one wins | graduation guard (3.8 ETH in the curve), take profit, sell pressure (other wallets' sales minus buys over the window, after `from` s), stall (no new high for `stall_s`), time (`hold_s` after its buy). All measured against its price, as the research did. |
| Sale | `sell(balance, minQuoteOut, us)`: sells the wallet's exact token balance; minimum = the expected ETH less 30%, then half that, then 0. Three failed tries: retried 5 s later, again and again. |
| Sends | Signed here (EIP-1559, chain 4663, the fee cap 3x the gas price); each goes to PublicNode and the official RPC; the receipt confirms it. Gas on Nov 18: 0.02 gwei, a buy ~100k gas, a sale ~80k: about 0.000003 ETH a trade. |
| Book | `/var/lib/rh-copier`: `state.json` (open positions, kept across restarts), `closed.jsonl`, `failed.jsonl`, `its.json`. |

Checked on Nov 18 against the chain: our buy call simulated on a live curve (6.07M tokens for 0.02 ETH; a too-high
minimum reverts); our sale call simulated one block before two real sales gave their exact ETH out; every RPC method on
both nodes. A 7-minute log-mode run on the live feed (two very active bots added as test wallets) copied 2 buys and
closed both. The official RPC ran 7-10 blocks behind PublicNode, so reads and receipts use PublicNode
(`rpc_url`) and history the official RPC (`logs_url`). Engine tests: `cargo test -p rh-copier` (13).

## 3. Risks, said plainly

- Nothing has been sent from it yet. The first real trades are its mechanics test: check them on chain (Blockscout),
  as `03-strategy-A-long-copy/deploy-frankfurt.md` §6 did for wallet 4.
- Other copy bots already follow wallets 1 and 2 within 2 blocks (`out/rh8_cobuyers.txt`). The backtest landed us 2,
  3 and 5 blocks late; the feed adds about 1 s (10 blocks) at worst on a slow moment. The price limit protects the buy.
- Coins that graduate while held are sold at 3.8 ETH by the guard; the pool is not traded.
- Nov 15 shows almost no copies for all three: a quiet day or a gap in the fetched data (not checked yet).
- PublicNode's free endpoints are the only live feed found (no key). If they fail for long, nothing is copied (open
  positions still exit on the clock, and reserves are re-read every 15 s).

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
Reading it: `rhq` (the same as `qqq`; wallet column 1-3, each wallet's result and the total). Stop new buys:
`sudo touch /var/lib/rh-copier/KILL` (exits continue). Stop all: `sudo systemctl stop rh-copier` (open coins stay in
the wallet; a restart picks them up from `state.json`).
