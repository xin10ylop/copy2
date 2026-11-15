# Step 2 (look before filtering). Every copyable buy on its own (no slot limit), the live rule, mean of the three
# landings: for each thing known when the bot sees its buy, the copies cut in about five groups by it,
# and for each group: copies, take profits, net a copy (SOL), and the group's net in blocks A / B / C. Also each
# feature's AUC for "reaches the take profit" (0.5 = no signal) and for "loses" . Categorical ones by value.
#   python3 -I explore.py > out/explore.txt
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import common as C
NUM = ["sol", "size_vs_recent", "progress", "mcap", "bps", "impact", "share", "hops", "nslot_before", "nslot_sell_before", "slot_buysol_before",
       "slot_users_before", "w4_big_10m", "w4_big_60m", "mins_since_last_big", "w4_tx_1500slots", "paper_last10_net", "paper_last10_tp",
       "w4_last10_ret", "age_s", "n_before", "tx_60s", "tx_300s", "fail_share", "hour", "dev_share", "slots_since_create", "creator_prev", "creator_prev_net"]
CAT = ["anchor", "how", "wday", "is_create"]
L = C.LAND
def stats(rs):
    net = sum(sum(r["res"][n][0] for n in L) for r in rs) / 3
    tp = sum(sum(1 for n in L if r["res"][n][1] == "tp") for r in rs) / 3
    ref = sum(sum(1 for n in L if r["res"][n][1] == "refused") for r in rs) / 3
    bl = [sum(sum(r["res"][n][0] for n in L) for r in rs if r["blk"] == b) / 3 for b in range(3)]
    return len(rs), tp, ref, net, bl
def auc(xs, ys):
    """P(x of a positive > x of a negative), ties half."""
    pos = sorted(x for x, y in zip(xs, ys) if y); neg = sorted(x for x, y in zip(xs, ys) if not y)
    if not pos or not neg: return float("nan")
    import bisect
    s = sum(bisect.bisect_left(neg, p) + 0.5 * (bisect.bisect_right(neg, p) - bisect.bisect_left(neg, p)) for p in pos)
    return s / len(pos) / len(neg)
if __name__ == "__main__":
    R = C.R
    n, tp, ref, net, bl = stats(R)
    print(f"all {n} copyable buys, each on its own: {tp:.1f} take profits, {ref:.1f} refused, net {net:+.2f} SOL ({net / n:+.4f} a copy), A/B/C {bl[0]:+.2f} {bl[1]:+.2f} {bl[2]:+.2f}")
    istp = [r["res"][4][1] == "tp" for r in R]; lose = [r["res"][4][0] < 0 and r["res"][4][1] != "refused" for r in R]
    print("\nAUC at landing 4: P(feature of a take-profit copy > feature of another copy); and the same for losing copies")
    for k in NUM:
        xs = [float(r["f"][k]) for r in R]; print(f"   {k:20s} TP {auc(xs, istp):.3f}   loser {auc(xs, lose):.3f}")
    print("\nquintiles: group | range | copies | take profits | refused | net a copy | group net A / B / C")
    for k in NUM:
        v = sorted(r["f"][k] for r in R); edges = sorted({v[int(len(v) * q) - 1] for q in (0.2, 0.4, 0.6, 0.8)} | {v[-1]})
        print(f"== {k}   (groups cut at the 20/40/60/80% values; equal values stay together)")
        lo = None
        for e in edges:
            g = [r for r in R if (lo is None or r["f"][k] > lo) and r["f"][k] <= e]; lo = e
            if not g: continue
            g.sort(key=lambda r: r["f"][k]); n, tp, ref, net, bl = stats(g)
            print(f"   {g[0]['f'][k]:>10.4g} .. {g[-1]['f'][k]:<10.4g} | {n:3d} | {tp:5.1f} ({100 * tp / n:4.1f}%) | {ref:4.1f} | {net / n:+.4f} | {bl[0]:+6.2f} {bl[1]:+6.2f} {bl[2]:+6.2f}")
    for k in CAT:
        print(f"== {k}")
        for v in sorted({r['f'][k] for r in R}, key=str):
            g = [r for r in R if r["f"][k] == v]; n, tp, ref, net, bl = stats(g)
            print(f"   {str(v):10s} | {n:3d} | {tp:5.1f} ({100 * tp / n:4.1f}%) | {ref:4.1f} | {net / n:+.4f} | {bl[0]:+6.2f} {bl[1]:+6.2f} {bl[2]:+6.2f}")
