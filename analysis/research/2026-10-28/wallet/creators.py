# 50 random other-quote coins wallet 4 bought (Oct 19-28): the creator; the creator's funding (first SOL in, from its
# oldest signatures, up to 5 pages back); whether wallet 4 / 8h5eizMg / HxcdEi6C / the privacy pool ever appear in the
# creator's oldest 1,000 or newest 1,000 transactions' plain SOL transfers; and wallet 4's buy slot vs the curve's first slot.
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
from pda import bonding_curve
import random
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
SET = {W: "wallet4", "8h5eizMgJ14dpEht6YfcMwYhZwiD2q88BFM4FNPdSbsx": "8h5eizMg", "HxcdEi6CWzQtPCmM8E2maEZ3oYVGZxESqCWU1iPzmhVW": "HxcdEi6C", "4AV2Qzp3N4c9RfzyEbNZs2wqWfW4EwKnnxFAZCndvfGh": "privacy pool"}
R = rows(); INIT = 1073000000 * 10**6
oq = []
for r in R:
    for t in r["tr"]:
        if t[1] == W and t[2] == 1 and t[5] == 0: oq.append((r, t)); break
random.seed(9); smp = random.sample(oq, 50)
def oldest(addr, pages=5):
    before = None; last = []
    for k in range(pages):
        p = tri.sigs(addr, before=before, limit=1000)
        if not p: break
        last = p
        if len(p) < 1000: return p, True
        before = p[-1]["signature"]
    return last, False
out = []
for k, (r, t) in enumerate(smp):
    mint, creator = t[0], t[8]; curve = bonding_curve(mint)
    cs, full = oldest(curve, 5); first_slot = min(x["slot"] for x in cs) if cs and full else None
    os_, cfull = oldest(creator, 3)
    olds = sorted(os_, key=lambda x: x["slot"])[:15]
    with ThreadPoolExecutor(5) as ex: txs = list(ex.map(lambda x: tri.tx(x["signature"]), olds))
    funders = []; hits = set()
    for x, tx in zip(olds, txs):
        if not tx: continue
        for kk, a, b, l, m, d, inn in transfers(tx):
            if b == creator and a != creator and m in ("SOL", WSOL) and l >= 1e7: funders.append((a, round(l / 1e9, 3)))
        for a in keys_of(tx):
            if a in SET: hits.add(SET[a])
    new = tri.sigs(creator, limit=200)
    with ThreadPoolExecutor(5) as ex: ntx = list(ex.map(lambda x: tri.tx(x["signature"]), new[:60]))
    for tx in ntx:
        if not tx: continue
        for kk, a, b, l, m, d, inn in transfers(tx):
            if a in SET and b == creator: hits.add(SET[a] + "->creator")
    pre_vtok = t[6] + t[4]
    out.append(dict(mint=mint, creator=creator, buy_slot=r["s"], first_slot=first_slot, curve_full=full, first_trade=pre_vtok == INIT,
                    creator_sigs_full=cfull, creator_first=ts(olds[0]["blockTime"]) if olds else None, funders=funders[:3], hits=sorted(hits)))
    print(k, mint[:8], "creator", creator[:8], "buy-first slot", (r["s"] - first_slot) if first_slot else "n/a", "first trade" if pre_vtok == INIT else "", "funders", funders[:2], "hits", sorted(hits), flush=True)
json.dump(out, open(OUT + "/creators.json", "w"))
d = Counter((o["buy_slot"] - o["first_slot"]) if o["first_slot"] else "n/a" for o in out)
print("buy slot minus curve's first slot:", sorted(d.items(), key=lambda z: (isinstance(z[0], str), z[0])))
print("creators with any link hit:", sum(1 for o in out if o["hits"]))
fc = Counter(f[0] for o in out for f in o["funders"]); print("funders seen more than once:", [(a[:8], c) for a, c in fc.most_common(8) if c > 1])
