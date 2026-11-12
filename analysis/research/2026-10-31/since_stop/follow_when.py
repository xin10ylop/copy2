# Sell behind wallet 4's sale only when its sale comes at a certain age (seconds from its buy), otherwise keep our own
# exits (tp 2.4, 30 min, no stop). Windows [a, b): follow a sale at age a..b. Also "follow if it sells early AND we
# are below a price". Picked on week 1 (mean of landings 4 / 8 / one block late, without the best 2), scored on week 2.
# 1 SOL, 2 open, raw model.
#   python3 -I follow_when.py SPD
import sys, os, io, contextlib, itertools
from multiprocessing import Pool
SPD = sys.argv[1]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import exit_search as E
M = E.M; G = E.G
def model(r, n, a, b, below=1e9, tp=2.4, hold=1790, pmax=1.25):
    m, tr = G.P[f"{r['slot']}_{r['mint8']}"]
    k = next((i for i, e in enumerate(tr) if e["user"] == M.W4 and e["buy"] and e["slot"] == r["slot"]), None)
    if k is None: return None
    its = tr[k]; vta = its["vt"]; t0 = its["t"]; rate = r["sol"] * 1e9 / (its["q"] * (1 + its["bps"] / 1e4))
    j = k + len([e for e in tr[k + 1:] if e["slot"] <= its["slot"] + 1]) if n == "slot+1" else min(k + n, len(tr) - 1)
    ent = tr[j]; px_in = (vta / ent["vt"]) ** 2
    if px_in > pmax: return (-0.0004, "refused", 0)
    Q = 1e9 * (1 - 0.003) / rate; net_in = Q * 1e4 / (1e4 + ent["bps"]); tok = ent["vt"] - ent["vt"] * ent["vq"] / (ent["vq"] + net_in)
    ex, why = None, "time"
    for i in range(j + 1, len(tr)):
        e = tr[i]; px = (vta / e["vt"]) ** 2; age = e["t"] - t0
        if e.get("real") == 0: why, ex = "graduated", i; break
        if e["user"] == M.W4 and not e["buy"] and a <= age < b and px < below: why, ex = "its_sell", min(i + 1, len(tr) - 1); break
        if px >= tp: why, ex = "tp", min(i + 1, len(tr) - 1); break
        if age >= hold: why, ex = "time", i; break
    if ex is None: ex = len(tr) - 1
    x = tr[ex]; vq_r = x["vq"] + net_in; vt_r = x["vt"] * x["vq"] / vq_r
    out = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - x["bps"] / 1e4)
    return (out * rate * (1 - 0.003) / 1e9 - 1.0 - 0.0026, why, x["t"] - t0)
def sim(rs, n, kw):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x > r["t"]]
        if len(open_) >= 2: continue
        o = model(r, n, **kw)
        if o is None: continue
        if o[1] != "refused": open_.append(r["t"] + o[2])
        out.append(o)
    v = sorted((o[0] for o in out), reverse=True)
    return sum(v), sum(v[2:]), sum(1 for o in out if o[1] == "its_sell")
EDGES = (0, 30, 60, 120, 180, 240, 300, 420, 600, 900, 1200, 1790)
GRID = [dict(a=a, b=b, below=bl) for a, b in itertools.combinations(EDGES, 2) for bl in (1e9, 1.0, 1.5)]
def ev(kw):
    w = [[sim(W, n, kw) for n in E.LAND] for W in (E.A, E.B)]
    m = lambda x, i: sum(y[i] for y in x) / 3
    return kw, (m(w[0], 0), m(w[0], 1), m(w[0], 2)), (m(w[1], 0), m(w[1], 1), m(w[1], 2))
if __name__ == "__main__":
    with Pool(4) as p: R = p.map(ev, [dict(a=0, b=0, below=1e9)] + GRID)
    base = R[0]; R = R[1:]
    lab = lambda kw: f"follow its sale at {kw['a']}-{kw['b']} s" + ("" if kw["below"] > 100 else f" if below {kw['below']}x")
    row = lambda r: print(f"   {lab(r[0]):42s} | {r[1][0]:+6.2f} ({r[1][1]:+6.2f}) {r[1][2]:4.0f} | {r[2][0]:+6.2f} ({r[2][1]:+6.2f}) {r[2][2]:4.0f} | {r[1][0]+r[2][0]:+6.2f}")
    print(f"{len(R)} rules; tp 2.4, 30 min, no stop; 1 SOL, 2 open, raw, mean of 3 landings")
    print(f"   {'rule':42s} | week 1 (w/o 2) follows | week 2 (w/o 2) follows | both")
    print(f"   {'LIVE: never follow':42s} | {base[1][0]:+6.2f} ({base[1][1]:+6.2f})      | {base[2][0]:+6.2f} ({base[2][1]:+6.2f})      | {base[1][0]+base[2][0]:+6.2f}")
    R.sort(key=lambda r: -r[1][1])
    print("\n== the 12 best on week 1 (without the best 2), and their week 2")
    for r in R[:12]: row(r)
    print(f"\n   beat live in BOTH weeks without the best 2: {sum(1 for r in R if r[1][1] > base[1][1] and r[2][1] > base[2][1])} of {len(R)}")
    for r in sorted((r for r in R if r[1][1] > base[1][1] and r[2][1] > base[2][1]), key=lambda r: -(r[1][1] + r[2][1]))[:10]: row(r)
