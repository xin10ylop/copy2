# Sell before the leader does (Nov 19; the owner: wallet 2 "typically sells after 33 seconds, what if we always sell
# before? after x seconds of buying"). Each wallet's live setting with the time limit cut to 3-120 s after ITS buy (our
# buy lands 2-5 blocks, 0.2-0.5 s, after it), and the same as a pure time sale (no other exit). Exact model, every coin;
# halves, without the best 2%, last 7 days. The model sells at the first trade at or after the time: in seconds-long
# holds the live sale (sent on the clock, landing ~0.3 s later) can differ more than in long ones.
#   python3 -I rhd19_short_hold.py DIR GROUPS_JSON > out/rhd19_short_hold.txt
import sys, os, json, numpy as np
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
T, H, S, ST, I = R.TP, R.HOLD, R.SPS, R.STALL, R.ITS
H[:] = [3, 5, 8, 10, 15, 20, 25, 30, 45, 60, 90, 120, 300, 600, 900]
D, GJ = sys.argv[1], sys.argv[2]; DATA = R.Data(D)
G = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
W = {"wallet 1 (live 600 s)": ({"0x9a3955a122ab8a649a8511df2dce169471fd0ec1"}, 0.1, 0.5, 1.5, (T.index(4), H.index(600), 0, 0, 0)),
     "wallet 2 (live 900 s)": ({"0x5bc235acecff3dde394f4bfc696f7c35efd502f0"}, 0.05, 0, 1.5, (T.index(3.5), H.index(900), S.index((10, 30)), 0, 0)),
     "wallet 3 (live 300 s)": ({"0xc54d3914f91f984d61b63d491f38934c4e706b79"}, 0.03, 0, 3.0, (T.index(3), H.index(300), S.index((8, 60)), ST.index(240), 0)),
     "group 4-8 (live 900 s)": (G, 0.02, 0.5, 3.0, (T.index(3.5), H.index(900), 0, ST.index(240), I.index("early")))}
for name, (addrs, mn, mx, lim, ix) in W.items():
    rows = []
    for c in DATA.L:
        if c not in DATA.TR or not any(x[3] in addrs and x[2] for x in DATA.TR[c]): continue
        tr = DATA.path(c); k = next((j for j, e in enumerate(tr) if e["user"] in addrs and e["buy"]), None)
        if k is None or tr[k]["q"] / 1e9 < mn or tr[k]["t"] > DATA.t_end - 900: continue
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        if (mx and before >= mx) or tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue
        prems, vals = R.copy_one(tr, k)
        rows.append((tr[k]["t"], np.mean([vals[l] if prems[l] <= lim else np.full(vals[l].shape, -0.0004) for l in range(len(vals))], axis=0) / R.RATE))
    rows.sort(key=lambda r: r[0]); t = np.array([r[0] for r in rows]); X = np.array([r[1] for r in rows]); A = t < np.median(t); L7 = t >= DATA.t_end - 7 * 86400
    k2 = max(1, round(0.02 * len(rows)))
    print(f"\n=== {name}: {len(rows)} copies   (a copy | ETH all | half 1 / half 2 | w/o best 2% | last 7 d)")
    for lab, fn in (("live exits, time cut to", lambda j: X[(slice(None),) + tuple([ix[0], j] + list(ix[2:]))]),
                    ("time only (no other exit), sold at", lambda j: X[:, T.index(1e9), j, 0, 0, 0])):
        print(f"   {lab}:")
        for j, h in enumerate(H):
            x = fn(j); print(f"      {h:4d} s  {100 * x.mean() / R.STAKE:+6.1f}% | {x.sum():+.3f} | {x[A].sum():+.3f} / {x[~A].sum():+.3f} | {np.sort(x)[:-k2].sum():+.3f} | {100 * x[L7].mean() / R.STAKE:+6.1f}%"
                         + ("   <- live" if (lab.startswith("live") and j == ix[1]) else ""))
