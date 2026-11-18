# Who buys right after these wallets (Nov 18)? For each wallet, its 5 most frequent co-buyers (within 300 s): in what
# share of its coins, how many BLOCKS after its buy (median: 1-2 = a copy bot reading its block), how often they buy a
# coin BEFORE it does (independent traders do), and whether they follow more than one of our wallets. Also: the
# addresses that appear as "seller" most often overall (a router selling for users hides the user).
import sys, json, gzip, glob, collections, numpy as np
D, WS = sys.argv[1], [w.lower() for w in sys.argv[2:]]; T = json.load(open(f"{D}/topics.json")); FACTORY = "0x7ed598bcef8bd9edd8c97a195c6d13f40801ec7e"
words = lambda d: [int(d[2 + 64 * i: 2 + 64 * (i + 1)], 16) for i in range((len(d) - 2) // 64)]
ETHC, TR, SEEN, sellers, sell_rcpt = set(), collections.defaultdict(list), set(), collections.Counter(), collections.Counter()
for f in glob.glob(f"{D}/logs_*.json.gz"):
    for l in json.load(gzip.open(f)):
        if (l["blockNumber"], l["logIndex"]) in SEEN: continue
        SEEN.add((l["blockNumber"], l["logIndex"])); t0 = l["topics"][0]
        if t0 == T["TokenLaunched"] and l["address"].lower() == FACTORY:
            w = words(l["data"])
            if len(w) >= 3 and w[0] == 0: ETHC.add("0x" + l["topics"][2][-40:])
        elif t0 in (T["CurveBuy"], T["CurveSell"]):
            buy = t0 == T["CurveBuy"]; a1, a2 = "0x" + l["topics"][1][-40:], "0x" + l["topics"][2][-40:]
            if not buy: sellers[a1] += 1; sell_rcpt[a1 == a2] += 1
            TR[l["address"].lower()].append((int(l["blockNumber"], 16), int(l["logIndex"], 16), buy, a2 if buy else a1, a1, a2))
print("CurveSell: seller == recipient in", sell_rcpt[True], "of", sum(sell_rcpt.values()), "sales; the top 5 'sellers':", [(s[:10], n) for s, n in sellers.most_common(5)])
for c in TR: TR[c].sort()
follow = collections.defaultdict(set)
for W in WS:
    coins = []; co = collections.Counter(); delay = collections.defaultdict(list)
    for c in ETHC:
        tr = TR.get(c, []); k = next((j for j, e in enumerate(tr) if e[3] == W and e[2]), None)
        if k is None: continue
        coins.append(c); n0 = tr[k][0]; seen = set()
        for n, i, buy, u, a1, a2 in tr[k + 1:]:
            if n - n0 > 3000: break
            if buy and u != W and u not in seen: seen.add(u); co[u] += 1; delay[u].append(n - n0)
    print(f"\n{W}: {len(coins)} coins; its top co-buyers:")
    for u, n in co.most_common(5):
        follow[u].add(W[:10])
        before = sum(1 for c in ETHC if any(e[3] == u and e[2] for e in TR.get(c, [])) and not any(e[3] == W for e in TR.get(c, [])))
        print(f"   {u}  in {100 * n / len(coins):3.0f}% of its coins, median {np.median(delay[u]):.0f} blocks after it ({np.median(delay[u]) * 0.1026:.1f} s), "
              f"{100 * np.mean(np.array(delay[u]) <= 2):.0f}% within 2 blocks; it also bought {before} coins this wallet never touched")
print("\nco-buyers following more than one of these wallets:", {u[:10]: sorted(v) for u, v in follow.items() if len(v) > 1})
