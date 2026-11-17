# SolHouse VIP, the 2-minute confirmation (after the audit): don't buy at the call; wait, and buy only the calls that
# hold up in their first 2 minutes. The audit's fixes are in: no look-ahead (tg_vip_lab at()), trades in their real order
# inside a slot (tg_channel.order_slots), a coin that graduates while held is sold at GRAD_HAIRCUT x the curve's end
# (0.8; also 0.6 and 1.0 shown), costs 0.0345 SOL a round trip. Signs at +2 min use only trades up to t+120; the buy is
# the first trade from t+DELAY (DELAY >= 121), at whatever price (no cap over the call's price: we buy what we see).
# Discipline as the lab: everything is picked on TRAIN (first 50% of the design sample by time), must hold on VAL (next
# 25%), then TEST (last 25%) and the separate HOLDOUT calls (vip_rest) are scored once.
#   python3 -I tg_vip_confirm.py TGDIR > out/tg_vip_confirm.txt
import sys, os, json, statistics as st, numpy as np
TG = sys.argv[1]; here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "tg_vip_lab.py")).read().split("# ---- 1. signs")[0]
def rows_of(v):
    os.environ["VDIR"] = v; ns = {"__file__": os.path.join(here, "tg_vip_lab.py")}; sys.argv = ["x", TG]
    exec(compile(src, "tg_vip_lab.py", "exec"), ns); return ns
ns = rows_of("vip"); D_ = sorted(ns["rows"], key=lambda r: r["t"]); trade, STAKE = ns["trade"], ns["STAKE"]
H_ = sorted(rows_of("vip_rest")["rows"], key=lambda r: r["t"])
n = len(D_); TR, VA, TE = D_[: n // 2], D_[n // 2: 3 * n // 4], D_[3 * n // 4:]
def entry(r, delay):
    k = int(np.searchsorted(r["T"], r["t"] + delay, side="left"))
    return k if k < len(r["T"]) - 1 else None
def run(R, delay=121, **ex):
    out = []
    for r in R:
        k = entry(r, delay)
        if k is not None: out.append(trade(r, k, **ex))
    return out
def S(v):
    if not v: return "   0"
    s = sorted(v, reverse=True); return f"{len(v):4d} {sum(v):+7.2f} ({sum(v) / len(v) / STAKE:+6.1%}) w/o5 {sum(s[5:]):+7.2f}"
BASE = dict(tp=2.75, cap=3600)
print(f"design {n} calls (TRAIN {len(TR)}, VAL {len(VA)}, TEST {len(TE)}), HOLDOUT {len(H_)}; costs {ns['COST']} SOL a round trip, "
      f"graduation haircut {os.environ.get('GRAD_HAIRCUT', '0.8')}")
print(f"\n0. every call, bought at +121 s, tp 2.75 / 60 min: TRAIN {S(run(TR, **BASE))} | VAL {S(run(VA, **BASE))}")
# 1. signs, judged by what a copy bought at +121 s makes (not by a winner label)
keys = sorted({k for r in D_ for k in r if k[:2] in ("s_", "a_")}); kept = []
print("\n1. SIGNS (a copy at +121 s, tp 2.75 / 60 min): mean a copy below / above the TRAIN median, TRAIN | VAL")
for k in keys:
    a = [r for r in TR if k in r]; b = [r for r in VA if k in r]
    if len(a) < 30 or len(b) < 15: continue
    cut = st.median([r[k] for r in a]); m = lambda R: (sum(run(R, **BASE)) / max(1, len(run(R, **BASE)))) / STAKE
    lo_a, hi_a = m([r for r in a if r[k] <= cut]), m([r for r in a if r[k] > cut])
    lo_b, hi_b = m([r for r in b if r[k] <= cut]), m([r for r in b if r[k] > cut])
    ok = abs(hi_a - lo_a) >= 0.05 and abs(hi_b - lo_b) >= 0.05 and (hi_a > lo_a) == (hi_b > lo_b)
    if ok: kept.append((k, cut, hi_a > lo_a))
    print(f"   {k:11s} cut {cut:9.3g} | {lo_a:+6.1%} / {hi_a:+6.1%} | {lo_b:+6.1%} / {hi_b:+6.1%} {'KEPT ' + ('high' if hi_a > lo_a else 'low') if ok else ''}")
sc = lambda r: sum(1 for k, c, hi in kept if k in r and ((r[k] > c) if hi else (r[k] <= c)))
print(f"\n2. FILTER: at least N of the {len(kept)} kept signs ({', '.join(k for k, _, _ in kept)})")
bestN, bestm = 0, None
for N in range(0, len(kept) + 1):
    a = run([r for r in TR if sc(r) >= N], **BASE); b = run([r for r in VA if sc(r) >= N], **BASE)
    print(f"   at least {N}: TRAIN {S(a)} | VAL {S(b)}")
    if len(a) >= 20 and (bestm is None or sum(a) / len(a) > bestm): bestN, bestm = N, sum(a) / len(a)
F = lambda R: [r for r in R if sc(r) >= bestN]
print(f"   picked on TRAIN: at least {bestN}")
# 3. entry delay and exit, plateaus on TRAIN (20+ copies)
def plateau(res):
    m = [sum(a) / len(a) if a and len(a) >= 20 else -9 for *_, a, _ in res]; best = None
    for i in range(len(res)):
        nb = [m[j] for j in (i - 1, i, i + 1) if 0 <= j < len(res)]
        if min(nb) > 0 and (best is None or m[i] > m[best]): best = i
    return best if best is not None else int(np.argmax(m))
print("\n3. ENTRY DELAY (filtered, tp 2.75 / 60 min)")
res = [(d, run(F(TR), d, **BASE), run(F(VA), d, **BASE)) for d in (121, 150, 180, 240, 300)]
for d, a, b in res: print(f"   +{d} s: TRAIN {S(a)} | VAL {S(b)}")
DEL = res[plateau(res)][0]; print(f"   picked: +{DEL} s")
print("\n4. EXIT (filtered, the picked delay): tp x time limit, no stop")
res = []
for cap in (600, 1200, 1800, 3600):
    for tp in (1.5, 2, 2.5, 2.75, 3, 4, None):
        a = run(F(TR), DEL, tp=tp, cap=cap); b = run(F(VA), DEL, tp=tp, cap=cap); res.append(((tp, cap), a, b))
        print(f"   tp {str(tp):4s} {cap // 60:2d} min: TRAIN {S(a)} | VAL {S(b)}")
EXIT = res[plateau(res)][0]; EX = dict(tp=EXIT[0], cap=EXIT[1]); print(f"   picked: tp {EXIT[0]}, {EXIT[1] // 60} min")
print(f"\n5. SCORED ONCE: filter at least {bestN} of {len(kept)}, buy at +{DEL} s, tp {EXIT[0]} / {EXIT[1] // 60} min")
print(f"   VAL     {S(run(F(VA), DEL, **EX))}")
print(f"   TEST    {S(run(F(TE), DEL, **EX))}   (every call, same entry and exit: {S(run(TE, DEL, **EX))})")
print(f"   HOLDOUT {S(run(F(H_), DEL, **EX))}   (every call: {S(run(H_, DEL, **EX))})")
