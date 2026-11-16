# Lowering the take profit to catch the coins that do not reach 3-4x (the owner, Nov 16: "also test for lowering tp,
# that was my point, maybe to catch some profits from coins that don't go to 3 or 4x"). As dynamic_tp.py (its model,
# its live baseline, the same checks and wallet 4's newest days):
#   weak    at T s (30 / 60), a copy that is not strong (by its price, net buying or trades, as dynamic_tp.py) gets a take
#           profit of 1.3 / 1.5 / 2.0 / 2.5x; a strong one keeps 4.0
#   decay   the take profit is 4.0 until T2 s (120 / 180 / 300) and then D (1.3 / 1.5 / 2.0 / 2.5x) for every copy
#   python3 -I lower_tp.py CQ ALL NEW > out/lower_tp.txt
import sys, os, itertools, collections, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dynamic_tp as D
from dynamic_tp import L, ROWS, NROWS, NPREP, NEX, score
base_model = D.model
def model(p, x, stake, rule):
    if not rule or rule[0] not in ("decay",): return base_model(p, x, stake, rule)
    # decay: as the live model with the take profit lowered after T2 (implemented through a class rule that is strong
    # for nobody, so that the weak take profit applies from T2)
    return base_model(p, x, stake, ("class", rule[1], "trades", 10 ** 9, (4.0, 600), rule[2]))
D.model = model
RULES = collections.OrderedDict()
for T, (met, lvls), tpw in itertools.product((30, 60), (("price", (1.2, 1.5)), ("netbuy", (10, 20)), ("trades", (50, 100))), (1.3, 1.5, 2.0, 2.5)):
    for lvl in lvls: RULES[f"at {T} s, {met} under {lvl:g}: tp {tpw:g} (strong keep 4)"] = ("class", T, met, lvl, (4.0, 600), tpw)
for T2, d in itertools.product((120, 180, 300), (1.3, 1.5, 2.0, 2.5)):
    RULES[f"decay: tp 4 until {T2} s, then {d:g}"] = ("decay", T2, d)
B0 = score(None); S = {nm: score(r) for nm, r in RULES.items()}; random.seed(7)
def line(nm, s, ref=B0):
    d = [a - c for a, c in zip(s["days"], ref["days"])]; dr = sorted(sum(random.choice(d) for _ in d) for _ in range(1000))
    star = "*" if all(s["b"][i] > ref["b"][i] for i in range(3)) else " "
    return f"   {nm:50s} | {s['tot']:+6.2f} | {s['tot'] - ref['tot']:+6.2f}{star} | {s['b'][0] - ref['b'][0]:+5.2f} {s['b'][1] - ref['b'][1]:+5.2f} {s['b'][2] - ref['b'][2]:+5.2f} | {s['wo5']:+6.2f} | {s['neg']} | {s['worst']:+5.2f} | {sum(1 for y in dr if y > 0) / 10:5.1f}%"
hdr = f"   {'':50s} | total  | gain    | by block A / B / C | w/o b5 | neg | worst | ahead in draws"
print(f"{len(ROWS)} buys, 0.5 SOL, the bot's run; the live setup {B0['tot']:+.2f} (this model; w/o best 5 {B0['wo5']:+.2f}, losing days {B0['neg']}, worst {B0['worst']:+.2f}); {len(RULES)} rules; * = ahead in all three blocks; noise about +-3.4")
print("== a lower take profit for the weak coins, by the level\n" + hdr)
for tpw in (1.3, 1.5, 2.0, 2.5):
    xs = [(nm, s) for nm, s in S.items() if nm.endswith(f": tp {tpw:g} (strong keep 4)")]
    b = max(xs, key=lambda q: q[1]["tot"]); w = min(xs, key=lambda q: q[1]["tot"])
    print(f"   tp {tpw:g} for the weak coins: {len(xs)} settings, gain from {w[1]['tot'] - B0['tot']:+.2f} to {b[1]['tot'] - B0['tot']:+.2f}; ahead {sum(1 for nm, s in xs if s['tot'] > B0['tot'])}, in all blocks {sum(1 for nm, s in xs if all(s['b'][i] > B0['b'][i] for i in range(3)))}")
    print(line(b[0], b[1]))
print("== the take profit lowered with time, for every copy\n" + hdr)
for nm, s in S.items():
    if nm.startswith("decay"): print(line(nm, s))
print("== the 10 best of all\n" + hdr)
for nm, s in sorted(S.items(), key=lambda q: -q[1]["tot"])[:10]: print(line(nm, s))
pab = max(S, key=lambda k: S[k]["b"][0] + S[k]["b"][1]); top = sorted(S, key=lambda k: -(S[k]["b"][0] + S[k]["b"][1]))[:10]
print(f"== walk-forward: best on A+B '{pab}' -> on C {S[pab]['b'][2] - B0['b'][2]:+.2f}; the 10 best on A+B -> on C {sum(S[k]['b'][2] - B0['b'][2] for k in top) / 10:+.2f}, ahead on C {sum(1 for k in top if S[k]['b'][2] > B0['b'][2])} of 10")
N0 = score(None, NROWS, NPREP, NEX)
print(f"== wallet 4's newest days (live setup {N0['tot']:+.2f}): best on A+B {score(RULES[pab], NROWS, NPREP, NEX)['tot'] - N0['tot']:+.2f}; the 5 best of all: " + ", ".join(f"{score(RULES[k], NROWS, NPREP, NEX)['tot'] - N0['tot']:+.2f}" for k in sorted(S, key=lambda k: -S[k]['tot'])[:5]))
