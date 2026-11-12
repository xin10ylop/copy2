# A take profit that steps down: 2.5x until T seconds after its buy, then L until the 30-minute timer. Holding through
# its sale, no stop, 1 SOL, 2 open, raw model, mean over landing 4 / 8 / one block late; week 1 / week 2.
#   python3 -I tp_step.py SPD
import sys, os, io, contextlib, itertools
from multiprocessing import Pool
SPD = sys.argv[1]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import exit_search as E
M = E.M; G = E.G
def model(r, n, T, L, tp=2.5, hold=1790, pmax=1.25):
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
        if px >= tp: why, ex = "tp", min(i + 1, len(tr) - 1); break
        if age >= T and px >= L: why, ex = "tp_low", min(i + 1, len(tr) - 1); break
        if age >= hold: why, ex = "time", i; break
    if ex is None: ex = len(tr) - 1
    x = tr[ex]; vq_r = x["vq"] + net_in; vt_r = x["vt"] * x["vq"] / vq_r
    out = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - x["bps"] / 1e4)
    return (out * rate * (1 - 0.003) / 1e9 - 1.0 - 0.0026, why, x["t"] - t0)
def sim(rs, n, T, L):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x > r["t"]]
        if len(open_) >= 2: continue
        o = model(r, n, T, L)
        if o is None: continue
        if o[1] != "refused": open_.append(r["t"] + o[2])
        out.append(o)
    v = sorted((o[0] for o in out), reverse=True); took = [o for o in out if o[1] != "refused"]
    return sum(v), sum(v[2:]), sum(1 for o in took if o[1] == "tp_low") / max(1, len(took))
TS = (120, 300, 600, 1000, 1300, 1600); LS = (1.0, 1.1, 1.2, 1.3, 1.5, 2.0)
def ev(a): return a, [[sim(W, n, *a) for n in E.LAND] for W in (E.A, E.B)]
if __name__ == "__main__":
    with Pool(4) as p: res = dict(p.map(ev, list(itertools.product(TS, LS))))
    m = lambda w, i: sum(x[i] for x in w) / 3
    live = [[E.sim(W, n, dict(tp=2.5, sl=None, hold=1790, follow=None, pmax=1.25, trail=None)) for n in E.LAND] for W in (E.A, E.B)]
    print(f"live (tp 2.5 to the end): week 1 {m(live[0],1):+.2f} ({m(live[0],2):+.2f}), week 2 {m(live[1],1):+.2f} ({m(live[1],2):+.2f}), "
          f"both {m(live[0],1)+m(live[1],1):+.2f} ({m(live[0],2)+m(live[1],2):+.2f})")
    print("\nweek 1 / week 2 / both (both without each week's best 2), and the share of copies sold by the lowered target")
    print("   then " + "".join(f"| after {t:>4d} s                       " for t in TS))
    for L in LS:
        cells = []
        for T in TS:
            w1, w2 = res[(T, L)]
            cells.append(f"| {m(w1,0):+6.2f} {m(w2,0):+6.2f} {m(w1,0)+m(w2,0):+6.2f} ({m(w1,1)+m(w2,1):+6.2f}) {100*(m(w1,2)+m(w2,2))/2:3.0f}% ")
        print(f"   {L:<5}" + "".join(cells))
