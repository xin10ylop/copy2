# Does wallet 4's operator trade on other chains? (Nov 18)

The owner: "track wallet 4 to check if he trades on other chains, robinhood, bnb, base". A Solana address has no twin on
an EVM chain, so the link has to come from money that crossed. The one crossing on record (`07-rework-2026-10-28/
wallet-check.md` §5): on Oct 17 the predecessor `HxcdEi6C` sent 50 + 90 SOL through a cross-chain swap program
(`J88B7gma`, `XSwapNative`), at 21:48 and 21:53 UTC (`4MunAtQA…`, `wh2vUqbs…`).

`xchain.py` (the public Solana RPC: Alchemy's monthly capacity was used up on Nov 18) fetched both. The instruction
data, after the 8-byte discriminator: the amount (50.0 / 90.0 SOL as a u64), then a 20-byte receiver,
**`0x387a760358943e4ea0ca87fc1d37e35f587c416b` in both**.

That address on 11 chains (PublicNode RPCs, Nov 18): Ethereum 45 sent transactions, 0.388 ETH; BNB 5; Avalanche 9,
2.93 AVAX; **Base, Arbitrum, Optimism, Polygon, Linea and Robinhood Chain: 0**. Its Ethereum history (Blockscout,
2024-11 to 2026-11): Lido staking (`submit`), yield-vault deposits, USDC transfers, two LiFi swaps; on Oct 17, 22:01-
22:06 UTC (right after the two swaps) 3.5 ETH staked, a LiFi swap and a USDC vault deposit. Many 1e-9 ETH transfers in
from `0x3771…` lookalikes are address poisoning. **A savings wallet, not a trading bot**: no memecoin trading by this
address on any EVM chain checked. The operator may hold other addresses; wallet 4's own outflows since Oct 28 were not
re-checked (Alchemy at its cap).

Robinhood Chain (chain 4663, an Arbitrum Orbit L2, ~35,000 blocks an hour): PublicNode's free endpoint refuses logs
older than the latest blocks ("archive requests require a personal token"), so a wallet screen there needs a keyed
provider (Bitquery's indexed trades fit best: Pons curve trades, graduations, Uniswap v4 swaps, by trader).
