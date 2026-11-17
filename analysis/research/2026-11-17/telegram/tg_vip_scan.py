# SolHouse VIP, a segment scan (the owner, Nov 17: "push hard ... from the ones that pay of course we can filter them,
# check age of token too"). Every priced VIP call of both samples (the audited, fixed lab rows), bought 1 s after the
# post; three fixed exits; every sign known at the call cut into fine buckets (not one median split), alone and in pairs
# with the tier. A segment is listed when it has 30+ copies, a positive mean in BOTH halves of the days, and a positive
# total without its best 5. With this many segments some pass by chance (the count scanned is printed): a survivor is a
# hypothesis to freeze and test on calls posted after this export, never a rule to trade.
# COST = 0.01 SOL a round trip here (a bot that does not race: small priority fees and about 1% of slippage; entry speed
# changes nothing on these calls); the 0.0345 of the racing studies is printed beside each survivor.
#   python3 -I tg_vip_scan.py TGDIR > out/tg_vip_scan.txt
import sys, os, numpy as np, itertools
TG = sys.argv[1]; here = os.path.dirname(os.path.abspath(__file__)); os.environ.setdefault("COST", "0.01")
src = open(os.path.join(here, "tg_vip_lab.py")).read().split("# ---- 1. signs")[0]
R = []
for v in ("vip", "vip_rest"):
    os.environ["VDIR"] = v; ns = {"__file__": os.path.join(here, "tg_vip_lab.py")}; sys.argv = ["x", TG]
    exec(compile(src, "tg_vip_lab.py", "exec"), ns); R += ns["rows"]; entry, trade, STAKE, COST = ns["entry"], ns["trade"], ns["STAKE"], ns["COST"]
R.sort(key=lambda r: r["t"]); half = R[len(R) // 2]["t"]
EX = {"hold 2 min": dict(tp=None, cap=120), "tp1.5 / 10 min": dict(tp=1.5, cap=600), "tp2 / 60 min": dict(tp=2, cap=3600)}
for r in R:
    k = entry(r, delay=1); r["pnl"] = {n: trade(r, k, **e) for n, e in EX.items()} if k is not None else None
R = [r for r in R if r["pnl"]]
B = {"s_age": [0, 1, 2, 5, 15, 1e9], "s_mc": [0, 7e3, 1e4, 1.5e4, 3e4, 1e12], "s_holders": [0, 50, 100, 200, 400, 1e9], "s_buyers": [0, 100, 200, 400, 800, 1e9],
     "s_avgbuy": [0, 0.2, 0.35, 0.5, 0.8, 1e9], "s_run10": [0, 1.2, 2, 3, 5, 1e9], "s_run1": [0, 0.95, 1.0, 1.1, 1.3, 1e9], "s_top10": [0, 0.15, 0.2, 0.25, 0.35, 9],
     "s_dev": [-1, 0, 0.02, 0.05, 9], "s_bundle": [-1, 0.1, 0.2, 0.3, 0.45, 9], "s_n10": [0, 150, 300, 600, 1200, 1e9], "s_txns": [0, 100, 200, 400, 800, 1e12],
     "s_sell10": [-1, 0.3, 0.4, 0.5, 0.6, 9], "s_prog": [-1, 0.3, 0.5, 0.7, 0.85, 9], "s_hour": [-1, 5, 11, 17, 24], "s_pace": [-1, 15, 25, 35, 50, 1e9],
     "s_spotted": [-1, 0, 1, 99], "s_smallbuys": [-1, 0.1, 0.2, 0.3, 9], "s_fee": [-1, 100, 125, 1e9]}
def seg_of(r, k):
    if k not in r: return None
    e = B[k]; i = next((j for j in range(len(e) - 1) if e[j] < r[k] <= e[j + 1]), None)
    return None if i is None else f"{k[2:]} ({e[i]:g}, {e[i + 1]:g}]"
segs = {}
for r in R:
    labs = [("tier " + str(r["tier"]),)] + [(s,) for s in (seg_of(r, k) for k in B) if s]
    labs += [(("tier " + str(r["tier"])), s[0]) for s in labs[1:]] + [(a[0], b[0]) for a, b in itertools.combinations([l for l in labs[1:] if l[0].split()[0] in ("age", "mc", "holders", "avgbuy", "run10")], 2)]
    for l in labs: segs.setdefault(l, []).append(r)
print(f"{len(R)} VIP calls bought 1 s after the post; costs {COST} SOL a round trip; {len(segs)} segments x {len(EX)} exits scanned = {len(segs) * len(EX)} tests")
base = {n: np.mean([r["pnl"][n] for r in R]) / STAKE for n in EX}
print("every call: " + ", ".join(f"{n} {v:+.1%}" for n, v in base.items()))
out = []
for l, v in segs.items():
    if len(v) < 30: continue
    for n in EX:
        a = [r["pnl"][n] for r in v if r["t"] < half]; b = [r["pnl"][n] for r in v if r["t"] >= half]
        if len(a) < 10 or len(b) < 10: continue
        x = a + b; s5 = sum(sorted(x, reverse=True)[5:])
        if np.mean(a) > 0 and np.mean(b) > 0 and s5 > 0:
            hi = [p - (0.0345 - COST) for p in x]   # the same copies at the racing studies' costs
            out.append((np.mean(x) / STAKE, " & ".join(l), n, len(x), sum(x), np.mean(a) / STAKE, np.mean(b) / STAKE, s5, np.mean(hi) / STAKE))
out.sort(reverse=True)
print(f"\nsegments with 30+ copies, both halves positive and positive without the best 5: {len(out)} of {len(segs) * len(EX)} tests")
for m, l, n, c, s, ma, mb, s5, mh in out[:40]:
    print(f"  {l:44s} | {n:14s} | {c:3d} copies {s:+6.2f} ({m:+6.1%}) | halves {ma:+6.1%} / {mb:+6.1%} | w/o5 {s5:+6.2f} | at 0.0345: {mh:+6.1%}")
print("\nthe age the post gives (minutes), every call, by bucket:")
for i in range(len(B["s_age"]) - 1):
    v = [r for r in R if B["s_age"][i] < r.get("s_age", -1) <= B["s_age"][i + 1]]
    if v: print(f"  age ({B['s_age'][i]:g}, {B['s_age'][i + 1]:g}] min: {len(v):3d} calls | " + " | ".join(f"{n} {np.mean([r['pnl'][n] for r in v]) / STAKE:+6.1%}" for n in EX))
v0 = [r for r in R if r.get("s_age", -1) == 0]
if v0: print(f"  age 0 (under a minute): {len(v0)} calls | " + " | ".join(f"{n} {np.mean([r['pnl'][n] for r in v0]) / STAKE:+6.1%}" for n in EX))
