# Wallets with wallet 4's edge, found from fresh creates (on-chain scan, Oct 28)

**Question.** Wallet 4 (`H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg`) buys 1.45+ SOL of pump coins priced in
other tokens, in the create slot or the next, and holds up to 30 minutes. Which other wallets do the same? This study
starts from every pump create of the last 24 hours, not from wallet 4's coins.

*Status: in progress (written as the steps finish).*

## Run order

Data goes to the scratchpad `SPW = /tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallets/creates`
(every RPC response cached there, gzip'd JSON under `cache/`). The Triton URL is read from the old scratchpad's
`month/.triton_url` and is never printed (errors are redacted).

```
python3 -I s1_list.py 24          # every signature on the pump mint authority, 24 h back  -> SPW/s1_sigs.json
python3 -I s2_quotes.py all 48    # each landed create: CreateEvent quote mint, creator     -> SPW/s2_creates.json
python3 -I s3_frenzy.py 16 8      # each other-quote coin: its mint's signatures since the create -> SPW/s3_coins.json, s3_sigs/
python3 -I s4_trades.py 48 4      # frenzy coins: TradeEvents in slots +0..+3                -> SPW/s4_trades.json
```
`crc.py` holds the RPC, the cache and the event decoders (the full layouts of `crates/pump-codec/src/events.rs`).

## 1. The creates (s1_list.py)

The pump mint authority `TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM` is account #1 of both `create` and `create_v2`
(`crates/pump-codec/fixtures/idl/pump.json`; `constants.rs` `MINT_AUTHORITY`), so its signature list is the list of creates.

- **Window: 2026-10-27 22:51:51 to 2026-10-28 22:51:51 UTC** (24.00 h; Beirut 00:51 Oct 28 to 00:51 Oct 29),
  slots 462,246,222 to 462,651,728 (4.693 slots/s, 0.213 s a slot).
- 50,794 signatures, **47,194 landed creates, 1,966 an hour** (lowest hour 05 UTC: 1,157; highest 20 UTC: 2,750).
- Paging the list costs 51 calls of 0.6 s; fetching each create is the cost (about 0.5-0.9 s a call, 48 in parallel).
