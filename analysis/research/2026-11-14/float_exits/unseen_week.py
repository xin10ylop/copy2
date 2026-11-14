# One more week the rules never saw (the owner, Nov 14): wallet 4's copyable buys BEFORE the study period, Oct 21
# 18:30 UTC to Oct 29 12:02 UTC (7.7 days), through the same pipeline (scan with the PUMP and SPCX floats, 31-minute
# paths, lib.py's model; 0.5 SOL, 2 open, SOL 1 / WBTC 2 / PUMP 1 / SPCX 1, raw). The rule live since Nov 14 was picked
# on Oct 29 - Nov 13 only. Its place among the 840 rules of float_exits.py on this week, against the old rule, and one
# setting changed at a time.
#   python3 -I unseen_week.py SPD
import sys, os, datetime, collections
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp()
os.environ["FE_T0"] = str(T0); os.environ["FE_T1"] = str(1793274720 + 600)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:2] + ["0.5"]; import float_exits as F
import lib as L
from multiprocessing import Pool
CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
R = lambda tp, hold, a, b, below=1.5, sl=None: dict(tp=tp, hold=hold, early=(a, b, below) if b else None, sl=sl)
CH, OLD = R(3.0, 1200, 30, 290), R(2.4, 1790, 30, 180)
def score(kw, cal=False):
    full = [F.sim(F.rows, n, kw, caps=CAPS, cal=cal) for n in L.LAND]
    wo = lambda k: sum(sum(sorted((x[1] for x in res), reverse=True)[k:]) for res in full) / 3
    return wo(0), wo(2), wo(5), [sum(x[1] for x in res) for res in full], sum(sum(1 for x in res if x[2] == "tp") for res in full) / 3, sum(len(res) for res in full) / 3
def ev(kw): s = score(kw); return kw, s[0], s[1]
if __name__ == "__main__":
    f = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d %H:%M")
    c = collections.Counter(r["anchor"] for r in F.rows)
    print(f"{len(F.rows)} copyable buys, {f(min(r['t'] for r in F.rows))} to {f(max(r['t'] for r in F.rows))} Beirut; paid with: {dict(c)}; {F.info['nopath']} without a path")
    print(f"\n{'rule':46s} | net    | w/o best 2 | w/o best 5 | landing 4 / 8 / late     | copies | tp exits | corrected")
    for name, kw in (("CHOSEN: tp 3.0, 1200 s, early 30-290", CH), ("old: tp 2.4, 1790 s, early 30-180", OLD), ("tp 2.4, the rest as chosen", R(2.4, 1200, 30, 290)), ("tp 2.0, the rest as chosen", R(2.0, 1200, 30, 290)),
                     ("tp 3.5, the rest as chosen", R(3.5, 1200, 30, 290)), ("tp 4.0, the rest as chosen", R(4.0, 1200, 30, 290)), ("timer 300 s", R(3.0, 300, 30, 290)), ("timer 600 s", R(3.0, 600, 30, 290)),
                     ("timer 900 s", R(3.0, 900, 30, 290)), ("timer 1790 s", R(3.0, 1790, 30, 290)), ("his sale never followed", R(3.0, 1200, 0, 0)), ("early 30-180 s", R(3.0, 1200, 30, 180)),
                     ("early 30-330 s (his 300 s sales too)", R(3.0, 1200, 30, 330)), ("his every sale followed", R(3.0, 1200, 0, 1e9, 1e9)), ("a 0.5x stop added", R(3.0, 1200, 30, 290, sl=0.5))):
        s = score(kw); cor = score(kw, cal=True)[0]
        print(f"{name:46s} | {s[0]:+6.2f} | {s[1]:+6.2f}     | {s[2]:+6.2f}     | " + " / ".join(f"{x:+6.2f}" for x in s[3]) + f" | {s[5]:5.0f}  | {s[4]:5.1f}    | {cor:+6.2f}")
    with Pool(4) as p: G = p.map(ev, F.GRID + [CH])
    ch = G[-1]; G = G[:-1]
    print(f"\nthe 840 rules of float_exits.py on this week: the chosen rule's net {ch[1]:+.2f} would rank {1 + sum(1 for g in G if g[1] > ch[1])} of {len(G) + 1}, without the best 2 {ch[2]:+.2f} rank {1 + sum(1 for g in G if g[2] > ch[2])}; "
          f"the old rule ranks {1 + sum(1 for g in G if g[1] > next(x[1] for x in G if x[0] == F.LIVE))} and {1 + sum(1 for g in G if g[2] > next(x[2] for x in G if x[0] == F.LIVE))}; rules above zero: {sum(1 for g in G if g[1] > 0)} of {len(G)}")
    G.sort(key=lambda g: -g[2]); print("   the 5 best of this week (hindsight):")
    for g in G[:5]: print(f"      {F.lab(g[0])} {g[1]:+6.2f} ({g[2]:+6.2f})")
    print("\nby kind, every copy, the chosen rule / the old rule (mean of landings):")
    for k in ("SOL", "WBTC", "PUMP", "SPCX"):
        rs = [r for r in F.rows if r["anchor"] == k]
        if not rs: continue
        a = [sum(L.model(F.PREP[r["key"], n], 0.5, **kw)[0] for n in L.LAND for r in rs) / 3 for kw in (CH, OLD)]
        print(f"   {k:5s} {len(rs):3d} copies: {a[0]:+6.2f} / {a[1]:+6.2f}")
    d = collections.defaultdict(lambda: [0.0, 0.0])
    for i, kw in enumerate((CH, OLD)):
        for n in L.LAND:
            for r, net, why in F.sim(F.rows, n, kw, caps=CAPS): d[datetime.datetime.fromtimestamp(r["t"] + 7200, datetime.timezone.utc).strftime("%m-%d")][i] += net / 3
    print("by Beirut day, chosen / old: " + "  ".join(f"{k} {v[0]:+.2f}/{v[1]:+.2f}" for k, v in sorted(d.items())))
