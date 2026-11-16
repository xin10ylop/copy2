# The owner (Nov 16): "sell pressure thing, shouldn't we trigger it after his sell and earlier than 30 seconds?
# directly maybe?" The live rule counts from 30 s after its buy, whatever wallet 4 does. Variants, each one change to
# the live setup (tp 4.0, 600 s, its sale followed 30-290 s under 1.5x, sell_pressure [5, 60, 30], stall 180 s):
#   from F s        the pressure rule counted from 0 / 10 / 20 s instead of 30 (every copy)
#   after its sale  once wallet 4 has sold (any time, any price): the pressure rule with no 30 s floor, a lower count,
#                   or out at once
#   its first 30 s  its sale followed in its first 30 s too
#   python3 -I after_his_sale.py CQ ALL > out/after_his_sale.txt
import sys, os, random
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "signals")); sys.argv = sys.argv[:3]
import round3 as R3
from round3 import L, ROWS, PREP, EX, score
r3 = R3.trigger
def trigger(p, x, sig):
    kind = sig[0]
    if kind not in ("press", "stall2", "pafter"): return r3(p, x, sig)
    age = p["age"]; n = len(age)
    if n == 0: return None
    if kind == "stall2":
        px = p["px"] / x["pin"]; pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]])
        last = np.maximum.accumulate(np.where(newhi, age, -1e9)); return L.first((pk >= sig[1]) & (age - last >= sig[2]))
    lo = np.searchsorted(age, age - sig[2], side="left") if sig[2] else None
    s = np.concatenate([[0], np.cumsum(x["sell"])]); b = np.concatenate([[0], np.cumsum(x["buy"])])
    if kind == "press": return L.first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= sig[1]) & (age >= sig[3]))
    j = L.first(p["sell"])
    if j is None: return None
    after = np.arange(n) > j
    if sig[1] == 0: return L.first(after)
    return L.first(after & ((s[1:] - s[lo]) - (b[1:] - b[lo]) >= sig[1]))
R3.trigger = trigger
P0, S0, E0 = ("press", 5, 60, 30), ("stall2", 1.0, 180), (30, 290, 1.5)
def rule(P=P0, A=None, E=E0): return (tuple(s for s in (P, S0, A) if s), 4.0, 600, E)
B0 = score(rule()); random.seed(7)
def line(nm, r):
    s = score(r); d = [a - b for a, b in zip(s["days"], B0["days"])]; dr = sorted(sum(random.choice(d) for _ in d) for _ in range(2000))
    star = "*" if all(s["b"][i] > B0["b"][i] for i in range(3)) else " "
    return (f"   {nm:62s} | {s['tot']:+6.2f} | {s['tot'] - B0['tot']:+6.2f}{star} | {s['b'][0] - B0['b'][0]:+5.2f} {s['b'][1] - B0['b'][1]:+5.2f} {s['b'][2] - B0['b'][2]:+5.2f} | {s['wo5']:+6.2f} | {s['neg']}/{s['nd']} | {s['worst']:+5.2f} | {sum(1 for y in dr if y > 0) / 20:5.1f}% [{dr[100]:+5.1f}, {dr[1900]:+5.1f}]")
print(f"against the live setup {B0['tot']:+.2f} SOL ({len(ROWS)} buys, 0.5 SOL, the bot's run); * = ahead in all three blocks; the noise of one change is about +-3.4 SOL")
print(f"   {'':62s} | total  | gain    | by block A / B / C | w/o b5 | neg  | worst | draws ahead [5%, 95%]")
for F in (0, 10, 20): print(line(f"the pressure rule counted from {F} s after its buy (live: 30 s)", rule(P=("press", 5, 60, F))))
for nm, N, W in (("the live count (5 in 60 s), no 30 s floor", 5, 60), ("3 more sells than buys in 60 s", 3, 60), ("5 in 30 s", 5, 30), ("3 in 30 s", 3, 30), ("2 in 30 s", 2, 30), ("out at once (on the next trade)", 0, 0)):
    print(line(f"after its sale: {nm}", rule(A=("pafter", N, W))))
print(line("its sale followed in its first 30 s too (0-290 s under 1.5x)", rule(E=(0, 290, 1.5))))
print(line("its sale followed in its first 30 s at any price, and 30-290 s under 1.5x", rule(A=None, E=(0, 290, 1.5))))
