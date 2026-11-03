# The whole leaderboard, not its top 100: accounts that trade (any market, crypto or the builder-deployed stocks and
# commodities), have made money over their life and this month, and are not market makers. Their portfolio histories
# are fetched for history.py and rank.py.
#   python3 -I scan.py DATA_DIR
import json, os, sys, time, urllib.request

D = sys.argv[1]; API = "https://api.hyperliquid.xyz/info"; GAP = 1.1; last = [0.0]
def info(body):
    for i in range(8):
        dt = time.time() - last[0]
        if dt < GAP: time.sleep(GAP - dt)
        last[0] = time.time()
        try:
            req = urllib.request.Request(API, json.dumps(body).encode(), {"Content-Type": "application/json"})
            return json.loads(urllib.request.urlopen(req, timeout=60).read())
        except Exception as e:
            wait = 15 * (i + 1) if "429" in str(e) else 3 * (i + 1)
            print(f"  retry in {wait}s: {str(e)[:60]}", flush=True); time.sleep(wait)
    return None
def w(r, k):
    v = dict(r["windowPerformances"]).get(k, {})
    return float(v.get("pnl") or 0), float(v.get("roi") or 0), float(v.get("vlm") or 0)
rows = json.load(open(f"{D}/leaderboard.json"))["leaderboardRows"]
c = [r for r in rows if float(r["accountValue"] or 0) >= 5e4 and w(r, "allTime")[0] >= 3e5 and w(r, "month")[0] > 0
     and w(r, "month")[2] >= 1e6 and w(r, "month")[2] / max(1.0, float(r["accountValue"])) <= 200]
c.sort(key=lambda r: -w(r, "allTime")[0])
json.dump(c, open(f"{D}/cands.json", "w"))
os.makedirs(f"{D}/port", exist_ok=True)
print(len(c), "candidates", flush=True)
for k, r in enumerate(c):
    a = r["ethAddress"]; f = f"{D}/port/{a}.json"
    if os.path.exists(f): continue
    p = info({"type": "portfolio", "user": a})
    if p is not None: json.dump(p, open(f, "w"))
    if (k + 1) % 50 == 0: print(f"{k + 1} fetched", flush=True)
print("done", flush=True)
