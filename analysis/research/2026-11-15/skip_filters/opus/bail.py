# Step 7 (apart from the entry filters). Bailing out in the first seconds: one check at T seconds after wallet 4's
# buy (T = 10 / 20 / 30 / 45 / 60), on what is known then (the trades that landed before T), and if it fires we sell
# on the next trade. Checks: the price under x times the price its buy left; under x times OUR entry price; the
# highest price since our buy still under h; fewer than k trades since our buy; and his sale followed from 0 / 10 /
# 20 s instead of 30 s. Otherwise the live rule (tp 3.0, 600 s, his sale 30-290 s under 1.5x). Run as the bot runs
# (slots freed sooner), mean of the three landings; scored like the entry filters (better in each of A, B, C).
#   python3 -I bail.py SPD > out/bail.txt
import os, sys, datetime
import numpy as np
SPD = sys.argv[1]
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp(); os.environ["FE_T0"] = str(T0)
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(1, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); sys.argv = ["x", SPD, "0.5"]
import float_exits as F, lib as L
import common as C
RULE = dict(tp=3.0, hold=600, early=(30, 290, 1.5), sl=None)
def model_b(p, pxin, stake, tp, hold, early, sl, bail=None):
    """lib.model plus one bail check: bail = (kind, T, x)."""
    if p["refused"]: return (-0.0004, "refused", 0)
    vt0, vq0, bps0 = p["ent"]
    Q = stake * 1e9 * p["hopf"] / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    n = len(p["px"])
    if n == 0:
        vq_r = vq0 + net_in; vt_r = vt0 * vq0 / vq_r
        return ((vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - bps0 / 1e4) * p["rate"] * p["hopf"] / 1e9 - stake - 0.0026, "time", int(p["last"]))
    c = []
    i = L.first(p["grad"]);                                  c += [(i, 0, "graduated", 0)] if i is not None else []
    if early:
        i = L.first(p["sell"] & (p["age"] >= early[0]) & (p["age"] < early[1]) & (p["px"] < early[2])); c += [(i, 1, "its_sell", 1)] if i is not None else []
    if tp: i = L.first(p["px"] >= tp);                       c += [(i, 2, "tp", 1)] if i is not None else []
    if bail:
        kind, T, x = bail; i = L.first(p["age"] >= T)          # the first trade at or after T: we sell on it
        if i is not None:
            last = p["px"][i - 1] if i > 0 else pxin; hi = max(pxin, p["px"][:i].max()) if i > 0 else pxin
            fire = {"px": last < x, "vs_entry": last < x * pxin, "high": hi < x, "trades": i < x}[kind]
            if fire: c += [(i - 1, 2.5, "bail", 1)]
    i = L.first(p["age"] >= hold);                           c += [(i, 4, "time", 0)] if i is not None else []
    if c:
        i, _, why, d = min(c); ex = min(max(i + d, 0), n - 1)
    else:
        why, ex = "time", n - 1
    vq_r = p["vq"][ex] + net_in; vt_r = p["vt"][ex] * p["vq"][ex] / vq_r
    out = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - p["bps"][ex] / 1e4)
    return (out * p["rate"] * p["hopf"] / 1e9 - stake - 0.0026, why, int(p["age"][ex]))
RULES = [("px", T, x) for T in (10, 20, 30, 45, 60) for x in (0.8, 0.9, 1.0, 1.1)] + [("vs_entry", T, x) for T in (10, 20, 30, 45, 60) for x in (0.8, 0.9, 1.0)] \
      + [("high", T, x) for T in (10, 20, 30, 45, 60) for x in (1.1, 1.2, 1.3, 1.5)] + [("trades", T, x) for T in (10, 20, 30, 45, 60) for x in (3, 5, 10, 20)]
EARLY = [0, 10, 20]
NAME = {"px": "price < {x}x its buy's", "vs_entry": "price < {x}x our entry", "high": "high so far < {x}x", "trades": "fewer than {x} trades"}
def run(rule=None, early=None):
    for r in C.R:
        r["res"] = {n: model_b(F.PREP[r["key"], n], r["pxin"][n], 0.5, **dict(RULE, early=early or RULE["early"]), bail=rule) for n in C.LAND}
    return C.measures(None)
if __name__ == "__main__":
    orig = {r["key"]: r["res"] for r in C.R}
    base = run()
    same = all(abs(r["res"][n][0] - orig[r["key"]][n][0]) < 1e-9 and r["res"][n][1] == orig[r["key"]][n][1] for r in C.R for n in C.LAND)
    print(f"model_b without a bail equals lib.model on every copy and landing: {same}")
    base = C.measures(None)                                     # with base's own runs for kept/lost counts
    print("baseline"); print("   " + C.HDR); print("   " + C.row(base))
    out = []
    for rule in RULES:
        run(rule); m = C.measures(lambda r, n: False, base); out.append((f"at {rule[1]:2d} s: " + NAME[rule[0]].format(x=rule[2]), m))
    for e in EARLY:
        run(None, (e, 290, 1.5)); m = C.measures(lambda r, n: False, base); out.append((f"his sale followed from {e} s", m))
    print(f"\n{len(out)} bail-out rules tried")
    print("   rule                              | change A / B / C      | all    | bails a run (L4) | " + C.HDR + " | days ahead")
    for name, m in out:
        d = [m["blocks"][b] - base["blocks"][b] for b in range(3)]; nb = sum(1 for x in m["runs"][4] if x[2] == "bail")
        print(f"   {name:34s} | {d[0]:+6.2f} {d[1]:+6.2f} {d[2]:+6.2f} | {sum(d):+6.2f} | {nb:16d} | {C.row(m, base)} | {100 * C.boot(m, base):5.1f}%{'  <- all three' if all(x > 0 for x in d) else ''}")
    for r in C.R: r["res"] = orig[r["key"]]
