# Step 8. All the features at once: a ridge regression of each copy's net (every copy on its own, mean of the three
# landings) on the 25 numeric features of filters.py (standardised) plus the kind of copy, fitted on two blocks and used
# on the third (each way round): skip the third block's buys with the lowest predicted net (10 / 20 / 30% of them,
# cut values from the two fitting blocks), run as the bot runs, compared with no skip on that block. Also the same
# with the fee rule bps < 125 on in both arms (does the model add anything to it?).
#   python3 -I model_cv.py > out/model_cv.txt
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import common as C, filters as FI
KINDS = ("WBTC", "PUMP", "SPCX")
def X(rs):
    return np.array([[float(r["f"][k]) for k in FI.NUM] + [float(r["anchor"] == a) for a in KINDS] for r in rs])
y = np.array([sum(r["res"][n][0] for n in C.LAND) / 3 for r in C.R])
XA = X(C.R)
if __name__ == "__main__":
    for pre_name, pre in (("no other filter", lambda r, n: False), ("on top of bps < 125", lambda r, n: r["f"]["bps"] < 125)):
        print(f"== {pre_name}")
        base = C.measures(pre)
        for out in range(3):
            tr = np.array([r["blk"] != out for r in C.R]); mu = XA[tr].mean(0); sd = XA[tr].std(0) + 1e-12
            Z = (XA - mu) / sd; Z = np.hstack([Z, np.ones((len(Z), 1))])
            for lam in (10.0, 100.0):
                I = np.eye(Z.shape[1]); I[-1, -1] = 0
                w = np.linalg.solve(Z[tr].T @ Z[tr] + lam * I, Z[tr].T @ y[tr]); pred = Z @ w
                for q in (0.1, 0.2, 0.3):
                    cut = np.quantile(pred[tr], q); skipk = {r["key"] for r, p in zip(C.R, pred) if r["blk"] == out and p < cut}
                    m = C.measures(lambda r, n: pre(r, n) or r["key"] in skipk, base)
                    d = m["blocks"][out] - base["blocks"][out]
                    print(f"   fit on {'ABC'.replace('ABC'[out], '')}, used on {'ABC'[out]} | ridge {lam:5.0f} | skip lowest {int(q * 100)}% | skipped {len(skipk):3d} | "
                          f"block {'ABC'[out]} net {base['blocks'][out]:+6.2f} -> {m['blocks'][out]:+6.2f} ({d:+.2f}) | TP lost {m['tp_lost']:.1f}")
