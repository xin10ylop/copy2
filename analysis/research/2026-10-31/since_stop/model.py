# The long copy as built, coin by coin, on wallet 4's routable 1.45+ SOL buys (scan.out from examples/scan.rs): each
# coin's curve followed trade by trade for 31 minutes after its buy, our buy landing N trades of the coin after its own
# (block order from getBlock for its slot and the next two), refused past 1.25x the price its buy left (the floor since
# bfc2fa7), then TP 2.0x / stop 0.8x of that price / 1790 s, the sell filling on the trade after the trigger. Our own
# buy and sell are exact constant-product quotes on the event's reserves with its fee bps; our quote stays in the curve
# for the later trades (the cautious "q" model). Costs: one pool hop each way (0.3%), 0.0026 SOL of tips and fees a
# round trip, 0.0004 a refused buy. Quote tokens are valued at wallet 4's own rate at its buy (no drift).
#   python3 -I model.py SPD [STAKE] [N]    (SPD = the data folder: w4tx/, scan.out, routable.json)
import sys, os, json, gzip, time, urllib.request, concurrent.futures as cf, datetime, statistics
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
sys.path.insert(0, SP + "/rivalpnl"); sys.path.insert(0, "/home/user/rugsnipe/analysis")
import common as C
from rugsnipe_analysis import events as E
R = open(f"{SP}/month/.triton_url").read().strip()
SPD = sys.argv[1]; STAKE = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0; N = int(sys.argv[3]) if len(sys.argv) > 3 else 4
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
CACHE = f"{SPD}/cache"; os.makedirs(CACHE, exist_ok=True)
def call(m, p, key=None):
    path = f"{CACHE}/{key}.json.gz" if key else None
    if path and os.path.exists(path): return json.load(gzip.open(path))
    for k in range(8):
        try:
            req = urllib.request.Request(R, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"content-type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=60))
            if "error" in r: raise RuntimeError(str(r["error"])[:100])
            res = r["result"]
            if path and res is not None: json.dump(res, gzip.open(path, "wt"))
            return res
        except Exception:
            time.sleep(1.5 * (k + 1))
    return None
TXO = {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}
# wallet 4's transactions: (blockTime, signature) for anchors, and the full mint of each routable buy
w4 = []; mints = {}
for f in os.listdir(f"{SPD}/w4tx"):
    t = json.load(open(f"{SPD}/w4tx/{f}")); s = t["transaction"]["signatures"][0]; w4.append((t["blockTime"], s))
    for b in t["meta"].get("postTokenBalances") or []:
        if b.get("owner") == W4: mints.setdefault((t["slot"], b["mint"][:8]), b["mint"])
w4.sort()
rows = [r for r in json.load(open(f"{SPD}/routable.json")) if r["ok"]]
import struct
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def b58(b):
    n = int.from_bytes(b, "big"); out = ""
    while n: n, r = divmod(n, 58); out = B58[r] + out
    return "1" * (len(b) - len(b.lstrip(b"\0"))) + out
def decode_trade(d):
    """pump's TradeEvent payload (after tag and discriminator), the field order of crates/pump-codec/src/events.rs
    decode_trade: the quote fields for coins priced in another token sit after a variable-length shareholders list."""
    o = [0]
    def take(n):
        if o[0] + n > len(d): raise IndexError
        v = d[o[0]:o[0] + n]; o[0] += n; return v
    left = lambda: len(d) - o[0]
    u64 = lambda: struct.unpack("<Q", take(8))[0]
    opt = lambda f: f() if left() else None
    e = dict(mint=b58(take(32)), sol=u64(), tok=u64(), buy=take(1)[0] == 1, user=b58(take(32)), ts=struct.unpack("<q", take(8))[0],
             vsol=u64(), vt=u64())
    e["real_sol"] = opt(u64); e["real"] = opt(u64); opt(lambda: take(32)); e["fee_bps"] = opt(u64); opt(u64)
    opt(lambda: take(32)); e["cfee_bps"] = opt(u64); opt(u64); opt(lambda: take(1)); opt(u64); opt(u64); opt(u64); opt(u64)
    if left(): n = struct.unpack("<I", take(4))[0]; take(n)                      # ix_name
    opt(lambda: take(1)); opt(u64); opt(u64); opt(u64); opt(u64)                  # mayhem, cashback x2, buyback x2
    if left(): n = struct.unpack("<I", take(4))[0]; take(34 * n)                 # shareholders
    e["quote_mint"] = opt(lambda: b58(take(32))); e["q"] = opt(u64); e["vq"] = opt(u64)
    return e
def trades(tx, m):
    out = []
    ks = tx["transaction"]["message"]["accountKeys"] + (tx["meta"].get("loadedAddresses") or {}).get("writable", []) + (tx["meta"].get("loadedAddresses") or {}).get("readonly", [])
    for g in tx["meta"].get("innerInstructions") or []:
        for ix in g["instructions"]:
            if ks[ix["programIdIndex"]] != C.PUMP: continue
            raw = C.b58d(ix.get("data", ""))
            if raw[:8] == E.EVENT_IX_TAG and raw[8:16] == E.DISC_TRADE:
                try: e = decode_trade(raw[16:])
                except Exception: continue
                if e["mint"] == m:
                    out.append(dict(slot=tx["slot"], t=tx["blockTime"], sig=tx["transaction"]["signatures"][0], user=e["user"], buy=e["buy"],
                                    q=e["q"] if e.get("q") else e["sol"], tok=e["tok"], vt=e["vt"], vq=e["vq"] if e.get("vq") else e["vsol"],
                                    bps=(e["fee_bps"] or 0) + (e["cfee_bps"] or 0), real=e["real"]))
    return out
def path(r):
    m = mints.get((r["slot"], r["mint8"]))
    if not m: return None
    t0 = r["t"]; anchor = next((s for bt, s in w4 if bt >= t0 + 1880), None)
    sigs, before = [], anchor
    while True:
        p = {"limit": 1000}
        if before: p["before"] = before
        page = call("getSignaturesForAddress", [m, p], key=f"sigs_{m[:12]}_{(before or 'now')[:12]}")
        if not page: break
        sigs += [x for x in page if x["err"] is None and x["slot"] >= r["slot"]]
        if page[-1]["slot"] < r["slot"] or len(page) < 1000: break
        before = page[-1]["signature"]
    with cf.ThreadPoolExecutor(12) as ex:
        txs = list(ex.map(lambda x: call("getTransaction", [x["signature"], TXO], key=f"tx_{x['signature'][:24]}"), sigs))
    tr = [e for tx in txs if tx for e in trades(tx, m)]
    order = {}
    for s in (r["slot"], r["slot"] + 1, r["slot"] + 2):
        b = call("getBlock", [s, {"encoding": "json", "transactionDetails": "signatures", "maxSupportedTransactionVersion": 1, "rewards": False}], key=f"blk_{s}")
        if b: order.update({sg: (s, i) for i, sg in enumerate(b["signatures"])})
    tr.sort(key=lambda e: order.get(e["sig"], (e["slot"], 10**6)))
    return m, tr
def model(r, m, tr, stake, n):
    k = next((i for i, e in enumerate(tr) if e["user"] == W4 and e["buy"] and e["slot"] == r["slot"]), None)
    if k is None: return dict(note="its buy not found")
    its = tr[k]; vta = its["vt"]; t0 = its["t"]
    rate = r["sol"] * 1e9 / (its["q"] * (1 + its["bps"] / 1e4))          # lamports per quote unit, at its buy
    if n == "slot+1":
        ahead = [e for e in tr[k + 1:] if e["slot"] <= its["slot"] + 1]; j = k + len(ahead)
    else:
        j = min(k + n, len(tr) - 1)
    ent = tr[j]; px_in = (vta / ent["vt"]) ** 2
    if px_in > 1.25: return dict(exit="refused", px_in=px_in, net=-0.0004)
    Q = stake * 1e9 * (1 - 0.003) / rate; net_in = Q * 1e4 / (1e4 + ent["bps"])
    tok = ent["vt"] - ent["vt"] * ent["vq"] / (ent["vq"] + net_in)
    ex, why, peak = None, "time", px_in
    for i in range(j + 1, len(tr)):
        e = tr[i]; px = (vta / e["vt"]) ** 2; peak = max(peak, px)
        if e.get("real") == 0: why, ex = "graduated", i; break
        if px >= 2.0: why, ex = "tp", min(i + 1, len(tr) - 1); break
        if px <= 0.8: why, ex = "stop", min(i + 1, len(tr) - 1); break
        if e["t"] - t0 >= 1790: why, ex = "time", i; break
    if ex is None: ex = len(tr) - 1; why = "time" if tr[-1]["t"] - t0 < 1790 else why
    x = tr[ex]; vq_r = x["vq"] + net_in; vt_r = x["vt"] * x["vq"] / vq_r
    out = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - x["bps"] / 1e4)
    sol = out * rate * (1 - 0.003) / 1e9
    return dict(exit=why, px_in=px_in, px_out=(vta / x["vt"]) ** 2, peak=peak, held=x["t"] - t0, net=sol - stake - 0.0026, trades_ahead=j - k)
if __name__ == "__main__":
    f = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d %H:%M")   # Beirut
    paths = {}
    with cf.ThreadPoolExecutor(4) as ex:
        for r, res in zip(rows, ex.map(path, rows)): paths[r["slot"], r["mint8"]] = res
    json.dump({f"{k[0]}_{k[1]}": v for k, v in paths.items() if v}, gzip.open(f"{SPD}/paths.json.gz", "wt"))
    print(f"{len(rows)} routable buys, {sum(1 for v in paths.values() if v)} paths; stake {STAKE}, landing {N}")
