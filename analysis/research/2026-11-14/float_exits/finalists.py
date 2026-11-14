# The finalists over all 23.3 days (the unseen week A and the study halves B, C; three_blocks.py): by block without
# the best 2 and the best 5, by landing, days drawn again 10,000 times against the rule live since Nov 14 01:20 UTC
# (tp 3.0, 1200 s, early 30-290), take-profit counts, the worst day and the deepest fall.
#   python3 -I finalists.py SPD
import sys, os, datetime, collections, random
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp(); os.environ["FE_T0"] = str(T0)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:2] + ["0.5"]; import float_exits as F
import lib as L
CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
TB = L.T_STOP; TC = datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp()
blk = lambda r: 0 if r["t"] < TB else 1 if r["t"] < TC else 2
R = lambda tp, hold, b=290: dict(tp=tp, hold=hold, early=(30, b, 1.5), sl=None)
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
C = [("LIVE: tp 3.0, 1200 s", R(3.0, 1200)), ("tp 3.0, 600 s", R(3.0, 600)), ("tp 3.0, 900 s", R(3.0, 900)), ("tp 4.0, 1200 s", R(4.0, 1200)), ("tp 4.0, 900 s", R(4.0, 900)),
     ("tp 4.0, 600 s", R(4.0, 600)), ("tp 4.0, 450 s", R(4.0, 450)), ("tp 4.0, 300 s", R(4.0, 300)), ("tp 3.5, 600 s", R(3.5, 600)), ("tp 5.0, 600 s", R(5.0, 600)),
     ("tp 4.0, 600 s, early 30-330", R(4.0, 600, 330)), ("tp 4.0, 750 s", R(4.0, 750))]
def runs(kw): return [F.sim(F.rows, n, kw, caps=CAPS) for n in L.LAND]
def days_of(full):
    d = collections.defaultdict(float)
    for res in full:
        for r, net, why in res: d[day(r["t"])] += net / 3
    return d
live = days_of(runs(C[0][1])); alld = sorted(live); random.seed(2)
print(f"{len(F.rows)} buys, {len(alld)} Beirut days; early window 30-290 s under 1.5x unless said; A / B / C: net [without the best 2] [without the best 5]")
print(f"   {'rule':28s} | A: unseen week        | B                      | C                      | all    | landing 4 / 8 / late     | tp | worst day | deepest fall | ahead of LIVE in")
for name, kw in C:
    full = runs(kw); cells = []
    for b in range(3):
        v = [sorted((x[1] for x in res if blk(x[0]) == b), reverse=True) for res in full]
        cells.append(f"{sum(sum(x) for x in v) / 3:+6.2f} [{sum(sum(x[2:]) for x in v) / 3:+6.2f}] [{sum(sum(x[5:]) for x in v) / 3:+6.2f}]")
    d = days_of(full); diff = [d[x] - live[x] for x in alld]; wins = sum(sum(random.choice(diff) for _ in diff) > 0 for _ in range(10000))
    dd = worst = 0.0
    for r, net, why in full[0]:
        dd = min(0.0, dd + net); worst = min(worst, dd)
    print(f"   {name:28s} | " + " | ".join(cells) + f" | {sum(d.values()):+6.2f} | " + " / ".join(f"{sum(x[1] for x in res):+6.2f}" for res in full)
          + f" | {sum(sum(1 for x in res if x[2] == 'tp') for res in full) / 3:3.0f} | {min(d.values()):+5.2f}     | {worst:+5.2f}        | " + ("" if name.startswith("LIVE") else f"{wins / 100:5.1f}% of draws, on {sum(1 for x in diff if x > 0)} of {len(diff)} days"))
