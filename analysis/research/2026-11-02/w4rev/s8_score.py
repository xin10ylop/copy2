# Step 3c: score a set of simulated launch buys (s5_sim.py output) by period: P1 Oct 19-22 (where a rule was picked),
# P2 Oct 23-26 (out of sample). Each coin's fill is its own half-and-half draw (F = hash(mint) % 2: after the create slot
# or after the next); "F0"/"F1" force one. Columns: trades, total SOL, median trade, wins, take-profit share, total
# without the period's best 2 trades.
#   python3 -I s8_score.py SIM_JSON TABLE_FILTER  (filter: all | pick | big | nonpick | rule:<name> (out/rule_<name>.json mints))
import sys, os, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib, feat
def rows_for(sim, mints, per_of, cfg, fill="mix"):
    out = {"P1": [], "P2": []}
    for m in mints:
        r = sim.get(m)
        if not r or "err" in r: continue
        F = r["_F"] if fill == "mix" else int(fill[1])
        x = r.get(f"{cfg}|F{F}")
        if not x: continue
        out[per_of[m]].append((x["pnl"], x["kind"], m))
    return out
def line(L):
    if not L: return "    0"
    p = sorted(v for v, k, m in L)
    tot = sum(p); wo = sum(p[:-2]) if len(p) > 2 else 0.0
    return (f"{len(L):5d} {tot:+8.2f} {statistics.median(p):+7.3f} {sum(1 for v in p if v > 0):5d} "
            f"{sum(1 for v, k, m in L if k == 'tp') / len(L):6.1%} {wo:+8.2f}")
def table(sim, mints, per_of, title, fills=("mix",)):
    print(f"== {title}")
    print(f"{'config':18s} | {'P1: n':>5s} {'total':>8s} {'median':>7s} {'wins':>5s} {'TP %':>6s} {'w/o b2':>8s} | {'P2: n':>5s} {'total':>8s} {'median':>7s} {'wins':>5s} {'TP %':>6s} {'w/o b2':>8s}")
    for fill in fills:
        for cfg in ("its|1.0", "ours|1.0", "its|0.1", "ours|0.1"):
            R = rows_for(sim, mints, per_of, cfg, fill)
            print(f"{cfg + ' ' + fill:18s} | {line(R['P1'])} | {line(R['P2'])}")
if __name__ == "__main__":
    sim = lib.jl(sys.argv[1]); flt = sys.argv[2] if len(sys.argv) > 2 else "all"
    T = {t["mint"]: t for t in lib.jl(lib.OUT + "/table.json")} if os.path.exists(lib.OUT + "/table.json") else {}
    if not T:                                   # before the table exists: wallet 4's picks only, labelled from picks.json
        for m, p in lib.jl(lib.OUT + "/picks.json").items():
            if p.get("cbt"): T[m] = dict(per=feat.per(p["cbt"]), pick=int(p["ds"] <= 1), big=int(p["ds"] <= 1 and p["v"] >= 1.45))
    per_of = {m: T[m]["per"] for m in sim if m in T}
    if flt == "all": ms = [m for m in sim if m in T]
    elif flt in ("pick", "big"): ms = [m for m in sim if m in T and T[m][flt]]
    elif flt == "nonpick": ms = [m for m in sim if m in T and not T[m]["pick"]]
    elif flt.startswith("rule:"):
        name, _, part = flt[5:].partition("&")
        ms = [m for m in lib.jl(lib.OUT + f"/rule_{name}.json") if m in sim and m in T]
        if part == "pick": ms = [m for m in ms if T[m]["pick"]]
        elif part == "skip": ms = [m for m in ms if not T[m]["pick"]]
        elif part == "big": ms = [m for m in ms if T[m]["big"]]
    table(sim, ms, per_of, f"{sys.argv[1]} [{flt}]", fills=("mix", "F0", "F1"))
