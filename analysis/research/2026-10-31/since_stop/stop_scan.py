# Stop losses with the live rule (tp 2.4, 30 min, holding through its sale): none, 0.3-0.8x the price its buy left.
# Two weeks, 1 SOL, 2 open, raw model, mean over landing 4 / 8 / one block late. And how often a coin that fell to X
# came back: of the copies that touched X, how many still reached the take profit, and the share that ended above the
# entry. Calibration (calib.py, Oct 28-29 live trades): real minus model +3.9 points on stop exits, +9.3 on timer
# exits, +18.9 on take profits; "adj" moves each copy a stop turns from a timer/tp exit by that difference.
#   python3 -I stop_scan.py SPD
import sys, os, io, contextlib
from multiprocessing import Pool
SPD = sys.argv[1]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import exit_search as E
CAL = {"stop": 0.039, "time": 0.093, "tp": 0.189, "graduated": 0.093, "refused": 0.0}
SL = (None, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)
def run(rs, n, kw):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x > r["t"]]
        if len(open_) >= 2: continue
        o = E.model(r, n, **kw)
        if o is None: continue
        if o[1] != "refused": open_.append(r["t"] + o[2])
        out.append(o)
    return out
def ev(sl):
    kw = dict(tp=2.4, sl=sl, hold=1790, follow=None, pmax=1.25, trail=None); res = {}
    for wk, W in (("w1", E.A), ("w2", E.B)):
        xs = [run(W, n, kw) for n in E.LAND]
        res[wk] = (sum(sum(o[0] for o in x) for x in xs) / 3, sum(sum(sorted((o[0] for o in x), reverse=True)[2:]) for x in xs) / 3,
                   sum(sum(o[0] + CAL[o[1]] for o in x) for x in xs) / 3, sum(sum(1 for o in x if o[1] == "stop") for x in xs) / 3)
    return sl, res
if __name__ == "__main__":
    with Pool(4) as p: R = dict(p.map(ev, SL))
    print("tp 2.4, 30 min, holding; SOL at 1 SOL, two weeks")
    print("stop  | week 1 | week 2 |  both  | both w/o best 2s | both calibrated | stops hit")
    for sl in SL:
        x = R[sl]
        print(f"{str(sl):5s} | {x['w1'][0]:+6.2f} | {x['w2'][0]:+6.2f} | {x['w1'][0]+x['w2'][0]:+6.2f} | {x['w1'][1]+x['w2'][1]:+16.2f} | "
              f"{x['w1'][2]+x['w2'][2]:+15.2f} | {x['w1'][3]+x['w2'][3]:5.0f}" + ("   <- live" if sl is None else ""))
    # recoveries: every copy (no slot limit), landing 4, no stop: did it touch X, and how did it end
    print("\nevery copy, landing 4, no stop: of those whose price touched X (x the price its buy left)")
    print("  X    touched  then reached tp 2.4   ended above our entry   their result with no stop / with a stop at X")
    for X in (0.3, 0.4, 0.5, 0.6, 0.7):
        tch = tp = up = 0; s0 = s1 = 0.0
        for r in E.A + E.B:
            m, tr = E.G.P[f"{r['slot']}_{r['mint8']}"]
            a = E.model(r, 4, tp=2.4, sl=None, hold=1790, follow=None, pmax=1.25, trail=None)
            b = E.model(r, 4, tp=2.4, sl=X, hold=1790, follow=None, pmax=1.25, trail=None)
            if not a or not b or a[1] == "refused" or b[1] != "stop": continue
            tch += 1; tp += a[1] == "tp"; up += a[0] > 0; s0 += a[0]; s1 += b[0]
        print(f"  {X:.1f}  {tch:7d}  {tp:10d}            {up:10d}              {s0:+7.2f} / {s1:+7.2f}")
