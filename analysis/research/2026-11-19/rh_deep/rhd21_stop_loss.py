# A stop loss (Nov 19; the owner: "what about a stop loss?"). Each wallet's setting now (wallet 1 tp 4 600 s; wallet 2
# tp 3.5 900 s sp 10/30; wallet 3 sold at 45 s; the group tp 3.5 900 s stall 240 early sale) plus a stop: sell when what
# our coin would sell for is X% below what we paid (10% to 60%), checked at every trade, sold at the next trade (as a
# take profit is), from the start or only after a grace time (30 s, 60 s). Exact model (rhd15's path simulation), every
# coin, picked on one half and scored on the other; without the best 2%. LANDB sets the landings (2/3/5 by default).
#   python3 -I rhd21_stop_loss.py DIR GROUPS_JSON > out/rhd21_stop_loss.txt
import sys, os, json, numpy as np
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
D, GJ = sys.argv[1], sys.argv[2]; DATA = R.Data(D)
G = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
W = {"wallet 1 (tp 4, 600 s)": ({"0x9a3955a122ab8a649a8511df2dce169471fd0ec1"}, 0.1, 0.5, 1.5, (4.0, 600, None, 0, False)),
     "wallet 2 (tp 3.5, 900 s, sp 10/30)": ({"0x5bc235acecff3dde394f4bfc696f7c35efd502f0"}, 0.05, 0, 1.5, (3.5, 900, (10, 30), 0, False)),
     "wallet 3 (sold at 45 s)": ({"0xc54d3914f91f984d61b63d491f38934c4e706b79"}, 0.03, 0, 3.0, (1e9, 45, None, 0, False)),
     "group 4-8 (tp 3.5, 900 s, stall 240, early)": (G, 0.02, 0.5, 3.0, (3.5, 900, None, 240, True))}
SL = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60]; GRACE = [0, 30, 60]
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
    rows.sort(key=lambda r: r[0]); t = np.array([r[0] for r in rows]); A = t < np.median(t); L7 = t >= DATA.t_end - 7 * 86400
    X = {key: np.array([r[1][key] for r in rows]) for key in rows[0][1]}; base = X["live"]; k2 = max(1, round(0.02 * len(base)))
    w2 = lambda x: np.sort(x)[:-k2].sum(); pc = lambda x: 100 * x.mean() / R.STAKE
    print(f"\n=== {name}: {len(rows)} copies   (a copy | ETH all | half 1 / half 2 | w/o best 2% | last 7 d)")
    print(f"   no stop (live)          {pc(base):+6.1f}% | {base.sum():+.3f} | {base[A].sum():+.3f} / {base[~A].sum():+.3f} | {w2(base):+.3f} | {pc(base[L7]):+6.1f}%")
    for s, g in keys:
        x = X[(s, g)]; flag = "  better on both halves" if x[A].sum() > base[A].sum() and x[~A].sum() > base[~A].sum() and w2(x) > w2(base) else ""
        print(f"   stop -{100 * s:2.0f}%{'' if g == 0 else f' after {g} s':10s}  {pc(x):+6.1f}% | {x.sum():+.3f} | {x[A].sum():+.3f} / {x[~A].sum():+.3f} | {w2(x):+.3f} | {pc(x[L7]):+6.1f}%{flag}")
    for P, Q, lab in ((A, ~A, "half 1 -> half 2"), (~A, A, "half 2 -> half 1")):
        bk = max(keys, key=lambda k_: X[k_][P].sum())
        print(f"   picked on {lab}: stop -{100 * bk[0]:.0f}% after {bk[1]} s: {X[bk][P].sum() - base[P].sum():+.3f} ETH on the pick half, {X[bk][Q].sum() - base[Q].sum():+.3f} on the other")
