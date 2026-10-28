# Does our buy fit with 3 hops? Bytes of the buy txb.rs builds (compute budget x2; when paying wSOL: create the wSOL ATA,
# transfer, SyncNative; create the coin ATA; multi_hop_swap with 16 + 5 a hop accounts; close the wSOL ATA; the tip),
# counted from the wire format: legacy as built, v0 with an address lookup table holding the accounts that never change
# (PumpSwap's global and fee configs and event authority, pump's global, fee config and event authority, Token-2022,
# pump's program, our volume accumulator, the buyback fee account, the wSOL and WBTC mints; invoked programs and the tip
# account stay static), and the variants that drop the wSOL wrap (a wSOL account kept funded, as wallet 4 does). Checked
# on the 2-hop wSOL buy measured on mainnet (1,088 bytes, docs/20 section 3: simulated, no tip). Also: pump's own lookup
# table (constants.rs PUMP_MAINNET_ALT) read from the chain, which of our fixed accounts it holds; and wallet 4's own buys
# by hops: transaction version and bytes (routes.json).   python3 -I txsize.py
import sys, os, json, base64, statistics, collections
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
SPX = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/more"
sys.path.insert(0, SP + "/month"); sys.path.insert(0, SP + "/rivalpnl")
import tri, common as C
LIMIT = 1232
FIXED = {"PS_GLOBAL_CONFIG": "ADyA8hdefvWN2dbGGWFotbzWxrAvLW83WG6QCVXvJKqw", "PS_FEE_CONFIG": "5PHirr8joyTMp9JMm6nW7hNDVyEYdkzDqazxPD7RaTjx",
         "PS_EVENT_AUTHORITY": "GS4CU59F31iL7aR2Q8zVS8DRrcRnXX1yjQ66TqNVQnaR", "GLOBAL": "4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf",
         "FEE_CONFIG": "8Wf5TiAheLUqBrKXeYg2JtAFFMWtKdG2BSFgqUcPVwTt", "EVENT_AUTHORITY": "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1",
         "TOKEN_2022": "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb", "PUMP": "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
         "WSOL_MINT": "So11111111111111111111111111111111111111112", "WBTC_MINT": "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh",
         "SPL_TOKEN": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "SYSTEM": "11111111111111111111111111111111",
         "PUMP_SWAP": "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"}
def cu(n): return 1 if n < 128 else 2
PUMP_ALT_HOLDS = None                           # set below from the chain: our ALT candidates pump's table has
def size(hops, wrap=True, tip=True, alt=False):
    """bytes of our buy: hops = the route's hop count from wSOL"""
    keys = {"user": "s", "wsol_ata": "w", "coin_ata": "w", "uva": "w", "buyback": "w", "COMPUTE_BUDGET": "p", "ATA": "p",
            "SYSTEM": "p", "SPL_TOKEN": "p", "PUMP_SWAP": "p"}
    for k in ("PS_GLOBAL_CONFIG", "PS_FEE_CONFIG", "PS_EVENT_AUTHORITY", "GLOBAL", "FEE_CONFIG", "EVENT_AUTHORITY", "TOKEN_2022", "PUMP", "WSOL_MINT"):
        keys[k] = "r"
    for h in range(hops):                       # a new mint (the coin last), a market, two vaults per hop
        keys[f"mint{h}"] = "r"; keys[f"market{h}"] = "w"; keys[f"vb{h}"] = "w"; keys[f"vq{h}"] = "w"
    if tip: keys["tip"] = "w"
    # instructions: (accounts, data bytes)
    ixs = [(0, 5), (0, 9)]                      # SetComputeUnitLimit, SetComputeUnitPrice
    if wrap: ixs += [(6, 1), (2, 12), (1, 1)]   # create the wSOL ATA, transfer, SyncNative
    ixs += [(6, 1), (16 + 5 * hops, 24)]        # create the coin ATA, multi_hop_swap
    if wrap: ixs += [(3, 1)]                    # close the wSOL ATA
    if tip: ixs += [(2, 12)]
    in_alt = {"PS_GLOBAL_CONFIG", "PS_FEE_CONFIG", "PS_EVENT_AUTHORITY", "GLOBAL", "FEE_CONFIG", "EVENT_AUTHORITY",
              "TOKEN_2022", "PUMP", "WSOL_MINT", "uva", "buyback"} if alt else set()
    if alt == "pump": in_alt = {k for k in in_alt if k in PUMP_ALT_HOLDS}
    static = [k for k in keys if k not in in_alt]
    n = 1 + 64 + 3 + cu(len(static)) + 32 * len(static) + 32 + cu(len(ixs)) + sum(1 + cu(a) + a + cu(d) + d for a, d in ixs)
    if alt:
        n += 1 + 1 + 32 + 1 + sum(keys[k] == "w" for k in in_alt) + 1 + sum(keys[k] != "w" for k in in_alt)
    return n, len(keys)
alt = tri.rpc("getAccountInfo", ["Hyif6eWb8x88RVrvjPfabsgRYnwkVnyByEXTVTXbUcyP", {"encoding": "base64"}], cache=False)["value"]
d = base64.b64decode(alt["data"][0]); addrs = [C.b58e(d[56 + 32 * i:88 + 32 * i]) for i in range((len(d) - 56) // 32)]
deact = int.from_bytes(d[4:12], "little")
PUMP_ALT_HOLDS = {k for k, v in FIXED.items() if v in addrs}
n2, _ = size(2, tip=False)
print(f"check: 2-hop wSOL buy without a tip {n2} bytes (measured on mainnet: 1,088)")
print(f"{'hops':>4s} {'keys':>4s} {'legacy':>7s} {'legacy, no wrap':>15s} {'v0 + our ALT':>12s} {'v0 + our ALT, no wrap':>21s} {'v0 + pump ALT':>13s}   (limit {LIMIT}; with the tip)")
for h in (1, 2, 3, 4):
    a, k = size(h); b, _ = size(h, wrap=False); c, _ = size(h, alt=True); e, _ = size(h, wrap=False, alt=True); p, _ = size(h, alt="pump")
    f = lambda x: f"{x}{'*' if x > LIMIT else ' '}"
    print(f"{h:4d} {k:4d} {f(a):>7s} {f(b):>15s} {f(c):>12s} {f(e):>21s} {f(p):>13s}")
print("   * over the limit")
print(f"pump's lookup table Hyif6eWb: owner {alt['owner'][:8]}, {len(addrs)} addresses, deactivation slot {'none' if deact == 2**64 - 1 else deact}")
print("   holds: " + ", ".join(k for k, v in FIXED.items() if v in addrs) + "; lacks: " + (", ".join(k for k, v in FIXED.items() if v not in addrs) or "-"))
RT = json.load(open(f"{SPX}/routes.json")); QS = {q["sig"]: q for q in json.load(open(f"{SPX}/quotes.json"))}
g = collections.defaultdict(list)
for s, r in RT.items():
    g[(len(r["hops"]) if r.get("hops") else 0, r.get("version"), r.get("alts"))].append(r["bytes"])
print("wallet 4's own buys (1.45+ SOL, other quotes): hops (0 = no multi_hop_swap), version, lookup tables: bytes min / median / max")
for k in sorted(g): print(f"   {k}: {len(g[k])} buys, {min(g[k])} / {statistics.median(g[k]):.0f} / {max(g[k])}")
