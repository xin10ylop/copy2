# How far to trust a higher take profit and a shorter timer (float_exits.py's best rules): the candidates by thirds of
# the period, by landing, without each half's best 2 and best 5; and what the coins that reach 2.4x do next.
#   python3 -I tp_check.py SPD [STAKE]
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:3]; import float_exits as F
import lib as L, numpy as np
rows, STAKE = F.rows, F.STAKE
E0, E1, E2 = (30, 180, 1.5), (30, 240, 1.5), (30, 300, 1.5)
CAND = [("live: tp 2.4, 1790 s, early 30-180", dict(tp=2.4, hold=1790, early=E0, sl=None)),
        ("tp 2.4, 1790 s, early 30-300", dict(tp=2.4, hold=1790, early=E2, sl=None)),
        ("tp 2.4, 1200 s, early 30-300", dict(tp=2.4, hold=1200, early=E2, sl=None)),
        ("tp 3.0, 1790 s, early 30-180", dict(tp=3.0, hold=1790, early=E0, sl=None)),
        ("tp 3.0, 1790 s, early 30-300", dict(tp=3.0, hold=1790, early=E2, sl=None)),
        ("tp 3.0, 1200 s, early 30-300", dict(tp=3.0, hold=1200, early=E2, sl=None)),
        ("tp 3.5, 1790 s, early 30-300", dict(tp=3.5, hold=1790, early=E2, sl=None)),
        ("tp 4.0, 1790 s, early 30-300", dict(tp=4.0, hold=1790, early=E2, sl=None)),
        ("tp 4.0, 1200 s, early 30-300", dict(tp=4.0, hold=1200, early=E2, sl=None)),
        ("tp 5.0, 1790 s, early 30-300", dict(tp=5.0, hold=1790, early=E2, sl=None)),
        ("no tp, 1790 s, early 30-300", dict(tp=None, hold=1790, early=E2, sl=None))]
T0, T1 = L.T_STOP, F.END; third = lambda r: min(2, int(3 * (r["t"] - T0) / (T1 - T0)))
print(f"{len(rows)} buys, stake {STAKE}, 2 open, 1 from each of PUMP / SPCX; raw model")
print(f"{'rule':36s} | thirds of the period (mean of landings)  | both halves: net, w/o best 2, w/o best 5 | landing 4 / 8 / late | tp exits | corrected")
for name, kw in CAND:
    th = [sum(sum(x[1] for x in F.sim([r for r in rows if third(r) == k], n, kw, caps=F.CAPS)) for n in L.LAND) / 3 for k in range(3)]
    full = [F.sim(rows, n, kw, caps=F.CAPS) for n in L.LAND]
    def wo(k):
        s = 0
        for res in full:
            for h in (0, 1):
                v = sorted((x[1] for x in res if F.HALF(x[0]) == h), reverse=True); s += sum(v[k:])
        return s / 3
    cor = sum(sum(x[1] for x in F.sim(rows, n, kw, caps=F.CAPS, cal=True)) for n in L.LAND) / 3
    print(f"{name:36s} | {th[0]:+6.2f} {th[1]:+6.2f} {th[2]:+6.2f}                     | {wo(0):+6.2f} {wo(2):+6.2f} {wo(5):+6.2f}                    | "
          + " / ".join(f"{sum(x[1] for x in res):+6.2f}" for res in full) + f" | {sum(sum(1 for x in res if x[2] == 'tp') for res in full) / 3:5.1f}    | {cor:+6.2f}")
print("\nthe copies whose price reached 2.4x (landing 4, every copy, early 30-180 under 1.5x, 1790 s): where they go if we do not sell there")
for cls in ("SOL", "WBTC", "PUMP", "SPCX", "all"):
    n24 = n3 = n4 = 0; after = []
    for r in rows:
        if cls != "all" and r["anchor"] != cls: continue
        p = F.PREP[r["key"], 4]
        if p["refused"]: continue
        i = L.first(p["px"] >= 2.4)
        if i is None: continue
        # an early sale before it would have closed us first
        j = L.first(p["sell"] & (p["age"] >= 30) & (p["age"] < 180) & (p["px"] < 1.5))
        if j is not None and j < i: continue
        if p["age"][i] >= 1790: continue
        n24 += 1; rest = p["px"][i:][p["age"][i:] < 1790]
        n3 += bool((rest >= 3.0).any()); n4 += bool((rest >= 4.0).any())
        if not (rest >= 4.0).any(): after.append(float(rest[-1]))
    med = np.median(after) if after else float("nan")
    print(f"   {cls:5s}: {n24:3d} reached 2.4x; of them {n3} reached 3.0x ({100 * n3 / max(1, n24):.0f}%), {n4} reached 4.0x ({100 * n4 / max(1, n24):.0f}%); "
          f"the {len(after)} that did not reach 4.0x ended at {med:.2f}x (median), {sum(1 for a in after if a < 2.4)} of them under 2.4x, {sum(1 for a in after if a < 1.0)} under 1.0x")
