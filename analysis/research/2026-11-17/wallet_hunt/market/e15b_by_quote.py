# TAB's backtest copies by quote token and by day (Nov 18): did the copies of TTWO-priced coins, its main quote since
# Nov 15, ever make money?
import sys, os, collections, numpy as np, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); spec = sys.argv[3]; sys.argv = sys.argv[:3] + ["x=" + spec]
exec(open(os.path.join(here, "e11_check.py")).read().split("base = None")[0])
v = per_copy(spec).mean(axis=1); Q = np.array([r["q"] for r in rows]); day = np.array([dt.datetime.fromtimestamp(t, dt.UTC).strftime("%m-%d") for t in T])
print(f"\n{spec}: by quote token (copies, SOL, a copy, won)")
for q, n in collections.Counter(Q).most_common(12):
    f = Q == q; print(f"   {q}: {n:4d} {v[f].sum():+6.2f} {100 * v[f].mean() / 0.5:+6.1f}% {100 * np.mean(v[f] > 0):3.0f}%")
print("TTWofwAg by day:", " ".join(f"{d_} {int(((day == d_) & (Q == 'TTWofwAg')).sum())}/{v[(day == d_) & (Q == 'TTWofwAg')].sum():+.2f}" for d_ in sorted(set(day))))
