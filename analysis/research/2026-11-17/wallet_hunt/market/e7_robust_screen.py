# The re-screen with no exit assumed (Nov 18, the owner: "there is no tab style exit or wallet 4 exit, there is find a
# wallet then engineer the exit"; "the floats are the edge even for new wallets"). The 4 days of float-quote launches on
# disk (Nov 14 01:07 - Nov 18 01:07 UTC, paths_full, true in-slot order). Every wallet's first buy of a coin (0.5+ SOL),
# our 0.5 SOL at the three landings (hunt_lib), 0.0345 SOL a round trip, under 64 exit settings: tp {2, 3, 4, 6}x x stall
# {off, 180 s} x sell pressure {off, 5/60 from 30 s} x {300, 600} s x its sale {never followed, followed 30-290 s under
# 1.5x}. A wallet with 30+ copies qualifies when 75%+ of the settings are positive on both halves (days 1-2 / 3-4), the
# median setting is positive without the best 2%, and its bootstrap P(mean > 0) is 90%+. Wallet 4 and TAB16RxX shown.
#   python3 -I e7_robust_screen.py SP LAUNCHES,... > ../out/e7_robust_screen.txt
import sys, os, json, gzip, itertools, collections, numpy as np
from multiprocessing import Pool
SP = sys.argv[1]; O = f"{SP}/market"; PD = f"{O}/paths_full"
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(here, "..")); import hunt_lib as H
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; TAB = "TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3"; ME = H.ME
WSOL = "So11111111111111111111111111111111111111112"; COST = 0.0345 - 0.0026; MINC = int(os.environ.get("MINC", 30))
FLOATS = ("3NZ9JMVB", "pumpCmXq", "SPCXxcqX", "TTWofwAg", "DJTu7vi8", "98sMhvDw", "XsbEhLAt"); L = {}
for f_ in sys.argv[2].split(","): L.update({m: x for m, x in json.load(open(f_)).items() if x and x["quote"][:8] in FLOATS and os.path.exists(f"{PD}/{m}.json.gz")})
PR = json.load(open(f"{O}/prices.json")); su = PR[WSOL]["usdPrice"]; rate_of = lambda q: PR[q]["usdPrice"] / su * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None
G = list(itertools.product((2, 3, 4, 6), (0, 180), (None, (5, 60, 30)), (300, 600), (None, (30, 290, 1.5))))
def vals(p):
    """The 64 settings at once on one prepared copy (hunt_lib.model's code, every part a setting)."""
    if p["refused"]: return np.full(len(G), -0.0004)
    vt0, vq0, bps0 = p["ent"]; Q = 0.5e9 * p["hopf"] / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    n = len(p["px"])
    def out(ex):
        if ex is None: vq, vt, b = vq0, vt0, bps0
        else: vq, vt, b = p["vq"][ex], p["vt"][ex], p["bps"][ex]
        vq_r = vq + net_in; vt_r = vt * vq / vq_r
        return (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - b / 1e4) * p["rate"] * p["hopf"] / 1e9 - 0.5 - 0.0026
    if n == 0: return np.full(len(G), out(None))
    px, age = p["px"], p["age"]
    gi = H.first(p["grad"])
    lo = np.searchsorted(age, age - 60, side="left"); s = np.concatenate([[0], np.cumsum(p["osell"])]); b = np.concatenate([[0], np.cumsum(p["obuy"])])
    spi = H.first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= 5) & (age >= 30))
    pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
    sti = H.first((pk >= 1.0) & (age - lasthi >= 180)); ei = H.first(p["sell"] & (age >= 30) & (age < 290) & (px < 1.5))
    tpi = {t: H.first(px >= t) for t in (2, 3, 4, 6)}; hi = {h: H.first(age >= h) for h in (300, 600)}
    res = []
    for tp, st, sp, hold, early in G:
        c = []
        if gi is not None: c.append((gi, 0))
        if early and ei is not None: c.append((ei, 1))
        if tpi[tp] is not None: c.append((tpi[tp], 1))
        if sp and spi is not None: c.append((spi, 1))
        if st and sti is not None: c.append((sti, 1))
        if hi[hold] is not None: c.append((hi[hold], 0))
        if not c: res.append(out(n - 1)); continue
        i, d = min(c); res.append(out(min(i + d, n - 1)))
    return np.array(res)
def firsts(m):
    x = L[m]; r = rate_of(x["quote"])
    if r is None: return []
    try: tr = json.load(gzip.open(f"{PD}/{m}.json.gz"))
    except Exception: return []
    if not tr: return []
    seen = set(); out = []
    for i, e in enumerate(tr):
        u = e["user"]
        if u in seen or u == ME: continue
        seen.add(u)
        if e["buy"] and e["q"] * (1 + e["bps"] / 1e4) * r / 1e9 >= 0.5 and tr[-1]["t"] - e["t"] >= 600: out.append((u, m, i, e["t"]))
    return out
def job(a):
    m, items = a; x = L[m]; r = rate_of(x["quote"]); tr = json.load(gzip.open(f"{PD}/{m}.json.gz"))
    return [(u, t, np.mean([vals(H.prep(tr, i, r, n)) for n in (4, 8, "slot+1")], axis=0) - COST, x["creator"], tr[i]["slot"] - x["slot"]) for u, i, t in items]
if __name__ == "__main__":
    with Pool(8) as P: F = [b for part in P.map(firsts, sorted(L), chunksize=20) for b in part]
    cnt = collections.Counter(u for u, m, i, t in F); keep = {u for u, n in cnt.items() if n >= MINC} | {W4, TAB}
    jobs = collections.defaultdict(list)
    for u, m, i, t in F:
        if u in keep: jobs[m].append((u, i, t))
    with Pool(8) as P: R = [z for part in P.map(job, list(jobs.items()), chunksize=4) for z in part]
    tmid = np.median([t for u, t, v, c, l in R]); W = collections.defaultdict(list)
    for u, t, v, c, l in R: W[u].append((t, v, c, l))
    print(f"{len(L)} float-quote coins; {len(keep) - 2} wallets with {MINC}+ copies (+ wallet 4, TAB16RxX); {len(G)} exit settings; halves at the median copy time")
    rows = []
    for u, v in W.items():
        T = np.array([z[0] for z in v]); V = np.array([z[1] for z in v]); A = T < tmid
        if A.sum() < 5 or (~A).sum() < 5: continue
        both = np.mean((V[A].mean(axis=0) > 0) & (V[~A].mean(axis=0) > 0))
        tot = V.mean(axis=0); med = int(np.argsort(tot)[len(G) // 2]); vm = V[:, med]; s = np.sort(vm); k = max(1, round(0.02 * len(vm)))
        boot = float(np.mean(np.random.default_rng(7).choice(vm, size=(4000, len(vm))).mean(axis=1) > 0))
        best = int(np.argmax(np.minimum(V[A].mean(axis=0), V[~A].mean(axis=0))))
        rows.append(dict(u=u, n=len(v), both=both, med=100 * vm.mean() / 0.5, wo=s[:-k].sum(), boot=boot, best=G[best], bmin=100 * min(V[A, best].mean(), V[~A, best].mean()) / 0.5,
                         cre=len({z[2] for z in v}), launch=np.mean([z[3] <= 1 for z in v]), ok=both >= 0.75 and s[:-k].sum() > 0 and boot >= 0.90))
    nm = lambda g: f"tp {g[0]}x, stall {g[1] or 'off'}, sp {'5/60' if g[2] else 'off'}, {g[3]} s, its sale {'followed' if g[4] else 'not'}"
    hdr = "wallet        copies | settings + on both halves | median setting: a copy, w/o 2%, P | creators, at launch | steadiest setting (its weaker half)"
    line = lambda r: f"{r['u'][:12]}  {r['n']:5d} | {100 * r['both']:5.0f}% | {r['med']:+6.1f}% {r['wo']:+6.2f} {100 * r['boot']:5.1f}% | {r['cre']:4d} {100 * r['launch']:4.0f}% | {nm(r['best'])} ({r['bmin']:+.1f}%)"
    print("\n== THE YARDSTICKS ==\n" + hdr)
    for r in rows:
        if r["u"] in (W4, TAB): print(line(r))
    Q = sorted([r for r in rows if r["ok"] and r["u"] not in (W4, TAB)], key=lambda r: -r["wo"])
    print(f"\n== QUALIFY: {len(Q)} of {len(rows)} wallets ==\n" + hdr)
    for r in Q: print(line(r))
    print("\n== the 10 nearest that do not qualify ==\n" + hdr)
    for r in sorted([r for r in rows if not r["ok"] and r["u"] not in (W4, TAB)], key=lambda r: -(r["both"] + (r["wo"] > 0)))[:10]: print(line(r))
    json.dump([{k: (v if k != "best" else list(map(str, v))) for k, v in r.items()} for r in Q], open(f"{O}/e7_qualify.json", "w"))
