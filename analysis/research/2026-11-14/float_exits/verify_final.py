# "Verify one last time that this is the best" (the owner, Nov 14). The rule live since Nov 14 (tp 3.0, 1200 s, his
# sale followed at 30-290 s under 1.5x, no stop) on the study period (Oct 29 - Nov 13, 0.5 SOL, 2 open, SOL 1 / WBTC 2
# / PUMP 1 / SPCX 1, raw, mean of landings 4 / 8 / one block late):
# (a) its neighbours: is it on a plateau or a lone peak? (b) days drawn again with replacement 10,000 times: how often
# does it beat each rival? (c) does it still beat the old rule with any one day removed?
#   python3 -I verify_final.py SPD
import sys, os, collections, datetime, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:2] + ["0.5"]; import float_exits as F
import lib as L
CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
R = lambda tp, hold, a, b, below=1.5, sl=None: dict(tp=tp, hold=hold, early=(a, b, below) if b else None, sl=sl)
CH = R(3.0, 1200, 30, 290)
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
def bydays(kw):
    d = collections.defaultdict(float)
    for n in L.LAND:
        for r, net, why in F.sim(F.rows, n, kw, caps=CAPS): d[day(r["t"])] += net / 3
    return d
def both(kw):
    full = [F.sim(F.rows, n, kw, caps=CAPS) for n in L.LAND]; s = [0, 0]
    for res in full:
        for h in (0, 1):
            v = sorted((x[1] for x in res if F.HALF(x[0]) == h), reverse=True); s[0] += sum(v) / 3; s[1] += sum(v[2:]) / 3
    return s
print(f"{len(F.rows)} buys; (a) the neighbours: both halves' net (without the best 2 of each); early window 30-E s under 1.5x")
for e in (240, 270, 290):
    print(f"   E = {e}:   timer " + "".join(f"{h:>17d}" for h in (900, 1050, 1200, 1350, 1500, 1790)))
    for tp in (2.6, 2.8, 3.0, 3.2, 3.4):
        print(f"      tp {tp}:    " + "".join("  {:+6.2f} ({:+6.2f})".format(*both(R(tp, h, 30, e))) for h in (900, 1050, 1200, 1350, 1500, 1790)))
RIV = [("the old rule (tp 2.4, 1790 s, early 30-180)", R(2.4, 1790, 30, 180)), ("tp 2.4, the rest as chosen", R(2.4, 1200, 30, 290)), ("tp 4.0, the rest as chosen", R(4.0, 1200, 30, 290)),
       ("timer 600 s, the rest as chosen", R(3.0, 600, 30, 290)), ("timer 1790 s, the rest as chosen", R(3.0, 1790, 30, 290)), ("his sale never followed", R(3.0, 1200, 0, 0)),
       ("early 30-180 s, the rest as chosen", R(3.0, 1200, 30, 180)), ("his every sale followed", R(3.0, 1200, 0, 1e9, 1e9)), ("a 0.5x stop added", R(3.0, 1200, 30, 290, sl=0.5))]
ch = bydays(CH); days = sorted(ch); random.seed(1)
print(f"\n(b) {len(days)} Beirut days drawn again with replacement, 10,000 times; the chosen rule {sum(ch.values()):+.2f} SOL; (c) one day left out")
print(f"   {'rival':44s} | its net | chosen - rival | chosen ahead in | the 5% worst draw | ahead on days | smallest lead with one day left out")
for name, kw in RIV:
    rv = bydays(kw); d = [ch[x] - rv[x] for x in days]; wins = 0; draws = []
    for _ in range(10000):
        s = sum(random.choice(d) for _ in d); wins += s > 0; draws.append(s)
    draws.sort()
    print(f"   {name:44s} | {sum(rv.values()):+6.2f}  | {sum(d):+6.2f}         | {wins / 100:5.1f}% of draws | {draws[500]:+6.2f}            | {sum(1 for x in d if x > 0):2d} of {len(d)}      | {sum(d) - max(d):+6.2f}")
