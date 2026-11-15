# Lower min_sol from 1.45 to 1.3? The bot's run (the live rule, the six kinds, SOL 1 / WBTC 2 / one open from each
# other float, the fee rule on), its 1.45+ buys (ALL) with and without its 1.3-1.45 buys (CQ, all of them), at 2 and 3
# open, 0.5 SOL, raw, mean of three landings; blocks A | B | C; without the best 5; losing days; deepest fall.
#   python3 -I min13.py CQ ALL
import sys, os, datetime, collections
CQ, ALL = sys.argv[1], sys.argv[2]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); import lib as L
RULE = dict(tp=3.0, hold=600, early=(30, 290, 1.5), sl=None)
CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1, "TTWofwAg": 1, "DJTu7vi8": 1}
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp()
TB = L.T_STOP; TC = datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp()
blk = lambda r: 0 if r["t"] < TB else 1 if r["t"] < TC else 2
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
PREP, ROWS = {}, []
for SPD, lo, hi in ((ALL, 1.45, 1e9), (CQ, 1.3, 1.45)):
    rows, P, info = L.load(SPD, T0)
    for r in rows:
        if r["anchor"] not in CAPS or not (lo <= r["sol"] < hi): continue
        ps = [L.prep(r, P, n) for n in L.LAND]
        if any(p is None for p in ps): continue
        m, tr = P[r["key"]]; bps = next(e for e in tr if e["user"] == L.W4 and e["buy"] and e["slot"] == r["slot"])["bps"]
        if 0 < bps < 125: continue                              # the fee rule
        for n, p in zip(L.LAND, ps): PREP[r["key"], n] = p
        ROWS.append(r)
ROWS.sort(key=lambda r: r["t"]); last = max(day(r["t"]) for r in ROWS)
def sim(rs, n, mo):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x[0] > r["t"]]
        if len(open_) >= mo or sum(1 for x in open_ if x[1] == r["anchor"]) >= CAPS[r["anchor"]]: continue
        net, why, held = L.model(PREP[r["key"], n], 0.5, **RULE)
        if why != "refused": open_.append((r["t"] + held, r["anchor"]))
        out.append((r, net, why))
    return out
print(f"{sum(1 for r in ROWS if r['sol'] >= 1.45)} buys of 1.45+ SOL and {sum(1 for r in ROWS if r['sol'] < 1.45)} of 1.3-1.45 (fee rule applied); 0.5 SOL")
print(f"   {'':28s} | net (w/o best 5)   | A      B      C      | losing days, worst day, deepest fall | copies, take profits (landing 4)")
for mo in (2, 3):
    for name, lo in (("min_sol 1.45", 1.45), ("min_sol 1.3", 1.3)):
        rs = [r for r in ROWS if r["sol"] >= lo]; m = collections.defaultdict(float)
        for n in L.LAND:
            res = sim(rs, n, mo); nets = sorted((x[1] for x in res), reverse=True)
            m["net"] += sum(nets) / 3; m["wo5"] += sum(nets[5:]) / 3
            for k in range(3): m[f"b{k}"] += sum(x[1] for x in res if blk(x[0]) == k) / 3
            d = collections.defaultdict(float)
            for r, net, why in res: d[day(r["t"])] += net
            v = sorted(x for k, x in d.items() if k not in ("10-21", last)); m["neg"] += sum(1 for x in v if x < 0) / 3; m["worst"] += v[0] / 3
            cum = hi = lo_ = 0.0
            for r, net, why in res: cum += net; hi = max(hi, cum); lo_ = min(lo_, cum - hi)
            m["dd"] += lo_ / 3
            if n == 4: m["copies"] = len(res); m["tp"] = sum(1 for x in res if x[2] == "tp")
        print(f"   {mo} open, {name:20s} | {m['net']:+6.2f} ({m['wo5']:+6.2f}) | {m['b0']:+6.2f} {m['b1']:+6.2f} {m['b2']:+6.2f} | {m['neg']:4.1f} {m['worst']:+6.2f} {m['dd']:+6.2f}       | {m['copies']} {m['tp']}")
# the 1.3-1.45 buys outside the first sample (the slice was chosen on the sample): every copy, by block
import json, gzip
samp = set(json.load(gzip.open(f"{CQ}/paths_sample.json.gz")).keys())
for name, sel in (("in the first sample (the slice was picked on these)", lambda r: r["key"] in samp), ("not in it (unseen when it was picked)", lambda r: r["key"] not in samp)):
    rs = [r for r in ROWS if r["sol"] < 1.45 and sel(r)]
    nets = [(r, sum(L.model(PREP[r["key"], n], 0.5, **RULE)[0] for n in L.LAND) / 3) for r in rs]
    b = [sum(x for r, x in nets if blk(r) == k) for k in range(3)]; tp = sum(1 for r in rs if L.model(PREP[r["key"], 4], 0.5, **RULE)[1] == "tp")
    s = sorted((x for _, x in nets), reverse=True)
    print(f"   1.3-1.45, {name}: {len(rs)} copies, {tp} tp, every copy {sum(b):+.2f} (A {b[0]:+.2f}  B {b[1]:+.2f}  C {b[2]:+.2f}), without the best 3 {sum(s[3:]):+.2f}, {100 * sum(b) / max(1, len(rs)) / 0.5:+.1f}% a copy")
