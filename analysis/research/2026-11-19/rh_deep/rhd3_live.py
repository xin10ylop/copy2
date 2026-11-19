# The three live wallets (config/rh-copier.example.toml) under their exact live settings, scored two ways (Nov 19):
#   OLD: the first pass's rule (coins whose trading stopped within 600 s of its buy left out)
#   NEW: every coin (a coin that went quiet is sold at its last state, as the live bot would); only buys in the data's
#        last 600 s are left out
# both on the exact curve (rhd_lib), our 0.02 ETH landing 2, 3 and 5 blocks after its buy. By period, by day for the last
# 7 days, and the coins that went quiet.
#   python3 -I rhd3_live.py DIR > out/rhd3_live.txt
import sys, os, collections, numpy as np, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
D = sys.argv[1]; DATA = R.Data(D)
LIVE = [("wallet 1", "0x9a3955a122ab8a649a8511df2dce169471fd0ec1", 0.1, 0.5, 1.5, (R.TP.index(4), R.HOLD.index(600), 0, 0, 0)),
        ("wallet 2", "0x5bc235acecff3dde394f4bfc696f7c35efd502f0", 0.05, 0, 1.5, (R.TP.index(3.5), R.HOLD.index(600), R.SPS.index((10, 30)), 0, 0)),
        ("wallet 3", "0xc54d3914f91f984d61b63d491f38934c4e706b79", 0.03, 0, 1e9, (R.TP.index(2.5), R.HOLD.index(300), R.SPS.index((8, 60)), R.STALL.index(240), 0))]
P1, P2 = DATA.t_start + (DATA.t_end - DATA.t_start) / 3, DATA.t_start + 2 * (DATA.t_end - DATA.t_start) / 3
print(f"data {dt.datetime.fromtimestamp(DATA.t_start, dt.UTC):%m-%d %H:%M} to {dt.datetime.fromtimestamp(DATA.t_end, dt.UTC):%m-%d %H:%M} UTC; "
      f"periods to {dt.datetime.fromtimestamp(P1, dt.UTC):%m-%d %H:%M} / {dt.datetime.fromtimestamp(P2, dt.UTC):%m-%d %H:%M} / the end")
mine = collections.defaultdict(list)
for c in DATA.L:
    if c not in DATA.TR: continue
    users = {x[3] for x in DATA.TR[c] if x[2]}
    for name, w, *_ in LIVE:
        if w in users: mine[w].append(c)
for name, w, mn, mx, lim, ix in LIVE:
    rows = []
    for c in mine[w]:
        tr = DATA.path(c); k = next((j for j, e in enumerate(tr) if e["user"] == w and e["buy"]), None)
        if k is None or tr[k]["q"] / 1e9 < mn or tr[k]["t"] > DATA.t_end - 600: continue
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        if mx and before >= mx: continue
        if tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue                       # the bot's graduation guard
        prems, vals = R.copy_one(tr, k)
        x = np.mean([vals[l][ix] if prems[l] <= lim else -0.0004 for l in range(len(vals))]) / R.RATE
        rows.append(dict(t=tr[k]["t"], x=x, quiet=tr[-1]["t"] - tr[k]["t"] < 600))
    rows.sort(key=lambda r: r["t"]); X = np.array([r["x"] for r in rows]); T = np.array([r["t"] for r in rows]); Qt = np.array([r["quiet"] for r in rows])
    def line(m, lab):
        x = X[m]; k = max(1, round(0.02 * len(x)))
        if not len(x): return f"   {lab:34s} none"
        bs = np.random.default_rng(7).choice(x, size=(5000, len(x))).mean(1)
        return (f"   {lab:34s} {len(x):4d} copies {x.sum():+.4f} ETH ({100 * x.mean() / R.STAKE:+6.1f}% a copy), w/o 2% {np.sort(x)[:-k].sum() if len(x) > k else 0:+.4f}, "
                f"won {100 * np.mean(x > 0):3.0f}%, P(mean>0) {100 * np.mean(bs > 0):5.1f}%")
    print(f"\n{name} {w}: its buys {mn}+ ETH{f', coins under {mx} ETH in the curve' if mx else ''}, limit {'none' if lim > 1e8 else lim}")
    print(line(~Qt, "OLD (quiet coins left out)"))
    print(line(np.ones(len(X), bool), "NEW (every coin)"))
    print(line(Qt, "   the quiet coins alone"))
    for p, (a, b) in enumerate(((0, P1), (P1, P2), (P2, 1e12))): print(line((T >= a) & (T < b), f"NEW, P{p + 1}"))
    print(line(T >= DATA.t_end - 3 * 86400, "NEW, the last 3 days"))
    for d in range(7, 0, -1):
        a = DATA.t_end - d * 86400; m = (T >= a) & (T < a + 86400)
        if m.any(): print(f"      day to {dt.datetime.fromtimestamp(a + 86400, dt.UTC):%m-%d %H:%M}: {m.sum():3d} copies {X[m].sum():+.4f} ETH ({100 * X[m].mean() / R.STAKE:+6.1f}%)")
