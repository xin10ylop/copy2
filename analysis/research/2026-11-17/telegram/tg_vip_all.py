# SolHouse VIP, every call, no filter: does ANY simple way of following it pay? (the owner, Nov 17: "it has good reviews
# and paying subscribers, impossible"). Both samples (vip + vip_rest, the look-ahead fixed), buy 1 s after the post, every
# take profit from 1.1x to 5x with time limits from 1 to 60 min, no stop; by tier; and how often the calls reach 1.5x / 2x
# (what members see) against what a copy makes. Uses tg_vip_lab.py's rows, entry and trade (the audited, fixed code).
#   python3 -I tg_vip_all.py TGDIR > out/tg_vip_all.txt
import sys, os, json, numpy as np
TG = sys.argv[1]; here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "tg_vip_lab.py")).read().split("# ---- 1. signs")[0]   # rows, entry(), trade()
R = []
for v in ("vip", "vip_rest"):
    os.environ["VDIR"] = v; ns = {"__file__": os.path.join(here, "tg_vip_lab.py")}; sys.argv = ["x", TG]
    exec(compile(src, "tg_vip_lab.py", "exec"), ns); R += ns["rows"]; entry, trade, STAKE = ns["entry"], ns["trade"], ns["STAKE"]
R.sort(key=lambda r: r["t"]); half = R[len(R) // 2]["t"]
pk = [r["pr"][r["k0"] + 1:][r["T"][r["k0"] + 1:] <= r["t"] + 3600].max() / r["p0"] for r in R if (r["T"] > r["t"]).any()]
print(f"{len(R)} VIP calls with a price path (both samples). Within the hour of the post: reached 1.5x {np.mean([p >= 1.5 for p in pk]):.0%}, "
      f"2x {np.mean([p >= 2 for p in pk]):.0%}, 5x {np.mean([p >= 5 for p in pk]):.0%}, 10x {np.mean([p >= 10 for p in pk]):.0%} (what members see)")
best = []
for cap in (60, 120, 300, 600, 1800, 3600):
    for tp in (1.1, 1.2, 1.3, 1.5, 2, 3, 5, None):
        a, b = [], []
        for r in R:
            k = entry(r, delay=1)
            if k is None: continue
            (a if r["t"] < half else b).append(trade(r, k, tp=tp, cap=cap))
        x = a + b; best.append((sum(x) / len(x), cap, tp, len(x), sum(x), sum(a) / len(a), sum(b) / len(b)))
best.sort(key=lambda x: -x[0])
print("\nevery call, buy 1 s after: the 12 best of 48 exits (a copy at 0.5 SOL; costs 0.0026 SOL a round trip, the optimistic figure)")
for m, cap, tp, n_, s_, ma, mb in best[:12]:
    print(f"  tp {str(tp):4s} or {cap // 60 if cap >= 60 else cap}{' min' if cap >= 60 else ' s'}: {n_} copies {s_:+7.2f} SOL ({m / STAKE:+6.1%} a copy) | halves {ma / STAKE:+6.1%} / {mb / STAKE:+6.1%}")
print(f"  ... the worst: tp {best[-1][2]} or {best[-1][1] // 60} min {best[-1][0] / STAKE:+.1%} a copy")
print("\nby tier, the best exit above:")
_, cap, tp, *_ = best[0]
for tier in ("Diamond", "Safe", "Gamble", "Gamble Risk"):
    x = [trade(r, entry(r, delay=1), tp=tp, cap=cap) for r in R if r["tier"] == tier and entry(r, delay=1) is not None]
    if x: print(f"  {tier:12s}: {len(x):3d} copies {sum(x):+7.2f} ({sum(x) / len(x) / STAKE:+6.1%} a copy)")
