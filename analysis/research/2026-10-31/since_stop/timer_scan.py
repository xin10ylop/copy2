# The timer, finely: 30 s to 30 min (the cached paths end 31 min after its buy, so nothing longer can be tested), with
# tp 2.5 (live) and 3.0, holding through its sale or selling behind it. Two weeks, 1 SOL, 2 open, raw model, mean over
# landing 4 / 8 / one block late; days up at landing 4.
#   python3 -I timer_scan.py SPD
import sys, os, io, contextlib, itertools, datetime
from multiprocessing import Pool
SPD = sys.argv[1]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import exit_search as E
HOLDS = (30, 60, 90, 120, 150, 180, 240, 300, 420, 600, 900, 1200, 1500, 1790)
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
def run(rs, n, kw):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x > r["t"]]
        if len(open_) >= 2: continue
        o = E.model(r, n, **kw)
        if o is None: continue
        if o[1] != "refused": open_.append(r["t"] + o[2])
        out.append((r, o[0]))
    return out
def ev(a):
    tp, h, fol = a; kw = dict(tp=tp, sl=None, hold=h, follow=fol, pmax=1.25, trail=None)
    res = {}
    for wk, W in (("w1", E.A), ("w2", E.B)):
        xs = [run(W, n, kw) for n in E.LAND]
        res[wk] = (sum(sum(v for _, v in x) for x in xs) / 3, sum(sum(sorted((v for _, v in x), reverse=True)[2:]) for x in xs) / 3)
    d = {}
    for r, v in run(E.A + E.B, 4, kw): d[day(r["t"])] = d.get(day(r["t"]), 0) + v
    res["up"] = (sum(1 for v in d.values() if v > 0), len(d))
    return a, res
if __name__ == "__main__":
    with Pool(4) as p: R = dict(p.map(ev, list(itertools.product((2.5, 3.0), HOLDS, (None, 1e9)))))
    for tp in (2.5, 3.0):
        for fol, lab in ((None, "hold through its sale"), (1e9, "sell behind its sale")):
            print(f"\n== tp {tp}, {lab}: week 1 | week 2 | both | both without each week's best 2 | days up (landing 4)")
            for h in HOLDS:
                x = R[(tp, h, fol)]
                print(f"   {h:5d} s  {x['w1'][0]:+6.2f} | {x['w2'][0]:+6.2f} | {x['w1'][0]+x['w2'][0]:+6.2f} | {x['w1'][1]+x['w2'][1]:+6.2f} | {x['up'][0]:2d}/{x['up'][1]}"
                      + ("   <- live" if (tp, h, fol) == (2.5, 1790, None) else ""))
