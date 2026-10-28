# Privacy pool 4AV2Qzp3: every deposit and withdrawal in two windows (Oct 17 15:00-Oct 18 03:00 UTC, when wallet 4's
# chain was funded; Oct 27 13:00-Oct 28 15:00, after wallet 4 put 5 SOL in). Withdrawal recipient = the account whose
# balance rose by the payout; depositor = the signer.
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
from concurrent.futures import ThreadPoolExecutor
POOL = "4AV2Qzp3N4c9RfzyEbNZs2wqWfW4EwKnnxFAZCndvfGh"
S = json.load(open(OUT + "/sigs_4AV2Qzp3.json"))
WIN = [(1792256400, 1792299600), (1793106000, 1793200000)]
sel = [x for x in S if not x[3] and any(a <= x[2] <= b for a, b in WIN)]
print("pool txs in the windows", len(sel), flush=True)
with ThreadPoolExecutor(8) as ex: txs = list(ex.map(lambda x: tri.tx(x[0]), sel))
ev = []
for x, t in zip(sel, txs):
    if not t: continue
    ks = keys_of(t); pre, post = t["meta"]["preBalances"], t["meta"]["postBalances"]
    if POOL not in ks: continue
    pi = ks.index(POOL); dp = post[pi] - pre[pi]
    ch = sorted([(post[j] - pre[j], ks[j]) for j in range(len(pre)) if j != pi], key=lambda z: z[0])
    if dp < 0: ev.append(dict(bt=x[2], kind="W", sol=-dp / 1e9, who=ch[-1][1], got=ch[-1][0] / 1e9, payer=ks[0], sig=x[0]))
    elif dp > 0: ev.append(dict(bt=x[2], kind="D", sol=dp / 1e9, who=ks[0], got=0, payer=ks[0], sig=x[0]))
    else: ev.append(dict(bt=x[2], kind="0", sol=0, who=ks[0], got=0, payer=ks[0], sig=x[0]))
ev.sort(key=lambda e: e["bt"])
json.dump(ev, open(OUT + "/pool_events.json", "w"))
from collections import Counter
print(Counter(e["kind"] for e in ev), "payers of withdrawals", Counter(e["payer"][:8] for e in ev if e["kind"] == "W").most_common(3))
for e in ev:
    if e["bt"] < 1792299600: print(ts(e["bt"]), e["kind"], round(e["sol"], 3), e["who"], round(e["got"], 3), e["payer"][:8])
