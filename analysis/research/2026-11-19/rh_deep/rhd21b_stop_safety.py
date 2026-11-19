# Is a stop loss SAFER (Nov 19; the owner: "-30% ... i think its safer no? or -20% even")? rhd21's simulation, all four
# wallets together, per UTC day: the worst day, losing days, the spread of days, the deepest fall of the running total,
# the worst single copy and the share of copies that lose more than 30%, without a stop and with -20/-30/-40%.
#   python3 -I rhd21b_stop_safety.py DIR GROUPS_JSON > out/rhd21b_stop_safety.txt
import sys, os, json, numpy as np
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
D, GJ = sys.argv[1], sys.argv[2]; DATA = R.Data(D)
G = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
W = {"wallet 1 (tp 4, 600 s)": ({"0x9a3955a122ab8a649a8511df2dce169471fd0ec1"}, 0.1, 0.5, 1.5, (4.0, 600, None, 0, False)),
     "wallet 2 (tp 3.5, 900 s, sp 10/30)": ({"0x5bc235acecff3dde394f4bfc696f7c35efd502f0"}, 0.05, 0, 1.5, (3.5, 900, (10, 30), 0, False)),
     "wallet 3 (sold at 45 s)": ({"0xc54d3914f91f984d61b63d491f38934c4e706b79"}, 0.03, 0, 3.0, (1e9, 45, None, 0, False)),
     "group 4-8 (tp 3.5, 900 s, stall 240, early)": (G, 0.02, 0.5, 3.0, (3.5, 900, None, 240, True))}
SL = [0.20, 0.30, 0.40]; GRACE = [0]
import collections, datetime as dt; ALL = []
def first(m): i = np.flatnonzero(m); return int(i[0]) if len(i) else None
def sim(p, tp, hold, sp, stall, early):
    """the value (stake units) of selling at each trade, and the live exit's index"""
    vt0, vq0, bps0 = p["ent"]; Q = 0.5e9 * p["hopf"] / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    px, age = p["px"], p["age"]; n = len(px); vq, vt, b = p["vq"], p["vt"], p["bps"]; vq_r = vq + net_in; vt_r = vt * vq / vq_r
    val = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - b / 1e4) * p["rate"] * p["hopf"] / 1e9 - 0.5 - 0.0026
    BIG = 10 ** 9; trig = lambda i: BIG if i is None else min(i + 1, n - 1); at = lambda i: BIG if i is None else i
    E = [at(first(p["grad"])), trig(first(px >= tp)), at(first(age >= hold))]
    if sp:
        s = np.concatenate([[0], np.cumsum(p["osell"])]); bb = np.concatenate([[0], np.cumsum(p["obuy"])]); lo = np.searchsorted(age, age - sp[1], side="left")
        E.append(trig(first(((s[1:] - s[lo]) - (bb[1:] - bb[lo]) >= sp[0]) & (age >= 30))))
    if stall:
        pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
        E.append(trig(first((pk >= 1.0) & (age - lasthi >= stall))))
    if early: E.append(trig(first(p["sell"] & (age >= 30) & (age < 290) & (px < 1.5))))
    return val, min(E), age, n, trig
for name, (addrs, mn, mx, lim, (tp, hold, sp, stall, early)) in W.items():
    rows = []; keys = [(s, g) for s in SL for g in GRACE]
    for c in DATA.L:
        if c not in DATA.TR or not any(x[3] in addrs and x[2] for x in DATA.TR[c]): continue
        tr = DATA.path(c); k = next((j for j, e in enumerate(tr) if e["user"] in addrs and e["buy"]), None)
        if k is None or tr[k]["q"] / 1e9 < mn or tr[k]["t"] > DATA.t_end - 3600: continue
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        if (mx and before >= mx) or tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue
        out = {"live": []}; out.update({key: [] for key in keys}); ok = True
        for j in R.landings(tr, k):
            if j is None: ok = False; break
            p = R.H.prep(tr, k, R.RATE, j - k, pmax=1000); p["rate"] = R.RATE
            if (tr[k]["vt"] / p["ent"][0]) ** 2 > lim:
                for key in out: out[key].append(-0.0004)
                continue
            if not len(p["px"]): ok = False; break
            val, e, age, n, trig = sim(p, tp, hold, sp, stall, early); e = min(e, n - 1)
            out["live"].append(val[e] - R.COST)
            for s, g in keys:
                i = trig(first((val <= -0.5 * s) & (age >= g)))   # val is in stake units of 0.5: -0.5*s = s of the stake lost
                out[(s, g)].append(val[min(e, i, n - 1)] - R.COST)
        if not ok: continue
        rows.append((tr[k]["t"], {key: np.mean(v) / R.RATE for key, v in out.items()}))
    ALL.extend((t_, name, v) for t_, v in rows)

day = lambda t: dt.datetime.fromtimestamp(t, dt.UTC).strftime("%m-%d")
keys = ["live"] + [(s, 0) for s in SL]; lab = {"live": "no stop", **{(s, 0): f"stop -{100 * s:.0f}%" for s in SL}}
print(f"all four together, {len(ALL)} copies, Oct 9 - Nov 19 (our 0.02 ETH a copy)")
print(f"{'':10s} {'total ETH':>9s} {'a copy':>7s} {'losing days':>11s} {'worst day':>9s} {'sd of days':>10s} {'deepest fall':>12s} {'worst copy':>10s} {'copies < -30%':>13s} {'avg loser':>9s}")
for k in keys:
    d = collections.defaultdict(float); x = np.array([v[k] for _, _, v in ALL])
    for (t_, _, v) in ALL: d[day(t_)] += v[k]
    dd = np.array([d[z] for z in sorted(d)]); cum = np.cumsum(dd); fall = np.max(np.maximum.accumulate(cum) - cum)
    print(f"{lab[k]:10s} {x.sum():+9.3f} {100 * x.mean() / R.STAKE:+6.1f}% {int((dd < 0).sum()):5d} of {len(dd):2d} {dd.min():+9.4f} {dd.std():10.4f} {fall:12.4f} "
          f"{100 * x.min() / R.STAKE:+9.1f}% {100 * (x < -0.3 * R.STAKE).mean():12.1f}% {100 * x[x < 0].mean() / R.STAKE:+8.1f}%")
