# How does wallet 4 choose? Step 3 (Nov 18): a launch rule from what is visible in the create slot (c3: wallet 4's coins
# have a smaller creator buy, more other buyers and more of their SOL in the create slot, more TTWofwAg quotes). Our
# 0.5 SOL at the first trade after the create slot, wallet 4's live model with no sale followed, 0.0345 SOL a round
# trip. Grid: other buyers in the create slot >= {2,3,4,5,6}, their SOL >= {0,2,4,6}, the creator's buy <= {1,2,3,any},
# quote {any, TTWofwAg}. Picked on day 1 (the 48 h's first half by launch time, 10+ buys), scored on day 2 -- on the
# coins wallet 4 did NOT buy (the extra trades), and shown on all coins.
#   python3 -I c4_rule.py SP > out/c4_rule.txt
import sys, os, json, gzip, numpy as np
from multiprocessing import Pool
SP = sys.argv[1]; O = f"{SP}/market"; PD = f"{O}/paths_full"
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt"); import hunt_lib as H
WSOL = "So11111111111111111111111111111111111111112"; COST = 0.0345 - 0.0026
L = json.load(open(f"{O}/launches.json")); PR = json.load(open(f"{O}/prices.json")); sol_usd = PR[WSOL]["usdPrice"]
rate_of = lambda q: PR[q]["usdPrice"] / sol_usd * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None
F = {f["m"]: f for f in json.load(open(f"{SP}/launch_features.json"))}
def val(m):
    x = L[m]; r = rate_of(x["quote"])
    try: tr = json.load(gzip.open(f"{PD}/{m}.json.gz"))
    except Exception: return m, None, None
    k = max((j for j, e in enumerate(tr) if e["slot"] <= x["slot"]), default=None)
    if k is None or tr[-1]["t"] - tr[k]["t"] < 300: return m, None, None
    p = H.prep(tr, k, r, "slot+1", pmax=1000)
    return m, (H.model(p, early=None)[0] - COST) if not p["refused"] else None, x["t"]
if __name__ == "__main__":
    with Pool(8) as P: V = {m: (v, t) for m, v, t in P.map(val, sorted(F), chunksize=20) if v is not None}
    R = [dict(F[m], v=v, t=t) for m, (v, t) in V.items()]; tmid = np.median([r["t"] for r in R])
    def S(v):
        v = np.array(v); n = len(v)
        if not n: return "   0"
        s = np.sort(v); k = max(1, round(0.02 * n)); return f"{n:4d} {v.sum():+7.2f} ({100 * v.mean() / 0.5:+6.1f}%) w/o 2% {s[:-k].sum() if n > 1 else 0:+7.2f}"
    print(f"{len(R)} coins with a launch buy; day 1 / day 2 split at the median launch time")
    print(f"baseline, every coin: day 1 {S([r['v'] for r in R if r['t'] < tmid])} | day 2 {S([r['v'] for r in R if r['t'] >= tmid])}")
    print(f"wallet 4's coins:     day 1 {S([r['v'] for r in R if r['t'] < tmid and r['w4']])} | day 2 {S([r['v'] for r in R if r['t'] >= tmid and r['w4']])}")
    G = []
    for nb in (2, 3, 4, 5, 6):
        for so in (0, 2, 4, 6):
            for dv in (1, 2, 3, 1e9):
                for qq in ("any", "TTWofwAg"):
                    f = lambda r, nb=nb, so=so, dv=dv, qq=qq: r["nb0"] >= nb and r["sol0"] >= so and r["dev"] <= dv and (qq == "any" or r["q"] == qq)   # bound now (a late-binding closure gave every rule the last values)
                    d1 = [r["v"] for r in R if r["t"] < tmid and not r["w4"] and f(r)]
                    if len(d1) >= 10: G.append((np.mean(d1), nb, so, dv, qq, f))
    G.sort(key=lambda g: -g[0])
    print(f"\n{len(G)} rules with 10+ day-1 buys (not wallet 4's coins); the 5 best on day 1:")
    for g in G[:5]:
        f = g[5]
        print(f"   buyers>={g[1]} SOL>={g[2]} dev<={g[3] if g[3] < 1e8 else 'any'} quote {g[4]:8s}: day 1 {S([r['v'] for r in R if r['t'] < tmid and not r['w4'] and f(r)])} | day 2 {S([r['v'] for r in R if r['t'] >= tmid and not r['w4'] and f(r)])}")
    g = G[0]; f = g[5]; v = np.array([r["v"] for r in R if r["t"] >= tmid and not r["w4"] and f(r)])
    bs = np.random.default_rng(7).choice(v, size=(10000, len(v))).mean(axis=1) if len(v) else np.zeros(1)
    print(f"\nPICKED on day 1: buyers>={g[1]} SOL>={g[2]} dev<={g[3] if g[3] < 1e8 else 'any'} quote {g[4]} -> day 2, coins wallet 4 skipped: {S(v)}; P(mean>0) {100 * np.mean(bs > 0):.1f}%")
    print(f"   the same rule on all coins, day 2 (wallet 4's included): {S([r['v'] for r in R if r['t'] >= tmid and f(r)])}")
