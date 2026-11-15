# Step 4: the fee tier (bps = protocol fee + creator fee of wallet 4's own buy, from the trade event) looked at
# closely: every value, the copies, take profits, net by block, what we pay with, how far along the curve, and the
# fee split (protocol / creator) read from its buy's event.
#   python3 -I bps_look.py SKIPQ
import sys, json, collections, statistics
D = json.load(open(f"{sys.argv[1]}/features.json"))
for f in D: f["net"] = (f["net_4"] + f["net_8"] + f["net_slot+1"]) / 3
g = collections.defaultdict(list)
for f in D: g[f["bps"]].append(f)
print(f"{'bps':>5s} {'copies':>6s} {'tp':>3s} | A      B      C     | all    | a copy | pays with (SOL/WBTC/PUMP/SPCX) | curve sold, median | its buy SOL, median | days seen")
for b in sorted(g):
    r = g[b]; bl = [sum(f["net"] for f in r if f["blk"] == k) for k in range(3)]; a = collections.Counter(f["anchor"] for f in r)
    print(f"{b:5d} {len(r):6d} {sum(f['why_4'] == 'tp' for f in r):3d} | {bl[0]:+6.2f} {bl[1]:+6.2f} {bl[2]:+6.2f} | {sum(bl):+6.2f} | {100 * sum(bl) / len(r) / 0.5:+6.1f}% | {a['SOL']:3d} {a['WBTC']:3d} {a['PUMP']:3d} {a['SPCX']:3d}              | {statistics.median(f['sold'] for f in r):.3f}              | {statistics.median(f['sol'] for f in r):.2f}                | {len({f['day'] for f in r})}")
lo = [f for f in D if f["bps"] <= 100]; hi = [f for f in D if f["bps"] > 100]
for name, r in (("bps <= 100", lo), ("bps > 100", hi)):
    for a in ("SOL", "WBTC", "PUMP", "SPCX"):
        x = [f for f in r if f["anchor"] == a]
        if x: print(f"{name:10s} {a:4s}: {len(x):3d} copies, {sum(f['why_4'] == 'tp' for f in x):2d} tp, net {sum(f['net'] for f in x):+6.2f} ({100 * sum(f['net'] for f in x) / len(x) / 0.5:+5.1f}% a copy); A/B/C " + " / ".join(f"{sum(f['net'] for f in x if f['blk'] == k):+.2f}" for k in range(3)))
print("\nbps <= 100 by day: " + "  ".join(f"{d} {len(v)} {sum(f['net'] for f in v):+.2f}" for d, v in sorted(collections.OrderedDict((d, [f for f in lo if f['day'] == d]) for d in sorted({f['day'] for f in lo})).items())))
print("its 4 take profits:", [(f["key"], f["anchor"], round(f["net"], 2)) for f in lo if f["why_4"] == "tp"])
w = [f["peak_4"] for f in lo]; w2 = [f["peak_4"] for f in hi]
print(f"peak within 600 s, median: bps <= 100 {statistics.median(w):.2f}x, others {statistics.median(w2):.2f}x; share reaching 2x: {100 * sum(1 for x in w if x >= 2) / len(w):.0f}% vs {100 * sum(1 for x in w2 if x >= 2) / len(w2):.0f}%")
