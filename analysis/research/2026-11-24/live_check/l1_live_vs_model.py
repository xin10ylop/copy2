# The live copies against the model on the same buys, and the copies' result by day (Nov 24; the owner: "none of the
# wallets are making money, double check your pick"). Reads f1_rows.py outputs: the 14-day test copies (../coin_filters/out)
# and a new fetch of Nov 21-24 (out/, `NOSTOP=1 f1_rows.py`). Each unit's coins and live exit; 0.5 SOL a copy = (v + 0.0064)
# x 0.5 - 0.0064 from the 1 SOL result v. Live numbers: the owner's `pnl` paste, Nov 24 evening.
#   python3 -I l1_live_vs_model.py
import json, os, numpy as np, datetime as dt, collections
H = os.path.dirname(os.path.abspath(__file__)); TEST, NEW = f"{H}/../coin_filters/out", f"{H}/out"
U = {"CqCAzte8": ("all", "2026-11-22T08:00", 50, -0.1522), "CgyPomTG": ("all", "2026-11-23T15:26", 11, -0.0119),
     "3XeFcZKS": ("token", "2026-11-23T17:45", 3, -0.1122), "6LwMLkCe": ("token", "2026-11-23T17:45", 1, -0.2558),
     "6nNzEg86": ("token", "2026-11-24T07:45", 0, 0.0), "GqWfqfG6": ("all", "2026-11-24T08:20", 4, -0.3282)}
def vals(path, w, kind):
    d = json.load(open(path)); ex = d["exits"]; et, es = ex.index("tp 3x / 420 s / stall 240"), ex.index("tp 2x / 120 s")
    return [(r, -0.0004 if r["prem"] > 1.5 else r["g"][et if (r["tok"] or w != "CqCAzte8") else es]) for r in d["rows"] if kind == "all" or r["tok"]]
rng = np.random.default_rng(1)
print("1. live against the model on the same buys (since each unit started, UTC); chance of the live count at or under 0 by luck if the test held")
for w, (k, st, nl, pl) in U.items():
    t0 = dt.datetime.fromisoformat(st).replace(tzinfo=dt.UTC).timestamp()
    rv = [(r, v) for r, v in vals(f"{NEW}/{w}.json", w, k) if r["t"] >= t0]; v = np.array([x for _, x in rv]); h = (v + 0.0064) * 0.5 - 0.0064
    tv = np.array([x for _, x in vals(f"{TEST}/{w}.json", w, k)]); th = (tv + 0.0064) * 0.5 - 0.0064
    luck = np.mean([rng.choice(th, nl).sum() <= 0 for _ in range(20000)]) if nl else float("nan")
    print(f"  {w}: model {len(v)} copies {100 * v.mean() if len(v) else 0:+.1f}% a copy, {h.sum():+.2f} SOL at 0.5 | live {nl} trades {pl:+.2f} | test {100 * tv.mean():+.1f}% a copy; luck alone: {luck:.0%}")
print("\n2. % a copy at 1 SOL by day (copies), the test copies and the new fetch together")
days = [f"11-{d:02d}" for d in range(10, 25)]; tot = collections.defaultdict(list)
print(f"  {'wallet':9s} " + " ".join(f"{d[3:]:>8s}" for d in days))
for w, (k, *_ ) in U.items():
    seen = {}
    for p in (f"{TEST}/{w}.json", f"{NEW}/{w}.json"):
        for r, v in vals(p, w, k): seen[(r["m"], r["t"])] = (dt.datetime.fromtimestamp(r["t"], dt.UTC).strftime("%m-%d"), v)
    by = collections.defaultdict(list)
    for dd, v in seen.values(): by[dd].append(v); tot[dd].append(v)
    print(f"  {w:9s} " + " ".join(f"{100 * np.mean(by[d]):+5.0f}({len(by[d]):2d})" if by[d] else "       -" for d in days))
print(f"  {'all six':9s} " + " ".join(f"{100 * np.mean(tot[d]):+5.0f}({len(tot[d]):2d})" if tot[d] else "       -" for d in days))
for a, b in (("11-10", "11-12"), ("11-13", "11-15"), ("11-16", "11-18"), ("11-19", "11-21"), ("11-22", "11-24")):
    v = np.array([x for d in days if a <= d <= b for x in tot[d]]); k = max(1, round(0.02 * len(v)))
    print(f"  {a} to {b}: {len(v)} copies, {100 * v.mean():+.1f}% a copy, without the best 2%: {100 * (v.sum() - np.sort(v)[-k:].sum()) / len(v):+.1f}%")
