# The owner (Nov 19): "identify bots that always do the same thing and find a way to smartly profit". Copy-bots buy
# right after the wallets they follow; if a wallet's buys reliably pull in buyers within seconds, a FAST copy (the first
# trade in the next slot) sold a few seconds later sells into those followers. For every wallet's first buys (0.5+ SOL)
# on the 4 days: the buys by others in the 10 s after, and our quick flip: in at the next slot (refused past 1.25x),
# out at the first trade T s (2, 5, 10, 20) after its buy or at x1.2 / x1.5 of our entry. Wallets picked on days 1-2
# (6+ buys there: by their mean flip, or by their followers), scored on days 3-4.
#   LAUNCHES=<the 3 launch lists> python3 -I m11_follow_flow.py SP > ../out/m11_follow_flow.txt
import sys, os, json, gzip, itertools, collections, numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import m4_direct as M, m7_own_vs_copy as M7
H = M.H; TS = [2, 5, 10, 20]; TPS = [1.2, 1.5, 1e9]; GRID = list(itertools.product(TS, TPS))
def first(c): i = int(np.argmax(c)) if len(c) else 0; return i if len(c) and c[i] else None
def job(m):
    rate = M.rate_of(M.L[m]["quote"]); tr = json.load(gzip.open(f"{M.PD}/{m}.json.gz")); us = M7.PAIRS[m]; seen = set(); out = []
    for i, e in enumerate(tr):
        u = e["user"]
        if u not in us or u in seen or not e["buy"]: seen.add(u); continue
        seen.add(u)
        fol = sum(1 for x in tr[i + 1:] if x["buy"] and x["user"] != u and x["t"] - e["t"] <= 10)
        p = H.prep(tr, i, rate, "slot+1")
        if p["refused"] or not len(p["px"]): out.append((u, e["t"], fol, [-0.0004] * len(GRID))); continue
        vt0, vq0, b0 = p["ent"]; Q = 0.5e9 / rate; net_in = Q * 1e4 / (1e4 + b0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
        vq, vt, bb = p["vq"], p["vt"], p["bps"]; vq_r = vq + net_in; vt_r = vt * vq / vq_r
        val = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - bb / 1e4) * rate / 1e9 - 0.5 - 0.0026; n = len(val); age = p["age"]; g = first(p["grad"])
        res = []
        for T, TP in GRID:
            c = [n - 1] + ([g] if g is not None else [])
            i_ = first(age >= T); c += [i_] if i_ is not None else []
            if TP < 1e8: i_ = first(val >= (TP - 1) * 0.5); c += [min(i_ + 1, n - 1)] if i_ is not None else []
            res.append(val[min(c)] - (0.0345 - 0.0026))
        out.append((u, e["t"], fol, res))
    return out
if __name__ == "__main__":
    with Pool(8) as P: X = [r for part in P.map(job, sorted(M7.PAIRS), chunksize=16) for r in part]
    t0 = min(r[1] for r in X); mid = t0 + 2 * 86400
    W = collections.defaultdict(list)
    for r in X: W[r[0]].append(r)
    allv = np.array([r[3] for r in X]); print(f"{len(X)} first buys of {len(W)} wallets; the flip on ALL of them, by exit (a trade): " +
          ", ".join(f"T{T}/tp{TP if TP < 1e8 else '-'} {100 * allv[:, j].mean() / 0.5:+.1f}%" for j, (T, TP) in enumerate(GRID)))
    fol = np.array([r[2] for r in X]); print(f"followers in 10 s: median {np.median(fol):.0f}, 90% {np.percentile(fol, 90):.0f}")
    for lab, key in (("by the flip's mean on days 1-2", "flip"), ("by followers in 10 s on days 1-2", "fol")):
        for j, (T, TP) in enumerate(GRID):
            sc = []
            for u, v in W.items():
                a = [r for r in v if r[1] < mid]; b = [r for r in v if r[1] >= mid]
                if len(a) < 6 or not b: continue
                s = np.mean([r[3][j] for r in a]) if key == "flip" else np.mean([r[2] for r in a])
                sc.append((s, u, [r[3][j] for r in a], [r[3][j] for r in b]))
            sc.sort(key=lambda z: -z[0])
            for N in (10, 50):
                top = sc[:N]; x1 = [x for z in top for x in z[2]]; x2 = [x for z in top for x in z[3]]
                if j in (0, 1, 4, 7): print(f"   {lab}, top {N:2d}, exit T{T}s/tp{TP if TP < 1e8 else '-'}: days 1-2 {100 * np.mean(x1) / 0.5:+6.1f}% ({len(x1)})  ->  days 3-4 {100 * np.mean(x2) / 0.5:+6.1f}% ({len(x2)}), {sum(x2):+.2f} SOL")
