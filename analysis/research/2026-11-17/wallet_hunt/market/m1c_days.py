# Market scan for more days, the cheap way (Nov 18, the owner: "do 4 days, and super efficient"). The 48 h of
# launches.json (Nov 15 01:07 - Nov 17 01:07 UTC) are on disk; this lists the launches of [T0, T1) for the other days:
#   1. the signatures of pump's quote-control PDA (6z6GDdfb..., in the create_v2 of every coin priced in another token,
#      not in SOL creates: about a quarter of all creates). Checked on the last 6 h of the 48 h: it catches 95.5% of
#      the known other-token creates, and every miss is USDC-quoted (no float quote missed);
#   2. those transactions, batched (100 a request, kept-alive): the create's coin, quote, creator (m1's decoder);
#      kept: quotes we hold as floats (the coins a copy can trade);
#   3. each kept coin's signatures back to its create (10 pages at most, m1's rule) -> its first WIN s.
# -> SP/market/launches_<T0>.json in launches.json's format (then m2b_full.py fetches the paths with LAUNCHES=...).
#   RPC_URL=... python3 -I m1c_days.py SP T0 T1 [WIN=2400]
import sys, os, json, time, threading, requests
from concurrent.futures import ThreadPoolExecutor
SP, T0, T1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); WIN = int(sys.argv[4]) if len(sys.argv) > 4 else 2400
URL = os.environ["RPC_URL"]; O = f"{SP}/market"
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M, lib
QC = "6z6GDdfb2AjR9ZhJmAUQ5cipJCVxQvLJhB2H8mCwTFBP"; WSOL = "So11111111111111111111111111111111111111112"
FLOATS = ("3NZ9JMVB", "pumpCmXq", "SPCXxcqX", "TTWofwAg", "DJTu7vi8", "98sMhvDw", "XsbEhLAt")
_tl = threading.local()
def S():
    if not hasattr(_tl, "s"): _tl.s = requests.Session()
    return _tl.s
def call(m, p):
    for i in range(6):
        try:
            r = S().post(URL, json={"jsonrpc": "2.0", "id": 1, "method": m, "params": p}, timeout=60).json()
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
            for x in S().post(URL, json=[{"jsonrpc": "2.0", "id": k, "method": "getTransaction", "params": [s, M.TXO]} for k, s in enumerate(need)], timeout=60).json():
                if isinstance(x, dict) and x.get("result"): out[need[x["id"]]] = x["result"]
        except Exception: pass
        if len(out) < len(sigs): time.sleep(i + 1)
    return [out.get(x) for x in sigs]
t0 = time.time()
# 1. quote-control signatures in [T0, T1)
sg, before = [], None
while True:
    r = call("getSignaturesForAddress", [QC, {"limit": 1000, **({"before": before} if before else {})}])
    if not r: break
    sg += [[x["signature"], x["slot"], x["blockTime"]] for x in r if not x["err"] and x.get("blockTime") and T0 <= x["blockTime"] < T1]
    before = r[-1]["signature"]
    if r[-1]["blockTime"] < T0: break
print(f"step 1: {len(sg)} quote-control transactions in the window ({time.time() - t0:.0f} s)", flush=True)
# 2. the creates
def create_of(s, tx):
    if not tx or tx["meta"] is None or tx["meta"]["err"] is not None: return None
    ks = tx["transaction"]["message"]["accountKeys"] + (tx["meta"].get("loadedAddresses") or {}).get("writable", []) + (tx["meta"].get("loadedAddresses") or {}).get("readonly", [])
    trades = []
    for g in tx["meta"].get("innerInstructions") or []:
        for ix in g["instructions"]:
            if ks[ix["programIdIndex"]] != lib.PUMP: continue
            raw = lib.b58d(ix.get("data", ""))
            if raw[:8] == M.E.EVENT_IX_TAG and raw[8:16] == M.E.DISC_TRADE:
                try: trades.append(M.decode_trade(raw[16:]))
                except Exception: pass
    pre = {x["mint"] for x in (tx["meta"].get("preTokenBalances") or [])}
    new = [b["mint"] for b in (tx["meta"].get("postTokenBalances") or []) if b["mint"] not in pre]
    coin = next((m for m in new if m.endswith("pump")), None)
    if not coin: return None
    q = next((e.get("quote_mint") for e in trades if e["mint"] == coin and e.get("quote_mint")), None)
    if q is None:
        others = [b["mint"] for b in (tx["meta"].get("postTokenBalances") or []) if b["mint"] != coin]
        q = others[0] if len(set(others)) == 1 else "?"
    return dict(mint=coin, slot=s[1], t=s[2], quote=q, creator=ks[0])
ch = [sg[i:i + 100] for i in range(0, len(sg), 100)]
with ThreadPoolExecutor(4) as ex: txs = [t for part in ex.map(lambda c: batch([s[0] for s in c]), ch) for t in part]
C = [c for s, tx in zip(sg, txs) for c in [create_of(s, tx)] if c]
keep = {c["mint"]: c for c in C if c["quote"][:8] in FLOATS}
import collections
print(f"step 2: {len(C)} creates read, {len(keep)} with a float quote ({time.time() - t0:.0f} s); quotes {collections.Counter(c['quote'][:8] for c in C).most_common(6)}", flush=True)
# 3. each kept coin's first WIN s
def life(r):
    out, before = [], None
    for _ in range(10):
        page = call("getSignaturesForAddress", [r["mint"], {"limit": 1000, **({"before": before} if before else {})}])
        if not page: break
        out += page; before = page[-1]["signature"]
        if page[-1]["slot"] <= r["slot"] or len(page) < 1000: break
    if out and out[-1]["slot"] > r["slot"]: return None
    return dict(r, sigs=[[x["signature"], x["slot"], x["blockTime"]] for x in reversed(out) if not x["err"] and x.get("blockTime") and x["blockTime"] - r["t"] <= WIN])
with ThreadPoolExecutor(8) as ex: L = {r["mint"]: x for r, x in zip(keep.values(), ex.map(life, keep.values()))}
json.dump(L, open(f"{O}/launches_{T0}.json", "w"))
n = [len(x["sigs"]) for x in L.values() if x]
print(f"step 3: {len(n)} coins listed; 30+ transactions: {sum(1 for k in n if k >= 30)} ({sum(k for k in n if k >= 30)} transactions); mega coins left out {sum(1 for x in L.values() if x is None)} ({time.time() - t0:.0f} s)", flush=True)
