# SolHouse VIP, other entries than "buy at the post" (the owner, Nov 17: "find something else ... others pay too"). The
# alerts fire after a pump (the price is already falling at the post), so: buy a crash (the first trade within WAIT at x
# times the post's price or lower), buy strength (at x times or higher), or buy the survivors (a fixed delay). Exits are
# multiples of OUR entry price, or a time after our buy. Found on one set of calls (FIND: vip + vip_rest, Nov 10-17);
# what is positive there in both halves and without the best 5, with 30+ copies, is listed; with TEST given (vip2: Nov
# 1-6) each listed setup is scored once there. Costs COST (0.01: no race), the fixed lab's rows and trade().
#   python3 -I tg_vip_explore.py TGDIR [TESTDIR] > out/tg_vip_explore.txt
import sys, os, numpy as np
TG = sys.argv[1]; TEST = sys.argv[2] if len(sys.argv) > 2 else None; here = os.path.dirname(os.path.abspath(__file__)); os.environ.setdefault("COST", "0.01")
src = open(os.path.join(here, "tg_vip_lab.py")).read().split("# ---- 1. signs")[0]
def load(names):
    R = []
    for v in names:
        os.environ["VDIR"] = v; ns = {"__file__": os.path.join(here, "tg_vip_lab.py")}; sys.argv = ["x", TG]
        exec(compile(src, "tg_vip_lab.py", "exec"), ns); R += ns["rows"]
    return sorted(R, key=lambda r: r["t"]), ns["trade"], ns["STAKE"]
def entry(r, kind, x, wait):
    T, pr, t, p0 = r["T"], r["pr"], r["t"], r["p0"]
    if kind == "delay": k = int(np.searchsorted(T, t + x, side="left")); return k if k < len(T) - 1 else None
    m = (T >= t + 1) & (T <= t + wait) & ((pr <= x * p0) if kind == "crash" else (pr >= x * p0))
    ok = np.where(m)[0]
    return int(ok[0]) if len(ok) and ok[0] < len(T) - 1 else None
SETUPS = [("delay", d, 0) for d in (600, 1200, 1800)] + [("crash", x, w) for x in (0.8, 0.7, 0.6, 0.5, 0.4) for w in (600, 1800)] \
       + [("strength", x, w) for x in (1.2, 1.5, 2.0) for w in (300, 600)]
EXITS = [dict(tp=1.3, cap=600), dict(tp=1.5, cap=600), dict(tp=1.5, cap=1800), dict(tp=2, cap=1800), dict(tp=3, cap=1800), dict(tp=None, cap=300), dict(tp=None, cap=1200)]
def score(R, trade, s, ex):
    out = []
    for r in R:
        k = entry(r, *s)
        if k is not None: out.append((r["t"], trade(r, k, **ex)))
    return out
F, trade, STAKE = load(["vip", "vip_rest", "vip_h1"]); half = F[len(F) // 2]["t"]
print(f"FIND: {len(F)} VIP calls (Nov 10-17); {len(SETUPS)} entries x {len(EXITS)} exits = {len(SETUPS) * len(EXITS)} tests; costs {os.environ['COST']}")
keep = []
for s in SETUPS:
    for ex in EXITS:
        v = score(F, trade, s, ex)
        if len(v) < 30: continue
        a = [p for t, p in v if t < half]; b = [p for t, p in v if t >= half]; x = [p for _, p in v]; s5 = sum(sorted(x, reverse=True)[5:])
        line = f"{s[0]:8s} x={s[1]:<6g} wait {s[2]:4d} s | tp {str(ex['tp']):4s} {ex['cap'] // 60:2d} min | {len(x):3d} copies {np.mean(x) / STAKE:+6.1%} | halves {np.mean(a) / STAKE if a else 0:+6.1%} / {np.mean(b) / STAKE if b else 0:+6.1%} | w/o5 {s5:+6.2f}"
        if a and b and np.mean(a) > 0 and np.mean(b) > 0 and s5 > 0: keep.append((np.mean(x), s, ex, line))
        if ex == EXITS[2]: print("  " + line)
keep.sort(key=lambda k: -k[0])
print(f"\npositive in both halves and without the best 5: {len(keep)} of {len(SETUPS) * len(EXITS)}")
for _, s, ex, line in keep: print("  KEEP " + line)
if TEST and keep:
    T_, trade, STAKE = load([TEST]); print(f"\nTEST on {TEST}: {len(T_)} calls of another week, each kept setup scored once")
    for _, s, ex, line in keep:
        v = [p for _, p in score(T_, trade, s, ex)]; s5 = sum(sorted(v, reverse=True)[5:]) if v else 0
        print(f"  {s[0]:8s} x={s[1]:<6g} wait {s[2]:4d} s | tp {str(ex['tp']):4s} {ex['cap'] // 60:2d} min | {len(v):3d} copies {np.mean(v) / STAKE if v else 0:+6.1%} | w/o5 {s5:+6.2f}")
