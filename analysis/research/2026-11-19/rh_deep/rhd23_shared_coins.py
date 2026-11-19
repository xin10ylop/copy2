# Coins two copied wallets buy (Nov 19; on 0x3a227ce5 and 0x6869cba8 wallets 2 and 3 bought together, the bot sold on
# wallet 3's rules and wallet 2's would have made +77.5% and +54.7% in the model). For every coin bought by 2+ of the
# four, the copy under each buyer's settings now (wallet 1 tp 4 600 s; wallet 2 tp 3.5 900 s sp 10/30; wallet 3 sold at
# 45 s; the group tp 3.5 900 s stall 240 early), and three rules: the first buyer's (the bot now), the longest hold's,
# wallet 3's always. Exact model, landing 2/3/5 blocks from the FIRST buyer's buy.
#   python3 -I rhd23_shared_coins.py DIR GROUPS_JSON > out/rhd23_shared_coins.txt
import sys, os, json, collections, numpy as np
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
T, H, S, ST, I = R.TP, R.HOLD, R.SPS, R.STALL, R.ITS
H[:] = [45, 600, 900]
D, GJ = sys.argv[1], sys.argv[2]; DATA = R.Data(D)
G = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
W = {"w1": ({"0x9a3955a122ab8a649a8511df2dce169471fd0ec1"}, 0.1, 0.5, 1.5, (T.index(4), H.index(600), 0, 0, 0), 600),
     "w2": ({"0x5bc235acecff3dde394f4bfc696f7c35efd502f0"}, 0.05, 0, 1.5, (T.index(3.5), H.index(900), S.index((10, 30)), 0, 0), 900),
     "w3": ({"0xc54d3914f91f984d61b63d491f38934c4e706b79"}, 0.03, 0, 3.0, (T.index(1e9), H.index(45), 0, 0, 0), 45),
     "grp": (G, 0.02, 0.5, 3.0, (T.index(3.5), H.index(900), 0, ST.index(240), I.index("early")), 899)}
rows = []
for c in DATA.L:
    if c not in DATA.TR: continue
    tr = DATA.path(c); who = {}
    for name, (addrs, mn, mx, lim, ix, hold) in W.items():
        k = next((j for j, e in enumerate(tr) if e["user"] in addrs and e["buy"]), None)
        if k is None or tr[k]["q"] / 1e9 < mn or tr[k]["t"] > DATA.t_end - 900: continue
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        if (mx and before >= mx) or tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue
        who[name] = k
    if len(who) < 2: continue
    k0 = min(who.values()); first = min(who, key=lambda n: (who[n], -W[n][5]))
    if tr[who[first]]["slot"] + 5 < max(tr[k]["slot"] for k in who.values()): continue   # only buys within 5 blocks of each other: one copy
    prems, vals = R.copy_one(tr, k0)
    v = {n: np.mean([vals[l][W[n][4]] if prems[l] <= W[n][3] else -0.0004 for l in range(len(vals))]) / R.RATE for n in who}
    rows.append((tr[k0]["t"], c[:10], who, first, v))
rows.sort(key=lambda r: r[0]); t = np.array([r[0] for r in rows]); A = t < np.median(t)
rules = {"first buyer (the bot now)": lambda r: r[4][r[3]], "longest hold": lambda r: r[4][max(r[2], key=lambda n: W[n][5])],
         "shortest hold": lambda r: r[4][min(r[2], key=lambda n: W[n][5])], "the best (hindsight)": lambda r: max(r[4].values())}
print(f"{len(rows)} coins bought by 2+ of the four within 5 blocks (data to the end): pairs {collections.Counter('+'.join(sorted(r[2])) for r in rows).most_common()}")
for lab, f in rules.items():
    x = np.array([f(r) for r in rows]); print(f"   {lab:26s} {100 * x.mean() / R.STAKE:+6.1f}% a copy | {x.sum():+.3f} ETH | halves {x[A].sum():+.3f} / {x[~A].sum():+.3f}")
