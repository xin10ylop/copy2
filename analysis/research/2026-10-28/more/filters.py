# Entry filters on part A (D ii), each bucket picked on P1 and scored on P2. Per copy: the rule as built (sim.one, no
# cap); per filter: the copies it keeps, at most 4 open. Features, all known when its buy is seen unless marked:
#   progress  the curve's progress after its buy: (1,073M - vt) / 793.1M tokens (pump's curve completes at vt 279.9M)
#   its_open  its own big buys (1.45+ SOL, any quote) still open at its buy (bought before, sold after)
#   hour      the hour block of its buy (UTC)
#   age       the coin's age at its buy in seconds (age.py: the curve's first signature; its big buys come in the first minute)
#   quote     the curve's quote token (_quote.json)
#   tier      its buy 1.45-1.5 / 1.5-1.6 / 1.6+ SOL (LO 1.45 to see the first)
#   before    trades on the curve between the coin's create and its buy (age.py; capped at 30,000)
#   frenzy    trades in its slot after it and the next 2 slots (NOT known when we buy at +1: a later-entry test below)
#   python3 -I filters.py [LO]
import sys, os, json, collections, datetime, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim
LO = float(sys.argv[1]) if len(sys.argv) > 1 else 1.5
SPX = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/more"
AGE = json.load(open(f"{SPX}/age.json"))
TR = sim.trips(lo=LO)
# its big buys (any coin) open at each moment
big = [(x["tr"][0]["bt"], x["tr"][-1]["bt"]) for x in sim.T.values() if x["tr"] and x["tr"][0]["buy"] and (x["tr"][0]["v"] or 0) >= 1.45 and len(x["tr"]) >= 2]
def its_open(t): return sum(1 for a, b in big if a < t < b)
def bucket(v, edges, labels):
    for e, l in zip(edges, labels):
        if v < e: return l
    return labels[-1]
F = {}
for m, x, path in TR:
    b = x["tr"][0]; vab = b["vt"]; bt = b["bt"]
    prog = (1_073_000_000e6 - vab) / 793_100_000e6
    a = AGE.get(m) or {}
    age = (bt - a["create_bt"]) if a.get("create_bt") else None
    fr = sum(1 for r in path if (r[0], r[1]) > (b["s"], b["i"] or 0) and r[0] <= b["s"] + 2)
    F[m] = {
        "progress": bucket(prog, (0.05, 0.1, 0.15, 0.2, 0.4), ("a <5%", "b 5-10%", "c 10-15%", "d 15-20%", "e 20-40%", "f 40%+")),
        "its_open": bucket(its_open(bt), (2, 4, 7), ("0-1", "2-3", "4-6", "7+")),
        "hour": f"{datetime.datetime.fromtimestamp(bt, datetime.timezone.utc).hour // 6 * 6:02d}-{datetime.datetime.fromtimestamp(bt, datetime.timezone.utc).hour // 6 * 6 + 6:02d}h",
        "age": "?" if age is None else bucket(age, (2, 5, 10, 20, 60), ("a <2 s", "b 2-5 s", "c 5-10 s", "d 10-20 s", "e 20-60 s", "f 60 s+")),
        "before": bucket(a.get("before_n", 0), (5, 10, 20, 40), ("a <5", "b 5-10", "c 10-20", "d 20-40", "e 40+")),
        "quote": sim.Q.get(m, "via SOL") if sim.Q.get(m) in ("WBTC", "PUMP", "CARDS", "TTWO") else ("via SOL" if not sim.Q.get(m) else "other"),
        "tier": bucket(b["v"], (1.5, 1.6), ("1.45-1.5", "1.5-1.6", "1.6+")),
        "route": "WBTC" if sim.cls(x) in "BC" else "wSOL",
        "frenzy (not known at +1)": bucket(fr, (1, 3, 6), ("0", "1-2", "3-5", "6+")),
    }
RES = {m: sim.one(x, p) for m, x, p in TR}
print(f"{len(TR)} buys of {LO}+ SOL (grid.py's set); per copy as built, no cap: P1 / P2 copies, net (without best 2), mean")
for f in next(iter(F.values())):
    print(f"  {f}:")
    g = collections.defaultdict(lambda: {"P1": [], "P2": []})
    for m, x, p in TR:
        r = RES[m]
        if r: g[F[m][f]][sim.per(x["tr"][0]["bt"])].append(r[2])
    for k in sorted(g):
        cells = []
        for P in ("P1", "P2"):
            v = sorted(g[k][P], reverse=True)
            cells.append(f"{P} {len(v):3d} {sum(v):+6.2f} ({sum(v[2:]):+6.2f}) {sum(v) / max(1, len(v)):+.3f}")
        print(f"     {k:12s} " + "   ".join(cells))
# filters: drop one bucket (or keep one) of a feature, picked on P1 at 4 open (without its best 2), shown on P2
base = sim.score(TR, cap=4)[0]
sim.show("as built, 4 open", base)
cand = []
for f in next(iter(F.values())):
    if f.startswith("frenzy"): continue
    vals = sorted({F[m][f] for m in F})
    for k in (1, 2):
        for drop in itertools.combinations(vals, k):
            if len(drop) >= len(vals): continue
            T2 = [t for t in TR if F[t[0]][f] not in drop]
            sc = sim.score(T2, cap=4)[0]
            cand.append((sc["P1"][2], f"{f} without {'+'.join(drop)}", sc))
cand.sort(key=lambda c: -c[0])
print(f"best 12 of {len(cand)} filters on P1 (4 open, without its best 2), and P2:")
for _, name, sc in cand[:12]: sim.show(name, sc, 52)
# the frenzy as a later entry: wait to see the 2 slots after its buy, buy at +3 only when at least K trades came
for kmin in (1, 3, 6):
    kw = lambda m, x, kmin=kmin: {"land": 3} if F[m]["frenzy (not known at +1)"] not in ("0", "1-2", "3-5", "6+")[:(0 if kmin <= 0 else 1 if kmin <= 1 else 2 if kmin <= 3 else 3)] else {"skip": True}
    sim.show(f"buy at +3 only after {kmin}+ trades in its slot..+2", sim.score(TR, cap=4, kw_of=kw)[0], 52)
sim.show("buy at +3, every copy", sim.score(TR, cap=4, land=3)[0], 52)
