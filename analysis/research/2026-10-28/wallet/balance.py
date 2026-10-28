# Wallet 4's native SOL balance over time: from the raw pre-Oct-19 transactions and the Oct 19+ rows; the per-day
# change split into deposits/withdrawals (netflows.json) and everything else.
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
from collections import defaultdict
old = sorted(oldsigs(), key=lambda x: x[1])
last = None
for sig, slot, bt, err in old:
    t = tri.tx(sig); ks = keys_of(t); i = ks.index(W); last = (bt, t["meta"]["postBalances"][i], slot)
print("balance after the last tx before Oct 19:", ts(last[0]), last[1] / 1e9)
first_t = tri.tx(old[0][0]); print("balance after the first tx:", first_t["meta"]["postBalances"][keys_of(first_t).index(W)] / 1e9)
R = sorted(rows(), key=lambda r: (r["s"], r["i"] or 0))
S = json.load(open(SP + "/h9long/H9kuqGKN_sigs.json"))
landed = {r["sig"] for r in R}
failed = [x for x in S if x[3]]
print("Oct 19+ signatures", len(S), "failed", len(failed), "landed rows", len(R), "landed sigs not in rows", sum(1 for x in S if not x[3] and x[0] not in landed))
# fee of failed txs: fetch a sample later; here assume rows-only
bal = last[1]; day = defaultdict(lambda: [0, 0]); nf = json.load(open(OUT + "/netflows.json")); nfs = {x["sig"]: x for x in nf}
for r in R:
    bal += r["d"]; k = time.strftime("%m-%d", time.gmtime(r["bt"]))
    if r["sig"] in nfs: day[k][1] += r["d"]
    else: day[k][0] += r["d"]
print("balance from rows only (no failed-tx fees) at", ts(R[-1]["bt"]), bal / 1e9)
for k in sorted(day): print(k, "other", round(day[k][0] / 1e9, 3), "deposit/withdrawal", round(day[k][1] / 1e9, 3))
# check: getBalance at a slot is not available; compare with the last row's own post balance
t = tri.tx(R[-1]["sig"]); print("last row post balance on chain", t["meta"]["postBalances"][keys_of(t).index(W)] / 1e9, ts(R[-1]["bt"]))
# Oct 27 00:40 point
b = last[1]
for r in R:
    if r["bt"] > 1793061600: break   # 2026-10-27 00:40 UTC
    b += r["d"]
print("rows-only balance at Oct 27 00:40 UTC", b / 1e9)
