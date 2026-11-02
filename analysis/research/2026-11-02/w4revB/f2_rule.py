# Step 2b: does a simple create-time rule separate wallet 4's part-B launch picks? Fit on P1 (Oct 19-22) only, scored on
# P2 (Oct 23-26): precision (its picks among the coins the rule passes), recall (the share of its picks it passes).
# (a) shallow decision trees (as ../w4rev/s7_rule.py; w4_prior excluded), (b) hand rules read off f1_table.py's P1
# rates, (c) the quote alone (which quote tokens it follows) against the coin features within a quote.
#   python3 -I f2_rule.py [TARGET=pick] -> out/rules.json {name: [mints passing, all periods]}
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text
TARGET = sys.argv[1] if len(sys.argv) > 1 else "pick"
T = blib.jl(blib.OUT + "/table.json")
P1 = [t for t in T if t["per"] == "P1"]; P2 = [t for t in T if t["per"] == "P2"]
CAT = ["qsym", "host", "progs", "cfee"]
NUM = ["depth", "dev_sol", "dev_n", "dev_users", "dev_tok", "cre_is_user", "hour", "nlen", "slen", "s_upper", "s_eq_n", "nonascii",
       "digits", "nwords", "nsig", "cu", "fee", "cidx", "prior", "prior24", "gap", "prior_same_q", "q_heat1h", "q_share1h", "mayhem"]
top = {c: [v for v, _ in collections.Counter(t[c] for t in P1).most_common(25)] for c in CAT}
names = [f"{c}={str(v)[:40]}" for c in CAT for v in top[c]] + NUM
def X(rows):
    out = np.zeros((len(rows), len(names)))
    for i, t in enumerate(rows):
        j = 0
        for c in CAT:
            for v in top[c]: out[i, j] = float(t[c] == v); j += 1
        for c in NUM:
            v = t[c]; out[i, j] = -1 if v is None else float(v); j += 1
    return out
def score(rows, keep, y):
    tp = sum(1 for t, k in zip(rows, keep) if k and t[y]); n = int(sum(keep)); P = sum(t[y] for t in rows)
    return tp, n, P, (tp / n if n else 0), (tp / P if P else 0)
def show(name, f, y=TARGET):
    a = score(P1, [f(t) for t in P1], y); b = score(P2, [f(t) for t in P2], y)
    print(f"  {name:58s} P1 pass {a[1]:6d} picks {a[0]:4d}/{a[2]:4d} prec {a[3]:6.1%} rec {a[4]:6.1%} | P2 pass {b[1]:6d} picks {b[0]:4d}/{b[2]:4d} prec {b[3]:6.1%} rec {b[4]:6.1%}")
    return a, b
MANUAL = {"ata+cb+pump", "ata+pump", "ata+pump+sys", "ata+cb+pump+sys"}
RULES = {
    "R0 dev buy in the create tx": lambda t: t["dev_n"] >= 1,
    "R1 R0 + creator's first coin (prior 0)": lambda t: t["dev_n"] >= 1 and t["prior"] == 0,
    "R2 R1 + manual create tx (ata[+cb]+pump[+sys])": lambda t: t["dev_n"] >= 1 and t["prior"] == 0 and t["progs"] in MANUAL,
    "R3 R2 + dev buy 0.1-2 SOL": lambda t: t["dev_n"] >= 1 and t["prior"] == 0 and t["progs"] in MANUAL and 0.1 <= t["dev_sol"] < 2,
    "R4 R2 + dev buy 0.5-2 SOL": lambda t: t["dev_n"] >= 1 and t["prior"] == 0 and t["progs"] in MANUAL and 0.5 <= t["dev_sol"] < 2,
    "R5 R3 + cfee 150-250": lambda t: t["dev_n"] >= 1 and t["prior"] == 0 and t["progs"] in MANUAL and 0.1 <= t["dev_sol"] < 2 and 150 <= (t["cfee"] or 0) <= 250,
}
if __name__ == "__main__":
    print(f"target {TARGET}; P1 {len(P1)} creates, {sum(t[TARGET] for t in P1)} positive; P2 {len(P2)}, {sum(t[TARGET] for t in P2)} positive")
    print("\n(b) hand rules (read off f1_table.py's P1 rates):")
    keep = {}
    for k, f in RULES.items():
        show(k, f); keep[k] = [t["mint"] for t in T if f(t)]
    print("\n(a) decision trees fit on P1:")
    X1, X2 = X(P1), X(P2); y1 = np.array([t[TARGET] for t in P1])
    for depth, ml in ((2, 100), (3, 60), (4, 40), (5, 30)):
        tree = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=ml, random_state=0).fit(X1, y1)
        if depth == 3: print(export_text(tree, feature_names=names, show_weights=True, decimals=3))
        pr1 = tree.predict_proba(X1)[:, 1]; pr2 = tree.predict_proba(X2)[:, 1]
        for thr in (0.5, 0.3, 0.2, 0.1):
            a = score(P1, pr1 >= thr, TARGET); b = score(P2, pr2 >= thr, TARGET)
            print(f"  tree depth {depth} leaf>={ml}, leaves with P1 rate >= {thr:.0%}: P1 pass {a[1]:6d} picks {a[0]:4d} prec {a[3]:6.1%} rec {a[4]:6.1%}"
                  f" | P2 pass {b[1]:6d} picks {b[0]:4d} prec {b[3]:6.1%} rec {b[4]:6.1%}")
            if thr in (0.3, 0.2) and depth in (3, 4):
                keep[f"tree{depth}_{int(thr * 100)}"] = [t["mint"] for t, p in zip(P1, pr1) if p >= thr] + [t["mint"] for t, p in zip(P2, pr2) if p >= thr]
    # (c) the quote alone vs the coin within the quote
    print("\n(c) the quote alone: quotes it bought >= 5% of the launches of in P1 (with >= 10 picks), as a rule on P2")
    q1 = collections.defaultdict(lambda: [0, 0])
    for t in P1: q1[t["quote"]][0] += 1; q1[t["quote"]][1] += t[TARGET]
    QS = {q for q, (n, p) in q1.items() if p >= 10 and p / n >= 0.05}
    print("   quotes:", sorted(blib.jl(blib.OUT + '/table.json')[0] and {next(t['qsym'] for t in P1 if t['quote'] == q) for q in QS}))
    show("Q  quote in the P1 list", lambda t: t["quote"] in QS)
    show("Q+R3 quote in the P1 list and R3", lambda t: t["quote"] in QS and RULES["R3 R2 + dev buy 0.1-2 SOL"](t))
    print("\n   R3 within each main quote (P1 | P2):")
    for qs in ("CARDS", "PUMP", "TTWO", "XMR", "ZEC", "SPCX", "98sMhvDw", "Pren1F", "DJTu", "XsoCS1Tf", "Xsc9qvGR", "USDC"):
        sub1 = [t for t in P1 if t["qsym"] == qs]; sub2 = [t for t in P2 if t["qsym"] == qs]
        f = RULES["R3 R2 + dev buy 0.1-2 SOL"]
        a = score(sub1, [f(t) for t in sub1], TARGET); b = score(sub2, [f(t) for t in sub2], TARGET)
        base1 = sum(t[TARGET] for t in sub1) / max(1, len(sub1)); base2 = sum(t[TARGET] for t in sub2) / max(1, len(sub2))
        print(f"   {qs:9s} base {base1:5.1%} -> R3 prec {a[3]:5.1%} rec {a[4]:5.1%} (pass {a[1]:5d}) | base {base2:5.1%} -> R3 prec {b[3]:5.1%} rec {b[4]:5.1%} (pass {b[1]:5d})")
    blib.jdump(keep, blib.OUT + f"/rules_{TARGET}.json")
