# Winners first, step 2: the early trades of every graduated coin of the 48 h (outcomes.json) and of a random control
# sample of the coins that did not graduate (seed 7; it gives the base rate: how often a coin that reached a given point
# of its curve went on to graduate). Each coin: its bonding curve's signatures (the curve account sees only curve
# trades), oldest first, the first CAP landed ones fetched and their TradeEvents decoded (cmodel's decoder).
# Out: SP/winners/paths/<mint>.json.gz (cmodel's trade format: slot, t, sig, user, buy, q, tok, vt, vq, bps, real).
# Resumable. The RPC from RPC_URL, never printed.
#   RPC_URL=... python3 -I w2_trades.py SP [NCTRL=3000] [CAP=400]
import sys, os, json, gzip, time, random, urllib.request
from concurrent.futures import ThreadPoolExecutor
from solders.pubkey import Pubkey
SP = sys.argv[1]; NCTRL = int(sys.argv[2]) if len(sys.argv) > 2 else 3000; CAP = int(sys.argv[3]) if len(sys.argv) > 3 else 400
URL = os.environ["RPC_URL"]; PUMP = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M
O = f"{SP}/winners/paths"; os.makedirs(O, exist_ok=True)
oc = json.load(open(f"{SP}/winners/outcomes.json"))
grad = sorted(m for m, x in oc.items() if x[0]); rest = sorted(m for m, x in oc.items() if not x[0])
ctrl = random.Random(7).sample(rest, NCTRL)
json.dump({"grad": grad, "ctrl": ctrl, "n_rest": len(rest)}, open(f"{SP}/winners/sample.json", "w"))
order = grad + ctrl; random.Random(7).shuffle(order)
todo = [m for m in order if not os.path.exists(f"{O}/{m}.json.gz")]
print(f"{len(grad)} graduated + {len(ctrl)} control of {len(rest)}; {len(todo)} to fetch", flush=True)
def call(m, p):
    for i in range(8):
        try:
            rq = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(rq, timeout=60))
            if "error" in r: raise RuntimeError("rpc error")
            return r["result"]
        except Exception: time.sleep(1.5 * (i + 1))
    return None
def curve(m): return str(Pubkey.find_program_address([b"bonding-curve", bytes(Pubkey.from_string(m))], PUMP)[0])
POOL = ThreadPoolExecutor(96); t0 = time.time(); done = [0, 0]
def coin(m):
    c, sigs, before = curve(m), [], None
    for _ in range(30):
        pg = call("getSignaturesForAddress", [c, {"limit": 1000, **({"before": before} if before else {})}])
        if not pg: break
        sigs += pg; before = pg[-1]["signature"]
        if len(pg) < 1000: break
    sigs = [s["signature"] for s in reversed(sigs) if s["err"] is None][:CAP]
    txs = list(POOL.map(lambda s: call("getTransaction", [s, M.TXO]), sigs))
    tr = [e for tx in txs if tx for e in M.trades(tx, m)]
    with gzip.open(f"{O}/{m}.json.gz.tmp", "wt") as f: json.dump(tr, f)
    os.replace(f"{O}/{m}.json.gz.tmp", f"{O}/{m}.json.gz")
    done[0] += 1; done[1] += len(sigs)
    if done[0] % 200 == 0: print(f"{done[0]} coins, {done[1]} transactions, {time.time() - t0:.0f} s", flush=True)
with ThreadPoolExecutor(8) as ex: list(ex.map(coin, todo))
print(f"done: {done[0]} coins, {done[1]} transactions in {time.time() - t0:.0f} s", flush=True)
