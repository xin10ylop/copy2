# Step 2a: the feature table of every routable create (class A/B/C) of the quote-control universe, Oct 19 00:00 -
# Oct 27 00:00 UTC, labelled with wallet 4's launch buys (+0/+1, out/picks.json): pick (any size), big (1.45+ SOL).
#   python3 -I s6_table.py -> out/table.json [row]
import sys, os, glob, collections, calendar
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib, feat
fn = lib.OUT + f"/qc_creates_{calendar.timegm((2026, 10, 19, 0, 0, 0))}_{calendar.timegm((2026, 10, 27, 0, 0, 0))}.json"
rows = feat.load_universe(fn)
H = feat.creator_hist(rows)                               # creator history over every quote-control create (all quotes)
P = lib.jl(lib.OUT + "/picks.json")
pk = {p["csig"]: p for p in P.values() if p.get("csig") and p.get("ds") is not None and p["ds"] <= 1}
# the creator's earlier routable coins that wallet 4 bought (a diagnostic, not a feature a rule may use)
by = collections.defaultdict(list)
for r in sorted(rows, key=lambda r: r["cslot"]): by[r["user"]].append(r)
T = []
for r in rows:
    if r["cls"] not in "ABC": continue
    f = feat.base(r); f.update(H[r["csig"]])
    prev = [p for p in by[r["user"]] if p["cslot"] < r["cslot"]]
    f["w4_prior"] = sum(1 for p in prev if p["csig"] in pk)
    p = pk.get(r["csig"])
    f.update(mint=r["mint"], csig=r["csig"], cslot=r["cslot"], cbt=r["cbt"], user=r["user"], vquote=r["vquote"], per=feat.per(r["cbt"]),
             pick=int(p is not None), big=int(p is not None and p["v"] >= 1.45), w4v=p["v"] if p else 0, w4net=p["net"] if p else 0,
             w4ds=p["ds"] if p else None, name=r["name"], sym=r["sym"], uri=r["uri"])
    T.append(f)
lib.jdump(T, lib.OUT + "/table.json")
c = collections.Counter((t["per"], t["cls"]) for t in T)
print(f"{len(rows)} quote-control creates read, {len(T)} routable")
for per in ("P1", "P2"):
    S = [t for t in T if t["per"] == per]
    print(f"  {per}: routable {len(S)} (A {c[(per,'A')]}, B {c[(per,'B')]}, C {c[(per,'C')]}); wallet 4 launch picks {sum(t['pick'] for t in S)}"
          f" ({sum(t['pick'] for t in S)/len(S):.1%}), of which 1.45+ {sum(t['big'] for t in S)} ({sum(t['big'] for t in S)/len(S):.1%}); its net on them {sum(t['w4net'] for t in S):+.2f} ({sum(t['w4net'] for t in S if t['big']):+.2f} on 1.45+)")
d = collections.Counter(lib.crc.json.dumps(0) and __import__('time').strftime("%m-%d", __import__('time').gmtime(t["cbt"])) for t in T)
dp = collections.Counter(__import__('time').strftime("%m-%d", __import__('time').gmtime(t["cbt"])) for t in T if t["pick"])
db = collections.Counter(__import__('time').strftime("%m-%d", __import__('time').gmtime(t["cbt"])) for t in T if t["big"])
print("by day (UTC): routable creates / its launch picks / 1.45+")
for k in sorted(d): print(f"  {k}  {d[k]:5d}  {dp[k]:4d} ({dp[k]/d[k]:5.1%})  {db[k]:4d} ({db[k]/d[k]:5.1%})")
pm = {t["csig"] for t in T}
miss = [p for p in pk.values() if p["csig"] not in pm and lib.jl and p.get("quote")]
import routes
print("its routable launch picks not in the universe:", sum(1 for p in miss if routes.cls(p["quote"]) in "ABC"))
