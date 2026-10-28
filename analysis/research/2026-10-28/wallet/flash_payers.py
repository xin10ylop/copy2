# FLASHX8D: fee payers of 400 random transactions from its last 5,000 signatures; Axiom markers; wallet 4 present?
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
import random
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
s = json.load(open(OUT + "/flash_sigs.json")); random.seed(7)
smp = random.sample([x for x in s if not x.get("err")], 400)
with ThreadPoolExecutor(6) as ex: txs = list(ex.map(lambda x: tri.tx(x["signature"]), smp))
payers = Counter(); axiom = 0; pump = 0; W4 = 0; keysets = Counter()
for t in txs:
    if not t: continue
    ks = keys_of(t); payers[ks[0]] += 1
    if any("Axiom" in k for k in ks): axiom += 1
    if PUMP in ks or PUMPSWAP in ks: pump += 1
    if W in ks: W4 += 1
    for k in ks:
        if k.startswith("jitodontfront") or "Axiom" in k: keysets[k] += 1
print("sampled", len(txs), "distinct fee payers", len(payers), "top payer share", payers.most_common(1)[0][1] if payers else 0)
print("with an 'Axiom' account key", axiom, " touching pump/PumpSwap", pump, " wallet 4 in keys", W4)
print("marker keys", keysets.most_common(5))
print("payers seen more than twice", [(p[:8], c) for p, c in payers.most_common(10) if c > 2])
