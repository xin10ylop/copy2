# Step 2e: the creator's EARLIER routable coins and how they did in their first 60 s (out/act60.json), added to the
# table: pa_n (earlier routable coins of the signer), pa_med / pa_max (their median / max landed transactions in 60 s),
# pa_hot (how many had 20+). Only coins created before this one count.   python3 -I s6c_prior_act.py -> out/table.json
import sys, os, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
T = lib.jl(lib.OUT + "/table.json"); A = lib.jl(lib.OUT + "/act60.json")
by = collections.defaultdict(list)
for t in sorted(T, key=lambda t: t["cslot"]): by[t["user"]].append(t)
for u, L in by.items():
    for i, t in enumerate(L):
        prev = [A.get(p["mint"]) for p in L[:i] if A.get(p["mint"]) is not None]
        t["pa_n"] = i; t["pa_med"] = statistics.median(prev) if prev else -1; t["pa_max"] = max(prev) if prev else -1
        t["pa_hot"] = sum(1 for v in prev if v >= 20)
lib.jdump(T, lib.OUT + "/table.json")
print(f"{len(T)} rows; act60 known for {sum(1 for t in T if A.get(t['mint']) is not None)}")
for per in ("P1", "P2"):
    S = [t for t in T if t["per"] == per]
    for lab, f in (("no earlier coin", lambda t: t["pa_n"] == 0), ("earlier coins, none hot", lambda t: t["pa_n"] > 0 and t["pa_hot"] == 0),
                   ("an earlier coin had 20+ in 60 s", lambda t: t["pa_hot"] > 0)):
        k = [t for t in S if f(t)]
        print(f"  {per} {lab:32s} {len(k):5d} coins, picks {sum(t['pick'] for t in k):4d} ({sum(t['pick'] for t in k)/max(1,len(k)):.1%}), 1.45+ {sum(t['big'] for t in k)}")
