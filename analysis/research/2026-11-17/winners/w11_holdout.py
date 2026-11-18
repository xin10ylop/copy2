# The frozen rule of PREREG_6ua7w2Gv.md, scored once on the holdout (and, for reference, on the exploration set).
#   python3 -I w11_holdout.py SP WALLET8 SUFFIX
import sys, json, numpy as np
SP, W8, SUF = sys.argv[1], sys.argv[2], sys.argv[3]
R = sorted((r for r in json.load(open(f"{SP}/winners/study_{W8}{SUF}.json")) if not r["refused"]), key=lambda r: r["t"])
C = json.load(open(f"{SP}/winners/ctx_{W8}{SUF}.json"))
dev = lambda r: ((C.get(f"{r['m']}:{r['t']}") or {}).get("create") or {}).get("dev_buy")
def S(v):
    s = sorted(v); return f"{len(v):3d} {sum(v):+6.2f} ({100 * np.mean(v) / 0.5 if v else 0:+6.1f}%) w/o5 {sum(s[:-5]) if len(s) > 5 else 0:+6.2f}"
K = [r for r in R if dev(r) is not None and 0 < dev(r) <= 2]; h = len(K) // 2
print(f"{W8}{SUF}: {len(R)} copies, {sum(1 for r in R if dev(r) is not None)} with the create read, {len(K)} kept by the rule")
for cost in (0.0345, 0.01):
    v = [r["ex"]["sp5/60s"] - (cost - 0.0026) for r in K]; w = [r["ex"]["sp5/60s"] - (cost - 0.0026) for r in R]
    print(f"   cost {cost}: the rule {S(v)} | its halves {S(v[:h])} / {S(v[h:])} | every copy, same exit {S(w)}")
v = [r["ex"]["sp5/60s"] - 0.0319 for r in K]; s = sorted(v)
# the fairer measures (the owner, Nov 18: a fixed best 5 is a different share for each wallet): the best 2% out, a bootstrap
def fair(v, name):
    v = np.array(v); n = len(v)
    if n == 0: return print(f"   {name}: no copies")
    k = max(1, int(round(0.02 * n))); s = np.sort(v); bs = np.random.default_rng(7).choice(v, size=(10000, n)).mean(axis=1)
    print(f"   {name}: {n} copies, without the best 2% ({k}) {s[:-k].sum():+.2f} SOL; P(mean > 0) {np.mean(bs > 0):.1%}; 5th pct {100 * np.percentile(bs, 5) / 0.5:+.1f}% a copy")
print(f"   PASS: {len(K) >= 40 and sum(v) > 0 and sum(s[:-5]) > 0}  (40+ kept, positive at 0.0345, positive without the best 5)")

fair([r["ex"]["sp5/60s"] - 0.0319 for r in K], "FAIRER MEASURES, the rule's copies at 0.0345")
