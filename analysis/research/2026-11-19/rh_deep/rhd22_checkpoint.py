# A checkpoint (Nov 19; the owner: "if tp is not reached within x seconds, sell ... be smart"). Each wallet's setting now
# plus: at T seconds after its buy, if the coin has not proved itself (variant "peak": its price never reached M x its
# price by T; variant "now": the price at T is under M x), sell at T; otherwise keep the live exits. T 10-300 s, M 1.0-2.0.
# rhd21's simulation, exact model, every coin; picked on one half, scored on the other; without the best 2%.
#   python3 -I rhd22_checkpoint.py DIR GROUPS_JSON > out/rhd22_checkpoint.txt
import sys, os, json, numpy as np
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
D, GJ = sys.argv[1], sys.argv[2]; DATA = R.Data(D)
G = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
W = {"wallet 1 (tp 4, 600 s)": ({"0x9a3955a122ab8a649a8511df2dce169471fd0ec1"}, 0.1, 0.5, 1.5, (4.0, 600, None, 0, False)),
     "wallet 2 (tp 3.5, 900 s, sp 10/30)": ({"0x5bc235acecff3dde394f4bfc696f7c35efd502f0"}, 0.05, 0, 1.5, (3.5, 900, (10, 30), 0, False)),
     "wallet 3 (sold at 45 s)": ({"0xc54d3914f91f984d61b63d491f38934c4e706b79"}, 0.03, 0, 3.0, (1e9, 45, None, 0, False)),
     "group 4-8 (tp 3.5, 900 s, stall 240, early)": (G, 0.02, 0.5, 3.0, (3.5, 900, None, 240, True))}
TS = [10, 20, 30, 45, 60, 90, 120, 180, 300]; MS = [1.0, 1.1, 1.2, 1.3, 1.5, 2.0]; VAR = ["peak", "now"]
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
    rows = []; keys = [(T_, M_, v_) for T_ in TS if T_ < hold for M_ in MS for v_ in VAR]
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
            px = p["px"]; pk = np.maximum.accumulate(px)
            for T_, M_, v_ in keys:
                c_ = first(age >= T_)
                if c_ is None or c_ >= e: out[(T_, M_, v_)].append(val[e] - R.COST); continue   # the live exit came first
                fail = (pk[c_] < M_) if v_ == "peak" else (px[c_] < M_)
                out[(T_, M_, v_)].append(val[c_ if fail else e] - R.COST)
        if not ok: continue
        rows.append((tr[k]["t"], {key: np.mean(v) / R.RATE for key, v in out.items()}))
    rows.sort(key=lambda r: r[0]); t = np.array([r[0] for r in rows]); A = t < np.median(t); L7 = t >= DATA.t_end - 7 * 86400
    X = {key: np.array([r[1][key] for r in rows]) for key in rows[0][1]}; base = X["live"]; k2 = max(1, round(0.02 * len(base)))
    w2 = lambda x: np.sort(x)[:-k2].sum(); pc = lambda x: 100 * x.mean() / R.STAKE
    print(f"\n=== {name}: {len(rows)} copies   (a copy | ETH all | half 1 / half 2 | w/o best 2% | last 7 d)")
    print(f"   live                   {pc(base):+6.1f}% | {base.sum():+.3f} | {base[A].sum():+.3f} / {base[~A].sum():+.3f} | {w2(base):+.3f} | {pc(base[L7]):+6.1f}%")
    good = [k_ for k_ in keys if X[k_][A].sum() > base[A].sum() and X[k_][~A].sum() > base[~A].sum() and w2(X[k_]) > w2(base)]
    print(f"   better than live on both halves and without the best 2%: {len(good)} of {len(keys)}")
    for k_ in sorted(good, key=lambda k_: -min(X[k_][A].sum() - base[A].sum(), X[k_][~A].sum() - base[~A].sum()))[:6]:
        x = X[k_]; print(f"      by {k_[0]:3d} s {k_[2]:4s} >= {k_[1]:.1f}x  {pc(x):+6.1f}% | {x.sum():+.3f} | {x[A].sum():+.3f} / {x[~A].sum():+.3f} | {w2(x):+.3f} | {pc(x[L7]):+6.1f}%")
    for P, Q, lab in ((A, ~A, "half 1 -> half 2"), (~A, A, "half 2 -> half 1")):
        bk = max(keys, key=lambda k_: X[k_][P].sum())
        print(f"   picked on {lab}: by {bk[0]} s {bk[2]} >= {bk[1]}x: {X[bk][P].sum() - base[P].sum():+.3f} ETH on the pick half, {X[bk][Q].sum() - base[Q].sum():+.3f} on the other")
