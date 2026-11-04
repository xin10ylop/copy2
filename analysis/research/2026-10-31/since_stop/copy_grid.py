# The copy since the stop (Oct 29 13:52 Beirut, the bot's last sale, to the end of the data) with max_open 3, at 1 SOL,
# by day; then the exits as a grid, picked on the first half (to Nov 1 00:00 Beirut) without each half's best 2, and
# scored on the second half. model.py's model() with its exits as parameters; landing N trades after its buy.
#   python3 -I copy_grid.py SPD [N]
import sys, os, json, gzip, datetime, itertools
SPD = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 4
sys.argv = [sys.argv[0], SPD]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import model as M
P = json.load(gzip.open(f"{SPD}/paths.json.gz"))
T_STOP = 1793274720 + 600; T_HALF = datetime.datetime(2026, 10, 31, 22, 0, tzinfo=datetime.timezone.utc).timestamp()  # Nov 1 00:00 Beirut
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
trips = sorted((r for r in M.rows if r["t"] >= T_STOP and f"{r['slot']}_{r['mint8']}" in P), key=lambda r: r["t"])
def sim(rs, n=N, cap=3, **kw):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x > r["t"]]
        if len(open_) >= cap: continue
        m, tr = P[f"{r['slot']}_{r['mint8']}"]; o = M.model(r, m, tr, 1.0, n, **kw)
        if "net" not in o: continue
        if o["exit"] != "refused": open_.append(r["t"] + o.get("held", 0))
        out.append((r, o))
    return out
def score(res):
    v = sorted((o["net"] for _, o in res), reverse=True); return len(v), sum(v), sum(v[2:])
A = [r for r in trips if r["t"] < T_HALF]; B = [r for r in trips if r["t"] >= T_HALF]
base = dict(tp=2.0, sl=0.8, hold=1790, follow=False, pmax=1.25)
print(f"{len(trips)} routable buys since the stop ({len(A)} to Nov 1 00:00 Beirut, {len(B)} after); 1 SOL, max_open 3, landing {N}")
for name, kw in (("AS BUILT (tp 2.0, stop 0.8, 1790 s, hold through its sale)", base), ("the same, but sell behind its sale (follow_its_sell = true)", dict(base, follow=True))):
    res = sim(trips, **kw); n, s, s2 = score(res); ex = {}
    for _, o in res: ex[o["exit"]] = ex.get(o["exit"], 0) + 1
    days = {}
    for r, o in res: days.setdefault(day(r["t"]), []).append(o["net"])
    print(f"\n== {name}: {n} copies, NET {s:+.2f} SOL, without the best 2 {s2:+.2f}; exits {ex}")
    print("   by day:", "  ".join(f"{d} {len(v)} {sum(v):+.2f}" for d, v in sorted(days.items())))
grid = []
for tp, sl, hold, follow, pmax in itertools.product((1.3, 1.5, 1.75, 2.0, 2.5, None), (0.7, 0.8, 0.9, None), (120, 300, 600, 1790), (False, True), (1.15, 1.25)):
    kw = dict(tp=tp, sl=sl, hold=hold, follow=follow, pmax=pmax)
    a, b = score(sim(A, **kw)), score(sim(B, **kw))
    grid.append((a[2], a, b, kw))
grid.sort(key=lambda g: -g[0])
print(f"\n== the exit grid ({len(grid)} variants): picked on the first half without its best 2, scored on the second")
print(f"   {'tp':>4s} {'stop':>4s} {'hold':>5s} {'follow':>6s} {'pmax':>4s} | first half: n, net (w/o best 2) | second half: n, net (w/o best 2)")
show = lambda g: print(f"   {str(g[3]['tp']):>4s} {str(g[3]['sl']):>4s} {g[3]['hold']:5d} {str(g[3]['follow']):>6s} {g[3]['pmax']:4.2f} | {g[1][0]:3d} {g[1][1]:+6.2f} ({g[1][2]:+6.2f}) | {g[2][0]:3d} {g[2][1]:+6.2f} ({g[2][2]:+6.2f})")
for g in grid[:12]: show(g)
print("   ... as built:"); show(next(g for g in grid if g[3] == base))
print(f"   second half positive without its best 2: {sum(1 for g in grid if g[2][2] > 0)} of {len(grid)} variants; best second half: ", end="")
show(max(grid, key=lambda g: g[2][2]))
