# Wallet 4's failed transactions since Oct 19: count, fees, error kinds, programs, payer; and the balance check.
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
from collections import Counter
F = json.load(open(OUT + "/failed.json"))
fees = 0; kinds = Counter(); progc = Counter(); payer = Counter(); dsum = 0; logs = Counter(); perday = Counter()
for s in F:
    t = tri.tx(s); ks = keys_of(t); meta = t["meta"]; payer[ks[0] == W] += 1
    i = ks.index(W); d = meta["postBalances"][i] - meta["preBalances"][i]; dsum += d
    e = meta["err"]; ek = json.dumps(e)
    if isinstance(e, dict) and "InstructionError" in e:
        ix, inner = e["InstructionError"]; prog = ks[t["transaction"]["message"]["instructions"][ix]["programIdIndex"]]
        ek = f"{prog[:8]} {json.dumps(inner)}"
    kinds[ek] += 1
    msg = [l for l in meta.get("logMessages") or [] if "Error" in l or "error" in l or "failed" in l]
    if msg: logs[msg[-1][:110]] += 1
    perday[time.strftime("%m-%d", time.gmtime(t["blockTime"]))] += 1
print("failed", len(F), "payer is W", payer[True], "SOL lost (its balance change)", round(dsum / 1e9, 4))
print("per day", sorted(perday.items()))
print("error kinds:"); [print("  ", c, k) for k, c in kinds.most_common(12)]
print("last error log lines:"); [print("  ", c, k) for k, c in logs.most_common(12)]
