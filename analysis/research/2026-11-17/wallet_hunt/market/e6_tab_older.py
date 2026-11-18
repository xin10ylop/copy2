# TAB16RxX on 14 more days, no fetch (Nov 18, the owner: "get more days for tab"). The Nov 15 study's data on disk:
# SP/tab/lk/paths (its buys' 31-minute paths, Oct 31 - Nov 15) and SP/tab2/scan_all.out (the bot's own detection over
# its 17,668 transactions with the floats of then: ROUTABLE, the route, the float it pays with). Kept: its ROUTABLE first
# buys of a coin (0.5+ SOL; a rebuy within an hour is not a new copy) BEFORE Nov 14 01:07 UTC, so none is in the 4 days
# that found it. Each path put in the true in-slot order. Our 0.5 SOL at the three landings (hunt_lib), 0.0345 SOL a round
# trip; the deployed exit (tp 3.5x, stall 180, sell pressure 5/60, 600 s, its sale never followed) and e4's 128 settings
# (all four parts free), by week. The rate is its own: its buy's SOL value over its quote paid.
#   python3 -I e6_tab_older.py SP > ../out/e6_tab_older.txt
import sys, os, re, json, gzip, itertools, datetime as dt, numpy as np
SP = sys.argv[1]; PD = f"{SP}/tab/lk/paths"; SCAN = f"{SP}/tab2/scan_all.out"; T_END = 1794618422
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(here, "..")); import hunt_lib as H
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-18/churn"); import slot_order as SO
src = open(os.path.join(here, "e4_tab_grid.py")).read(); ns = {"H": H, "np": np}; exec(src[src.index("def model("):src.index("TPS = ")], ns); model = ns["model"]
TAB = "TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3"; COST = 0.0345 - 0.0026
files = {}
for f in os.listdir(PD):
    s_, m_ = f.split(".")[0].split("_"); files[f"{s_}_{m_[:8]}"] = f
rows = []; last = {}
for l in open(SCAN):
    m = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL from (\S+) quote (\S+) jupiter (\S+): ROUTABLE hops (\d+) how (\S+) .*?input: (\w{8})", l)
    if not m or float(m.group(3)) < 0.5: continue
    key = f"{m.group(1)}_{m.group(2)}"
    if key not in files: continue
    tr = SO.reorder(json.load(gzip.open(f"{PD}/{files[key]}")))
    k = next((i for i, e in enumerate(tr) if e["user"] == TAB and e["buy"] and e["slot"] == int(m.group(1))), None)
    if k is None: continue
    t = tr[k]["t"]
    if t >= T_END: continue
    if m.group(2) in last and t - last[m.group(2)] < 3600: last[m.group(2)] = t; continue
    last[m.group(2)] = t
    rate = float(m.group(3)) * 1e9 / (tr[k]["q"] * (1 + tr[k]["bps"] / 1e4))
    rows.append(dict(t=t, sol=float(m.group(3)), anchor=m.group(9), hops=int(m.group(7)), ps=[H.prep(tr, k, rate, n) for n in (4, 8, "slot+1")]))
rows.sort(key=lambda r: r["t"])
if os.environ.get("FLOAT_ONLY"): rows = [r for r in rows if r["anchor"] != "So111111"]   # FLOAT_ONLY=1: the copies paid with a float (the agreed rule)
G = list(itertools.product((2, 3, 3.5, 4, 6), (0, 60, 120, 180), (None, (3, 30, 30), (5, 60, 30), (10, 60, 30)), (300, 600))); DEP = (3.5, 180, (5, 60, 30), 600)
V = {g: np.array([np.mean([model(p, g[0], g[3], g[2], g[1]) for p in r["ps"]]) - COST for r in rows]) for g in G}
T = np.array([r["t"] for r in rows]); W1 = T < 1793836800   # Nov 6 00:00 UTC: the two weeks' split
def S(v):
    v = np.array(v); n = len(v)
    if not n: return "   0"
    s = np.sort(v); k = max(1, round(0.02 * n)); bs = np.random.default_rng(7).choice(v, size=(10000, n)).mean(axis=1)
    return f"{n:3d} {v.sum():+6.2f} SOL ({100 * v.mean() / 0.5:+6.1f}% a copy) w/o 2% {s[:-k].sum():+6.2f} | won {100 * np.mean(v > 0):3.0f}% | P(mean>0) {100 * np.mean(bs > 0):5.1f}%"
d0, d1 = dt.datetime.fromtimestamp(T.min(), dt.UTC), dt.datetime.fromtimestamp(T.max(), dt.UTC)
np.save(os.environ.get("SAVE", "/dev/null"), V[(3.5, 180, (5, 60, 30), 600)]) if os.environ.get("SAVE") else None
print(f"{'FLOAT-PAID ONLY: ' if os.environ.get('FLOAT_ONLY') else ''}{len(rows)} copies, {d0:%m-%d %H:%M} to {d1:%m-%d %H:%M} UTC (all before the 4 days that found it); weeks split at Nov 6 00:00 UTC")
v = V[DEP]; print(f"\nTHE DEPLOYED EXIT (tp 3.5x, stall 180, sp 5/60, 600 s, its sale never followed):")
print(f"   Oct 31 - Nov 5:  {S(v[W1])}"); print(f"   Nov 6 - Nov 13:  {S(v[~W1])}"); print(f"   all 14 days:     {S(v)}")
both = sum(1 for g in G if V[g][W1].mean() > 0 and V[g][~W1].mean() > 0); allp = sum(1 for g in G if V[g].mean() > 0)
print(f"\nthe {len(G)} settings: positive on both weeks {both}; positive over the 14 days {allp}")
rk = sorted(G, key=lambda g: -min(V[g][W1].mean(), V[g][~W1].mean()))
print("the 8 best by the weaker week:")
for g in rk[:8]: print(f"   tp {g[0]}x, stall {g[1] or 'off'}, sp {'off' if not g[2] else f'{g[2][0]}/{g[2][1]}'}, {g[3]} s | week 1 {100 * V[g][W1].mean() / 0.5:+6.1f}% | week 2 {100 * V[g][~W1].mean() / 0.5:+6.1f}% | all {100 * V[g].mean() / 0.5:+6.1f}%")
print(f"   the deployed one ranks {1 + rk.index(DEP)} of {len(G)}")
print("\nby its buy size (the deployed exit):")
for a, b in ((0.5, 0.75), (0.75, 1.0), (1.0, 1.3), (1.3, 2.0), (2.0, 99)):
    f = np.array([a <= r["sol"] < b for r in rows]); print(f"   {a}-{b} SOL: week 1 {S(v[f & W1])} | week 2 {S(v[f & ~W1])}")
print("\nby the float it pays with (the deployed exit):")
for an in sorted({r["anchor"] for r in rows}):
    f = np.array([r["anchor"] == an for r in rows]); print(f"   {an}: {S(v[f])}")
