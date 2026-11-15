# Copying its 1.0-1.45 SOL buys (part C's top band, +202.57 SOL for wallet 4 over Oct 29 - Nov 15, decomp.py): our
# copy of every third of them by time (CQ: the sample, its paths), every copy with no slot limit, the live rule (tp
# 3.0, 600 s, early 30-290 s under 1.5x), 0.5 SOL, raw, mean of the three landings; by block (A to Oct 29 12:02 UTC,
# B to Nov 6 05:32, C after) and by what we pay with; next to the same numbers for the 1.45+ buys the bot copies now
# (ALL, the six kinds). With the fee rule (skip under 125 bps) too.
#   python3 -I c_band.py CQ ALL
import sys, os, datetime, collections
CQ, ALL = sys.argv[1], sys.argv[2]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); import lib as L
RULE = dict(tp=3.0, hold=600, early=(30, 290, 1.5), sl=None)
TB = L.T_STOP; TC = datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp()
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp()
blk = lambda r: 0 if r["t"] < TB else 1 if r["t"] < TC else 2
KINDS = {"SOL", "WBTC", "PUMP", "SPCX", "TTWofwAg", "DJTu7vi8"}
def every(SPD, lo, hi):
    rows, P, info = L.load(SPD, T0)
    rows = [r for r in rows if r["anchor"] in KINDS and lo <= r["sol"] < hi]
    out = []
    for r in rows:
        ps = [L.prep(r, P, n) for n in L.LAND]
        if any(p is None for p in ps): continue
        res = [L.model(p, 0.5, **RULE) for p in ps]
        m, tr = P[r["key"]]; bps = next(e for e in tr if e["user"] == L.W4 and e["buy"] and e["slot"] == r["slot"])["bps"]
        out.append(dict(r=r, net=sum(x[0] for x in res) / 3, tp=res[0][1] == "tp", refused=res[0][1] == "refused", bps=bps))
    return out, info
def show(name, x):
    k = [c for c in x if not c["refused"]]; b = [sum(c["net"] for c in x if blk(c["r"]) == j) for j in range(3)]
    nets = sorted((c["net"] for c in x), reverse=True)
    print(f"   {name:46s} {len(x):4d} copies ({len(x) - len(k)} refused), {sum(c['tp'] for c in x):3d} tp ({100 * sum(c['tp'] for c in x) / max(1, len(k)):4.1f}%) | "
          f"A {b[0]:+6.2f}  B {b[1]:+6.2f}  C {b[2]:+6.2f} | all {sum(b):+7.2f} ({sum(nets[3:]):+7.2f} w/o best 3) | {100 * sum(b) / max(1, len(k)) / 0.5:+6.1f}% a copy")
if __name__ == "__main__":
    c, ci = every(CQ, 1.0, 1.45); a, ai = every(ALL, 1.45, 1e9)
    print(f"every copy, no slot limit, 0.5 SOL, mean of three landings; the 1.0-1.45 band is every third buy ({ci['nopath']} without a path)")
    show("its 1.0-1.45 SOL buys (a third of them)", c); show("  the same, fee rule on", [x for x in c if not (0 < x["bps"] < 125)])
    show("its 1.45+ SOL buys (all; the bot copies these)", a); show("  the same, fee rule on", [x for x in a if not (0 < x["bps"] < 125)])
    print("\nthe 1.0-1.45 band by what we pay with:")
    for k in sorted({x["r"]["anchor"] for x in c}): show(k, [x for x in c if x["r"]["anchor"] == k])
    print("\nthe 1.0-1.45 band by size:")
    for lo, hi in ((1.0, 1.1), (1.1, 1.2), (1.2, 1.3), (1.3, 1.45)): show(f"{lo}-{hi} SOL", [x for x in c if lo <= x["r"]["sol"] < hi])
