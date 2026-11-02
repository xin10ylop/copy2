# Small counts quoted in the README: routable creates by class over Oct 19-26, wallet 4's share of launch buys in the
# create slot, rule W's pass share, F0 - F1 on W.   python3 -I s1g_counts.py -> out/s1g.out
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
T = lib.jl(lib.OUT + "/table.json"); TF = lib.jl(lib.OUT + "/table_fresh.json")
print("routable creates Oct 19-26 by class:", dict(collections.Counter(t["cls"] for t in T)))
P = lib.jl(lib.OUT + "/picks.json")
z = sum(1 for p in P.values() if p.get("ds") == 0); o = sum(1 for p in P.values() if p.get("ds") == 1)
print(f"its other-quote launch buys in the create slot: {z} of {z + o} ({z / (z + o):.1%})")
for name, tab in (("W", T), ("WF", TF)):
    ms = set(lib.jl(lib.OUT + f"/rule_{name}.json"))
    for per in sorted({t["per"] for t in tab}):
        S = [t for t in tab if t["per"] == per]
        print(f"rule {name} {per}: passes {sum(1 for t in S if t['mint'] in ms)} of {len(S)} ({sum(1 for t in S if t['mint'] in ms) / len(S):.1%})")
for sim, rule, tab in (("sim_W", "W", T), ("sim_fresh", "WF", TF)):
    S = lib.jl(lib.OUT + f"/{sim}.json"); per = {t["mint"]: t["per"] for t in tab}
    ms = [m for m in lib.jl(lib.OUT + f"/rule_{rule}.json") if m in S and "err" not in S[m] and m in per]
    for p in sorted({per[m] for m in ms}):
        f0 = sum(S[m]["ours|1.0|F0"]["pnl"] for m in ms if per[m] == p and "ours|1.0|F0" in S[m])
        f1 = sum(S[m]["ours|1.0|F1"]["pnl"] for m in ms if per[m] == p and "ours|1.0|F1" in S[m])
        print(f"W {p} ours 1 SOL: F0 {f0:+.2f}, F1 {f1:+.2f}, F0 - F1 {f0 - f1:+.2f}")
errs = set()
for f in ("sim_picks", "sim_W", "sim_base", "sim_fresh"):
    errs |= {m for m, r in lib.jl(lib.OUT + f"/{f}.json").items() if "err" in r}
print("coins whose simulation failed:", len(errs), sorted(errs))
