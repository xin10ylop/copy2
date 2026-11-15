# Step 4d: who makes the coins. Creators of the copied coins (from wallet 4's buy event): how many coins each, the
# copies' results; and the low-fee coins (creator fee <= 100 bps, quoted in another coin) by creator.
#   python3 -I creators.py SKIPQ
import sys, json, collections
D = json.load(open(f"{sys.argv[1]}/features.json"))
for f in D: f["net"] = (f["net_4"] + f["net_8"] + f["net_slot+1"]) / 3; f["low"] = f["bps"] <= 100
g = collections.defaultdict(list)
for f in D: g[f["creator"]].append(f)
print(f"{len(D)} coins by {len(g)} creators; creators with 1 coin: {sum(1 for r in g.values() if len(r) == 1)}; with 5+: {sum(1 for r in g.values() if len(r) >= 5)}")
print("the 15 creators with the most coins: coins, low-fee coins, take profits, net, blocks seen")
for c, r in sorted(g.items(), key=lambda kv: -len(kv[1]))[:15]:
    print(f"   {c[:8]} {len(r):3d} {sum(f['low'] for f in r):3d} {sum(f['why_4'] == 'tp' for f in r):2d} {sum(f['net'] for f in r):+6.2f}  blocks {sorted({'ABC'[f['blk']] for f in r})}  pays {dict(collections.Counter(f['anchor'] for f in r))}")
lo = [f for f in D if f["low"]]; gl = collections.Counter(f["creator"] for f in lo)
print(f"\nthe {len(lo)} low-fee coins come from {len(gl)} creators; the top 5 make {sum(n for _, n in gl.most_common(5))} of them: {[(c[:8], n) for c, n in gl.most_common(5)]}")
rep = [f for f in D if len(g[f["creator"]]) >= 3]; one = [f for f in D if len(g[f["creator"]]) < 3]
for name, r in (("creators with 3+ coins", rep), ("creators with 1-2 coins", one)):
    b = [sum(f["net"] for f in r if f["blk"] == k) for k in range(3)]
    print(f"{name}: {len(r)} copies, {sum(f['why_4'] == 'tp' for f in r)} tp, net {sum(b):+.2f} ({100 * sum(b) / len(r) / 0.5:+.1f}% a copy), A/B/C {b[0]:+.2f} / {b[1]:+.2f} / {b[2]:+.2f}")
# a creator seen before (in an earlier copied coin): does its past result tell?
D.sort(key=lambda f: f["t"]); seen = collections.defaultdict(list); rows = []
for f in D:
    past = seen[f["creator"]]
    rows.append((len(past), sum(past) / len(past) if past else None, f)); seen[f["creator"]].append(f["net"])
for name, sel in (("creator's first coin here", lambda n, m: n == 0), ("creator seen before, its past copies lost on average", lambda n, m: n > 0 and m < 0), ("creator seen before, its past copies won on average", lambda n, m: n > 0 and m >= 0)):
    r = [f for n, m, f in rows if sel(n, m)]; b = [sum(f["net"] for f in r if f["blk"] == k) for k in range(3)]
    print(f"{name}: {len(r)} copies, {sum(f['why_4'] == 'tp' for f in r)} tp, net {sum(b):+.2f} ({100 * sum(b) / max(1, len(r)) / 0.5:+.1f}% a copy), A/B/C {b[0]:+.2f} / {b[1]:+.2f} / {b[2]:+.2f}")
