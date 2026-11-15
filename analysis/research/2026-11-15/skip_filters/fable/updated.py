# The fee-tier rule with the newest buys in (the owner, Nov 15: "if it is more profitable why not deploy it?"): the
# bot's run on the wider dataset (ALL: Oct 21 - Nov 15 12:10 UTC), the four live kinds, with and without skipping
# coins whose fee tier is under 125 bps. Blocks A | B | C and D = after the study data (Nov 14 15:39 UTC on).
#   python3 -I updated.py ALL SKIPQ
import sys, os, json, datetime, collections, random
ALL, SKIPQ = sys.argv[1], sys.argv[2]
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp(); os.environ["FE_T0"] = str(T0)
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); sys.argv = ["x", ALL, "0.5"]
import float_exits as F, lib as L
tmax = max(f["t"] for f in json.load(open(f"{SKIPQ}/features.json")))
RULE = dict(tp=3.0, hold=600, early=(30, 290, 1.5), sl=None); CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
TB = L.T_STOP; TC = datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp()
blk = lambda r: 0 if r["t"] < TB else 1 if r["t"] < TC else 2 if r["t"] <= tmax else 3
rows = [r for r in F.rows if r["anchor"] in CAPS]
bps = {r["key"]: next(e for e in F.P[r["key"]][1] if e["user"] == L.W4 and e["buy"] and e["slot"] == r["slot"])["bps"] for r in rows}
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
out = {}
for name, keep in (("no rule", lambda r: True), ("skip fee tier under 125 bps", lambda r: not (0 < bps[r["key"]] < 125))):
    m = collections.defaultdict(float); dd = collections.defaultdict(float)
    for n in L.LAND:
        res = F.sim([r for r in rows if keep(r)], n, RULE, caps=CAPS); nets = sorted((x[1] for x in res), reverse=True)
        m["net"] += sum(nets) / 3; m["wo5"] += sum(nets[5:]) / 3; m["tp"] += sum(1 for x in res if x[2] == "tp") / 3; m["copies"] += len(res) / 3
        for k in range(4): m[f"b{k}"] += sum(x[1] for x in res if blk(x[0]) == k) / 3
        for r, net, why in res: dd[day(r["t"])] += net / 3
    out[name] = (m, dd)
    print(f"{name:28s}: copies {m['copies']:.0f}, take profits {m['tp']:.1f}, net {m['net']:+.2f} (without the best 5 {m['wo5']:+.2f}) | A {m['b0']:+.2f}  B {m['b1']:+.2f}  C {m['b2']:+.2f}  D (after the study data) {m['b3']:+.2f}")
a, b = out["no rule"][1], out["skip fee tier under 125 bps"][1]; days = sorted(set(a) | set(b)); d = [b[x] - a[x] for x in days]
random.seed(5); wins = sum(sum(random.choice(d) for _ in d) > 0 for _ in range(10000)) / 100
print(f"the rule's gain by day, {len(days)} days: total {sum(d):+.2f}, ahead on {sum(1 for x in d if x > 0)} days, behind on {sum(1 for x in d if x < 0)}; worst day for the rule {min(d):+.2f} ({days[d.index(min(d))]}), best {max(d):+.2f}; ahead in {wins:.1f}% of draws of the days")
low = [r for r in rows if 0 < bps[r["key"]] < 125]
print(f"low-fee buys: {len(low)} of {len(rows)}; by block A {sum(1 for r in low if blk(r) == 0)}, B {sum(1 for r in low if blk(r) == 1)}, C {sum(1 for r in low if blk(r) == 2)}, D {sum(1 for r in low if blk(r) == 3)}")
for name in out:
    v = sorted(out[name][1].values()); cum = hi = lo = 0.0
    for x in (out[name][1][k] for k in sorted(out[name][1])):
        cum += x; hi = max(hi, cum); lo = min(lo, cum - hi)
    print(f"{name:28s}: days {len(v)}, losing {sum(1 for x in v if x < 0)}, worst {v[0]:+.2f}, median {v[len(v) // 2]:+.2f}, best {v[-1]:+.2f}; deepest fall over days {lo:+.2f}")
print("by day, no rule / rule: " + "  ".join(f"{k} {a[k]:+.2f}/{b[k]:+.2f}" for k in days))
