# Two weeks of one wallet, fast (Nov 21; the owner: "take the best wallet in the recorder for now and do a 2 week
# backtest, unseen, seen, the whole process, fast"). Its history (candidates/c1_fetch.py, SUB=cand_<w8>, 14 days), its
# first buys of 0.5+ SOL (non-SOL quotes at Jupiter's price now), at most MAXC of them at random (seed 7), and each coin's
# trades for 31 minutes from its buy (tab_exits/cmodel.path). RPC from RPC_URL, never printed.
#   RPC_URL=... LK=SP/lk python3 -I b1_paths.py SP WALLET [MAXC=350] > out/b1_<w8>.txt
import sys, os, json, time, random, urllib.request, concurrent.futures as cf
SP, W = sys.argv[1], sys.argv[2]; MAXC = int(sys.argv[3]) if len(sys.argv) > 3 else 350; D = f"{SP}/cand_{W[:8]}"
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M
SOLM = "So11111111111111111111111111111111111111112"
sigs = sorted((t, s) for s, t in json.load(open(f"{D}/{W[:8]}_sigs.json"))); now = max(t for t, _ in sigs)
first = {}
for l in open(f"{D}/{W[:8]}_trades.jsonl"):
    for e in (json.loads(l)["trades"] or []):
        if e["m"] not in first or (e["slot"], not e["buy"]) < (first[e["m"]]["slot"], not first[e["m"]]["buy"]): first[e["m"]] = e
q = sorted({e["quote"] for e in first.values() if e["quote"] and not e["quote"].startswith("1111")}); P = {}
for i in range(0, len(q), 40):
    try: P.update({k: v for k, v in json.load(urllib.request.urlopen("https://lite-api.jup.ag/price/v3?ids=" + ",".join(q[i:i + 40] + [SOLM]), timeout=20)).items() if v})
    except Exception as x: print("prices:", type(x).__name__)
su = P[SOLM]["usdPrice"]
coins = []
for m, e in first.items():
    if not e["buy"] or e["t"] > now - 1900: continue
    sol = not e["quote"] or e["quote"].startswith("1111")
    rate = 1.0 if sol else (P[e["quote"]]["usdPrice"] / su * 1e9 / 10 ** P[e["quote"]]["decimals"] if e["quote"] in P else None)
    if rate is None or e["q"] * rate / 1e9 < 0.5: continue
    coins.append(dict(m=m, slot=e["slot"], t=e["t"], quote=e["quote"], sol=not e["quote"] or e["quote"].startswith("1111"), its_sol=e["q"] * rate / 1e9,
                      rate=rate, anchor=next((s for t, s in sigs if t >= e["t"] + 1890), sigs[-1][1])))
n_all = len(coins); random.seed(7); coins = sorted(random.sample(coins, min(MAXC, len(coins))), key=lambda c: c["t"])
json.dump(coins, open(f"{D}/coins.json", "w")); print(f"{W[:8]}: {n_all} first buys of 0.5+ SOL in 14 days, {len(coins)} taken", flush=True)
def one(c):
    try: return len(M.path(c["m"], c["slot"], c["anchor"], threads=10))
    except Exception as x: return f"error {type(x).__name__}"
t0 = time.time()
with cf.ThreadPoolExecutor(8) as ex:
    for i, n in enumerate(ex.map(one, coins)):
        if (i + 1) % 25 == 0 or i + 1 == len(coins): print(f"{i + 1}/{len(coins)} ({time.time() - t0:.0f} s)", flush=True)
