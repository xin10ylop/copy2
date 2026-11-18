# Market scan, the direct way (Nov 18; the owner: "find a tactic, an efficient and smart way to find wallet 4's ...
# directly find them"). No behaviour rule picks candidates first: EVERY wallet's first buys (0.5+ SOL, its first on the
# coin) on the live other-token coins of the 48 h get OUR COPY scored with wallet 4's live model (hunt_lib: landing 4 /
# 8 trades or the next slot, refused past 1.25x, tp 4.0, its sale followed 30-290 s under 1.5x, sell pressure, stall,
# 600 s, 0.5 SOL), the mean of the three landings. A wallet is FOUND when, with 6+ copies: our copy makes money on day 1
# AND on day 2 (halves by time), and without its best 2%, at 0.0345 SOL a round trip. Wallet 4 is the yardstick.
#   PATHS=paths_full python3 -I m4_direct.py SP > ../out/m4_direct.txt
import sys, os, json, gzip, collections, numpy as np
from multiprocessing import Pool
SP = sys.argv[1]; O = f"{SP}/market"; PD = f"{O}/{os.environ.get('PATHS', 'paths_full')}"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); import hunt_lib as H
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; ME = H.ME; WSOL = "So11111111111111111111111111111111111111112"
MINSOL = float(os.environ.get("MINSOL", 0.5)); MINC = int(os.environ.get("MINC", 6)); COST = 0.0345 - 0.0026   # the model already pays 0.0026
# LAUNCHES (Nov 18, the 4 days): comma-separated launch lists (launches.json and m1c_days.py's); FLOATQ=1 keeps the
# coins whose quote we hold as a float (the coins a copy can trade), the same universe on every day
FLOATS = ("3NZ9JMVB", "pumpCmXq", "SPCXxcqX", "TTWofwAg", "DJTu7vi8", "98sMhvDw", "XsbEhLAt"); L = {}
for f_ in os.environ.get("LAUNCHES", f"{O}/launches.json").split(","):
    L.update({m: x for m, x in json.load(open(f_)).items() if x and os.path.exists(f"{PD}/{m}.json.gz") and (os.environ.get("FLOATQ") != "1" or x["quote"][:8] in FLOATS)})
PR = json.load(open(f"{O}/prices.json")); sol_usd = PR[WSOL]["usdPrice"]
rate_of = lambda q: PR[q]["usdPrice"] / sol_usd * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None
def firsts(m):
    x = L[m]; rate = rate_of(x["quote"])
    if rate is None: return m, []
    try: tr = json.load(gzip.open(f"{PD}/{m}.json.gz"))
    except Exception: return m, []
    if not tr: return m, []
    seen = set(); out = []; t_end = tr[-1]["t"]
    for i, e in enumerate(tr):
        u = e["user"]
        if u in seen or u == ME: continue
        seen.add(u)
        if not e["buy"]: continue
        sol = e["q"] * (1 + e["bps"] / 1e4) * rate / 1e9
        if sol >= MINSOL and t_end - e["t"] >= 600: out.append((u, i, e["t"], sol))
    return m, out
def copies(job):
    m, buys = job; x = L[m]; rate = rate_of(x["quote"]); tr = json.load(gzip.open(f"{PD}/{m}.json.gz")); res = []
    for u, i, t, sol in buys:
        v = sum(H.model(H.prep(tr, i, rate, n))[0] for n in (4, 8, "slot+1")) / 3
        res.append((u, m, t, sol, v - COST, x["creator"], tr[i]["slot"] - x["slot"]))
    return res
if __name__ == "__main__":
    with Pool(8) as P: F = P.map(firsts, sorted(L), chunksize=20)
    cnt = collections.Counter(u for m, b in F for u, *_ in b)
    keep = {u for u, n in cnt.items() if n >= MINC} | {W4}
    jobs = [(m, [b for b in bs if b[0] in keep]) for m, bs in F]; jobs = [j for j in jobs if j[1]]
    print(f"{len(L)} coins with a path; {len(cnt)} wallets with a {MINSOL}+ SOL first buy; {len(keep)} with {MINC}+; copies to model: {sum(len(j[1]) for j in jobs)}", flush=True)
    with Pool(8) as P: R = [r for part in P.map(copies, jobs, chunksize=4) for r in part]
    ts = sorted(r[2] for r in R); tmid = ts[len(ts) // 2]
    W = collections.defaultdict(list)
    for r in R: W[r[0]].append(r)
    rows = []
    for u, v in W.items():
        a = np.array([r[4] for r in v]); n = len(a); k = max(1, round(0.02 * n)); s = np.sort(a)
        d1 = sum(r[4] for r in v if r[2] < tmid); d2 = sum(r[4] for r in v if r[2] >= tmid)
        rows.append(dict(u=u, n=n, net=a.sum(), wo=s[:-k].sum(), d1=d1, d2=d2, n1=sum(1 for r in v if r[2] < tmid), n2=sum(1 for r in v if r[2] >= tmid),
                         won=float(np.mean(a > 0)), cre=len({r[5] for r in v}), launch=float(np.mean([r[6] <= 1 for r in v])), size=float(np.median([r[3] for r in v])), a=a))
    found = [r for r in rows if r["n"] >= MINC and r["d1"] > 0 and r["d2"] > 0 and r["wo"] > 0 and r["n1"] >= 2 and r["n2"] >= 2]
    rng = np.random.default_rng(7)
    for r in found + [r for r in rows if r["u"] == W4]:
        r["boot"] = float(np.mean(rng.choice(r["a"], size=(10000, r["n"])).mean(axis=1) > 0))
    hdr = "wallet       copies | our copy net (a copy) | w/o best 2% | day 1 / day 2 (copies) | won | creators | at launch | size med | P(mean>0)"
    def line(r): return (f"{r['u'][:12]} {r['n']:5d} | {r['net']:+7.2f} ({100 * r['net'] / r['n'] / 0.5:+6.1f}%) | {r['wo']:+7.2f} | {r['d1']:+6.2f} ({r['n1']}) / {r['d2']:+6.2f} ({r['n2']}) |"
                         f" {100 * r['won']:3.0f}% | {r['cre']:4d} | {100 * r['launch']:3.0f}% | {r['size']:5.2f} | {100 * r.get('boot', 0):5.1f}%")
    big = [r for r in R if r[0] == W4 and r[3] >= 1.45]   # wallet 4's part A (its 1.45+ SOL buys): what the live bot copies
    if big:
        a = np.array([r[4] for r in big]); k = max(1, round(0.02 * len(a)))
        rows4 = dict(u=W4 + " 1.45+", n=len(a), net=a.sum(), wo=np.sort(a)[:-k].sum(), d1=sum(r[4] for r in big if r[2] < tmid), d2=sum(r[4] for r in big if r[2] >= tmid),
                     n1=sum(1 for r in big if r[2] < tmid), n2=sum(1 for r in big if r[2] >= tmid), won=float(np.mean(a > 0)), cre=len({r[5] for r in big}),
                     launch=float(np.mean([r[6] <= 1 for r in big])), size=float(np.median([r[3] for r in big])), boot=float(np.mean(rng.choice(a, size=(10000, len(a))).mean(axis=1) > 0)))
    print("\n== THE YARDSTICK: wallet 4, all its 0.5+ SOL buys, and its 1.45+ SOL buys (what the live bot copies) ==\n" + hdr)
    [print(line(r)) for r in rows if r["u"] == W4]
    if big: print(line(rows4))
    print(f"\n== FOUND: our copy positive on both days and without its best 2% ({len(found)} of {len(rows)} wallets), by w/o best 2% ==\n" + hdr)
    for r in sorted(found, key=lambda r: -r["wo"]): print(line(r))
    print(f"\n== for scale: the {len(rows)} wallets' copies pooled: {sum(r['net'] for r in rows):+.2f} SOL on {sum(r['n'] for r in rows)} copies")
    json.dump([dict((k, v) for k, v in r.items() if k != "a") for r in found], open(f"{O}/m4_found.json", "w"))
