# The pool hunt (the owner, Nov 18: "it is impossible that there is only wallet 4 that works for us"). Every search so
# far read pump's bonding curve (launches, the first minutes, copies held 10 min at most). Not covered: wallets that
# trade graduated coins on their PumpSwap pool and hold minutes to hours, where a copy a few seconds late loses little.
# Step 1: a random sample of the coins that graduated Nov 10-18 (SP/winners/week_migrations_7d.json, seed 7); each
# coin's canonical pool (index 0, creator = pump's pool-authority of the mint, quote WSOL); its transactions from the
# migration to +6 h (the first MAXTX); every signer's trade read venue-free from the balances: the coin's token change
# and SOL + WSOL change (fees and tips included: what the wallet really paid), the pool's reserves after.
#   RPC_URL=... SHARD=0/2 python3 -I p1_fetch.py SP N   -> SP/pools/<mint>.json.gz
import sys, os, json, gzip, random, time
from concurrent.futures import ThreadPoolExecutor
from solders.pubkey import Pubkey
SP, N = sys.argv[1], int(sys.argv[2]); OUT = f"{SP}/pools"; os.makedirs(OUT, exist_ok=True)
URL = os.environ["RPC_URL"]; MAXTX = int(os.environ.get("MAXTX", 1500)); HOURS = 6
a, b = os.environ.get("SHARD", "0/1").split("/"); a, b = int(a), int(b)
PUMP = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"); PSWAP = Pubkey.from_string("pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA")
WSOL = "So11111111111111111111111111111111111111112"
def pool_of(m):
    mk = Pubkey.from_string(m); auth = Pubkey.find_program_address([b"pool-authority", bytes(mk)], PUMP)[0]
    return str(Pubkey.find_program_address([b"pool", (0).to_bytes(2, "little"), bytes(auth), bytes(mk), bytes(Pubkey.from_string(WSOL))], PSWAP)[0])
import threading, requests
_tl = threading.local()
def _sess():
    if not hasattr(_tl, "s"): _tl.s = requests.Session()
    return _tl.s
def call(method, params):
    for i in range(6):
        try:
            r = _sess().post(URL, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=30).json()
            if "error" in r: raise RuntimeError("rpc error")
            return r["result"]
        except Exception: time.sleep(1.5 * (i + 1))
    return None
TXO = {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}
def txs_batch(sigs):
    """Batches of 100 getTransaction in one request on a kept-alive connection (Nov 18: 150x the one-by-one speed)."""
    out = {}
    for i in range(6):
        need = [x for x in sigs if x not in out]
        if not need: break
        try:
            j = _sess().post(URL, json=[{"jsonrpc": "2.0", "id": k, "method": "getTransaction", "params": [x, TXO]} for k, x in enumerate(need)], timeout=60).json()
            for k, x in enumerate(j):
                if isinstance(x, dict) and x.get("result"): out[need[x["id"]]] = x["result"]
        except Exception: pass
        if len(out) < len(sigs): time.sleep(1.0 * (i + 1))
    return [out.get(x) for x in sigs]
def trades(tx, m, pool):
    if not tx or tx["meta"] is None or tx["meta"]["err"] is not None: return []
    msg = tx["transaction"]["message"]; keys = [k if isinstance(k, str) else k["pubkey"] for k in msg["accountKeys"]]
    keys += tx["meta"].get("loadedAddresses", {}).get("writable", []) + tx["meta"].get("loadedAddresses", {}).get("readonly", [])
    nsig = msg["header"]["numRequiredSignatures"]; signers = keys[:nsig]
    def bal(side):
        d = {}
        for x in tx["meta"][side]:
            d[(x.get("owner"), x["mint"])] = d.get((x.get("owner"), x["mint"]), 0) + int(x["uiTokenAmount"]["amount"])
        return d
    pre, post = bal("preTokenBalances"), bal("postTokenBalances")
    rb = post.get((pool, m)); rq = post.get((pool, WSOL))
    if rb is None or rq is None: return []
    out = []
    for i, u in enumerate(signers):
        dt = post.get((u, m), 0) - pre.get((u, m), 0)
        if dt == 0: continue
        dsol = tx["meta"]["postBalances"][i] - tx["meta"]["preBalances"][i] + post.get((u, WSOL), 0) - pre.get((u, WSOL), 0)
        out.append(dict(user=u, t=tx["blockTime"], slot=tx["slot"], tok=dt, sol=dsol, rb=rb, rq=rq))
    return out
def one(item):
    m, tmig = item; f = f"{OUT}/{m}.json.gz"
    if os.path.exists(f): return 0
    pool = pool_of(m); sigs, before = [], None
    for _ in range(40):   # page back to the migration
        pg = call("getSignaturesForAddress", [pool, {"limit": 1000, **({"before": before} if before else {})}])
        if not pg: break
        sigs += pg; before = pg[-1]["signature"]
        if len(pg) < 1000 or (pg[-1].get("blockTime") or 0) < tmig - 60: break
    sigs = [s for s in sigs if s["err"] is None and tmig - 60 <= (s.get("blockTime") or 0) <= tmig + HOURS * 3600]
    sigs = sorted(sigs, key=lambda s: (s["slot"], s.get("blockTime") or 0))[:MAXTX]
    ch = [[x["signature"] for x in sigs[i:i + 100]] for i in range(0, len(sigs), 100)]
    with ThreadPoolExecutor(4) as ex: txs = [t for part in ex.map(txs_batch, ch) for t in part]
    tr = [dict(e, sig=s["signature"]) for s, tx in zip(sigs, txs) for e in trades(tx, m, pool)]
    json.dump(dict(m=m, pool=pool, tmig=tmig, nsig=len(sigs), tr=tr), gzip.open(f + ".tmp", "wt")); os.replace(f + ".tmp", f); return len(tr)
mig = json.load(open(f"{SP}/winners/week_migrations_7d.json"))
mig = [x for x in mig if x[0].endswith("pump")]; random.Random(7).shuffle(mig); mig = mig[:N]
mine = [x for i, x in enumerate(mig) if i % b == a]
t0 = time.time(); done = 0
with ThreadPoolExecutor(8) as ex:
    for n in ex.map(one, mine):
        done += 1
        if done % 10 == 0: print(f"{done}/{len(mine)} coins, {time.time() - t0:.0f} s", flush=True)
print("done", done)
