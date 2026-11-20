# The sell-pressure audit's data (Nov 20; the owner: "you sure sell pressure is the most optimal? audit it"): every coin
# wallet 4 opened since the exit was frozen (Nov 15 19:29 UTC) with a first buy of 1.3+ SOL on a token-quoted curve (what
# the bot copies; its value at the quote token's Jupiter rate on Nov 20 ~21:00 UTC), the coin's every trade from its buy
# slot to 31 minutes after (tab_exits/cmodel.path: block order for its slot and the next two). Its history from
# candidates/c1_fetch.py (SUB=w4since, 5.15 days). RPC from RPC_URL (never printed); paths cached under LK/paths.
#   RPC_URL=... LK=SP/lk python3 -I f1_paths.py SP > out/f1_paths.txt
import sys, os, json, time, datetime as dt, concurrent.futures as cf
SP = sys.argv[1]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; SOLM = "So11111111111111111111111111111111111111112"
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M
FREEZE = dt.datetime(2026, 11, 15, 19, 29, tzinfo=dt.UTC).timestamp()
P = json.load(open(f"{SP}/w4since/prices.json")); su = P[SOLM]["usdPrice"]
lam = lambda q, quote: q * P[quote]["usdPrice"] / su * 1e9 / 10 ** P[quote]["decimals"] if quote in P else None
sigs = sorted((t, s) for s, t in json.load(open(f"{SP}/w4since/H9kuqGKN_sigs.json")))
first = {}
for l in open(f"{SP}/w4since/H9kuqGKN_trades.jsonl"):
    for e in (json.loads(l)["trades"] or []):
        if e["m"] not in first or (e["slot"], not e["buy"]) < (first[e["m"]]["slot"], not first[e["m"]]["buy"]): first[e["m"]] = e
now = max(t for t, _ in sigs)
coins = []
for m, e in first.items():
    if not e["buy"] or not e["quote"] or e["quote"].startswith("1111") or e["t"] < FREEZE or e["t"] > now - 1900: continue
    v = lam(e["q"], e["quote"])
    if v is None or v < 1.3e9: continue
    anchor = next(s for t, s in sigs if t >= e["t"] + 1890)
    coins.append(dict(m=m, slot=e["slot"], t=e["t"], quote=e["quote"], its_q=e["q"], its_sol=v / 1e9, rate=v / e["q"], anchor=anchor))
coins.sort(key=lambda c: c["t"]); json.dump(coins, open(f"{SP}/w4since/coins.json", "w"))
print(f"{len(coins)} coins, {dt.datetime.fromtimestamp(coins[0]['t'], dt.UTC):%m-%d %H:%M} to {dt.datetime.fromtimestamp(coins[-1]['t'], dt.UTC):%m-%d %H:%M} UTC", flush=True)
def one(c):
    try: tr = M.path(c["m"], c["slot"], c["anchor"], threads=12); return c["m"], len(tr)
    except Exception as x: return c["m"], f"error {type(x).__name__}"
t0 = time.time()
with cf.ThreadPoolExecutor(3) as ex:
    for i, (m, n) in enumerate(ex.map(one, coins)):
        print(f"{i + 1}/{len(coins)} {m[:8]} {n} trades ({time.time() - t0:.0f} s)", flush=True)
