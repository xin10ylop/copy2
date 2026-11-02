# Step 2f: launch-slot features on the seeded 10% baseline (out/rule_base.json, tapes of s4_paths.py): buys by wallets
# other than wallet 4 in the create slot after the create (count, SOL-equivalent size = quote x 30 / initial virtual
# quote) and in the next slot, against wallet 4's pick rate. (Wallet 4 lands in the create slot on 57% of its picks, so
# it cannot see most of these before it buys; a rule using them must fill in the next slot.)   python3 -I s6d_slot0.py
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
T = {t["mint"]: t for t in lib.jl(lib.OUT + "/table.json")}
B = [m for m in lib.jl(lib.OUT + "/rule_base.json") if os.path.exists(f"{lib.OUT}/tapes/{m}.json")]
rows = []
for m in B:
    t = T[m]; d = lib.jl(f"{lib.OUT}/tapes/{m}.json")
    s0 = s1 = 0; z0 = z1 = 0.0
    for sg, tr in d["tr"].items():
        if sg == t["csig"]: continue
        for x in tr:
            if not x[4] or x[3] == lib.W4: continue
            v = 30.0 * (x[5] or 0) / t["vquote"]
            if x[0] == t["cslot"]: s0 += 1; z0 += v
            elif x[0] == t["cslot"] + 1: s1 += 1; z1 += v
    rows.append((t, s0, z0, s1, z1))
def show(lab, key):
    c = collections.Counter(); p = collections.Counter()
    for r in rows: k = key(r); c[(r[0]["per"], k)] += 1; p[(r[0]["per"], k)] += r[0]["pick"]
    print(f"== {lab}")
    for k in sorted({k for _, k in c}, key=str):
        print(f"   {str(k):12s} " + "  ".join(f"{per}: {c[(per, k)]:4d} coins, picks {p[(per, k)]:3d} ({p[(per, k)]/max(1, c[(per, k)]):5.1%})" for per in ("P1", "P2")))
bk = lambda x, e: next((f"<{v}" for v in e if x < v), f">={e[-1]}")
print(f"{len(rows)} baseline coins with tapes; picks {sum(r[0]['pick'] for r in rows)}")
show("buys in the create slot after the create (not wallet 4)", lambda r: min(r[1], 4))
show("their size, SOL-equivalent", lambda r: bk(r[2], [0.01, 0.5, 1, 2, 4]))
show("buys in the next slot (not wallet 4)", lambda r: min(r[3], 4))
