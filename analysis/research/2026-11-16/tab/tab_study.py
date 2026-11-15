# TAB16RxX, step 2: the same study as wallet 4's, on 25 days (Oct 21 - Nov 15) and every buy the bot could copy with the
# six floats (the scan at 0.5+ SOL), each with its 31-minute path (paths.py).
# Part 1, what to copy: every copy by the size of its buy and by what it was paid with, in each block, under a rule
#   that was not picked here (TAB16RxX's last live rule: tp 4.0, 600 s, its sale followed in its first 60 s).
# Part 2, the exit (for buys of MIN+ SOL): each part changed ALONE against a reference (that rule plus wallet 4's two
#   signals), the noise measured by drawing the days again, what its own sale means, the walk-forward.
# Part 3, does it add to wallet 4: the same without the coins wallet 4 bought with 1.3+ SOL within 30 minutes.
#   python3 -I tab_study.py PATHS SCAN W4SCAN [MIN=1.0] > out/tab_study.txt
import sys, os, re, json, gzip, datetime, collections, random
import numpy as np
PATHS, SCAN, W4SCAN = sys.argv[1:4]; MIN = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); import lib as L
TAB = "TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3"; L.W4 = TAB
OURS = {TAB, "Eao8T2Pk2aDzPWUFCA8si7oWd5ndFKfnX3HjYMpERst6"}
NAMES = {"So111111": "SOL", "3NZ9JMVB": "WBTC", "pumpCmXq": "PUMP", "SPCXxcqX": "SPCX", "TTWofwAg": "TTWO", "DJTu7vi8": "DJT", "98sMhvDw": "HYPE"}
CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1, "TTWO": 1, "DJT": 1, "HYPE": 1}
files = {}
for f in os.listdir(PATHS):
    slot, mint = f.split(".")[0].split("_"); files[f"{slot}_{mint[:8]}"] = f
rows, P = [], {}
for l in open(SCAN):
    m = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL from (\S+) quote (\S+) jupiter (\S+): ROUTABLE hops (\d+) how (\S+) .*?input: (\w{8})", l)
    if not m: continue
    key = f"{m.group(1)}_{m.group(2)}"
    if key not in files: continue
    if key not in P: P[key] = (files[key].split(".")[0].split("_")[1], json.load(gzip.open(f"{PATHS}/{files[key]}")))
    its = next((e for e in P[key][1] if e["user"] == TAB and e["buy"] and e["slot"] == int(m.group(1))), None)
    if its is None: continue
    rows.append(dict(slot=int(m.group(1)), mint8=m.group(2), t=its["t"], sol=float(m.group(3)), hops=int(m.group(7)), how=m.group(8), key=key, anchor=NAMES.get(m.group(9), m.group(9))))
rows.sort(key=lambda r: r["t"]); last, ALLROWS = {}, []
for r in rows:
    again = r["mint8"] in last and r["t"] - last[r["mint8"]] < 3600; last[r["mint8"]] = r["t"]
    if not again: ALLROWS.append(r)
PREP, EX = {}, {}
for r in list(ALLROWS):
    ps = [L.prep(r, P, n) for n in L.LAND]
    if any(p is None for p in ps): ALLROWS.remove(r); continue
    tr = P[r["key"]][1]; k = next(i for i, e in enumerate(tr) if e["user"] == TAB and e["buy"] and e["slot"] == r["slot"])
    for n, p in zip(L.LAND, ps):
        PREP[r["key"], n] = p; rest = tr[len(tr) - len(p["px"]):]; j = len(tr) - len(p["px"]) - 1
        other = np.array([e["user"] not in OURS for e in rest], dtype=bool); sell = np.array([not e["buy"] for e in rest], dtype=bool) & other
        EX[r["key"], n] = dict(sell=sell, buy=other & ~sell, pin=(tr[k]["vt"] / tr[j]["vt"]) ** 2)
w4 = collections.defaultdict(list)
for l in open(W4SCAN):
    m = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL", l)
    if m and float(m.group(3)) >= 1.3: w4[m.group(2)].append(int(m.group(1)))
for r in ALLROWS: r["w4"] = any(abs(s - r["slot"]) < 4500 for s in w4.get(r["mint8"], []))
TB = L.T_STOP; TC = datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp()
blk = lambda r: 0 if r["t"] < TB else 1 if r["t"] < TC else 2
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
def model(p, x, stake, rule):
    sigs, tp, hold, early = rule
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
def score(rule, rs):
    tot, b, wo5, days, whys, n_c = 0, [0, 0, 0], 0, collections.defaultdict(float), collections.Counter(), 0
    for n in L.LAND:
        out, open_ = [], []
        for r in rs:
            open_ = [y for y in open_ if y[0] > r["t"]]
            if len(open_) >= 2 or sum(1 for y in open_ if y[1] == r["anchor"]) >= CAPS[r["anchor"]]: continue
            net, why, held = model(PREP[r["key"], n], EX[r["key"], n], STAKE, rule)
            if why != "refused": open_.append((r["t"] + held, r["anchor"]))
            out.append((r, net, why))
        v = sorted((y[1] for y in out), reverse=True); tot += sum(v) / 3; wo5 += sum(v[5:]) / 3; n_c += len(out) / 3
        for r, net, why in out: b[blk(r)] += net / 3; days[day(r["t"])] += net / 3; whys[why] += 1 / 3
    alld = sorted({day(r["t"]) for r in ALLROWS})[1:-1]; dv = sorted(days.get(k, 0.0) for k in alld)
    return dict(tot=tot, b=b, wo5=wo5, neg=sum(1 for y in dv if y < 0), nd=len(dv), worst=dv[0], days=[days.get(k, 0.0) for k in alld], whys=whys, n=n_c)
PR, ST = ("press", 5, 60, 30), ("stall", 180)
LIVE2 = ((), 4.0, 600, (0, 60, 1e9)); REF = ((PR, ST), 4.0, 600, (0, 60, 1e9)); W4SET = ((PR, ST), 4.0, 600, (30, 290, 1.5))
if __name__ == "__main__":
    f = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d %H:%M")
    print(f"{len(ALLROWS)} copyable first buys of 0.5+ SOL with a path, {f(ALLROWS[0]['t'])} to {f(ALLROWS[-1]['t'])} UTC; blocks A / B / C: "
          + " / ".join(str(sum(1 for r in ALLROWS if blk(r) == i)) for i in range(3)) + f"; {STAKE} SOL a copy")
    # ---- part 1
    def every(rs, rule):
        v = [sum(model(PREP[r["key"], n], EX[r["key"], n], STAKE, rule)[0] for n in L.LAND) / 3 for r in rs]
        b = [sum(x for r, x in zip(rs, v) if blk(r) == i) for i in range(3)]; s = sorted(v, reverse=True)
        return f"{len(rs):4d} copies | {sum(v):+7.2f} SOL ({100 * sum(v) / max(1, len(v)) / STAKE:+6.1f}% a copy) | A {b[0]:+6.2f} B {b[1]:+6.2f} C {b[2]:+6.2f} | w/o best 2 {sum(s[2:]):+7.2f} | won {100 * sum(1 for x in v if x > 0) / max(1, len(v)):4.1f}%"
    for nm, rule in (("TAB16RxX's last live rule (tp 4.0, 600 s, its sale 0-60 s)", LIVE2), ("the same with wallet 4's two signals", REF)):
        print(f"== part 1, every copy (no slot limit), {nm}")
        print("   by the size of its buy:")
        for lo, hi in ((0.5, 0.75), (0.75, 1.0), (1.0, 1.3), (1.3, 1.6), (1.6, 2.0), (2.0, 3.0), (3.0, 99)):
            rs = [r for r in ALLROWS if lo <= r["sol"] < hi]
            if rs: print(f"      {lo:4.2f} to {hi:5.2f} SOL: " + every(rs, rule))
        print("   by what it paid with (buys of 1.0+ SOL):")
        for a in CAPS:
            rs = [r for r in ALLROWS if r["anchor"] == a and r["sol"] >= 1.0]
            if rs: print(f"      {a:5s} {dict(collections.Counter(r['hops'] for r in rs))} hops: " + every(rs, rule))
        print("   wallet 4 bought the coin too (1.3+ SOL, within 30 minutes), buys of 1.0+ SOL:")
        for nm2, sel in (("yes", True), ("no ", False)):
            rs = [r for r in ALLROWS if r["w4"] == sel and r["sol"] >= 1.0]; print(f"      {nm2}: " + every(rs, rule))
    # ---- part 2
    ROWS = [r for r in ALLROWS if r["sol"] >= MIN]
    B0 = score(REF, ROWS); random.seed(7); cache = {}
    def g(rule):
        if rule not in cache: cache[rule] = score(rule, ROWS)
        return cache[rule]
    def line(nm, rule, ref=None):
        ref = ref or B0; s = g(rule); d = [a - b for a, b in zip(s["days"], ref["days"])]; dr = sorted(sum(random.choice(d) for _ in d) for _ in range(2000))
        star = "*" if all(s["b"][i] > ref["b"][i] for i in range(3)) else " "
        return (f"   {nm:52s} | {s['tot']:+6.2f} | {s['tot'] - ref['tot']:+6.2f}{star} | {s['b'][0]:+6.2f} {s['b'][1]:+6.2f} {s['b'][2]:+6.2f} | {s['wo5']:+6.2f} | {s['neg']:2d}/{s['nd']} | {s['worst']:+5.2f} |"
                f" {sum(1 for y in dr if y > 0) / 20:5.1f}% [{dr[100]:+5.1f}, {dr[1900]:+5.1f}] | " + " ".join(f"{w} {c:.0f}" for w, c in s["whys"].most_common() if w != "refused"))
    hdr = f"   {'':52s} | total  | gain    | block A  B  C         | w/o b5 | neg   | worst | draws ahead [5%, 95%]  | exits (a landing)"
    print(f"\n== part 2, the exit, buys of {MIN}+ SOL: {len(ROWS)} buys, the bot's run (2 open, caps); gain = against the reference; * = ahead in all three blocks")
    print(hdr); print(line("REFERENCE: tp 4, 600 s, its sale 0-60 s, press, stall", REF))
    print(line("TAB16RxX's last live rule (no signals)", LIVE2)); print(line("WALLET 4'S FROZEN SETUP, untouched", W4SET))
    grp = collections.defaultdict(list)
    for r in ROWS:
        p, x = PREP[r["key"], 4], EX[r["key"], 4]
        if p["refused"]: continue
        j = L.first(p["sell"]); net, why, held = model(p, x, STAKE, ((PR, ST), 4.0, 600, None))
        if j is None or p["age"][j] > held: k = "it had not sold when we closed"
        else:
            a = p["age"][j]; px = p["px"][j]
            k = ("it sold in its first 30 s" if a < 30 else "it sold at 30-60 s" if a < 60 else "it sold at 60-290 s" if a < 290 else "it sold after 290 s") + (", under 1.5x" if px < 1.5 else ", at 1.5x or more")
        grp[k].append(net)
    print("== what its own sale means: its sale NEVER followed (press, stall, tp 4, 600 s), by what it did (every copy, landing 4)")
    for k, v in sorted(grp.items(), key=lambda q: -len(q[1])): print(f"   {k:44s}: {len(v):4d} copies, net {sum(v):+7.2f} SOL, {100 * sum(v) / len(v) / STAKE:+6.1f}% a copy, {100 * sum(1 for y in v if y > 0) / len(v):4.1f}% won")
    SETS = collections.OrderedDict()
    E = lambda e: ((PR, ST), 4.0, 600, e)
    SETS["its sale followed"] = [("never", E(None)), ("0-30 s", E((0, 30, 1e9))), ("0-120 s", E((0, 120, 1e9))), ("0-290 s", E((0, 290, 1e9))), ("any time", E((0, 600, 1e9))),
        ("0-60 s under 1.5x", E((0, 60, 1.5))), ("0-290 s under 1.5x", E((0, 290, 1.5))), ("30-290 s under 1.5x (wallet 4's)", E((30, 290, 1.5))), ("0-600 s under 1.0x", E((0, 600, 1.0))), ("60-600 s under 1.5x", E((60, 600, 1.5)))]
    SETS["take profit"] = [(f"tp {t}" if t else "no tp", ((PR, ST), t, 600, (0, 60, 1e9))) for t in (2.0, 2.5, 3.0, 3.5, 5.0, 6.0, None)]
    SETS["timer"] = [(f"{h} s", ((PR, ST), 4.0, h, (0, 60, 1e9))) for h in (180, 300, 450, 900, 1200, 1790)]
    SETS["the signals"] = [("neither", LIVE2), ("pressure only", ((PR,), 4.0, 600, (0, 60, 1e9))), ("stall only", ((ST,), 4.0, 600, (0, 60, 1e9))),
        ("pressure 3 in 60 s", ((("press", 3, 60, 30), ST), 4.0, 600, (0, 60, 1e9))), ("pressure 5 in 90 s", ((("press", 5, 90, 30), ST), 4.0, 600, (0, 60, 1e9))),
        ("pressure 8 in 120 s", ((("press", 8, 120, 30), ST), 4.0, 600, (0, 60, 1e9))), ("stall 120 s", ((PR, ("stall", 120)), 4.0, 600, (0, 60, 1e9))), ("stall 300 s", ((PR, ("stall", 300)), 4.0, 600, (0, 60, 1e9)))]
    for title, rs in SETS.items():
        print(f"== {title}: one change against the reference\n" + hdr)
        for nm, r in rs: print(line(nm, r))
    w = []
    for t, rs in SETS.items():
        for nm, r in rs:
            s = g(r); d = [a - b for a, b in zip(s["days"], B0["days"])]; dr = sorted(sum(random.choice(d) for _ in d) for _ in range(1000)); w.append((dr[950] - dr[50]) / 2)
    print(f"== the noise: half the [5%, 95%] band of a one-change gain, median over {len(w)} changes: {sorted(w)[len(w) // 2]:.2f} SOL")
    ALLR = [r for r in cache if r != REF]
    pa = max(ALLR, key=lambda r: cache[r]["b"][0]); pab = max(ALLR, key=lambda r: cache[r]["b"][0] + cache[r]["b"][1])
    print(f"== walk-forward over the {len(ALLR)} setups (gain over the reference): best on A ({cache[pa]['b'][0] - B0['b'][0]:+.2f}) -> on B {cache[pa]['b'][1] - B0['b'][1]:+.2f}, on C {cache[pa]['b'][2] - B0['b'][2]:+.2f}; "
          f"best on A+B ({cache[pab]['b'][0] + cache[pab]['b'][1] - B0['b'][0] - B0['b'][1]:+.2f}) -> on C {cache[pab]['b'][2] - B0['b'][2]:+.2f}")
    top = sorted(ALLR, key=lambda r: -(cache[r]["b"][0] + cache[r]["b"][1]))[:10]
    print(f"   the 10 best on A+B -> on C on average {sum(cache[r]['b'][2] - B0['b'][2] for r in top) / 10:+.2f}; ahead on C: {sum(1 for r in top if cache[r]['b'][2] > B0['b'][2])} of 10")
    # ---- part 3
    print(f"\n== part 3, what it adds to wallet 4: the bot's run on buys of {MIN}+ SOL without the coins wallet 4 bought too\n" + hdr)
    for nm, rule in (("the reference", REF), ("TAB16RxX's last live rule", LIVE2)):
        s = score(rule, [r for r in ROWS if not r["w4"]]); nd = s["nd"]
        print(f"   {nm:52s} | {s['tot']:+6.2f} | {'':7s} | {s['b'][0]:+6.2f} {s['b'][1]:+6.2f} {s['b'][2]:+6.2f} | {s['wo5']:+6.2f} | {s['neg']:2d}/{nd} | {s['worst']:+5.2f} | {s['n']:.0f} copies, {s['n'] / (nd + 1):.1f} a day, {s['tot'] / (nd + 1):+.2f} SOL a day")
