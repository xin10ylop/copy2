# Buy the dip after a strong wallet's buy (Nov 19; the owner: "keep looking"). Instead of buying right behind the
# wallet (m4), wait: enter at the first trade, within W s (60, 300) of its buy, where the price is at or below (1 - d)
# of the price its buy left (d = 0, 10%, 20%, 30%); or at a fixed delay (30 s, 120 s). Same exits as m13 (tp x1.5-none,
# hold 60-2400 s, a 30% fall from our best or not). Leaders: wallet 4 (its 0.5+ SOL first buys), the wallets whose
# copy (m6 rows) was up on days 1-2 without the best 2% (6+ copies), and every wallet. Picked on days 1-2, scored on
# days 3-4. COST a round trip (0.0345 by default; a dip entry needs no race, so COST=0.0026 is shown too).
#   LAUNCHES=<the 3 launch lists> [COST=...] python3 -I m14_dip_after.py SP > ../out/m14_dip_after.txt
import sys, os, json, gzip, itertools, collections, numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import m4_direct as M
H = M.H; COST = float(os.environ.get("COST", 0.0345))
TPS = [1.5, 2, 3, 5, 1e9]; HOLDS = [60, 300, 900, 2400]; TRAIL = [False, True]; GRID = list(itertools.product(TPS, HOLDS, TRAIL))
ENTRIES = [("dip", d, w) for d in (0.0, 0.1, 0.2, 0.3) for w in (60, 300)] + [("delay", 0, 30), ("delay", 0, 120)]
def first(c): i = int(np.argmax(c)) if len(c) else 0; return i if len(c) and c[i] else None
def grid_from(tr, k, j, rate):
    """enter right after trade j (j > k = its buy); every GRID exit, SOL"""
    p = H.prep(tr, k, rate, j - k, pmax=1e9)
    if not len(p["px"]): return None
    vt0, vq0, b0 = p["ent"]; Q = 0.5e9 / rate; net_in = Q * 1e4 / (1e4 + b0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq, vt, bb = p["vq"], p["vt"], p["bps"]; vq_r = vq + net_in; vt_r = vt * vq / vq_r
    val = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - bb / 1e4) * rate / 1e9 - 0.5 - 0.0026; n = len(val)
    age = p["age"] - p["last"]; g = first(p["grad"]); best = np.maximum.accumulate(val); out = []
    for tp, hold, trail in GRID:
        c = [n - 1] + ([g] if g is not None else [])
        i = first(age >= hold); c += [i] if i is not None else []
        if tp < 1e8: i = first(val >= (tp - 1) * 0.5); c += [min(i + 1, n - 1)] if i is not None else []
        if trail: i = first(val < best - 0.3 * (best + 0.5)); c += [min(i + 1, n - 1)] if i is not None else []
        out.append(val[min(c)] - (COST - 0.0026))
    return out
R = json.load(gzip.open(f"{M.O}/m6_rows.json.gz")); BY = collections.defaultdict(list)
for u, m, t, sol, v, cre, off in R: BY[m].append((u, t))
def job(m):
    x = M.L.get(m); rate = M.rate_of(x["quote"]) if x else None
    if rate is None: return []
    try: tr = json.load(gzip.open(f"{M.PD}/{m}.json.gz"))
    except Exception: return []
    out = []
    for u, t in BY[m]:
        k = next((i for i, e in enumerate(tr) if e["user"] == u and e["buy"]), None)
        if k is None: continue
        pk = tr[k]["vq"] / tr[k]["vt"]; res = {}
        for kind, d, w in ENTRIES:
            if kind == "dip": j = next((i for i in range(k + 1, len(tr)) if tr[i]["t"] - tr[k]["t"] <= w and tr[i]["slot"] > tr[k]["slot"] and tr[i]["vq"] / tr[i]["vt"] <= (1 - d) * pk), None)
            else: j = next((i for i in range(k + 1, len(tr)) if tr[i]["t"] - tr[k]["t"] >= w), None)
            if j is not None and j < len(tr) - 1: res[(kind, d, w)] = grid_from(tr, k, j, rate)
        out.append((u, t, res))
    return out
if __name__ == "__main__":
    with Pool(8) as P: X = [r for part in P.map(job, sorted(BY), chunksize=16) for r in part]
    t0 = min(r[1] for r in X); mid = t0 + 2 * 86400
    copyv = collections.defaultdict(list)
    for u, m, t, sol, v, cre, off in R:
        if t < mid: copyv[u].append(v)
    good = {u for u, v in copyv.items() if len(v) >= 6 and sum(v) > 0 and np.sort(v)[:-max(1, round(0.02 * len(v)))].sum() > 0}
    groups = {"wallet 4": {M.W4}, f"chosen on days 1-2 ({len(good)} wallets)": good, "every wallet": None}
    print(f"{len(X)} leader buys; COST {COST} SOL a round trip; days 1-2 pick (entry and exit), days 3-4 blind")
    for gname, us in groups.items():
        print(f"\n== {gname} ==")
        for ent in ENTRIES:
            a = np.array([r[2][ent] for r in X if (us is None or r[0] in us) and ent in r[2] and r[2][ent] and r[1] < mid])
            b = np.array([r[2][ent] for r in X if (us is None or r[0] in us) and ent in r[2] and r[2][ent] and r[1] >= mid])
            if len(a) < 8 or len(b) < 8: print(f"   {ent}: too few ({len(a)} / {len(b)})"); continue
            k = max(1, round(0.02 * len(a))); j = int(np.argmax([np.sort(a[:, i])[:-k].sum() for i in range(len(GRID))]))
            both = sum(1 for i in range(len(GRID)) if a[:, i].sum() > 0 and b[:, i].sum() > 0)
            print(f"   {ent[0]} {ent[1]:.0%} within {ent[2]} s: {len(a)} / {len(b)} | picked {GRID[j]}: {100 * a[:, j].mean() / 0.5:+.1f}% -> blind {100 * b[:, j].mean() / 0.5:+.1f}% ({b[:, j].sum():+.2f} SOL) | exits up on both: {both}/{len(GRID)}")
