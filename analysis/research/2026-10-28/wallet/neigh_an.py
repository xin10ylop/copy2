# Tabulate the other buyers around wallet 4's 40 sampled buys (neigh.json): position relative to its buy.
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
from collections import Counter, defaultdict
N = json.load(open(OUT + "/neigh.json"))
pos = defaultdict(Counter); coins = defaultdict(set); tipamt = defaultdict(Counter); nonce = defaultdict(Counter); payer_of = defaultdict(Counter)
found = 0; tot = Counter()
for e in N:
    me = [x for x in e["txs"] if x["sig"] == e["sig"]]
    if not me: continue
    found += 1; mi = me[0]["i"]
    for x in e["txs"]:
        if x["sig"] == e["sig"] or x["err"]: continue
        buyers = {t[1] for t in x["tr"] if t[2] == 1 and t[0] == e["mint"]}
        sellers = {t[1] for t in x["tr"] if t[2] == 0 and t[0] == e["mint"]}
        for u in buyers:
            if u == W: continue
            if x["off"] < 0: p = f"slot {x['off']}"
            elif x["off"] == 0: p = "same slot, before" if x["i"] < mi else "same slot, after"
            else: p = f"slot +{x['off']}"
            pos[u][p] += 1; coins[u].add(e["mint"]); tot[p] += 1; payer_of[u][x["payer"] == u] += 1
            for s, l in x["tips"]: tipamt[u][l] += 1
            nonce[u][x["nonce"]] += 1
print("buys with its own tx found in the curve list:", found, "of", len(N))
print("other buys by position:", dict(tot))
ORDER = ["slot -2", "slot -1", "same slot, before", "same slot, after", "slot +1", "slot +2"]
top = sorted(pos, key=lambda u: (-len(coins[u]), -sum(pos[u].values())))[:20]
print(f"{'wallet':45s} coins  " + "  ".join(f"{o[:14]:>14s}" for o in ORDER) + "  nonce  tips")
for u in top:
    print(f"{u:45s} {len(coins[u]):5d}  " + "  ".join(f"{pos[u][o]:14d}" for o in ORDER) + f"  {nonce[u][True]}/{sum(nonce[u].values())}  {tipamt[u].most_common(2)}")
json.dump(dict(top=top, pos={u: dict(pos[u]) for u in top}, coins={u: len(coins[u]) for u in top}), open(OUT + "/neigh_top.json", "w"))
# same-slot-before repeat offenders (possible leaders)
lead = sorted(pos, key=lambda u: -(pos[u]["same slot, before"] + pos[u]["slot -1"] + pos[u]["slot -2"]))[:8]
print("\nmost often BEFORE wallet 4 (slot -2/-1/same-before):", [(u[:8], pos[u]["slot -2"] + pos[u]["slot -1"] + pos[u]["same slot, before"], len(coins[u])) for u in lead])
print("wallets that bought on more than one of the 40 coins:", sum(1 for u in pos if len(coins[u]) > 1), " on 1 coin only:", sum(1 for u in pos if len(coins[u]) == 1))
