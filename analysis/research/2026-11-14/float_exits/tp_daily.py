# The owner's question (Nov 14): do the take profits come every day, and from every kind of copy (SOL, WBTC, PUMP,
# SPCX, 3-hop routes)? The bot's run at the rule live since Nov 14 (tp 3.0, 1200 s, early 30-290 s under 1.5x; 0.5 SOL,
# 2 open, SOL 1 / WBTC 2 / PUMP 1 / SPCX 1), landing 4: copies and take profits by Beirut day and by kind.
#   python3 -I tp_daily.py SPD
import sys, os, collections, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:2] + ["0.5"]; import float_exits as F
import lib as L
NEW = dict(tp=3.0, hold=1200, early=(30, 290, 1.5), sl=None); CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
res = F.sim(F.rows, 4, NEW, caps=CAPS)
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
K = ("SOL", "WBTC", "PUMP", "SPCX")
D = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0.0]))     # day -> kind -> [copies, tps, net]
for r, net, why in res:
    if why == "refused": continue
    for k in (r["anchor"], "3-hop" if r["hops"] == 3 else None, "all"):
        if k: x = D[day(r["t"])][k]; x[0] += 1; x[1] += why == "tp"; x[2] += net
print("copies / take profits by Beirut day (first and last day are partial)")
print(f"   {'day':5s} | " + " | ".join(f"{k:>9s}" for k in K + ("3-hop", "all")) + " | net SOL | net without the take profits")
for d in sorted(D):
    notp = sum(net for r, net, why in res if day(r["t"]) == d and why != "tp")
    print(f"   {d} | " + " | ".join(f"{D[d][k][0]:4d} / {D[d][k][1]:<2d}" for k in K + ("3-hop", "all")) + f" | {D[d]['all'][2]:+6.2f}  | {notp:+6.2f}")
nd = len(D)
print(f"\n{nd} days:")
for k in K + ("3-hop", "all"):
    c = sum(D[d][k][0] for d in D); t = sum(D[d][k][1] for d in D); n = sum(D[d][k][2] for d in D)
    tpnet = sum(net for r, net, why in res if why == "tp" and (k == "all" or r["anchor"] == k or (k == "3-hop" and r["hops"] == 3)))
    print(f"   {k:5s}: {c:3d} copies ({c / nd:4.1f} a day), {t:2d} take profits (1 in {c / max(1, t):.1f} copies; {t / nd:.1f} a day), days with at least one {sum(1 for d in D if D[d][k][1] > 0)} of {nd}; "
          f"net {n:+6.2f} SOL = take profits {tpnet:+6.2f}, the rest {n - tpnet:+6.2f}")
gaps = []; last = None
for r, net, why in res:
    if why == "tp":
        if last: gaps.append((r["t"] - last) / 3600)
        last = r["t"]
gaps.sort()
print(f"hours between one take profit and the next: median {gaps[len(gaps) // 2]:.1f}, longest {gaps[-1]:.1f}, second longest {gaps[-2]:.1f}")
run = worst = 0
for r, net, why in res:
    if why == "refused": continue
    run = 0 if why == "tp" else run + 1; worst = max(worst, run)
print(f"longest run of copies without a take profit: {worst}")
