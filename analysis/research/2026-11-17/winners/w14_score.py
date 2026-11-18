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
print(f"PASS: {len(X) >= 40 and sum(v) > 0 and sum(v[:-5]) > 0}")
