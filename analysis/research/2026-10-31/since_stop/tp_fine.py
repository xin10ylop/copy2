# Take profit 1.8-3.0 in steps of 0.1 (30 min, holding through its sale, no stop): two weeks, 1 SOL, 2 open, raw model,
# mean over landing 4 / 8 / one block late; days up at landing 4; and the take profit's hit rate.
#   python3 -I tp_fine.py SPD
import sys, os, io, contextlib, datetime
from multiprocessing import Pool
SPD = sys.argv[1]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import exit_search as E
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
TPS = [round(1.8 + 0.1 * i, 1) for i in range(13)]
def run(rs, n, kw):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x > r["t"]]
        if len(open_) >= 2: continue
        o = E.model(r, n, **kw)
        if o is None: continue
        if o[1] != "refused": open_.append(r["t"] + o[2])
        out.append((r, o))
    return out
def ev(tp):
    kw = dict(tp=tp, sl=None, hold=1790, follow=None, pmax=1.25, trail=None); res = {}
    for wk, W in (("w1", E.A), ("w2", E.B)):
        xs = [run(W, n, kw) for n in E.LAND]
        res[wk] = (sum(sum(o[0] for _, o in x) for x in xs) / 3, sum(sum(sorted((o[0] for _, o in x), reverse=True)[2:]) for x in xs) / 3,
                   sum(sum(1 for _, o in x if o[1] == "tp") / max(1, sum(1 for _, o in x if o[1] != "refused")) for x in xs) / 3)
    d = {}
    for r, o in run(E.A + E.B, 4, kw): d[day(r["t"])] = d.get(day(r["t"]), 0) + o[0]
    res["up"] = sum(1 for v in d.values() if v > 0), len(d)
    return tp, res
if __name__ == "__main__":
    with Pool(4) as p: R = dict(p.map(ev, TPS))
    print("tp    | week 1 | week 2 |  both  | both w/o best 2s | tp hit | days up")
    for tp in TPS:
        x = R[tp]
        print(f"{tp:<5} | {x['w1'][0]:+6.2f} | {x['w2'][0]:+6.2f} | {x['w1'][0]+x['w2'][0]:+6.2f} | {x['w1'][1]+x['w2'][1]:+16.2f} | "
              f"{100*(x['w1'][2]+x['w2'][2])/2:5.0f}% | {x['up'][0]}/{x['up'][1]}" + ("   <- live" if tp == 2.5 else ""))
