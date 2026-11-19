# "Are these the best take profits, not lower?" (Nov 19). Each live setting with only the take profit changed (1.5x to
# none), exact model, landing 2/3/5 blocks, every coin: all copies, each half, the last 7 days, and the result without
# the best 2% of copies (a take profit that only pays on rare spikes shows here).
#   python3 -I rhd11_tp.py DIR GROUPS_JSON > out/rhd11_tp.txt
import sys, os, json, numpy as np
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
D, GJ = sys.argv[1], sys.argv[2]; DATA = R.Data(D)
T, H, S, ST, I = R.TP, R.HOLD, R.SPS, R.STALL, R.ITS
G = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
W = {"wallet 1 (live tp 4)": ({"0x9a3955a122ab8a649a8511df2dce169471fd0ec1"}, 0.1, 0.5, 1.5, (T.index(4), H.index(600), 0, 0, 0)),
     "wallet 2 (live tp 3.5)": ({"0x5bc235acecff3dde394f4bfc696f7c35efd502f0"}, 0.05, 0, 1.5, (T.index(3.5), H.index(600), S.index((10, 30)), 0, 0)),
     "wallet 3 (live tp 2.5)": ({"0xc54d3914f91f984d61b63d491f38934c4e706b79"}, 0.03, 0, 1e9, (T.index(2.5), H.index(300), S.index((8, 60)), ST.index(240), 0)),
     "group 4-8 (live tp 3.5)": (G, 0.02, 0.5, 1e9, (T.index(3.5), H.index(600), 0, ST.index(240), I.index("early")))}
for name, (addrs, mn, mx, lim, ix) in W.items():
    rows = []
    for c in DATA.L:
        if c not in DATA.TR or not any(x[3] in addrs and x[2] for x in DATA.TR[c]): continue
        tr = DATA.path(c); k = next((j for j, e in enumerate(tr) if e["user"] in addrs and e["buy"]), None)
        if k is None or tr[k]["q"] / 1e9 < mn or tr[k]["t"] > DATA.t_end - 600: continue
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        if (mx and before >= mx) or tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue
        prems, vals = R.copy_one(tr, k)
        V = np.mean([vals[l] if prems[l] <= lim else np.full(vals[l].shape, -0.0004) for l in range(len(vals))], axis=0) / R.RATE
        rows.append((tr[k]["t"], V[(slice(None),) + tuple(ix[1:])]))
    rows.sort(key=lambda r: r[0]); t = np.array([r[0] for r in rows]); X = np.array([r[1] for r in rows]); A = t < np.median(t); L7 = t >= DATA.t_end - 7 * 86400
    print(f"\n=== {name}: {len(rows)} copies   (a copy | ETH all | half 1 / half 2 ETH | without the best 2% | last 7 days a copy ({L7.sum()}) | hit the tp)")
    for j, tp in enumerate(T):
        x = X[:, j]; k = max(1, round(0.02 * len(x))); hit = np.mean(np.abs(X[:, j] - X[:, -1]) > 1e-12) if tp < 1e8 else 0
        print(f"   tp {'none' if tp > 1e8 else str(tp) + 'x':5s} {100 * x.mean() / R.STAKE:+6.1f}% | {x.sum():+.3f} | {x[A].sum():+.3f} / {x[~A].sum():+.3f} | {np.sort(x)[:-k].sum():+.3f} | {100 * x[L7].mean() / R.STAKE:+6.1f}% | {100 * hit:4.1f}%"
              + ("   <- live" if j == ix[0] else ""))
