# Step 1f: wallet 4's other-quote buys by route class of the curve's quote (routes.py), at launch (+0/+1) or later, by
# size, and against the class read from its own route (h9long routable.json, the 598 1.45+ SOL buys).
#   python3 -I s1f_picks_routes.py -> out/picks_cls.json {mint: cls}
import sys, os, collections, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib, routes
P = lib.jl(lib.OUT + "/picks.json")
routes.ensure([p.get("quote") for p in P.values()])
K = {m: routes.cls(p["quote"]) for m, p in P.items() if "quote" in p}
lib.jdump(K, lib.OUT + "/picks_cls.json")
R = lib.jl(lib.H9 + "/routable.json")
day = lambda p: time.strftime("%m-%d", time.gmtime(p["bbt"]))
launch = {m for m, p in P.items() if p.get("ds") is not None and p["ds"] <= 1}
print(f"{len(P)} other-quote buys; at launch (+0/+1) {len(launch)}")
c = collections.Counter((K[m], m in launch, P[m]["v"] >= 1.45) for m in K)
print("class  launch  1.45+  count  its net")
for k in sorted(c):
    net = sum(P[m]["net"] for m in K if (K[m], m in launch, P[m]["v"] >= 1.45) == k)
    print(f"  {k[0]}  {str(k[1]):5s}  {str(k[2]):5s}  {c[k]:5d}  {net:+8.2f}")
x = collections.Counter((R[m][0], K.get(m)) for m in R)
print("routable.json class (its own route) vs quote class:", sorted(x.items()))
ok = sum(n for (a, b), n in x.items() if (a in "ABCD") == (b in "ABC"))
print(f"routable or not agrees on {ok} of {sum(x.values())}")
rl = [m for m in K if K[m] in "ABC" and m in launch]
print("routable launch picks by day:", sorted(collections.Counter(day(P[m]) for m in rl).items()))
print("  of which 1.45+:", sorted(collections.Counter(day(P[m]) for m in rl if P[m]["v"] >= 1.45).items()))
print("quotes of routable launch picks:", collections.Counter((P[m]["quote"][:8], K[m]) for m in rl).most_common(20))
print("quote count among routable picks:", len({P[m]['quote'] for m in rl}))
print("buy size tiers (routable launch):", sorted(collections.Counter(round(P[m]["v"], 1) for m in rl).items()))
