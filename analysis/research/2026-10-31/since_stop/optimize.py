# The exits at our live speed (landing N trades after its buy; the live median is 3-4), every combination picked on the
# first half of the period since the stop and scored on the second, raw model and corrected by its miss on our real
# trades. 1 SOL, max_open 2 (the cap is checked apart).
#   python3 -I optimize.py SPD N
import sys, os, io, contextlib, datetime, itertools
SPD = sys.argv[1]; N = int(sys.argv[2])
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = [sys.argv[0], SPD, "4"]
with contextlib.redirect_stdout(io.StringIO()): import copy_grid as G
T_SPLIT = datetime.datetime(2026, 11, 5, 10, 0, tzinfo=datetime.timezone.utc).timestamp()   # Nov 5 12:00 Beirut
A = [r for r in G.trips if r["t"] < T_SPLIT]; B = [r for r in G.trips if r["t"] >= T_SPLIT]
BIAS = {"tp": 0.189, "time": 0.093, "stop": 0.039}
def score(rs, cap=2, **kw):
    res = G.sim(rs, n=N, cap=cap, **kw)
    raw = sorted((o["net"] for _, o in res), reverse=True)
    cor = sorted((o["net"] + (BIAS.get(o["exit"], 0) if o["exit"] != "refused" else 0) for _, o in res), reverse=True)
    return len(raw), sum(raw), sum(raw[2:]), sum(cor), sum(cor[2:])
f = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%b %d %H:%M")
print(f"landing {N}; first half {len(A)} buys ({f(G.T_STOP)} - {f(T_SPLIT)} Beirut), second half {len(B)} (to {f(max(r['t'] for r in B))})")
grid = []
for tp, sl, hold, follow, pmax in itertools.product((1.5, 1.75, 2.0, 2.5, 3.0), (None, 0.7, 0.8), (300, 600, 900, 1790), (False, True), (1.15, 1.25, 1.5)):
    kw = dict(tp=tp, sl=sl, hold=hold, follow=follow, pmax=pmax)
    grid.append((kw, score(A, **kw), score(B, **kw)))
ours = dict(tp=2.0, sl=None, hold=1790, follow=False, pmax=1.25)
row = lambda g: (f"  tp {g[0]['tp']:<4} stop {str(g[0]['sl']):4s} hold {g[0]['hold']:4d} follow {str(g[0]['follow']):5s} pmax {g[0]['pmax']:.2f} | "
                 f"1st raw {g[1][1]:+6.2f} ({g[1][2]:+6.2f}) cor {g[1][3]:+6.2f} ({g[1][4]:+6.2f}) | 2nd raw {g[2][1]:+6.2f} ({g[2][2]:+6.2f}) cor {g[2][3]:+6.2f} ({g[2][4]:+6.2f})")
for key, name in ((2, "raw"), (4, "corrected")):
    grid.sort(key=lambda g: -g[1][key])
    print(f"\n== top 8 picked on the first half by {name}, without the best 2; then their second half")
    for g in grid[:8]: print(row(g))
    rank = next(i for i, g in enumerate(grid) if g[0] == ours) + 1
    print(f"  ... ours (tp 2.0, no stop, 1790 s, hold through its sale, 1.25) ranks {rank} of {len(grid)} on the first half:")
    print(row(next(g for g in grid if g[0] == ours)))
    gb = sorted(grid, key=lambda g: -g[2][key]); rb = next(i for i, g in enumerate(gb) if g[0] == ours) + 1
    print(f"  ours ranks {rb} of {len(grid)} on the second half; the second half's best:"); print(row(gb[0]))
print("\n== the cap, ours: 1st half / 2nd half, raw (w/o best 2) and corrected")
for cap in (1, 2, 3, 4):
    a, b = score(A, cap=cap, **ours), score(B, cap=cap, **ours)
    print(f"  max_open {cap}: 1st {a[1]:+6.2f} ({a[2]:+6.2f}) cor {a[3]:+6.2f} | 2nd {b[1]:+6.2f} ({b[2]:+6.2f}) cor {b[3]:+6.2f}")
