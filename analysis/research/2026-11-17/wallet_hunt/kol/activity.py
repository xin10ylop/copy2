# The kolscan.io leaderboard (fetched Nov 17 ~01:05 UTC, kol/leaderboard_nov17.json: 143 rows, 1 / 7 / 30-day SOL
# profit, wins, losses) -> each wallet's newest 1,000 signatures: how busy it is now and since when. A wallet idle for
# a day or doing thousands of transactions an hour is noted; the next step fetches the transactions of the rest.
#   RPC_URL=... python3 -I kol/activity.py kol/leaderboard_nov17.json SP > out/kol_activity.txt
import sys, os, json, time, datetime, urllib.request
from concurrent.futures import ThreadPoolExecutor
L = json.load(open(sys.argv[1])); SP = sys.argv[2]; URL = os.environ["RPC_URL"]
def call(m, p):
    for i in range(6):
        try:
            rq = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(rq, timeout=40))
            if "error" in r: raise RuntimeError("rpc error")
            return r["result"]
        except Exception: time.sleep(1.5 * (i + 1))
    return []
W = {}
for r in L:
    w = W.setdefault(r["w"], dict(name=r["name"], p={}))
    w["p"][r["tf"]] = (r["profit"], r["wins"], r["losses"])
def act(w):
    s = call("getSignaturesForAddress", [w, {"limit": 1000}])
    ok = [x for x in s if not x["err"] and x.get("blockTime")]
    return w, len(s), len(ok), (ok[0]["blockTime"] if ok else 0), (ok[-1]["blockTime"] if ok else 0)
with ThreadPoolExecutor(8) as ex: A = list(ex.map(act, W))
now = time.time(); out = {}
print("wallet   name             | 1 d / 7 d / 30 d profit SOL (wins-losses 30 d) | newest 1,000 signatures: landed, span hours, last seen")
for w, n, ok, t1, t0 in sorted(A, key=lambda x: -W[x[0]]["p"].get(30, (0,))[0]):
    p = W[w]["p"]; span = (t1 - t0) / 3600 if ok else 0
    out[w] = dict(name=W[w]["name"], p=p, landed=ok, span_h=span, last=t1)
    g = lambda tf: f"{p[tf][0]:+7.0f}" if tf in p else "      -"
    wl = f"{p[30][1]}-{p[30][2]}" if 30 in p else "-"
    print(f"{w[:8]} {W[w]['name'][:16]:16s} | {g(1)} / {g(7)} / {g(30)} ({wl:>9s}) | {ok:4d} in {span:6.1f} h, {(now - t1) / 3600 if t1 else 0:5.1f} h ago")
json.dump(out, open(f"{SP}/kol_activity.json", "w"))
