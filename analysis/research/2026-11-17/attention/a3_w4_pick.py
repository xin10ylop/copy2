# Attention study, H7: what separates the coins wallet 4 trades from the rest, on what is known at the create, and how
# its coins end. Wallet 4's first trade time of each coin from SP/hunt/w4_mints.json (its transactions to Nov 16 19:39
# UTC); the launches of SP/market/creates.json up to then.
#   python3 -I a3_w4_pick.py SP > out/a3_w4_pick.txt
import sys, json, collections
import numpy as np
SP = sys.argv[1]; W4M = json.load(open(f"{SP}/hunt/w4_mints.json")); W4LAST = 1794858000
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__))); import creates
C = {m: v for m, (s, v) in creates.load(SP).items()}; OUT = json.load(open(f"{SP}/attn/outcomes.json"))
L = sorted((v for m, v in C.items() if OUT.get(m) and v["t"] < W4LAST - 3600), key=lambda v: v["t"])
SOL = "11111111111111111111111111111111"
by_c = collections.defaultdict(list)
for v in L: by_c[v["creator"]].append(v)
for v in L:
    v["grad"] = OUT[v["mint"]][0]; v["w4"] = v["mint"] in W4M; v["lag"] = W4M.get(v["mint"], 0) - v["t"]
    prev = [w for w in by_c[v["creator"]] if w["t"] < v["t"]]; v["n24"] = sum(1 for w in prev if w["t"] > v["t"] - 86400)
    known = [w for w in prev if w["t"] <= v["t"] - 7200]; v["kn"] = len(known); v["kg"] = sum(w["grad"] for w in known)
Y = [v for v in L if v["w4"]]; N = [v for v in L if not v["w4"]]
r = lambda X: sum(v["grad"] for v in X) / max(1, len(X))
print(f"{len(L)} launches to Nov 16 18:39 UTC; wallet 4 traded {len(Y)} ({len(Y) / len(L):.1%})")
print(f"graduated: its coins {r(Y):.2%} ({sum(v['grad'] for v in Y)}) | the rest {r(N):.2%}")
lags = np.array([v["lag"] for v in Y]); print(f"its first trade after the create: median {np.median(lags):.0f} s; within 2 s {np.mean(lags <= 2):.0%}, within 60 s {np.mean(lags <= 60):.0%}, after 1 h {np.mean(lags > 3600):.0%}")
def share(name, key):
    cy = collections.Counter(key(v) for v in Y); cn = collections.Counter(key(v) for v in N)
    print(f"\n{name}: share of its coins | share of the rest | graduated among its coins | among the rest")
    for k in sorted(set(cy) | set(cn), key=str):
        yk = [v for v in Y if key(v) == k]; nk = [v for v in N if key(v) == k]
        print(f"   {str(k):24s} {cy[k] / len(Y):6.1%} | {cn[k] / len(N):6.1%} | {r(yk):6.2%} ({len(yk)}) | {r(nk):6.2%} ({len(nk)})")
QN = collections.Counter(v["quote"] for v in L)
share("quote", lambda v: "SOL" if v["quote"] == SOL else (v["quote"][:8] if QN[v["quote"]] >= 500 else "other token (small)"))
share("creator's launches in 24 h before", lambda v: "0 (first)" if v["n24"] == 0 else ("1-4" if v["n24"] <= 4 else ("5-19" if v["n24"] <= 19 else "20+")))
share("creator's record (2 h+)", lambda v: "none earlier" if v["kn"] == 0 else ("0 graduated" if v["kg"] == 0 else "1+ graduated"))
share("when it first traded", lambda v: "-" if not v["w4"] else ("<= 2 s" if v["lag"] <= 2 else ("<= 60 s" if v["lag"] <= 60 else ("<= 1 h" if v["lag"] <= 3600 else "> 1 h"))))
