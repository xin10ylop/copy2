# How many copies at once each float (and SOL) must carry: the bot's run at the new rule (tp 3.0, early 30-290 s
# under 1.5x, 1790 s, no stop) and the live one, 0.5 SOL, 2 open, with caps per paying token; a day's result spread.
#   python3 -I caps_check.py SPD [STAKE]
import sys, os, collections, datetime, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:3]; import float_exits as F
import lib as L
rows = F.rows; NEW = dict(tp=3.0, hold=1790, early=(30, 290, 1.5), sl=None)
days = (F.END - L.T_STOP) / 86400
print(f"0.5 SOL, 2 open; first half (w/o best 2) | second half | both; copies a day; SOL needed = 0.55 a SOL slot + 0.5 a float slot")
for rname, kw in (("live (tp 2.4, early 30-180)", F.LIVE), ("new (tp 3.0, early 30-290)", NEW)):
    print(f" {rname}")
    for name, caps, need in (("SOL 2, WBTC 2, PUMP 2, SPCX 2", {}, 4.1), ("SOL 2, WBTC 2, PUMP 1, SPCX 1", {"PUMP": 1, "SPCX": 1}, 3.1), ("SOL 2, WBTC 1, PUMP 1, SPCX 1", {"WBTC": 1, "PUMP": 1, "SPCX": 1}, 2.6),
                             ("SOL 1, WBTC 2, PUMP 1, SPCX 1", {"SOL": 1, "PUMP": 1, "SPCX": 1}, 2.55), ("SOL 1, WBTC 1, PUMP 1, SPCX 1", {"SOL": 1, "WBTC": 1, "PUMP": 1, "SPCX": 1}, 2.05),
                             ("no SOL routes; WBTC 2, PUMP 1, SPCX 1", {"SOL": 0, "PUMP": 1, "SPCX": 1}, 2.0), ("no SOL routes; WBTC 1, PUMP 1, SPCX 1", {"SOL": 0, "WBTC": 1, "PUMP": 1, "SPCX": 1}, 1.5)):
        n = sum(len(F.sim(rows, k, kw, caps=caps)) for k in L.LAND) / 3
        print(f"   {name:38s} needs {need:4.2f} | raw {F.show(F.halves(rows, kw, caps=caps))} | cor {F.halves(rows, kw, caps=caps, cal=True)[0][0] + F.halves(rows, kw, caps=caps, cal=True)[1][0]:+6.2f} | {n / days:4.1f} a day")
caps = {"SOL": 1, "WBTC": 1, "PUMP": 1, "SPCX": 1}
res = F.sim(rows, 4, NEW, caps=caps); byday = collections.defaultdict(float)
for r, net, why in res: byday[datetime.datetime.fromtimestamp(r["t"], datetime.timezone.utc).strftime("%m-%d")] += net
v = sorted(byday.values())
print(f"\nnew rule, 1 open from each, landing 4, by UTC day: {len(v)} days, {sum(1 for x in v if x > 0)} up; worst {v[0]:+.2f}, second worst {v[1]:+.2f}, median {statistics.median(v):+.2f}, best {v[-1]:+.2f}")
print("   " + "  ".join(f"{d} {x:+.2f}" for d, x in sorted(byday.items())))
streak = worst = 0.0
for r, net, why in res:
    streak = min(0.0, streak + net); worst = min(worst, streak)
print(f"   deepest fall from a high: {worst:+.2f} SOL; exits {dict(collections.Counter(x[2] for x in res))}")
by = collections.defaultdict(list)
for r, net, why in res: by[r["anchor"]].append(net)
print("   by what we pay with: " + "; ".join(f"{k} {len(x)} copies {sum(x):+.2f}" for k, x in by.items()))
