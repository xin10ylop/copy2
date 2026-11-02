# Step 4b: the P3 coins to price (Oct 27 00:00 - Nov 1 23:00 UTC), only for what passed P2:
#  - "rot": every P3 R2 coin (out/fresh_table.json) of the rotation rule's quote sets (out/rot_sets.json: the quotes where
#    R2 was positive on P1, and those where it was positive on P2; float|ours and jup|ours), 98sMhvDw sampled at NMAX
#    (weight = its R2 coins / NMAX), the rest weight 1;
#  - "pick": wallet 4's part-B launch buys found in the seeded sample of its own transactions (w1_recent.py), weight =
#    its landed transactions that day / those sampled (its buys are sampled at that rate).
#   python3 -I u3_fresh_sample.py [NMAX=150] -> out/fresh_sample2.json {mint: {rot_w, pick_w, day, quote}}, out/coins_fresh2.json
import sys, os, random, collections, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib
from f2_rule import RULES
from u1_universe import sym
NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 150
R2 = RULES["R2 R1 + manual create tx (ata[+cb]+pump[+sys])"]
FT = {t["mint"]: t for t in blib.jl(blib.OUT + "/fresh_table.json")}
RS = blib.jl(blib.OUT + "/rot_sets.json")
Q = set()
for cfg in ("float|ours|1.0", "jup|ours|1.0"): Q |= set(RS[cfg]["A"]) | set(RS[cfg]["B"])
rnd = random.Random(20261105); S = {}
g = collections.defaultdict(list)
for t in FT.values():
    if R2(t) and t["quote"] in Q: g[t["quote"]].append(t)
for q, L in g.items():
    k = rnd.sample(L, min(NMAX, len(L)))
    for t in k: S[t["mint"]] = dict(rot_w=len(L) / len(k), pick_w=None, day=t["day"], quote=q)
W = blib.jl(blib.OUT + "/w4_recent.json")
for x in W:
    if not x["buy"] or x["cls"] != "E" or x["ds"] is None or x["ds"] > 1 or x["m"] not in FT: continue
    t = FT[x["m"]]
    S.setdefault(x["m"], dict(rot_w=None, pick_w=None, day=t["day"], quote=t["quote"]))
    S[x["m"]]["pick_w"] = x["scale"]; S[x["m"]]["w4sol"] = x["sol"]
blib.jdump(S, blib.OUT + "/fresh_sample2.json")
blib.jdump(sorted(S, key=lambda m: (S[m]["pick_w"] is None, FT[m]["cbt"])), blib.OUT + "/coins_fresh2.json")
print(f"rotation quotes {len(Q)}: {sorted(sym(q) for q in Q)}")
print(f"rot coins {sum(1 for v in S.values() if v['rot_w'])} ({[(sym(q), len(L)) for q, L in sorted(g.items(), key=lambda kv: -len(kv[1]))]}), "
      f"its sampled part-B launch buys {sum(1 for v in S.values() if v['pick_w'])}, total coins {len(S)}")
