# m2bs (Nov 19): m2b_full.py with PATHS_OUT (a folder) for the SOL-coin search.
# Market scan, step 4 again in full (Nov 18; the owner: "why dont you find similar to wallet 4"). m2_trades kept half
# the coins and each coin's first 300 transactions, because one-by-one fetching was slow. Now batched (100 a request,
# kept-alive, ~150x faster): every live other-token coin of launches.json (MIN+ transactions), every transaction of its
# first WIN s, its TradeEvents decoded (cmodel), the path put in its true in-slot order (2026-11-18/churn/slot_order).
# -> SP/market/paths_full/<mint>.json.gz, the same format; m3_screen reads it with PATHS=paths_full.
#   RPC_URL=... SHARD=0/2 python3 -I m2b_full.py SP [MIN=30]
import sys, os, json, gzip, time, threading, requests
from concurrent.futures import ThreadPoolExecutor
SP = sys.argv[1]; MIN = int(sys.argv[2]) if len(sys.argv) > 2 else 30; URL = os.environ["RPC_URL"]
a, b = map(int, os.environ.get("SHARD", "0/1").split("/"))
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-18/churn"); import slot_order as SO
O = os.environ.get("PATHS_OUT", f"{SP}/market/paths_full"); os.makedirs(O, exist_ok=True)
L = {m: x for m, x in json.load(open(os.environ.get("LAUNCHES", f"{SP}/market/launches.json"))).items() if x and len(x["sigs"]) >= MIN}   # LAUNCHES: another day's list (m1c_days.py)
todo = [m for i, m in enumerate(sorted(L)) if i % b == a and not os.path.exists(f"{O}/{m}.json.gz")]
if os.environ.get("REVERSE"): todo = todo[::-1]   # a second fetcher on the same shard from the other end
print(f"{len(L)} live coins, {sum(len(x['sigs']) for x in L.values())} transactions; this shard {len(todo)} to fetch", flush=True)
_tl = threading.local()
def batch(sigs):
    if not hasattr(_tl, "s"): _tl.s = requests.Session()
    out = {}
    for i in range(6):
        need = [x for x in sigs if x not in out]
        if not need: break
        try:
            for x in _tl.s.post(URL, json=[{"jsonrpc": "2.0", "id": k, "method": "getTransaction", "params": [s, M.TXO]} for k, s in enumerate(need)], timeout=60).json():
                if isinstance(x, dict) and x.get("result"): out[need[x["id"]]] = x["result"]
        except Exception: pass
        if len(out) < len(sigs): time.sleep(i + 1)
    return [out.get(x) for x in sigs]
POOL = ThreadPoolExecutor(24); t0 = time.time(); done = [0, 0]
def coin(m):
    if os.path.exists(f"{O}/{m}.json.gz"): return   # done by the other fetcher of this shard
    s = [x[0] for x in L[m]["sigs"]]; ch = [s[i:i + 100] for i in range(0, len(s), 100)]
    txs = [t for p in POOL.map(batch, ch) for t in p]
    tr = SO.reorder([e for tx in txs if tx for e in M.trades(tx, m)])
    with gzip.open(f"{O}/{m}.json.gz.tmp", "wt") as f: json.dump(tr, f)
    os.replace(f"{O}/{m}.json.gz.tmp", f"{O}/{m}.json.gz"); done[0] += 1; done[1] += len(s)
    if done[0] % 200 == 0: print(f"{done[0]} coins, {done[1]} transactions, {time.time() - t0:.0f} s", flush=True)
with ThreadPoolExecutor(8) as ex: list(ex.map(coin, todo))
print(f"done: {done[0]} coins, {done[1]} transactions in {time.time() - t0:.0f} s", flush=True)
