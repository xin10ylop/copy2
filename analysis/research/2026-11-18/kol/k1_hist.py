# The leaderboard wallets (kolscan, Nov 18; kol_wallets.json), step 1: each wallet's own trades since Nov 3 00:00 UTC
# (the newest MAXSIG signatures), venue-free: per transaction it signs, every token whose balance it changed and its
# SOL + WSOL change (fees and tips in). Batched fetches (100 a request, kept-alive). -> SP/kol/hist/<wallet>.json
#   RPC_URL=... SHARD=0/2 python3 -I k1_hist.py SP [MAXSIG]
import sys, os, json, time, threading, requests
from concurrent.futures import ThreadPoolExecutor
SP = sys.argv[1]; MAXSIG = int(sys.argv[2]) if len(sys.argv) > 2 else 6000; OUT = f"{SP}/kol/hist"; os.makedirs(OUT, exist_ok=True)
URL = os.environ["RPC_URL"]; T0 = 1793664000; WSOL = "So11111111111111111111111111111111111111112"
a, b = map(int, os.environ.get("SHARD", "0/1").split("/"))
TXO = {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}
_tl = threading.local()
def S():
    if not hasattr(_tl, "s"): _tl.s = requests.Session()
    return _tl.s
def call(method, params):
    for i in range(6):
        try:
            r = S().post(URL, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=30).json()
            if "error" in r: raise RuntimeError("rpc")
            return r["result"]
        except Exception: time.sleep(1.5 * (i + 1))
    return None
def batch(sigs):
    out = {}
    for i in range(6):
        need = [x for x in sigs if x not in out]
        if not need: break
        try:
            for x in S().post(URL, json=[{"jsonrpc": "2.0", "id": k, "method": "getTransaction", "params": [s, TXO]} for k, s in enumerate(need)], timeout=60).json():
                if isinstance(x, dict) and x.get("result"): out[need[x["id"]]] = x["result"]
        except Exception: pass
        if len(out) < len(sigs): time.sleep(i + 1)
    return [out.get(x) for x in sigs]
def legs(tx, w):
    if not tx or tx["meta"] is None or tx["meta"]["err"] is not None: return None
    keys = [k if isinstance(k, str) else k["pubkey"] for k in tx["transaction"]["message"]["accountKeys"]]
    if w not in keys: return None
    i = keys.index(w); m = tx["meta"]
    def bal(side):
        d = {}
        for x in m[side]:
            if x.get("owner") == w: d[x["mint"]] = d.get(x["mint"], 0) + int(x["uiTokenAmount"]["amount"])
        return d
    pre, post = bal("preTokenBalances"), bal("postTokenBalances")
    dec = {x["mint"]: x["uiTokenAmount"]["decimals"] for x in m["postTokenBalances"] + m["preTokenBalances"]}
    tok = {k: post.get(k, 0) - pre.get(k, 0) for k in set(pre) | set(post) if k != WSOL and post.get(k, 0) != pre.get(k, 0)}
    sol = m["postBalances"][i] - m["preBalances"][i] + post.get(WSOL, 0) - pre.get(WSOL, 0)
    progs = sorted({keys[ix["programIdIndex"]] for ix in tx["transaction"]["message"]["instructions"] if ix["programIdIndex"] < len(keys)})
    return dict(t=tx["blockTime"], slot=tx["slot"], sol=sol, tok=tok, dec={k: dec.get(k) for k in tok}, progs=progs, signer=keys[0] == w)
def one(w):
    f = f"{OUT}/{w}.json"
    if os.path.exists(f): return w, -1
    sigs, before = [], None
    while len(sigs) < MAXSIG:
        pg = call("getSignaturesForAddress", [w, {"limit": 1000, **({"before": before} if before else {})}])
        if not pg: break
        sigs += [s for s in pg if s["err"] is None and (s.get("blockTime") or 0) >= T0]; before = pg[-1]["signature"]
        if len(pg) < 1000 or (pg[-1].get("blockTime") or 0) < T0: break
    sigs = sigs[:MAXSIG]; ch = [[s["signature"] for s in sigs[i:i + 100]] for i in range(0, len(sigs), 100)]
    with ThreadPoolExecutor(4) as ex: txs = [t for p in ex.map(batch, ch) for t in p]
    L = [dict(l, sig=s["signature"]) for s, tx in zip(sigs, txs) for l in [legs(tx, w)] if l and l["tok"]]
    json.dump(dict(w=w, nsig=len(sigs), capped=len(sigs) >= MAXSIG, legs=L), open(f + ".tmp", "w")); os.replace(f + ".tmp", f); return w, len(L)
W = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "kol_wallets.json")))["wallets"]
mine = [w for i, w in enumerate(W) if i % b == a]
with ThreadPoolExecutor(4) as ex:
    for w, n in ex.map(one, mine): print(w[:8], n, flush=True)
