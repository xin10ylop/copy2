# Where the early-sale window should end, and under what price (wallet 4 sells many coins at about 300 s), at take
# profit 2.4 and 3.0; and its own sale times on the copyable coins.
#   python3 -I early_check.py SPD [STAKE]
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:3]; import float_exits as F
import lib as L, numpy as np
rows = F.rows
ages = []
for r in rows:
    p = F.PREP[r["key"], 4]; i = L.first(p["sell"])
    ages.append(int(p["age"][i]) if i is not None else None)
b = collections.Counter("never in 31 min" if a is None else "0-29" if a < 30 else "30-179" if a < 180 else "180-239" if a < 240 else "240-289" if a < 290 else "290-299" if a < 300
                        else "300-309" if a < 310 else "310-329" if a < 330 else "330-599" if a < 600 else "600+" for a in ages)
print("its first sale after its buy, seconds:", {k: b[k] for k in ("0-29", "30-179", "180-239", "240-289", "290-299", "300-309", "310-329", "330-599", "600+", "never in 31 min")})
def line(name, kw):
    full = [F.sim(rows, n, kw, caps=F.CAPS) for n in L.LAND]
    def wo(k, hs=(0, 1)):
        s = 0
        for res in full:
            for h in hs:
                v = sorted((x[1] for x in res if F.HALF(x[0]) == h), reverse=True); s += sum(v[k:])
        return s / 3
    its = sum(sum(1 for x in res if x[2] == "its_sell") for res in full) / 3
    print(f"   {name:34s} | {wo(0, (0,)):+6.2f} ({wo(2, (0,)):+6.2f}) | {wo(0, (1,)):+6.2f} ({wo(2, (1,)):+6.2f}) | {wo(0):+6.2f} ({wo(2):+6.2f}) [{wo(5):+6.2f}] | {its:5.1f}")
for tp in (2.4, 3.0):
    print(f"\ntp {tp}, 1790 s, no stop; 0.5 SOL, 2 open: first half (w/o best 2) | second half | both [w/o best 5] | sold behind it")
    line("never", dict(tp=tp, hold=1790, early=None, sl=None))
    for a, b_ in ((30, 180), (30, 240), (30, 290), (30, 300), (30, 310), (30, 330), (30, 420), (30, 600), (30, 1790), (0, 330), (60, 330), (120, 330), (180, 330), (240, 330)):
        line(f"{a}-{b_} s under 1.5x", dict(tp=tp, hold=1790, early=(a, b_, 1.5), sl=None))
    for below in (1.0, 1.2, 2.0, 1e9):
        line(f"30-330 s under {below if below < 1e9 else 'any'}x", dict(tp=tp, hold=1790, early=(30, 330, below), sl=None))
