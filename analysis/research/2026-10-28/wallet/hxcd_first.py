# HxcdEi6C (wallet 4's probable predecessor): its first 400 transactions: funding and when it started trading.
# Then a sample of 1,500 random signatures over its whole life: deposits/withdrawals (SOL+wSOL >= 0.5 with no other token).
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
import random
from concurrent.futures import ThreadPoolExecutor
A = "HxcdEi6CWzQtPCmM8E2maEZ3oYVGZxESqCWU1iPzmhVW"
S = sorted(json.load(open(OUT + "/sigs_HxcdEi6C_full.json")), key=lambda x: x[1])
print("signatures", len(S), "first", ts(S[0][2]), S[0][0][:20], "last", ts(S[-1][2]))
def flows(sel):
    with ThreadPoolExecutor(8) as ex: txs = list(ex.map(lambda x: tri.tx(x[0]), sel))
    out = []
    for x, t in zip(sel, txs):
        if not t or t["meta"]["err"]: continue
        ks = keys_of(t)
        if A not in ks: continue
        i = ks.index(A); td = {}
        for side, sg in (("preTokenBalances", -1), ("postTokenBalances", 1)):
            for b in t["meta"].get(side) or []:
                if b.get("owner") == A: td[b["mint"]] = td.get(b["mint"], 0) + sg * int(b["uiTokenAmount"]["amount"])
        td = {k: v for k, v in td.items() if v}
        net = t["meta"]["postBalances"][i] - t["meta"]["preBalances"][i] + td.get(WSOL, 0) + (t["meta"]["fee"] if ks[0] == A else 0)
        if abs(net) >= 5e8 and not [m for m in td if m != WSOL]:
            ch = [(ks[j], t["meta"]["postBalances"][j] - t["meta"]["preBalances"][j]) for j in range(len(t["meta"]["preBalances"]))]
            cp = (min if net > 0 else max)(ch, key=lambda z: z[1])
            out.append((x[2], net / 1e9, cp[0], ks[0], [p[:8] for p in progs_of(t)], x[0]))
    return out, txs
first, ftx = flows(S[:400])
t0 = ftx[0]; i = keys_of(t0).index(A); print("balance before its first tx:", t0["meta"]["preBalances"][i] / 1e9)
pumpstart = next((ts(x[2]) for x, t in zip(S[:400], ftx) if t and PUMP in keys_of(t)), None); print("first pump tx among the first 400:", pumpstart)
print("deposits/withdrawals in the first 400:"); [print("  ", ts(r[0]), f"{r[1]:+.3f}", r[2], "payer", r[3][:8], r[4], r[5][:20]) for r in first]
random.seed(4); smp = random.sample(S[400:-2000], 1500)
mid, _ = flows(sorted(smp, key=lambda x: x[1]))
print("deposits/withdrawals in a random 1,500 of the middle (Jul 27 + 400 .. Oct 15):"); [print("  ", ts(r[0]), f"{r[1]:+.3f}", r[2], "payer", r[3][:8], r[4], r[5][:20]) for r in mid]
