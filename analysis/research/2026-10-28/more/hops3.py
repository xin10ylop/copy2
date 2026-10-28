# Its big buys whose own route has 3 hops (routes.json): the bot skips them ("route of 3 hops", route.rs MAX_OUR_HOPS = 2)
# but grid.py's routable set (route_cls.py classes A / B: multihop from wSOL or WBTC, any length) has them. Their copy
# as grid.py prices it, and part A without them (what the bot as built can take), at most 4 open.   python3 -I hops3.py
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim
SPX = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/more"
QS = {q["m"]: q for q in json.load(open(f"{SPX}/quotes.json"))}; RT = json.load(open(f"{SPX}/routes.json"))
def hops(m):
    q = QS.get(m); r = RT.get(q["sig"]) if q else None
    return len(r["hops"]) if r and r.get("hops") else (1 if q and not q["mh"] else 0)
c = collections.Counter((QS[m]["per"], hops(m), QS[m]["cls"]) for m in QS)
print("its single-trip 1.45+ SOL buys of other-quote coins by period, hops of its route (0 = direct curve buy), route class:")
for k in sorted(c): print(f"   {k}: {c[k]}")
A = sim.trips()
three = {m for m, x, p in A if hops(m) >= 3}
print(f"in grid.py's routable 1.5+ set: {len(A)}, of which 3-hop: {len(three)} ({', '.join(m[:8] for m in sorted(three))})")
for cap in (4, 99):
    sc, got = sim.score(A, cap=cap)
    sim.show(f"part A as in grid.py (3-hop in), at most {cap} open", sc)
    sim.show(f"part A as the bot routes it (3-hop out), {cap} open", sim.score([t for t in A if t[0] not in three], cap=cap)[0])
    for p in ("P1", "P2"):
        print(f"      {p} the 3-hop copies: " + ", ".join(f"{m[:8]} {r:+.2f} ({sim.KIND.get(m, '')})" for r, m in got[p] if m in three))
