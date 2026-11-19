# Adaptive take profit (Nov 19; the owner: "or to lower take profit when x y or z changes, stuff like that, adaptation").
# Each live setting plus ONE extra, earlier exit (all live exits stay): the take profit falling with time; a lower take
# profit after the leader's first sale; a trailing stop once the price has risen; a lower take profit under sell
# pressure; a lock-in once the price has risen. Built on rhd15's one-setting simulator. Each live setting; when its TIME limit is what ends the copy, look at that
# moment: if a condition holds (the leader still holds 50%+ of its tokens; the price at or above its price / 1.25x; the
# other traders' net buying over the last 60 s; combinations), keep the coin until a cap (30 min, 1 h, none) and sell
# earlier on: the leader's sale, a 20% drop from the price at the time limit, or either; the take profit stays.
# Otherwise sell at the time limit as now. Exact model, landing 2/3/5 blocks, every coin; picked on one half, scored on
# the other; the variants better than live on both halves listed.
#   python3 -I rhd16_adaptive_tp.py DIR GROUPS_JSON > out/rhd16_adaptive_tp.txt
import sys, os, json, itertools, numpy as np
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
D, GJ = sys.argv[1], sys.argv[2]; DATA = R.Data(D)
G = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
W = {"wallet 1": ({"0x9a3955a122ab8a649a8511df2dce169471fd0ec1"}, 0.1, 0.5, 1.5, (4.0, 600, None, 0, False)),
     "wallet 2": ({"0x5bc235acecff3dde394f4bfc696f7c35efd502f0"}, 0.05, 0, 1.5, (3.5, 900, (10, 30), 0, False)),
     "wallet 3": ({"0xc54d3914f91f984d61b63d491f38934c4e706b79"}, 0.03, 0, 3.0, (3.0, 300, (8, 60), 240, False)),
     "group 4-8": (G, 0.02, 0.5, 3.0, (3.5, 900, None, 240, True))}
CONDS = {"it holds": lambda c: c["holds"], "price >= its": lambda c: c["px"] >= 1.0, "price >= 1.25x its": lambda c: c["px"] >= 1.25,
         "buyers coming (60 s)": lambda c: c["net_buy"] > 0, "it holds & price >= its": lambda c: c["holds"] and c["px"] >= 1.0,
         "it holds & buyers coming": lambda c: c["holds"] and c["net_buy"] > 0, "it holds & price >= 1.25x": lambda c: c["holds"] and c["px"] >= 1.25}
CAPS = [1800, 3600, 10 ** 9]; EXITS = ["its sale", "20% drop", "its sale or 20% drop"]
def first(m): i = np.flatnonzero(m); return int(i[0]) if len(i) else None
def sim(p, rest, L, its_tok, tp, hold, sp, stall, early):
    """live exit index and reason, the value array, and per-index helpers"""
    vt0, vq0, bps0 = p["ent"]; Q = 0.5e9 * p["hopf"] / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    px, age = p["px"], p["age"]; n = len(px); vq, vt, b = p["vq"], p["vt"], p["bps"]; vq_r = vq + net_in; vt_r = vt * vq / vq_r
    val = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - b / 1e4) * p["rate"] * p["hopf"] / 1e9 - 0.5 - 0.0026
    BIG = 10 ** 9; trig = lambda i: BIG if i is None else min(i + 1, n - 1); at = lambda i: BIG if i is None else i
    E = {"grad": at(first(p["grad"])), "tp": trig(first(px >= tp)), "time": at(first(age >= hold))}
    if sp:
        s = np.concatenate([[0], np.cumsum(p["osell"])]); bb = np.concatenate([[0], np.cumsum(p["obuy"])]); lo = np.searchsorted(age, age - sp[1], side="left")
        E["sp"] = trig(first(((s[1:] - s[lo]) - (bb[1:] - bb[lo]) >= sp[0]) & (age >= 30)))
    if stall:
        pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
        E["stall"] = trig(first((pk >= 1.0) & (age - lasthi >= stall)))
    if early: E["its"] = trig(first(p["sell"] & (age >= 30) & (age < 290) & (px < 1.5)))
    why = min(E, key=E.get); e = E[why]
    sold = np.cumsum([e_["tok"] if (e_["user"] == L and not e_["buy"]) else 0.0 for e_ in rest]); bought = its_tok + np.cumsum([e_["tok"] if (e_["user"] == L and e_["buy"]) else 0.0 for e_ in rest])
    return val, e, why, dict(px=px, age=age, n=n, sold=sold, bought=bought, osell=p["osell"], obuy=p["obuy"], itssell=p["sell"], tp_i=E["tp"], trig=trig)
V = {}
for t1 in (60, 120, 180, 300):
    for tp2 in (1.25, 1.5, 2.0, 2.5): V[f"tp falls to {tp2}x after {t1} s"] = ("decay", t1, tp2)
for tp2 in (1.0, 1.25, 1.5, 2.0): V[f"after its sale, tp {tp2}x"] = ("its", tp2)
for a in (1.5, 2.0, 2.5):
    for b in (0.2, 0.3, 0.4): V[f"trail: from {a}x, out on a {int(b * 100)}% drop"] = ("trail", a, b)
for tp2 in (1.0, 1.25, 1.5): V[f"under sell pressure (5/30 s), tp {tp2}x"] = ("press", tp2)
for a in (1.5, 2.0):
    for l_ in (1.0, 1.2): V[f"lock: once {a}x, out at {l_}x"] = ("lock", a, l_)
def extra(h, e_live, spec):
    px, age, n = h["px"], h["age"], h["n"]; trig = h["trig"]
    if spec[0] == "decay": return trig(first((age >= spec[1]) & (px >= spec[2])))
    if spec[0] == "its":
        i0 = first(h["itssell"]); 
        if i0 is None: return 10 ** 9
        return trig(first((np.arange(n) > i0) & (px >= spec[1])))
    if spec[0] == "trail":
        pk = np.maximum.accumulate(px); return trig(first((pk >= spec[1]) & (px <= (1 - spec[2]) * pk)))
    if spec[0] == "press":
        s = np.concatenate([[0], np.cumsum(h["osell"])]); bb = np.concatenate([[0], np.cumsum(h["obuy"])]); lo = np.searchsorted(age, age - 30, side="left")
        return trig(first((((s[1:] - s[lo]) - (bb[1:] - bb[lo])) >= 5) & (age >= 30) & (px >= spec[1])))
    if spec[0] == "lock":
        pk = np.maximum.accumulate(px); return trig(first((pk >= spec[1]) & (px <= spec[2])))
for name, (addrs, mn, mx, lim, (tp, hold, sp, stall, early)) in W.items():
    rows = []
    for c in DATA.L:
        if c not in DATA.TR or not any(x[3] in addrs and x[2] for x in DATA.TR[c]): continue
        tr = DATA.path(c); k = next((j for j, e in enumerate(tr) if e["user"] in addrs and e["buy"]), None)
        if k is None or tr[k]["q"] / 1e9 < mn or tr[k]["t"] > DATA.t_end - 600: continue
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        if (mx and before >= mx) or tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue
        L = tr[k]["user"]; out = {"live": []}; out.update({v: [] for v in V}); ok = True
        for j in R.landings(tr, k):
            if j is None: ok = False; break
            p = R.H.prep(tr, k, R.RATE, j - k, pmax=1000); p["rate"] = R.RATE; prem = (tr[k]["vt"] / p["ent"][0]) ** 2
            if prem > lim:
                for key in out: out[key].append(-0.0004)
                continue
            if not len(p["px"]): ok = False; break
            val, e, why, h = sim(p, tr[j + 1:], L, tr[k]["tok"], tp, hold, sp, stall, early); n = h["n"]
            out["live"].append(val[min(e, n - 1)] - R.COST)
            for v, spec in V.items(): out[v].append(val[min(e, extra(h, e, spec), n - 1)] - R.COST)
        if not ok: continue
        rows.append((tr[k]["t"], {key: np.mean(v) / R.RATE for key, v in out.items()}))
    rows.sort(key=lambda r: r[0]); t = np.array([r[0] for r in rows]); A = t < np.median(t)
    X = {key: np.array([r[1][key] for r in rows]) for key in rows[0][1]}; base = X["live"]
    k2 = max(1, round(0.02 * len(base))); w2 = lambda x: np.sort(x)[:-k2].sum()
    print(f"\n=== {name} (tp {tp}, {hold} s): {len(rows)} copies; live {100 * base.mean() / R.STAKE:+.1f}% a copy, halves {base[A].sum():+.3f} / {base[~A].sum():+.3f} ETH, w/o best 2% {w2(base):+.3f}")
    keys = [k_ for k_ in X if k_ != "live"]
    for P, Q, lab in ((A, ~A, "half 1 -> half 2"), (~A, A, "half 2 -> half 1")):
        bk = max(keys, key=lambda k_: X[k_][P].sum())
        print(f"   picked on {lab}: '{bk}': {X[bk][P].sum() - base[P].sum():+.3f} ETH on the pick half, {X[bk][Q].sum() - base[Q].sum():+.3f} on the other")
    good = [k_ for k_ in keys if X[k_][A].sum() > base[A].sum() and X[k_][~A].sum() > base[~A].sum() and w2(X[k_]) > w2(base)]
    print(f"   better than live on both halves AND without the best 2%: {len(good)} of {len(keys)}")
    for k_ in sorted(good, key=lambda k_: -min(X[k_][A].sum() - base[A].sum(), X[k_][~A].sum() - base[~A].sum()))[:8]:
        x = X[k_]; print(f"      {k_:44s} {100 * x.mean() / R.STAKE:+6.1f}% a copy, halves {x[A].sum() - base[A].sum():+.3f} / {x[~A].sum() - base[~A].sum():+.3f}, w/o 2% {w2(x) - w2(base):+.3f}")
