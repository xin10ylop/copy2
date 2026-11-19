# Following the leader's sale under conditions, as wallet 4's Solana copy does (Nov 19; the owner: "in wallet 4, we
# sometimes follow its sell, depending on filters, check here too"). Each live setting, plus: sell at the trade after
# the leader's FIRST sale that meets a condition (its age window, the price against its price, the share of its tokens
# it sells). A one-setting copy of e8's copy_vals (checked equal to it with the condition "never"). Exact model,
# landing 2/3/5 blocks, every coin; halves; each condition picked on one half and scored on the other.
#   python3 -I rhd13_its_sale_filters.py DIR GROUPS_JSON > out/rhd13_its_sale_filters.txt
import sys, os, json, numpy as np
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
T, H, S, ST, I = R.TP, R.HOLD, R.SPS, R.STALL, R.ITS
D, GJ = sys.argv[1], sys.argv[2]; DATA = R.Data(D)
G = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
W = {"wallet 1": ({"0x9a3955a122ab8a649a8511df2dce169471fd0ec1"}, 0.1, 0.5, 1.5, (4.0, 600, None, 0)),
     "wallet 2": ({"0x5bc235acecff3dde394f4bfc696f7c35efd502f0"}, 0.05, 0, 1.5, (3.5, 900, (10, 30), 0)),
     "wallet 3": ({"0xc54d3914f91f984d61b63d491f38934c4e706b79"}, 0.03, 0, 3.0, (3.0, 300, (8, 60), 240)),
     "group 4-8": (G, 0.02, 0.5, 3.0, (3.5, 900, None, 240))}
COND = {"never": None, "always": dict(),
        "in 0-30 s": dict(age=(0, 30)), "in 30-290 s (wallet 4's)": dict(age=(30, 290)), "in 0-60 s": dict(age=(0, 60)), "after 60 s": dict(age=(60, 1e9)),
        "price < 1.0x": dict(px=1.0), "price < 1.25x": dict(px=1.25), "price < 1.5x": dict(px=1.5),
        "sells 50%+ of its tokens": dict(frac=0.5), "sells all": dict(frac=0.99),
        "30-290 s, under 1.5x (wallet 4's rule)": dict(age=(30, 290), px=1.5), "30-290 s, sells 50%+": dict(age=(30, 290), frac=0.5),
        "under 1.0x, sells 50%+": dict(px=1.0, frac=0.5), "after 60 s, under 1.25x": dict(age=(60, 1e9), px=1.25)}
def first(m): i = np.flatnonzero(m); return int(i[0]) if len(i) else None
def one(p, rest, L, its_tok, tp, hold, sp, stall, cond):
    """our ETH for one landing under one setting (e8's copy_vals, one combination) and an its-sale condition"""
    if p["refused"] or not len(p["px"]): return None
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
    if cond is not None:
        m = p["sell"].copy()
        if "age" in cond: m &= (age >= cond["age"][0]) & (age < cond["age"][1])
        if "px" in cond: m &= px < cond["px"]
        if "frac" in cond:
            sold = np.cumsum([e["tok"] if (e["user"] == L and not e["buy"]) else 0.0 for e in rest]); m &= sold >= cond["frac"] * its_tok
        E.append(trig(first(m)))
    e = min(E); return val[min(e, n - 1)]
for name, (addrs, mn, mx, lim, (tp, hold, sp, stall)) in W.items():
    rows = []
    for c in DATA.L:
        if c not in DATA.TR or not any(x[3] in addrs and x[2] for x in DATA.TR[c]): continue
        tr = DATA.path(c); k = next((j for j, e in enumerate(tr) if e["user"] in addrs and e["buy"]), None)
        if k is None or tr[k]["q"] / 1e9 < mn or tr[k]["t"] > DATA.t_end - 600: continue
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        if (mx and before >= mx) or tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue
        L = tr[k]["user"]; its_tok = tr[k]["tok"]; vs = {cn: [] for cn in COND}
        for j in R.landings(tr, k):
            if j is None: break
            p = R.H.prep(tr, k, R.RATE, j - k, pmax=1000); p["rate"] = R.RATE; prem = (tr[k]["vt"] / p["ent"][0]) ** 2; rest = tr[j + 1:]
            for cn, cd in COND.items():
                v = one(p, rest, L, its_tok, tp, hold, sp, stall, cd)
                vs[cn].append(-0.0004 if prem > lim else (None if v is None else v - R.COST))
        if any(len(v) < 3 or None in v for v in vs.values()): continue
        rows.append((tr[k]["t"], {cn: np.mean(v) / R.RATE for cn, v in vs.items()}))
    rows.sort(key=lambda r: r[0]); t = np.array([r[0] for r in rows]); A = t < np.median(t)
    X = {cn: np.array([r[1][cn] for r in rows]) for cn in COND}; base = X["never"]
    print(f"\n=== {name} (tp {tp}, {hold} s, sp {sp}, stall {stall}, limit {lim}): {len(rows)} copies   (a copy | ETH all | half 1 / half 2 | against never: half 1 / half 2)")
    for cn, x in X.items():
        d1, d2 = x[A].sum() - base[A].sum(), x[~A].sum() - base[~A].sum()
        print(f"   {cn:40s} {100 * x.mean() / R.STAKE:+6.1f}% | {x.sum():+.3f} | {x[A].sum():+.3f} / {x[~A].sum():+.3f} | {d1:+.3f} / {d2:+.3f}{'   <- better on both halves' if d1 > 0 and d2 > 0 else ''}")
