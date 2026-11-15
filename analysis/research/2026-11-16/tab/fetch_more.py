# Step 2a: TAB16RxX's landed transactions beyond the Nov 13 fetch (../../2026-11-13/tab_exits/fetch_all.py: Oct 29
# 12:45 - Nov 12 17:18 UTC), newer up to now and older back to Oct 21 18:30 UTC (where wallet 4's study starts), into the
# same TXDIR, and SIGS (all of them, [sig, slot, time]). The RPC from the environment (RPC_URL, never printed).
#   RPC_URL=... python3 -I fetch_more.py TXDIR OLD_SIGS.json SIGS.json
import sys, json, os, time, datetime, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor
URL = os.environ["RPC_URL"]; W = "TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3"; TXDIR, OLD, OUT = sys.argv[1:4]
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp()
def call(m, p):
    for i in range(10):
        try:
            rq = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(rq, timeout=40))
            if "error" in r: raise RuntimeError("rpc error")
            return r["result"]
        except Exception: time.sleep(min(10, 1.5 * (i + 1)))
    raise RuntimeError(m)
old = sorted(json.load(open(OLD)), key=lambda s: s[1]); have = {s[0] for s in old}
if os.path.exists(OUT): sigs = json.load(open(OUT))
else:
    new, before = [], None                                   # newer: from now back to the newest one we have
    while True:
        p = {"limit": 1000}
        if before: p["before"] = before
        r = call("getSignaturesForAddress", [W, p])
        if not r: break
        new += [[s["signature"], s["slot"], s["blockTime"]] for s in r if not s["err"] and s["signature"] not in have]
        before = r[-1]["signature"]
        if r[-1]["slot"] <= old[-1][1]: break
    older, before = [], old[0][0]                            # older: before the oldest one we have, to T0
    while True:
        r = call("getSignaturesForAddress", [W, {"limit": 1000, "before": before}])
        if not r: break
        older += [[s["signature"], s["slot"], s["blockTime"]] for s in r if not s["err"] and s["blockTime"] >= T0]
        before = r[-1]["signature"]
        if r[-1]["blockTime"] < T0: break
    sigs = sorted(older + old + new, key=lambda s: s[1]); json.dump(sigs, open(OUT, "w"))
    f = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d %H:%M")
    print(f"signatures: {len(older)} older, {len(old)} had, {len(new)} newer; {f(sigs[0][2])} to {f(sigs[-1][2])} UTC", flush=True)
todo = [s for s in sigs if not os.path.exists(f"{TXDIR}/{s[1]}_{s[0][:20]}.json")]
print(len(sigs), "landed;", len(todo), "to fetch", flush=True)
n = [0]; lk = threading.Lock()
def get(s):
    try: t = call("getTransaction", [s[0], {"encoding": "json", "maxSupportedTransactionVersion": 0}])
    except Exception: print("gave up", s[0][:12], flush=True); return
    if t: json.dump(t, open(f"{TXDIR}/{s[1]}_{s[0][:20]}.json", "w"))
    with lk:
        n[0] += 1
        if n[0] % 1000 == 0: print("fetched", n[0], flush=True)
with ThreadPoolExecutor(10) as ex: list(ex.map(get, todo))
print("done", len(os.listdir(TXDIR)), flush=True)
