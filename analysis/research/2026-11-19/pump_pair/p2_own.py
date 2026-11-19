# The 8zqsUMty + FDhoU1DE trader's own pump trades (p1_fetch), as one trader: per coin, SOL out of its sales minus SOL
# into its buys (quote tokens at SP/market/prices.json, Nov 17-18; tokens still held count as 0, so a coin it still
# holds reads as a loss), by UTC day; sizes, coins, how many coins both wallets bought.
#   python3 -I p2_own.py SP > out/p2_own.txt
import sys, os, json, collections, datetime as dt, numpy as np
SP = sys.argv[1]; O = f"{SP}/pair"; PR = json.load(open(f"{SP}/market/prices.json")); WSOL = "So11111111111111111111111111111111111111112"
sol_usd = PR[WSOL]["usdPrice"]; SOLQ = {WSOL, "11111111111111111111111111111111", None}
def rate(q): return 1.0 if q in SOLQ else (PR[q]["usdPrice"] / sol_usd * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None)
coin = collections.defaultdict(lambda: dict(spent=0.0, got=0.0, tok=0.0, t=None, who=set(), quote=None, nb=0, ns=0)); unpriced = 0; failed = 0
for w in ("8zqsUMty", "FDhoU1DE"):
    for l in open(f"{O}/{w}_trades.jsonl"):
        x = json.loads(l)
        if x["trades"] is None: failed += 1; continue
        for e in x["trades"]:
            r = rate(e["quote"])
            if r is None: unpriced += 1; continue
            c = coin[e["m"]]; c["who"].add(w); c["quote"] = (e["quote"] or "SOL")[:8]
            if e["buy"]: c["spent"] += e["q"] * (1 + e["bps"] / 1e4) * r / 1e9; c["tok"] += e["tok"]; c["nb"] += 1; c["t"] = min(c["t"] or e["t"], e["t"])
            else: c["got"] += e["q"] * (1 - e["bps"] / 1e4) * r / 1e9; c["tok"] -= e["tok"]; c["ns"] += 1
C = {m: c for m, c in coin.items() if c["spent"] > 0}
print(f"{len(C)} coins bought; transactions unread {failed}; trades in an unpriced quote {unpriced}")
print(f"quotes: {collections.Counter(c['quote'] for c in C.values()).most_common(6)}; bought by both wallets: {sum(1 for c in C.values() if len(c['who']) == 2)}")
print(f"size a coin (SOL): median {np.median([c['spent'] for c in C.values()]):.2f}; coins still held (no sale): {sum(1 for c in C.values() if c['ns'] == 0)}")
d = collections.defaultdict(list)
for c in C.values(): d[dt.datetime.fromtimestamp(c["t"], dt.UTC).strftime("%m-%d")].append(c["got"] - c["spent"])
print("\nday    coins  net SOL   won  big (+100%)  best coin")
for k in sorted(d):
    v = np.array(d[k]); sp = [c["spent"] for c in C.values() if dt.datetime.fromtimestamp(c["t"], dt.UTC).strftime("%m-%d") == k]
    big = sum(1 for c in C.values() if dt.datetime.fromtimestamp(c["t"], dt.UTC).strftime("%m-%d") == k and c["got"] >= 2 * c["spent"])
    print(f"{k}  {len(v):5d}  {v.sum():+8.2f}  {int((v > 0).sum()):4d}  {big:5d}       {v.max():+.2f}")
allv = np.array([c["got"] - c["spent"] for c in C.values()])
print(f"\ntotal {allv.sum():+.2f} SOL on {len(allv)} coins; without its best 5 {np.sort(allv)[:-5].sum():+.2f}; days up {sum(1 for k in d if sum(d[k]) > 0)} of {len(d)}")
