# One exit for all, judged blind on each unit (Nov 27): for each unit, the exit picked on ALL THE OTHER units' copies (each
# unit weighted the same: its smoothed value without its best 2%, a copy), then scored once on this unit's own copies, by
# block, against its live exit. A unit's own data never takes part in its pick, so the score is blind. Rule (fixed before):
# the pooled exit replaces a unit's live exit only if it beats it on that unit in total, without its best 2% and in at least
# 3 of its 4 blocks. Last, the one pick on every unit's copies.
#   python3 -I x3_pooled.py SP UNIT ...
import sys, json, numpy as np
SP, LABS = sys.argv[1], sys.argv[2:]
sys.argv = [sys.argv[0], SP, LABS[0]]
src = open(__file__.replace("x3_pooled.py", "x2_analyze.py")).read().split('print(f"{LAB}: {N} copies')[0]
g = {}; exec(compile(src, "x2", "exec"), g)   # the helpers (wo2, smooth, name ...) and the axes, from the first unit's file
wo2, wo2v, smooth, name, SH = g["wo2"], g["wo2v"], g["smooth"], g["name"], g["SH"]
D = {}
for u in LABS:
    z = np.load(f"{SP}/exits_all/{u}.npz"); o = np.argsort(z["t"]); Gu = z["G"].astype(np.float64)[o]
    D[u] = dict(G=Gu, live=int(z["live"]), B=np.array_split(np.arange(len(Gu)), 4), v=smooth(wo2(Gu)) / len(Gu))
pct = lambda v: 100 * np.mean(v)
print(f"{'unit':5s} {'n':>4s}  the others' pick, scored on this unit (blocks)                     vs its live exit")
for u in LABS:
    d = D[u]; j = int(np.argmax(sum(D[o]["v"] for o in LABS if o != u))); G, L = d["G"], d["live"]
    per = [pct(G[b, j]) - pct(G[b, L]) for b in d["B"]]; tot = pct(G[:, j]) - pct(G[:, L]); w = 100 * (wo2v(G[:, j]) - wo2v(G[:, L])) / len(G)
    ok = tot > 0 and w > 0 and sum(p > 0 for p in per) >= 3
    print(f"{u:5s} {len(G):4d}  {name(j)}\n        {pct(G[:, j]):+6.1f}% against live {pct(G[:, L]):+6.1f}%: by block " + " ".join(f"{p:+5.1f}" for p in per)
          + f", w/o 2% {w:+5.1f} points" + ("  <- REPLACES" if ok else ""))
j = int(np.argmax(sum(D[o]["v"] for o in LABS)))
print(f"\nthe one pick on every unit: {name(j)}")
for u in LABS:
    G, L = D[u]["G"], D[u]["live"]; print(f"  {u}: {pct(G[:, j]):+6.1f}% (live {pct(G[:, L]):+6.1f}%)")
