# Step 6: the fee-tier rule on buys the search never saw: wallet 4's copyable buys after the study data ended (Nov 14
# 08:13 Beirut) to Nov 15 14:10 Beirut, from the wider dataset built for the new floats (ALL), the four live kinds
# only. And the fee tier of the real trades that are only in that dataset.
#   python3 -I fresh_check.py ALL SKIPQ
import sys, os, json, datetime
ALL, SKIPQ = sys.argv[1], sys.argv[2]
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp(); os.environ["FE_T0"] = str(T0)
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); sys.argv = ["x", ALL, "0.5"]
import float_exits as F, lib as L
old = {f["key"] for f in json.load(open(f"{SKIPQ}/features.json"))}; tmax = max(f["t"] for f in json.load(open(f"{SKIPQ}/features.json")))
RULE = dict(tp=3.0, hold=600, early=(30, 290, 1.5), sl=None)
def bps_of(r):
    m, tr = F.P[r["key"]]; return next(e for e in tr if e["user"] == L.W4 and e["buy"] and e["slot"] == r["slot"])["bps"]
new = [r for r in F.rows if r["t"] > tmax and r["anchor"] in ("SOL", "WBTC", "PUMP", "SPCX")]
print(f"{len(new)} buys of the four live kinds after the study data; every copy, mean of the three landings:")
for name, sel in (("fee tier <= 100 bps", lambda b: b <= 100), ("fee tier > 100 bps", lambda b: b > 100)):
    rs = [r for r in new if sel(bps_of(r))]
    nets = [sum(L.model(F.PREP[r["key"], n], 0.5, **RULE)[0] for n in L.LAND) / 3 for r in rs]
    tp = sum(1 for r in rs if L.model(F.PREP[r["key"], 4], 0.5, **RULE)[1] == "tp")
    print(f"   {name}: {len(rs)} copies, {tp} take profits, net {sum(nets):+.2f} SOL" + (f" ({100 * sum(nets) / len(rs) / 0.5:+.1f}% a copy)" if rs else ""))
    for r, x in zip(rs, nets):
        if sel(50): print(f"      {datetime.datetime.fromtimestamp(r['t'] + 7200, datetime.timezone.utc).strftime('%m-%d %H:%M')} {r['mint8']} pays {r['anchor']} bps {bps_of(r)} net {x:+.3f}")
by8 = {r["mint8"]: r for r in F.rows}
print("the real trades of Nov 14-15 not in the study data: " + "; ".join(f"{c} fee tier {bps_of(by8[c]) if c in by8 else 'not in the rows'}" for c in ("8FE3SQjW", "4A7n9wq8", "BURn1o8x", "BTCmcoKg")))
# the same split over the whole wider dataset, the new kinds apart
for kinds, name in ((("SOL", "WBTC", "PUMP", "SPCX"), "the four live kinds, all dates"), (("TTWofwAg", "98sMhvDw", "DJTu7vi8", "XsbEhLAt"), "the four candidate floats")):
    for nm, sel in (("<= 100", lambda b: b <= 100), ("> 100", lambda b: b > 100)):
        rs = [r for r in F.rows if r["anchor"] in kinds and sel(bps_of(r))]
        nets = [sum(L.model(F.PREP[r["key"], n], 0.5, **RULE)[0] for n in L.LAND) / 3 for r in rs]
        print(f"   {name}, fee tier {nm}: {len(rs)} copies, net {sum(nets):+.2f}" + (f" ({100 * sum(nets) / len(rs) / 0.5:+.1f}% a copy)" if rs else ""))
