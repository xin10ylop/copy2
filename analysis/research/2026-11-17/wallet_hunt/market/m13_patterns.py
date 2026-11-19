# Coin patterns as trades (Nov 19; the owner: "keep looking, don't stop"). Not copying a wallet: rules on the coins
# themselves, on the 4 days fetched in full (7,263 other-token coins, every trade of each coin's first 40 minutes).
#   A. CREATOR TRACK RECORD: a creator whose earlier coins (in the data, before this one) reached x3 / x5 the launch
#      price or 50% of the curve; we buy its next coin at the first trade 1 s or more after the create.
#   B. RUN-UP: the first trade that takes the curve past P% sold (P = 30, 50, 70, 85) with N+ buys in the last 30 s;
#      we buy at the first trade of the next slot.
# Exits (on our own value): take profit x1.5 / x2 / x3 / x5 / none, hold 60 / 300 / 900 / 2400 s, a 30% fall from our
# best or not; a completed curve sells at its last curve trade. 0.5 SOL, COST SOL a round trip (0.0345, the racing cost, by
# default; a slow rule needs no tip: COST=0.0026 is the model's own fees only), refused past 1.25x
# the decision's price. Picked on days 1-2 (net and without the best 2%), scored blind on days 3-4.
#   LAUNCHES=<the 3 launch lists> python3 -I m13_patterns.py SP > ../out/m13_patterns.txt
import sys, os, json, gzip, itertools, collections, numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import m4_direct as M
H = M.H; INIT = 793_100_000_000_000
TPS = [1.5, 2, 3, 5, 1e9]; HOLDS = [60, 300, 900, 2400]; TRAIL = [False, True]; GRID = list(itertools.product(TPS, HOLDS, TRAIL))
def first(c): i = int(np.argmax(c)) if len(c) else 0; return i if len(c) and c[i] else None
def value(tr, k, rate):
    """our copy entering at the first trade of a later slot than tr[k]; every grid exit's SOL"""
    p = H.prep(tr, k, rate, "slot+1")
    if p["refused"] or not len(p["px"]): return None
    vt0, vq0, b0 = p["ent"]; Q = 0.5e9 / rate; net_in = Q * 1e4 / (1e4 + b0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq, vt, bb = p["vq"], p["vt"], p["bps"]; vq_r = vq + net_in; vt_r = vt * vq / vq_r
    val = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - bb / 1e4) * rate / 1e9 - 0.5 - 0.0026; n = len(val); age = p["age"]; g = first(p["grad"])
    best = np.maximum.accumulate(val); out = []
    for tp, hold, trail in GRID:
        c = [n - 1] + ([g] if g is not None else [])
        i = first(age >= hold); c += [i] if i is not None else []
        if tp < 1e8: i = first(val >= (tp - 1) * 0.5); c += [min(i + 1, n - 1)] if i is not None else []
        if trail: i = first(val < best - 0.3 * (best + 0.5)); c += [min(i + 1, n - 1)] if i is not None else []
        out.append(val[min(c)] - (float(os.environ.get("COST", 0.0345)) - 0.0026))
    return out
def coin(m):
    x = M.L[m]; rate = M.rate_of(x["quote"])
    if rate is None: return None
    try: tr = json.load(gzip.open(f"{M.PD}/{m}.json.gz"))
    except Exception: return None
    if len(tr) < 2: return None
    px0 = (tr[0]["vq"] / tr[0]["vt"]); pmax = max(e["vq"] / e["vt"] for e in tr) / px0; prog = max(1 - e["real"] / INIT for e in tr)
    res = dict(m=m, t=x["t"], creator=x["creator"], pmax=pmax, prog=prog, A=None, B={})
    k = next((i for i, e in enumerate(tr) if e["t"] - x["t"] >= 1), None)
    if k is not None: res["A"] = value(tr, k, rate)
    for P in (0.30, 0.50, 0.70, 0.85):
        for i, e in enumerate(tr):
            if 1 - e["real"] / INIT >= P:
                nb = sum(1 for y in tr[max(0, i - 400):i + 1] if y["buy"] and e["t"] - y["t"] <= 30)
                res["B"][P] = (nb, value(tr, i, rate)); break
    return res
if __name__ == "__main__":
    with Pool(8) as P_: C = [c for c in P_.map(coin, sorted(M.L), chunksize=16) if c]
    C.sort(key=lambda c: c["t"]); t0 = C[0]["t"]; mid = t0 + 2 * 86400
    print(f"{len(C)} coins, {sum(1 for c in C if c['prog'] >= 0.999)} completed their curve in the window; days 1-2 pick, days 3-4 blind")
    def report(name, rows):   # rows: (t, values over GRID)
        rows = [r for r in rows if r[1] is not None]
        a = np.array([r[1] for r in rows if r[0] < mid]); b = np.array([r[1] for r in rows if r[0] >= mid])
        if len(a) < 10 or len(b) < 10: print(f"   {name}: too few ({len(a)} / {len(b)})"); return
        k = max(1, round(0.02 * len(a))); w = [np.sort(a[:, j])[:-k].sum() for j in range(len(GRID))]; j = int(np.argmax(w))
        allpos = sum(1 for jj in range(len(GRID)) if a[:, jj].sum() > 0 and b[:, jj].sum() > 0)
        print(f"   {name}: {len(a)} / {len(b)} trades | picked {GRID[j]}: days 1-2 {a[:, j].sum():+.2f} SOL ({100 * a[:, j].mean() / 0.5:+.1f}%) -> days 3-4 {b[:, j].sum():+.2f} ({100 * b[:, j].mean() / 0.5:+.1f}%)"
              f" | exits positive on both: {allpos} of {len(GRID)}")
    print("\nA. CREATOR TRACK RECORD (its earlier coins in the data):")
    seen = collections.defaultdict(list)
    rowsA = collections.defaultdict(list)
    for c in C:
        prev = seen[c["creator"]]
        if prev:
            rowsA["any earlier coin"].append((c["t"], c["A"]))
            if any(p["pmax"] >= 3 for p in prev): rowsA["an earlier coin x3"].append((c["t"], c["A"]))
            if any(p["pmax"] >= 5 for p in prev): rowsA["an earlier coin x5"].append((c["t"], c["A"]))
            if any(p["prog"] >= 0.5 for p in prev): rowsA["an earlier coin past 50% of the curve"].append((c["t"], c["A"]))
            if sum(p["pmax"] >= 3 for p in prev) >= 2: rowsA["2+ earlier coins x3"].append((c["t"], c["A"]))
        else: rowsA["first coin of its creator"].append((c["t"], c["A"]))
        seen[c["creator"]].append(c)
    for k_, v in rowsA.items(): report(k_, v)
    print("\nB. RUN-UP (the first trade past P% of the curve, with N+ buys in the last 30 s):")
    for P in (0.30, 0.50, 0.70, 0.85):
        for N in (0, 10, 25):
            report(f"P {int(P * 100)}%, {N}+ buys", [(c["t"], c["B"][P][1]) for c in C if P in c["B"] and c["B"][P][0] >= N])
