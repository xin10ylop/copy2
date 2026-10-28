# Who else tips exactly 1,067,000 or 1,010,000 lamports? Recent transactions to tip accounts of the services wallet 4
# uses (HELIUS x10, ASTRALANE x5, JITO x3): 120 newest signatures each, every tx fetched; tips to that account by amount.
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
acc = [a for a, s in TIPS.items() if s == "HELIUS"][:10] + [a for a, s in TIPS.items() if s == "ASTRALANE"][:5] + [a for a, s in TIPS.items() if s == "JITO"][:3]
sig = []
for a in acc:
    p = tri.sigs(a, limit=120); sig += [(a, x["signature"], x["blockTime"]) for x in p if not x.get("err")]
print("signatures", len(sig), "time span", ts(min(x[2] for x in sig)), "->", ts(max(x[2] for x in sig)), flush=True)
with ThreadPoolExecutor(8) as ex: txs = list(ex.map(lambda x: tri.tx(x[1]), sig))
amt = Counter(); who = defaultdict(Counter); n = 0; payers = set()
for (a, s, bt), t in zip(sig, txs):
    if not t: continue
    ks = keys_of(t); n += 1; payers.add(ks[0])
    for k, src, dst, l, m, d, inn in transfers(t):
        if dst == a: amt[l] += 1; who[l][src] += 1
print("txs", n, "distinct payers", len(payers))
print("top tip amounts:", amt.most_common(12))
for l in (1067000, 1010000): print(l, "lamports from:", dict(who[l]))
json.dump({str(k): dict(v) for k, v in who.items() if k in (1067000, 1010000)}, open(OUT + "/tipscan.json", "w"))
