# Market scan, step 4 (discovery pass): the trades on the live other-token coins (MIN+ landed transactions in their
# first WIN s, from launches.json), in a random order (seed 7) so a stop leaves a fair sample, FRAC of the coins, each
# coin's first CAP transactions only (1.73 million in full: too many; activity is front-loaded, and this pass only finds
# the wallets; their copy is scored on full paths of their own history afterwards). Each transaction fetched once, its TradeEvents on the coin decoded (cmodel's decoder), in the order
# the chain listed them (oldest first). -> SP/market/paths/<mint>.json.gz (a path in screen.py's format). Resumable.
# The RPC from RPC_URL, never printed.
#   RPC_URL=... python3 -I m2_trades.py SP [MIN=30] [FRAC=0.5] [CAP=300]
import sys, os, json, gzip, time, random, urllib.request
from concurrent.futures import ThreadPoolExecutor
SP = sys.argv[1]; MIN = int(sys.argv[2]) if len(sys.argv) > 2 else 30; FRAC = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
CAP = int(sys.argv[4]) if len(sys.argv) > 4 else 300; URL = os.environ["RPC_URL"]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M
O = f"{SP}/market/paths"; os.makedirs(O, exist_ok=True)
L = {m: x for m, x in json.load(open(f"{SP}/market/launches.json")).items() if x and len(x["sigs"]) >= MIN}
order = sorted(L); random.Random(7).shuffle(order); order = order[:int(len(order) * FRAC)]
for m in order: L[m] = dict(L[m], sigs=L[m]["sigs"][:CAP])
L = {m: L[m] for m in order}
todo = [m for m in order if not os.path.exists(f"{O}/{m}.json.gz")]
print(f"{len(L)} live coins, {sum(len(x['sigs']) for x in L.values())} transactions; {len(todo)} to fetch", flush=True)
def call(m, p):
    for i in range(8):
        try:
            rq = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(rq, timeout=60))
            if "error" in r: raise RuntimeError("rpc error")
            return r["result"]
        except Exception: time.sleep(1.5 * (i + 1))
    return None
POOL = ThreadPoolExecutor(96); t0 = time.time(); done = [0, 0]
def coin(m):
    x = L[m]; txs = list(POOL.map(lambda s: call("getTransaction", [s[0], M.TXO]), x["sigs"]))
    tr = [e for tx in txs if tx for e in M.trades(tx, m)]
    with gzip.open(f"{O}/{m}.json.gz.tmp", "wt") as f: json.dump(tr, f)
    os.replace(f"{O}/{m}.json.gz.tmp", f"{O}/{m}.json.gz")
    done[0] += 1; done[1] += len(x["sigs"])
    if done[0] % 100 == 0: print(f"{done[0]} coins, {done[1]} transactions, {time.time() - t0:.0f} s", flush=True)
with ThreadPoolExecutor(8) as ex: list(ex.map(coin, todo))
print(f"done: {done[0]} coins, {done[1]} transactions in {time.time() - t0:.0f} s", flush=True)
