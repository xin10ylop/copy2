# Step 2g: wallet 4's launch pick rate by single create-time feature, P1 and P2 side by side (out/table.json).
#   python3 -I s7a_univar.py -> the most common values of each feature
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
T = lib.jl(lib.OUT + "/table.json")
bk = lambda x, e: next((f"<{v}" for v in e if x < v), f">={e[-1]}")
FE = [("route class", lambda t: t["cls"]), ("quote mint", lambda t: t["quote"][:8]), ("metadata host", lambda t: t["host"]),
      ("creator fee bps", lambda t: t["cfee"]), ("top-level programs", lambda t: t["progs"][:40]),
      ("dev buy, SOL-equivalent", lambda t: bk(t["dev_sol"], [0.001, 0.1, 0.5, 1, 2, 5])),
      ("signer's creates in the 24 h before", lambda t: min(t["prior24"], 5)), ("hour UTC (4 h blocks)", lambda t: t["hour"] // 4 * 4),
      ("symbol length", lambda t: min(t["slen"], 8)), ("creator = signer", lambda t: t["cre_is_user"])]
tot = {p: (sum(1 for t in T if t["per"] == p), sum(t["pick"] for t in T if t["per"] == p)) for p in ("P1", "P2")}
print("all routable creates: " + "  ".join(f"{p}: {n} coins, picks {k} ({k/n:.1%})" for p, (n, k) in tot.items()))
print(f"together: {sum(n for n, k in tot.values())} coins, picks {sum(k for n, k in tot.values())} ({sum(k for n, k in tot.values())/sum(n for n, k in tot.values()):.1%}),"
      f" 1.45+ {sum(t['big'] for t in T)} ({sum(t['big'] for t in T)/len(T):.1%})")
for name, f in FE:
    c = collections.Counter((t["per"], f(t)) for t in T); k = collections.Counter((t["per"], f(t)) for t in T if t["pick"])
    vals = [v for v, _ in collections.Counter(f(t) for t in T if t["per"] == "P1").most_common(8)]
    print(f"== {name}")
    for v in vals:
        print(f"   {str(v)[:42]:42s} " + "  ".join(f"{p}: {c[(p, v)]:5d} coins, {k[(p, v)]:4d} picks ({k[(p, v)]/max(1, c[(p, v)]):5.1%})" for p in ("P1", "P2")))
