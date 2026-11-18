# The exit and filter engineering on the market paths, the way wallet 4's was built (Nov 18, the owner: "test exit
# after its sell, then filters, hold time, tp, sell pressure, stall, sell after its sell, exactly like we engineered for
# wallet 4, also which coins to copy and buy size"). No new fetch: the 4 days of float-quote launches (paths_full).
# For each wallet with 12+ copies (its first buy of a coin, 0.5+ SOL), every copy (our 0.5 SOL at the landings 4 / 8
# trades / next slot, averaged) under e1_exits' 23 exits (its sale; time 30-600 s; tp 1.2-4x from our entry; sell
# pressure 3/30, 5/60, 10/60; stall 60-180 s; its sale + tp / + sell pressure; sell pressure + stall + tp 4x; wallet 4's
# live model), x coins (all floats, or one quote token) x its buy size (0.5+ / 1.0+ / 1.3+ / 2.0+ SOL). Picked on days
# 1-2 (8+ copies), scored once on days 3-4: positive, positive without the best 2%, bootstrap. Wallet 4 is run the same way.
#   python3 -I e2_market_exits.py SP LAUNCHES,... > ../out/e2_market_exits.txt
import sys, os, json, gzip, collections, numpy as np
from multiprocessing import Pool
SP = sys.argv[1]; LISTS = sys.argv[2].split(","); O = f"{SP}/market"; PD = f"{O}/paths_full"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); import hunt_lib as H
here = "/home/user/copy2/analysis/research/2026-11-17/winners"; ws = open(f"{here}/wallet_study.py").read()
ns = {"H": H, "np": np}; exec(ws[ws.index("def sim("):ws.index("def menu(")], ns); sim = ns["sim"]
e1 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "e1_exits.py")).read()
g = dict(ns, COST=0.0345 - 0.0026); exec(e1[e1.index("def stall_mask("):e1.index("def S(v):")], g); exits = g["exits"]   # one namespace: exits() finds stall_mask, sim
NAMES = eval(e1[e1.index("NAMES = ") + 8:e1.index("   # the menu, in its declared order")])
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; ME = H.ME; WSOL = "So11111111111111111111111111111111111111112"
FLOATS = ("3NZ9JMVB", "pumpCmXq", "SPCXxcqX", "TTWofwAg", "DJTu7vi8", "98sMhvDw", "XsbEhLAt"); MINC = int(os.environ.get("MINC", 12))
L = {}
for f_ in LISTS: L.update({m: x for m, x in json.load(open(f_)).items() if x and x["quote"][:8] in FLOATS and os.path.exists(f"{PD}/{m}.json.gz")})
PR = json.load(open(f"{O}/prices.json")); sol_usd = PR[WSOL]["usdPrice"]
rate_of = lambda q: PR[q]["usdPrice"] / sol_usd * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None
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
        if e["buy"] and e["q"] * (1 + e["bps"] / 1e4) * r / 1e9 >= 0.5 and tr[-1]["t"] - e["t"] >= 600: out.append((u, m, i))
    return out
def copies(job):
    m, items = job; x = L[m]; r = rate_of(x["quote"]); tr = json.load(gzip.open(f"{PD}/{m}.json.gz")); out = []
    for u, i in items:
        acc = {k: 0.0 for k in NAMES}; sol = tr[i]["q"] * (1 + tr[i]["bps"] / 1e4) * r / 1e9
        for n in (4, 8, "slot+1"):
            p = H.prep(tr, i, r, n)
            if p["refused"] or not len(p["px"]): ex = {k: -0.0004 for k in NAMES}
            else: ex = exits(p, (tr[i]["vt"] / p["ent"][0]) ** 2)
            for k in NAMES: acc[k] += ex[k] / 3
        out.append((u, dict(t=tr[i]["t"], q=x["quote"][:8], sol=sol, ex=acc)))
    return out
def S(v):
    v = np.array(v); n = len(v)
    if not n: return "   0"
    s = np.sort(v); k = max(1, round(0.02 * n)); return f"{n:4d} {v.sum():+7.2f} ({100 * v.mean() / 0.5:+6.1f}%) w/o 2% {s[:-k].sum() if n > 1 else 0:+7.2f}"
if __name__ == "__main__":
    with Pool(8) as P: F = [b for part in P.map(firsts, sorted(L), chunksize=20) for b in part]
    cnt = collections.Counter(u for u, m, i in F); keep = {u for u, n in cnt.items() if n >= MINC} | {W4}
    jobs = collections.defaultdict(list)
    for u, m, i in F:
        if u in keep: jobs[m].append((u, i))
    with Pool(8) as P: R = [z for part in P.map(copies, list(jobs.items()), chunksize=4) for z in part]
    tmid = np.median([d["t"] for u, d in R]); W = collections.defaultdict(list)
    for u, d in R: W[u].append(d)
    print(f"{len(L)} float-quote coins over the 4 days; {len(keep) - 1} wallets with {MINC}+ copies (+ wallet 4); days 1-2 / 3-4 split at the median time")
    best = []
    for u, v in W.items():
        D1 = [d for d in v if d["t"] < tmid]; D2 = [d for d in v if d["t"] >= tmid]
        quotes = ["all"] + [q for q, c in collections.Counter(d["q"] for d in D1).items() if c >= 8]
        opts = []
        for q in quotes:
            for mn in (0.5, 1.0, 1.3, 2.0):
                a1 = [d for d in D1 if (q == "all" or d["q"] == q) and d["sol"] >= mn]; a2 = [d for d in D2 if (q == "all" or d["q"] == q) and d["sol"] >= mn]
                if len(a1) < 8 or len(a2) < 5: continue
                for e_ in NAMES: opts.append((np.mean([d["ex"][e_] for d in a1]), q, mn, e_, a1, a2))
        if not opts: continue
        o = max(opts, key=lambda z: z[0]); v2 = np.array([d["ex"][o[3]] for d in o[5]]); k2 = max(1, round(0.02 * len(v2)))
        boot = float(np.mean(np.random.default_rng(7).choice(v2, size=(5000, len(v2))).mean(axis=1) > 0))
        best.append(dict(u=u, n=len(v), q=o[1], mn=o[2], e=o[3], d1=S([d["ex"][o[3]] for d in o[4]]), d2=S(v2), ok=v2.sum() > 0 and np.sort(v2)[:-k2].sum() > 0 and boot >= 0.95,
                         boot=boot, s2=v2.sum(), its=S([d["ex"]["its sale"] for d in D2]), live=S([d["ex"]["wallet 4's live model"] for d in D2])))
    # ONLY=prefix,... (Nov 18): the full table for some wallets: every exit on all its copies, days 1-2 against 3-4, and
    # the size and coin filters under the two exits that matter (wallet 4's live model, its sale)
    for u in [u for u in W if any(u.startswith(x) for x in os.environ.get("ONLY", "").split(",") if x)]:
        v = W[u]; D1 = [d for d in v if d["t"] < tmid]; D2 = [d for d in v if d["t"] >= tmid]
        print(f"\n== {u}: {len(v)} copies (days 1-2 {len(D1)}, days 3-4 {len(D2)}) ==")
        for e_ in NAMES: print(f"   {e_:40s} | days 1-2 {S([d['ex'][e_] for d in D1])} | days 3-4 {S([d['ex'][e_] for d in D2])}")
        for e_ in ("wallet 4's live model", "its sale"):
            for q in ["all"] + sorted({d["q"] for d in v}):
                for mn in (0.5, 1.0, 1.3, 2.0):
                    a1 = [d for d in D1 if (q == "all" or d["q"] == q) and d["sol"] >= mn]; a2 = [d for d in D2 if (q == "all" or d["q"] == q) and d["sol"] >= mn]
                    if len(a1) + len(a2) >= 10: print(f"   [{e_}] coins {q:9s} its {mn}+ SOL | days 1-2 {S([d['ex'][e_] for d in a1])} | days 3-4 {S([d['ex'][e_] for d in a2])}")
    w4 = [b for b in best if b["u"] == W4]
    print("\n== WALLET 4 (the yardstick), engineered the same way ==")
    for b in w4: print(f"   picked: coins {b['q']}, its {b['mn']}+ SOL, {b['e']} | days 1-2 {b['d1']} | days 3-4 {b['d2']}; P {100 * b['boot']:.0f}% | days 3-4 its sale {b['its']} | live model {b['live']}")
    P_ = sorted([b for b in best if b["ok"] and b["u"] != W4], key=lambda b: -b["s2"])
    print(f"\n== PASS on days 3-4 (positive, w/o 2% positive, P >= 95%): {len(P_)} of {len(best) - len(w4)} wallets ==")
    for b in P_: print(f"   {b['u']} ({b['n']} copies): coins {b['q']}, its {b['mn']}+ SOL, {b['e']} | days 1-2 {b['d1']} | days 3-4 {b['d2']}; P {100 * b['boot']:.0f}%")
    print("\n== the 15 best days-3-4 results that did not pass, for scale ==")
    for b in sorted([b for b in best if not b["ok"] and b["u"] != W4], key=lambda b: -b["s2"])[:15]:
        print(f"   {b['u'][:12]} ({b['n']}): {b['q']}, {b['mn']}+, {b['e']} | days 3-4 {b['d2']}; P {100 * b['boot']:.0f}%")
    json.dump([{k: v for k, v in b.items()} for b in P_], open(f"{O}/e2_pass.json", "w"))
