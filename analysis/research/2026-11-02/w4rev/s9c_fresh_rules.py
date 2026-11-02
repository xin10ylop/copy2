# Step 4c: the rules of s7b_rules.py, unchanged, on the fresh table (Oct 28 00:00 - Nov 1 21:30 UTC): each rule's coins
# (out/rule_<name>F.json), a seeded 10% baseline (out/rule_baseF.json), their union for the tapes (out/coins_fresh.json),
# and precision / recall against wallet 4's launch buys when the table carries them.   python3 -I s9c_fresh_rules.py
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
from s7b_rules import RULES, pr
T = lib.jl(lib.OUT + "/table_fresh.json"); ms = set()
for name, f in RULES.items():
    k = [t["mint"] for t in T if f(t)]; lib.jdump(k, lib.OUT + f"/rule_{name}F.json"); ms |= set(k)
    a = pr(T, f, "pick"); b = pr(T, f, "big")
    print(f"{name:3s} passes {a[0]:5d} of {len(T)}; wallet 4 launch picks: {a[1]} of {a[2]} (precision {a[3]:.1%}, recall {a[4]:.1%}); 1.45+: {b[1]} of {b[2]} (precision {b[3]:.1%}, recall {b[4]:.1%})")
rnd = random.Random(1102); base = [t["mint"] for t in T if rnd.random() < 0.10]
lib.jdump(base, lib.OUT + "/rule_baseF.json"); ms |= set(base)
print(f"baseline {len(base)}; wallet 4 picks among them {sum(1 for t in T if t['mint'] in set(base) and t['pick'])}")
C = {t["mint"]: dict(csig=t["csig"], cslot=t["cslot"], cbt=t["cbt"], quote=t["quote"], vquote=t["vquote"], cls=t["cls"]) for t in T if t["mint"] in ms}
lib.jdump(C, lib.OUT + "/coins_fresh.json"); print(len(C), "coins for the tapes,", sum(1 for m in C if not os.path.exists(f"{lib.OUT}/tapes/{m}.json")), "new")
