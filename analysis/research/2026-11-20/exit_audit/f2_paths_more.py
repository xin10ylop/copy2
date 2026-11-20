# "If he is profitable on all of it, why don't we copy him on more?" (Nov 20). Since the freeze (Nov 15 19:29 UTC) wallet
# 4 opened 3,422 coins; the bot copies its token-coin buys of 1.3+ SOL (149). The rest by kind: token coins 0.5-1.3 SOL
# 728, SOL coins 1.3+ 118, SOL coins 0.5-1.3 609 (smaller ones left out: at 0.2-0.5 SOL its buy hardly moves the curve).
# Paths as f1_paths.py: SOL coins 1.3+ all, the two 0.5-1.3 kinds a random sample of 150 each (seed 7).
#   RPC_URL=... LK=SP/lk python3 -I f2_paths_more.py SP > out/f2_paths_more.txt
import sys, os, json, time, random, datetime as dt, concurrent.futures as cf
SP = sys.argv[1]; SOLM = "So11111111111111111111111111111111111111112"
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M
FREEZE = dt.datetime(2026, 11, 15, 19, 29, tzinfo=dt.UTC).timestamp()
P = json.load(open(f"{SP}/w4since/prices.json")); su = P[SOLM]["usdPrice"]
sigs = sorted((t, s) for s, t in json.load(open(f"{SP}/w4since/H9kuqGKN_sigs.json"))); now = max(t for t, _ in sigs)
first = {}
for l in open(f"{SP}/w4since/H9kuqGKN_trades.jsonl"):
    for e in (json.loads(l)["trades"] or []):
        if e["m"] not in first or (e["slot"], not e["buy"]) < (first[e["m"]]["slot"], not first[e["m"]]["buy"]): first[e["m"]] = e
cats = {"token 0.5-1.3": [], "SOL 1.3+": [], "SOL 0.5-1.3": []}
for m, e in sorted(first.items()):
    if not e["buy"] or e["t"] < FREEZE or e["t"] > now - 1900: continue
    sol = not e["quote"] or e["quote"].startswith("1111")
    rate = 1.0 if sol else (P[e["quote"]]["usdPrice"] / su * 1e9 / 10 ** P[e["quote"]]["decimals"] if e["quote"] in P else None)
    if rate is None: continue
    v = e["q"] * rate / 1e9
    k = ("SOL " if sol else "token ") + ("1.3+" if v >= 1.3 else "0.5-1.3" if v >= 0.5 else "")
    if k in cats: cats[k].append(dict(m=m, slot=e["slot"], t=e["t"], quote=e["quote"], its_q=e["q"], its_sol=v, rate=rate, cat=k,
                                       anchor=next(s for t, s in sigs if t >= e["t"] + 1890)))
random.seed(7); coins = []
for k, v in cats.items(): coins += v if k == "SOL 1.3+" else random.sample(v, min(150, len(v)))
coins.sort(key=lambda c: c["t"]); json.dump(coins, open(f"{SP}/w4since/coins_more.json", "w"))
print({k: len(v) for k, v in cats.items()}, "->", len(coins), "coins", flush=True)
def one(c):
    try: return c["m"], len(M.path(c["m"], c["slot"], c["anchor"], threads=10))
    except Exception as x: return c["m"], f"error {type(x).__name__}"
t0 = time.time()
with cf.ThreadPoolExecutor(6) as ex:
    for i, (m, n) in enumerate(ex.map(one, coins)):
        print(f"{i + 1}/{len(coins)} {m[:8]} {n} ({time.time() - t0:.0f} s)", flush=True)
