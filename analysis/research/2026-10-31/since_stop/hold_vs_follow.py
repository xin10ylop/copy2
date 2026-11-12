# Last 7 days: hold through its sale (live) against selling behind it, and stop losses, at our live landing.
# Per coin: what holding past its sale gained or lost against following it. 1 SOL, max_open 2, raw model (q).
#   python3 -I hold_vs_follow.py SPD
import sys, os, io, contextlib, datetime
SPD = sys.argv[1]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD, "4"]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import copy_grid as G
END = max(r["t"] for r in G.M.rows); T0 = END - 7 * 86400; MID = T0 + 3.5 * 86400
rs = [r for r in G.trips if r["t"] >= T0]
bt = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d %H:%M")
print(f"{bt(T0)} to {bt(END)} Beirut: {len(rs)} routable buys; 1 SOL, 2 open, tp 2.5, 1790 s, price limit 1.25")
LIVE = dict(tp=2.5, sl=None, hold=1790, follow=False, pmax=1.25)
for n in (4, 8):
    print(f"\n== landing {n} trades after its buy (live: 3, 7, 8)")
    print(f"   {'variant':34s} {'n':>3s} {'net':>7s} {'w/o best 2':>10s} {'1st half':>8s} {'2nd half':>8s}  exits")
    for name, kw in (("LIVE: hold, no stop", {}), ("follow its sale, no stop", dict(follow=True)),
                     ("hold, stop 0.8", dict(sl=0.8)), ("hold, stop 0.7", dict(sl=0.7)), ("hold, stop 0.6", dict(sl=0.6)),
                     ("hold, stop 0.5", dict(sl=0.5)), ("follow its sale, stop 0.7", dict(follow=True, sl=0.7))):
        res = G.sim(rs, n, 2, **dict(LIVE, **kw)); c, s, s2 = G.score(res)
        h1 = sum(o["net"] for r, o in res if r["t"] < MID); ex = {}
        for _, o in res: ex[o["exit"]] = ex.get(o["exit"], 0) + 1
        print(f"   {name:34s} {c:3d} {s:+7.2f} {s2:+10.2f} {h1:+8.2f} {s-h1:+8.2f}  {ex}")
    # coin by coin, the same coins: hold (live) minus follow
    d = []
    for r in rs:
        m, tr = G.P[f"{r['slot']}_{r['mint8']}"]
        a = G.M.model(r, m, tr, 1.0, n, **LIVE); b = G.M.model(r, m, tr, 1.0, n, **dict(LIVE, follow=True))
        if "net" in a and "net" in b and a["exit"] != "refused": d.append((a["net"] - b["net"], a["net"], b["net"], r["mint8"]))
    diff = [x for x in d if abs(x[0]) > 1e-9]
    win = [x for x in diff if x[0] > 0]; lose = [x for x in diff if x[0] < 0]
    print(f"   coin by coin (every buy, no slot limit): holding differs from following on {len(diff)} of {len(d)}")
    print(f"     holding better on {len(win)}: +{sum(x[0] for x in win):.2f} SOL (biggest {', '.join(f'{x[3]} +{x[0]:.2f}' for x in sorted(win)[::-1][:3])})")
    print(f"     holding worse  on {len(lose)}: {sum(x[0] for x in lose):.2f} SOL (average {sum(x[0] for x in lose)/max(len(lose),1):+.3f})")
    print(f"     net for holding {sum(x[0] for x in diff):+.2f}; without its best 2 coins {sum(sorted(x[0] for x in diff)[:-2]):+.2f}")
