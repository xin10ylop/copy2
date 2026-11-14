# Wallet 4's copy with PUMP and SPCX held as floats, 0.5 SOL a copy, 2 open: what the new coins add, and the exits
# reviewed over everything the bot would then copy (SOL and WBTC routes, 3-hop ones, PUMP- and SPCX-paid coins).
# Since the stop (Oct 29 12:02 UTC) to the end of the data, split in two halves: rules picked on the first (mean of
# landings 4 / 8 / one block late, without its best 2), scored on the second. Raw model (lib.py), and "corrected" by
# its measured miss on our real trades per exit type (lib.CAL).
#   python3 -I float_exits.py SPD [STAKE]
import sys, os, itertools, datetime, collections
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib as L
SPD = sys.argv[1]; STAKE = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
# FE_T0 / FE_T1 (unix seconds): another window than "since the stop" (unseen_week.py)
T_A = float(os.environ.get("FE_T0", L.T_STOP)); T_B = float(os.environ.get("FE_T1", "inf"))
rows, P, info = L.load(SPD, T_A, T_B)
PREP = {}
for r in rows:
    for n in L.LAND:
        p = L.prep(r, P, n)
        if p is not None: PREP[r["key"], n] = p
rows = [r for r in rows if all((r["key"], n) in PREP for n in L.LAND)]
END = max(r["t"] for r in rows); MID = (T_A + END) / 2
HALF = lambda r: 0 if r["t"] < MID else 1
LIVE = dict(tp=2.4, hold=1790, early=(30, 180, 1.5), sl=None)
f = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d %H:%M")
def sim(rs, n, kw, stake=STAKE, max_open=2, caps=None, cal=False):
    """The bot's run: max_open at once, and at most caps[anchor] at once from one float. -> [(row, net, why)]"""
    out, open_ = [], []                                      # open_: (closes at, anchor)
    for r in rs:
        open_ = [x for x in open_ if x[0] > r["t"]]
        if len(open_) >= max_open: continue
        if caps and sum(1 for x in open_ if x[1] == r["anchor"]) >= caps.get(r["anchor"], max_open): continue
        net, why, held = L.model(PREP[r["key"], n], stake, **kw)
        if why != "refused": open_.append((r["t"] + held, r["anchor"]))
        out.append((r, net + (L.CAL[why] * stake if cal else 0), why))
    return out
def tot(res):
    v = sorted((x[1] for x in res), reverse=True); return sum(v), sum(v[2:])
def halves(rs, kw, **o):
    """mean over the landings of (net, net without the best 2) for each half."""
    r = []
    for h in (0, 1):
        x = [tot(sim([q for q in rs if HALF(q) == h], n, kw, **o)) for n in L.LAND]
        r.append((sum(a for a, _ in x) / 3, sum(b for _, b in x) / 3))
    return r
show = lambda h: f"{h[0][0]:+6.2f} ({h[0][1]:+6.2f}) | {h[1][0]:+6.2f} ({h[1][1]:+6.2f}) | {h[0][0] + h[1][0]:+6.2f} ({h[0][1] + h[1][1]:+6.2f})"
EARLY = {"never": None, "30-180<1.5 (live)": (30, 180, 1.5), "0-180<1.5": (0, 180, 1.5), "30-240<1.5": (30, 240, 1.5), "30-300<1.5": (30, 300, 1.5),
         "0-300<1.0": (0, 300, 1.0), "30-180 any": (30, 180, 1e9), "always": (0, 1e9, 1e9)}
GRID = [dict(tp=tp, hold=h, early=EARLY[e], sl=sl) for tp, h, e, sl in itertools.product((1.8, 2.0, 2.2, 2.4, 2.6, 3.0, 4.0), (300, 600, 900, 1200, 1790), EARLY, (None, 0.4, 0.5))]
en = lambda kw: next(k for k, v in EARLY.items() if v == kw["early"])
lab = lambda kw: f"tp {kw['tp']:<3} {kw['hold']:>4}s early {en(kw):18s} stop {str(kw['sl']):4s}"
CAPS = {"WBTC": 2, "PUMP": 1, "SPCX": 1}
def ev(kw): return kw, halves(rows, kw, caps=CAPS)
def ev_class(a):
    cls, kw = a; rs = [r for r in rows if r["anchor"] == cls]
    return cls, kw, halves(rs, kw, max_open=10**6)
if __name__ == "__main__":
    print(f"{info['rows']} copyable 1.45+ SOL buys since Oct 29 14:02 Beirut; {info['rebuy']} a coin bought again within the hour, {info['nopath']} without a path; "
          f"{len(rows)} used, to {f(END)} Beirut; halves split at {f(MID)}")
    print(f"stake {STAKE} SOL; SOL = mean over landings 4, 8 and one block late; (w/o best 2); first half | second half | both\n")
    print("== 1. every copy with the live rule (tp 2.4, 30 min, early-sale 30-180 s under 1.5x, no stop), by what we pay with")
    print(f"   {'pays with':9s} {'copies':>6s} {'a day':>5s} | first half       | second half      | both             | a copy | won | tp / timer / its sale / refused")
    days = (END - L.T_STOP) / 86400
    for cls in ("SOL", "WBTC", "PUMP", "SPCX", "all"):
        rs = [r for r in rows if cls == "all" or r["anchor"] == cls]
        h = halves(rs, LIVE, max_open=10**6); res = sim(rs, 4, LIVE, max_open=10**6); ex = collections.Counter(x[2] for x in res)
        n = len(res) - ex["refused"]
        print(f"   {cls:9s} {len(rs):6d} {len(rs) / days:5.1f} | {show(h)} | {100 * (h[0][0] + h[1][0]) / max(1, n) / STAKE:+5.1f}% | {100 * sum(1 for x in res if x[1] > 0) / max(1, len(res)):3.0f}% | "
              f"{ex['tp']} / {ex['time'] + ex['graduated']} / {ex['its_sell']} / {ex['refused']}")
    print("\n== 2. the bot's run, 2 open, live rule: what the floats add (raw, then corrected by the model's miss on our real trades)")
    sets = (("SOL + WBTC routes (live now)", ("SOL", "WBTC"), {"WBTC": 2}), ("+ PUMP float, 1 open from it", ("SOL", "WBTC", "PUMP"), {"WBTC": 2, "PUMP": 1}),
            ("+ PUMP and SPCX, 1 open from each", ("SOL", "WBTC", "PUMP", "SPCX"), CAPS), ("+ PUMP and SPCX, 2 from each", ("SOL", "WBTC", "PUMP", "SPCX"), {}),
            ("+ PUMP and SPCX, 1 each, WBTC 1", ("SOL", "WBTC", "PUMP", "SPCX"), {"WBTC": 1, "PUMP": 1, "SPCX": 1}))
    for name, cl, caps in sets:
        rs = [r for r in rows if r["anchor"] in cl]
        n = sum(len(sim(rs, k, LIVE, caps=caps)) for k in L.LAND) / 3
        print(f"   {name:34s} {n:5.0f} copies ({n / days:4.1f} a day) | raw {show(halves(rs, LIVE, caps=caps))}")
        print(f"   {'':34s} {'':24s} | cor {show(halves(rs, LIVE, caps=caps, cal=True))}")
    for mo in (3,):
        rs = rows; print(f"   {'all four, 1 each from PUMP/SPCX, ' + str(mo) + ' open':34s} {'':24s} | raw {show(halves(rs, LIVE, caps=CAPS, max_open=mo))}")
    print("\n== 3. the exits over all four (2 open, 1 from each new float), 840 rule sets: picked on the first half, scored on the second")
    with Pool(4) as p: R = p.map(ev, GRID)
    live = next(r for r in R if r[0] == LIVE)
    print(f"   {'rule':52s} | first half       | second half      | both"); print(f"   {lab(live[0])} | {show(live[1])}   <- live")
    R.sort(key=lambda r: -r[1][0][1]); print("   the 10 best on the first half (without its best 2):")
    for r in R[:10]: print(f"   {lab(r[0])} | {show(r[1])}")
    both = [r for r in R if r[1][0][1] > live[1][0][1] and r[1][1][1] > live[1][1][1] and r[1][0][0] > live[1][0][0] and r[1][1][0] > live[1][1][0]]
    print(f"   beat live in BOTH halves, with and without the best 2: {len(both)} of {len(R)}; the 10 best of them by both halves without the best 2:")
    for r in sorted(both, key=lambda r: -(r[1][0][1] + r[1][1][1]))[:10]: print(f"   {lab(r[0])} | {show(r[1])}")
    print("   each choice on its own: the mean over every rule set with it, first half / second half (without the best 2)")
    for key, vals, g in (("tp", (1.8, 2.0, 2.2, 2.4, 2.6, 3.0, 4.0), str), ("hold", (300, 600, 900, 1200, 1790), str),
                         ("early", list(EARLY.values()), lambda v: next(k for k, x in EARLY.items() if x == v)), ("sl", (None, 0.4, 0.5), str)):
        mean = lambda v, h: sum(r[1][h][1] for r in R if r[0][key] == v) / sum(1 for r in R if r[0][key] == v)
        print(f"   {key:5s}: " + "   ".join(f"{g(v)} {mean(v, 0):+.2f} / {mean(v, 1):+.2f}" for v in vals))
    print("\n== 4. does one kind of coin want other exits? every copy of that kind; the live rule, then single changes to it")
    alts = [("live", LIVE)] + [(f"tp {tp}", dict(LIVE, tp=tp)) for tp in (1.8, 2.0, 3.0, 4.0)] + [(f"{h} s", dict(LIVE, hold=h)) for h in (300, 600, 1200)] \
        + [("early never", dict(LIVE, early=None)), ("early 30-300<1.5", dict(LIVE, early=(30, 300, 1.5))), ("early always", dict(LIVE, early=(0, 1e9, 1e9))), ("stop 0.5", dict(LIVE, sl=0.5))]
    with Pool(4) as p: C = p.map(ev_class, [(c, kw) for c in ("SOL", "WBTC", "PUMP", "SPCX") for _, kw in alts])
    for c in ("SOL", "WBTC", "PUMP", "SPCX"):
        print(f"   {c}:")
        for (name, kw) in alts:
            h = next(x[2] for x in C if x[0] == c and x[1] == kw); print(f"      {name:18s} | {show(h)}")
