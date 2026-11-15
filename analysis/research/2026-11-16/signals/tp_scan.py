# The owner (Nov 15 evening): "shouldn't we do tp 3.5x? test from 3 to 4, the lower the better". Both signals (5+ more
# sells than buys by others in 60 s; no new high for 180 s), tp 3.0 to 4.0 and a few above; as combo.py.
#   python3 -I tp_scan.py CQ ALL > out/tp_scan.txt
import sys, os, collections, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:3]
import combo as C                                            # patches the combined trigger in
from signals2 import L, run, score, day
SIG = ("combo", (C.SEL, C.STALL), None, None)
L0 = score(None, 3.0)
d0 = collections.defaultdict(float)
for n in L.LAND:
    for r, net, why in run(None, 3.0, n): d0[day(r["t"])] += net / 3
keys = sorted(d0)[1:-1]
print(f"both signals, 600 s, early 30-290 s; 0.5 SOL; gain = against the live rule (tp 3.0, no signal) {L0['tot']:+.2f}")
res = {}
for tp in (3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.5, 5.0, None):
    random.seed(7); s = score(SIG, tp); d = collections.defaultdict(float)
    for n in L.LAND:
        for r, net, why in run(SIG, tp, n): d[day(r["t"])] += net / 3
    g = [d[k] - d0[k] for k in keys]; draws = [sum(random.choice(g) for _ in g) for _ in range(2000)]
    print(f"   tp {str(tp) if tp else 'none':4s}: {s['tot']:+6.2f} | A {s['b'][0]:+6.2f} B {s['b'][1]:+6.2f} C {s['b'][2]:+6.2f} | w/o best 5 {s['wo5']:+6.2f}"
          f" | losing days {s['neg']}/{s['nd']}, worst {s['worst']:+5.2f}, deepest fall {s['fall']:+5.2f} | ahead of live in {100 * sum(1 for x in draws if x > 0) / 2000:.1f}% of draws | take profits {s['whys'].get('tp', 0):.0f}")
