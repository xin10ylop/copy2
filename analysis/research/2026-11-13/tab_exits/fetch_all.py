# TAB16RxX's landed transactions from Oct 29 12:00 UTC to now, one JSON file each (RPC json encoding) in ./tx, and
# ./sigs.json; the RPC from the environment (RPC_URL, never printed).   RPC_URL=... python3 -I fetch_all.py
import sys, json, os, time, datetime, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor
URL = os.environ["RPC_URL"]; W = "TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3"
T0 = datetime.datetime(2026, 10, 29, 12, 0, tzinfo=datetime.timezone.utc).timestamp()
def call(m, p):
    for i in range(10):
        try:
            rq = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(rq, timeout=40))
            if "error" in r: raise RuntimeError(r["error"])
            return r["result"]
        except Exception as e:
            time.sleep(min(10, 1.5 * (i + 1)))
    raise RuntimeError(m)
if os.path.exists("sigs.json"): sigs = json.load(open("sigs.json"))
else:
    sigs, before = (json.load(open("sigs_partial.json")) if os.path.exists("sigs_partial.json") else ([], None))
    while True:
        p = {"limit": 1000}
        if before: p["before"] = before
        r = call("getSignaturesForAddress", [W, p])
        if not r: break
        sigs += [[s["signature"], s["slot"], s["blockTime"]] for s in r if not s["err"]]
        before = r[-1]["signature"]; json.dump([sigs, before], open("sigs_partial.json", "w"))
        print("sigs", len(sigs), datetime.datetime.fromtimestamp(r[-1]["blockTime"], datetime.timezone.utc), flush=True)
        if r[-1]["blockTime"] < T0: break
    sigs = [s for s in sigs if s[2] >= T0]; json.dump(sigs, open("sigs.json", "w"))
todo = [s for s in sigs if not os.path.exists(f"tx/{s[1]}_{s[0][:20]}.json")]
print(len(sigs), "landed;", len(todo), "to fetch", flush=True)
n = [0]; lk = threading.Lock()
def get(s):
    try: t = call("getTransaction", [s[0], {"encoding": "json", "maxSupportedTransactionVersion": 0}])
    except Exception: print("gave up", s[0][:12], flush=True); return
    if t: json.dump(t, open(f"tx/{s[1]}_{s[0][:20]}.json", "w"))
    with lk:
        n[0] += 1
        if n[0] % 500 == 0: print("fetched", n[0], flush=True)
with ThreadPoolExecutor(12) as ex: list(ex.map(get, todo))
print("done", len(os.listdir("tx")), flush=True)
