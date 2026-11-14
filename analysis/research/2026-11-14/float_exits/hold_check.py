# The owner's question (Nov 14): our real take profits came within 600 s; is a 600 s timer better than 1790 s?
# The timer scanned at the new rule (tp 3.0, early 30-290 s under 1.5x, no stop) and the live one; when the take
# profits come; and what the wait from 600 s to 1790 s earns and costs (every copy, landing 4).
#   python3 -I hold_check.py SPD [STAKE]
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:3]; import float_exits as F
import lib as L
rows = F.rows; CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
for rname, base in (("new: tp 3.0, early 30-290", dict(tp=3.0, early=(30, 290, 1.5), sl=None)), ("live: tp 2.4, early 30-180", dict(tp=2.4, early=(30, 180, 1.5), sl=None))):
    print(f"{rname}; 0.5 SOL, 2 open (SOL 1, WBTC 2, PUMP 1, SPCX 1); raw")
    print(f"   {'timer':>6s} | first half (w/o best 2) | second half     | both (w/o best 2) [w/o best 5] | landing 4 / 8 / late     | copies | tp exits | every copy: SOL / WBTC / PUMP / SPCX coins")
    for hold in (300, 450, 600, 750, 900, 1200, 1500, 1790):
        kw = dict(base, hold=hold); full = [F.sim(rows, n, kw, caps=CAPS) for n in L.LAND]
        def wo(k, hs=(0, 1)):
            s = 0
            for res in full:
                for h in hs:
                    v = sorted((x[1] for x in res if F.HALF(x[0]) == h), reverse=True); s += sum(v[k:])
            return s / 3
        cls = []
        for c in ("SOL", "WBTC", "PUMP", "SPCX"):
            h = F.halves([r for r in rows if r["anchor"] == c], kw, max_open=10**6); cls.append(f"{h[0][0] + h[1][0]:+6.2f}")
        print(f"   {hold:5d}s | {wo(0, (0,)):+6.2f} ({wo(2, (0,)):+6.2f})      | {wo(0, (1,)):+6.2f} ({wo(2, (1,)):+6.2f}) | {wo(0):+6.2f} ({wo(2):+6.2f}) [{wo(5):+6.2f}]      | "
              + " / ".join(f"{sum(x[1] for x in res):+6.2f}" for res in full) + f" | {sum(len(res) for res in full) / 3:5.0f}  | {sum(sum(1 for x in res if x[2] == 'tp') for res in full) / 3:5.1f}    | " + " / ".join(cls))
    print()
for tp in (2.4, 3.0):
    kw = dict(tp=tp, hold=1790, early=(30, 290, 1.5), sl=None); b = collections.Counter(); s = collections.Counter()
    late_gain = wait_cost = 0.0; nlate = nwait = 0
    for r in rows:
        p = F.PREP[r["key"], 4]
        if p["refused"]: continue
        a = L.model(p, 0.5, **kw); c = L.model(p, 0.5, **dict(kw, hold=600))
        if a[1] == "tp":
            k = "0-300 s" if a[2] < 300 else "300-600 s" if a[2] < 600 else "600-900 s" if a[2] < 900 else "900-1200 s" if a[2] < 1200 else "1200-1790 s"
            b[k] += 1; s[k] += a[0]
        if c[1] == "time" and c[2] >= 600:                   # still held at 600 s: what the wait to 1790 s changes
            if a[1] == "tp": nlate += 1; late_gain += a[0] - c[0]
            else: nwait += 1; wait_cost += a[0] - c[0]
    print(f"tp {tp}, every copy, landing 4: when the take profit comes (copies, their net SOL): " + ", ".join(f"{k} {b[k]} ({s[k]:+.2f})" for k in ("0-300 s", "300-600 s", "600-900 s", "900-1200 s", "1200-1790 s")))
    print(f"   still held at 600 s: {nlate} reach the take profit later, the wait earns {late_gain:+.2f} SOL on them; the other {nwait} change by {wait_cost:+.2f} SOL from 600 s to their exit; net of waiting {late_gain + wait_cost:+.2f} SOL")
