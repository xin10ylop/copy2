# The take profit in steps of 0.2 with the early-sale window 30-290 s (under 1.5x), 1790 s, no stop; and the bot's
# 17 real trades replayed with tp 2.4 and tp 3.0 (model, landing 4, the real stake).
#   python3 -I tp_fine.py SPD [STAKE]
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:3]; import float_exits as F
import lib as L
rows = F.rows; E = (30, 290, 1.5)
print("0.5 SOL, 2 open, 1 from each of PUMP / SPCX; early 30-290 s under 1.5x, 1790 s; raw")
print(f"   {'tp':>4s} | first half (w/o best 2) | second half     | both (w/o best 2) [w/o best 5] | landing 4 / 8 / late     | tp exits | SOL / WBTC / PUMP / SPCX coins, every copy")
for tp in (2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 4.0, 5.0):
    kw = dict(tp=tp, hold=1790, early=E, sl=None)
    full = [F.sim(rows, n, kw, caps=F.CAPS) for n in L.LAND]
    def wo(k, hs=(0, 1)):
        s = 0
        for res in full:
            for h in hs:
                v = sorted((x[1] for x in res if F.HALF(x[0]) == h), reverse=True); s += sum(v[k:])
        return s / 3
    cls = []
    for c in ("SOL", "WBTC", "PUMP", "SPCX"):
        h = F.halves([r for r in rows if r["anchor"] == c], kw, max_open=10**6); cls.append(f"{h[0][0] + h[1][0]:+6.2f}")
    print(f"   {tp:4.1f} | {wo(0, (0,)):+6.2f} ({wo(2, (0,)):+6.2f})      | {wo(0, (1,)):+6.2f} ({wo(2, (1,)):+6.2f}) | {wo(0):+6.2f} ({wo(2):+6.2f}) [{wo(5):+6.2f}]      | "
          + " / ".join(f"{sum(x[1] for x in res):+6.2f}" for res in full) + f" | {sum(sum(1 for x in res if x[2] == 'tp') for res in full) / 3:5.1f}    | " + " / ".join(cls))
print("\nthe bot's real take profits (journal) and what the model says of the same coins at tp 2.4 / 3.0 (landing 4, real stake, early 30-290):")
by = {r["mint8"]: r for r in rows}
for m8, st, real in (("5tePJcGm", 0.1, 0.3531), ("Eymbsj8M", 0.5, 0.6228), ("BUdiaswB", 0.5, 1.3340)):
    p = L.prep(by[m8], F.P, 4)
    a = L.model(p, st, tp=2.4, hold=1790, early=E, sl=None); b = L.model(p, st, tp=3.0, hold=1790, early=E, sl=None)
    w = p["age"] < 1790
    print(f"   {m8}: real {real:+.4f} at {st} SOL; model tp 2.4 {a[0]:+.4f} ({a[1]}, {a[2]} s); tp 3.0 {b[0]:+.4f} ({b[1]}, {b[2]} s); the coin's high within 30 min {p['px'][w].max():.2f}x")
