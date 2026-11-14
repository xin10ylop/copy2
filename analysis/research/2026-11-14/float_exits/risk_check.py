# The run at the rule chosen (tp 3.0, 1200 s, early 30-290 s under 1.5x, no stop), 0.5 SOL, 2 open (SOL 1, WBTC 2,
# PUMP 1, SPCX 1): by day, the deepest fall
# from a high and when, with and without the 1.0 SOL daily stop (UTC day), at each landing.
#   python3 -I risk_check.py SPD [STAKE]
import sys, os, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:3]; import float_exits as F
import lib as L
NEW = dict(tp=3.0, hold=1200, early=(30, 290, 1.5), sl=None); CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
f = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d %H:%M")
for n in L.LAND:
    res = F.sim(F.rows, n, NEW, caps=CAPS)
    for stop in (None, 1.0):
        tot = dd = worst = 0.0; day = None; dsum = 0.0; at = lo = None; start = None; n_ = 0
        for r, net, why in res:
            d = int(r["t"] // 86400)
            if d != day: day, dsum = d, 0.0
            if stop and dsum <= -stop: continue                # the daily stop: no new buys that UTC day
            dsum += net; tot += net; n_ += 1
            if dd == 0.0: start = r["t"]
            dd = min(0.0, dd + net)
            if dd < worst: worst, at, lo = dd, start, r["t"]
        print(f"landing {str(n):6s} daily stop {str(stop):4s}: {n_} copies, net {tot:+6.2f} SOL; deepest fall {worst:+.2f} SOL, from {f(at)} to {f(lo)} Beirut")
import collections, statistics
res = F.sim(F.rows, 4, NEW, caps=CAPS); byday = collections.defaultdict(float)
for r, net, why in res: byday[datetime.datetime.fromtimestamp(r["t"], datetime.timezone.utc).strftime("%m-%d")] += net
v = sorted(byday.values())
print(f"landing 4 by UTC day: {len(v)} days, {sum(1 for x in v if x > 0)} up; worst {v[0]:+.2f}, median {statistics.median(v):+.2f}, best {v[-1]:+.2f}; the best 3 days {sum(v[-3:]):+.2f} of {sum(v):+.2f}")
print("   " + "  ".join(f"{d} {x:+.2f}" for d, x in sorted(byday.items())))
by = collections.defaultdict(list)
for r, net, why in res: by[r["anchor"]].append(net)
print("   by what we pay with: " + "; ".join(f"{k} {len(x)} copies {sum(x):+.2f} ({sum(1 for y in x if y > 0)} won)" for k, x in by.items()) + f"; exits {dict(collections.Counter(x[2] for x in res))}")
