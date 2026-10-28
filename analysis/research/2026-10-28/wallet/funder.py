# The first funder 8h5eizMg: all its transactions (114), where its SOL came from and where it went.
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
from collections import defaultdict, Counter
F = sys.argv[1] if len(sys.argv) > 1 else "8h5eizMgJ14dpEht6YfcMwYhZwiD2q88BFM4FNPdSbsx"
s = []; before = None
while True:
    p = tri.sigs(F, before=before, limit=1000); s += p
    if len(p) < 1000: break
    before = p[-1]["signature"]
    if len(s) >= 5000: print("capped at 5000"); break
s.sort(key=lambda x: x["slot"])
print(F, "signatures", len(s), "first", ts(s[0]["blockTime"]), "last", ts(s[-1]["blockTime"]))
ins = defaultdict(float); outs = defaultdict(float); nin = Counter(); nout = Counter(); progs = Counter(); rows_ = []
for x in s:
    t = tri.tx(x["signature"])
    if not t or t["meta"]["err"]: continue
    for p in progs_of(t): progs[p] += 1
    for k, a, b, lam, mint, dec, inner in transfers(t):
        if mint not in ("SOL", WSOL) or a == b: continue
        if b == F: ins[a] += lam / 1e9; nin[a] += 1; rows_.append((x["blockTime"], "IN ", a, lam / 1e9, x["signature"]))
        elif a == F: outs[b] += lam / 1e9; nout[b] += 1; rows_.append((x["blockTime"], "OUT", b, lam / 1e9, x["signature"]))
print("programs", [(p[:10], c) for p, c in progs.most_common(10)])
print("IN by sender:"); [print("  ", a, round(v, 4), nin[a]) for a, v in sorted(ins.items(), key=lambda z: -z[1])]
print("OUT by receiver (top 40):"); [print("  ", a, round(v, 4), nout[a]) for a, v in sorted(outs.items(), key=lambda z: -z[1])[:40]]
print("receivers", len(outs), "total out", round(sum(outs.values()), 3), "total in", round(sum(ins.values()), 3))
print("first 15 flows:"); [print("  ", ts(r[0]), r[1], r[2], round(r[3], 4), r[4][:20]) for r in rows_[:15]]
json.dump(dict(sigs=len(s), ins=ins, outs=outs, nin=nin, nout=nout, flows=rows_), open(OUT + f"/funder_{F[:8]}.json", "w"))
