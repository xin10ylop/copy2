# Failed tx count + sampled mean fee per rival over the window its Enhanced history covers.
import sys, os, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
top = json.load(open(os.path.join(C.OUTD, "top12.json")))
out = {}
for w in top:
    h = json.load(open(os.path.join(C.OUTD, f"hist_{w}.json")))
    t0 = min(t["timestamp"] for t in h["txs"]); before = None; S = []
    for _ in range(30):
        p = {"limit": 1000}
        if before: p["before"] = before
        r = C.rpc("getSignaturesForAddress", [w, p], cache=bool(before))
        if not r: break
        S += r; before = r[-1]["signature"]
        if (r[-1].get("blockTime") or 0) < t0: break
    S = [s for s in S if (s.get("blockTime") or 0) >= t0]
    fails = [s for s in S if s["err"]]
    random.seed(1); smp = random.sample(fails, min(15, len(fails)))
    fees = []; payer_self = 0
    for s in smp:
        tx = C.rpc("getTransaction", [s["signature"], {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}])
        if not tx: continue
        ks = tx["transaction"]["message"]["accountKeys"]
        if ks[0] == w: fees.append(tx["meta"]["fee"]); payer_self += 1
        else: fees.append(0)
    out[w] = dict(n_sigs=len(S), n_ok=len(S) - len(fails), n_failed=len(fails), sampled=len(fees), mean_fee=(sum(fees) / len(fees)) if fees else 0,
                  enh_n=len(h["txs"]))
    print(w[:10], out[w])
json.dump(out, open(os.path.join(C.OUTD, "failed.json"), "w"))
