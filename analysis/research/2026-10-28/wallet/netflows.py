# Every transaction of wallet 4 since its first (Oct 17) where its SOL + wSOL changed by >= 0.5 SOL (fee added back)
# while no other token moved: deposits and withdrawals by any route (plain transfer, privacy pool, anything).
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
from collections import Counter
out = []
def tokd(t, owner):
    ks = keys_of(t); meta = t["meta"]; d = {}
    for side, sg in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in meta.get(side) or []:
            if b.get("owner") != owner: continue
            d[b["mint"]] = d.get(b["mint"], 0) + sg * int(b["uiTokenAmount"]["amount"])
    return {k: v for k, v in d.items() if v}
for sig, slot, bt, err in oldsigs():
    t = tri.tx(sig)
    if t["meta"]["err"]: continue
    ks = keys_of(t); td = tokd(t, W)
    net = sol_delta(t, W) + td.get(WSOL, 0) + (t["meta"]["fee"] if ks[0] == W else 0)
    if abs(net) >= 5e8 and not [m for m in td if m != WSOL]:
        out.append(dict(sig=sig, bt=bt, net=net / 1e9, payer=ks[0], progs=progs_of(t), src="raw"))
R = rows()
for r in R:
    net = r["d"] + r["tok"].get(WSOL, [0])[0] + (r["fee"] if r["signer"] else 0)
    if abs(net) >= 5e8 and not [m for m in r["tok"] if m != WSOL]:
        out.append(dict(sig=r["sig"], bt=r["bt"], net=net / 1e9, payer="W" if r["signer"] else "other", progs=r["progs"], src="row"))
out.sort(key=lambda x: x["bt"])
print("transactions with |SOL+wSOL| >= 0.5 and no other token:", len(out))
for x in out: print(ts(x["bt"]), round(x["net"], 4), x["payer"][:8], [p[:8] for p in x["progs"]], x["sig"])
json.dump(out, open(OUT + "/netflows.json", "w"))
