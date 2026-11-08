# getTransaction for every ok signature, N threads: python3 -I txsp.py SIGS_JSON OUT_DIR [N]
import json, sys, time, os, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor
s = [x["signature"] for x in json.load(open(sys.argv[1])) if not x.get("err")]; out = sys.argv[2]; os.makedirs(out, exist_ok=True)
N = int(sys.argv[3]) if len(sys.argv) > 3 else 4
U = "https://api.mainnet-beta.solana.com"; cnt = [0, 0]; lk = threading.Lock()
def one(sig):
    fn = f"{out}/{sig}.json"
    if os.path.exists(fn): return
    for i in range(10):
        try:
            b = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "getTransaction", "params": [sig, {"encoding": "json", "maxSupportedTransactionVersion": 1}]}).encode()
            r = json.loads(urllib.request.urlopen(urllib.request.Request(U, b, {"Content-Type": "application/json"}), timeout=60).read())
            if r.get("result"):
                json.dump(r["result"], open(fn, "w"))
                with lk: cnt[0] += 1
                return
        except Exception: pass
        time.sleep(2 * (i + 1))
    with lk: cnt[1] += 1
with ThreadPoolExecutor(N) as ex: list(ex.map(one, s))
print(len(s), "sigs;", cnt[0], "fetched;", cnt[1], "failed", flush=True)
