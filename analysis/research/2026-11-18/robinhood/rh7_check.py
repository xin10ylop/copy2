# Who are these wallets, and are the buyers after them real? (Nov 18; the owner: "what is their average holding
# time, have you checked that outsiders are buying normally, like on SOL?") From the logs on disk, per wallet, its
# first buys of 0.03+ ETH on ETH-quoted Pons curves:
# - its own hold: first buy to first sale (median, quartiles), coins never sold in the data, sold within 10 / 30 s;
# - the coins' creators: how often it bought its own launch, how many different creators, the top creator's share;
# - the buyers after it (to 300 s): distinct other buyers and ETH from them (median), and the RING test: the 20 wallets
#   that most often buy after it, and in what share of its coins any of them buys (a ring of the same wallets in most
#   of its coins = coordinated buying, not outside demand); the same for a random sample of other coins, for scale.
import sys, json, gzip, glob, bisect, collections, random, numpy as np
D, WS = sys.argv[1], [w.lower() for w in sys.argv[2:]]
T = json.load(open(f"{D}/topics.json")); B = {int(k): v for k, v in json.load(open(f"{D}/blocks.json")).items()}; bk = sorted(B)
FACTORY = "0x7ed598bcef8bd9edd8c97a195c6d13f40801ec7e"
def tm(n):
    i = min(max(bisect.bisect_left(bk, n), 1), len(bk) - 1); a, b = bk[i - 1], bk[i]; return B[a] + (B[b] - B[a]) * (n - a) / max(1, b - a)
words = lambda d: [int(d[2 + 64 * i: 2 + 64 * (i + 1)], 16) for i in range((len(d) - 2) // 64)]
L, TR, SEEN = {}, collections.defaultdict(list), set()
for f in glob.glob(f"{D}/logs_*.json.gz"):
    for l in json.load(gzip.open(f)):
        if (l["blockNumber"], l["logIndex"]) in SEEN: continue
        SEEN.add((l["blockNumber"], l["logIndex"])); t0 = l["topics"][0]
        if t0 == T["TokenLaunched"] and l["address"].lower() == FACTORY:
            w = words(l["data"])
            if len(w) >= 3 and w[0] == 0: L["0x" + l["topics"][2][-40:]] = dict(dep="0x" + l["topics"][3][-40:], n=int(l["blockNumber"], 16))
        elif t0 in (T["CurveBuy"], T["CurveSell"]):
            buy = t0 == T["CurveBuy"]; w = words(l["data"])
            TR[l["address"].lower()].append((int(l["blockNumber"], 16), int(l["logIndex"], 16), buy, "0x" + (l["topics"][2] if buy else l["topics"][1])[-40:], (w[0] if buy else w[1]) / 1e18))
for c in TR: TR[c].sort()
def after(c, k, W):   # the other buyers in the 300 s after its buy
    t0 = tm(TR[c][k][0]); out = collections.Counter()
    for n, i, buy, u, q in TR[c][k + 1:]:
        if tm(n) - t0 > 300: break
        if buy and u != W: out[u] += q
    return out
def report(W, coins):
    holds, never, own, deps, nb, eth, cob = [], 0, 0, collections.Counter(), [], [], collections.Counter()
    for c, k in coins:
        tr = TR[c]; t0 = tm(tr[k][0]); fs = next((tm(n) for n, i, buy, u, q in tr[k + 1:] if u == W and not buy), None)
        if fs is None: never += 1
        else: holds.append(fs - t0)
        own += L[c]["dep"] == W; deps[L[c]["dep"]] += 1
        a = after(c, k, W); nb.append(len(a)); eth.append(sum(a.values())); cob.update(set(a))
    top = [u for u, _ in cob.most_common(20)]; ring = sum(any(u in set(after(c, k, W)) for u in top) for c, k in coins)
    h = np.array(holds) if holds else np.array([np.nan])
    print(f"  coins {len(coins)} | its hold: median {np.nanmedian(h):.0f} s (quartiles {np.nanpercentile(h, 25):.0f} - {np.nanpercentile(h, 75):.0f} s), mean {np.nanmean(h):.0f} s; never sold in the data {never}; sold within 10 s {np.mean(h <= 10) * 100:.0f}%, within 30 s {np.mean(h <= 30) * 100:.0f}%")
    print(f"  creators: its own launches {own} ({100 * own / len(coins):.0f}%), {len(deps)} different creators, the top creator {deps.most_common(1)[0][1]} coins ({100 * deps.most_common(1)[0][1] / len(coins):.0f}%)")
    print(f"  buyers after it (300 s): median {np.median(nb):.0f} other wallets, {np.median(eth):.3f} ETH; the 20 most frequent co-buyers appear in {100 * ring / len(coins):.0f}% of its coins; the most frequent one in {100 * cob.most_common(1)[0][1] / len(coins):.0f}%")
for W in WS:
    coins = []
    for c in L:
        tr = TR.get(c, []); k = next((j for j, e in enumerate(tr) if e[3] == W and e[2]), None)
        if k is not None and tr[k][4] >= 0.03: coins.append((c, k))
    print(f"\n{W}"); report(W, coins) if coins else print("  none")
print("\nFOR SCALE, random coins (a random buyer of 0.03+ ETH on each, 400 coins):")
random.seed(7); pool = [c for c in L if len(TR.get(c, [])) > 5]; rows = []
for c in random.sample(pool, min(400, len(pool))):
    ks = [j for j, e in enumerate(TR[c]) if e[2] and e[4] >= 0.03]
    if ks: k = random.choice(ks); rows.append((c, k, TR[c][k][3]))
nb = [len(after(c, k, u)) for c, k, u in rows]; eth = [sum(after(c, k, u).values()) for c, k, u in rows]
print(f"  median {np.median(nb):.0f} other buyers and {np.median(eth):.3f} ETH in the 300 s after a buy")
