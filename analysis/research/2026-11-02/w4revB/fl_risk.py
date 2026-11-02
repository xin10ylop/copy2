# The float's own price risk: what holding a fixed amount of each quote token would have done over Oct 19-27, from its
# SOL price in wallet 4's own swaps (out/tokp.json = h9long/ledger.py's source; smoothed by a 9-swap running median as in
# copy2 analysis/research/2026-10-28/more/floats.py): its change over P1 (Oct 19-22) and P2 (Oct 23-26), its worst
# fall (running peak to trough), and the SOL a 1 SOL float would have gained or lost. Quotes with fewer than 10 swaps
# are listed as unpriced.   python3 -I fl_risk.py [MINPICKS=5]
import sys, os, collections, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib, prices
from u1_universe import sym
MINP = int(sys.argv[1]) if len(sys.argv) > 1 else 5
T = blib.jl(blib.OUT + "/table.json"); TK = prices.load()
pk = collections.Counter(t["quote"] for t in T if t["pick"])
print(f"{'quote':10s} {'swaps':>5s} {'P1 change':>9s} {'P2 change':>9s} {'worst fall':>10s} {'(to)':>6s}  {'1 SOL float: P1':>15s} {'P2':>7s}   daily medians (SOL per token)")
for q, n in pk.most_common():
    if n < MINP: continue
    x = TK.get(q)
    if not x or len(x["ser"]) < 10:
        print(f"{sym(q):10s} {len(x['ser']) if x else 0:5d}  unpriced (fewer than 10 own swaps)"); continue
    ser = [(t, p) for t, p in x["ser"] if blib.T_LO <= t < blib.T_HI]
    if len(ser) < 10:
        print(f"{sym(q):10s} {len(ser):5d}  unpriced in the window"); continue
    sm = [sorted(p for _, p in ser[max(0, k - 4):k + 5])[len(ser[max(0, k - 4):k + 5]) // 2] for k in range(len(ser))]
    pk_, dd, ddt = sm[0], 0.0, None
    for (t, _), p in zip(ser, sm):
        pk_ = max(pk_, p)
        if p / pk_ - 1 < dd: dd, ddt = p / pk_ - 1, t
    ch = {}
    for P in ("P1", "P2"):
        v = [p for (t, _), p in zip(ser, sm) if blib.per(t) == P]
        ch[P] = (v[-1] / v[0] - 1) if len(v) >= 2 else None
    byd = collections.defaultdict(list)
    for t, p in ser: byd[time.strftime("%m-%d", time.gmtime(t))].append(p)
    med = " ".join(f"{d[3:]}:{sorted(v)[len(v) // 2]:.3g}" for d, v in sorted(byd.items()))
    f = lambda v: f"{v:+9.1%}" if v is not None else f"{'-':>9s}"
    g = lambda v: f"{v:+7.3f}" if v is not None else f"{'-':>7s}"
    print(f"{sym(q):10s} {len(ser):5d} {f(ch['P1'])} {f(ch['P2'])} {dd:+10.1%} {time.strftime('%m-%d', time.gmtime(ddt)) if ddt else '-':>6s}  {g(ch['P1']):>15s} {g(ch['P2'])}   {med}")
