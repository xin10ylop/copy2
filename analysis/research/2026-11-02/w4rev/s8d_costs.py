# Step 3f: the same results under copy2's usual cost model instead of this study's 0.003 SOL a round trip: 0.0095 SOL
# a transaction (two) plus the 0.0155 SOL a fill model bias (copy2 CLAUDE.md "Conventions"), i.e. 0.0315 SOL more a trade.
# Own half-and-half fill.   python3 -I s8d_costs.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
EXTRA = 2 * 0.0095 + 0.0155 - 0.003
T = {t["mint"]: t for t in lib.jl(lib.OUT + "/table.json")}
TF = {t["mint"]: t for t in lib.jl(lib.OUT + "/table_fresh.json")} if os.path.exists(lib.OUT + "/table_fresh.json") else {}
SETS = [("W", "sim_W", "rule_W", T), ("W1", "sim_W", "rule_W1", T), ("N", "sim_W", "rule_N", T), ("base", "sim_base", "rule_base", T),
        ("w4 picks", "sim_picks", None, T)]
if TF and os.path.exists(lib.OUT + "/sim_fresh.json"):
    SETS += [(n + " (P3)", "sim_fresh", f"rule_{n}F", TF) for n in ("W", "W1", "N", "base")]
print(f"extra cost {EXTRA:.4f} SOL a trade; totals (and without each period's best 2) at the study's costs -> at copy2's costs")
for cfg in ("ours|1.0", "its|1.0"):
    print(f"== {cfg}")
    for name, s, r, TT in SETS:
        sim = lib.jl(lib.OUT + f"/{s}.json")
        ms = [m for m in (lib.jl(lib.OUT + f"/{r}.json") if r else [m for m in sim if m in TT and TT[m]["pick"]]) if m in sim and "err" not in sim[m] and m in TT]
        out = []
        for per in sorted({TT[m]["per"] for m in ms}):
            L = sorted(sim[m][f"{cfg}|F{sim[m]['_F']}"]["pnl"] for m in ms if TT[m]["per"] == per and f"{cfg}|F{sim[m]['_F']}" in sim[m])
            L2 = sorted(v - EXTRA for v in L)
            out.append(f"{per} {len(L):4d}: {sum(L):+7.2f} ({sum(L[:-2]):+7.2f}) -> {sum(L2):+7.2f} ({sum(L2[:-2]):+7.2f})")
        print(f"  {name:10s} " + "   ".join(out))
