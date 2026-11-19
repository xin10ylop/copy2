# Which wallet is the steadiest (Nov 19; the owner: "check over all days, which wallet is the most stable, losing days for
# all"). The settings live since Nov 19 afternoon (config/rh-copier.example.toml), exact model, landing 2/3/5 blocks,
# every coin; per wallet and UTC day: copies, net ETH. Positive and losing days, the worst day, the longest losing run,
# the deepest fall from a peak of the running total, and the same for all four together.
#   python3 -I rhd17_daily_all.py DIR GROUPS_JSON > out/rhd17_daily_all.txt
import sys, os, json, collections, numpy as np, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
T, H, S, ST, I = R.TP, R.HOLD, R.SPS, R.STALL, R.ITS
H[:] = [60, 120, 180, 300, 450, 600, 900]
D, GJ = sys.argv[1], sys.argv[2]; DATA = R.Data(D)
G = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
W = {"wallet 1": ({"0x9a3955a122ab8a649a8511df2dce169471fd0ec1"}, 0.1, 0.5, 1.5, (T.index(4), H.index(600), 0, 0, 0)),
     "wallet 2": ({"0x5bc235acecff3dde394f4bfc696f7c35efd502f0"}, 0.05, 0, 1.5, (T.index(3.5), H.index(900), S.index((10, 30)), 0, 0)),
     "wallet 3": ({"0xc54d3914f91f984d61b63d491f38934c4e706b79"}, 0.03, 0, 3.0, (T.index(3), H.index(300), S.index((8, 60)), ST.index(240), 0)),
     "group 4-8": (G, 0.02, 0.5, 3.0, (T.index(3.5), H.index(900), 0, ST.index(240), I.index("early")))}
day = lambda t: dt.datetime.fromtimestamp(t, dt.UTC).strftime("%m-%d")
per = {n: collections.defaultdict(list) for n in W}
for name, (addrs, mn, mx, lim, ix) in W.items():
    for c in DATA.L:
        if c not in DATA.TR or not any(x[3] in addrs and x[2] for x in DATA.TR[c]): continue
        tr = DATA.path(c); k = next((j for j, e in enumerate(tr) if e["user"] in addrs and e["buy"]), None)
        if k is None or tr[k]["q"] / 1e9 < mn or tr[k]["t"] > DATA.t_end - 600: continue
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        if (mx and before >= mx) or tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue
        prems, vals = R.copy_one(tr, k)
        per[name][day(tr[k]["t"])].append(np.mean([vals[l][tuple(ix)] if prems[l] <= lim else -0.0004 for l in range(len(vals))]) / R.RATE)
days = sorted({d for n in per for d in per[n]})
print(f"data {days[0]} to {days[-1]} UTC ({len(days)} days; the last is partial, to {dt.datetime.fromtimestamp(DATA.t_end, dt.UTC):%H:%M}); our 0.02 ETH a copy; live settings")
def summary(name, daily):
    act = [(d, v, n) for d, v, n in daily if n > 0]; vals = np.array([v for _, v, _ in act]); cum = np.cumsum(vals); dd = (np.maximum.accumulate(np.concatenate([[0], cum]))[1:] - cum).max()
    run = best = 0
    for v in vals: run = run + 1 if v < 0 else 0; best = max(best, run)
    worst = min(act, key=lambda x: x[1]); lose = [f"{d} {v:+.3f} ({n})" for d, v, n in act if v < 0]
    print(f"\n=== {name}: active {len(act)} of {len(days)} days, {sum(n for *_, n in act)} copies, total {vals.sum():+.3f} ETH")
    print(f"   positive days {int((vals > 0).sum())}, losing days {int((vals < 0).sum())} ({100 * np.mean(vals < 0):.0f}%); a day: mean {vals.mean():+.4f}, median {np.median(vals):+.4f}, spread (sd) {vals.std():.4f}")
    print(f"   worst day {worst[0]} {worst[1]:+.4f} ({worst[2]} copies); longest losing run {best} days; deepest fall from a peak of the total {dd:.4f} ETH")
    print(f"   losing days: {', '.join(lose) if lose else 'none'}")
for name in W: summary(name, [(d, sum(per[name][d]), len(per[name][d])) for d in days])
summary("ALL FOUR TOGETHER", [(d, sum(sum(per[n][d]) for n in W), sum(len(per[n][d]) for n in W)) for d in days])
print("\nday by day (net ETH, copies):")
print(f"   {'day':6s}" + "".join(f"{n:>17s}" for n in W) + f"{'all':>17s}")
for d in days:
    print(f"   {d:6s}" + "".join((f"{sum(per[n][d]):+9.4f} ({len(per[n][d]):3d})" if per[n][d] else f"{'-':>17s}") for n in W) + f"{sum(sum(per[n][d]) for n in W):+9.4f} ({sum(len(per[n][d]) for n in W):3d})")
