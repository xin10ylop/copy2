# Where to run the long copy, and which feed (researched 2026-10-28)

All prices were fetched on **2026-10-28** between 15:05 and 15:30 UTC (17:05-17:30 Beirut), unless a row says
otherwise. RTTs marked "LG" are pings from TeraSwitch's own routers (lg.teraswitch.com, 5 pings, min/avg), run at
15:20-15:28 UTC. A rented server adds roughly 0.05-0.2 ms on top of a router ping (repo estimate, speed-gap-6 §3).
"Could not verify" means the page was unreachable or did not say.

**Exchange rates used:** SOL = **$100.91** (CoinGecko; Coinbase $100.975, Kraken $100.96, ~15:14 UTC).
EUR/USD = **1.1133** (ECB reference rate, 2026-10-28).

---

## 0. The answer

**Is there something better for performance than fra1?** No, nothing that matters for this bot. The only place
that is faster is inside the TeraSwitch Frankfurt building, and that gains about 0.3-0.5 ms, which is about 0.002 of
a slot.

**Can you get the same as fra1 from Cherry Servers?** Yes. A Cherry Frankfurt **virtual dedicated server
(VDS) at €59 a month (€0.101 an hour)** puts the bot 0.4-0.6 ms from the TeraSwitch building. Ohio is about 100 ms
away. The VDS is in stock today: 10 of them.

**Feed:** use your **Triton** account. Point the bot at **`https://riptide.rpcpool.com`** with your mainnet-shared
token as `x-token`. That address is anycast. It answered in 0.09-0.11 ms from TeraSwitch's Frankfurt router, so a
Frankfurt box gets a Frankfurt Triton node. The bandwidth for this stream is about $0.2-0.5 a month, paid out of your
$75.42 credit.

| | (a) 0.1 SOL real test, this week | (b) 1 SOL run |
|---|---|---|
| Box | Cherry FRA VDS `G2-4-16gb` (EPYC 9354P, 4 vCPU, 16 GB, 100 GB NVMe), **hourly** €0.101/h | the same box, **monthly** €59 |
| Feed | Triton Riptide gRPC, mainnet-shared token | the same |
| Senders | Nozomi `fra2` (the code's default) for buys and sells, plus `rpc_send` through the Triton endpoint for sells | the same |
| Ohio | unchanged: paper on Alchemy, as the comparison | keep it for analytics and the fra1 backup |
| Cost | about **€17 ($19) for 7 days** plus the trade fees | about **$66 a month** (€59) plus ~$0.5 of feed. €73.7 ($82) if it stays on hourly billing |

**Why it pays, honestly stated** (§7):
- Geography alone makes Ohio about **0.27 slot** later on average. That is 58 ms of extra round trip (repo model)
  at today's **211 ms slot**. On European leaders it is about 0.5 slot.
- That costs roughly **0.5-1.1 SOL a month ($55-115)** at the backtest's pace. That is about the VDS price.
- If Ohio really lands 2-3 slots behind, as `going-live.md` expects, the cost is **2-8 SOL a month ($200-770)**.
  Then the VDS clearly pays.
- Measure it before you decide: run paper on both boxes for a day and compare the journal's `seen at its slot +N`
  (§8).

---

## 1. Corrections to what the repo or the brief assume

| Assumption | Today's fact | Source |
|---|---|---|
| "A slot is ~400 ms" (README "about 0.4 s") | **207.6-215.1 ms per slot**, about 211 ms average over 10 one-minute samples. So 100 ms is about **0.47 slot**, not 0.25 | `getRecentPerformanceSamples(10)` on the public RPC, 15:08 UTC. The repo had already measured 217 ms on Oct 14 (speed-geography §4) |
| Cherry FRA is "0.09 ms" from TeraSwitch FRA2 | **0.37-0.61 ms** today. The same Cherry address (185.191.117.97) was 0.089 ms on Oct 14. The traceroute shows TeraSwitch handing straight into Cherry's AS213896 (the private link exists), with 3 Cherry hops | LG Frankfurt-FRA2 ping and traceroute, 15:21-15:22 UTC |
| Cherry FRA EPYC 9375F €989 "in stock" | **0 in stock**. In stock in FRA: EPYC 9355 €599 (1), TR PRO 7965WX €979 (1), and VDS plans | api.cherryservers.com/v1/plans, 15:13 UTC |
| Triton routes by GeoDNS | Your endpoint `<your-endpoint>.mainnet.rpcpool.com` is **anycast**. It resolves to 208.91.108.10 for every client (EDNS scope /0), and ipinfo flags it anycast. It answers in 0.08 ms from TeraSwitch FRA2, 0.11 ms from AMS3 and 0.16 ms from Pittsburgh. Every unknown `*.rpcpool.com` name resolves to the same IP | getent, dns.google with client subnets, ipinfo, LG |
| Hetzner bans "everything crypto" | Its terms ban **mining, farming and plotting**. A trading bot is not named. Hetzner is also **not in Frankfurt**: Nuremberg is 3.7 ms and Falkenstein 5.1 ms from TeraSwitch FRA2 | hetzner.com/legal/terms-and-conditions; LG |

---

## 2. What decides speed for this bot (the critical path)

**Step by step:**
1. Wallet 4's transaction lands in slot N, built by leader L. L is in Frankfurt 35% of the time, Amsterdam 21%,
   elsewhere in Europe 18% (74% Europe), US 15%, Asia 11% (speed-geography §1).
2. **Feed leg.** L's block data travels to the feed's node (Triton or Alchemy). The node replays it and streams the
   transaction at `processed` (feed.rs). The stream then travels from the node to the bot.
3. The bot decides, builds and signs. This takes milliseconds.
4. **Send leg.** The bot sends to the sender (Nozomi). The sender passes it to the leader of slot N+1 or later.
   Leaders hold 4 slots in a row, so usually that is L again.

**Ohio against a Frankfurt box, for a leader in Frankfurt or Amsterdam:**

| Leg | From Ohio | From a FRA box | Extra from Ohio |
|---|---|---|---|
| Feed: L → feed node → bot | L → US node about 45 ms one way (TeraSwitch FRA↔Pittsburgh 89.5 ms RTT, LG today), then node → Ohio about 5-9 ms. From Ohio, Alchemy `solana-mainnet.g.alchemy.com` resolves to OVH Warrenton VA, and Triton anycast answered from `lb-nyc18` | L → Triton FRA node about 0.1 ms, node → bot about 0.5 ms | **~50 ms** |
| Send: bot → sender → L | Ohio → Nozomi `ewr1` (Newark) about 8 ms one way, then Nozomi's own link to FRA about 38-45 ms. Or Ohio → `fra2` directly, about 52 ms one way (Ohio↔FRA 103.6-107.9 ms RTT, speed-geography §3) | about 0.5 ms | **~50 ms** |
| **Total** | | | **~100 ms ≈ 0.47 slot** |

- **Feed and send are about half each.** A FRA box removes both.
- On US-led slots (15%), Ohio is about 70 ms *better*. On Asian slots (11%), it is about 80 ms better.
- **Averaged over every leader**, the repo's model gives a mean round trip to the leader of 101.9 ms from Ohio and
  43.8 ms from FRA. A FRA box saves **about 58 ms, 0.27 slot** (speed-geography §4).
- In plain words: about one Ohio buy in four lands one slot later than it would from Frankfurt. On a European
  leader it is about one in two.

**What geography does not explain.** fra1 landed most copies 1 slot after wallet 4: 21 of the first 35 live fills
of the launch copy (04-strategy-D README). `going-live.md` expects Ohio at 2-3 slots, which would be +1 to +2 over
fra1. Geography explains only +0.27 to +0.5 of that. Two other things may add lag, and neither is measured:
- the feed provider's own processing (a shared node falling behind);
- landing (the fee and the sender).

The journal's `seen at its slot +N`, once `7184554` is deployed, measures the feed half on each box.

**The sells are late too.** Backtests §8 shifts only our buy. A sell from Ohio also reaches the leader about 0.27
slot later on average. That matters most for take profits: 4 of 5 paper take profits came within 10 s. The real cost
of Ohio is therefore somewhat above the §7 figures. This part is not measured.

---

## 3. Triton One

| Question | Answer | Source |
|---|---|---|
| Does mainnet-shared / pay-as-you-go include Yellowstone gRPC (Dragon's Mouth)? | **Yes.** "Every Triton product is included on every plan." Riptide "is available on shared Dragon's Mouth subscriptions, and usage is billed as part of the shared service" | triton.one/pricing; docs.triton.one/project-yellowstone/riptide.md |
| gRPC endpoint | **`https://riptide.rpcpool.com:443`** ("Routing: automatic to the nearest location; no region-specific endpoints"). Your normal endpoint also takes gRPC with the token in the header: docs say token-in-URL "is not supported on gRPC and returns 403", which implies the header works there. The FAQ says "For gRPC we recommend using Riptide" | riptide.md; getting-started.md; support-faqs.md |
| Where it lands | Riptide 208.91.108.100 is anycast (TeraSwitch AS20326). LG: **0.093/0.110 ms from Frankfurt-FRA2**, 0.068/0.092 from AMS3, 0.157/0.242 from PIT1. A Frankfurt box reaches a Frankfurt node. `fra.rpcpool.com` (64.130.50.105 / .84) is in the same Frankfurt building, 0.07-0.11 ms; it is unclear whether it takes your token for gRPC (not verified). `ams.rpcpool.com` is 198.13.134.86, TeraSwitch Amsterdam | getent, ipinfo, LG |
| How the token is passed | the `x-token` header (gRPC metadata). Never in the URL for gRPC. For JSON-RPC, `https://<endpoint>.mainnet.rpcpool.com/<token>` also works. The bot already does this: `[feeds] grpc.x_token = "GRPC_TOKEN"` names a line in `api-keys.toml` (main.rs 287-299) | getting-started.md |
| Where to get the token | customers.triton.one → the **mainnet-shared** subscription → **Tokens** (create one: a name and a rate tier). The same token works for Riptide. A `403 Access forbidden` with empty `x-ratelimit-*` headers means the token is not enabled for Riptide: ask Triton support (support@triton.one or Telegram t.me/tritonone) | docs ask-API answer citing riptide.md and tokens.md. **Could not verify the portal screens myself** (login needed) |
| Rate limits, shared | JSON-RPC: **1,200 requests per 10 s per IP** for most methods; expensive methods lower; on a 429, pause 10 s. Token auth gets a "more favourable" limit than origin-restricted endpoints. gRPC stream and connection limits: "flexible", **no number published** | core-features/ratelimits.md; rate-tiers.md; pricing page |
| Price | $125 minimum deposit, prepaid, non-refundable, valid 12 months. **Streaming $0.08/GB.** JSON-RPC and unary gRPC $0.08/GB + $10 per million calls. Shred streaming FRA/AMS $1,500/mo or $0.59 per 15 min (not needed) | triton.one/pricing |
| Is bandwidth billed compressed or uncompressed? | The pricing page lists this FAQ question, but its answer is not in the page: **could not verify** | triton.one/pricing |

**What this bot's stream costs.** The filters are wallet 4 + our wallet + held mints + slots (feed.rs). My
estimate, with its basis:

| Part | Basis | Per day |
|---|---|---|
| Wallet 4's landed transactions | 16,845 landed in about 9 days (backtests §1), about 1,870 a day × 3.5-4.5 KB per update (infra-shopping §0) | 6.5-8.5 MB |
| Transactions on held mints | **mean 66 curve trades per hold** over 2,703 of its holds (`n` in `h9long/H9kuqGKN_fpaths.json`), × 27-35 copies a day, × 3.5-4.5 KB, × 2 for non-curve transactions | 12-20 MB |
| Slots | 409,500 slots a day (211 ms) × 3-7 status messages × about 55 B. The slots filter is unfiltered, and the bot sets no compression | 60-160 MB |
| **Total** | | **75-190 MB a day ≈ 2.3-5.7 GB a month ≈ $0.18-0.46 a month** |

- The JSON-RPC calls are event-driven: blockhash, statuses, simulate and send per trade (chain.rs). That is
  thousands a month, so **under $0.10**.
- The **$75.42 credit covers the feed for its whole 12-month life.**
- Alchemy at $75/TB would cost about the same, $0.17-0.43.

---

## 4. Cherry Servers

**Live stock and prices**, from Cherry's public API `api.cherryservers.com/v1/plans` (2026-10-28 15:13 UTC). Prices
are EUR, ex VAT ("taxed": false).

| Region | Plan | CPU | RAM | Disk / traffic | €/mo | €/h | In stock |
|---|---|---|---|---|---|---|---|
| **Frankfurt** | **VDS `G2-4-16gb-100nv-ded`** ("Cloud VDS 2 (Gen 2)") | 4 vCPU of AMD EPYC 9354P (2 cores / 4 threads, 3.0 GHz), dedicated | 16 GB | 100 GB NVMe / 3 TB | **59** | **0.101** | **10** |
| Frankfurt | VDS `G1-4-16gb-100nv-ded` ("Cloud VDS 2") | 4 vCPU of Intel Gold 6230R (2.1 GHz) | 16 GB | 100 GB NVMe / 10 TB | 49 | 0.084 | 12 |
| Frankfurt | VDS G2-8-32gb / G1-8-32gb | 8 vCPU | 32 GB | | 99 / 89 | 0.17 / 0.152 | 4 / 5 |
| Frankfurt | Shared VPS B2 (1-6 vCore), Performance VDS (Ryzen 7950X), Premium VDS (EPYC 9554P) | | | | 3-169 | | **0** |
| Frankfurt | bare metal EPYC 9355 (32C, 192 GB, 3 Gbps) | | | | 599 | 1.026 | 1 |
| Frankfurt | bare metal TR PRO 7965WX (24C, 512 GB) | | | | 979 | 1.676 | 1 |
| Frankfurt | bare metal Ryzen 7700X / 9900X / 7950X / 9950X, EPYC 4564P, EPYC 9375F and the rest | | | | 159-1,351 | | **0** |
| Amsterdam | VDS G1-4-16gb | | | | 49 | 0.084 | 1 (everything else in AMS: 0, except 6 × TR PRO 7975WX €1,249 and 1 × Ryzen 7700X €159) |
| Šiauliai (LT) | VDS G1 (15), ARM VDS, many bare metal plans | | | | from 49 | | yes, but **29.5 ms** from TeraSwitch FRA2 (LG): not a match for this bot |

**Billing, provisioning, terms and network:**
- **Billing:** hourly, monthly, quarterly, semi-annual or annual. Hourly servers "continue to run as long as you have
  enough credit in your Team balance" (prepaid). Could not verify whether an hourly server can be switched to
  monthly later. ([virtual-servers docs](https://www.cherryservers.com/knowledge/docs/compute/virtual-servers))
- **Provisioning:** virtual servers "within 3 minutes, on average" (same page). Bare metal "about 12 minutes"
  ([Germany page](https://www.cherryservers.com/bare-metal-dedicated-servers/germany)).
- **Facility:** "Equinix FR13 Data Center in Frankfurt", with DE-CIX (Germany page). Cherry says it has a private
  link (PNI) with TeraSwitch in Frankfurt and Amsterdam, with "Latency between Jito servers in Frankfurt and Cherry
  Servers in Frankfurt … now under 0.25ms" ([blog, Aug 26 2025, updated Nov 7 2025](https://www.cherryservers.com/blog/pni-with-teraswitch)).
  - **Measured today:** 0.37-0.61 ms (LG FRA2 → Cherry FRA). TeraSwitch FRA2 is LIKELY Equinix FR2 (repo).
  - **Same campus: could not verify.** The measured ~0.4-0.6 ms is what matters, and it is plenty.
- **Terms on crypto:** no clause bans crypto use or trading bots. Cherry sells "Solana Servers" and "Trading"
  solutions and takes crypto payments. Two clauses apply:
  - **ToS 3.3:** new clients who pay in crypto can't order the lowest-priced services until they verify identity or
    top up at least €100.
  - **ToS 6.2(c):** don't overload or disrupt the network.
  ([terms-of-service](https://www.cherryservers.com/legal/terms-of-service))
- **Network:** Cherry Frankfurt is AS213896 (`/v1/regions`). That is the same "Private Customer" AS that hosts 2.9%
  of leader slots (speed-geography §1).

---

## 5. TeraSwitch

| Item | Finding | Source |
|---|---|---|
| Website, pricing, portal, terms | teraswitch.com, `/bare-metal`, `/terms-of-service` and portal.teraswitch.com all return **403** from here: **could not verify** prices, stock, lead time or terms from the vendor | curl, 15:17 UTC |
| Bare metal (aggregator, listed Oct 3 2026) | E3-1270v6 $60; EPYC 7313P $177; 7443P $230; 7543P $270; **Ryzen 9 9950X (128 GB, 4 TB, 2×25G) $425**; EPYC 9254 $460; 9354 $490; up to Turin 9575F $1,520 | [whtop review](https://www.whtop.com/review/teraswitch.com), [9950X listing](https://www.whtop.com/plans/teraswitch.com/158524) |
| Billing | "billed by the hour from provisioning until teardown", no minimum; reserved by quote; 150 TB pooled egress EU/NA, $10/TB over | whtop (aggregator) |
| Cloud / VPS | "Cloud Compute … described as forthcoming", no prices: **no small box to buy** | whtop |
| Why it is the "best building" | Jito FRA 0.091 ms, Helius fra-sender 0.077 ms, Nozomi fra2 0.091 ms, Triton Riptide 0.093 ms from its own FRA2 router (LG today) | LG |
| Verdict for this bot | about 0.3-0.5 ms better than Cherry, about 0.002 slot. Not worth $177-425 a month against €59 | |

---

## 6. Other Frankfurt options for a small box (2 cores / 4 GB is enough; 4 / 16 is comfortable for building)

RTT to TeraSwitch FRA is from TeraSwitch's FRA2 router to a host of that provider (LG, today). **Any row under
~2 ms is as good as in-building for this bot**: 2 ms is 0.01 slot.

| Provider | Product | $/mo | Hourly? | Facility | RTT to TeraSwitch FRA (LG) | Crypto-terms risk | Notes |
|---|---|---|---|---|---|---|---|
| **Cherry Servers** | VDS G2-4-16gb (dedicated vCPU) | **$65.68** (€59) | yes, €0.101 | Equinix FR13 | **0.37-0.61** | low (sells Solana and trading servers) | in stock (10) |
| Cherry Servers | VDS G1-4-16gb | $54.55 (€49) | yes, €0.084 | same | same | low | slower CPU (2.1 GHz); in stock (12) |
| AWS eu-central-1 | c7i.large 2 vCPU / 4 GiB | **$74.35** ($0.10185/h) + IPv4 $3.65 + disk | per second | AWS Frankfurt | 0.65-0.74 (DynamoDB endpoint; the EC2 API host drops ping) | low | c7i.xlarge $148.70, c7i.2xlarge $297.40, c8g.large $66.21 ([AWS price map, published 2026-10-27](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/EU%20(Frankfurt)/Linux/index.json); IPv4 $0.005/h, [VPC pricing](https://aws.amazon.com/vpc/pricing/)). The owner already knows AWS |
| Vultr | `vhp-2c-4gb` (shared) / `voc-c-2c-4gb` (dedicated CPU) | **$24** / $40 | yes, $0.033 / $0.055 | Vultr FRA | 0.66-0.69 (fra-de-ping.vultr.com) | **could not verify** Vultr's mining/crypto clause | cheapest serious option ([api.vultr.com/v2/plans](https://api.vultr.com/v2/plans)) |
| DigitalOcean | Basic 2 vCPU / 4 GB; CPU-optimized 2 / 4 | $24; $42 | per second, monthly cap | FRA1 | **could not verify** (speedtest host did not resolve) | AUP bans mining without written permission; trading not named | [droplet pricing](https://www.digitalocean.com/pricing/droplets) |
| Latitude.sh | vm.small 4 vCPU / 16 GB; f4.metal.small (12C 4.4 GHz) | $69; $398 | yes, $0.09/h; $0.55/h | FRA / FRA2 (facility not named) | 0.69 (Latitude FRA host) | low (13% of Solana stake) | **could not verify** that VMs are offered in Frankfurt ([pricing](https://www.latitude.sh/pricing), [locations](https://www.latitude.sh/locations)) |
| OVH | VPS-1 2 vCore / 4 GB | from $4.54 | page shows a 12-month option | OVH Limburg (FRA) | 1.41 (an OVH FRA host) | could not verify | **could not verify** FRA as a location on the page ([VPS](https://www.ovhcloud.com/en/vps/)) |
| Hetzner | Cloud: shared from €6.49, dedicated vCPU from €43.49 (ex VAT) | | hourly | **Nuremberg / Falkenstein**, not Frankfurt | 3.6-3.7 (NBG1) / 5.1 (FSN1) | **medium**: terms ban crypto mining/farming/plotting; the repo cites 2022 node bans | [cloud](https://www.hetzner.com/cloud/), [terms](https://www.hetzner.com/legal/terms-and-conditions/) |
| Scaleway | DEV1-M 3 vCPU / 4 GB | ~€19 (third-party, unverified) | yes | **Amsterdam / Paris / Warsaw**: no Frankfurt | 6.8 (Scaleway AMS) | could not verify | [products availability](https://www.scaleway.com/en/docs/account/reference-content/products-availability/) |
| Contabo | Cloud VPS 10 | ~€4.40 (third-party, unverified) | no | Germany (city not verified) | not measured | could not verify | oversold shared hosting; not recommended |
| TeraSwitch | bare metal only | from $177 (aggregator) | yes | FRA2 | 0.08-0.11 (in-building) | could not verify (403) | no VPS |

---

## 7. Senders and feeds from each location

| Service | From a FRA box | From Ohio | Tip / limit | Source |
|---|---|---|---|---|
| **Nozomi** (Temporal) | `http://fra2.nozomi.temporal.xyz` (code default; 64.130.47.135, TeraSwitch FRA, 0.091 ms LG) | `ewr1` (Newark 208.91.110.41; `pit1` is the same IP), `ash1` (Ashburn) | min tip **0.001 SOL**; new keys **5 req/s per region**; limits are per region; "Nozomi also cross-forwards internally between regional servers" | [use.temporal.xyz/llms-full.txt](https://use.temporal.xyz/llms-full.txt) |
| **Helius Sender** | `http://fra-sender.helius-rpc.com/fast` (64.130.50.91, 0.077 ms LG) | `ewr-sender` (Newark) | Sender Max **0.001 SOL**; **SWQOS-only 0.000005 SOL** (`?swqos_only=true`); 50 req/s per key per region; keyless 1 req/s | [helius sender docs](https://www.helius.dev/docs/sending-transactions/sender.md) |
| **Jito** | `frankfurt.mainnet.block-engine.jito.wtf` (also `amsterdam`) | `ny.` | min tip 1,000 lamports; **1 req/s per IP per region** | [docs.jito.wtf](https://docs.jito.wtf/lowlatencytxnsend/) |
| Triton Cascade (`sendTransaction` / `/sendtx` on your endpoint) | used when `rpc_url` = the Triton endpoint (`rpc_send = true`, sells) | same | $10 per million calls | [transaction-submission](https://docs.triton.one/chains/solana/cascade/transaction-submission.md) |
| **Feed** | Triton Riptide → Frankfurt node (0.093 ms LG). Alchemy `solana-mainnet.streaming.alchemy.com` resolves to 64.130.50.164 / 198.13.138.x, the TeraSwitch FRA building (0.08-0.12 ms LG) | Alchemy `solana-mainnet.g.alchemy.com` (Ohio's journal) resolves to OVH Warrenton, VA. Triton anycast answers from New York (`x-rpc-node: lb-nyc18` from a Columbus, OH egress) | | DNS with client subnets; ipinfo |

**Is sending from Ohio to a Frankfurt sender fine?** Yes. It works and lands. Sending to `ewr1` and letting Nozomi
forward costs the same ~50 ms one way. `going-live.md` §3 step 2 (point Nozomi at the US endpoint on Ohio) is right
for Ohio. On a FRA box, keep `fra2`.

Do not add a second *buy* sender. Each sender gets its own signed copy (send.rs), so two would mean two buys.

---

## 8. Money: what delay costs, against the box

**Profit base** (backtests §6): P2 (Oct 23-27, 5 days) **+11.13 SOL** at 4 open, 1 SOL. On 136 copies that is
**+0.082 SOL a copy**, **2.23 SOL a day**, 27 copies a day. A 30-day month:
- at the backtest's pace (27 a day): **66.8 SOL ($6,740)**;
- at 30 copies a day: 73.7 SOL ($7,430);
- at 35 copies a day: 85.9 SOL ($8,670).

**Delay losses** (backtests §8, at 3 open, against landing 1 slot after wallet 4):
- 2 slots: P1 −3.0%, P2 −6.3%;
- 3 slots: −8.9% / −8.6%;
- 5 slots: −17.5% / −20.1%;
- 10 slots: −64% / −52%.

| Extra delay over fra1's +1 | Share of profit lost | SOL a month (27 / 35 copies a day) | USD a month |
|---|---|---|---|
| **~0.27 slot** (Ohio by geography alone, averaged over all leaders) | ~0.8-1.7% | 0.5-1.1 / 0.7-1.5 | **$55-150** |
| **1 slot** (lands at +2) | 3-6% | 2.0-4.0 / 2.6-5.2 | **$200-520** |
| **2 slots** (+3) | ~9% | 5.7-5.9 / 7.4-7.6 | **$580-770** |
| **4 slots** (+5) | ~18-20% | 11.7-13.4 / 15.0-17.3 | **$1,180-1,740** |

**Against the boxes:**

| Box | $/mo | In SOL |
|---|---|---|
| Cherry FRA VDS G2 (monthly) | $65.68 | 0.65 |
| Cherry FRA VDS G2 (hourly × 730) | $82.08 | 0.81 |
| Cherry VDS for one test week (hourly) | $18.89 | 0.19 |
| Cherry FRA VDS G1 | $54.55 | 0.54 |
| AWS c7i.large FRA + IPv4 | $78.00 + disk | 0.77 |
| Vultr FRA vhp-2c-4gb | $24 | 0.24 |
| TeraSwitch 9950X (aggregator) | $425 | 4.21 |
| Cherry FRA bare metal EPYC 9355 | $666.87 | 6.61 |

**Reading it:**
- If Ohio is only the geography (+0.27 slot), the FRA VDS costs about what it saves.
- If Ohio is 1 slot or more behind fra1 (the repo expects 1-2), the VDS pays 3-8 times over.
- Bare metal never pays for this bot: it buys 0.3-0.5 ms.

**Caveats:**
- These figures use the backtest's edge. Wallet 4 changed: 8 of 20 paper copies saw its early sell, against 3-6% in
  the data. If the real edge is half, every SOL figure halves.
- At **0.1 SOL** stakes the delay costs a tenth of these figures, about 0.05-0.5 SOL a month. The test is about
  measuring, not money.

---

## 9. Recommendation and steps

### (a) The 0.1 SOL real test this week

1. **Box.** Cherry FRA VDS `G2-4-16gb-100nv-ded`, **hourly** (€0.101/h, about €17 for 7 days).
   - **Why not test on Ohio?** The test must show where buys land for the 1 SOL run, and that run should be from
     Frankfurt. From Ohio you would measure Ohio.
   - **Zero-cost alternative:** run the test on Ohio with Nozomi `ewr1` (going-live §3). Then expect buys about
     0.27 slot later on average than from FRA (0.5 slot on European leaders).
2. **Feed.** Triton Riptide `https://riptide.rpcpool.com`, the mainnet-shared token as `GRPC_TOKEN`. Cost about
   $0.1 for the week, from the credit.
3. **Senders.** Nozomi `fra2` (the default). Keep `rpc_send = true` with `RPC_URL` = your Triton endpoint, so sells
   also go through Triton's sender.
4. **Order of work:**
   - Day 0: order, install, acceptance test 1.
   - Day 0-1: paper on both boxes, acceptance test 2.
   - Then: new long wallet on the FRA box, 0.1 SOL, `max_open = 1`, `mode = "on"` (going-live §3 steps 1, 3-6).
   - **Only one box ever runs live.** Ohio stays in paper.

### (b) The 1 SOL run

Keep the same Cherry VDS on **monthly** billing (€59 ≈ $66). If Cherry can't switch an hourly server, order a
monthly one and move; €73.7 ($82) if it stays hourly. Keep Triton Riptide (≈ $0.2-0.5 a month) and Nozomi `fra2`.

**Total: about $66 a month plus Ohio.**

**Fallback feed:** Alchemy streaming. Its Frankfurt node is also in the TeraSwitch FRA building. You already have
the key on Ohio.

**Don't buy bare metal for this.**

**Later, one change at a time:** an A/B of Helius `swqos_only` (0.000005 SOL minimum tip) against Nozomi
(0.001 SOL) for sells. It could save about 0.001 SOL per transaction, ≈ 1-2 SOL a month at 1 SOL stakes. Not
measured; only after the 1 SOL run is stable.

### Signup and ordering steps

**Cherry Servers (on your laptop, in the browser):**
1. cherryservers.com → **Sign up**, verify the email.
2. Add funds. Card is simplest. If you pay in crypto as a new client, either verify your identity or top up at
   least €100 (ToS 3.3). Hourly servers draw from the prepaid balance.
3. **Deploy → Virtual servers → Cloud VDS → Frankfurt, DE → "Cloud VDS 2 (Gen 2)" `G2-4-16gb-100nv-ded` →
   Ubuntu 24.04 → billing Hourly**. Add your SSH **public** key, name it `fra-long`, deploy. It takes about 3 minutes.

**Triton (in the browser):**
1. customers.triton.one → the **mainnet-shared** subscription → **Tokens** → create one (for example `fra-long`).
2. Copy the token straight into the box's key file (step 3 below). Never into chat or a terminal line.
3. If the bot later logs a 403, ask Triton support to enable Riptide / gRPC on that token.

**The box.** Same as `03-strategy-A-long-copy/deploy-ohio.md` §1, but with `--role hot`. That role creates
`long.toml` and the `rugsnipe-long` unit (install.sh lines 104-106, 458-466). Never enable `rugsnipe-hot`.
1. Clone upstream `xin10ylop/rugsnipe`, branch `claude/eloquent-mayer-264bxk` (at `7184554` or later), into
   `~/rugsnipe`. Run `sudo bash deploy/install.sh --role hot --dry-run`, then without `--dry-run`. This sets chrony to
   Jito's Frankfurt NTP.
2. In `/etc/rugsnipe/rugsnipe.toml` set:
   - `[feeds]`: `grpc = { enabled = true, url = "https://riptide.rpcpool.com", x_token = "GRPC_TOKEN", stale_ms = 2_000, bundle_run = true }`;
   - `[senders]`: `nozomi = { enabled = true, url = "http://fra2.nozomi.temporal.xyz", key = "NOZOMI_KEY", min_tip = 1_000_000 }`.
3. `sudo nano /etc/rugsnipe/keys/api-keys.toml` (root, 0400). Type in from the dashboards:
   - `GRPC_TOKEN` (Triton);
   - `NOZOMI_KEY` (Nozomi dashboard);
   - `RPC_URL` (`https://<your-endpoint>.mainnet.rpcpool.com/<token>`).

   Do not copy fra1's backup to this box.
4. Keep `mode = "log"` in `/etc/rugsnipe/long.toml` and start `rugsnipe-long`.

### Acceptance tests

**Test 1, network** (on the new Cherry box, right after it boots; no repo paths, so no `cd`):
```
getent hosts riptide.rpcpool.com
for ip in 64.130.50.88 64.130.50.91 64.130.47.135 208.91.108.100; do ping -c 50 -i 0.2 -q $ip | tail -1; done
mtr -rwc 20 64.130.50.88
```
What each part should print:
- `getent` prints `208.91.108.100  riptide.rpcpool.com`.
- The loop prints four `rtt min/avg/max/mdev = …` lines (Jito FRA, Helius fra-sender, Nozomi fra2, Triton Riptide).
  **Pass: every avg below 1 ms.** About 0.4-0.7 ms is expected (LG today: Cherry 0.37-0.61 ms from the FRA2 router).
  - Riptide at about 6 ms means Triton's Amsterdam node is serving you. That is fine.
  - About 90 ms means the anycast goes to the US: open a Triton ticket.
- `mtr` should show Cherry hops (AS213896), then TeraSwitch (AS20326), with no ocean crossing.

**Test 2, feed** (on the new box first, then the same grep on Ohio, `ubuntu@ip-172-31-17-131`; Ohio must be on
`7184554`):
```
cd ~/rugsnipe
sudo journalctl -u rugsnipe-long -n 5 --no-pager
sudo journalctl -u rugsnipe-long --since "2026-10-29 00:00" --no-pager | grep -E 'paper-buy|paper-refused'
```
What each part should print:
- The first command shows `long feed connected` and no `403`.
- The second shows lines ending `seen at its slot +N`. Expect N = 0 on most lines on Frankfurt. Compare the same coins
  on Ohio.
- **Ohio's real extra ≈ 2 × (Ohio's N − Frankfurt's N)**: the send half is about the size of the feed half (§2).

**Test 3, real (0.1 SOL)** (on the new box):
- Run `rugsnipe-long status --config /etc/rugsnipe/long.toml --chain` and read each buy's slot against wallet 4's.
- **Pass:**
  - most buys land at its slot +1, almost none past +2;
  - every sell lands, including a pool sell after graduation;
  - the chain result matches the journal (going-live §3 step 6).

**Decision for (b):**
- **Stay in Frankfurt** if test 2 shows Frankfurt ahead of Ohio by ≥ 0.3 slot on average, or if test 3 lands
  mostly at +1.
- If Frankfurt and Ohio come out even (under 0.1 slot apart), the box saves about what it costs. Keep it anyway
  for the faster sells, or drop it to save $66 a month.

---

## 10. The Ohio box

**Terminated by the owner on Oct 28 evening, after this was written.** fra1's backup went with it; the wallet in it
was already empty (its SOL went to the owner's Phantom on Oct 27, 05-live), and its API keys should be rotated anyway.
The section below is kept as written; none of it applies any more. The Frankfurt box is the only box.

- **Keep it.** It holds the **only copy of fra1's backup** (wallet and API keys, `/root/backups/fra1-backup.tgz`,
  root only). **Never Terminate it.** AWS Stop keeps the disk; Terminate deletes it.
- **Don't copy the backup to the Cherry box**, to git or to any cloud sync. The new box gets fresh keys typed in
  from the dashboards.
- **Use:**
  - analytics and research scripts, `rugsnipe-history`;
  - the paper comparison in test 2;
  - a cold standby (paper only).
- **Once the FRA box is live**, either stop `rugsnipe-long` on Ohio or keep it in paper as a shadow. **Never run two
  live bots.**
- **To cut cost:** downsize the instance (Stop → change type → Start), or Stop it when idle. Its instance type is
  not in the repo, so its current price is not known here.
- **Switching Ohio's feed to Triton gains nothing measurable.** From Ohio, Triton's anycast serves from New York;
  Ohio's Alchemy node is in Virginia. The gain comes from moving the box.

---

## 11. Could not verify

- TeraSwitch: prices from the vendor, stock, lead time, terms (403).
- Triton:
  - whether bandwidth is billed compressed or uncompressed;
  - gRPC stream and connection limits;
  - the portal screens (login needed);
  - whether `fra.rpcpool.com` accepts your token for gRPC.
- Cherry:
  - whether FR13 is the same campus as TeraSwitch FRA2;
  - whether hourly billing can switch to monthly.
- Vultr: its terms on crypto.
- DigitalOcean: FRA1's RTT to TeraSwitch.
- Latitude: whether VMs are offered in Frankfurt.
- OVH: whether the VPS page's plans are in Frankfurt.
- Scaleway and Contabo: prices (third-party only).
- The real feed lag of Alchemy and Triton shared nodes, and Ohio's real landing. Only tests 2 and 3 settle these.
- The status messages per slot that this Yellowstone version sends with an empty slots filter (3 to 7 assumed).

## Sources (all fetched 2026-10-28 unless noted)

- Triton: [pricing](https://triton.one/pricing); [Riptide](https://docs.triton.one/project-yellowstone/riptide.md);
  [Dragon's Mouth](https://docs.triton.one/project-yellowstone/dragons-mouth-grpc-subscriptions.md);
  [getting started](https://docs.triton.one/getting-started.md); [routing](https://docs.triton.one/core-features/geodns.md);
  [rate limits](https://docs.triton.one/core-features/ratelimits.md); [rate tiers](https://docs.triton.one/account-management/api-access/rate-tiers.md);
  [FAQs](https://docs.triton.one/core-features/support-faqs.md); [tokens](https://docs.triton.one/account-management/api-access/tokens.md);
  [subscription types](https://docs.triton.one/account-management/api-access/subscription-types.md);
  [streaming checklist](https://docs.triton.one/chains/solana/streaming/streaming-troubleshooting-checklist.md);
  [Cascade /sendtx](https://docs.triton.one/chains/solana/cascade/transaction-submission.md).
- Cherry Servers: [plans API](https://api.cherryservers.com/v1/plans) and [regions API](https://api.cherryservers.com/v1/regions)
  (15:13 UTC); [Germany page](https://www.cherryservers.com/bare-metal-dedicated-servers/germany);
  [PNI with TeraSwitch](https://www.cherryservers.com/blog/pni-with-teraswitch);
  [virtual servers](https://www.cherryservers.com/knowledge/docs/compute/virtual-servers);
  [naming convention](https://www.cherryservers.com/knowledge/docs/compute/virtual-servers/naming-convention);
  [terms of service](https://www.cherryservers.com/legal/terms-of-service).
- TeraSwitch: [whtop review](https://www.whtop.com/review/teraswitch.com) and [9950X listing](https://www.whtop.com/plans/teraswitch.com/158524)
  (aggregator, listed Oct 3 2026); [looking glass](https://lg.teraswitch.com) (all LG pings, 15:20-15:28 UTC).
- Others: [AWS EC2 price map, Frankfurt](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/EU%20(Frankfurt)/Linux/index.json)
  (published 2026-10-27); [AWS VPC pricing](https://aws.amazon.com/vpc/pricing/); [Vultr plans API](https://api.vultr.com/v2/plans);
  [DigitalOcean droplets](https://www.digitalocean.com/pricing/droplets); [Latitude pricing](https://www.latitude.sh/pricing);
  [Latitude locations](https://www.latitude.sh/locations); [OVH VPS](https://www.ovhcloud.com/en/vps/);
  [Hetzner cloud](https://www.hetzner.com/cloud/); [Hetzner terms](https://www.hetzner.com/legal/terms-and-conditions/);
  [Scaleway availability](https://www.scaleway.com/en/docs/account/reference-content/products-availability/);
  [cloud-mercato DEV1-M](https://pcr.cloud-mercato.com/providers/scaleway/flavors/dev1-m);
  [Contabo price tracker](https://pricingsaas.com/companies/contabo).
- Feeds and senders: [Alchemy gRPC pricing](https://support.alchemy.com/articles/5952597732-how-is-solana-grpc-yellowstone-streaming-priced);
  [Nozomi docs](https://use.temporal.xyz/llms-full.txt); [Helius Sender](https://www.helius.dev/docs/sending-transactions/sender.md);
  [Jito](https://docs.jito.wtf/lowlatencytxnsend/).
- Prices of SOL and EUR: [CoinGecko](https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd,eur),
  [Coinbase](https://api.coinbase.com/v2/prices/SOL-USD/spot), [Kraken](https://api.kraken.com/0/public/Ticker?pair=SOLUSD),
  [ECB](https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml).
- Chain: public RPC `getRecentPerformanceSamples` (15:08 UTC).
- Repo:
  - docs/research/speed-geography.md §1, §3, §4; speed-gap-6.md §3, §5; infra-shopping-2026.md §0, §1;
  - 03-strategy-A-long-copy/backtests.md §1, §6, §8, §11; going-live.md §1, §3;
  - 04-strategy-D-launch-copy/README.md;
  - crates/rugsnipe-long/src/feed.rs, send.rs, main.rs, chain.rs; config/rugsnipe.example.toml; deploy/install.sh;
  - the dataset `data/datasets/h9long.tar.xz` (`H9kuqGKN_fpaths.json`, the hold trade counts).
