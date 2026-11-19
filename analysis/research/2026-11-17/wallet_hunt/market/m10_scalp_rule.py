# The winners' rule, traded ourselves (Nov 19, after m9_profile: the daily winners that do not buy at launch buy coins
# seconds old and leave fast unless the coin runs; their winners and losers look the same when they buy). On EVERY coin
# of the 4 days: decide at the first trade A s or more after the launch (A = 3, 5, 10, 20, 30), only if the last 30 s had
# B+ buys (0, 10, 20); enter at the first trade in a LATER slot (refused past 1.25x the decision's price), 0.5 SOL. Exit
# on OUR value: at H s (10, 20, 30, 60) after the decision, sell if we are under +X% (0, 5, 10%); after that a take
# profit (x1.5, x2, x3), a fall of 30% from our best value, or 300 s; a completed curve sells at its last trade.
# 0.0345 SOL a round trip. Picked on days 1-2 (net and without the best 2%), scored on days 3-4.
#   LAUNCHES=<the 3 launch lists> python3 -I m10_scalp_rule.py SP > ../out/m10_scalp_rule.txt
import sys, os, json, gzip, itertools, collections, numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import m4_direct as M
H = M.H; AS = [3, 5, 10, 20, 30]; BS = [0, 10, 20]; HS = [10, 20, 30, 60]; XS = [0.0, 0.05, 0.10]; TPS = [1.5, 2.0, 3.0]
GRID = list(itertools.product(HS, XS, TPS))
def first(c): i = int(np.argmax(c)) if len(c) else 0; return i if len(c) and c[i] else None
def coin(m):
    rate = M.rate_of(M.L[m]["quote"])
    if rate is None: return []
    try: tr = json.load(gzip.open(f"{M.PD}/{m}.json.gz"))
    except Exception: return []
    if len(tr) < 3: return []
    t0 = tr[0]["t"]; out = []
    for A in AS:
        k = next((i for i, e in enumerate(tr) if e["t"] - t0 >= A), None)
        if k is None: continue
        b30 = sum(1 for e in tr[:k + 1] if e["buy"] and tr[k]["t"] - e["t"] <= 30)
        p = H.prep(tr, k, rate, "slot+1")
        if p["refused"] or not len(p["px"]): continue
        vt0, vq0, b0 = p["ent"]; Q = 0.5e9 / rate; net_in = Q * 1e4 / (1e4 + b0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
        vq, vt, bb = p["vq"], p["vt"], p["bps"]; vq_r = vq + net_in; vt_r = vt * vq / vq_r
        val = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - bb / 1e4) * rate / 1e9 - 0.5 - 0.0026   # SOL if sold at each trade
        age = p["age"]; n = len(val); g = first(p["grad"]); best = np.maximum.accumulate(val)
        res = []
        for Hs, X, TP in GRID:
            c = [n - 1] + ([g] if g is not None else [])
            ih = first(age >= Hs)
            if ih is not None and val[ih] < X * 0.5: c.append(min(ih + 1, n - 1))   # not running at H s: out
            i = first(val >= (TP - 1) * 0.5); c += [min(i + 1, n - 1)] if i is not None else []
            i = first((age >= Hs) & (val < best - 0.3 * (best + 0.5))); c += [min(i + 1, n - 1)] if i is not None else []
            i = first(age >= 300); c += [i] if i is not None else []
            res.append(val[min(c)] - (0.0345 - 0.0026))
        out.append((A, b30, tr[k]["t"], res))
    return out
if __name__ == "__main__":
    with Pool(8) as P: R = [(m, x) for m, part in zip(sorted(M.L), P.map(coin, sorted(M.L), chunksize=16)) for x in part]
    t0 = min(x[2] for _, x in R); mid = t0 + 2 * 86400
    print(f"{len(M.L)} coins; {len(R)} decisions (coins x entry times)")
    best = []
    for A in AS:
        for B in BS:
            rows = [x for _, x in R if x[0] == A and x[1] >= B]
            if not rows: continue
            Xa = np.array([x[3] for x in rows]); T = np.array([x[2] for x in rows]); a = T < mid
            for j, (Hs, X, TP) in enumerate(GRID):
                x1 = Xa[a, j]; x2 = Xa[~a, j]
                if len(x1) < 30: continue
                k = max(1, round(0.02 * len(x1))); wo = np.sort(x1)[:-k].sum()
                best.append((x1.sum(), wo, A, B, Hs, X, TP, len(x1), 100 * x1.mean() / 0.5, x2.sum(), len(x2), 100 * x2.mean() / 0.5 if len(x2) else 0))
    best.sort(key=lambda r: -r[1])
    print(f"\n{len(best)} rules. The 10 best on days 1-2 (by the result without the best 2%), then their days 3-4 (unseen):")
    print("   entry age  buys30 | out at H s if under | tp  || days 1-2: trades  a trade  net   w/o 2%  || days 3-4: trades  a trade  net")
    for r in best[:10]:
        print(f"   {r[2]:4d} s    {r[3]:3d}   | {r[4]:3d} s under +{100 * r[5]:.0f}%      | x{r[6]:<3} ||  {r[7]:6d}  {r[8]:+6.1f}%  {r[0]:+7.1f}  {r[1]:+7.1f} ||  {r[10]:6d}  {r[11]:+6.1f}%  {r[9]:+7.1f}")
    pos = [r for r in best if r[0] > 0 and r[1] > 0]
    print(f"\nrules positive on days 1-2 (and without the best 2%): {len(pos)} of {len(best)}; of those, positive on days 3-4: {sum(1 for r in pos if r[9] > 0)}")
    allr = np.array([r[11] for r in best]); print(f"all {len(best)} rules on days 3-4: median {np.median(allr):+.1f}% a trade, best {allr.max():+.1f}%")
