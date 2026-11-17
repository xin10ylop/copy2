# Scores the frozen hypothesis H1 (out/vip_prereg_h1.md) on its test calls (vip_h1: never priced before the freeze).
#   python3 -I tg_vip_h1.py TGDIR [vip_h1 | vip_h1b]   (vip_h1b: the Nov 1-6 export, before the scan's days)
import sys, os, numpy as np
VD = sys.argv[2] if len(sys.argv) > 2 else "vip_h1"; TG = sys.argv[1]; here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "tg_vip_lab.py")).read().split("# ---- 1. signs")[0]
for cost in ("0.01", "0.0345"):
    os.environ["COST"] = cost; os.environ["VDIR"] = sys.argv[2] if len(sys.argv) > 2 else "vip_h1"; ns = {"__file__": os.path.join(here, "tg_vip_lab.py")}; sys.argv = ["x", TG]; os.environ["VDIR"] = VD
    exec(compile(src, "tg_vip_lab.py", "exec"), ns); R = sorted(ns["rows"], key=lambda r: r["t"]); entry, trade, STAKE = ns["entry"], ns["trade"], ns["STAKE"]
    R = [r for r in R if r["tier"] == "Diamond" and 0 < r.get("s_age", -1) <= 1]
    x = [(r["t"], trade(r, entry(r, delay=1), tp=2, cap=3600)) for r in R if entry(r, delay=1) is not None]
    if not x: print("no copies yet"); continue
    half = x[len(x) // 2][0]; v = [p for _, p in x]; a = [p for t, p in x if t < half]; b = [p for t, p in x if t >= half]; s5 = sum(sorted(v, reverse=True)[5:])
    print(f"H1 at {cost} SOL a round trip: {len(v)} copies {sum(v):+.2f} SOL ({np.mean(v) / STAKE:+.1%} a copy), won {np.mean([p > 0 for p in v]):.0%} | "
          f"halves {np.mean(a) / STAKE:+.1%} / {np.mean(b) / STAKE:+.1%} | without the best 5 {s5:+.2f}")
