# The 2-minute timer that low_tp.py turned up (tp 2.5-3.0, 120 s): by day and by landing, against the live 30 minutes.
#   python3 -I short_timer.py SPD
import sys, os, io, contextlib, datetime
SPD = sys.argv[1]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import exit_search as E
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
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
R = {"live tp 2.5, 30 min": dict(tp=2.5, hold=1790), "tp 2.5, 2 min": dict(tp=2.5, hold=120), "tp 3.0, 2 min": dict(tp=3.0, hold=120),
     "tp 2.5, 3 min": dict(tp=2.5, hold=180), "tp 2.5, 90 s": dict(tp=2.5, hold=90)}
rs = E.A + E.B
for name, kw in R.items():
    kw = dict(kw, sl=None, follow=None, pmax=1.25, trail=None)
    by = {n: run(rs, n, kw) for n in E.LAND}
    days = {}
    for r, o in by[4]: days.setdefault(day(r["t"]), 0.0); days[day(r["t"])] += o[0]
    land = " / ".join(f"{sum(o[0] for _, o in v):+.2f}" for v in by.values())
    print(f"{name:20s} landing 4 / 8 / late: {land}; days up {sum(1 for v in days.values() if v > 0)} of {len(days)}")
    print("   by day (landing 4): " + " ".join(f"{d} {v:+.2f}" for d, v in sorted(days.items())))
