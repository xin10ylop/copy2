# How much the copied wallets put in (Nov 18): every curve buy of each wallet on ETH-quoted Pons coins, 30 days:
# its first buy on a coin (what we copy) and all its buys (adds included), and its total ETH in a coin.
import sys, json, gzip, glob, collections, numpy as np
D, WS = sys.argv[1], [w.lower() for w in sys.argv[2:]]; T = json.load(open(f"{D}/topics.json")); FACTORY = "0x7ed598bcef8bd9edd8c97a195c6d13f40801ec7e"
words = lambda d: [int(d[2 + 64 * i: 2 + 64 * (i + 1)], 16) for i in range((len(d) - 2) // 64)]
ETHC, BUYS, SEEN = set(), collections.defaultdict(list), set()
for f in glob.glob(f"{D}/logs_*.json.gz"):
    for l in json.load(gzip.open(f)):
        if (l["blockNumber"], l["logIndex"]) in SEEN: continue
        SEEN.add((l["blockNumber"], l["logIndex"])); t0 = l["topics"][0]
        if t0 == T["TokenLaunched"] and l["address"].lower() == FACTORY:
            w = words(l["data"])
            if len(w) >= 3 and w[0] == 0: ETHC.add("0x" + l["topics"][2][-40:])
        elif t0 == T["CurveBuy"]:
            u = "0x" + l["topics"][2][-40:]
            if u in WS: BUYS[u].append((l["address"].lower(), int(l["blockNumber"], 16), int(l["logIndex"], 16), words(l["data"])[0] / 1e18))
q = lambda v: f"median {np.median(v):.3f}, middle half {np.percentile(v, 25):.3f}-{np.percentile(v, 75):.3f}, max {np.max(v):.3f}, mean {np.mean(v):.3f}"
for W in WS:
    b = sorted(x for x in BUYS[W] if x[0] in ETHC); per = collections.defaultdict(list)
    for c, n, i, e in b: per[c].append(e)
    first = [v[0] for v in per.values()]; tot = [sum(v) for v in per.values()]
    print(f"\n{W}: {len(b)} buys on {len(per)} coins ({len(b) / max(1, len(per)):.2f} buys a coin)")
    print(f"   first buy on a coin (ETH): {q(first)}")
    print(f"   every buy (ETH):           {q([e for *_, e in b])}")
    print(f"   total in a coin (ETH):     {q(tot)}; ETH put in over 30 days {sum(tot):.1f}")
    print(f"   first buys by size: " + ", ".join(f"<{x}: {np.mean(np.array(first) < x) * 100:.0f}%" for x in (0.03, 0.05, 0.1, 0.2, 0.5)))
