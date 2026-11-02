# Step 3 sample: which part-B coins get a price path, and the weight each stands for.
#  - "pick": every wallet 4 launch pick (weight 1);
#  - "r2": coins that pass rule R2 (f2_rule.py: a dev buy in the create tx, the creator's first coin since Oct 19, a
#    manual create tx) and that it did not pick: a seeded random NR2 a period (weight = pool / NR2);
#  - "base": the other launches (not picked, not R2) of the active quotes (those with 5+ launch picks over Oct 19-26),
#    per (quote, period) max(MINQ, its share of NB), seeded (weight = pool / sampled).
# Together they estimate "every part-B launch of the active quotes"; picks + r2 estimate "every R2 coin".
#   python3 -I t0_sample.py [NR2=600] [NB=750] [MINQ=15] -> out/sample.json {mint: {set, w, per, quote}}, out/coins_<set>.json
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib
from f2_rule import RULES
NR2 = int(sys.argv[1]) if len(sys.argv) > 1 else 600; NB = int(sys.argv[2]) if len(sys.argv) > 2 else 750
MINQ = int(sys.argv[3]) if len(sys.argv) > 3 else 15
R2 = RULES["R2 R1 + manual create tx (ata[+cb]+pump[+sys])"]
T = blib.jl(blib.OUT + "/table.json")
pk = collections.Counter(t["quote"] for t in T if t["pick"])
ACTIVE = {q for q, n in pk.items() if n >= 5}
rnd = random.Random(20261102)
S = {}
for t in T:
    if t["pick"]: S[t["mint"]] = dict(set="pick", w=1.0, per=t["per"], quote=t["quote"])
for pp in ("P1", "P2"):
    pool = [t for t in T if t["per"] == pp and not t["pick"] and not t["late"] and R2(t)]
    s = rnd.sample(pool, min(NR2, len(pool)))
    for t in s: S[t["mint"]] = dict(set="r2", w=len(pool) / len(s), per=pp, quote=t["quote"])
    print(f"{pp}: R2 non-picks {len(pool)}, sampled {len(s)} (weight {len(pool) / len(s):.2f})")
    base = [t for t in T if t["per"] == pp and not t["pick"] and not t["late"] and not R2(t) and t["quote"] in ACTIVE]
    g = collections.defaultdict(list)
    for t in base: g[t["quote"]].append(t)
    nb = 0
    for q, L in sorted(g.items()):
        k = min(len(L), max(MINQ, round(NB * len(L) / len(base))))
        for t in rnd.sample(L, k): S[t["mint"]] = dict(set="base", w=len(L) / k, per=pp, quote=q)
        nb += k
    print(f"{pp}: base pool (active quotes, not picked, not R2) {len(base)} in {len(g)} quotes, sampled {nb}")
print(f"active quotes (5+ launch picks over Oct 19-26): {len(ACTIVE)}; their launches {sum(1 for t in T if t['quote'] in ACTIVE)} of {len(T)}")
print("sample:", collections.Counter(v["set"] for v in S.values()))
blib.jdump(S, blib.OUT + "/sample.json")
big = [m for m, v in S.items() if v["set"] == "pick" and next(t for t in T if t["mint"] == m)["big"]] if False else None
TB = {t["mint"]: t for t in T}
order = sorted(S, key=lambda m: ({"pick": 0, "r2": 1, "base": 2}[S[m]["set"]], -TB[m]["big"], TB[m]["cbt"]))
for name in ("pick", "r2", "base"):
    blib.jdump([m for m in order if S[m]["set"] == name], blib.OUT + f"/coins_{name}.json")
blib.jdump(order, blib.OUT + "/coins_all.json")
