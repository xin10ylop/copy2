# Attention study, H7 step 4: does wallet 4 follow creators? Within the 48 h (to Nov 16 18:39 UTC): the creators (fee
# payer of the create) of its coins, how many of each creator's coins it bought, and how the creator's coins it did NOT
# buy ended. If it follows a list of creators, their other coins would be few and would graduate like its own; if it
# reads each coin, they would end like the market.
#   python3 -I a6_w4_creators.py SP > out/a6_w4_creators.txt
import sys, json, collections
SP = sys.argv[1]; W4M = json.load(open(f"{SP}/hunt/w4_mints.json")); W4LAST = 1794858000
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__))); import creates
C = [v for s, v in creates.load(SP).values()]; OUT = json.load(open(f"{SP}/attn/outcomes.json"))
L = [v for v in C if OUT.get(v["mint"]) and v["t"] < W4LAST - 3600]
for v in L: v["grad"] = OUT[v["mint"]][0]; v["w4"] = v["mint"] in W4M
by = collections.defaultdict(list)
for v in L: by[v["creator"]].append(v)
mine = {c for c, X in by.items() if any(v["w4"] for v in X)}
g = lambda X: sum(v["grad"] for v in X) / max(1, len(X))
Yc = [v for c in mine for v in by[c] if v["w4"]]; Nc = [v for c in mine for v in by[c] if not v["w4"]]
print(f"its {len(Yc)} coins come from {len(mine)} creators; those creators made {len(Yc) + len(Nc)} coins in the window")
print(f"graduated: the ones it bought {g(Yc):.2%} ({len(Yc)}) | the same creators' coins it did NOT buy {g(Nc):.2%} ({len(Nc)}) | all other creators {g([v for c in by if c not in mine for v in by[c]]):.2%}")
k = collections.Counter(sum(v["w4"] for v in by[c]) for c in mine); print("coins it bought per creator:", sorted(k.items()))
share = [sum(v["w4"] for v in by[c]) / len(by[c]) for c in mine]
print(f"share of a creator's coins it bought: median {sorted(share)[len(share) // 2]:.0%}; creators where it bought all: {sum(1 for s in share if s == 1)} of {len(mine)}")
# repeat creators: it bought 2+ coins of the creator; does it buy the creator's next coin, and in time order
rep = [c for c in mine if sum(v["w4"] for v in by[c]) >= 2]
print(f"creators it bought 2+ times: {len(rep)}, their coins {sum(len(by[c]) for c in rep)}, bought {sum(v['w4'] for c in rep for v in by[c])}")
# the creator's coins in time order: is its pick the first coin of the creator in the window, or later ones too
pos = collections.Counter()
for c in mine:
    X = sorted(by[c], key=lambda v: v["t"])
    for i, v in enumerate(X):
        if v["w4"]: pos["first" if i == 0 else ("2nd" if i == 1 else "3rd+")] += 1
print("its pick's place among the creator's coins in the window:", dict(pos))
# creators with many coins: does it pick the one that will graduate among them (skill) or buy at random
multi = [c for c in mine if len(by[c]) >= 5]
hit = [(sum(v["w4"] and v["grad"] for v in by[c]), sum(v["w4"] for v in by[c]), sum(v["grad"] for v in by[c]), len(by[c])) for c in multi]
a, b, cc, d = map(sum, zip(*hit)) if hit else (0, 0, 0, 0)
print(f"creators with 5+ coins: {len(multi)}; it bought {b} of their {d} coins; graduated among its buys {a}/{b} = {a / max(1, b):.1%}, among all their coins {cc}/{d} = {cc / max(1, d):.1%}")
