# Lower take profits (1.1-3.0x the price its buy left) with timers, holding through its sale or selling behind it.
# Oct 29 - Nov 12, week 1 / week 2, 1 SOL, 2 open, raw model, mean over landing 4 / 8 / one block late. No stop.
#   python3 -I low_tp.py SPD
import sys, os, io, contextlib, itertools
from multiprocessing import Pool
SPD = sys.argv[1]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import exit_search as E
TPS = (1.1, 1.2, 1.3, 1.4, 1.5, 1.75, 2.0, 2.5, 3.0); HOLDS = (60, 120, 300, 600, 1790)
def detail(rs, n, kw):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x > r["t"]]
        if len(open_) >= 2: continue
        o = E.model(r, n, **kw)
        if o is None: continue
        if o[1] != "refused": open_.append(r["t"] + o[2])
        out.append(o)
    v = sorted((o[0] for o in out), reverse=True); took = [o for o in out if o[1] != "refused"]
    return len(took), sum(v), sum(v[2:]), sum(1 for o in took if o[1] == "tp") / max(1, len(took))
def ev(a):
    tp, hold, fol = a; kw = dict(tp=tp, sl=None, hold=hold, follow=fol, pmax=1.25, trail=None)
    return a, [[detail(W, n, kw) for n in E.LAND] for W in (E.A, E.B)]
if __name__ == "__main__":
    with Pool(4) as p: res = p.map(ev, list(itertools.product(TPS, HOLDS, (None, 1e9))))
    m = lambda w, i: sum(x[i] for x in w) / 3
    for fol, lab in ((None, "HOLD through its sale"), (1e9, "SELL BEHIND its sale")):
        print(f"\n== {lab}: net SOL, week 1 / week 2 / both (both without each week's best 2); tp hit rate")
        print("   tp    " + "".join(f"| {h:>4d} s                       " for h in HOLDS))
        for tp in TPS:
            cells = []
            for h in HOLDS:
                w1, w2 = next(r[1] for r in res if r[0] == (tp, h, fol))
                cells.append(f"| {m(w1,1):+6.2f} {m(w2,1):+6.2f} {m(w1,1)+m(w2,1):+6.2f} ({m(w1,2)+m(w2,2):+6.2f}) {100*(m(w1,3)+m(w2,3))/2:3.0f}% ")
            print(f"   {tp:<5}" + "".join(cells))
    best = sorted(res, key=lambda r: -(m(r[1][0], 2)))[:5]
    print("\n== the 5 best on week 1 (without its best 2), and week 2")
    for a, (w1, w2) in best:
        print(f"   tp {a[0]} hold {a[1]} {'follow' if a[2] else 'hold'}: week 1 {m(w1,1):+.2f} ({m(w1,2):+.2f}), week 2 {m(w2,1):+.2f} ({m(w2,2):+.2f}), copies {m(w1,0):.0f}/{m(w2,0):.0f}")
