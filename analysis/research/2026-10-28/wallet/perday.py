# Wallet 4 per day (UTC): signatures, failed, its curve buys (other-quote / SOL), sizes, 1.45+ other-quote buys.
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
from collections import defaultdict, Counter
S = json.load(open(SP + "/h9long/H9kuqGKN_sigs.json")) + [[x[0], x[1], x[2], x[3]] for x in oldsigs()]
R = rows()
def spent(r): return -(r["d"] + r["tok"].get(WSOL, [0])[0] + r["fee"]) / 1e9
sig = Counter(); fl = Counter()
for x in S: k = time.strftime("%m-%d", time.gmtime(x[2])); sig[k] += 1; fl[k] += x[3]
oq = defaultdict(list); sq = defaultdict(list)
for r in R:
    for t in r["tr"]:
        if t[1] == W and t[2] == 1:
            k = time.strftime("%m-%d", time.gmtime(r["bt"])); (oq if t[5] == 0 else sq)[k].append(spent(r)); break
print("day    sigs  failed  oq-buys  oq-median  oq>=1.45  sol-buys")
for k in sorted(sig):
    v = sorted(oq[k]); print(f"{k}  {sig[k]:5d}  {fl[k]:5d}  {len(v):7d}  {v[len(v)//2] if v else 0:9.3f}  {sum(1 for x in v if x >= 1.45):8d}  {len(sq[k]):8d}")
print("Oct 28 covers 00:00-14:54 UTC (14.9 h); Oct 17 covers 19:22-24:00")
