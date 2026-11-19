# Every wallet x every entry STYLE x every exit (Nov 19; the owner: "this is an example that you can find strategies on
# other wallets to make money ... here you found the dip thing"). The dip on wallet 4 was found by trying entry styles,
# not filters. For each wallet with 6+ first buys (0.5+ SOL) on days 1-2 and 4+ on days 3-4 of the 4 days: entries =
# plain (the next slot), dip d = 0/5/10/15/20/30% within 60 / 300 s, a 30 s / 120 s delay; exits = m13's 40. The wallet's
# best (entry, exit) is picked on days 1-2 by the result without its best 2%, then scored blind on days 3-4.
#   LAUNCHES=<the 3 launch lists> python3 -I m16_wallet_styles.py SP > ../out/m16_wallet_styles.txt
import sys, os, json, gzip, collections, numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import m14_dip_after as D
D.ENTRIES[:] = [("plain", 0, 0)] + [("dip", d, w) for d in (0.0, 0.05, 0.1, 0.15, 0.2, 0.3) for w in (60, 300)] + [("delay", 0, 30), ("delay", 0, 120)]
def job(m):
    x = D.M.L.get(m); rate = D.M.rate_of(x["quote"]) if x else None
    if rate is None: return []
    try: tr = json.load(gzip.open(f"{D.M.PD}/{m}.json.gz"))
    except Exception: return []
    out = []
    for u, t in D.BY[m]:
        k = next((i for i, e in enumerate(tr) if e["user"] == u and e["buy"]), None)
        if k is None: continue
        pk = tr[k]["vq"] / tr[k]["vt"]; res = {}
        for kind, d, w in D.ENTRIES:
            if kind == "plain": j = next((i for i in range(k + 1, len(tr)) if tr[i]["slot"] > tr[k]["slot"]), None)
            elif kind == "dip": j = next((i for i in range(k + 1, len(tr)) if tr[i]["t"] - tr[k]["t"] <= w and tr[i]["slot"] > tr[k]["slot"] and tr[i]["vq"] / tr[i]["vt"] <= (1 - d) * pk), None)
            else: j = next((i for i in range(k + 1, len(tr)) if tr[i]["t"] - tr[k]["t"] >= w), None)
            if j is not None and j < len(tr) - 1:
                v = D.grid_from(tr, k, j, rate)
                if v: res[D.ENTRIES.index((kind, d, w))] = np.array(v, dtype=np.float32)
        out.append((u, t, res))
    return out
if __name__ == "__main__":
    cnt = collections.Counter(u for u, m, t, *_ in D.R); keep = {u for u, n in cnt.items() if n >= 10}
    D.BY.clear()
    for u, m, t, sol, v, cre, off in D.R:
        if u in keep: D.BY[m].append((u, t))
    with Pool(8) as P: X = [r for part in P.map(job, sorted(D.BY), chunksize=16) for r in part]
    t0 = min(r[1] for r in X); mid = t0 + 2 * 86400; NE, NG = len(D.ENTRIES), len(D.GRID)
    W = collections.defaultdict(list)
    for u, t, res in X: W[u].append((t, res))
    picks = []
    for u, v in W.items():
        a = [r for r in v if r[0] < mid]; b = [r for r in v if r[0] >= mid]
        if len(a) < 6 or len(b) < 4: continue
        best = None
        for e in range(NE):
            A = np.array([r[1][e] for r in a if e in r[1]])
            if len(A) < 6: continue
            k = max(1, round(0.02 * len(A))); s = np.sort(A, axis=0)[:-k].sum(axis=0); g = int(np.argmax(s))
            if best is None or s[g] > best[0]: best = (float(s[g]), e, g, float(A[:, g].sum()), len(A))
        if best is None or best[0] <= 0: continue
        e, g = best[1], best[2]; B = np.array([r[1][e][g] for r in b if e in r[1]])
        picks.append((u, best, len(B), float(B.sum()) if len(B) else 0.0))
    xs = sum(p[3] for p in picks); n = sum(p[2] for p in picks)
    print(f"{len(W)} wallets with 10+ first buys; {len(picks)} with a style positive on days 1-2 (w/o 2%, 6+ trades)")
    print(f"BLIND days 3-4, each with ITS style: {n} trades, {xs:+.2f} SOL ({100 * xs / max(1, n) / 0.5:+.1f}% a trade); wallets up: {sum(1 for p in picks if p[2] and p[3] > 0)} of {sum(1 for p in picks if p[2])}")
    by_e = collections.Counter(D.ENTRIES[p[1][1]][0] for p in picks); print(f"styles picked: {dict(by_e)}")
    print("\nthe wallets up on days 1-2 AND blind on days 3-4 (4+ blind trades), by blind result:")
    for u, b, nb, sb in sorted([p for p in picks if p[2] >= 4 and p[3] > 0], key=lambda p: -p[3])[:40]:
        print(f"   {u[:12]}  {D.ENTRIES[b[1]]}  exit {D.GRID[b[2]]}  days 1-2: {b[4]} trades {b[3]:+.2f} (w/o 2% {b[0]:+.2f})  ->  blind: {nb} trades {sb:+.2f} ({100 * sb / nb / 0.5:+.1f}%)")
