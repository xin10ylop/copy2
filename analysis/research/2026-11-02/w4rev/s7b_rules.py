# Step 2d: the rules written out from s7_rule.py's P1 trees (depth 3, target pick), evaluated on P1 and P2, each
# rule's coins saved for the backtest (out/rule_<name>.json), and a seeded 10% baseline of every routable create.
#   W  = host meta.notrandom.fun, or (no other create by the signer in the 24 h before AND creator fee > 0 bps)
#   W1 = host meta.notrandom.fun and dev buy > 0.141 SOL-equivalent (the tree's high-precision leaves)
#   N  = host meta.notrandom.fun (W's first branch; see the note at RULES)
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
T = lib.jl(lib.OUT + "/table.json")
RULES = {
    "W": lambda t: t["host"] == "meta.notrandom.fun" or (t["prior24"] == 0 and (t["cfee"] or 0) > 0),
    "W1": lambda t: t["host"] == "meta.notrandom.fun" and t["dev_sol"] > 0.141,
    # N: W's first branch alone. Chosen after the backtest of W by part (s8b_split.py: P1 +12.88 on 191 here against
    # +2.37 on 879 for the other branch); that output showed P2 as well, so N is not a clean out-of-sample pick.
    "N": lambda t: t["host"] == "meta.notrandom.fun",
}
def pr(rows, f, y):
    k = [t for t in rows if f(t)]; tp = sum(t[y] for t in k); P = sum(t[y] for t in rows)
    return len(k), tp, P, tp / max(1, len(k)), tp / max(1, P)
if __name__ == "__main__":
    print(f"{'rule':5s} {'target':6s} | {'P1 pass':>7s} {'hits':>5s} {'of':>5s} {'prec':>6s} {'recall':>6s} | {'P2 pass':>7s} {'hits':>5s} {'of':>5s} {'prec':>6s} {'recall':>6s}")
    for name, f in RULES.items():
        for y in ("pick", "big"):
            a = pr([t for t in T if t["per"] == "P1"], f, y); b = pr([t for t in T if t["per"] == "P2"], f, y)
            print(f"{name:5s} {y:6s} | {a[0]:7d} {a[1]:5d} {a[2]:5d} {a[3]:6.1%} {a[4]:6.1%} | {b[0]:7d} {b[1]:5d} {b[2]:5d} {b[3]:6.1%} {b[4]:6.1%}")
        lib.jdump([t["mint"] for t in T if f(t)], lib.OUT + f"/rule_{name}.json")
    rnd = random.Random(1101); base = [t["mint"] for t in T if rnd.random() < 0.10]
    lib.jdump(base, lib.OUT + "/rule_base.json")
    bp = collections.Counter(t["per"] for t in T if t["mint"] in set(base))
    print(f"baseline: {len(base)} of {len(T)} routable creates ({dict(bp)}), picks among them {sum(1 for t in T if t['mint'] in set(base) and t['pick'])}")
