# Transactions touching wallet 4 that someone else paid for (Oct 19+): who paid, what program, what wallet 4 got.
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
from collections import Counter, defaultdict
R = rows(); ns = [r for r in R if not r["signer"]]
BY = "BYdq7NJXWHnTzzCogT6VByrPXvUQwkD5PuZQLS8JvZtw"
grp = defaultdict(list)
for r in ns:
    t = tri.rpc("getTransaction", [r["sig"], {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}])
    if t is None: continue
    ks = keys_of(t); cat = "BYdq spam" if BY in r["progs"] else ("pump" if PUMP in r["progs"] else ",".join(p[:8] for p in r["progs"]) or "system only")
    logs = " ".join(l for l in t["meta"].get("logMessages") or [] if "Instruction:" in l)
    grp[cat].append((ks[0], r, logs))
for cat, L in sorted(grp.items(), key=lambda z: -len(z[1])):
    pay = Counter(x[0] for x in L); ins = Counter(x[2][:120] for x in L)
    print(f"\n{cat}: {len(L)} txs, {len(pay)} distinct payers; wallet 4 SOL change sum {sum(x[1]['d'] for x in L)/1e9:+.4f}")
    for p, c in pay.most_common(5): print("   payer", p, c)
    for k, c in ins.most_common(3): print("   ix", c, k)
    toks = Counter(m for x in L for m in x[1]["tok"]); print("   tokens received", toks.most_common(4))
