# Step 2: each feature alone. Bins (quintiles, or the categories), and for each bin: copies, take profits, the net of
# every copy (mean of the three landings, no slot limit) in blocks A / B / C and all, and the net per copy. A bin is
# flagged "skip?" when it loses in all three blocks.
#   python3 -I scan1.py SKIPQ
import sys, json, math, collections
SKIPQ = sys.argv[1]; D = json.load(open(f"{SKIPQ}/features.json"))
for f in D:
    f["net"] = (f["net_4"] + f["net_8"] + f["net_slot+1"]) / 3; f["tp"] = f["why_4"] == "tp"
    f["px_in"] = f["px_in_4"]; f["log_age"] = math.log10(max(1, f.get("age_s") or 1))
    f["w4_gap"] = f["since_last"] if f["since_last"] is not None else 1e9
NUM = ["sol", "move", "sold", "vq_sol", "bps", "ahead_n", "ahead_sells", "same_slot_after", "w4_buys_10m", "w4_buys_60m", "w4_all_buys_10m", "w4_gap",
       "w4_last5", "w4_last5_won", "gap_any", "any_5m", "any_30m", "any_60m", "since_sell", "session_pos", "session_age", "holding", "w4_last3", "w4_last10", "prior_n", "age_s", "prior_60s", "prior_err", "px_in", "hour"]
CAT = ["anchor", "hops", "how"]
def row(label, rs):
    b = [sum(f["net"] for f in rs if f["blk"] == k) for k in range(3)]; n = len(rs)
    flag = "  <- skip?" if n >= 25 and all(x < 0 for x in b) else ""
    print(f"      {label:28s} {n:4d} copies, {sum(f['tp'] for f in rs):3d} tp ({100 * sum(f['tp'] for f in rs) / max(1, n):4.1f}%) | A {b[0]:+6.2f}  B {b[1]:+6.2f}  C {b[2]:+6.2f} | all {sum(b):+7.2f} | {100 * sum(b) / max(1, n) / 0.5:+6.1f}% a copy{flag}")
print(f"{len(D)} buys; all: "); row("all", D)
for c in CAT:
    print(f"\n== {c}")
    for v in sorted({f[c] for f in D}, key=str): row(str(v), [f for f in D if f[c] == v])
for c in NUM:
    vals = sorted(f[c] for f in D if f.get(c) is not None)
    if not vals: continue
    qs = sorted({vals[int(len(vals) * q / 5)] for q in range(1, 5)})
    edges = [-1e18] + qs + [1e18]
    print(f"\n== {c} (missing {sum(1 for f in D if f.get(c) is None)})")
    for lo, hi in zip(edges, edges[1:]):
        rs = [f for f in D if f.get(c) is not None and lo < f[c] <= hi] if lo > -1e18 else [f for f in D if f.get(c) is not None and f[c] <= hi]
        if rs: row(f"{'' if lo < -1e17 else f'{lo:.4g} < '}x{'' if hi > 1e17 else f' <= {hi:.4g}'}", rs)
