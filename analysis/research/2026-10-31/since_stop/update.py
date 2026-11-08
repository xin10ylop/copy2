# The copy over a window [FROM, now] with the plan's settings (1 SOL, max_open 2, tp 2.0, 1790 s, hold through its
# sale) with and without the 0.8 stop, at landings 2 / 4 / 7, by day (Beirut), without the best 2.
#   python3 -I update.py SPD "YYYY-MM-DD HH:MM" (FROM, Beirut time)
import sys, os, io, contextlib, datetime
SPD = sys.argv[1]; FROM = datetime.datetime.strptime(sys.argv[2], "%Y-%m-%d %H:%M").replace(tzinfo=datetime.timezone.utc).timestamp() - 7200
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = [sys.argv[0], SPD, "4"]
with contextlib.redirect_stdout(io.StringIO()): import copy_grid as G
rs = [r for r in G.trips if r["t"] >= FROM]
last = max(r["t"] for r in G.M.rows)
f = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%b %d %H:%M")
print(f"{len(rs)} routable buys from {f(FROM)} to {f(last)} Beirut ({(last - FROM) / 86400:.1f} days); 1 SOL, max_open 2")
for n in (2, 4, 7):
    for name, sl in (("0.8 stop", 0.8), ("no stop ", None)):
        res = G.sim(rs, n=n, cap=2, tp=2.0, sl=sl, hold=1790)
        v = sorted((o["net"] for _, o in res), reverse=True); days = {}
        for r, o in res: days.setdefault(G.day(r["t"]), []).append(o["net"])
        ex = {}
        for _, o in res: ex[o["exit"]] = ex.get(o["exit"], 0) + 1
        print(f"landing {n} {name}: {len(v)} copies, NET {sum(v):+6.2f} SOL, without the best 2 {sum(v[2:]):+6.2f}; by day "
              + "  ".join(f"{d} {sum(x):+.2f}" for d, x in sorted(days.items())) + (f"  exits {ex}" if n == 4 else ""))
