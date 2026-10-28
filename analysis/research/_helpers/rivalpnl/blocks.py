# Compact pump-trade summaries of blocks, cached per slot.
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C, pumpparse as P
def summarize(slot):
    p = os.path.join(C.CACHE, f"blk_{slot}.json")
    if os.path.exists(p): return json.load(open(p))
    b = C.rpc("getBlock", [slot, {"encoding": "json", "transactionDetails": "full", "maxSupportedTransactionVersion": 1, "rewards": False}], cache=False)
    if b is None:
        out = None
    else:
        txs = []
        for ix, tx in enumerate(b["transactions"]):
            ks = P.keys_of(tx)
            if C.PUMP not in ks: continue
            r = P.analyze(tx)
            txs.append(dict(idx=ix, sig=tx["transaction"]["signatures"][0], signer=ks[0], err=r["err"], fee=r["fee"], cu_price=r["cu_price"],
                            cu_limit=r["cu_limit"], tips=r["tips"], tip_total=r["tip_total"], pump_ix=r["pump_ix"],
                            create_mint=r.get("create_mint"), trades=r["trades"],
                            tokmints=sorted({x["mint"] for x in (tx["meta"].get("postTokenBalances") or []) if x["mint"].endswith("pump")})[:3]))
        out = dict(slot=slot, n=len(b["transactions"]), time=b.get("blockTime"), txs=txs)
    json.dump(out, open(p, "w"))
    return out
