# Which of the four candidate floats to take when the money allows only some: every subset, the bot's run (2 open, 1
# open from each float, WBTC 2, SOL 1; the live rule), blocks A | B | C | all (without each block's best 2), and with
# the SOL routes left out (the SOL they would use funds a float instead).
#   python3 -I subsets.py SPD
import sys, itertools
sys.path.insert(0, "."); sys.argv = sys.argv[:2]
import copy_all as CA
F, L = CA.F, CA.L
base = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
for sol in (True, False):
    print(f"\n{'with' if sol else 'WITHOUT'} the SOL routes:")
    for k in range(0, 5):
        for add in itertools.combinations(CA.NEW, k):
            keep = (set(base) | set(add)) - (set() if sol else {"SOL"}); rs = [r for r in F.rows if r["anchor"] in keep]
            caps = dict(base, **{x: 1 for x in add}); h = CA.blocks(rs, caps, 2)
            n = len(F.sim(rs, 4, CA.RULE, caps=caps, max_open=2))
            print(f"   + {' + '.join(CA.NAME[x] for x in add) or 'nothing':28s} | {CA.show(h)} | {n / CA.days:4.1f} a day | floats' SOL at 0.5 each: {0.5 * (4 + len(add)) if False else 0.5 * len(add):.1f} more")
