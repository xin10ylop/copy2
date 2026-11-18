# The bundle wait's money (PREREG_bundle_wait.md): b0's coin table, the grid picked before Nov 17 13:49 UTC, scored after.
#   python3 -I b1_money.py SP > out/b1_money.txt
import sys, json, gzip, numpy as np
SP = sys.argv[1]; S0 = 1794923340; coins = json.load(gzip.open(f"{SP}/bundle_coins.json.gz"))
def trade(c, X, tp, cap):
    if any(s <= X for s in c["sells"]): return None
    tr, t0, W = c["tr"], c["t0"], set(c["bundle"])
    i = next((j for j, e in enumerate(tr) if e["t"] - t0 > X and e["slot"] > c["s0"]), None)
    if i is None: return None
    a = tr[i]; fee = 0.0125; tok = 0.5e9 * (1 - fee) * a["vt"] / (a["vq"] + 0.5e9); p0 = a["vq"] / a["vt"]; jo = len(tr) - 1
    for j in range(i + 1, len(tr)):
        e = tr[j]
        if e.get("real") == 0 or (tp and e["vq"] / e["vt"] >= tp * p0) or e["t"] - a["t"] >= cap: jo = j; break
        if e["user"] in W and not e["buy"]: jo = min(j + 1, len(tr) - 1); break
    b = tr[jo]; out = b["vq"] - b["vq"] * b["vt"] / (b["vt"] + tok); return out * (1 - fee) / 1e9 - 0.5 - 0.0345
def S(v):
    v = np.array(v)
    if not len(v): return "   0"
    s = np.sort(v); k = max(1, round(0.02 * len(v))); return f"{len(v):4d} {v.sum():+7.2f} ({100 * v.mean() / 0.5:+6.1f}%) w/o 2% {s[:-k].sum() if len(v) > 1 else 0:+7.2f}"
best = None
for X in (5, 10, 20):
    for tp in (1.2, 1.5, 2, None):
        for cap in (60, 120, 300):
            b = [x for c in coins if c["t"] < S0 for x in [trade(c, X, tp, cap)] if x is not None]
            a = [x for c in coins if c["t"] >= S0 for x in [trade(c, X, tp, cap)] if x is not None]
            print(f"   X={X:2d} tp={str(tp):4s} cap={cap:3d}: before {S(b)} | after {S(a)}")
            if len(b) >= 10 and (best is None or np.mean(b) > best[0]): best = (np.mean(b), X, tp, cap, a)
_, X, tp, cap, a = best; v = np.array(a); bs = np.random.default_rng(7).choice(v, size=(10000, len(v))).mean(axis=1) if len(v) else np.zeros(1)
print(f"\nPICKED before Nov 17 13:49: X={X} tp={tp} cap={cap} -> after {S(a)}; P(mean > 0) {np.mean(bs > 0):.1%}")
print(f"PASS: {len(v) >= 10 and v.sum() > 0 and np.sort(v)[:-max(1, round(0.02 * len(v)))].sum() > 0 and np.mean(bs > 0) >= 0.95}")
