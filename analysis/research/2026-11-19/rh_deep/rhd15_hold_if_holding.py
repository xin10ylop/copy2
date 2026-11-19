# Hold longer when it makes sense (Nov 19; the owner: "check if we decide to hold the coin for longer if wallet is still
# holding, idk stuff like that, be smart"). Each live setting; when its TIME limit is what ends the copy, look at that
# moment: if a condition holds (the leader still holds 50%+ of its tokens; the price at or above its price / 1.25x; the
# other traders' net buying over the last 60 s; combinations), keep the coin until a cap (30 min, 1 h, none) and sell
# earlier on: the leader's sale, a 20% drop from the price at the time limit, or either; the take profit stays.
# Otherwise sell at the time limit as now. Exact model, landing 2/3/5 blocks, every coin; picked on one half, scored on
# the other; the variants better than live on both halves listed.
#   python3 -I rhd15_hold_if_holding.py DIR GROUPS_JSON > out/rhd15_hold_if_holding.txt
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
for name, (addrs, mn, mx, lim, (tp, hold, sp, stall, early)) in W.items():
    rows = []
    for c in DATA.L:
        if c not in DATA.TR or not any(x[3] in addrs and x[2] for x in DATA.TR[c]): continue
        tr = DATA.path(c); k = next((j for j, e in enumerate(tr) if e["user"] in addrs and e["buy"]), None)
        if k is None or tr[k]["q"] / 1e9 < mn or tr[k]["t"] > DATA.t_end - 3600: continue
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        if (mx and before >= mx) or tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue
        L = tr[k]["user"]; out = {"live": []}; out.update({(cn, cap, ex): [] for cn in CONDS for cap in CAPS for ex in EXITS}); ok = True
        for j in R.landings(tr, k):
            if j is None: ok = False; break
            p = R.H.prep(tr, k, R.RATE, j - k, pmax=1000); p["rate"] = R.RATE; prem = (tr[k]["vt"] / p["ent"][0]) ** 2
            if prem > lim:
                for key in out: out[key].append(-0.0004)
                continue
            if not len(p["px"]): ok = False; break
            val, e, why, h = sim(p, tr[j + 1:], L, tr[k]["tok"], tp, hold, sp, stall, early); n = h["n"]
            live = val[min(e, n - 1)]; out["live"].append(live - R.COST)
            if why != "time" or e >= n:
                for key in out:
                    if key != "live": out[key].append(live - R.COST)
                continue
            age, px = h["age"], h["px"]; lo = np.searchsorted(age, age[e] - 60, side="left")
            ctx = dict(holds=h["sold"][e] < 0.5 * h["bought"][e], px=px[e], net_buy=int(h["obuy"][lo:e + 1].sum() - h["osell"][lo:e + 1].sum()))
            after = np.arange(n) > e
            for cn, cf in CONDS.items():
                go = cf(ctx)
                for cap in CAPS:
                    for ex in EXITS:
                        if not go: out[(cn, cap, ex)].append(live - R.COST); continue
                        cand = [h["tp_i"] if h["tp_i"] > e else 10 ** 9]
                        c_cap = first(after & (age >= cap)); cand.append(c_cap if c_cap is not None else n - 1)
                        if "its sale" in ex: i_ = first(after & h["itssell"]); cand.append(h["trig"](i_))
                        if "drop" in ex: i_ = first(after & (px < 0.8 * px[e])); cand.append(h["trig"](i_))
                        out[(cn, cap, ex)].append(val[min(min(cand), n - 1)] - R.COST)
        if not ok: continue
        rows.append((tr[k]["t"], {key: np.mean(v) / R.RATE for key, v in out.items()}))
    rows.sort(key=lambda r: r[0]); t = np.array([r[0] for r in rows]); A = t < np.median(t)
    X = {key: np.array([r[1][key] for r in rows]) for key in rows[0][1]}; base = X["live"]
    k2 = max(1, round(0.02 * len(base))); w2 = lambda x: np.sort(x)[:-k2].sum()
    print(f"\n=== {name} (tp {tp}, {hold} s): {len(rows)} copies; live {100 * base.mean() / R.STAKE:+.1f}% a copy, halves {base[A].sum():+.3f} / {base[~A].sum():+.3f} ETH, w/o best 2% {w2(base):+.3f}")
    keys = [k_ for k_ in X if k_ != "live"]
    for P, Q, lab in ((A, ~A, "half 1 -> half 2"), (~A, A, "half 2 -> half 1")):
        bk = max(keys, key=lambda k_: X[k_][P].sum())
        print(f"   picked on {lab}: '{bk[0]}', cap {'none' if bk[1] > 1e8 else str(bk[1]) + ' s'}, out on {bk[2]}: {X[bk][P].sum() - base[P].sum():+.3f} ETH on the pick half, {X[bk][Q].sum() - base[Q].sum():+.3f} on the other")
    good = [k_ for k_ in keys if X[k_][A].sum() > base[A].sum() and X[k_][~A].sum() > base[~A].sum() and w2(X[k_]) > w2(base)]
    print(f"   better than live on both halves AND without the best 2%: {len(good)} of {len(keys)}")
    for k_ in sorted(good, key=lambda k_: -min(X[k_][A].sum() - base[A].sum(), X[k_][~A].sum() - base[~A].sum()))[:8]:
        x = X[k_]; print(f"      {k_[0]:26s} cap {'none' if k_[1] > 1e8 else str(k_[1]) + ' s':7s} out on {k_[2]:22s} {100 * x.mean() / R.STAKE:+6.1f}% a copy, halves {x[A].sum() - base[A].sum():+.3f} / {x[~A].sum() - base[~A].sum():+.3f}, w/o 2% {w2(x) - w2(base):+.3f}")
