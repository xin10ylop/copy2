# For any wallet: every transaction (up to CAP newest signatures) where its SOL + wSOL changed by >= 0.5 SOL while no
# other token of it moved (deposits/withdrawals by any route), with the other party; plus balance path.
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
from concurrent.futures import ThreadPoolExecutor
A = sys.argv[1]; CAP = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
s = []; before = None
while True:
    p = tri.sigs(A, before=before, limit=1000); s += p
    if len(p) < 1000 or len(s) >= CAP: break
    before = p[-1]["signature"]
s.sort(key=lambda x: x["slot"])
print(A, len(s), "signatures", "(full)" if len(s) < CAP else "(newest CAP only)", ts(s[0]["blockTime"]), "->", ts(s[-1]["blockTime"]))
with ThreadPoolExecutor(8) as ex: txs = list(ex.map(lambda x: tri.tx(x["signature"]), s))
def tokd(t, owner):
    meta = t["meta"]; d = {}
    for side, sg in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in meta.get(side) or []:
            if b.get("owner") == owner: d[b["mint"]] = d.get(b["mint"], 0) + sg * int(b["uiTokenAmount"]["amount"])
    return {k: v for k, v in d.items() if v}
first_bal = None; last_bal = None; res = []
for x, t in zip(s, txs):
    if not t: continue
    ks = keys_of(t)
    if A not in ks: continue
    i = ks.index(A)
    if first_bal is None: first_bal = (t["meta"]["preBalances"][i], x["blockTime"])
    last_bal = (t["meta"]["postBalances"][i], x["blockTime"])
    if t["meta"]["err"]: continue
    td = tokd(t, A); net = t["meta"]["postBalances"][i] - t["meta"]["preBalances"][i] + td.get(WSOL, 0) + (t["meta"]["fee"] if ks[0] == A else 0)
    if abs(net) >= 5e8 and not [m for m in td if m != WSOL]:
        # other party: largest opposite balance change
        ch = [(ks[j], t["meta"]["postBalances"][j] - t["meta"]["preBalances"][j]) for j in range(len(t["meta"]["preBalances"]))]
        cp = (min if net > 0 else max)(ch, key=lambda z: z[1])
        res.append((x["blockTime"], net / 1e9, cp[0], ks[0], [p[:8] for p in progs_of(t)], x["signature"]))
print("balance before first:", first_bal[0] / 1e9, ts(first_bal[1]), " after last:", last_bal[0] / 1e9, ts(last_bal[1]))
for r in res: print("  ", ts(r[0]), f"{r[1]:+.4f}", "other party", r[2], "payer", r[3][:8], r[4], r[5][:24])
json.dump(res, open(OUT + f"/flows_{A[:8]}.json", "w"))
