# Step 2c: our copy of each candidate's OWN coins (routable, 0.9+ SOL, first buy of a coin, coins wallet 4 did not
# trade since Nov 3: the only ones that add trades). Each coin's path (cmodel.path: every curve trade from its buy
# slot, WIN s after it; cached in LK/paths) and the frozen live setup with the candidate as the leader (screen.py's
# model: landing 4 / 8 trades or the next slot after its buy, refused past 1.25x, tp 4.0, its sale followed 30-290 s
# under 1.5x, sell_pressure [5, 60, 30], stall 180 s, 600 s, 0.5 SOL, 0.3% a pool hop each way). At most CAP coins a
# wallet (a seeded random draw beyond that). The paths are fetched with RPC_URL (never printed).
#   RPC_URL=... LK=<dir> python3 -I step2_model.py SP CAP [WALLET8,...] > out/step2_model.txt
import sys, os, json, glob, random, datetime, bisect
from concurrent.futures import ThreadPoolExecutor
import numpy as np
SP, CAP = sys.argv[1], int(sys.argv[2]); ONLY = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
H = f"{SP}/hunt"; WIN = 720
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import hunt_lib as S0
rows = json.load(open(f"{H}/rows.json"))
def full_buy(w, r):
    for f in glob.glob(f"{H}/tx/{w[:8]}/{r['slot']}_*.json"):
        tx = json.load(open(f))
        for k in tx["meta"].get("postTokenBalances") or []:
            if k["mint"].startswith(r["m8"]):
                ev = [e for e in M.trades(tx, k["mint"]) if e["user"] == w and e["buy"]]
                if ev: return k["mint"]
    return None
plan = []
for w, R in rows.items():
    if ONLY and w[:8] not in ONLY: continue
    first = {}
    for r in sorted(R, key=lambda r: r["t"]): first.setdefault(r["m8"], r)
    B = [r for r in first.values() if r["routable"] and r["w4"] == "no" and r["sol"] >= 0.9]
    if len(B) > CAP: B = random.Random(7).sample(B, CAP)
    sigs = sorted(json.load(open(f"{H}/tx/{w[:8]}_sigs.json"))[:6000], key=lambda s: s[2]); T = [s[2] for s in sigs]
    for r in B:
        i = bisect.bisect_left(T, r["t"] + WIN)
        if i >= len(sigs): continue
        plan.append((w, r, sigs[i][0]))
print(f"{len(plan)} coins to model", flush=True)
def get(x):
    w, r, anchor = x
    m = full_buy(w, r)
    if not m: return None
    if os.environ.get("NOFETCH") and not os.path.exists(f"{M.PC}/{r['slot']}_{m}.json.gz"): return None   # a read of what is fetched so far
    try: tr = M.path(m, r["slot"], anchor, threads=16)
    except Exception as e: return None
    k = next((i for i, e in enumerate(tr) if e["user"] == w and e["buy"] and e["slot"] == r["slot"]), None)
    if k is None: return None
    e = tr[k]; rate = r["sol"] * 1e9 / (e["q"] * (1 + e["bps"] / 1e4)); hopf = 0.997 ** (r["hops"] - 1)
    res, res2 = [], []
    for n in (4, 8, "slot+1"):
        p = S0.prep(tr, k, rate, n); p["hopf"] = hopf                       # a pool hop: 0.3% each way
        res.append(S0.model(p)); res2.append(S0.model(p, early=None))         # its sale never followed (TAB16RxX's lesson)
    nxt = next((x for x in tr[k + 1:] if x["user"] == w and not x["buy"]), None)
    return dict(w=w, m=m, t=r["t"], sol=r["sol"], frm=r["frm"][:8], hops=r["hops"], net=sum(q[0] for q in res) / 3, net2=sum(q[0] for q in res2) / 3, why=res[0][1],
                held=(nxt["t"] - e["t"]) if nxt else None)
with ThreadPoolExecutor(8) as ex: got = [g for g in ex.map(get, plan) if g]
if not os.environ.get("NOFETCH"): json.dump(got, open(f"{H}/step2_copies.json", "w"))
f = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d")
print("wallet   | its own coins modelled | our copy: net SOL, a copy, won, tp | w/o best 5 | first half / second half | its sale never followed: net, w/o best 5 | held med | sizes med")
by = {}
for g in got: by.setdefault(g["w"], []).append(g)
for w, v in sorted(by.items(), key=lambda x: -sum(g["net"] for g in x[1])):
    v.sort(key=lambda g: g["t"]); nets = sorted((g["net"] for g in v), reverse=True); h = len(v) // 2
    c = [g for g in v if g["why"] != "refused"]; held = [g["held"] for g in v if g["held"] is not None]
    print(f"{w[:8]} | {len(v):3d} ({f(v[0]['t'])} to {f(v[-1]['t'])}) | {sum(nets):+6.2f} SOL {100 * sum(nets) / max(1, len(c)) / 0.5:+6.1f}%, won {100 * sum(1 for g in c if g['net'] > 0) / max(1, len(c)):3.0f}%,"
          f" tp {sum(1 for g in c if g['why'] == 'tp')} | {sum(nets[5:]):+6.2f} | {sum(g['net'] for g in v[:h]):+5.2f} / {sum(g['net'] for g in v[h:]):+5.2f} |"
          f" {sum(g['net2'] for g in v):+6.2f}, {sum(sorted((g['net2'] for g in v), reverse=True)[5:]):+6.2f} |"
          f" {np.median(held) if held else 0:5.0f} s | {np.median([g['sol'] for g in v]):4.2f}")
