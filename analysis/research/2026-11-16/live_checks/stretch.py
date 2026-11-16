# How unusual is a stretch of 24 copies at -6.8% a copy (the frozen setup live, #38-#62)? Every copy of the backtest
# (1,238 buys, the live setup, landing 4, every copy) in time order: the mean of each run of 24 consecutive copies, how
# many such runs are as bad, and the results by day, to see whether wallet 4's coins have been getting worse.
#   python3 -I stretch.py CQ ALL > out/stretch.txt
import sys, os, collections
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "buy_pressure")); sys.argv = sys.argv[:3]
import buy_pressure as BP
from buy_pressure import L, ROWS, PREP, EX, R3, rule
from round3 import day
sigs, tp, hold, E = rule()
v = []
for r in ROWS:
    net, why, held = R3.model(PREP[r["key"], 4], EX[r["key"], 4], 0.5, sigs, tp, hold, E)
    if why != "refused": v.append((r["t"], 100 * net / 0.5, why == "tp", day(r["t"])))
x = np.array([q[1] for q in v]); n = len(x)
print(f"{n} copies (landing 4): mean {x.mean():+.1f}% a copy, median {np.median(x):+.1f}%, standard deviation {x.std():.1f} points; {100 * np.mean([q[2] for q in v]):.1f}% take profits")
w = np.array([x[i:i + 24].mean() for i in range(n - 23)])
print(f"runs of 24 consecutive copies ({len(w)}): at -6.8% a copy or worse: {100 * np.mean(w <= -6.8):.1f}%; the worst run {w.min():+.1f}%; 5th percentile {np.percentile(w, 5):+.1f}%; median {np.median(w):+.1f}%")
nt = np.array([sum(q[2] for q in v[i:i + 24]) for i in range(n - 23)])
print(f"runs of 24 with no take profit: {100 * np.mean(nt == 0):.1f}%")
print("by day (Beirut): copies, mean a copy, take profits")
d = collections.defaultdict(list)
for q in v: d[q[3]].append(q)
for k in sorted(d): print(f"   {k}: {len(d[k]):3d} | {np.mean([q[1] for q in d[k]]):+6.1f}% | {sum(q[2] for q in d[k])}")
for N in (50, 100):
    w = np.array([x[i:i + N].mean() for i in range(n - N + 1)])
    print(f"runs of {N} consecutive copies ({len(w)}): 5th percentile {np.percentile(w, 5):+.1f}% a copy, 1st percentile {np.percentile(w, 1):+.1f}%, the worst {w.min():+.1f}%, median {np.median(w):+.1f}%; no take profit in {100 * np.mean(np.array([sum(q[2] for q in v[i:i + N]) for i in range(n - N + 1)]) == 0):.1f}%")
