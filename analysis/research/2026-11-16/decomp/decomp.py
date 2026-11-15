# Where wallet 4 makes its money now (the owner, Nov 16: "other than the floats we don't hold, see what makes him
# good money and we can engineer to copy"). The decomposition of 02-decomposition/ redone on Oct 29 12:02 UTC - Nov 15
# from its landed transactions: every coin it traded, its own result on it (SOL and every token in and out, tokens at
# prices_full2.json), the coin's class from its first buy (pump's trade event: the quote, the size):
#   A  priced in another token, 1.45+ SOL, paid with a token the bot holds now (SOL, WBTC, PUMP, SPCX, TTWO, DJT)
#   B  priced in another token, 1.45+ SOL, paid with another token
#   C  priced in another token, under 1.45 SOL (bands)
#   D  priced in SOL (bands; at the coin's creation slot or later)
#   E  no curve trade of its own (PumpSwap and other venues)
# Coins still held, or traded together with another coin, are counted apart. Halves split at Nov 6 12:00 UTC.
#   python3 -I decomp.py SPD
import sys, os, json, struct, collections, datetime
SPD = sys.argv[1]
SPX = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
sys.path.insert(0, SPX + "/rivalpnl"); sys.path.insert(0, "/home/user/rugsnipe/analysis")
import common as C
from rugsnipe_analysis import events as E
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; WSOL = "So11111111111111111111111111111111111111112"
T0 = 1793274720 + 600; TH = datetime.datetime(2026, 11, 6, 12, 0, tzinfo=datetime.timezone.utc).timestamp()
HOLD = {"So111111", "3NZ9JMVB", "pumpCmXq", "SPCXxcqX", "TTWofwAg", "DJTu7vi8"}
px = json.load(open(f"{SPD}/prices_full2.json")); px[WSOL] = 1.0
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def b58(b):
    n = int.from_bytes(b, "big"); out = ""
    while n: n, r = divmod(n, 58); out = B58[r] + out
    return "1" * (len(b) - len(b.lstrip(b"\0"))) + out
def ev(d):
    o = [0]
    def take(n):
        if o[0] + n > len(d): raise IndexError
        v = d[o[0]:o[0] + n]; o[0] += n; return v
    left = lambda: len(d) - o[0]; u64 = lambda: struct.unpack("<Q", take(8))[0]; opt = lambda f: f() if left() else None
    e = dict(mint=b58(take(32)), sol=u64(), tok=u64(), buy=take(1)[0] == 1, user=b58(take(32))); take(8); u64(); u64()
    for _ in range(2): opt(u64)
    opt(lambda: take(32)); opt(u64); opt(u64); opt(lambda: take(32)); opt(u64); opt(u64); opt(lambda: take(1)); [opt(u64) for _ in range(4)]
    if left(): n = struct.unpack("<I", take(4))[0]; take(n)
    opt(lambda: take(1)); [opt(u64) for _ in range(4)]
    if left(): n = struct.unpack("<I", take(4))[0]; take(34 * n)
    e["quote"] = opt(lambda: b58(take(32))) or WSOL; return e
trips = collections.defaultdict(lambda: dict(spent=0.0, back=0.0, held=0, first=None, cls=None, size=None, pay=None, mixed=False, buys=0))
lastt = 0
for fn in os.listdir(f"{SPD}/w4tx"):
    t = json.load(open(f"{SPD}/w4tx/{fn}")); m = t["meta"]
    if m.get("err") or t["blockTime"] < T0 - 7200: continue
    lastt = max(lastt, t["blockTime"])
    ks = t["transaction"]["message"]["accountKeys"] + sum(((m.get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
    if W4 not in ks: continue
    i = ks.index(W4); d = collections.defaultdict(int)
    for k, s in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in m.get(k) or []:
            if b.get("owner") == W4: d[b["mint"]] += s * int(b["uiTokenAmount"]["amount"])
    d = {k: v for k, v in d.items() if v}; sol = m["postBalances"][i] - m["preBalances"][i] + d.pop(WSOL, 0)
    coins = [k for k in d if k not in px]
    if not coins: continue
    evs = []
    for g in m.get("innerInstructions") or []:
        for ix in g["instructions"]:
            if ks[ix["programIdIndex"]] != C.PUMP: continue
            raw = C.b58d(ix.get("data", ""))
            if raw[:8] == E.EVENT_IX_TAG and raw[8:16] == E.DISC_TRADE:
                try: e = ev(raw[16:])
                except Exception: continue
                if e["user"] == W4: evs.append(e)
    v = (sol + sum(a * px[k] for k, a in d.items() if k in px)) / 1e9
    if len(coins) > 1:
        for c in coins: trips[c]["mixed"] = True
        continue
    c = coins[0]; tr = trips[c]; tr["held"] += d[c]
    if d[c] > 0:
        tr["spent"] += -v; tr["buys"] += 1
        if tr["first"] is None:
            tr["first"] = t["blockTime"]; tr["size"] = -v
            pays = [k for k, a in d.items() if a < 0 and k != c]; tr["pay"] = (pays[0] if pays else WSOL)[:8]
            e = next((e for e in evs if e["mint"] == c), None)
            tr["cls"] = "E" if e is None else ("D" if e["quote"] == WSOL else "OT")
    else:
        tr["back"] += v
def cls(tr):
    if tr["cls"] in ("E", None): return "E"
    if tr["cls"] == "D":
        s = tr["size"]; return "D <0.5" if s < 0.5 else "D 0.5-1.45" if s < 1.45 else "D 1.45+"
    s = tr["size"]
    if s >= 1.45: return "A" if tr["pay"] in HOLD else "B"
    return "C <0.5" if s < 0.5 else "C 0.5-1.0" if s < 1.0 else "C 1.0-1.45"
days = (lastt - T0) / 86400
G = collections.defaultdict(list); open_ = collections.Counter(); mixed = 0
for c, tr in trips.items():
    if tr["first"] is None or tr["first"] < T0: continue
    if tr["mixed"]: mixed += 1; continue
    if tr["held"] > 0: open_[cls(tr)] += 1; continue
    if tr["spent"] <= 0: continue
    G[cls(tr)].append(tr)
print(f"Oct 29 12:02 UTC to {datetime.datetime.fromtimestamp(lastt, datetime.timezone.utc):%b %d %H:%M} UTC ({days:.1f} days); coins it bought and sold out of; still held: {dict(open_)}; traded with another coin in one transaction: {mixed}")
print(f"   {'class':12s} {'coins':>5s} {'a day':>5s} | {'spent':>7s} {'its net':>8s} {'a coin':>7s} {'won':>4s} | {'w/o best 2':>10s} {'w/o best 5':>10s} | {'1st half':>8s} {'2nd half':>8s} | biggest win")
tot = 0
for k in ("A", "B", "C 1.0-1.45", "C 0.5-1.0", "C <0.5", "D 1.45+", "D 0.5-1.45", "D <0.5", "E"):
    r = G.get(k, [])
    if not r: continue
    nets = sorted((x["back"] - x["spent"] for x in r), reverse=True); sp = sum(x["spent"] for x in r); tot += sum(nets)
    h = [sum(x["back"] - x["spent"] for x in r if (x["first"] < TH) == (j == 0)) for j in (0, 1)]
    print(f"   {k:12s} {len(r):5d} {len(r) / days:5.1f} | {sp:7.1f} {sum(nets):+8.2f} {100 * sum(nets) / sp:+6.1f}% {sum(1 for x in nets if x > 0):4d} | {sum(nets[2:]):+10.2f} {sum(nets[5:]):+10.2f} | {h[0]:+8.2f} {h[1]:+8.2f} | {nets[0]:+.2f}")
print(f"   all closed coins: {tot:+.2f} SOL")
b = collections.defaultdict(list)
for x in G.get("B", []): b[x["pay"]].append(x["back"] - x["spent"])
print("   B by the token it paid with: " + ", ".join(f"{k} {len(v)} {sum(v):+.2f}" for k, v in sorted(b.items(), key=lambda kv: -sum(kv[1]))[:10]))
