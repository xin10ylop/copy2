# Step 4d: the fresh period P3 (Oct 28 00:00 - Nov 1 21:30 UTC), scored like s8_score.py: each rule's coins (out/rule_<name>F.json),
# own half-and-half fill and forced F0 / F1, with the wallet-4-picked / skipped split when the table carries labels.
#   python3 -I s8c_fresh_score.py [RULE ...]   (default W W1 N base)
import sys, os, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
from s8_score import line
sim = lib.jl(lib.OUT + "/sim_fresh.json"); T = {t["mint"]: t for t in lib.jl(lib.OUT + "/table_fresh.json")}
labelled = any(t["pick"] for t in T.values())
for name in (sys.argv[1:] or ["W", "W1", "N", "base"]):
    ms = [m for m in lib.jl(lib.OUT + f"/rule_{name}F.json") if m in sim and "err" not in sim[m]]
    print(f"== {name} (P3, {len(ms)} coins)")
    print(f"{'config':18s} | {'n':>5s} {'total':>8s} {'median':>7s} {'wins':>5s} {'TP %':>6s} {'w/o b2':>8s}" + ("  | picked: n, total | skipped: n, total" if labelled else ""))
    for fill in ("mix", "F0", "F1"):
        for cfg in ("its|1.0", "ours|1.0", "its|0.1", "ours|0.1"):
            L = []
            for m in ms:
                r = sim[m]; F = r["_F"] if fill == "mix" else int(fill[1]); x = r.get(f"{cfg}|F{F}")
                if x: L.append((x["pnl"], x["kind"], m))
            extra = ""
            if labelled:
                a = [v for v, k, m in L if T[m]["pick"]]; b = [v for v, k, m in L if not T[m]["pick"]]
                extra = f"  | {len(a):4d} {sum(a):+7.2f} | {len(b):4d} {sum(b):+7.2f}"
            print(f"{cfg + ' ' + fill:18s} | {line(L)}{extra}")
