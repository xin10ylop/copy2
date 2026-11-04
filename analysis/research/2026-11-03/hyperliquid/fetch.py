# Hyperliquid: the top N traders of the last 7 days (the public leaderboard, ranked by week PnL), then for each one its
# portfolio history, its current positions and its fills of the last DAYS days (newest first, paged back; the API
# keeps only a wallet's 10,000 newest fills, so a wallet that hits that cap is marked truncated).
#   python3 -I fetch.py DATA_DIR [N=100] [DAYS=30]
import json, os, sys, time, urllib.request

D = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 100; DAYS = int(sys.argv[3]) if len(sys.argv) > 3 else 30
API = "https://api.hyperliquid.xyz/info"
GAP = 1.1                                    # the info API allows 1,200 weight a minute; a full fills page weighs ~120
last = [0.0]

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
            print(f"  retry {body.get('type')} in {wait}s: {str(e)[:80]}", flush=True); time.sleep(wait)
    return None

lb = json.load(open(f"{D}/leaderboard.json"))["leaderboardRows"]
def win(r, w):
    return next((v for k, v in r["windowPerformances"] if k == w), {})
# traders only: the top of the board by PnL is mostly large holders (no volume, their holdings' price move); keep
# accounts that traded at least MIN_VLM this week, then rank by week PnL
MIN_VLM = float(os.environ.get("MIN_VLM", "1000000"))
lb = [r for r in lb if float(win(r, "week").get("vlm") or 0) >= MIN_VLM]
lb.sort(key=lambda r: -float(win(r, "week").get("pnl") or 0))
top = lb[:N]
json.dump(top, open(f"{D}/top.json", "w"))
for sub in ("port", "fills", "state"): os.makedirs(f"{D}/{sub}", exist_ok=True)
now = int(time.time() * 1000); start = now - DAYS * 86400 * 1000
for k, r in enumerate(top):
    a = r["ethAddress"]
    if os.path.exists(f"{D}/fills/{a}.json"): continue
    port = json.load(open(f"{D}/port/{a}.json")) if os.path.exists(f"{D}/port/{a}.json") else info({"type": "portfolio", "user": a})
    state = json.load(open(f"{D}/state/{a}.json")) if os.path.exists(f"{D}/state/{a}.json") else info({"type": "clearinghouseState", "user": a})
    # the API answers oldest first from the earliest of the wallet's 10,000 newest fills: page forward
    fills, s0, trunc = [], start, False
    for page in range(5):
        f = info({"type": "userFillsByTime", "user": a, "startTime": s0, "endTime": now, "aggregateByTime": True})
        if not f: break
        fills += f
        if len(f) < 2000: break
        s0 = max(x["time"] for x in f) + 1
    trunc = len(fills) >= 9990          # its 10,000 newest fills reach back less than the window
    json.dump(port, open(f"{D}/port/{a}.json", "w")); json.dump(state, open(f"{D}/state/{a}.json", "w"))
    json.dump({"address": a, "start": start, "now": now, "truncated": trunc, "fills": fills}, open(f"{D}/fills/{a}.json", "w"))
    span = (now - min(x["time"] for x in fills)) / 86400000 if fills else 0
    print(f"{k + 1:3d} {a} week {float(win(r, 'week').get('pnl') or 0):>14,.0f} fills {len(fills):5d} "
          f"{'TRUNCATED ' if trunc else ''}span {span:.1f} d", flush=True)
print("done", flush=True)
