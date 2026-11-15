# Step 4b: what the low fee tier is. Adds each buy's quote token (routable.json) to the features, then: the fee tier
# by quote token, and the low-fee copies (bps <= 100) by quote token and by what we pay with.
#   python3 -I quote_look.py SPD SKIPQ
import sys, json, collections
SPD, SKIPQ = sys.argv[1], sys.argv[2]
q = {f"{r['slot']}_{r['mint8']}": (r["quote"][:8], r["frm"][:8]) for r in json.load(open(f"{SPD}/routable.json"))}
D = json.load(open(f"{SKIPQ}/features.json"))
for f in D: f["quote"], f["frm"] = q.get(f["key"], ("?", "?")); f["net"] = (f["net_4"] + f["net_8"] + f["net_slot+1"]) / 3
json.dump([{k: v for k, v in f.items() if k != "net"} for f in D], open(f"{SKIPQ}/features.json", "w"))
g = collections.defaultdict(list)
for f in D: g[f["quote"]].append(f)
print(f"{len(g)} quote tokens. The 14 most used: quote, copies, low-fee copies (bps <= 100), the fee tiers seen, take profits, net (low-fee / others)")
for k, r in sorted(g.items(), key=lambda kv: -len(kv[1]))[:14]:
    lo = [f for f in r if f["bps"] <= 100]; hi = [f for f in r if f["bps"] > 100]
    print(f"   {k} {len(r):4d} {len(lo):3d} | tiers {dict(collections.Counter(f['bps'] for f in r).most_common(4))} | tp {sum(f['why_4'] == 'tp' for f in r):2d} | {sum(f['net'] for f in lo):+6.2f} / {sum(f['net'] for f in hi):+6.2f}")
lo = [f for f in D if f["bps"] <= 100]
print(f"\nthe {len(lo)} low-fee copies are quoted in {len({f['quote'] for f in lo})} tokens; the top: " + ", ".join(f"{k} {n}" for k, n in collections.Counter(f["quote"] for f in lo).most_common(8)))
big = {"3NZ9JMVB", "pumpCmXq", "SPCXxcqX", "So111111"}
for name, r in (("quoted in WBTC / PUMP / SPCX", [f for f in D if f["quote"] in big]), ("quoted in another coin", [f for f in D if f["quote"] not in big])):
    for nm, x in (("bps <= 100", [f for f in r if f["bps"] <= 100]), ("bps > 100", [f for f in r if f["bps"] > 100])):
        if x: print(f"   {name:30s} {nm:10s}: {len(x):3d} copies, {sum(f['why_4'] == 'tp' for f in x):2d} tp, net {sum(f['net'] for f in x):+6.2f} ({100 * sum(f['net'] for f in x) / len(x) / 0.5:+5.1f}% a copy); A/B/C " + " / ".join(f"{sum(f['net'] for f in x if f['blk'] == k):+.2f}" for k in range(3)))
# the fee tier against how far along the curve the coin is, for coins quoted in another coin
oth = [f for f in D if f["quote"] not in big]
print("\ncoins quoted in another coin, by fee tier: copies, median share of the curve sold, median virtual quote reserve in SOL")
import statistics
for b, r in sorted(collections.Counter(f["bps"] for f in oth).items()):
    x = [f for f in oth if f["bps"] == b]
    if len(x) >= 8: print(f"   bps {b:3d}: {len(x):3d} copies, sold {statistics.median(f['sold'] for f in x):.3f}, vq {statistics.median(f['vq_sol'] for f in x):.1f} SOL, its buy moved the price {statistics.median(f['move'] for f in x):.3f}x")
