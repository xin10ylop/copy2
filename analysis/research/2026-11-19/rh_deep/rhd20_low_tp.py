# A low take profit: small wins on more copies (Nov 19; the owner: "what if we set tp at 1.3x, making small profits but
# on more trades"). The take profit is a multiple of the LEADER's buy price (the bot's ratio = price / its price), and our
# buy lands above it (1.1-1.2x) and pays the early tax, so a low one can lock in little or nothing. Each wallet's live
# setting now (wallet 1 tp 4 600 s; wallet 2 tp 3.5 900 s sp 10/30; wallet 3 sold at 45 s; the group tp 3.5 900 s stall
# 240 early sale) with only the take profit changed, 1.1x to none: a copy, halves, without the best 2%, the last 7 days,
# how often it hits, and what a hit pays us. Exact model, every coin; LANDB sets the landings (2/3/5 blocks by default).
#   python3 -I rhd20_low_tp.py DIR GROUPS_JSON > out/rhd20_low_tp.txt
import sys, os, json, numpy as np
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
T, H, S, ST, I = R.TP, R.HOLD, R.SPS, R.STALL, R.ITS
T[:] = [1.1, 1.2, 1.3, 1.4, 1.5, 1.75, 2, 2.5, 3, 3.5, 4, 1e9]; H[:] = [45, 600, 900]
D, GJ = sys.argv[1], sys.argv[2]; DATA = R.Data(D)
G = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
W = {"wallet 1 (live tp 4, 600 s)": ({"0x9a3955a122ab8a649a8511df2dce169471fd0ec1"}, 0.1, 0.5, 1.5, 4, (H.index(600), 0, 0, 0)),
     "wallet 2 (live tp 3.5, 900 s)": ({"0x5bc235acecff3dde394f4bfc696f7c35efd502f0"}, 0.05, 0, 1.5, 3.5, (H.index(900), S.index((10, 30)), 0, 0)),
     "wallet 3 (live: sold at 45 s, no tp)": ({"0xc54d3914f91f984d61b63d491f38934c4e706b79"}, 0.03, 0, 3.0, 1e9, (H.index(45), 0, 0, 0)),
     "group 4-8 (live tp 3.5, 900 s)": (G, 0.02, 0.5, 3.0, 3.5, (H.index(900), 0, ST.index(240), I.index("early")))}
for name, (addrs, mn, mx, lim, live_tp, rest) in W.items():
    rows = []
    for c in DATA.L:
        if c not in DATA.TR or not any(x[3] in addrs and x[2] for x in DATA.TR[c]): continue
        tr = DATA.path(c); k = next((j for j, e in enumerate(tr) if e["user"] in addrs and e["buy"]), None)
        if k is None or tr[k]["q"] / 1e9 < mn or tr[k]["t"] > DATA.t_end - 900: continue
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        if (mx and before >= mx) or tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue
        prems, vals = R.copy_one(tr, k)
        V = np.mean([vals[l] if prems[l] <= lim else np.full(vals[l].shape, -0.0004) for l in range(len(vals))], axis=0) / R.RATE
        rows.append((tr[k]["t"], np.array([V[(i,) + rest] for i in range(len(T))])))
    rows.sort(key=lambda r: r[0]); t = np.array([r[0] for r in rows]); X = np.array([r[1] for r in rows])
    A = t < np.median(t); L7 = t >= DATA.t_end - 7 * 86400; k2 = max(1, round(0.02 * len(rows))); none = X[:, T.index(1e9)]
    print(f"\n=== {name}: {len(rows)} copies   (a copy | ETH all | half 1 / half 2 | w/o best 2% | last 7 d | hit | a hit pays us)")
    for i, tp in enumerate(T):
        x = X[:, i]; hit = np.abs(x - none) > 1e-12; pay = 100 * x[hit].mean() / R.STAKE if hit.any() else float("nan")
        print(f"   tp {'none' if tp > 1e8 else f'{tp:g}x':5s} {100 * x.mean() / R.STAKE:+6.1f}% | {x.sum():+.3f} | {x[A].sum():+.3f} / {x[~A].sum():+.3f} | "
              f"{np.sort(x)[:-k2].sum():+.3f} | {100 * x[L7].mean() / R.STAKE:+6.1f}% | {100 * hit.mean():4.1f}% | {pay:+6.1f}%" + ("   <- live" if tp == live_tp else ""))
