# Infrastructure from fetched transactions: 200 random tipped own transactions (tip service, amount, how many
# services per tx), 100 random own transactions (version, durable nonce, priority fee, CU limit).
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import random
R = rows(); random.seed(21)
own = [r for r in R if r["signer"]]
tipped = random.sample([r for r in own if r["tip"] > 0], 200); anyown = random.sample(own, 100)
with ThreadPoolExecutor(6) as ex: T1 = list(ex.map(lambda r: tri.tx(r["sig"]), tipped)); T2 = list(ex.map(lambda r: tri.tx(r["sig"]), anyown))
svc = Counter(); nsvc = Counter(); amt = Counter(); svc_amt = Counter()
for t in T1:
    tp = [(TIPS[b], l) for k, a, b, l, m, d, inn in transfers(t) if b in TIPS and a == W]
    nsvc[len(tp)] += 1
    for s, l in tp: svc[s] += 1; amt[l] += 1; svc_amt[(s, l)] += 1
print("200 tipped own txs: tips per tx", dict(nsvc)); print("  service:", svc.most_common()); print("  amount (lamports):", amt.most_common(8))
print("  service x amount:", svc_amt.most_common(10))
ver = Counter(); nonce = 0; pf = []; cul = []
for t in T2:
    ver[str(t.get("version"))] += 1; m = t["transaction"]["message"]; ks = keys_of(t); ix0 = m["instructions"][0]
    if ks[ix0["programIdIndex"]] == SYS and b58d(ix0.get("data", ""))[:4] == b"\x04\x00\x00\x00": nonce += 1
    cfg = m.get("transactionConfig") or {}
    if cfg.get("priorityFee") is not None: pf.append(cfg["priorityFee"])
    if cfg.get("computeUnitLimit") is not None: cul.append(cfg["computeUnitLimit"])
pf.sort(); cul.sort()
print("100 random own txs: version", dict(ver), " durable nonce first", nonce, " priorityFee lamports p10/50/90", [pf[int(p * len(pf) / 100)] for p in (10, 50, 90)] if pf else None, "n", len(pf), " CU limit p10/50/90", [cul[int(p * len(cul) / 100)] for p in (10, 50, 90)] if cul else None)
