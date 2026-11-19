# The owner's angle (Nov 19): "if they consistently get 2 good coins per day and end profitable, then it is a good
# wallet". m4_direct's copy of EVERY wallet's first buys (0.5+ SOL, wallet 4's live model, the mean of the 3 landings,
# 0.0345 SOL a round trip) on every coin of the 4 days fetched in full (Nov 14 01:07 - Nov 18 01:07 UTC), judged by DAY:
# days active, days our copy ended up, big winners (a copy +100% or more) and on how many days they came, worst day.
# Then BLIND: wallets chosen on days 1-2 only (up on both days, a big winner on both), scored on days 3-4.
#   LAUNCHES=<the 3 launch lists> python3 -I m6_days.py SP > ../out/m6_days.txt
import sys, os, json, gzip, collections, numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import m4_direct as M
if __name__ == "__main__":
    with Pool(8) as P: F = P.map(M.firsts, sorted(M.L), chunksize=20)
    cnt = collections.Counter(u for m, b in F for u, *_ in b); keep = {u for u, n in cnt.items() if n >= 4} | {M.W4}
    jobs = [(m, [b for b in bs if b[0] in keep]) for m, bs in F]; jobs = [j for j in jobs if j[1]]
    with Pool(8) as P: R = [r for part in P.map(M.copies, jobs, chunksize=4) for r in part]
    json.dump(R, gzip.open(f"{M.O}/m6_rows.json.gz", "wt"))
    t0 = min(r[2] for r in R); DAY = 86400; nd = int((max(r[2] for r in R) - t0) // DAY) + 1
    W = collections.defaultdict(list)
    for r in R: W[r[0]].append(r)
    STAKE = 0.5; BIG = STAKE   # a big winner: our copy +0.5 SOL or more on 0.5 (+100%)
    def stats(v):
        d = collections.defaultdict(list)
        for r in v: d[int((r[2] - t0) // DAY)].append(r[4])
        days = {k: sum(x) for k, x in d.items()}; bigd = {k: sum(1 for x in xs if x >= BIG) for k, xs in d.items()}
        return dict(n=len(v), net=sum(r[4] for r in v), act=len(days), up=sum(1 for x in days.values() if x > 0), worst=min(days.values()),
                    big=sum(bigd.values()), bigdays=sum(1 for x in bigd.values() if x > 0), days=days, cre=len({r[5] for r in v}))
    S = {u: stats(v) for u, v in W.items()}
    print(f"{len(M.L)} coins; {len(R)} copies of {len(W)} wallets with 4+ first buys of 0.5+ SOL; {nd} days from the data's start; pooled {sum(s['net'] for s in S.values()):+.1f} SOL")
    w4 = S.get(M.W4); print(f"wallet 4 (all its 0.5+ buys): {w4['n']} copies, {w4['net']:+.2f} SOL, up on {w4['up']} of {w4['act']} days, {w4['big']} big winners on {w4['bigdays']} days")
    cons = [(u, s) for u, s in S.items() if s["act"] >= 3 and s["up"] >= s["act"] - 0 and s["bigdays"] >= 3 and s["net"] > 0]
    loose = [(u, s) for u, s in S.items() if s["act"] >= 3 and s["up"] >= s["act"] - 1 and s["bigdays"] >= 2 and s["net"] > 0 and s["n"] >= 8]
    def show(L_, title):
        print(f"\n== {title}: {len(L_)} wallets ==\n   wallet        copies   net SOL  a copy  days up/active  big winners (days)  worst day  creators   day by day")
        for u, s in sorted(L_, key=lambda x: -x[1]["net"])[:40]:
            print(f"   {u[:12]}  {s['n']:5d}  {s['net']:+7.2f}  {100 * s['net'] / s['n'] / STAKE:+5.1f}%   {s['up']}/{s['act']}            {s['big']:3d} ({s['bigdays']})          {s['worst']:+6.2f}   {s['cre']:5d}   "
                  + " ".join(f"{s['days'].get(k, 0):+.2f}" if k in s['days'] else "  -  " for k in range(nd)))
    show(cons, "UP EVERY ACTIVE DAY (3+ days), a big winner on 3+ days")
    show(loose, "up on all but one active day (3+ days), big winners on 2+ days, 8+ copies")
    # blind: chosen on days 0-1, scored on days 2-3
    pick = []
    for u, v in W.items():
        a = [r for r in v if r[2] < t0 + 2 * DAY]; b = [r for r in v if r[2] >= t0 + 2 * DAY]
        if len(a) < 4: continue
        s = stats(a)
        if s["act"] == 2 and s["up"] == 2 and s["bigdays"] == 2: pick.append((u, s, b))
    xs = [r[4] for _, _, b in pick for r in b]; allb = [r[4] for r in R if r[2] >= t0 + 2 * DAY]
    print(f"\n== BLIND: chosen on days 1-2 (up both days, a big winner both days, 4+ copies): {len(pick)} wallets ==")
    print(f"   on days 3-4 (unseen): {len(xs)} copies, {sum(xs):+.2f} SOL, {100 * np.mean(xs) / STAKE if xs else 0:+.1f}% a copy; "
          f"wallets up on days 3-4: {sum(1 for *_, b in pick if b and sum(r[4] for r in b) > 0)} of {sum(1 for *_, b in pick if b)} that traded; "
          f"every wallet's copy on days 3-4: {100 * np.mean(allb) / STAKE:+.1f}% a copy")
    for u, s, b in sorted(pick, key=lambda x: -x[1]["net"]):
        print(f"   {u[:12]}  days 1-2: {s['n']:3d} copies {s['net']:+6.2f}  ->  days 3-4: {len(b):3d} copies {sum(r[4] for r in b):+6.2f}")
