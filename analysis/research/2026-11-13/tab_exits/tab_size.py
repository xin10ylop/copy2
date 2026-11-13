# Does TAB16RxX's bet size say which copies win? Its copyable buys (tab_grid.py's set) by its SOL, our copy with the
# live rule of Nov 13 (tp 4.0, 600 s, its sale followed within 60 s), every copy (no open-slot limit), mean of
# landings 4 / 8 / one block late; by week. Then rules picked on week 1 and scored on week 2: copy only its 2.0+ SOL
# buys, or stake more on them.   (same arguments as tab_grid.py)
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tab_grid as G
LIVE = dict(tp=4.0, hold=600, fol=(0, 60, 1e9), sl=None)
band = lambda s: "1.0-1.45" if s < 1.45 else "1.45-1.6" if s < 1.6 else "1.6-1.95" if s < 1.95 else "1.95-2.05" if s < 2.05 else "2.05+"
print("its buys by size (SOL): " + str(sorted(collections.Counter(round(r["sol"], 2) for r in G.ROWS).items(), key=lambda x: -x[1])[:10]))
print(f"\nevery copy at {G.STAKE} SOL, mean of 3 landings: copies, raw net, per copy, won, take profits | week 1 | week 2")
for b in ("1.0-1.45", "1.45-1.6", "1.6-1.95", "1.95-2.05", "2.05+"):
    cells = []
    for wk in G.WK:
        rs = [r for r in wk if band(r["sol"]) == b]
        if not rs: cells.append("   -"); continue
        o = [[G.model(r, n, **LIVE) for r in rs] for n in G.LAND]
        tk = [[x for x in v if x[1] != "refused"] for v in o]
        c = sum(len(v) for v in tk) / 3; s = sum(sum(x[0] for x in v) for v in o) / 3
        won = sum(sum(1 for x in v if x[0] > 0) for v in tk) / 3; tp = sum(sum(1 for x in v if x[1] == "tp") for v in tk) / 3
        cells.append(f"{c:5.1f} {s:+7.3f} {100*s/max(c,1)/G.STAKE:+6.1f}% won {won:4.1f} tp {tp:3.1f}")
    print(f"   {b:9s} | " + " | ".join(cells))
def sim(rs, n, keep, mult):
    out, open_ = [], []
    for r in rs:
        if not keep(r): continue
        open_ = [x for x in open_ if x > r["t"]]
        if len(open_) >= 2: continue
        o = G.model(r, n, **LIVE)
        if o[1] != "refused": open_.append(r["t"] + o[2])
        out.append(o[0] * mult(r))
    v = sorted(out, reverse=True); return sum(v), sum(v[2:])
print("\nrules, 2 open, mean of 3 landings, raw (without the best 2) | week 1 | week 2")
for name, keep, mult in (("live: every 1.0+ buy, same stake", lambda r: True, lambda r: 1),
                         ("only its 1.95+ buys", lambda r: r["sol"] >= 1.95, lambda r: 1),
                         ("only its 1.45+ buys", lambda r: r["sol"] >= 1.45, lambda r: 1),
                         ("double stake on its 1.95+ buys", lambda r: True, lambda r: 2 if r["sol"] >= 1.95 else 1)):
    x = [[sim(wk, n, keep, mult) for n in G.LAND] for wk in G.WK]
    print(f"   {name:34s} | " + " | ".join(f"{sum(a for a, _ in w)/3:+.3f} ({sum(b for _, b in w)/3:+.3f})" for w in x))
