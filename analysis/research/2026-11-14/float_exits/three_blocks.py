# All the data in three blocks: A = the unseen week (Oct 21 18:30 - Oct 29 12:02 UTC), B and C = the two halves of the
# study period (to Nov 6 05:32, to Nov 13 23:02 UTC). A rule worth running should hold up in all three. 100 rules:
# take profit 2.4 / 3.0 / 3.5 / 4.0 / 5.0 x timer 300 / 600 / 900 / 1200 / 1790 s x his sale followed 30-180 / 30-290 /
# 30-330 s under 1.5x / never. 0.5 SOL, 2 open (SOL 1, WBTC 2, PUMP 1, SPCX 1), raw, mean of landings 4 / 8 / late.
#   python3 -I three_blocks.py SPD
import sys, os, datetime, itertools
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp(); os.environ["FE_T0"] = str(T0)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:2] + ["0.5"]; import float_exits as F
import lib as L
from multiprocessing import Pool
CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
TB = L.T_STOP; TC = datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp()
blk = lambda r: 0 if r["t"] < TB else 1 if r["t"] < TC else 2
BL = [[r for r in F.rows if blk(r) == b] for b in range(3)]
EARLY = {"30-180": (30, 180, 1.5), "30-290": (30, 290, 1.5), "30-330": (30, 330, 1.5), "never": None}
GRID = [dict(tp=tp, hold=h, early=EARLY[e], sl=None) for tp, h, e in itertools.product((2.4, 3.0, 3.5, 4.0, 5.0), (300, 600, 900, 1200, 1790), EARLY)]
lab = lambda kw: f"tp {kw['tp']} {kw['hold']:>4} s early {next(k for k, v in EARLY.items() if v == kw['early']):6s}"
def ev(kw):
    out = []
    for rs in BL:
        x = [sorted((y[1] for y in F.sim(rs, n, kw, caps=CAPS)), reverse=True) for n in L.LAND]
        out.append((sum(sum(v) for v in x) / 3, sum(sum(v[2:]) for v in x) / 3))
    return kw, out
if __name__ == "__main__":
    with Pool(4) as p: R = p.map(ev, GRID)
    n = len(R); rank = lambda b, k: {id(r): i for i, r in enumerate(sorted(R, key=lambda r: -r[1][b][k]))}
    rk = [[rank(b, k) for k in (0, 1)] for b in range(3)]
    print(f"blocks: A {len(BL[0])} buys (unseen week), B {len(BL[1])}, C {len(BL[2])}; {n} rules; net SOL (without the block's best 2) [rank of {n} by the net without the best 2]")
    row = lambda r, tag="": print(f"   {lab(r[0])} | " + " | ".join(f"{r[1][b][0]:+6.2f} ({r[1][b][1]:+6.2f}) [{rk[b][1][id(r)] + 1:3d}]" for b in range(3))
                                  + f" | all {sum(x[0] for x in r[1]):+6.2f} ({sum(x[1] for x in r[1]):+6.2f}) | worst rank {max(rk[b][1][id(r)] for b in range(3)) + 1:3d} {tag}")
    get = lambda tp, h, e: next(r for r in R if r[0] == dict(tp=tp, hold=h, early=EARLY[e], sl=None))
    print(f"   {'rule':30s} | A: unseen week          | B: first half           | C: second half")
    row(get(3.0, 1200, "30-290"), "<- live now"); row(get(2.4, 1790, "30-180"), "<- the old rule")
    print("the 12 rules with the best WORST rank over the three blocks (steady everywhere):")
    for r in sorted(R, key=lambda r: (max(rk[b][1][id(r)] for b in range(3)), -sum(x[1] for x in r[1])))[:12]: row(r)
    print("the 8 best by the sum of the three blocks without their best 2:")
    for r in sorted(R, key=lambda r: -sum(x[1] for x in r[1]))[:8]: row(r)
    print("each choice on its own: the mean over every rule with it, A / B / C (net without the best 2)")
    for key, vals, g in (("tp", (2.4, 3.0, 3.5, 4.0, 5.0), str), ("hold", (300, 600, 900, 1200, 1790), str), ("early", list(EARLY.values()), lambda v: next(k for k, x in EARLY.items() if x == v))):
        m = lambda v, b: sum(r[1][b][1] for r in R if r[0][key] == v) / sum(1 for r in R if r[0][key] == v)
        print(f"   {key:5s}: " + "   ".join(f"{g(v)} {m(v, 0):+.2f} / {m(v, 1):+.2f} / {m(v, 2):+.2f}" for v in vals))
