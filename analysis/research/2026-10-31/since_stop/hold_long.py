# Holding longer than 30 minutes: the coins' trades for 2 hours after wallet 4's buy (paths_long.py -> paths_2h.json.gz),
# timers 30 min to 2 h with take profit 2.4, 3 and 4 (no stop, holding through its sale). Two weeks (week 1 to Nov 5
# 08:49 Beirut, week 2 to Nov 12 08:49), 1 SOL, 2 open (a longer hold keeps a slot busy longer: copies are lost), raw
# model, mean of landings 4 / 8 / one block late. And for the copies still open at 30 minutes: how many later reach
# the take profit, and what the extra time adds or costs.
#   python3 -I hold_long.py SPD
import sys, os, io, contextlib, json, gzip
SPD = sys.argv[1]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import exit_search as E
E.G.P = json.load(gzip.open(f"{SPD}/paths_2h.json.gz"))
A = [r for r in E.A if f"{r['slot']}_{r['mint8']}" in E.G.P]; B = [r for r in E.B if f"{r['slot']}_{r['mint8']}" in E.G.P]
def run(rs, n, kw):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x > r["t"]]
        if len(open_) >= 2: continue
        o = E.model(r, n, **kw)
        if o is None: continue
        if o[1] != "refused": open_.append(r["t"] + o[2])
        out.append(o)
    v = sorted((o[0] for o in out), reverse=True)
    return sum(v), sum(v[2:]), sum(1 for o in out if o[1] != "refused")
print(f"coins with a 2-hour path: week 1 {len(A)} of {len(E.A)}, week 2 {len(B)} of {len(E.B)}")
print("tp   timer  | week 1 (w/o 2)  copies | week 2 (w/o 2)  copies | both")
for tp in (2.4, 3.0, 4.0):
    for h in (1790, 2400, 3000, 3600, 5400, 7200):
        kw = dict(tp=tp, sl=None, hold=h, follow=None, pmax=1.25, trail=None)
        w = [[run(W, n, kw) for n in E.LAND] for W in (A, B)]
        m = lambda x, i: sum(y[i] for y in x) / 3
        print(f"{tp:<4} {h:5d}s | {m(w[0],0):+6.2f} ({m(w[0],1):+6.2f}) {m(w[0],2):5.0f} | {m(w[1],0):+6.2f} ({m(w[1],1):+6.2f}) {m(w[1],2):5.0f} | {m(w[0],0)+m(w[1],0):+6.2f}"
              + ("   <- live" if (tp, h) == (2.4, 1790) else ""))
print("\nevery copy, landing 4, tp 2.4: the copies still open at 30 minutes, and the same copies held to 2 hours")
still = later_tp = 0; d = 0.0
for r in A + B:
    a = E.model(r, 4, tp=2.4, sl=None, hold=1790, follow=None, pmax=1.25, trail=None)
    b = E.model(r, 4, tp=2.4, sl=None, hold=7200, follow=None, pmax=1.25, trail=None)
    if not a or a[1] != "time": continue
    still += 1; later_tp += b[1] == "tp"; d += b[0] - a[0]
print(f"   {still} copies timed out at 30 min; held to 2 h, {later_tp} reached the take profit; the extra time: {d:+.2f} SOL in all")
