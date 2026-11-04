# The one change "no stop" against the bot as built, since the stop, at landings 2 / 4 / 7, by half, with the worst trades.
#   python3 -I nostop_new.py SPD
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SPD = sys.argv[1]; sys.argv = [sys.argv[0], SPD, "4"]
import copy_grid as G
for n in (2, 4, 7):
    for name, kw in (("as built (stop 0.8)", dict(tp=2.0, sl=0.8, hold=1790)), ("no stop", dict(tp=2.0, sl=None, hold=1790))):
        res = G.sim(G.trips, n=n, **kw); a = G.score([x for x in res if x[0]["t"] < G.T_HALF]); b = G.score([x for x in res if x[0]["t"] >= G.T_HALF])
        nets = sorted(o["net"] for _, o in res if o["exit"] != "refused"); days = {}
        for r, o in res: days.setdefault(G.day(r["t"]), []).append(o["net"])
        print(f"landing {n}  {name:20s} total {a[1] + b[1]:+6.2f}  first half {a[1]:+6.2f} ({a[2]:+6.2f})  second half {b[1]:+6.2f} ({b[2]:+6.2f})  "
              f"worst trades {[round(x, 2) for x in nets[:3]]}  worst day {min(sum(v) for v in days.values()):+.2f}")
