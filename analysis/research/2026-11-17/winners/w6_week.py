# Winners first, step 6: the screen on 7 days of graduations, for the selective pickers a 48 h window cannot show (a
# wallet that buys a few coins a day has 1-2 winners in 48 h). Every graduation is a migrate signed by pump's migration
# signer (9C4nRvhh..., found on the coins of step 2; 1,637 of its transactions in the 48 h against 1,495 graduated
# launches); its transactions since DAYS ago -> the graduated mints (the new mint ending in "pump" in each). Each coin
# not already fetched by step 2: its curve's signatures oldest first, the first CAP transactions, trades decoded as in
# step 2, and its create (the oldest transaction: slot, time, fee payer = creator) -> SP/winners/paths/ and
# SP/winners/week_meta.json. Random order (seed 7): a stop leaves a fair sample. Resumable.
# The RPC from RPC_URL, never printed.
#   RPC_URL=... python3 -I w6_week.py SP [DAYS=7] [CAP=250]
import sys, os, json, gzip, time, random, urllib.request
from concurrent.futures import ThreadPoolExecutor
from solders.pubkey import Pubkey
SP = sys.argv[1]; DAYS = float(sys.argv[2]) if len(sys.argv) > 2 else 7; CAP = int(sys.argv[3]) if len(sys.argv) > 3 else 250
URL = os.environ["RPC_URL"]; PUMP = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"); MIG = "9C4nRvhhVquCKATjDCx5FKvNS9PNgNqgyWy9AcoDjYv5"
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M
W = f"{SP}/winners"; O = f"{W}/paths"; os.makedirs(O, exist_ok=True)
def call(m, p):
    for i in range(8):
        try:
            rq = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(rq, timeout=60))
            if "error" in r: raise RuntimeError("rpc error")
            return r["result"]
        except Exception: time.sleep(1.5 * (i + 1))
    return None
POOL = ThreadPoolExecutor(96); t0 = time.time()
fm = f"{W}/week_migrations.json"
if os.path.exists(fm): MG = json.load(open(fm))
else:
    sigs, before = [], None
    while True:
        pg = call("getSignaturesForAddress", [MIG, {"limit": 1000, **({"before": before} if before else {})}])
        if not pg: break
        sigs += [s for s in pg if s["err"] is None]; before = pg[-1]["signature"]
        if len(pg) < 1000 or sigs[0]["blockTime"] - pg[-1]["blockTime"] > DAYS * 86400: break
    sigs = [s for s in sigs if sigs[0]["blockTime"] - s["blockTime"] <= DAYS * 86400]
    def mint_of(s):
        tx = call("getTransaction", [s["signature"], M.TXO])
        if not tx: return None
        new = {b["mint"] for b in tx["meta"].get("postTokenBalances") or []}
        m = next((x for x in new if x.endswith("pump")), None)
        return [m, s["blockTime"]] if m else None
    MG = [x for x in POOL.map(mint_of, sigs) if x]
    json.dump(MG, open(fm, "w"))
print(f"{len(MG)} migrations in {DAYS} days ({time.time() - t0:.0f} s)", flush=True)
fmeta = f"{W}/week_meta.json"; META = json.load(open(fmeta)) if os.path.exists(fmeta) else {}
order = sorted({m for m, _ in MG}); random.Random(7).shuffle(order)
todo = [m for m in order if m not in META and not os.path.exists(f"{O}/{m}.json.gz")]
print(f"{len(order)} graduated coins, {len(todo)} to fetch", flush=True)
def curve(m): return str(Pubkey.find_program_address([b"bonding-curve", bytes(Pubkey.from_string(m))], PUMP)[0])
done = [0, 0]
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
    first = next((tx for tx in txs if tx), None)
    META[m] = dict(slot=first["slot"], t=first["blockTime"], creator=first["transaction"]["message"]["accountKeys"][0]) if first else None
    with gzip.open(f"{O}/{m}.json.gz.tmp", "wt") as f: json.dump(tr, f)
    os.replace(f"{O}/{m}.json.gz.tmp", f"{O}/{m}.json.gz")
    done[0] += 1; done[1] += len(sigs)
    if done[0] % 200 == 0:
        json.dump(dict(META), open(fmeta, "w")); print(f"{done[0]} coins, {done[1]} transactions, {time.time() - t0:.0f} s", flush=True)
with ThreadPoolExecutor(8) as ex: list(ex.map(coin, todo))
json.dump(dict(META), open(fmeta, "w"))
print(f"done: {done[0]} coins, {done[1]} transactions in {time.time() - t0:.0f} s", flush=True)
