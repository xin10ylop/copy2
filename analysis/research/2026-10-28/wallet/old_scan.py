# Every transaction of wallet 4 before Oct 19 00:00 UTC: first transactions, SOL in/out with counterparties, programs.
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
import json, collections
from w4lib import *
S = oldsigs(); S.sort(key=lambda x: (x[1], x[0]))
print("signatures before Oct 19:", len(S), "failed", sum(x[3] for x in S), "first", ts(S[0][2]), S[0][0])
prog_c = collections.Counter(); flows = []; first = []
day = collections.Counter(time.strftime("%m-%d", time.gmtime(x[2])) for x in S)
print("per day", dict(sorted(day.items())))
for k, (sig, slot, bt, err) in enumerate(S):
    t = tri.tx(sig)
    if not t: print("missing", sig); continue
    ks = keys_of(t); d = sol_delta(t, W); pr = progs_of(t)
    for p in pr: prog_c[p] += 1
    xs = [x for x in transfers(t) if (x[1] == W) != (x[2] == W) and x[4] in ("SOL", WSOL)]
    if k < 12: first.append((sig, ts(bt), ks[0] == W, d / 1e9, [p[:8] for p in pr], [(x[0], x[1][:8], x[2][:8], x[3] / 1e9) for x in transfers(t)][:6]))
    # plain transfers: no swap programs
    swap = any(p in pr for p in (PUMP, PUMPSWAP, JUP)) or len([p for p in pr if p not in (TOK, T22, "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL", "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr")]) > 0
    for x in xs:
        if x[3] >= 1e9 * 0.05 and not swap:
            flows.append(dict(sig=sig, bt=bt, kind=x[0], src=x[1], dst=x[2], sol=x[3] / 1e9, signer=ks[0], d=d / 1e9))
print("\nfirst 12 transactions:")
for f in first: print(f)
print("\nprograms:", [(p[:8], c) for p, c in prog_c.most_common(25)])
print("\nplain SOL/wSOL transfers >= 0.05 SOL to/from wallet 4 before Oct 19:")
for f in flows: print(ts(f["bt"]), f["kind"], f["src"], "->", f["dst"], round(f["sol"], 4), "payer", f["signer"][:8], f["sig"][:20])
json.dump(flows, open(OUT + "/old_flows.json", "w"))
