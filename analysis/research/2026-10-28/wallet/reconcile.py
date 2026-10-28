# Wallet 4's native SOL: checkpoints (rows + failed-tx fees), and what moved it between Oct 19 00:00 and Oct 28 14:54.
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
from collections import Counter
START = 57.870809677   # balance after its last tx before Oct 19 (balance.py)
R = rows(); F = json.load(open(OUT + "/failed.json"))
ev = [(r["bt"], r["s"], r["d"], "row", r) for r in R]
for s in F:
    t = tri.tx(s); ks = keys_of(t); i = ks.index(W)
    ev.append((t["blockTime"], t["slot"], t["meta"]["postBalances"][i] - t["meta"]["preBalances"][i], "failed", None))
ev.sort(key=lambda e: (e[1]))
cps = {"2026-10-27 00:40": 1793061600, "2026-10-28 00:00": 1793145600, "2026-10-28 14:54:39": 1793199279}
b = START * 1e9; done = set()
cat = Counter()
PLAIN = {TOK, T22, "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL", "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr"}
for bt, slot, d, kind, r in ev:
    for k, v in cps.items():
        if bt > v and k not in done: print("balance at", k, "UTC:", round(b / 1e9, 4)); done.add(k)
    b += d
    if kind == "failed": cat["failed-tx fees"] += d
    elif r["sig"] == "375CX8sjWJWjBu6KDvK1MyVHPFfc7fxdUZboRUSrJSw58pERS3W3Ks3BUtnKXtR8bg8apEBa2n8NgLMNbvqnYLGD": cat["5 SOL into the privacy pool"] += d
    elif not r["signer"]: cat["paid by others (pump holder-fee payouts, dust)"] += d
    elif set(r["progs"]) <= PLAIN and r["d"] + r["tok"].get(WSOL, [0])[0] + r["fee"] > 1e7: cat["rent back from closing its token accounts"] += r["d"]
    else: cat["its trading and everything else it signed"] += d
print("balance at the end:", round(b / 1e9, 4))
tot = 0
for k, v in cat.items(): print(f"  {k:52s} {v/1e9:+.3f}"); tot += v
print("  total", round(tot / 1e9, 3))
