# The owner's question (Nov 14): should each kind of copy (paid with SOL, WBTC, PUMP, SPCX) have its own exits?
# The honest test for overfitting: pick each kind's best rule on one half, score it on the OTHER half, both ways, and
# compare with the one rule for all (tp 3.0, 1200 s, early 30-290 s under 1.5x). 64 rules a kind: take profit 2.0 /
# 2.4 / 3.0 / 4.0 x timer 300 / 600 / 1200 / 1790 s x his sale followed never / 30-180 s / 30-290 s / always.
# 0.5 SOL, raw, mean of landings 4 / 8 / one block late. Picked on the net without the half's best 2.
#   python3 -I per_class.py SPD
import sys, os, itertools
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:2] + ["0.5"]; import float_exits as F
import lib as L
ONE = dict(tp=3.0, hold=1200, early=(30, 290, 1.5), sl=None)
EARLY = {"never": None, "30-180": (30, 180, 1.5), "30-290": (30, 290, 1.5), "always": (0, 1e9, 1e9)}
GRID = [dict(tp=tp, hold=h, early=EARLY[e], sl=None) for tp, h, e in itertools.product((2.0, 2.4, 3.0, 4.0), (300, 600, 1200, 1790), EARLY)]
lab = lambda kw: f"tp {kw['tp']} {kw['hold']:>4} s early {next(k for k, v in EARLY.items() if v == kw['early']):6s}"
K = ("SOL", "WBTC", "PUMP", "SPCX"); CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
def ev(a):
    c, i = a; rs = [r for r in F.rows if r["anchor"] == c]
    return c, i, F.halves(rs, GRID[i], max_open=10**6)       # [(net, w/o best 2) first half, (...) second half]
def sim_mixed(rs, n, rule, stake=0.5, max_open=2):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x[0] > r["t"]]
        if len(open_) >= max_open or sum(1 for x in open_ if x[1] == r["anchor"]) >= CAPS[r["anchor"]]: continue
        net, why, held = L.model(F.PREP[r["key"], n], stake, **rule[r["anchor"]])
        if why != "refused": open_.append((r["t"] + held, r["anchor"]))
        out.append(net)
    return out
def run(rule, h):
    x = []
    for n in L.LAND:
        v = sorted(sim_mixed([r for r in F.rows if F.HALF(r) == h], n, rule), reverse=True); x.append((sum(v), sum(v[2:])))
    return sum(a for a, _ in x) / 3, sum(b for _, b in x) / 3
if __name__ == "__main__":
    with Pool(4) as p: R = p.map(ev, [(c, i) for c in K for i in range(len(GRID))])
    S = {(c, i): h for c, i, h in R}; one_i = GRID.index(ONE); pick = {0: {}, 1: {}}
    print("each kind alone, every copy: net SOL (without the best 2)")
    print(f"   {'kind':5s} | the one rule: first half, second half | best on the FIRST half -> its SECOND half (against the one rule) | best on the SECOND half -> its FIRST half (against the one rule)")
    for c in K:
        o = S[c, one_i]; line = f"   {c:5s} | {o[0][0]:+6.2f} ({o[0][1]:+6.2f}), {o[1][0]:+6.2f} ({o[1][1]:+6.2f})   "
        for h in (0, 1):
            i = max(range(len(GRID)), key=lambda i: S[c, i][h][1]); pick[h][c] = GRID[i]; b = S[c, i][1 - h]; g = o[1 - h]
            line += f" | {lab(GRID[i])} -> {b[0]:+6.2f} ({b[1]:+6.2f}) vs {g[0]:+6.2f} ({g[1]:+6.2f}): {b[0] - g[0]:+5.2f} ({b[1] - g[1]:+5.2f})"
        print(line)
    print("\nthe bot's run (2 open; SOL 1, WBTC 2, PUMP 1, SPCX 1), each kind on its own picked rule, scored on the half it was NOT picked on:")
    one = {c: ONE for c in K}
    for h in (0, 1):
        a, b = run(pick[h], 1 - h), run(one, 1 - h)
        print(f"   picked on the {'first' if h == 0 else 'second'} half, scored on the {'second' if h == 0 else 'first'}: own rules {a[0]:+6.2f} ({a[1]:+6.2f}) | the one rule {b[0]:+6.2f} ({b[1]:+6.2f}) | difference {a[0] - b[0]:+5.2f} ({a[1] - b[1]:+5.2f})")
    print("\nhow stable is a kind's best rule? its rank (of 64, by the net without the best 2) on the other half:")
    for c in K:
        for h in (0, 1):
            i = GRID.index(pick[h][c]); order = sorted(range(len(GRID)), key=lambda j: -S[c, j][1 - h][1])
            print(f"   {c:5s} best on the {'first ' if h == 0 else 'second'} half ({lab(GRID[i])}): rank {order.index(i) + 1} on the other; the one rule ranks {sorted(range(len(GRID)), key=lambda j: -S[c, j][h][1]).index(one_i) + 1} and {order.index(one_i) + 1}")
    print("\none parameter at a time, each kind, both halves (net without the best 2; other settings as the one rule):")
    for key, vals in (("tp", (2.0, 2.4, 3.0, 4.0)), ("hold", (300, 600, 1200, 1790)), ("early", tuple(EARLY.values()))):
        for c in K:
            cells = []
            for v in vals:
                h = S[c, GRID.index(dict(ONE, **{key: v}))]; name = next(k for k, x in EARLY.items() if x == v) if key == "early" else str(v)
                cells.append(f"{name} {h[0][1]:+5.2f} / {h[1][1]:+5.2f}")
            print(f"   {key:5s} {c:5s}: " + "   ".join(cells))
