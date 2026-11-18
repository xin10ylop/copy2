# The consensus money test (PREREG_consensus.md). Paths: w5_copy's cpath from the first picker's buy slot, HOLD s on.
#   RPC_URL=... HOLD=600 python3 -I k3_money.py SP [prefetch] > out/k3_money.txt
import sys, os, json, glob, time, random, collections, numpy as np
from concurrent.futures import ThreadPoolExecutor
SP = sys.argv[1]; PRE = len(sys.argv) > 2; os.environ.setdefault("HOLD", "600"); A, B = 1794790020, 1794877620; NOW = time.time()
here = "/home/user/copy2/analysis/research/2026-11-17/winners"; src = open(f"{here}/w5_copy.py").read().split("EX = [")[0]
sys.argv = ["x", SP, "6ua7w2Gv"]; ns = {"__file__": f"{here}/w5_copy.py"}; exec(compile(src, "w5_copy.py", "exec"), ns); cpath = ns["cpath"]
SKIP = {"H9kuqGKN", "4sgdNABj", "AsDCYFPT", "8QzUkGJi", "B4BMZH3T", "HbovEh3L", "64Dn57gX", "H2nsBdjF", "EhS8bGVC", "Gf9gk8sZ", "DHLAr4dH", "91Wu2yN6", "G8hmNBej", "7zvP2xFF"}
buys = collections.defaultdict(list)
for f in glob.glob(f"{SP}/winners/hist/*.json"):
    w = os.path.basename(f)[:8]
    if w in SKIP: continue
    try: T = json.load(open(f))["trades"]
    except Exception: continue
    first = {}
    for e in sorted(T, key=lambda e: e["t"]):
        if e["buy"] and e["m"].endswith("pump"): first.setdefault(e["m"], e)
    for m, e in first.items():
        if not (A <= e["t"] < B) and NOW - e["t"] > 7200 and (e.get("quote") or "1111")[:4] in ("1111", "So11"): buys[m].append(e)
C = []
for m, v in buys.items():
    v.sort(key=lambda e: e["t"]); t0 = v[0]["t"]; ws, es = [], []
    for e in v:
        w = e.get("user") or id(e)
        if e["t"] - t0 <= 300 and not any(x is e for x in es): es.append(e)
    n = len(es)
    if n >= 4: C.append((m, es))
before = [c for c in C if c[1][0]["t"] < A]; after = [c for c in C if c[1][0]["t"] >= B]
b6 = [c for c in before if len(c[1]) >= 6]; b45 = [c for c in before if len(c[1]) < 6]; random.Random(7).shuffle(b45)
SEL = b6 + b45[:600] + after
print(f"coins with 4+ pickers: before {len(before)} (6+: {len(b6)}), after {len(after)}; modelled {len(SEL)}", flush=True)
def get(c):
    m, es = c
    try: return m, es, cpath(m, es[0]["slot"], es[0]["t"])
    except Exception: return m, es, None
order = SEL[::-1] if PRE else SEL
with ThreadPoolExecutor(8) as ex: D = [x for x in ex.map(get, order) if x[2]]
if PRE: print("prefetched", len(D)); sys.exit()
def trade(tr, es, k, tpo, cap):
    sk = es[k - 1]["slot"]; i = next((j for j, e in enumerate(tr) if e["slot"] > sk), None)
    if i is None: return None
    a = tr[i]; fee = 0.0125; tok = 0.5e9 * (1 - fee) * a["vt"] / (a["vq"] + 0.5e9); p0 = a["vq"] / a["vt"]
    j_out = len(tr) - 1
    for j in range(i + 1, len(tr)):
        e = tr[j]
        if e.get("real") == 0 or (tpo == "next") or (tpo and e["vq"] / e["vt"] >= tpo * p0) or e["t"] - a["t"] >= cap: j_out = j; break
    b = tr[j_out]; out = b["vq"] - b["vq"] * b["vt"] / (b["vt"] + tok); return out * (1 - fee) / 1e9 - 0.5 - 0.0345
EXITS = [("next", 600)] + [(tp, cap) for tp in (1.2, 1.5, 2, 3) for cap in (60, 300, 600)] + [(None, c) for c in (60, 300, 600)]
def S(v):
    v = np.array(v)
    if not len(v): return "   0"
    s = np.sort(v); kk = max(1, round(0.02 * len(v))); return f"{len(v):4d} {v.sum():+7.2f} ({100 * v.mean() / 0.5:+6.1f}%) w/o 2% {s[:-kk].sum():+7.2f}"
best = None
for k in (4, 6, 9):
    for tpo, cap in EXITS:
        bv = [x for m, es, tr in D if es[0]["t"] < A and len(es) >= k for x in [trade(tr, es, k, tpo, cap)] if x is not None]
        av = [x for m, es, tr in D if es[0]["t"] >= B and len(es) >= k for x in [trade(tr, es, k, tpo, cap)] if x is not None]
        print(f"   k={k} exit={str(tpo):4s} cap={cap:3d}: Nov 3-14 {S(bv)} | Nov 17 on {S(av)}")
        if len(bv) >= 30 and (best is None or np.mean(bv) > best[0]): best = (np.mean(bv), k, tpo, cap, av)
_, k, tpo, cap, av = best; v = np.array(av); bs = np.random.default_rng(7).choice(v, size=(10000, len(v))).mean(axis=1) if len(v) else np.array([0])
print(f"\nPICKED on Nov 3-14: k={k} exit={tpo} cap={cap} -> Nov 17 on {S(av)}; P(mean > 0) {np.mean(bs > 0):.1%}")
print(f"PASS: {len(v) >= 30 and v.sum() > 0 and np.sort(v)[:-max(1, round(0.02 * len(v)))].sum() > 0 and np.mean(bs > 0) >= 0.95}")
