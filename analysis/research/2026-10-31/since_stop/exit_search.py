# A wide search over our exit rules, since the stop (Oct 29) to Nov 12 08:49 Beirut: picked on the first week, scored on
# the second. Rules: take profit, stop, timer, price limit, a trailing stop, and how to treat wallet 4's sale: hold
# through it, sell behind it, or sell behind it only when we are below a price (hold the winners, cut the losers).
# 1 SOL, 2 open (as live), raw model (model.py's price model q). Score = net without each half's best 2, averaged over
# three landings: in its block 4 and 8 trades after it, and one block late.
#   python3 -I exit_search.py SPD
import sys, os, io, contextlib, itertools, datetime
from multiprocessing import Pool
SPD = sys.argv[1]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD, "4"]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import copy_grid as G
M = G.M; END = max(r["t"] for r in M.rows); MID = END - 7 * 86400
A = [r for r in G.trips if r["t"] < MID]; B = [r for r in G.trips if MID <= r["t"] <= END]
def model(r, n, tp, sl, hold, follow, pmax, trail):
    m, tr = G.P[f"{r['slot']}_{r['mint8']}"]
    k = next((i for i, e in enumerate(tr) if e["user"] == M.W4 and e["buy"] and e["slot"] == r["slot"]), None)
    if k is None: return None
    its = tr[k]; vta = its["vt"]; t0 = its["t"]; rate = r["sol"] * 1e9 / (its["q"] * (1 + its["bps"] / 1e4))
    if n == "slot+1": j = k + len([e for e in tr[k + 1:] if e["slot"] <= its["slot"] + 1])
    else: j = min(k + n, len(tr) - 1)
    ent = tr[j]; px_in = (vta / ent["vt"]) ** 2
    if px_in > pmax: return (-0.0004, "refused", 0)
    Q = 1e9 * (1 - 0.003) / rate; net_in = Q * 1e4 / (1e4 + ent["bps"]); tok = ent["vt"] - ent["vt"] * ent["vq"] / (ent["vq"] + net_in)
    ex, why, peak = None, "time", px_in
    for i in range(j + 1, len(tr)):
        e = tr[i]; px = (vta / e["vt"]) ** 2; peak = max(peak, px)
        if e.get("real") == 0: why, ex = "graduated", i; break
        if follow is not None and e["user"] == M.W4 and not e["buy"] and px < follow: why, ex = "its_sell", min(i + 1, len(tr) - 1); break
        if tp and px >= tp: why, ex = "tp", min(i + 1, len(tr) - 1); break
        if sl and px <= sl: why, ex = "stop", min(i + 1, len(tr) - 1); break
        if trail and peak >= 1.3 and px <= peak * trail: why, ex = "trail", min(i + 1, len(tr) - 1); break
        if e["t"] - t0 >= hold: why, ex = "time", i; break
    if ex is None: ex = len(tr) - 1
    x = tr[ex]; vq_r = x["vq"] + net_in; vt_r = x["vt"] * x["vq"] / vq_r
    out = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - x["bps"] / 1e4)
    return (out * rate * (1 - 0.003) / 1e9 - 1.0 - 0.0026, why, x["t"] - t0)
def sim(rs, n, kw):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x > r["t"]]
        if len(open_) >= 2: continue
        o = model(r, n, **kw)
        if o is None: continue
        if o[1] != "refused": open_.append(r["t"] + o[2])
        out.append(o)
    v = sorted((o[0] for o in out), reverse=True); return len(v), sum(v), sum(v[2:])
LAND = (4, 8, "slot+1")
def ev(kw): return kw, [sim(A, n, kw) for n in LAND], [sim(B, n, kw) for n in LAND]
FOLLOW = {"hold": None, "follow": 1e9, "follow<1.0": 1.0, "follow<1.5": 1.5, "follow<2.0": 2.0}
grid = [dict(tp=tp, sl=sl, hold=h, follow=FOLLOW[f], pmax=pm, trail=tl)
        for tp, sl, h, f, pm, tl in itertools.product((1.5, 2.0, 2.5, 3.0, 4.0, None), (None, 0.5, 0.6, 0.7), (300, 600, 1790),
                                                      FOLLOW, (1.15, 1.25), (None, 0.5, 0.7))]
name = lambda kw: (f"{next(f for f, v in FOLLOW.items() if v == kw['follow']):10s} tp {str(kw['tp']):4s} stop {str(kw['sl']):4s} "
                   f"{kw['hold']:4d}s limit {kw['pmax']:.2f} trail {str(kw['trail']):4s}")
if __name__ == "__main__":
    with Pool(4) as p: res = p.map(ev, grid)
    sa = lambda r: sum(x[2] for x in r[1]) / 3; sb = lambda r: sum(x[2] for x in r[2]) / 3
    fa = lambda r: sum(x[1] for x in r[1]) / 3; fb = lambda r: sum(x[1] for x in r[2]) / 3
    f = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d %H:%M")
    print(f"{len(grid)} rule sets; pick week {f(G.T_STOP)} to {f(MID)} ({len(A)} buys), test week to {f(END)} ({len(B)} buys), Beirut")
    print("1 SOL, 2 open, raw model; SOL = mean over landings 4, 8 and one block late; (w/o best 2)")
    hdr = f"   {'rule set':66s} | pick week: net (w/o best 2) | TEST week: net (w/o best 2) | test by landing 4 / 8 / late (w/o best 2)"
    row = lambda r: print(f"   {name(r[0]):66s} | {fa(r):+6.2f} ({sa(r):+6.2f})          | {fb(r):+6.2f} ({sb(r):+6.2f})           | "
                          + " / ".join(f"{x[2]:+.2f}" for x in r[2]))
    live = next(r for r in res if r[0] == dict(tp=2.5, sl=None, hold=1790, follow=None, pmax=1.25, trail=None))
    fol = next(r for r in res if r[0] == dict(tp=2.5, sl=None, hold=1790, follow=1e9, pmax=1.25, trail=None))
    print("\n== live, and live with its sale followed"); print(hdr); row(live); row(fol)
    res.sort(key=lambda r: -sa(r))
    print("\n== the 15 best on the pick week (without the best 2), and how they did the next week"); print(hdr)
    for r in res[:15]: row(r)
    print(f"\n   of the 50 best on the pick week, {sum(1 for r in res[:50] if sb(r) > sb(live))} beat live on the test week (w/o best 2); "
          f"of all {len(res)}, {sum(1 for r in res if sb(r) > sb(live))}")
    # by rule family: the average test-week result of each choice, over every rule set with it
    print("\n== each choice on its own: the mean TEST-week result (w/o best 2) over every rule set that has it, and the pick week's")
    for key, vals in (("follow", FOLLOW.values()), ("tp", (1.5, 2.0, 2.5, 3.0, 4.0, None)), ("sl", (None, 0.5, 0.6, 0.7)),
                      ("hold", (300, 600, 1790)), ("pmax", (1.15, 1.25)), ("trail", (None, 0.5, 0.7))):
        cells = []
        for v in vals:
            rr = [r for r in res if r[0][key] == v]
            lab = next(n for n, x in FOLLOW.items() if x == v) if key == "follow" else str(v)
            cells.append(f"{lab} {sum(map(sa, rr))/len(rr):+.2f} / {sum(map(sb, rr))/len(rr):+.2f}")
        print(f"   {key:6s}: " + "   ".join(cells))
    res.sort(key=lambda r: -sb(r)); print("\n== the 5 best on the test week (hindsight, for scale)"); print(hdr)
    for r in res[:5]: row(r)
