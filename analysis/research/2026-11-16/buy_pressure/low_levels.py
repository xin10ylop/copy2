# The same from 1.2x (the owner: "how didn't you start at 1.2x?"): the crossings of 1.2x, 1.3x, 1.5x and 1.75x by buy
# pressure, and a take profit there when buying has faded, added to the live setup. As buy_pressure.py.
#   python3 -I low_levels.py CQ ALL > out/low_levels.txt
import sys, os, random, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.argv = sys.argv[:3]
import buy_pressure as BP
from buy_pressure import L, ROWS, PREP, EX, score, netbuy, rule, B0
print(f"{len(ROWS)} buys. Part 1: the first crossing of a level within 600 s of its buy (landing 4), by the others' buys minus sells in the 60 s before")
for lvl, nxt in ((1.2, 1.5), (1.3, 2.0), (1.5, 2.0), (1.75, 3.0)):
    G = collections.defaultdict(list)
    for r in ROWS:
        p, x = PREP[r["key"], 4], EX[r["key"], 4]
        if p["refused"] or not len(p["px"]): continue
        ok = p["age"] <= 600; i = L.first((p["px"] >= lvl) & ok)
        if i is None: continue
        nb = netbuy(p, x, 60)[i]; rest = p["px"][i + 1:][ok[i + 1:]]
        if not len(rest): continue
        G["0 or less" if nb <= 0 else "1 to 5" if nb <= 5 else "6 to 15" if nb <= 15 else "16 or more"].append((rest.max() >= nxt, rest[-1] / lvl, rest.max() / lvl))
    print(f"== crossing {lvl}x ({sum(len(v) for v in G.values())} copies); next level {nxt}x")
    for k in ("0 or less", "1 to 5", "6 to 15", "16 or more"):
        v = G.get(k, [])
        if v: print(f"   buys minus sells {k:10s}: {len(v):4d} copies | reaches {nxt}x: {100 * sum(1 for y in v if y[0]) / len(v):5.1f}% | highest after, median {np.median([y[2] for y in v]):.2f}x of the level | at 600 s: median {np.median([y[1] for y in v]):.2f}x, mean {np.mean([y[1] for y in v]):.2f}x of the level")
random.seed(7)
def line(nm, r):
    s = score(r); d = [a - b for a, b in zip(s["days"], B0["days"])]; dr = sorted(sum(random.choice(d) for _ in d) for _ in range(2000))
    star = "*" if all(s["b"][i] > B0["b"][i] for i in range(3)) else " "
    return (f"   {nm:58s} | {s['tot']:+6.2f} | {s['tot'] - B0['tot']:+6.2f}{star} | {s['b'][0] - B0['b'][0]:+5.2f} {s['b'][1] - B0['b'][1]:+5.2f} {s['b'][2] - B0['b'][2]:+5.2f} | {s['wo5']:+6.2f} | {s['neg']}/{s['nd']} | {s['worst']:+5.2f} |"
            f" {sum(1 for y in dr if y > 0) / 20:5.1f}% [{dr[100]:+5.1f}, {dr[1900]:+5.1f}] | tp {s['whys'].get('tp', 0):.0f}, by it {s['whys'].get('early', 0):.0f}")
print(f"\nPart 2: a take profit at a low level when buying has faded, added to the live setup ({B0['tot']:+.2f}); * = ahead in all three blocks; noise about +-3.4 SOL")
print(f"   {'':58s} | total  | gain    | by block A / B / C | w/o b5 | neg  | worst | draws ahead [5%, 95%]  | exits")
for A in (1.2, 1.3, 1.5, 1.75):
    for W, M in ((60, 0), (60, -3), (60, -5), (30, 0), (120, 0), (120, -3)): print(line(f"out at {A}x if buys minus sells in {W} s is {M} or less", rule(("early", A, W, M))))
print("== for scale: a plain take profit at the level (no condition)")
for tp in (1.2, 1.3, 1.5, 1.75, 2.0): print(line(f"tp {tp}", rule(tp=tp)))
