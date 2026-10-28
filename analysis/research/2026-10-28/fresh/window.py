# Fresh study: wallet 4's curve buys of coins priced in another token between two times (UTC), at least MIN SOL (SOL value,
# ledger.py), with the route class (route_cls.py: A wSOL multihop, B WBTC multihop, C curve quoted in WBTC, E not routable)
# and the token it paid in. Did the paper bot miss a qualifying buy?   python3 -I window.py FROM TO [MIN]
import sys, os, json, datetime, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from route_cls import cls, by, WSOL
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/fresh3"
W = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
F, U = (int(datetime.datetime.strptime(a, "%Y-%m-%d %H:%M").replace(tzinfo=datetime.timezone.utc).timestamp()) for a in sys.argv[1:3])
MIN = float(sys.argv[3]) if len(sys.argv) > 3 else 1.45
T = {x["m"]: x for x in json.load(open(f"{SP}/h9long/{W[:8]}_trips.json"))}
Q = json.load(open(f"{SP}/h9long/{W[:8]}_quote.json"))
n = collections.Counter(); out = []
for m, x in T.items():
    for k, t in enumerate(x["tr"]):
        if not t["buy"] or not F <= t["bt"] < U: continue
        n[x["kind"]] += 1
        if x["kind"] != "pump, other quote" or (t["v"] or 0) < MIN: continue
        r = by.get((m, t["s"], 1)); paid = [kk[:8] for kk in (r["tok"] if r else {}) if kk not in (m, WSOL)]
        c = cls(dict(m=m, tr=[t])) if k == 0 else "later buy"
        out.append((t["bt"], m, t["v"], c, Q.get(m, "via SOL only"), ",".join(paid) or "SOL", len(x["tr"])))
print(f"its curve buys {sys.argv[1]} to {sys.argv[2]} UTC: " + "  ".join(f"{k} {v}" for k, v in n.items()))
print(f"of coins priced in another token, {MIN}+ SOL: {len(out)}")
for bt, m, v, c, qt, paid, nt in sorted(out):
    print(f"   {datetime.datetime.fromtimestamp(bt, datetime.timezone.utc):%m-%d %H:%M:%S} UTC  {m}  its {v:.3f} SOL  route {c}  quote {qt}  paid with {paid}  ({nt} curve trades)")
