# Day by day (Nov 19; the owner: "backtest yesterday, what were the results? were they close to today but ended up
# profitable?"). The settings that ran live on Nov 19 morning (wallet 1 tp 4 600 s; wallet 2 tp 3.5 600 s sp 10/30;
# wallet 3 tp 2.5 300 s sp 8/60 stall 240; the group tp 3.5 600 s stall 240 early sale), exact model, landing 2/3/5 blocks,
# every coin; per UTC day: copies, won, take profits hit, the best copy, net ETH, and the day without its best copy.
#   python3 -I rhd14_daily.py DIR GROUPS_JSON > out/rhd14_daily.txt
import sys, os, json, collections, numpy as np, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
T, H, S, ST, I = R.TP, R.HOLD, R.SPS, R.STALL, R.ITS
D, GJ = sys.argv[1], sys.argv[2]; DATA = R.Data(D)
G = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
W = {"w1": ({"0x9a3955a122ab8a649a8511df2dce169471fd0ec1"}, 0.1, 0.5, 1.5, (T.index(4), H.index(600), 0, 0, 0)),
     "w2": ({"0x5bc235acecff3dde394f4bfc696f7c35efd502f0"}, 0.05, 0, 1.5, (T.index(3.5), H.index(600), S.index((10, 30)), 0, 0)),
     "w3": ({"0xc54d3914f91f984d61b63d491f38934c4e706b79"}, 0.03, 0, 1e9, (T.index(2.5), H.index(300), S.index((8, 60)), ST.index(240), 0)),
     "grp": (G, 0.02, 0.5, 1e9, (T.index(3.5), H.index(600), 0, ST.index(240), I.index("early")))}
day = lambda t: dt.datetime.fromtimestamp(t, dt.UTC).strftime("%m-%d")
rows = collections.defaultdict(list)
for name, (addrs, mn, mx, lim, ix) in W.items():
    for c in DATA.L:
        if c not in DATA.TR or not any(x[3] in addrs and x[2] for x in DATA.TR[c]): continue
        tr = DATA.path(c); k = next((j for j, e in enumerate(tr) if e["user"] in addrs and e["buy"]), None)
        if k is None or tr[k]["q"] / 1e9 < mn or tr[k]["t"] > DATA.t_end - 600 or tr[k]["t"] < DATA.t_end - 15 * 86400: continue
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        if (mx and before >= mx) or tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue
        prems, vals = R.copy_one(tr, k)
        V = np.mean([vals[l] if prems[l] <= lim else np.full(vals[l].shape, -0.0004) for l in range(len(vals))], axis=0) / R.RATE
        x = V[tuple(ix)]; j = list(ix); j[0] = T.index(1e9); tp_hit = abs(x - V[tuple(j)]) > 1e-12
        rows[day(tr[k]["t"])].append((name, x, tp_hit))
print(f"data to {dt.datetime.fromtimestamp(DATA.t_end, dt.UTC):%m-%d %H:%M} UTC (the last day is partial); the four together (w1 w2 w3 and the group), our 0.02 ETH a copy")
print(f"{'day':6s} {'copies':>6s} {'won':>4s} {'tp hit':>6s} {'net ETH':>9s} {'a copy':>7s} {'best copy':>10s} {'net w/o best':>12s}   by wallet (copies, net ETH)")
for d in sorted(rows):
    r = rows[d]; x = np.array([v for _, v, _ in r]); best = x.max()
    byw = collections.defaultdict(lambda: [0, 0.0])
    for n_, v, _ in r: byw[n_][0] += 1; byw[n_][1] += v
    print(f"{d:6s} {len(r):6d} {int((x > 0).sum()):4d} {sum(1 for *_, h in r if h):6d} {x.sum():+9.4f} {100 * x.mean() / R.STAKE:+6.1f}% {best:+10.4f} {x.sum() - best:+12.4f}   "
          + "  ".join(f"{n_} {c_} {v_:+.3f}" for n_, (c_, v_) in sorted(byw.items())))
