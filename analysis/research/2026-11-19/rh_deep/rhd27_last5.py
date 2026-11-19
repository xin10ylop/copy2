# Per UTC day, the last DAYS days, wallets 1, 3 and the group (Nov 19 evening; the owner: "for wallet 1, 3 and the
# group, the pnl per day for the last 5 days of each"), with the settings now: wallet 1 tp 4 600 s (max 0.5 ETH in the
# curve, limit 1.5x); wallet 3 sold 45 s after its buy (limit 3x); the group tp 3.5 900 s stall 240 its early sale (max
# 0.5 ETH in the curve, limit 3x). Exact model, landing 2/3/5 blocks, every coin, STAKE ETH a copy (0.01 now).
#   STAKE=0.01 python3 -I rhd27_last5.py DIR GROUPS_JSON [DAYS=5] > out/rhd27_last5.txt
import sys, os, json, collections, numpy as np, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
T, H, S, ST, I = R.TP, R.HOLD, R.SPS, R.STALL, R.ITS
H[:] = [45, 600, 900]
D, GJ = sys.argv[1], sys.argv[2]; ND = int(sys.argv[3]) if len(sys.argv) > 3 else 5; DATA = R.Data(D)
G = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
W = {"wallet 1": ({"0x9a3955a122ab8a649a8511df2dce169471fd0ec1"}, 0.1, 0.5, 1.5, (T.index(4), H.index(600), 0, 0, 0)),
     "wallet 3": ({"0xc54d3914f91f984d61b63d491f38934c4e706b79"}, 0.03, 0, 3.0, (T.index(1e9), H.index(45), 0, 0, 0)),
     "group 4-8": (G, 0.02, 0.5, 3.0, (T.index(3.5), H.index(900), 0, ST.index(240), I.index("early")))}
day = lambda t: dt.datetime.fromtimestamp(t, dt.UTC).strftime("%m-%d")
d_end = (DATA.t_end // 86400) * 86400; d0 = d_end - (ND - 1) * 86400; days = [day(d0 + i * 86400) for i in range(ND)]
res = collections.defaultdict(lambda: collections.defaultdict(list)); seen = {}
for name, (addrs, mn, mx, lim, ix) in W.items():
    for c in DATA.L:
        if c not in DATA.TR or not any(x[3] in addrs and x[2] for x in DATA.TR[c]): continue
        tr = DATA.path(c); k = next((j for j, e in enumerate(tr) if e["user"] in addrs and e["buy"]), None)
        if k is None or tr[k]["t"] < d0 or tr[k]["q"] / 1e9 < mn: continue
        hold = 900 if name == "group 4-8" else (600 if name == "wallet 1" else 45)
        if tr[k]["t"] > DATA.t_end - hold - 60: continue          # not finished yet
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        if (mx and before >= mx) or tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue
        prems, vals = R.copy_one(tr, k)
        v = np.mean([vals[l][tuple(ix)] if prems[l] <= lim else -0.0004 for l in range(len(vals))]) / R.RATE
        res[name][day(tr[k]["t"])].append(v)
print(f"data to {dt.datetime.fromtimestamp(DATA.t_end, dt.UTC):%m-%d %H:%M} UTC (today is partial); {R.STAKE} ETH a copy; the backtest (exact model, landing {R.LANDB} blocks)")
print(f"{'':10s} " + "  ".join(f"{d:>17s}" for d in days) + f"  {'5 days':>17s}")
tot = collections.defaultdict(list)
for name in W:
    cells = []
    for d in days:
        x = res[name].get(d, []); tot[d] += x
        cells.append(f"{sum(x):+.4f} ({len(x):2d}, {sum(1 for y in x if y > 0):2d}w)" if x else f"{'-':>17s}")
    allx = [y for d in days for y in res[name].get(d, [])]
    print(f"{name:10s} " + "  ".join(f"{c:>17s}" for c in cells) + f"  {sum(allx):+.4f} ({len(allx):2d}, {100 * np.mean(allx) / R.STAKE if allx else 0:+.0f}%)")
print(f"{'all three':10s} " + "  ".join(f"{sum(tot[d]):+.4f} ({len(tot[d]):2d}, {sum(1 for y in tot[d] if y > 0):2d}w)" for d in days)
      + f"  {sum(sum(tot[d]) for d in days):+.4f}")
print("cells: net ETH (copies, won)")
