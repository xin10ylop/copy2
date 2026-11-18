# The crew trade (PREREG_crew.md): each crew coin with k+ crew wallets within 120 s; its curve trades from the first crew
# buy's slot, HOLD s on (w5_copy's cpath, cached); the trade under each grid setting; picked on export 1, scored on export 2.
#   RPC_URL=... HOLD=600 python3 -I c2_money.py SP > out/c2_money.txt
import sys, os, json, glob, numpy as np
from concurrent.futures import ThreadPoolExecutor
SP = sys.argv[1]; os.environ.setdefault("HOLD", "600")
here = "/home/user/copy2/analysis/research/2026-11-17/winners"; src = open(f"{here}/w5_copy.py").read().split("EX = [")[0]
sys.argv = ["x", SP, "6ua7w2Gv"]; ns = {"__file__": f"{here}/w5_copy.py"}; exec(compile(src, "w5_copy.py", "exec"), ns); cpath = ns["cpath"]
CREW = ["6ua7w2Gv", "q2q38wAb", "q2jJy82z", "7777P2fk", "GKd5EMzR", "6Z91Dgiz", "6anjqMeW", "2NUMEzNh"]
full = {}; first = {}
for w in CREW:
    f = glob.glob(f"{SP}/winners/hist/{w}*.json")[0]; full[w] = os.path.basename(f)[:8]
    for e in sorted(json.load(open(f))["trades"], key=lambda e: e["t"]):
        if e["buy"]: first.setdefault((e["m"], w), e)
rows = json.load(open(f"{SP}/crew_rows.json")); VIP = {}
for f in (f"{SP}/tg/vip/meta.json", f"{SP}/tg/vip2/meta.json"):
    for m, v in json.load(open(f)).items(): VIP.setdefault(m, v["t"])
EXP1 = (1793404800, 1794009600)   # Oct 31 00:00 - Nov 7 00:00 UTC
C = [r for r in rows if r["n"] >= 3]   # narrowed before any path was read (PREREG)
def one(r):
    es = sorted((first[(r["m"], w)] for w in r["crew"]), key=lambda e: e["t"]); e0 = es[0]
    if (e0.get("quote") or "1111")[:4] not in ("1111", "So11"): return None   # SOL curves only
    try: tr = cpath(r["m"], e0["slot"], e0["t"])
    except Exception: return None
    return r, es, tr
def val(tr, i_in, i_out):
    a, b = tr[i_in], tr[i_out]; fee = 0.0125
    tok = 0.5 * 1e9 * (1 - fee) * a["vt"] / (a["vq"] + 0.5e9)   # tokens for 0.5 SOL at the entry reserves (constant product)
    out = b["vq"] - b["vq"] * b["vt"] / (b["vt"] + tok); return out * (1 - fee) / 1e9 - 0.5 - 0.0345
with ThreadPoolExecutor(8) as ex: D = [x for x in ex.map(one, C) if x]
grid = [(k, d, cap) for k in (3, 4) for d in (0, 15, 30) for cap in (90, 120, 180)]
res = {g: [] for g in grid}
for r, es, tr in D:
    if not tr: continue
    t0 = es[0]["t"]; a = VIP.get(r["m"]); a = a if a and 0 < a - t0 <= 600 else None
    for k, d, cap in grid:
        if len(es) < k or es[k - 1]["t"] - t0 > 120: continue
        sk = es[k - 1]["slot"]; i_in = next((i for i, e in enumerate(tr) if e["slot"] > sk), None)
        if i_in is None: continue
        t_out = (a + d) if (a and a + d - t0 <= cap + d and a - t0 <= cap) else t0 + cap
        i_out = next((i for i in range(i_in + 1, len(tr)) if tr[i]["t"] >= t_out or tr[i].get("real") == 0), len(tr) - 1)
        res[(k, d, cap)].append((r["t"], val(tr, i_in, i_out), bool(a)))
def S(v):
    v = np.array(v); 
    if not len(v): return "  0"
    s = np.sort(v); kk = max(1, round(0.02 * len(v))); return f"{len(v):4d} {v.sum():+7.2f} ({100 * v.mean() / 0.5:+6.1f}%) w/o 2% {s[:-kk].sum():+7.2f}"
print(f"{len(D)} crew coins (2+ wallets) with a path; export 1 picks, export 2 scores")
best = None
for g in grid:
    e1 = [x for t, x, _ in res[g] if EXP1[0] <= t < EXP1[1]]; e2 = [x for t, x, _ in res[g] if t >= EXP1[1]]
    print(f"   k={g[0]} d={g[1]:2d} cap={g[2]:3d}: export 1 {S(e1)} | export 2 {S(e2)}")
    if e1 and (best is None or np.mean(e1) > best[0]): best = (np.mean(e1), g)
g = best[1]; v = np.array([x for t, x, _ in res[g] if t >= EXP1[1]])
bs = np.random.default_rng(7).choice(v, size=(10000, len(v))).mean(axis=1)
print(f"\nPICKED on export 1: k={g[0]} d={g[1]} cap={g[2]} -> export 2 {S(list(v))}; P(mean > 0) {np.mean(bs > 0):.1%}")
print(f"PASS: {len(v) >= 40 and v.sum() > 0 and np.sort(v)[:-max(1, round(0.02 * len(v)))].sum() > 0 and np.mean(bs > 0) >= 0.95}")
