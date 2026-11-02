# Step 2b: does a simple create-time rule separate wallet 4's launch picks? Shallow decision trees fit on P1 (Oct 19-22)
# only, scored on P2 (Oct 23-26): precision (its picks among the coins the rule passes) and recall (the share of its
# picks the rule passes), for its picks of any size (pick) and its 1.45+ SOL picks (big).
# Features: create-tx only (feat.base) + the signer's earlier creates in the universe (feat.creator_hist); categorical
# ones one-hot on their 25 most common P1 values. w4_prior (the creator's earlier coins wallet 4 bought) is excluded.
#   python3 -I s7_rule.py [TARGET=pick] [DEPTH=3] [MINLEAF=40]
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text
TARGET = sys.argv[1] if len(sys.argv) > 1 else "pick"; DEPTH = int(sys.argv[2]) if len(sys.argv) > 2 else 3
MINLEAF = int(sys.argv[3]) if len(sys.argv) > 3 else 40
T = lib.jl(lib.OUT + "/table.json")
P1 = [t for t in T if t["per"] == "P1"]; P2 = [t for t in T if t["per"] == "P2"]
CAT = ["cls", "quote", "host", "progs", "cfee"]
NUM = ["depth", "dev_sol", "dev_n", "dev_tok", "cre_is_user", "hour", "nlen", "slen", "s_upper", "s_eq_n", "nonascii", "digits",
       "nwords", "nsig", "cu", "fee", "cidx", "prior", "prior24", "gap", "prior_same_q"]
if os.environ.get("PRIORACT"): NUM += ["pa_n", "pa_med", "pa_max", "pa_hot"]      # after s6c_prior_act.py
top = {c: [v for v, _ in collections.Counter(t[c] for t in P1).most_common(25)] for c in CAT}
names = [f"{c}={str(v)[:44]}" for c in CAT for v in top[c]] + NUM
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
    tp = sum(1 for t, k in zip(rows, keep) if k and t[y]); n = sum(keep); P = sum(t[y] for t in rows)
    return tp, n, P, (tp / n if n else 0), (tp / P if P else 0)
if __name__ == "__main__":
    X1, X2 = X(P1), X(P2); y1 = np.array([t[TARGET] for t in P1])
    tree = DecisionTreeClassifier(max_depth=DEPTH, min_samples_leaf=MINLEAF, random_state=0).fit(X1, y1)
    print(f"target {TARGET}, depth {DEPTH}, min leaf {MINLEAF}; P1 {len(P1)} coins, {int(y1.sum())} positive; P2 {len(P2)} coins, {sum(t[TARGET] for t in P2)} positive")
    print(export_text(tree, feature_names=names, show_weights=True, decimals=3))
    # leaves: P1 rate and P2 rate
    l1, l2 = tree.apply(X1), tree.apply(X2)
    print("leaf   P1 n   P1 pos  P1 rate |  P2 n  P2 pos  P2 rate")
    for leaf in sorted(set(l1)):
        a = [t for t, l in zip(P1, l1) if l == leaf]; b = [t for t, l in zip(P2, l2) if l == leaf]
        print(f"{leaf:4d} {len(a):6d} {sum(t[TARGET] for t in a):7d} {sum(t[TARGET] for t in a)/max(1,len(a)):8.1%} | {len(b):5d} {sum(t[TARGET] for t in b):6d} {sum(t[TARGET] for t in b)/max(1,len(b)):8.1%}")
    for thr in (0.5, 0.3, 0.2, 0.1):
        p1 = tree.predict_proba(X1)[:, 1] >= thr; p2 = tree.predict_proba(X2)[:, 1] >= thr
        a = score(P1, p1, TARGET); b = score(P2, p2, TARGET)
        print(f"rule = leaves with P1 rate >= {thr:.0%}: P1 passes {a[1]}, picks {a[0]} of {a[2]}: precision {a[3]:.1%}, recall {a[4]:.1%}"
              f"  |  P2 passes {b[1]}, picks {b[0]} of {b[2]}: precision {b[3]:.1%}, recall {b[4]:.1%}")
