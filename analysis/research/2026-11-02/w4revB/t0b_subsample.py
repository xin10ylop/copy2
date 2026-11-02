# Step 3 sample, cut for time: wallet 4's picks under 1.45 SOL are kept at a seeded 50% per period (weight = picks /
# kept); its 1.45+ SOL picks all (weight 1); the r2 and base sets as t0_sample.py drew them. Rewrites out/sample.json
# (the full draw is kept in out/sample_full.json) and out/coins_all.json (order: 1.45+ picks, kept small picks, r2, base).
#   python3 -I t0b_subsample.py [KEEP=0.5]
import sys, os, random, shutil, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib
KEEP = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
if not os.path.exists(blib.OUT + "/sample_full.json"): shutil.copy(blib.OUT + "/sample.json", blib.OUT + "/sample_full.json")
S = blib.jl(blib.OUT + "/sample_full.json"); TB = {t["mint"]: t for t in blib.jl(blib.OUT + "/table.json")}
rnd = random.Random(20261102 + 1)
out = {m: v for m, v in S.items() if v["set"] != "pick" or TB[m]["big"]}
for pp in ("P1", "P2"):
    small = sorted(m for m, v in S.items() if v["set"] == "pick" and not TB[m]["big"] and v["per"] == pp)
    k = rnd.sample(small, round(KEEP * len(small)))
    for m in k: out[m] = dict(S[m], w=len(small) / len(k))
    print(f"{pp}: small picks {len(small)}, kept {len(k)} (weight {len(small) / len(k):.3f})")
blib.jdump(out, blib.OUT + "/sample.json")
order = sorted(out, key=lambda m: ({"pick": 0, "r2": 1, "base": 2}[out[m]["set"]], -TB[m]["big"], TB[m]["cbt"]))
blib.jdump(order, blib.OUT + "/coins_all.json")
print("sample:", collections.Counter((v["set"], TB[m]["big"]) for m, v in out.items()))
