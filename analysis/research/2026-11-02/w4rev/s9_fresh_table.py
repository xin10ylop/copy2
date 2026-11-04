# Step 4a: the fresh period's feature table: routable quote-control creates of Oct 28 00:00 - Nov 1 21:30 UTC (out of
# out/qc_creates_1793059200_1793574000.json, Oct 27 00:00 - Nov 1 23:00, Oct 27 kept for the creators' 24 h history),
# the same features as s6_table.py, labelled with wallet 4's launch buys of the period when out/w4_fresh.json exists
# (s9b_w4_fresh.py).   python3 -I s9_fresh_table.py -> out/table_fresh.json
import sys, os, collections, calendar, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib, feat
LO, HI = calendar.timegm((2026, 10, 28, 0, 0, 0)), calendar.timegm((2026, 11, 1, 21, 30, 0))
rows = feat.load_universe(lib.OUT + "/qc_creates_1793059200_1793574000.json")
H = feat.creator_hist(rows)
W = lib.jl(lib.OUT + "/w4_fresh.json") if os.path.exists(lib.OUT + "/w4_fresh.json") else None
T = []
for r in rows:
    if r["cls"] not in "ABC" or not (LO <= r["cbt"] < HI): continue
    f = feat.base(r); f.update(H[r["csig"]])
    p = (W or {}).get(r["mint"])
    f.update(mint=r["mint"], csig=r["csig"], cslot=r["cslot"], cbt=r["cbt"], user=r["user"], vquote=r["vquote"], per="P3",
             pick=int(bool(p) and p["ds"] <= 1), big=int(bool(p) and p["ds"] <= 1 and p["v"] >= 1.45), w4v=(p or {}).get("v", 0),
             name=r["name"], sym=r["sym"], uri=r["uri"])
    T.append(f)
lib.jdump(T, lib.OUT + "/table_fresh.json")
print(f"{len(rows)} quote-control creates read (Oct 27 - Nov 1), {len(T)} routable in Oct 28 00:00 - Nov 1 21:30 UTC"
      f" (A {sum(1 for t in T if t['cls']=='A')}, B {sum(1 for t in T if t['cls']=='B')}, C {sum(1 for t in T if t['cls']=='C')})")
d = collections.Counter(time.strftime("%m-%d", time.gmtime(t["cbt"])) for t in T)
print("routable creates by day:", sorted(d.items()))
if W is not None:
    print(f"wallet 4 launch picks {sum(t['pick'] for t in T)} ({sum(t['pick'] for t in T)/len(T):.1%} of the routable creates), of which 1.45+ {sum(t['big'] for t in T)} ({sum(t['big'] for t in T)/len(T):.1%})")
    dp = collections.Counter(time.strftime("%m-%d", time.gmtime(t["cbt"])) for t in T if t["pick"])
    db = collections.Counter(time.strftime("%m-%d", time.gmtime(t["cbt"])) for t in T if t["big"])
    print("by day: routable creates / its launch picks / 1.45+:", [(k, d[k], dp[k], db[k]) for k in sorted(d)])
