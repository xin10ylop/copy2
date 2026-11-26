# Each wallet's smaller buys copied (s1_replay.sh's saved copies): per band, copies, % a copy, without the best 2%, the 4
# time blocks, the two halves (pick on one, score on the other: a band is kept only when both halves are positive),
# the share of the result from its best 5 copies, the win rate, and the days up.
#   python3 -I s2_dig.py OUT_DIR
import sys, json, glob, os, datetime as dt, numpy as np, collections
O = sys.argv[1]
def wo2(v): k = max(1, round(0.02 * len(v))); return v.sum() - np.sort(v)[-k:].sum()
print(f"{'unit band':18s} {'copies':>6s} {'% copy':>7s} {'w/o 2%':>8s}  {'blocks':28s} {'halves':16s} {'top5':>6s} {'won':>5s} {'days up':>8s}  verdict")
for f in sorted(glob.glob(f"{O}/*.json")):
    lab = os.path.basename(f)[:-5]
    try: rows = sorted(json.load(open(f)), key=lambda r: r["t"])
    except Exception: continue
    if len(rows) < 12: print(f"{lab:18s} {len(rows):6d}  too few"); continue
    v = np.array([r["base"] for r in rows]); bl = np.array_split(v, 4); h1, h2 = np.array_split(v, 2)
    day = collections.defaultdict(float)
    for r in rows: day[dt.datetime.fromtimestamp(r["t"], dt.UTC).strftime("%m-%d")] += r["base"]
    top5 = np.sort(v)[-5:].sum() / v.sum() if v.sum() > 0 else float("nan")
    ok = v.mean() > 0 and wo2(v) > 0 and h1.mean() > 0 and h2.mean() > 0 and sum(b.mean() > 0 for b in bl) >= 3
    print(f"{lab:18s} {len(v):6d} {100 * v.mean():+6.1f}% {wo2(v):+8.2f}  " + " / ".join(f"{100 * b.mean():+5.1f}" for b in bl)
          + f"   {100 * h1.mean():+5.1f} / {100 * h2.mean():+5.1f}  {top5:6.0%} {np.mean(v > 0):5.0%} {sum(x > 0 for x in day.values()):3d} of {len(day):<3d}  {'KEEP' if ok else 'no'}")
