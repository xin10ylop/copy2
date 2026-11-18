# The report of a9_w4_filter.py: wallet 4's modelled copies by the create's signals, fixed groups; halves by time (pick on
# the first, score on the second); at 0.0345 SOL a round trip (the rows carry 0.0026: 0.0319 more is charged a copy).
#   python3 -I a9b_w4_filter_report.py SP > out/a9_w4_filter.txt
import sys, json, gzip, numpy as np
SP = sys.argv[1]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
R = sorted(json.load(gzip.open(f"{SP}/hunt_screen.json.gz"))[W4], key=lambda r: r["t"]); F = json.load(open(f"{SP}/attn/w4_create.json"))
for r in R: r["n"] = r["net"] - 0.0319; r["f"] = F.get(r["m"])
half = R[len(R) // 2]["t"]
def S(v):
    if not v: return "   0" + " " * 31
    s = sorted(v); return f"{len(v):4d} {sum(v):+7.2f} ({100 * np.mean(v) / 0.5:+6.1f}%) w/o5 {sum(s[:-5]) if len(s) > 5 else 0:+7.2f}"
print(f"wallet 4: {len(R)} modelled copies at 0.0345 SOL a round trip; create read for {sum(1 for r in R if r['f'])}")
print(f"all: {S([r['n'] for r in R])} | 1st half {S([r['n'] for r in R if r['t'] < half])} | 2nd half {S([r['n'] for r in R if r['t'] >= half])}")
cut = lambda x, cs: "unknown" if x is None else next((f"<= {c:g}" for c in cs if x <= c), f"> {cs[-1]:g}")
def show(name, key):
    G = {}
    for r in R: G.setdefault(key(r), []).append(r)
    print(f"\n{name}:  group | 1st half | 2nd half")
    for k in sorted(G, key=str):
        X = G[k]; print(f"   {str(k):18s} {S([r['n'] for r in X if r['t'] < half])} | {S([r['n'] for r in X if r['t'] >= half])}")
f = lambda r, k: (r["f"] or {}).get(k)
show("dev buy in the create (SOL)", lambda r: cut(f(r, "dev_buy"), [0, 0.5, 2, 5]))
show("tips in the create (SOL)", lambda r: cut(f(r, "tips"), [0, 0.001, 0.01]))
show("mayhem", lambda r: f(r, "mayhem") if r["f"] else "unknown")
show("creator fee bps", lambda r: f(r, "cfee") if r["f"] else "unknown")
show("payer is the creator", lambda r: f(r, "payer_is_creator") if r["f"] else "unknown")
show("payer's SOL before", lambda r: cut(f(r, "payer_sol"), [0.5, 3, 10, 100]))
show("its buy after the create (s)", lambda r: cut(r["t"] - f(r, "t") if r["f"] else None, [0, 2, 10]))
