# Nov 19, every copy the model makes (the settings that ran today) against what the bot did, by coin.
#   python3 -I rhd14b_today.py DIR GROUPS_JSON > out/rhd14b_today.txt
import sys, os, json, numpy as np, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
T, H, S, ST, I = R.TP, R.HOLD, R.SPS, R.STALL, R.ITS
D, GJ = sys.argv[1], sys.argv[2]; DATA = R.Data(D); ME = "0x35bb5c55a531d14213380fd978a501f0e239a77e"
G = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
W = {"w1": ({"0x9a3955a122ab8a649a8511df2dce169471fd0ec1"}, 0.1, 0.5, 1.5, (T.index(4), H.index(600), 0, 0, 0)),
     "w2": ({"0x5bc235acecff3dde394f4bfc696f7c35efd502f0"}, 0.05, 0, 1.5, (T.index(3.5), H.index(600), S.index((10, 30)), 0, 0)),
     "w3": ({"0xc54d3914f91f984d61b63d491f38934c4e706b79"}, 0.03, 0, 1e9, (T.index(2.5), H.index(300), S.index((8, 60)), ST.index(240), 0)),
     "grp": (G, 0.02, 0.5, 1e9, (T.index(3.5), H.index(600), 0, ST.index(240), I.index("early")))}
day0 = (DATA.t_end // 86400) * 86400; out = []
for name, (addrs, mn, mx, lim, ix) in W.items():
    for c in DATA.L:
        if c not in DATA.TR or not any(x[3] in addrs and x[2] for x in DATA.TR[c]): continue
        tr = DATA.path(c); k = next((j for j, e in enumerate(tr) if e["user"] in addrs and e["buy"]), None)
        if k is None or tr[k]["t"] < day0 or tr[k]["q"] / 1e9 < mn or tr[k]["t"] > DATA.t_end - 600: continue
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        skip = "coin type" if (mx and before >= mx) else ("graduation" if tr[k]["vq"] / 1e9 - R.V0 >= 3.8 else "")
        prems, vals = R.copy_one(tr, k)
        m = np.mean([vals[l][tuple(ix)] if prems[l] <= lim else -0.0004 for l in range(len(vals))]) / R.RATE
        ours_b = next((e for e in tr if e["user"] == ME and e["buy"]), None); ours_s = next((e for e in tr if e["user"] == ME and not e["buy"]), None)
        live = (ours_s["q"] / 1e9 - 0.02) if (ours_b and ours_s) else None
        out.append((tr[k]["t"], name, c[:10], skip, m, live, "bought" if ours_b else "not bought"))
out.sort()
print(f"{'UTC':8s} {'who':4s} {'coin':10s} {'model':>8s} {'live':>8s}  note")
for t, n, c, skip, m, live, b in out:
    print(f"{dt.datetime.fromtimestamp(t, dt.UTC):%H:%M:%S} {n:4s} {c} {100 * m / 0.02:+7.1f}% {('%+7.1f%%' % (100 * live / 0.02)) if live is not None else '      -'}  {skip or b}")
tk = [o for o in out if not o[3]]
both = [o for o in tk if o[5] is not None]; miss = [o for o in tk if o[6] == "not bought"]
print(f"\nmodel copies today (after its filters): {len(tk)}, model {sum(o[4] for o in tk):+.4f} ETH; bought by the bot and closed: {len(both)}, model {sum(o[4] for o in both):+.4f} live {sum(o[5] for o in both):+.4f}; "
      f"not bought: {len(miss)}, model {sum(o[4] for o in miss):+.4f}")
