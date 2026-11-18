# Real proof (Nov 18): do the copy bots already following our candidates make money? Their own result on every
# ETH-quoted Pons curve they bought (curve trades only: sales + what they still hold at the coin's last curve price,
# 0.9 of it), split by whether the coin was one the followed wallet had bought first; by half.
import sys, json, gzip, glob, bisect, collections, numpy as np
D = sys.argv[1]; PAIRS = [p.split(":") for p in sys.argv[2:]]   # copier:leader
T = json.load(open(f"{D}/topics.json")); B = {int(k): v for k, v in json.load(open(f"{D}/blocks.json")).items()}; bk = sorted(B); FACTORY = "0x7ed598bcef8bd9edd8c97a195c6d13f40801ec7e"
def tm(n):
    i = min(max(bisect.bisect_left(bk, n), 1), len(bk) - 1); a, b = bk[i - 1], bk[i]; return B[a] + (B[b] - B[a]) * (n - a) / max(1, b - a)
words = lambda d: [int(d[2 + 64 * i: 2 + 64 * (i + 1)], 16) for i in range((len(d) - 2) // 64)]
ETHC, TR, SEEN = set(), collections.defaultdict(list), set()
for f in glob.glob(f"{D}/logs_*.json.gz"):
    for l in json.load(gzip.open(f)):
        if (l["blockNumber"], l["logIndex"]) in SEEN: continue
        SEEN.add((l["blockNumber"], l["logIndex"])); t0 = l["topics"][0]
        if t0 == T["TokenLaunched"] and l["address"].lower() == FACTORY:
            w = words(l["data"])
            if len(w) >= 3 and w[0] == 0: ETHC.add("0x" + l["topics"][2][-40:])
        elif t0 in (T["CurveBuy"], T["CurveSell"]):
            buy = t0 == T["CurveBuy"]; w = words(l["data"])
            TR[l["address"].lower()].append((int(l["blockNumber"], 16), int(l["logIndex"], 16), buy, "0x" + (l["topics"][2] if buy else l["topics"][1])[-40:], (w[0] if buy else w[1]) / 1e18, (w[1] if buy else w[0]) / 1e18))
for c in TR: TR[c].sort()
SPLIT = 1793788260
for cp, ld in PAIRS:
    res = collections.defaultdict(list)
    for c in ETHC:
        tr = TR.get(c, [])
        if not any(e[3] == cp for e in tr): continue
        last = tr[-1]; px = last[4] / last[5] if last[5] else 0; inn = out = tok = 0.0; t0 = None
        for n, i, buy, u, q, tk in tr:
            if u != cp: continue
            if buy: inn += q; tok += tk; t0 = t0 or tm(n)
            else: out += q; tok -= tk
        if not inn: continue
        jl = next((j for j, e in enumerate(tr) if e[3] == ld and e[2]), None); jc = next((j for j, e in enumerate(tr) if e[3] == cp and e[2]), None)
        kind = "after the leader" if jl is not None and jl < jc else "other coins"
        res[(kind, "older" if t0 < SPLIT else "newer")].append(out + max(0, tok) * px * 0.9 - inn)
    print(f"\ncopier {cp} following {ld}:")
    for kind in ("after the leader", "other coins"):
        for h in ("older", "newer"):
            v = np.array(res[(kind, h)])
            if len(v): print(f"   {kind:16s} {h} half: {len(v):4d} coins, its result {v.sum():+.4f} ETH, won {100 * np.mean(v > 0):.0f}%")
