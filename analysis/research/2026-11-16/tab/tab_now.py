# TAB16RxX with wallet 4's method (the owner, Nov 15 night: "can we do all of that for the second wallet"). Step 1, no
# new fetch: the 183 copyable 1.0+ SOL buys of Oct 29 - Nov 13 that ../../2026-11-13/tab_exits/ built (its transactions,
# the bot's scan, each coin's 31-minute path), scored with the model and the signals of ../signals/ and ../final_exit/.
# The honest test of the method: wallet 4's frozen setup applied to TAB16RxX UNTOUCHED (nothing in it was picked on
# this wallet), against the two rules TAB16RxX ran live, then each part changed alone.
#   python3 -I tab_now.py PATHS SCAN W4SCAN > out/tab_now.txt     (PATHS = tab/lk/paths, SCAN = tab_exits/out/scan_tab.txt)
import sys, os, re, json, gzip, datetime, collections, random
import numpy as np
PATHS, SCAN, W4SCAN = sys.argv[1:4]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); import lib as L
TAB = "TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3"; W4 = L.W4; L.W4 = TAB      # lib.prep finds "its" buy and sales by this
OURS = {TAB, "Eao8T2Pk2aDzPWUFCA8si7oWd5ndFKfnX3HjYMpERst6"}
P = {}
for f in os.listdir(PATHS):
    slot, mint = f.split(".")[0].split("_"); P[f"{slot}_{mint[:8]}"] = (mint, json.load(gzip.open(f"{PATHS}/{f}")))
rows = []
for l in open(SCAN):
    m = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL from (\S+) quote (\S+) jupiter (\S+): ROUTABLE .*?input: (\w{8})", l)
    if not m: continue
    key = f"{m.group(1)}_{m.group(2)}"
    if key not in P: continue
    tr = P[key][1]; its = next((e for e in tr if e["user"] == TAB and e["buy"] and e["slot"] == int(m.group(1))), None)
    if its is None: continue
    rows.append(dict(slot=int(m.group(1)), mint8=m.group(2), mint=P[key][0], t=its["t"], sol=float(m.group(3)), hops=l.count("Hop {"), key=key,
                     anchor={"So111111": "SOL", "3NZ9JMVB": "WBTC"}.get(m.group(7), m.group(7))))
rows.sort(key=lambda r: r["t"]); last, ROWS = {}, []
for r in rows:
    again = r["mint8"] in last and r["t"] - last[r["mint8"]] < 3600; last[r["mint8"]] = r["t"]
    if not again: ROWS.append(r)
PREP, EX = {}, {}
for r in list(ROWS):
    ps = [L.prep(r, P, n) for n in L.LAND]
    if any(p is None for p in ps): ROWS.remove(r); continue
    tr = P[r["key"]][1]; k = next(i for i, e in enumerate(tr) if e["user"] == TAB and e["buy"] and e["slot"] == r["slot"])
    for n, p in zip(L.LAND, ps):
        PREP[r["key"], n] = p; rest = tr[len(tr) - len(p["px"]):]; j = len(tr) - len(p["px"]) - 1
        other = np.array([e["user"] not in OURS for e in rest], dtype=bool); sell = np.array([not e["buy"] for e in rest], dtype=bool) & other
        EX[r["key"], n] = dict(sell=sell, buy=other & ~sell, pin=(tr[k]["vt"] / tr[j]["vt"]) ** 2)
TC = datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp()
half = lambda r: 0 if r["t"] < TC else 1
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
def trigger(p, x, sig):
    age = p["age"]; n = len(age)
    if n == 0: return None
    if sig[0] == "stall":
        px = p["px"] / x["pin"]; pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]])
        last = np.maximum.accumulate(np.where(newhi, age, -1e9)); return L.first((pk >= 1.0) & (age - last >= sig[1]))
    lo = np.searchsorted(age, age - sig[2], side="left")
    s = np.concatenate([[0], np.cumsum(x["sell"])]); b = np.concatenate([[0], np.cumsum(x["buy"])])
    return L.first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= sig[1]) & (age >= sig[3]))
def model(p, x, stake, sigs, tp, hold, early):
    if p["refused"]: return (-0.0004, "refused", 0)
    base = L.model(p, stake, tp, hold, early, None)
    t = [(i, s[0]) for i, s in ((trigger(p, x, s), s) for s in sigs) if i is not None]
    if not t: return base
    i, why = min(t)
    if p["age"][i] >= hold: return base
    ex = min(i + 1, len(p["px"]) - 1)
    if p["age"][ex] > base[2] or (p["age"][ex] == base[2] and base[1] != "time"): return base
    vt0, vq0, bps0 = p["ent"]
    Q = stake * 1e9 * p["hopf"] / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq_r = p["vq"][ex] + net_in; vt_r = p["vt"][ex] * p["vq"][ex] / vq_r
    out = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - p["bps"][ex] / 1e4)
    return (out * p["rate"] * p["hopf"] / 1e9 - stake - 0.0026, why, int(p["age"][ex]))
STAKE = 0.5
def score(rule):
    sigs, tp, hold, early = rule
    tot, hv, wo2, wo5, days, whys = 0, [0, 0], 0, 0, collections.defaultdict(float), collections.Counter()
    for n in L.LAND:
        out, open_ = [], []
        for r in ROWS:
            open_ = [y for y in open_ if y > r["t"]]
            if len(open_) >= 2: continue
            net, why, held = model(PREP[r["key"], n], EX[r["key"], n], STAKE, sigs, tp, hold, early)
            if why != "refused": open_.append(r["t"] + held)
            out.append((r, net, why))
        v = sorted((y[1] for y in out), reverse=True); tot += sum(v) / 3; wo2 += sum(v[2:]) / 3; wo5 += sum(v[5:]) / 3
        for r, net, why in out: hv[half(r)] += net / 3; days[day(r["t"])] += net / 3; whys[why] += 1 / 3
    ks = sorted(days)[1:-1]; dv = sorted(days[k] for k in ks)
    return dict(tot=tot, h=hv, wo2=wo2, wo5=wo5, neg=sum(1 for y in dv if y < 0), nd=len(dv), worst=dv[0], days={k: days[k] for k in ks}, whys=whys)
PR, ST = ("press", 5, 60, 30), ("stall", 180)
RULES = collections.OrderedDict([
    ("TAB live 1 (Nov 12): tp 3.0, 300 s, its sale never", ((), 3.0, 300, None)),
    ("TAB live 2 (Nov 13): tp 4.0, 600 s, its sale 0-60 s", ((), 4.0, 600, (0, 60, 1e9))),
    ("WALLET 4'S FROZEN SETUP, untouched", ((PR, ST), 4.0, 600, (30, 290, 1.5))),
    ("  the same without the two signals", ((), 4.0, 600, (30, 290, 1.5))),
    ("  the same without the stall", ((PR,), 4.0, 600, (30, 290, 1.5))),
    ("  the same without the pressure rule", ((ST,), 4.0, 600, (30, 290, 1.5))),
    ("  the same, tp 3.0", ((PR, ST), 3.0, 600, (30, 290, 1.5))),
    ("  the same, tp 5.0", ((PR, ST), 5.0, 600, (30, 290, 1.5))),
    ("  the same, timer 300 s", ((PR, ST), 4.0, 300, (30, 290, 1.5))),
    ("  the same, timer 900 s", ((PR, ST), 4.0, 900, (30, 290, 1.5))),
    ("  the same, its sale never followed", ((PR, ST), 4.0, 600, None)),
    ("  the same, its sale 0-60 s at any price", ((PR, ST), 4.0, 600, (0, 60, 1e9))),
    ("  the same, its sale 0-290 s under 1.5x", ((PR, ST), 4.0, 600, (0, 290, 1.5))),
    ("  the same, its sale 30-290 s at any price", ((PR, ST), 4.0, 600, (30, 290, 1e9))),
    ("  the same, its sale at any time, any price", ((PR, ST), 4.0, 600, (0, 600, 1e9))),
])
if __name__ == "__main__":
    S = {nm: score(r) for nm, r in RULES.items()}
    REF = S["TAB live 2 (Nov 13): tp 4.0, 600 s, its sale 0-60 s"]; random.seed(7)
    print(f"{len(ROWS)} copyable first buys of 1.0+ SOL, {day(ROWS[0]['t'])} to {day(ROWS[-1]['t'])} (halves split Nov 6: {sum(1 for r in ROWS if half(r) == 0)} / {sum(1 for r in ROWS if half(r) == 1)}); "
          f"kinds {dict(collections.Counter(r['anchor'] for r in ROWS))}; {STAKE} SOL, 2 open, mean of three landings")
    print(f"   {'rule':52s} | total  | halves        | w/o best 2 | w/o best 5 | days<0 | worst | vs TAB live 2: gain, ahead in draws [5%, 95%] | exits (a landing)")
    for nm, s in S.items():
        d = [s["days"][k] - REF["days"][k] for k in REF["days"]]; dr = sorted(sum(random.choice(d) for _ in d) for _ in range(2000))
        print(f"   {nm:52s} | {s['tot']:+6.2f} | {s['h'][0]:+6.2f} {s['h'][1]:+6.2f} | {s['wo2']:+6.2f}     | {s['wo5']:+6.2f}     | {s['neg']:2d}/{s['nd']} | {s['worst']:+5.2f} | {s['tot'] - REF['tot']:+6.2f}, {sum(1 for y in dr if y > 0) / 20:5.1f}% [{dr[100]:+5.1f}, {dr[1900]:+5.1f}] | "
              + " ".join(f"{w} {c:.0f}" for w, c in s["whys"].most_common() if w != "refused"))
    # what TAB16RxX did, under wallet 4's frozen setup (every copy, landing 4)
    sigs, tp, hold, early = RULES["WALLET 4'S FROZEN SETUP, untouched"]; grp = collections.defaultdict(list)
    for r in ROWS:
        p, x = PREP[r["key"], 4], EX[r["key"], 4]
        if p["refused"]: continue
        j = L.first(p["sell"]); net, why, held = model(p, x, STAKE, sigs, tp, hold, early)
        if j is None or p["age"][j] > held: k = "it had not sold when we closed"
        elif why == "its_sell": k = "it sold under 1.5x at 30-290 s: followed"
        elif p["age"][j] < 30: k = "it sold in its first 30 s: not followed"
        elif p["age"][j] >= 290: k = "it sold after 290 s: not followed"
        else: k = "it sold at 1.5x or more: not followed"
        grp[k].append(net)
    print("== wallet 4's frozen setup on TAB16RxX, by what TAB16RxX did (every copy, landing 4)")
    for k, v in sorted(grp.items(), key=lambda q: -len(q[1])): print(f"   {k:44s}: {len(v):3d} copies, net {sum(v):+6.2f} SOL, {100 * sum(v) / len(v) / STAKE:+6.1f}% a copy, {100 * sum(1 for y in v if y > 0) / len(v):4.1f}% won")
    # does it add trades? the overlap with wallet 4 (wallet 4's own buys of any size, from its scan)
    w4 = collections.defaultdict(list)
    for l in open(W4SCAN):
        m = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL", l)
        if m: w4[m.group(2)].append((int(m.group(1)), float(m.group(3))))
    both = [(r, min(w4[r["mint8"]], key=lambda q: abs(q[0] - r["slot"]))) for r in ROWS if r["mint8"] in w4]
    near = [(r, q) for r, q in both if abs(q[0] - r["slot"]) < 4500]                       # within about 30 minutes
    print(f"== overlap with wallet 4: of TAB16RxX's {len(ROWS)} copyable buys, wallet 4 bought the same coin within 30 minutes on {len(near)} "
          f"({sum(1 for r, q in near if q[1] >= 1.3)} of them with 1.3+ SOL: the ones both bots would copy); wallet 4 first on {sum(1 for r, q in near if q[0] < r['slot'])}, the same slot {sum(1 for r, q in near if q[0] == r['slot'])}, TAB16RxX first on {sum(1 for r, q in near if q[0] > r['slot'])}")
