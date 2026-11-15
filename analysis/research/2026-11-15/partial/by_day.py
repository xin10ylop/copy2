# The live rule by Beirut day (the owner, Nov 15: "is there any day we ended negative?"): tp 3.0, 600 s, his sale
# followed 30-290 s under 1.5x, no stop; 0.5 SOL, 2 open (SOL 1, WBTC 2, PUMP 1, SPCX 1), raw, each landing.
#   python3 -I by_day.py SPD
import sys, os, datetime, collections
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp(); os.environ["FE_T0"] = str(T0)
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); sys.argv = sys.argv[:2] + ["0.5"]
import float_exits as F
import lib as L
CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}; RULE = dict(tp=3.0, hold=600, early=(30, 290, 1.5), sl=None)
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
D = collections.defaultdict(lambda: [0.0, 0.0, 0.0, 0, 0])
for j, n in enumerate(L.LAND):
    for r, net, why in F.sim(F.rows, n, RULE, caps=CAPS):
        D[day(r["t"])][j] += net
        if j == 0: D[day(r["t"])][3] += why != "refused"; D[day(r["t"])][4] += why == "tp"
print(f"{'day':5s} | landing 4 | landing 8 | one block late | copies, take profits (landing 4)")
for d in sorted(D):
    v = D[d]; print(f"{d} | {v[0]:+8.2f}  | {v[1]:+8.2f}  | {v[2]:+8.2f}       | {v[3]:3d} {v[4]:2d}")
for j, n in enumerate(L.LAND):
    s = sorted(v[j] for d, v in D.items() if d not in ("10-21", min(D), max(D)))
    print(f"landing {n}: full days {len(s)}, negative {sum(1 for x in s if x < 0)}, worst {s[0]:+.2f}, median {s[len(s) // 2]:+.2f}")
