# What the winning copies have in common, and what sets them apart from the losers (the owner, Nov 16: "analyze all
# the winning coins, and see what they have different than the losers, what they have in common"). The 1,238 buys of
# ../signals/ (seven kinds, 1.3+ SOL, Oct 21 - Nov 15), each copied with the live setup (tp 4.0, 600 s, its sale 30-290 s
# under 1.5x, sell_pressure [5, 60, 30], stall 180 s), 0.5 SOL, every copy (no slot limit), mean of three landings.
# Two kinds of trait: what is known WHEN WE BUY (it could decide whether to copy), and what shows in the first 30 s
# after (it could only decide an exit; shown to see what a winner looks like early).
# A trait counts only if its groups rank the same way in all three blocks AND the gap between its best and worst
# group is still there when the days are drawn again. (../../2026-11-15/skip_filters/ searched 66,430 skip rules on 781
# buys under the old exit and kept none; new here: 457 more buys, the live exit, the creators, TAB16RxX's own buys.)
#   python3 -I winners.py CQ ALL TABSCAN W4SCAN > out/winners.txt
import sys, os, re, random, collections, datetime
import numpy as np
TABSCAN, W4SCAN = sys.argv[3], sys.argv[4]
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "buy_pressure")); sys.argv = sys.argv[:3]
import buy_pressure as BP
from buy_pressure import L, ROWS, PREP, EX, R3, rule
from round3 import blk, day, CRE
LIVE = rule(); sigs, tp, hold, E = LIVE; STAKE = 0.5
# ---- the outcome of every copy
for r in ROWS:
    res = [R3.model(PREP[r["key"], n], EX[r["key"], n], STAKE, sigs, tp, hold, E) for n in L.LAND]
    r["net"] = sum(x[0] for x in res) / 3; r["why"] = res[0][1]; r["refused"] = res[0][1] == "refused"
C = [r for r in ROWS if not r["refused"]]
grp = lambda r: "took profit at 4x" if r["why"] == "tp" else "other winner" if r["net"] > 0 else "small loss (to -20%)" if r["net"] > -0.1 else "big loss (over -20%)"
print(f"{len(ROWS)} buys, {len(C)} copied at landing 4 (the rest refused: its price already 25% up); {STAKE} SOL a copy")
print("== the four groups")
for g in ("took profit at 4x", "other winner", "small loss (to -20%)", "big loss (over -20%)"):
    v = [r for r in C if grp(r) == g]; print(f"   {g:22s}: {len(v):4d} copies ({100 * len(v) / len(C):4.1f}%), net {sum(r['net'] for r in v):+7.2f} SOL, {100 * np.mean([r['net'] for r in v]) / STAKE:+6.1f}% a copy")
win = sorted((r["net"] for r in C if r["net"] > 0), reverse=True); tot = sum(r["net"] for r in C)
print(f"   all {tot:+.2f} SOL; the best 5% of the copies ({len(C) // 20}) make {sum(sorted((r['net'] for r in C), reverse=True)[:len(C) // 20]):+.2f}; the best 10% {sum(sorted((r['net'] for r in C), reverse=True)[:len(C) // 10]):+.2f}")
# ---- traits known when we buy
tabs = collections.defaultdict(list)
for l in open(TABSCAN):
    m = re.match(r"(\d+) (\S{8}) ", l)
    if m: tabs[m.group(2)].append(int(m.group(1)))
w4all = collections.defaultdict(list)
for l in open(W4SCAN):
    m = re.match(r"(\d+) (\S{8}) ", l)
    if m: w4all[m.group(2)].append(int(m.group(1)))
cre_seen = collections.Counter(); hist = []                  # (closes at, net) of earlier copies, for its recent form
T = [r["t"] for r in ROWS]
for i, r in enumerate(ROWS):
    p, x = PREP[r["key"], 4], EX[r["key"], 4]
    dt = datetime.datetime.fromtimestamp(r["t"] + 7200, datetime.timezone.utc)
    r["f"] = f = collections.OrderedDict()
    f["its buy, SOL"] = r["sol"]
    f["paid with"] = r["anchor"] if r["anchor"] in ("SOL", "WBTC", "PUMP") else {"TTWofwAg": "TTWO", "DJTu7vi8": "DJT", "98sMhvDw": "HYPE"}.get(r["anchor"], r["anchor"])
    f["route"] = f"{r['hops']} hop" + ("s" if r["hops"] > 1 else "")
    f["fee tier, bps"] = int(p["ent"][2])
    f["the coin's size when we buy (its curve's quote reserve, SOL)"] = p["ent"][1] * p["rate"] / 1e9
    f["our price against its price"] = EX[r["key"], 4]["pin"]
    f["hour (Beirut)"] = f"{dt.hour // 4 * 4:02d}-{dt.hour // 4 * 4 + 4:02d}"
    f["weekday"] = "weekend" if dt.weekday() >= 5 else "weekday"
    f["its copyable buys in the 10 minutes before"] = sum(1 for t in T[:i] if r["t"] - t <= 600)
    f["its copyable buys in the hour before"] = sum(1 for t in T[:i] if r["t"] - t <= 3600)
    f["seconds since its last copyable buy"] = (r["t"] - T[i - 1]) if i else 99999
    done = [n for c, n in hist if c <= r["t"]][-5:]
    f["its last 5 copies that had closed: how many won"] = sum(1 for n in done if n > 0) if len(done) == 5 else None
    f["its last 5 copies that had closed: their net, SOL"] = sum(done) if len(done) == 5 else None
    c = CRE.get(r["key"]); f["earlier coins of the same creator it bought"] = min(cre_seen[c], 3) if c else None
    if c: cre_seen[c] += 1
    f["it had bought this coin before (over an hour ago)"] = "yes" if any(s < r["slot"] - 9000 for s in w4all.get(r["mint8"], [])) else "no"
    ts = tabs.get(r["mint8"], [])
    f["TAB16RxX and the coin"] = ("bought it earlier" if any(r["slot"] - 4500 < s < r["slot"] for s in ts) else "bought it in the same slot" if any(s == r["slot"] for s in ts)
                                  else "bought it within 30 min after" if any(r["slot"] < s < r["slot"] + 4500 for s in ts) else "did not buy it")
    # the first 30 s after its buy (not known when we buy)
    r["e"] = e = collections.OrderedDict(); a = p["age"]; m30 = a <= 30
    e["trades by others in the first 30 s"] = int(m30.sum())
    e["buys minus sells in the first 30 s"] = int(x["buy"][m30].sum() - x["sell"][m30].sum())
    e["price 30 s after its buy, against our price"] = (p["px"][m30][-1] / x["pin"]) if m30.any() else 1.0
    e["highest price in the first 30 s, against our price"] = (p["px"][m30].max() / x["pin"]) if m30.any() else 1.0
    j = L.first(p["sell"]); e["its own sale"] = "none in 600 s" if j is None or a[j] > 600 else "in its first 30 s" if a[j] < 30 else "30-290 s" if a[j] < 290 else "290-600 s"
    hist.append((r["t"] + 600, r["net"]))
random.seed(7)
def table(name, key, rows, src):
    vals = [(r[src][name], r) for r in rows if r[src][name] is not None]
    if not vals: return None
    if isinstance(vals[0][0], str): groups = collections.OrderedDict((k, [r for v, r in vals if v == k]) for k in sorted({v for v, _ in vals}))
    else:
        xs = sorted(v for v, _ in vals); qs = sorted({xs[len(xs) * k // 4] for k in (1, 2, 3)})
        edges = [-1e18] + qs + [1e18]; groups = collections.OrderedDict()
        for lo, hi in zip(edges, edges[1:]):
            g = [r for v, r in vals if lo < v <= hi] if lo > -1e18 else [r for v, r in vals if v <= hi]
            if g:
                a, b = min(r[src][name] for r in g), max(r[src][name] for r in g)
                groups[f"{a:.3g} to {b:.3g}" if a != b else f"{a:.3g}"] = g
    out = [f"-- {name}"]; stats = {}
    for k, g in groups.items():
        if len(g) < 15: continue
        pc = lambda v: 100 * np.mean([r["net"] for r in v]) / STAKE if v else float("nan")
        b = [pc([r for r in g if blk(r) == i]) for i in range(3)]; stats[k] = (pc(g), b, g)
        out.append(f"   {k:28s}: {len(g):4d} copies | took profit {100 * sum(1 for r in g if r['why'] == 'tp') / len(g):4.1f}% | won {100 * sum(1 for r in g if r['net'] > 0) / len(g):4.1f}% | {pc(g):+6.1f}% a copy | blocks A {b[0]:+6.1f}% B {b[1]:+6.1f}% C {b[2]:+6.1f}% | net {sum(r['net'] for r in g):+6.2f} SOL")
    if len(stats) < 2: return None
    best = max(stats, key=lambda k: stats[k][0]); worst = min(stats, key=lambda k: stats[k][0])
    same = all(stats[best][1][i] > stats[worst][1][i] for i in range(3))
    days = sorted({day(r["t"]) for r in rows}); byd = lambda g: collections.Counter()
    def gap(sample):
        s = set(sample); w = collections.Counter(sample)
        f = lambda g: (sum(r["net"] * w[day(r["t"])] for r in g if day(r["t"]) in s) / max(1e-9, sum(w[day(r["t"])] for r in g if day(r["t"]) in s)))
        return f(stats[best][2]) - f(stats[worst][2])
    dr = [gap([random.choice(days) for _ in days]) for _ in range(400)]
    share = 100 * sum(1 for y in dr if y > 0) / len(dr)
    out.append(f"   => best '{best}' {stats[best][0]:+.1f}% against worst '{worst}' {stats[worst][0]:+.1f}%: the same order in all three blocks: {'YES' if same else 'no'}; the gap stays in {share:.0f}% of redrawn days")
    return "\n".join(out), (stats[best][0] - stats[worst][0], same, share, name, best, worst)
for title, src in (("KNOWN WHEN WE BUY", "f"), ("THE FIRST 30 SECONDS AFTER ITS BUY (not known when we buy)", "e")):
    print(f"\n==== {title}: every trait in four equal groups (or its kinds); net in % of the stake a copy")
    summ = []
    for name in C[0][src]:
        t = table(name, None, C, src)
        if t: print(t[0]); summ.append(t[1])
    print(f"\n==== {title}: which traits hold (the same order in all three blocks and the gap in 90%+ of redrawn days)")
    for gapv, same, share, name, best, worst in sorted(summ, key=lambda q: -q[0]):
        print(f"   {'HOLDS ' if same and share >= 90 else 'no    '} {name:62s} gap {gapv:+6.1f} points | blocks agree: {'yes' if same else 'no '} | {share:3.0f}% of draws | best: {best}; worst: {worst}")
# ---- can it be used? the traits that hold, as rules, against the live setup in the bot's run (2 open, caps)
import round3 as R3m
ALLR = list(ROWS); B0 = R3m.score(LIVE); random.seed(7)
def line(nm, rows=None, r=LIVE):
    R3m.ROWS = rows if rows is not None else ALLR
    s = R3m.score(r); R3m.ROWS = ALLR
    d = [a - b for a, b in zip(s["days"], B0["days"])]; dr = sorted(sum(random.choice(d) for _ in d) for _ in range(2000))
    star = "*" if all(s["b"][i] > B0["b"][i] for i in range(3)) else " "
    return (f"   {nm:60s} | {s['tot']:+6.2f} | {s['tot'] - B0['tot']:+6.2f}{star} | {s['b'][0] - B0['b'][0]:+5.2f} {s['b'][1] - B0['b'][1]:+5.2f} {s['b'][2] - B0['b'][2]:+5.2f} | {s['wo5']:+6.2f} | {s['neg']}/{s['nd']} | {s['worst']:+5.2f} |"
            f" {sum(1 for y in dr if y > 0) / 20:5.1f}% [{dr[100]:+5.1f}, {dr[1900]:+5.1f}]")
hdr = f"   {'':60s} | total  | gain    | by block A / B / C | w/o b5 | neg  | worst | draws ahead [5%, 95%]"
SZ = "the coin's size when we buy (its curve's quote reserve, SOL)"; HR = "its copyable buys in the hour before"; LS = "seconds since its last copyable buy"
print(f"\n==== CAN IT BE USED? the bot's run; gain = against the live setup ({B0['tot']:+.2f}); * = ahead in all three blocks; the noise of one change is about +-3.4 SOL")
print("== at the buy: skip the weak group of a trait that holds\n" + hdr)
print(line("skip coins under 31.6 SOL of reserve (the smallest quarter)", [r for r in ALLR if r["f"][SZ] >= 31.6]))
print(line("skip coins under 39.8 SOL of reserve (the smaller half)", [r for r in ALLR if r["f"][SZ] >= 39.8]))
print(line("skip when it made 5+ copyable buys in the hour before", [r for r in ALLR if r["f"][HR] < 5]))
print(line("skip when its last copyable buy was under 6 minutes ago", [r for r in ALLR if r["f"][LS] >= 362]))
print(line("skip 2-hop routes", [r for r in ALLR if r["hops"] != 2]))
print(line("skip the coins paid with SOL", [r for r in ALLR if r["anchor"] != "SOL"]))
print(line("skip under 31.6 SOL of reserve and 5+ buys in the hour", [r for r in ALLR if r["f"][SZ] >= 31.6 and r["f"][HR] < 5]))
# a checkpoint: T seconds after its buy, out if the coin has not started
r3t = R3m.trigger
def trig(p, x, sig):
    if sig[0] not in ("chk_px", "chk_nb", "chk_tr"): return r3t(p, x, sig)
    age = p["age"]
    if not len(age): return None
    win = (age >= sig[1]) & (age < sig[1] + 30)
    if sig[0] == "chk_px": f = p["px"] / x["pin"] < sig[2]
    elif sig[0] == "chk_nb": f = (np.cumsum(x["buy"]) - np.cumsum(x["sell"])) <= sig[2]
    else: f = np.arange(1, len(age) + 1) <= sig[2]
    return L.first(win & f)
R3m.trigger = trig
P0, S0 = ("press", 5, 60, 30), ("stall2", 1.0, 180)
print("== after the buy: a checkpoint T seconds after its buy, out if the coin has not started\n" + hdr)
for T in (30, 45, 60):
    for x in (0.9, 0.98, 1.0, 1.1): print(line(f"at {T} s: out if the price is under {x}x ours", None, ((P0, S0, ("chk_px", T, x)), 4.0, 600, (30, 290, 1.5))))
    for m in (0, -3): print(line(f"at {T} s: out if buys minus sells since our buy is {m} or less", None, ((P0, S0, ("chk_nb", T, m)), 4.0, 600, (30, 290, 1.5))))
    print(line(f"at {T} s: out if 1 trade or none by others since our buy", None, ((P0, S0, ("chk_tr", T, 1)), 4.0, 600, (30, 290, 1.5))))
