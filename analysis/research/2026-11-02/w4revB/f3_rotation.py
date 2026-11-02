# Step 2c: the quote rotation, from wallet 4's own numbers (out/table.json: its net on each launch pick, h9long trips):
# per day, its part-B launch picks and its net by quote token (top quotes), the share of its daily part-B net carried by
# the best quote that day, and whether a quote that led one period kept leading the next.
#   python3 -I f3_rotation.py
import sys, os, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib
T = [t for t in blib.jl(blib.OUT + "/table.json") if t["pick"]]
day = lambda t: time.strftime("%m-%d", time.gmtime(t["cbt"]))
days = sorted({day(t) for t in T})
net = collections.defaultdict(float); cnt = collections.Counter(); bnet = collections.defaultdict(float); bcnt = collections.Counter()
for t in T:
    net[t["qsym"], day(t)] += t["w4net"]; cnt[t["qsym"], day(t)] += 1
    if t["big"]: bnet[t["qsym"], day(t)] += t["w4net"]; bcnt[t["qsym"], day(t)] += 1
tot = collections.Counter()
for t in T: tot[t["qsym"]] += t["w4net"]
n_ = collections.Counter(t["qsym"] for t in T)
top = list(dict.fromkeys([q for q, _ in sorted(tot.items(), key=lambda kv: -abs(kv[1]))[:9]] + [q for q, _ in n_.most_common(6)]))
print("its net (SOL) on its part-B launch picks, by quote and day (UTC), all sizes [count]; Oct 19-22 = P1, Oct 23-26 = P2")
print(f"{'quote':10s} " + " ".join(f"{d:>13s}" for d in days) + f" {'P1':>8s} {'P2':>8s}")
for q in top + ["(rest)"]:
    cells = []
    for d in days:
        if q == "(rest)": v = sum(net[k] for k in net if k[1] == d and k[0] not in top); n = sum(cnt[k] for k in cnt if k[1] == d and k[0] not in top)
        else: v = net[q, d]; n = cnt[q, d]
        cells.append(f"{v:+7.2f} [{n:3d}]")
    p1 = sum(net[k] for k in net if (k[0] == q or (q == "(rest)" and k[0] not in top)) and k[1] <= "10-22")
    p2 = sum(net[k] for k in net if (k[0] == q or (q == "(rest)" and k[0] not in top)) and k[1] > "10-22")
    print(f"{q:10s} " + " ".join(f"{c:>13s}" for c in cells) + f" {p1:+8.2f} {p2:+8.2f}")
print(f"{'all':10s} " + " ".join(f"{sum(net[k] for k in net if k[1] == d):+7.2f} [{sum(cnt[k] for k in cnt if k[1] == d):3d}]" for d in days))
print("\nits 1.45+ SOL picks only:")
print(f"{'quote':10s} " + " ".join(f"{d:>13s}" for d in days))
for q in top:
    print(f"{q:10s} " + " ".join(f"{bnet[q, d]:+7.2f} [{bcnt[q, d]:3d}]" for d in days))
print(f"{'all':10s} " + " ".join(f"{sum(bnet[k] for k in bnet if k[1] == d):+7.2f} [{sum(bcnt[k] for k in bcnt if k[1] == d):3d}]" for d in days))
print("\nthe best quote each day and its share of that day's part-B net (all sizes):")
for d in days:
    row = sorted(((net[k], k[0]) for k in net if k[1] == d), reverse=True)
    dn = sum(v for v, _ in row)
    print(f"  {d}: day net {dn:+7.2f}; best {row[0][1]} {row[0][0]:+.2f}, 2nd {row[1][1]} {row[1][0]:+.2f}, worst {row[-1][1]} {row[-1][0]:+.2f}")
# does a quote's P1 sign carry to P2?
print("\nquotes with 10+ picks in both periods: its net per pick P1 -> P2")
for q in sorted({t["qsym"] for t in T}):
    a = [t["w4net"] for t in T if t["qsym"] == q and t["per"] == "P1"]; b = [t["w4net"] for t in T if t["qsym"] == q and t["per"] == "P2"]
    if len(a) >= 10 and len(b) >= 10: print(f"  {q:10s} P1 {sum(a):+7.2f} on {len(a):3d} ({sum(a) / len(a):+.3f} a pick) -> P2 {sum(b):+7.2f} on {len(b):3d} ({sum(b) / len(b):+.3f})")
