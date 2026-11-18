# TAB's deployed setting day by day (Nov 18, the owner: "how many tp on average per day, and the worst day?"): e11's
# copies; a copy counts as a take profit when tp 6x changes its result against no tp (the tp fired first), as a share
# of the three landings. SOL per UTC day, 0.5 SOL a copy.
#   PAY=float python3 -I e12_days.py SP WALLET "size,prem,tp,hold,sp,stall,its"
import sys, os, collections, datetime as dt, numpy as np
here = os.path.dirname(os.path.abspath(__file__)); spec = sys.argv[3]; sys.argv = sys.argv[:3] + ["x=" + spec]
src = open(os.path.join(here, "e11_check.py")).read().split("base = None")[0]; exec(src)
z = spec.split(","); X = per_copy(spec); Y = per_copy(",".join(z[:2] + ["none"] + z[3:]))
tp = (np.abs(X - Y) > 1e-9).mean(axis=1); v = X.mean(axis=1); bought = v != 0
day = np.array([dt.datetime.fromtimestamp(t, dt.UTC).strftime("%m-%d") for t in T])
print(f"\n{spec}: per UTC day (copies | take profits | SOL)")
D = sorted(set(day)); sols = []
for d_ in D:
    f = (day == d_) & bought; sols.append(v[f].sum())
    print(f"   {d_}: {f.sum():3d} | {tp[f].sum():4.1f} | {v[f].sum():+6.2f}")
full = D[1:-1]   # the first and last days are partial
fs = np.array([v[(day == d_) & bought].sum() for d_ in full]); ft = np.array([tp[(day == d_) & bought].sum() for d_ in full]); fn = np.array([((day == d_) & bought).sum() for d_ in full])
print(f"full days {full[0]} to {full[-1]} ({len(full)}): copies {fn.mean():.1f} a day, take profits {ft.mean():.2f} a day (all {tp[bought].sum():.1f} of {bought.sum()}),"
      f" SOL {fs.mean():+.2f} a day; worst day {full[int(np.argmin(fs))]} {fs.min():+.2f}, best {full[int(np.argmax(fs))]} {fs.max():+.2f}; days negative {int((fs < 0).sum())} of {len(full)}")
