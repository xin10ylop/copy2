# Step 4c: what the fee tier is made of. Wallet 4's own buy event decoded in full (the 35 fields of
# crates/pump-codec/src/events.rs TradeEvent): protocol fee, creator fee, cashback, buyback and holder-rewards basis
# points, the mayhem flag. Adds them to SKIPQ/features.json and tabulates the copies' results by each part.
#   python3 -I fee_parts.py SPD SKIPQ
import sys, os, json, struct, collections
SPD, SKIPQ = sys.argv[1], sys.argv[2]
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
sys.path.insert(0, SP + "/rivalpnl"); sys.path.insert(0, "/home/user/rugsnipe/analysis")
import common as C
from rugsnipe_analysis import events as E
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def b58(b):
    n = int.from_bytes(b, "big"); out = ""
    while n: n, r = divmod(n, 58); out = B58[r] + out
    return "1" * (len(b) - len(b.lstrip(b"\0"))) + out
def decode(d):
    o = [0]
    def take(n):
        if o[0] + n > len(d): raise IndexError
        v = d[o[0]:o[0] + n]; o[0] += n; return v
    left = lambda: len(d) - o[0]
    u64 = lambda: struct.unpack("<Q", take(8))[0]
    opt = lambda f: f() if left() else None
    e = dict(mint=b58(take(32)), sol=u64(), tok=u64(), buy=take(1)[0] == 1, user=b58(take(32)), ts=struct.unpack("<q", take(8))[0], vsol=u64(), vt=u64())
    opt(u64); opt(u64); opt(lambda: take(32)); e["fee_bps"] = opt(u64); opt(u64); e["creator"] = opt(lambda: b58(take(32))); e["cfee_bps"] = opt(u64); opt(u64)
    opt(lambda: take(1)); opt(u64); opt(u64); opt(u64); opt(u64)
    if left(): n = struct.unpack("<I", take(4))[0]; take(n)
    e["mayhem"] = opt(lambda: take(1)[0]); e["cashback_bps"] = opt(u64); opt(u64); e["buyback_bps"] = opt(u64); opt(u64)
    if left(): n = struct.unpack("<I", take(4))[0]; take(34 * n); e["shareholders"] = n
    e["quote"] = opt(lambda: b58(take(32))); opt(u64); opt(u64); opt(u64); e["holder_bps"] = opt(u64); opt(u64); opt(u64)
    return e
files = collections.defaultdict(list)
for f in os.listdir(f"{SPD}/w4tx"): files[f.split("_")[0]].append(f)
D = json.load(open(f"{SKIPQ}/features.json")); miss = 0
for f in D:
    slot, m8 = f["key"].split("_"); got = None
    for fn in files.get(slot, []):
        tx = json.load(open(f"{SPD}/w4tx/{fn}")); m = tx["meta"]
        ks = tx["transaction"]["message"]["accountKeys"] + sum(((m.get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
        for g in m.get("innerInstructions") or []:
            for ix in g["instructions"]:
                if ks[ix["programIdIndex"]] != C.PUMP: continue
                raw = C.b58d(ix.get("data", ""))
                if raw[:8] == E.EVENT_IX_TAG and raw[8:16] == E.DISC_TRADE:
                    try: e = decode(raw[16:])
                    except Exception: continue
                    if e["mint"].startswith(m8) and e["user"] == W4 and e["buy"]: got = e
    if not got: miss += 1; continue
    for k in ("fee_bps", "cfee_bps", "cashback_bps", "buyback_bps", "holder_bps", "mayhem", "shareholders", "creator"): f[k] = got.get(k)
    f["fee_total"] = sum(got.get(k) or 0 for k in ("fee_bps", "cfee_bps", "cashback_bps", "buyback_bps", "holder_bps"))
json.dump(D, open(f"{SKIPQ}/features.json", "w"))
for f in D: f["net"] = (f["net_4"] + f["net_8"] + f["net_slot+1"]) / 3
print(f"{len(D)} buys, {miss} without a decoded event")
def tab(title, keyf):
    g = collections.defaultdict(list)
    for f in D:
        if "fee_bps" in f: g[keyf(f)].append(f)
    print(f"\n== {title}: copies, take profits, net A / B / C, all, a copy")
    for k, r in sorted(g.items(), key=lambda kv: -len(kv[1])):
        if len(r) < 8: continue
        b = [sum(f["net"] for f in r if f["blk"] == j) for j in range(3)]
        print(f"   {str(k):46s} {len(r):4d} {sum(f['why_4'] == 'tp' for f in r):3d} | {b[0]:+6.2f} {b[1]:+6.2f} {b[2]:+6.2f} | {sum(b):+6.2f} | {100 * sum(b) / len(r) / 0.5:+6.1f}%")
tab("(protocol, creator, cashback, buyback, holder rewards) basis points", lambda f: (f["fee_bps"], f["cfee_bps"], f["cashback_bps"], f["buyback_bps"], f["holder_bps"]))
tab("protocol fee bps", lambda f: f["fee_bps"]); tab("creator fee bps", lambda f: f["cfee_bps"]); tab("cashback bps", lambda f: f["cashback_bps"])
tab("buyback bps", lambda f: f["buyback_bps"]); tab("holder rewards bps", lambda f: f["holder_bps"]); tab("mayhem flag", lambda f: f["mayhem"])
tab("all five parts together, bps", lambda f: f["fee_total"]); tab("shareholders in the event", lambda f: f.get("shareholders"))
