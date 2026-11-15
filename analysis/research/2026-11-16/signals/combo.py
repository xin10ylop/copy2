# The two round-2 leaders together (sell on whichever comes first), at tp 3.0 / 4.0 / none, against the live rule;
# and how many take profits each keeps (a signal that cuts winners shows here).
#   python3 -I combo.py CQ ALL > out/combo.txt
import sys, os, collections, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:3]
import signals2 as S2
from signals2 import L, run, score, day
base_trigger = S2.trigger
def trigger(p, x, sig):
    if sig[0] != "combo": return base_trigger(p, x, sig)
    t = [i for i in (base_trigger(p, x, s) for s in sig[1]) if i is not None]
    return min(t) if t else None
S2.trigger = trigger
SEL, STALL = ("sellers", 5, 60, None), ("stall", 1.0, 180, None)
RULES = [("live", None, 3.0), ("live, tp 4.0", None, 4.0), ("live, no tp", None, None)]
for tp in (3.0, 4.0, None):
    t = f"tp {tp}" if tp else "no tp"
    RULES += [(f"sellers 5+ in 60 s, {t}", SEL, tp), (f"no new high 180 s, {t}", STALL, tp), (f"both, {t}", ("combo", (SEL, STALL), None, None), tp)]
L0 = score(None, 3.0)
d0 = collections.defaultdict(float)
for n in L.LAND:
    for r, net, why in run(None, 3.0, n): d0[day(r["t"])] += net / 3
keys = sorted(d0)[1:-1]; random.seed(7)
print(f"{len(S2.ROWS)} buys; 0.5 SOL, 2 open, 600 s, early 30-290 s; gain = against the live rule (tp 3.0, no signal)")
if __name__ == "__main__":
  for name, sig, tp in RULES:
      s = score(sig, tp); d = collections.defaultdict(float)
      for n in L.LAND:
          for r, net, why in run(sig, tp, n): d[day(r["t"])] += net / 3
      g = [d[k] - d0[k] for k in keys]; draws = [sum(random.choice(g) for _ in g) for _ in range(2000)]
      print(f"   {name:32s}: {s['tot']:+6.2f} (gain {s['tot'] - L0['tot']:+6.2f}) | A {s['b'][0]:+6.2f} B {s['b'][1]:+6.2f} C {s['b'][2]:+6.2f} | w/o best 5 {s['wo5']:+6.2f}"
            f" | losing days {s['neg']}/{s['nd']}, worst {s['worst']:+5.2f}, deepest fall {s['fall']:+5.2f} | ahead in {100 * sum(1 for x in draws if x > 0) / 2000:.1f}% of draws"
            f" | take profits {s['whys'].get('tp', 0):.0f}, signal {s['whys'].get('signal', 0):.0f}, timer {s['whys'].get('time', 0):.0f}")
