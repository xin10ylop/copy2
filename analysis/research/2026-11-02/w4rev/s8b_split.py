# Step 3e: a rule's launch buys by day and by part (s5_sim.py results; each coin's own half-and-half fill), config CFG.
#   python3 -I s8b_split.py SIM_JSON RULE [CFG=ours|1.0]
import sys, os, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
sim = lib.jl(sys.argv[1]); rule = sys.argv[2]; cfg = sys.argv[3] if len(sys.argv) > 3 else "ours|1.0"
T = {t["mint"]: t for t in lib.jl(lib.OUT + "/table.json")}
if os.path.exists(lib.OUT + "/table_fresh.json"): T.update({t["mint"]: t for t in lib.jl(lib.OUT + "/table_fresh.json")})
ms = [m for m in lib.jl(lib.OUT + f"/rule_{rule}.json") if m in sim and "err" not in sim[m] and m in T]
def val(m):
    r = sim[m]; x = r.get(f"{cfg}|F{r['_F']}"); return x["pnl"] if x else None
parts = {"notrandom.fun host": lambda t: t["host"] == "meta.notrandom.fun", "first create in 24 h, fee > 0": lambda t: t["host"] != "meta.notrandom.fun"}
print(f"== {rule}, {cfg}, own fill draw: by day (UTC) -- all / wallet 4 picked / wallet 4 skipped")
g = collections.defaultdict(list)
for m in ms:
    v = val(m)
    if v is not None: g[time.strftime("%m-%d", time.gmtime(T[m]["cbt"]))].append((v, T[m]["pick"]))
for d in sorted(g):
    L = g[d]; a = [v for v, p in L]; b = [v for v, p in L if p]; c = [v for v, p in L if not p]
    print(f"  {d}  {len(a):4d} {sum(a):+7.2f}  |  {len(b):4d} {sum(b):+7.2f}  |  {len(c):4d} {sum(c):+7.2f}")
print("by part and period: n, total, picks among them")
for name, f in parts.items():
    for per in ("P1", "P2", "P3"):
        L = [val(m) for m in ms if T[m]["per"] == per and f(T[m]) and val(m) is not None]
        if L: print(f"  {name:32s} {per}  {len(L):4d} {sum(L):+7.2f}  picks {sum(1 for m in ms if T[m]['per'] == per and f(T[m]) and T[m]['pick'])}")
by = collections.defaultdict(list)
for m in ms:
    v = val(m)
    if v is not None: by[(T[m]["per"], T[m]["cls"])].append(v)
print("by route class:", {f"{k[0]} {k[1]}": f"{len(v)} {sum(v):+.2f}" for k, v in sorted(by.items())})
