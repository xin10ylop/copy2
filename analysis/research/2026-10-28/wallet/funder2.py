# A wallet's full history (up to CAP signatures): plain transfers (no swap program in the tx) in and out, with
# counterparties, plus a summary of its trading. Usage: funder2.py ADDR [CAP]
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
F = sys.argv[1]; CAP = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
PLAIN = {TOK, T22, "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL", "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr"}
s = []; before = None
while True:
    p = tri.sigs(F, before=before, limit=1000); s += p
    if len(p) < 1000 or len(s) >= CAP: break
    before = p[-1]["signature"]
s.sort(key=lambda x: x["slot"]); full = len(s) < CAP
print(F, "signatures", len(s), "(full history)" if full else f"(capped at {CAP}, newest only)", "first", ts(s[0]["blockTime"]), "last", ts(s[-1]["blockTime"]))
with ThreadPoolExecutor(8) as ex: txs = list(ex.map(lambda x: tri.tx(x["signature"]), s))
flows = []; ntrade = 0; buys = Counter(); payer = Counter()
for x, t in zip(s, txs):
    if not t or t["meta"]["err"]: continue
    pr = set(progs_of(t)); plain = pr <= PLAIN; ks = keys_of(t); payer[ks[0] == F] += 1
    if not plain: ntrade += 1
    for k, a, b, lam, mint, dec, inner in transfers(t):
        if mint not in ("SOL", WSOL) or a == b or lam < 1e7: continue
        if F not in (a, b): continue
        flows.append(dict(bt=x["blockTime"], dir="IN" if b == F else "OUT", cp=a if b == F else b, sol=lam / 1e9, plain=plain, payer=ks[0], sig=x["signature"]))
print("txs with a swap/pump program:", ntrade, " fee payer is the wallet:", payer[True], "other:", payer[False])
pf = [f for f in flows if f["plain"]]
agg = defaultdict(lambda: [0, 0.0]); 
for f in pf: agg[(f["dir"], f["cp"])][0] += 1; agg[(f["dir"], f["cp"])][1] += f["sol"]
print("PLAIN transfers >= 0.01 SOL by counterparty:")
for (d, cp), (n, v) in sorted(agg.items(), key=lambda z: -z[1][1]): print("  ", d, cp, n, round(v, 4))
print("plain IN total", round(sum(f["sol"] for f in pf if f["dir"] == "IN"), 4), " plain OUT total", round(sum(f["sol"] for f in pf if f["dir"] == "OUT"), 4))
for f in pf[:8] + pf[-5:]: print("  ", ts(f["bt"]), f["dir"], f["cp"], round(f["sol"], 4), "payer", f["payer"][:8], f["sig"][:24])
json.dump(dict(n=len(s), full=full, first=s[0]["blockTime"], last=s[-1]["blockTime"], flows=flows), open(OUT + f"/hist_{F[:8]}.json", "w"))
