# Step 5: the candidate skip rules on the bot's own run (2 open; SOL 1, WBTC 2, PUMP 1, SPCX 1; a skipped copy
# frees its slot), the live exits, 0.5 SOL, each landing. For each rule: copies kept and skipped, take profits kept
# and lost (against the baseline run), the 20 biggest wins kept and lost, losing copies skipped, the net, the net
# without the best 5 and 10 trades, losing days, the worst day, the deepest fall, the blocks A | B | C; then days
# drawn again with replacement (10,000 times): how often the rule is ahead of no rule; and which of the bot's 24 real
# trades the rule would have skipped.
#   python3 -I filters.py SPD SKIPQ
import sys, os, json, datetime, collections, random
SPD, SKIPQ = sys.argv[1], sys.argv[2]
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp(); os.environ["FE_T0"] = str(T0)
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); sys.argv = ["x", SPD, "0.5"]
import float_exits as F, lib as L
FT = {f["key"]: f for f in json.load(open(f"{SKIPQ}/features.json"))}
RULE = dict(tp=3.0, hold=600, early=(30, 290, 1.5), sl=None); CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
BIG = ("3NZ9JMVB", "pumpCmXq", "SPCXxcqX")
CAND = [("no rule", lambda f: False),
        ("fee tier <= 100 bps", lambda f: f["bps"] <= 100),
        ("fee tier <= 30 bps", lambda f: f["bps"] <= 30),
        ("fee tier 31-100 bps", lambda f: 30 < f["bps"] <= 100),
        ("fee tier <= 200 bps, coin quoted in another coin", lambda f: f["bps"] <= 200 and f["quote"] not in BIG),
        ("fee tier <= 100 and we pay with SOL", lambda f: f["bps"] <= 100 and f["anchor"] == "SOL"),
        ("curve under 10% sold", lambda f: f["sold"] <= 0.0989),
        ("curve under 16% sold", lambda f: f["sold"] <= 0.1626),
        ("its buy moved the price over 1.12x", lambda f: f["move"] > 1.119),
        ("its buy moved the price over 1.12x and curve under 16% sold", lambda f: f["move"] > 1.119 and f["sold"] <= 0.1626),
        ("every SOL-paid copy", lambda f: f["anchor"] == "SOL"),
        ("fee tier <= 100 or curve under 10% sold", lambda f: f["bps"] <= 100 or f["sold"] <= 0.0989)]
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
FULL = sorted({day(r["t"]) for r in F.rows} - {"10-21", max(day(r["t"]) for r in F.rows)})
def run(skip, n):
    rs = [r for r in F.rows if not skip(FT[r["key"]])]; return F.sim(rs, n, RULE, caps=CAPS)
base = {n: run(CAND[0][1], n) for n in L.LAND}
REAL = ["Ci9Bg1Bx", "BttUQVPM", "5tePJcGm", "7dDprVHP", "57pQW4mw", "Eymbsj8M", "GZn6HC8d", "GaHAZThn", "3EKoHX4f", "6S3iL67j", "BUdiaswB", "GLmWEbqA", "3a8RGrQg", "BTCmcoKg",
        "FAVdiH3q", "KgcdZjU4", "oxbezHbo", "EH6yuh4Y", "4TMzhGzY", "6KpdMXAS", "DHcZRxRX", "8FE3SQjW", "4A7n9wq8", "BURn1o8x"]
REALNET = dict(zip(REAL, [-0.0597, -0.0455, 0.3531, -0.1106, -0.0124, 0.6228, -0.3763, -0.1884, -0.0600, -0.0907, 1.3340, -0.2837, -0.2201, 0.5786, -0.0851, -0.2493, -0.4291,
                           -0.4260, -0.0310, -0.2420, -0.1991, -0.0924, -0.0703, 0.6038]))
by8 = {r["mint8"]: r for r in F.rows}
random.seed(3)
def days_of(res):
    d = collections.defaultdict(float)
    for r, net, why in res: d[day(r["t"])] += net
    return d
basedays = {n: days_of(base[n]) for n in L.LAND}
print(f"{len(F.rows)} buys; the bot's run; mean of the three landings unless said; {len(FULL)} full Beirut days")
for name, skip in CAND:
    runs = {n: run(skip, n) for n in L.LAND}; nskip = sum(1 for r in F.rows if skip(FT[r["key"]]))
    m = collections.defaultdict(float); diffs = []
    for n in L.LAND:
        res = runs[n]; b = base[n]; nets = sorted((x[1] for x in res), reverse=True)
        btp = {x[0]["key"] for x in b if x[2] == "tp"}; kept = {x[0]["key"] for x in res}; top20 = [x[0]["key"] for x in sorted(b, key=lambda x: -x[1])[:20]]
        m["copies"] += len(res) / 3; m["tp"] += sum(1 for x in res if x[2] == "tp") / 3; m["tp_lost"] += sum(1 for k in btp if k not in kept) / 3
        m["top20_lost"] += sum(1 for k in top20 if k not in kept) / 3
        m["losers_skipped"] += sum(1 for x in b if x[1] < 0 and x[0]["key"] not in kept) / 3
        m["net"] += sum(nets) / 3; m["wo5"] += sum(nets[5:]) / 3; m["wo10"] += sum(nets[10:]) / 3
        d = days_of(res); v = sorted(d[x] for x in FULL); m["neg"] += sum(1 for x in v if x < 0) / 3; m["worst"] += v[0] / 3
        cum = hi = lo = 0.0
        for r, net, why in res:
            cum += net; hi = max(hi, cum); lo = min(lo, cum - hi)
        m["dd"] += lo / 3
        for k in range(3): m[f"b{k}"] += sum(x[1] for x in res if FT[x[0]["key"]]["blk"] == k) / 3
        diffs.append([d[x] - basedays[n][x] for x in sorted(set(d) | set(basedays[n]))])
    alld = [sum(x) / 3 for x in zip(*[dd_ for dd_ in diffs if len(dd_) == len(diffs[0])])] if all(len(x) == len(diffs[0]) for x in diffs) else diffs[0]
    wins = sum(sum(random.choice(alld) for _ in alld) > 0 for _ in range(10000)) / 100 if name != "no rule" else 0
    real = [c for c in REAL if c in by8 and skip(FT[by8[c]["key"]])]
    print(f"\n== skip: {name}   ({nskip} of {len(F.rows)} buys match)")
    print(f"   copies {m['copies']:.0f} | take profits {m['tp']:.1f} (lost {m['tp_lost']:.1f}) | of the 20 biggest wins lost {m['top20_lost']:.1f} | losing copies skipped {m['losers_skipped']:.0f}")
    print(f"   net {m['net']:+.2f} | without the best 5 {m['wo5']:+.2f}, best 10 {m['wo10']:+.2f} | losing days {m['neg']:.1f} of {len(FULL)}, worst {m['worst']:+.2f} | deepest fall {m['dd']:+.2f} | A {m['b0']:+.2f}  B {m['b1']:+.2f}  C {m['b2']:+.2f}")
    print("   by landing 4 / 8 / late: " + " / ".join(f"{sum(x[1] for x in runs[n]):+.2f}" for n in L.LAND) + (f" | ahead of no rule in {wins:.1f}% of draws of the days" if name != "no rule" else ""))
    if name != "no rule": print(f"   real trades it would have skipped: {[(c, REALNET[c]) for c in real]} = {sum(REALNET[c] for c in real):+.4f} SOL; real trades not in the data: {[c for c in REAL if c not in by8]}")
