# The two live signals' own settings, all of them, on the live setup (the owner, Nov 15 night: "have you tried testing
# on different timings? or only in a minute, and also the other variables"). tp 4.0, 600 s, early 30-290 s under 1.5x;
# one thing changed at a time against sell_pressure [5, 60, 30] + stall 180 s, then the two together:
#   pressure   N more sells than buys (2-12) over W seconds (20-300), counted from F seconds after its buy (0-120)
#   solflow    the same in SOL: the others' sells minus buys over W seconds at X SOL or more (in place of the count)
#   stall      no new high for T seconds (60-400), armed once the price reached A times our buy (0 = at once, 1.0-1.5)
#   joint      the best few of each together, and the test: picked on two blocks, scored on the third
#   python3 -I grid.py CQ ALL > out/grid.txt
import sys, os, random, itertools
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:3]
import round3 as R3
from round3 import L, ROWS, score
r3_trigger = R3.trigger
def trigger(p, x, sig):
    kind = sig[0]
    if kind not in ("press", "solflow", "stall2"): return r3_trigger(p, x, sig)
    age = p["age"]; n = len(age)
    if n == 0: return None
    if kind == "stall2":                                     # (A, T): A = 0 arms at once
        px = p["px"] / x["pin"]; pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]])
        last = np.maximum.accumulate(np.where(newhi, age, -1e9)); return L.first((pk >= sig[1]) & (age - last >= sig[2]))
    N, W, F = sig[1], sig[2], sig[3]
    lo = np.searchsorted(age, age - W, side="left")
    if kind == "press":
        s = np.concatenate([[0], np.cumsum(x["sell"])]); b = np.concatenate([[0], np.cumsum(x["buy"])])
        return L.first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= N) & (age >= F))
    c = np.concatenate([[0], np.cumsum(x["sol"])]); return L.first(((c[1:] - c[lo]) <= -N) & (age >= F))
R3.trigger = trigger
E = (30, 290, 1.5)
rule = lambda pr, st, tp=4.0, hold=600: ((pr, st), tp, hold, E)
P0, S0 = ("press", 5, 60, 30), ("stall2", 1.0, 180)
B0 = score(rule(P0, S0))
chk = score(R3.BASE)
print(f"{len(ROWS)} buys; 0.5 SOL, 2 open; the live setup {B0['tot']:+.2f} (round 3's own: {chk['tot']:+.2f}); every figure below is the gain over it")
cache = {}
def g(r):
    if r not in cache: cache[r] = score(r)
    return cache[r]
gain = lambda r: g(r)["tot"] - B0["tot"]
allb = lambda r: all(g(r)["b"][i] > B0["b"][i] for i in range(3))
Ns, Ws = (2, 3, 4, 5, 6, 7, 8, 10, 12), (20, 30, 45, 60, 75, 90, 120, 150, 180, 240, 300)
print("== pressure: N more sells than buys (rows) over W seconds (columns), from 30 s; * = ahead in all three blocks")
print("        " + "".join(f"{w:>8d}s" for w in Ws))
for N in Ns: print(f"   N {N:2d}: " + "".join(f"{gain(rule(('press', N, w, 30), S0)):+8.2f}{'*' if allb(rule(('press', N, w, 30), S0)) else ' '}" for w in Ws))
print("== pressure: counted from F seconds after its buy (rows), N in W (columns)")
cols = ((5, 60), (4, 90), (5, 90), (6, 90), (6, 120), (8, 120), (8, 180))
print("         " + "".join(f"{f'{n} in {w}s':>12s}" for n, w in cols))
for F in (0, 10, 20, 30, 45, 60, 90, 120): print(f"   F {F:3d}: " + "".join(f"{gain(rule(('press', n, w, F), S0)):+11.2f}{'*' if allb(rule(('press', n, w, F), S0)) else ' '}" for n, w in cols))
print("== solflow in place of the count: the others' sells minus buys at X SOL (rows) over W seconds (columns), from 30 s")
Wf = (30, 60, 90, 120, 180, 240)
print("          " + "".join(f"{w:>8d}s" for w in Wf))
for X in (0.5, 1, 2, 3, 5, 8): print(f"   X {X:4g}: " + "".join(f"{gain(rule(('solflow', X, w, 30), S0)):+8.2f}{'*' if allb(rule(('solflow', X, w, 30), S0)) else ' '}" for w in Wf))
print("   no pressure rule at all (stall only): " + f"{gain((( S0,), 4.0, 600, E)):+.2f}")
print("== stall: no new high for T seconds (columns), armed at A times our buy (rows; 0 = at once)")
Ts = (60, 90, 120, 150, 180, 210, 240, 300, 400)
print("          " + "".join(f"{t:>8d}s" for t in Ts))
for A in (0, 0.8, 1.0, 1.1, 1.2, 1.3, 1.5): print(f"   A {A:4g}: " + "".join(f"{gain(rule(P0, ('stall2', A, t))):+8.2f}{'*' if allb(rule(P0, ('stall2', A, t))) else ' '}" for t in Ts))
print("   no stall rule at all (pressure only): " + f"{gain(((P0,), 4.0, 600, E)):+.2f}")
print("== joint: pressure x stall x take profit x timer (the whole grid below; the 15 best by total)")
J = [rule(('press', n, w, f), ('stall2', a, t), tp, h) for (n, w) in ((5, 60), (4, 90), (5, 90), (6, 90), (6, 120), (8, 120)) for f in (30, 60)
     for a in (1.0,) for t in (150, 180, 210, 240) for tp in (3.5, 4.0, 5.0) for h in (600, 900)]
lab = lambda r: f"{r[0][0][1]} in {r[0][0][2]} s from {r[0][0][3]} s; stall {r[0][1][2]} s; tp {r[1]}; timer {r[2]} s"
random.seed(7)
def line(r):
    s = g(r); d = [a - b for a, b in zip(s["days"], B0["days"])]; dr = [sum(random.choice(d) for _ in d) for _ in range(1000)]
    return f"   {lab(r):52s} | {s['tot']:+6.2f} | {s['tot'] - B0['tot']:+5.2f} | A {s['b'][0]:+6.2f} B {s['b'][1]:+6.2f} C {s['b'][2]:+6.2f} | w/o best 5 {s['wo5']:+6.2f} | losing days {s['neg']}/{s['nd']} | worst {s['worst']:+5.2f} | ahead in {100 * sum(1 for y in dr if y > 0) / 1000:5.1f}% of draws"
print(line(rule(P0, S0)) + "   <- live")
for r in sorted(J, key=lambda r: -g(r)["tot"])[:15]: print(line(r))
print(f"   of {len(J)} joint settings: {sum(1 for r in J if gain(r) > 0)} ahead of live, {sum(1 for r in J if allb(r))} in all three blocks; median gain {sorted(gain(r) for r in J)[len(J) // 2]:+.2f}")
print("== picked on two blocks out of every setting above, scored on the third (gain over live in the held-out block)")
ALLR = [r for r in cache if r != rule(P0, S0)]; tot = 0
for held in range(3):
    other = [i for i in range(3) if i != held]
    rk = sorted(ALLR, key=lambda r: -sum(cache[r]["b"][i] for i in other))
    gh = cache[rk[0]]["b"][held] - B0["b"][held]; tot += gh
    nm = lab(rk[0]) if rk[0][0][0][0] == "press" and len(rk[0][0]) == 2 else str(rk[0])
    print(f"   held out {'ABC'[held]}: picked '{nm}' ({sum(cache[rk[0]]['b'][i] - B0['b'][i] for i in other):+.2f} on the other two) -> {gh:+.2f}; the 10 best picks on average {sum(cache[r]['b'][held] - B0['b'][held] for r in rk[:10]) / 10:+.2f}")
print(f"   total out of sample: {tot:+.2f} SOL, out of {len(ALLR)} settings")
