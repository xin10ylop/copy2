# Round 2's leaders under harder tests (Nov 15 evening): day by day against the live rule, each landing apart, the
# days redrawn with replacement (2000 draws), and the neighbours of each setting. Also tp 4.0 / none alone, since they
# lead round 2's table.
#   python3 -I robust.py CQ ALL > out/robust.txt
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = sys.argv[:3]
import signals2 as S2                                        # runs round 2's loader (not its table: see __main__ guard)
from signals2 import ROWS, L, blk, day, run, score, lab
import numpy as np
LIVE = (None, 3.0)
CANDS = [(("sellers", 3, 60, None), 3.0), (("sellers", 5, 60, None), 3.0), (("sellers", 3, 60, 1.5), 3.0), (("sellers", 5, 60, 1.5), 3.0),
         (("stall", 1.0, 180, None), 3.0), (("stall", 1.0, 120, None), 3.0), (("stall", 1.0, 300, None), 3.0),
         (None, 4.0), (None, None), (("sellers", 5, 60, None), 4.0), (("sellers", 5, 60, None), None)]
def days_of(sig, tp):
    d = collections.defaultdict(float); per_land = []
    for n in L.LAND:
        res = run(sig, tp, n); per_land.append(sum(x[1] for x in res))
        for r, net, why in res: d[day(r["t"])] += net / 3
    return d, per_land
D0, P0 = days_of(*LIVE)
keys = sorted(D0)[1:-1]                                      # whole days only
print(f"{len(ROWS)} buys; {len(keys)} whole days ({keys[0]} to {keys[-1]}); against the live rule (tp 3.0, 600 s), 0.5 SOL")
print(f"   live: landings 4 / 8 / slot+1 {P0[0]:+.2f} / {P0[1]:+.2f} / {P0[2]:+.2f}")
random.seed(7)
for sig, tp in CANDS:
    D, P = days_of(sig, tp)
    g = [D[k] - D0[k] for k in keys]
    ahead = sum(1 for x in g if x > 0.005); behind = sum(1 for x in g if x < -0.005)
    draws = [sum(random.choice(g) for _ in g) for _ in range(2000)]
    big = sorted(g, reverse=True)
    print(f"   {lab(sig, tp):58s}: gain {sum(g):+6.2f} | landings " + " / ".join(f"{a - b:+.2f}" for a, b in zip(P, P0))
          + f" | days ahead {ahead}, behind {behind} | ahead in {100 * sum(1 for x in draws if x > 0) / 2000:.1f}% of draws | gain without its best 2 days {sum(big[2:]):+.2f} | worst day vs live {min(g):+.2f}")
print("== the neighbours of 'N+ more sellers than buyers in W s' at tp 3.0 (gain over live)")
for w in (10, 30, 60, 90, 120):
    print(f"   W {w:3d} s: " + "  ".join(f"N {k}: {score(('sellers', k, w, None), 3.0)['tot'] - score(*LIVE)['tot']:+5.2f}" for k in (2, 3, 4, 5, 7, 10)))
print("== the neighbours of 'no new high for T s' (once 1.0x) at tp 3.0")
print("   " + "  ".join(f"T {T}: {score(('stall', 1.0, T, None), 3.0)['tot'] - score(*LIVE)['tot']:+5.2f}" for T in (90, 120, 150, 180, 240, 300, 400)))
