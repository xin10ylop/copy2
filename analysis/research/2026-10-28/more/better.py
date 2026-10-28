# Copy better on part A (grid.py's machinery through sim.py; picked on P1, scored on P2; at most 4 open unless said):
#   base     the bot as built against grid.py's set (1.45+ SOL, no 3-hop routes) and grid.py's own (1.5+)
#   route    (i) WBTC routes only; a stake by route class (1.5 on WBTC routes, 0.5 on wSOL routes, ...)
#   stop     (iv) the stop by route class
#   premium  (vi) the entry limit, none to 5%
#   land     (vii) landing in its own slot (land 0) to 5 slots after
#   partial  (iii) partial exits: half at 1.5x and the rest at 2.0 / 2.5 / none; thirds at 1.5 / 2.0 / 2.5; a floor
#   python3 -I better.py base|route|stop|premium|land|partial [LO]
import sys, os, json, collections, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim
WHAT = sys.argv[1]
LO = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
SPX = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/more"
QS = {q["m"]: q for q in json.load(open(f"{SPX}/quotes.json"))}; RT = json.load(open(f"{SPX}/routes.json"))
def hops(m):
    q = QS.get(m); r = RT.get(q["sig"]) if q else None
    return len(r["hops"]) if r and r.get("hops") else 1
TR = [t for t in sim.trips(lo=LO) if hops(t[0]) <= 2] if os.environ.get("BOT") else sim.trips(lo=LO)
CL = {m: sim.cls(x) for m, x, p in TR}
print(f"{len(TR)} buys of {LO}+ SOL, routes ABC{', 2 hops at most (the bot as built)' if os.environ.get('BOT') else ''}; at most 4 open unless said")
sim.show("as built: tp 2.0 sl 0.8 1790 s, 1 SOL", sim.score(TR, cap=4)[0])
if WHAT == "base":
    for lo in (1.45, 1.5):
        for bot in (False, True):
            T2 = [t for t in sim.trips(lo=lo) if not bot or hops(t[0]) <= 2]
            for cap in (3, 4):
                sim.show(f"{lo}+ SOL, {'2 hops at most' if bot else 'any hops'}, {cap} open ({len(T2)} buys)", sim.score(T2, cap=cap)[0])
elif WHAT == "route":
    for routes in ("BC", "A", "B", "C"):
        sim.show(f"routes {routes} only", sim.score([t for t in TR if CL[t[0]] in routes], cap=4)[0])
    for wb, ws in ((1.5, 0.5), (1.5, 1.0), (2.0, 1.0), (1.0, 0.5), (2.0, 0.5), (1.5, 0.0)):
        kw = (lambda m, x, wb=wb, ws=ws: {"stake": wb} if CL[m] in "BC" else ({"stake": ws} if ws else {"skip": True}))
        for cap in (4, 99):
            sim.show(f"stake {wb} on WBTC routes, {ws} on wSOL, {cap} open", sim.score(TR, cap=cap, kw_of=kw)[0])
    for st in (1.5, 2.0):
        sim.show(f"stake {st} on every route, 4 open", sim.score(TR, cap=4, stake=st)[0])
    # the same SOL at work: the mean stake of the copies taken (capital ~ 4 x the mean stake)
    for wb, ws in ((1.0, 1.0), (1.5, 0.5), (1.5, 1.0), (2.0, 1.0), (1.5, 1.5), (2.0, 2.0)):
        _, got = sim.score(TR, cap=4, kw_of=lambda m, x, wb=wb, ws=ws: {"stake": wb if CL[m] in "BC" else ws})
        line = []
        for p in ("P1", "P2"):
            st = [wb if CL[m] in "BC" else ws for r, m in got[p]]; tot = sum(r for r, m in got[p])
            line.append(f"{p} {tot:+6.2f} on {sum(st):6.1f} SOL staked = {100 * tot / sum(st):+5.2f}% a staked SOL")
        print(f"   stake {wb} WBTC / {ws} wSOL: " + "   ".join(line))
    # what each class made per copy, and the SOL each needs
    _, got = sim.score(TR, cap=4)
    for p in ("P1", "P2"):
        g = collections.defaultdict(list)
        for r, m in got[p]: g["WBTC (B, C)" if CL[m] in "BC" else "wSOL (A)"].append(r)
        print(f"   {p} as built: " + "  ".join(f"{k} {len(v)} copies {sum(v):+.2f}, {sum(v) / len(v):+.3f} a copy" for k, v in g.items()))
elif WHAT == "stop":
    for sa, sb in itertools.product((0.75, 0.8, 0.85, 0.9), (0.75, 0.8, 0.85, 0.9)):
        sim.show(f"stop {sa} on wSOL routes, {sb} on WBTC routes", sim.score(TR, cap=4, kw_of=lambda m, x, sa=sa, sb=sb: {"sl": sa if CL[m] == "A" else sb})[0])
elif WHAT == "premium":
    for pm in (None, 1.0, 0.5, 0.35, 0.25, 0.15, 0.10, 0.05):
        sc, got = sim.score(TR, cap=4, pmax=pm)
        sim.show(f"entry at most {pm} over its price", sc)
    # the copies the 25% limit refuses: what they make when taken
    ref = [(m, x, p) for m, x, p in TR if sim.one(x, p, pmax=0.25) is None]
    res = [sim.one(x, p) for m, x, p in ref]
    print(f"   refused at 25%: {len(ref)} buys; taken anyway they make " +
          "  ".join(f"{P} {sum(1 for (m, x, p), r in zip(ref, res) if sim.per(x['tr'][0]['bt']) == P)} {sum(r[2] for (m, x, p), r in zip(ref, res) if sim.per(x['tr'][0]['bt']) == P):+.2f}" for P in ("P1", "P2")))
elif WHAT == "land":
    for land in (0, 1, 2, 3, 5):
        sim.show(f"landing {land} slot(s) after its slot", sim.score(TR, cap=4, land=land)[0])
elif WHAT == "partial":
    L = [("as built (all at 2.0)", dict()),
         ("half 1.5, half 2.0", dict(ladder=[(0.5, 1.5), (0.5, 2.0)])),
         ("half 1.5, half 2.25", dict(ladder=[(0.5, 1.5), (0.5, 2.25)])),
         ("half 1.5, half 2.5 (before its sell)", dict(ladder=[(0.5, 1.5), (0.5, 2.5)])),
         ("half 1.5, half no tp (stop / time / its sell)", dict(ladder=[(0.5, 1.5), (0.5, None)])),
         ("half 1.75, half 2.5", dict(ladder=[(0.5, 1.75), (0.5, 2.5)])),
         ("half 2.0, half 2.5", dict(ladder=[(0.5, 2.0), (0.5, 2.5)])),
         ("thirds 1.5 / 2.0 / 2.5", dict(ladder=[(1 / 3, 1.5), (1 / 3, 2.0), (1 / 3, 2.5)])),
         ("thirds 1.5 / 1.75 / 2.0", dict(ladder=[(1 / 3, 1.5), (1 / 3, 1.75), (1 / 3, 2.0)])),
         ("tp 2.0, floor 1.5 after 1.8", dict(floor=(1.8, 1.5))),
         ("tp 2.0, floor 1.3 after 1.6", dict(floor=(1.6, 1.3))),
         ("tp 2.0, floor 1.2 after 1.5", dict(floor=(1.5, 1.2))),
         ("tp 2.5, floor 1.5 after 1.8", dict(tp=2.5, floor=(1.8, 1.5))),
         ("tp 2.5, floor 1.8 after 2.0", dict(tp=2.5, floor=(2.0, 1.8))),
         ("tp 3.0, floor 1.8 after 2.0", dict(tp=3.0, floor=(2.0, 1.8))),
         ("no tp, floor 1.8 after 2.0", dict(tp=None, floor=(2.0, 1.8)))]
    for name, kw in L:
        sc, got = sim.score(TR, cap=4, **kw)
        won = "  ".join(f"won {sum(r > 0 for r, _ in got[p])}/{len(got[p])}" for p in ("P1", "P2"))
        sim.show(f"{name}", sc); print(f"   {'':46s} {won}")
