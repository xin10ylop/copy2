# Winners first, step 7: the 7-day screen for selective pickers. Every graduated coin of the week (step 2's and step 6's
# paths), the copyable early buys as in step 3 (first buy, 0.25+ SOL, not the creator, 2+ slots after the create, under
# half the curve sold). Wallets with 3+ such hits from 3+ creators; for each, its landed transactions over the same days
# counted from its signatures alone (no transaction fetched): a selective picker has few. Ranked by hits per 100
# transactions (a buy and a sale are 2), the precision a busy bot cannot have. The top N go to step 4 (CANDS file).
# The RPC from RPC_URL, never printed.
#   RPC_URL=... python3 -I w7_week_screen.py SP [N=40] > out/w7_week_screen.txt
import sys, os, json, gzip, time, collections, statistics as st, urllib.request
from concurrent.futures import ThreadPoolExecutor
SP = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 40; W = f"{SP}/winners"
URL = os.environ["RPC_URL"]; INIT_REAL = 793_100_000_000_000; WSOL = "So11111111111111111111111111111111111111112"
SOLQ = {WSOL, "11111111111111111111111111111111", None, "?"}
PR = json.load(open(f"{SP}/market/prices.json")); sol_usd = PR[WSOL]["usdPrice"]
def call(m, p):
    for i in range(8):
        try:
            rq = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(rq, timeout=60))
            if "error" in r: raise RuntimeError("rpc error")
            return r["result"]
        except Exception: time.sleep(1.5 * (i + 1))
    return None
meta = {}
for v in json.load(open(f"{SP}/market/creates.json")).values():
    if v and v.get("mint"): meta[v["mint"]] = dict(slot=v["slot"], t=v["t"], creator=v.get("creator"), quote=v.get("quote"))
for m, v in json.load(open(f"{W}/week_meta.json")).items():
    if v and m not in meta: meta[m] = dict(v, quote=None)
grad = set(json.load(open(f"{W}/sample.json"))["grad"]) | {m for m, _ in json.load(open(f"{W}/week_migrations.json"))}
prog = lambda e: max(0.0, (INIT_REAL - e["real"]) / INIT_REAL)
B = collections.defaultdict(list); n = 0; tmin, tmax = 1e18, 0
for m in grad:
    f = f"{W}/paths/{m}.json.gz"
    if m not in meta or not os.path.exists(f): continue
    tr = json.load(gzip.open(f)); mt = meta[m]; n += 1
    if not tr: continue
    q = mt["quote"]
    if q is not None: rate = 1.0 if q in SOLQ else (PR[q]["usdPrice"] / sol_usd * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None)
    else:   # step 6's coins: a SOL curve starts at 30 SOL virtual (k / initial virtual tokens); others are left out
        rate = 1.0 if 25e9 < tr[0]["vq"] * tr[0]["vt"] / 1.073e15 < 35e9 else None
    if rate is None: continue
    seen = set(); pb = 0.0; tmin = min(tmin, mt["t"]); tmax = max(tmax, mt["t"])
    for e in tr:
        u = e["user"]
        if e["buy"] and u not in seen and u != mt["creator"] and e["slot"] - mt["slot"] >= 2 and pb < 0.5:
            sol = e["q"] * (1 + e["bps"] / 1e4) * rate / 1e9
            if sol >= 0.25: B[u].append(dict(m=m, t=e["t"], p=pb, sol=sol, cr=mt["creator"], dt=e["t"] - mt["t"]))
        seen.add(u); pb = prog(e)
cand = [(u, v) for u, v in B.items() if len(v) >= 3 and len({x["cr"] for x in v}) >= 3]
print(f"{n} graduated coins read (launched {time.strftime('%m-%d %H:%M', time.gmtime(tmin))} to {time.strftime('%m-%d %H:%M', time.gmtime(tmax))} UTC); "
      f"{len(B)} wallets with a copyable early buy on one; {len(cand)} with 3+ from 3+ creators")
def volume(u):
    c, before = 0, None
    for _ in range(20):
        pg = call("getSignaturesForAddress", [u, {"limit": 1000, **({"before": before} if before else {})}])
        if not pg: break
        c += sum(1 for s in pg if s["err"] is None and tmin <= (s.get("blockTime") or 0) <= tmax + 86400)
        before = pg[-1]["signature"]
        if len(pg) < 1000 or (pg[-1].get("blockTime") or 0) < tmin: break
    return c
with ThreadPoolExecutor(32) as ex: vol = dict(zip([u for u, _ in cand], ex.map(volume, [u for u, _ in cand])))
rows = sorted(({"u": u, "hits": len(v), "cr": len({x["cr"] for x in v}), "tx": vol[u], "per100": 100 * len(v) / max(vol[u], 1),
                "p": st.median(x["p"] for x in v), "dt": st.median(x["dt"] for x in v), "sol": st.median(x["sol"] for x in v),
                "days": len({x["t"] // 86400 for x in v})} for u, v in cand), key=lambda r: -r["per100"])
print("wallet   | hits creators days | its transactions in the days | hits per 100 transactions | entry p med, s after launch, SOL med")
for r in rows[:80]:
    print(f"{r['u'][:8]} | {r['hits']:3d} {r['cr']:3d} {r['days']:2d} | {r['tx']:6d} | {r['per100']:6.1f} | {r['p']:4.0%} {r['dt']:6.0f} s {r['sol']:5.2f}")
json.dump(rows, open(f"{W}/w7_rows.json", "w"))
json.dump([r["u"] for r in rows[:N]], open(f"{W}/w7_cands.json", "w"))
