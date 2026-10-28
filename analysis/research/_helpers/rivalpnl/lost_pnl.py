# Step 3: what did the wallets ahead of us make on each lost mint. Uses Enhanced history of the bonding curve back to the create slot.
import sys, os, json, collections, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C, rival_stats as R
L = json.load(open(os.path.join(C.OUTD, "lost_fail.json")))
rk = json.load(open(os.path.join(C.OUTD, "rival_rank.json"))); bund = set(rk["bund"])
out = []
for o in L:
    mint = o["mint"]; curve = C.bonding_curve(mint); txs = []; before = None; reached = False
    for page in range(8):
        try: j = C.enhanced(curve, before=before)
        except Exception as e: print("err", mint[:8], e); break
        if not j: reached = True; break
        txs += j; before = j[-1]["signature"]
        if j[-1]["slot"] <= o["cslot"]: reached = True; break
    users = {x["user"] for x in o["ahead"] if not x["is_creator"]}
    per = {}
    for w in users:
        cost = proc = 0; tb = ts = 0.0; fb = fs = None
        for t in sorted(reversed(txs), key=lambda t: t["slot"]):
            p = R.parse(w, t)
            v = p["legs"].get(mint)
            if not v: continue
            if v > 0: cost += -p["delta"]; tb += v; fb = fb or t["timestamp"]
            else: proc += p["delta"]; ts += -v; fs = fs or t["timestamp"]
        per[w] = dict(cost=cost / 1e9, proc=proc / 1e9, held=ts < 0.99 * tb, hold=(fs - fb) if (fs and fb) else None, found=tb > 0, bundle=w in bund)
    out.append(dict(mint=mint, reached=reached, ntx=len(txs), per=per))
    print(mint[:8], "reached", reached, "ntx", len(txs), "found", sum(1 for v in per.values() if v["found"]), "/", len(per))
json.dump(out, open(os.path.join(C.OUTD, "lost_pnl.json"), "w"))
