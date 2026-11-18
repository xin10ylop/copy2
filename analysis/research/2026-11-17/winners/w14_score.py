# The frozen rule of PREREG_4sgdNABj.md on the copies the rule was not found on (the full study, PMAX=2, minus the interim's).
#   python3 -I w14_score.py SP WALLET8 FULL_SUFFIX INTERIM_SUFFIX
import sys, json, numpy as np
SP, W8, FS, IS = sys.argv[1:5]
F = sorted((r for r in json.load(open(f"{SP}/winners/study_{W8}{FS}.json")) if not r["refused"]), key=lambda r: r["t"])
seen = {(r["m"], r["t"]) for r in json.load(open(f"{SP}/winners/study_{W8}{IS}.json"))}
X = [r for r in F if (r["m"], r["t"]) not in seen]
def S(v):
    s = sorted(v); return f"{len(v):3d} {sum(v):+6.2f} ({100 * np.mean(v) / 0.5 if v else 0:+6.1f}%) w/o5 {sum(s[:-5]) if len(s) > 5 else 0:+6.2f}"
for cost in (0.0345, 0.01):
    v = [r["ex"]["sp5/60s"] - (cost - 0.0026) for r in X]; h = len(v) // 2
    print(f"{W8}: {len(F)} copies, {len(X)} not seen by the rule; cost {cost}: {S(v)} | halves {S(v[:h])} / {S(v[h:])}")
v = sorted(r["ex"]["sp5/60s"] - 0.0319 for r in X)
print(f"   (all unseen copies, in-sample to the screen for those of Nov 15-17: 40+, positive, positive without the best 5: {len(X) >= 40 and sum(v) > 0 and sum(v[:-5]) > 0})")
A = [r for r in X if r["t"] >= 1794877620]   # after the screen (Nov 17 01:07 UTC): the clean test (the amendment)
for cost in (0.0345, 0.01):
    print(f"   AFTER THE SCREEN only, cost {cost}: {S([r['ex']['sp5/60s'] - (cost - 0.0026) for r in A])}")
a = sorted(r["ex"]["sp5/60s"] - 0.0319 for r in A)
# the fairer measures (the owner, Nov 18: a fixed best 5 is a different share for each wallet): the best 2% out, a bootstrap
def fair(v, name):
    v = np.array(v); n = len(v)
    if n == 0: return print(f"   {name}: no copies")
    k = max(1, int(round(0.02 * n))); s = np.sort(v); bs = np.random.default_rng(7).choice(v, size=(10000, n)).mean(axis=1)
    print(f"   {name}: {n} copies, without the best 2% ({k}) {s[:-k].sum():+.2f} SOL; P(mean > 0) {np.mean(bs > 0):.1%}; 5th pct {100 * np.percentile(bs, 5) / 0.5:+.1f}% a copy")
print(f"PASS (the amendment: after-screen buys, 20+, positive at 0.0345, positive without the best 5): {len(A) >= 20 and sum(a) > 0 and sum(a[:-5]) > 0}")

fair([r["ex"]["sp5/60s"] - 0.0319 for r in A], "FAIRER MEASURES, after-screen copies at 0.0345")
