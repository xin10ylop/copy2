# Part sales (the owner, Nov 15): sell x% of the position when the price first reaches y (1.2x to 2.9x), the rest by the
# live rule (tp 3.0, 600 s, his sale followed 30-290 s under 1.5x, no stop); also with the rest's take profit at 4.0
# or none (the timer). Every x from 10% to 90%. 0.5 SOL, 2 open (SOL 1, WBTC 2, PUMP 1, SPCX 1), raw, mean of
# landings 4 / 8 / one block late, over the three blocks A (Oct 21-29, unseen when the live rule was picked), B, C.
#   python3 -I partial.py SPD
import sys, os, datetime, itertools
from multiprocessing import Pool
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp(); os.environ["FE_T0"] = str(T0)
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); sys.argv = sys.argv[:2] + ["0.5"]
import float_exits as F
import lib as L
KINDS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
ROWS = [r for r in F.rows if r["anchor"] in KINDS]
TB = L.T_STOP; TC = datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp()
blk = lambda r: 0 if r["t"] < TB else 1 if r["t"] < TC else 2
E = (30, 290, 1.5)
def sim(rs, n, kw):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x[0] > r["t"]]
        if len(open_) >= 2 or sum(1 for x in open_ if x[1] == r["anchor"]) >= KINDS[r["anchor"]]: continue
        net, why, held = L.model_partial(F.PREP[r["key"], n], 0.5, **kw)
        if why != "refused": open_.append((r["t"] + held, r["anchor"]))
        out.append(net)
    return out
def ev(kw):
    b = []
    for k in range(3):
        x = [sorted(sim([r for r in ROWS if blk(r) == k], n, kw), reverse=True) for n in L.LAND]
        b.append((sum(sum(v) for v in x) / 3, sum(sum(v[2:]) for v in x) / 3, sum(sum(v[5:]) for v in x) / 3))
    return kw, b
TP1 = [round(1.2 + 0.1 * i, 1) for i in range(18)]                 # 1.2 .. 2.9
FR = [round(0.1 * i, 1) for i in range(1, 10)]                      # 10% .. 90%
GRID = [dict(tp1=None, frac=0, tp=tp, hold=600, early=E) for tp in (3.0, 4.0, None)] + \
       [dict(tp1=a, frac=f, tp=tp, hold=600, early=E) for tp in (3.0, 4.0, None) for a in TP1 for f in FR]
if __name__ == "__main__":
    with Pool(4) as p: R = p.map(ev, GRID)
    tot = lambda r, i: sum(x[i] for x in r[1])
    base = {r[0]["tp"]: r for r in R if r[0]["frac"] == 0}
    print(f"{len(ROWS)} buys (SOL, WBTC, PUMP, SPCX), Oct 21 to Nov 15; {len(GRID)} rules; SOL over A | B | C, and all: net / without each block's best 2 / best 5")
    lab = lambda kw: "sell all at once" if not kw["frac"] else f"sell {int(kw['frac'] * 100):2d}% at {kw['tp1']:.1f}x"
    row = lambda r: print(f"   {lab(r[0]):22s} rest tp {str(r[0]['tp']):4s} | " + " | ".join(f"{x[0]:+6.2f}" for x in r[1]) + f" | {tot(r, 0):+6.2f} / {tot(r, 1):+6.2f} / {tot(r, 2):+6.2f}")
    for tp in (3.0, 4.0, None):
        print(f"\n== the rest's take profit {tp}: the baseline, then the 8 best part sales by the total without each block's best 5")
        row(base[tp])
        for r in sorted([r for r in R if r[0]["tp"] == tp and r[0]["frac"]], key=lambda r: -tot(r, 2))[:8]: row(r)
        b = base[tp]; better = [r for r in R if r[0]["tp"] == tp and r[0]["frac"] and all(r[1][k][1] > b[1][k][1] for k in range(3))]
        print(f"   part sales better than selling all at once in ALL three blocks (without the best 2): {len(better)} of {len(TP1) * len(FR)}")
    print("\n== at the live rule (rest tp 3.0): the total without each block's best 2, by part price (rows) and share sold (columns)")
    print("   price | " + " ".join(f"{int(f * 100):5d}%" for f in FR) + f" | all at once {tot(base[3.0], 1):+.2f}")
    for a in TP1:
        cells = [tot(next(r for r in R if r[0] == dict(tp1=a, frac=f, tp=3.0, hold=600, early=E)), 1) for f in FR]
        print(f"   {a:.1f}x | " + " ".join(f"{c:+6.2f}" for c in cells))
