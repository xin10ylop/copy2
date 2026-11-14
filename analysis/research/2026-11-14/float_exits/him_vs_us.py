# The owner's two remarks (Nov 14): "all our wins would have been losses at tp 3.0" and "he loses much less than us and
# even profits on trades we lose". (1) How high each real winner went within 30 min. (2) Why a copy cannot have his
# result: what our buy pays over the price his buy left, and what his sale does to the price (the 443 backtest coins,
# landing 4). (3) Our 18 real trades in the model under three rules: the rule live then, his every sale followed, and
# the new rule.
#   python3 -I him_vs_us.py SPD
import sys, os, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:2] + ["0.5"]; import float_exits as F
import lib as L, numpy as np
rows = F.rows; by = {r["mint8"]: r for r in rows}
print("(1) the real take profits: the coin's high within 30 min of its buy, and when it passed 3.0x")
for m8 in ("5tePJcGm", "Eymbsj8M", "BUdiaswB"):
    p = F.PREP[by[m8]["key"], 4]; w = p["age"] < 1790; i = L.first(p["px"] >= 3.0)
    print(f"   {m8}: high {p['px'][w].max():.2f}x, passed 3.0x at {int(p['age'][i])} s")
print("   BTCmcoKg (WBTC-paid, under 1.45 SOL at the study's WBTC price, fetched apart): high 4.75x at 49 s, passed 3.0x at 29 s")
prem, drop, before, after_ = [], [], [], []
for r in rows:
    p = F.PREP[r["key"], 4]
    prem.append(100 * (p["ent"][1] / p["ent"][0] and ((1.0) and 0) or 0)) if False else None
    m, tr = F.P[r["key"]]
    k = next(i for i, e in enumerate(tr) if e["user"] == L.W4 and e["buy"] and e["slot"] == r["slot"])
    vta = tr[k]["vt"]; j = min(k + 4, len(tr) - 1); prem.append(100 * ((vta / tr[j]["vt"]) ** 2 - 1))
    s = next((i for i in range(k + 1, len(tr)) if tr[i]["user"] == L.W4 and not tr[i]["buy"]), None)
    if s is not None and s - 1 > k:
        a, b = (vta / tr[s - 1]["vt"]) ** 2, (vta / tr[s]["vt"]) ** 2; drop.append(100 * (b / a - 1)); before.append(a); after_.append(b)
print(f"\n(2) {len(rows)} coins: our buy 4 trades after his pays {statistics.median(prem):+.1f}% over the price his buy left (median; a quarter pay over {np.percentile(prem, 75):+.1f}%)")
print(f"    his first sale moves the price by {statistics.median(drop):+.1f}% (median; a quarter by {np.percentile(drop, 25):+.1f}% or more): he sells at {statistics.median(before):.2f}x, the next seller at {statistics.median(after_):.2f}x")
E = (30, 180, 1.5)
REAL = [(0, "Ci9Bg1Bx", 0.1, -0.0597, 2.5, None), (1, "BttUQVPM", 0.1, -0.0455, 2.5, None), (2, "5tePJcGm", 0.1, 0.3531, 2.5, None), (3, "7dDprVHP", 0.5, -0.1106, 2.5, None),
        (4, "57pQW4mw", 0.5, -0.0124, 2.5, None), (5, "Eymbsj8M", 0.5, 0.6228, 2.5, None), (6, "GZn6HC8d", 0.5, -0.3763, 2.4, None), (7, "GaHAZThn", 0.5, -0.1884, 2.4, None),
        (8, "3EKoHX4f", 0.5, -0.0600, 2.4, E), (9, "6S3iL67j", 0.5, -0.0907, 2.4, E), (10, "BUdiaswB", 0.5, 1.3340, 2.4, E), (11, "GLmWEbqA", 0.5, -0.2837, 2.4, E),
        (12, "3a8RGrQg", 0.5, -0.2201, 2.4, E), (14, "FAVdiH3q", 1.0, -0.0851, 2.4, E), (15, "KgcdZjU4", 1.0, -0.2493, 2.4, E), (16, "oxbezHbo", 1.0, -0.4291, 2.4, E)]
print("\n(3) our real trades in the model (landing 4, the real stake), SOL: the rule live then | his every sale followed | the new rule (tp 3.0, 1200 s, early 30-290)")
tot = [0.0] * 4
for i, m8, st, real, tp, early in REAL:
    p = L.prep(by[m8], F.P, 4)
    a = L.model(p, st, tp=tp, hold=1790, early=early, sl=None); b = L.model(p, st, tp=tp, hold=1790, early=(0, 1e9, 1e9), sl=None)
    c = L.model(p, st, tp=3.0, hold=1200, early=(30, 290, 1.5), sl=None)
    tot[0] += real; tot[1] += a[0]; tot[2] += b[0]; tot[3] += c[0]
    print(f"   #{i:<2d} {m8} real {real:+.4f} | {a[0]:+.4f} ({a[1]:8s}) | {b[0]:+.4f} ({b[1]:8s} {b[2]:4d} s) | {c[0]:+.4f} ({c[1]:8s} {c[2]:4d} s)")
print(f"   16 trades (not #13, #17: no path): real {tot[0]:+.4f} | model, rule then {tot[1]:+.4f} | his every sale followed {tot[2]:+.4f} | new rule {tot[3]:+.4f}")
