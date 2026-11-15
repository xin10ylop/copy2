# Part 2: bailing out in the first seconds (reported apart from the entry filters). On top of the live rule (tp 3.0,
# 600 s, early 30-290 s under 1.5x), sell early when, T seconds after wallet 4's buy:
#   (a) the price is under X;  (b) the price has never been above Y since our buy;  (c) more of the trades since our
#   buy were sells than buys (by count; by quote volume). The sell lands on the trade after the check. The bot's run
#   (2 open; SOL 1, WBTC 2, PUMP 1, SPCX 1), 0.5 SOL, each landing; blocks A | B | C; take profits lost; without the
#   best 5 / 10; losing days; the deepest fall. Also each rule together with the fee-tier entry filter.
#   python3 -I bail.py SPD SKIPQ
import sys, os, json, datetime, collections
SPD, SKIPQ = sys.argv[1], sys.argv[2]
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp(); os.environ["FE_T0"] = str(T0)
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); sys.argv = ["x", SPD, "0.5"]
import float_exits as F, lib as L
import numpy as np
FT = {f["key"]: f for f in json.load(open(f"{SKIPQ}/features.json"))}
RULE = dict(tp=3.0, hold=600, early=(30, 290, 1.5), sl=None); CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}; STAKE = 0.5
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
FULL = sorted({day(r["t"]) for r in F.rows} - {"10-21", max(day(r["t"]) for r in F.rows)})
# the buys' own flags per path (who bought, for the sell/buy balance): rebuilt from the paths
BUY = {}
for r in F.rows:
    m, tr = F.P[r["key"]]; k = next(i for i, e in enumerate(tr) if e["user"] == L.W4 and e["buy"] and e["slot"] == r["slot"])
    for n in L.LAND:
        j = k + len([e for e in tr[k + 1:] if e["slot"] <= tr[k]["slot"] + 1]) if n == "slot+1" else min(k + n, len(tr) - 1)
        rest = tr[j + 1:]; BUY[r["key"], n] = (np.array([e["buy"] for e in rest], bool), np.array([float(e["q"]) for e in rest]))
def payoff(p, ex):
    vt0, vq0, bps0 = p["ent"]; Q = STAKE * 1e9 * p["hopf"] / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq_r = p["vq"][ex] + net_in; vt_r = p["vt"][ex] * p["vq"][ex] / vq_r
    return (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - p["bps"][ex] / 1e4) * p["rate"] * p["hopf"] / 1e9 - STAKE - 0.0026
def copy(r, n, bail):
    p = F.PREP[r["key"], n]; net, why, held = L.model(p, STAKE, **RULE)
    if bail is None or why == "refused" or len(p["px"]) == 0: return net, why, held
    kind, T, x = bail; i = L.first(p["age"] >= T)
    if i is None or p["age"][i] > held or (p["age"][i] == held and why != "time"): return net, why, held
    before = p["age"] < T
    if kind == "under": hit = (p["px"][before][-1] if before.any() else 1.0) < x
    elif kind == "never": hit = (p["px"][before].max() if before.any() else 0.0) < x
    else:
        b, q = BUY[r["key"], n]; bb, qq = b[before], q[before]
        hit = ((~bb).sum() > bb.sum()) if kind == "sells_n" else (qq[~bb].sum() > qq[bb].sum())
        hit = hit and before.sum() >= 3
    if not hit: return net, why, held
    ex = min(i + 1, len(p["px"]) - 1); return payoff(p, ex), "bail", int(p["age"][ex])
def run(n, bail, skip=None):
    out, open_ = [], []
    for r in F.rows:
        if skip and skip(FT[r["key"]]): continue
        open_ = [x for x in open_ if x[0] > r["t"]]
        if len(open_) >= 2 or sum(1 for x in open_ if x[1] == r["anchor"]) >= CAPS[r["anchor"]]: continue
        net, why, held = copy(r, n, bail)
        if why != "refused": open_.append((r["t"] + held, r["anchor"]))
        out.append((r, net, why))
    return out
def score(bail, skip=None, base=None):
    m = collections.defaultdict(float)
    for n in L.LAND:
        res = run(n, bail, skip); nets = sorted((x[1] for x in res), reverse=True)
        m["net"] += sum(nets) / 3; m["wo5"] += sum(nets[5:]) / 3; m["wo10"] += sum(nets[10:]) / 3; m["tp"] += sum(1 for x in res if x[2] == "tp") / 3; m["bail"] += sum(1 for x in res if x[2] == "bail") / 3
        d = collections.defaultdict(float)
        for r, net, why in res: d[day(r["t"])] += net
        v = sorted(d[x] for x in FULL); m["neg"] += sum(1 for x in v if x < 0) / 3; m["worst"] += v[0] / 3
        cum = hi = lo = 0.0
        for r, net, why in res:
            cum += net; hi = max(hi, cum); lo = min(lo, cum - hi)
        m["dd"] += lo / 3
        for k in range(3): m[f"b{k}"] += sum(x[1] for x in res if FT[x[0]["key"]]["blk"] == k) / 3
    return m
def show(name, m, b=None):
    star = "" if b is None else ("  <- better in A, B and C" if all(m[f"b{k}"] > b[f"b{k}"] for k in range(3)) else "")
    print(f"   {name:44s} | {m['net']:+6.2f} | {m['b0']:+6.2f} {m['b1']:+6.2f} {m['b2']:+6.2f} | {m['wo5']:+6.2f} {m['wo10']:+6.2f} | tp {m['tp']:4.1f} bailed {m['bail']:5.1f} | losing days {m['neg']:3.1f}, worst {m['worst']:+5.2f}, fall {m['dd']:+5.2f}{star}")
base = score(None)
print(f"{len(F.rows)} buys; the bot's run, mean of the three landings; net | A B C | without the best 5, 10 | take profits, bails | days")
show("the live rule, no bail-out", base)
RULES = [("under", T, x) for T in (15, 30, 45, 60, 90, 120, 180) for x in (0.6, 0.7, 0.8, 0.9, 1.0)] + [("never", T, y) for T in (30, 60, 120, 180) for y in (1.05, 1.1, 1.2, 1.5)] \
        + [(k, T, 0) for k in ("sells_n", "sells_q") for T in (15, 30, 60)]
lab = lambda b: (f"price under {b[2]}x at {b[1]} s" if b[0] == "under" else f"never above {b[2]}x by {b[1]} s" if b[0] == "never" else f"more sells than buys ({'count' if b[0] == 'sells_n' else 'volume'}) by {b[1]} s")
R = [(b, score(b)) for b in RULES]
for b, m in R: show(lab(b), m, base)
good = [(b, m) for b, m in R if all(m[f"b{k}"] > base[f"b{k}"] for k in range(3))]
print(f"\n{len(RULES)} bail-out rules tried; better than no bail-out in each of A, B and C: {len(good)}")
low = lambda f: f["bps"] <= 100
fb = score(None, low); print("\nwith the fee-tier entry filter (skip when the fee tier is 100 bps or less):"); show("fee filter, no bail-out", fb, base)
for b, m in sorted(R, key=lambda x: -x[1]["net"])[:5]: show("fee filter + " + lab(b), score(b, low), fb)
