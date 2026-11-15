# Step 3: a wide search for skip rules, with the guard against finding one by luck. Conditions: every numeric
# feature at its deciles, both ways ("x <= q", "x > q"), and what we pay with and the hops; rules = one condition or
# two together (AND). A rule is VALID when the copies it skips (40-400 of 781) lose money in each of the three blocks
# and it loses at most MAXTP take profits (of 80). Its gain = minus the net of what it skips (mean of the three
# landings, 0.5 SOL, every copy). The guard: the same search after shuffling the copies' results among the rows
# inside each block (so no feature can know anything), 300 times: how big is the best "valid" gain found by luck?
# Then picked-on-two, scored-on-the-third: the best rule on each pair of blocks and what it does on the block left out.
#   [EXCL=bps] python3 -I rules.py SKIPQ [MAXTP]
import sys, os, json, math
import numpy as np
SKIPQ = sys.argv[1]; MAXTP = int(sys.argv[2]) if len(sys.argv) > 2 else 4
D = json.load(open(f"{SKIPQ}/features.json")); n = len(D); rng = np.random.default_rng(7)
net = np.array([(f["net_4"] + f["net_8"] + f["net_slot+1"]) / 3 for f in D]); tp = np.array([f["why_4"] == "tp" for f in D], float)
blk = np.array([f["blk"] for f in D])
NUM = ["sol", "move", "sold", "vq_sol", "bps", "ahead_n", "same_slot_after", "w4_buys_10m", "w4_buys_60m", "w4_all_buys_10m", "since_last", "gap_any", "any_5m",
       "any_30m", "any_60m", "since_sell", "w4_last3", "w4_last5", "w4_last10", "prior_n", "prior_60s", "prior_err", "px_in_4", "hour"]
conds, names = [], []
for c in NUM:
    x = np.array([f[c] if f.get(c) is not None else np.nan for f in D], float); ok = ~np.isnan(x)
    for q in sorted({float(np.quantile(x[ok], k / 10)) for k in range(1, 10)}):
        for lab, m in ((f"{c} <= {q:.4g}", ok & (x <= q)), (f"{c} > {q:.4g}", ok & (x > q))):
            if 40 <= m.sum() <= n - 40: conds.append(m); names.append(lab)
for a in ("SOL", "WBTC", "PUMP", "SPCX"): conds.append(np.array([f["anchor"] == a for f in D])); names.append(f"pays with {a}")
for h in (1, 2, 3):
    m = np.array([f["hops"] == h for f in D])
    if m.sum() >= 40: conds.append(m); names.append(f"hops {h}")
EXCL = [x for x in os.environ.get("EXCL", "").split(",") if x]      # EXCL=bps,...: leave out conditions on these features
keep = [i for i, nm in enumerate(names) if not any(nm.startswith(x) for x in EXCL)]
conds = [conds[i] for i in keep]; names = [names[i] for i in keep]
C = np.array(conds, float); K = len(C)
size = C @ C.T; sizes1 = C.sum(1)
def search(net_, tp_, blocks=(0, 1, 2), score_blocks=(0, 1, 2)):
    """best valid single and pair: gain summed over score_blocks; valid = skipped set loses in each of `blocks`."""
    g = [-(C * (net_ * (blk == b))) @ C.T for b in range(3)]; t = (C * tp_) @ C.T
    gain = sum(g[b] for b in score_blocks)
    valid = (size >= 40) & (size <= 400) & (t <= MAXTP)
    for b in blocks: valid &= g[b] > 0
    gv = np.where(valid, gain, -1e9); i, j = np.unravel_index(np.argmax(gv), gv.shape)
    return gv[i, j], i, j, g, t, valid, gv
best, i, j, g, t, valid, gv = search(net, tp)
print(f"{n} copies, {int(tp.sum())} take profits, net of all {net.sum():+.2f} SOL; {K} conditions, {K + K * (K - 1) // 2} rules (one or two conditions); at most {MAXTP} take profits lost")
print(f"valid rules (skipped set loses in A, B and C): {int(np.triu(valid).sum())}")
order = np.dstack(np.unravel_index(np.argsort(-np.triu(gv), axis=None), gv.shape))[0]
print("the 25 best valid rules: gain SOL (A / B / C), copies skipped, take profits lost")
seen = 0
for a, b in order:
    if gv[a, b] < -1e8 or seen >= 25: break
    lab = names[a] if a == b else f"{names[a]}  AND  {names[b]}"
    print(f"   {gv[a, b]:+6.2f} ({g[0][a, b]:+5.2f} / {g[1][a, b]:+5.2f} / {g[2][a, b]:+5.2f})  {int(size[a, b]):3d} skipped, {int(t[a, b])} tp lost | {lab}"); seen += 1
# the guard: results shuffled inside each block
null = []
for _ in range(300):
    p = np.arange(n)
    for b in range(3):
        ix = np.where(blk == b)[0]; p[ix] = rng.permutation(ix)
    null.append(search(net[p], tp[p])[0])
null = np.array(null)
print(f"\nthe guard, results shuffled inside each block, 300 times: the best valid gain found by luck: median {np.median(null):+.2f}, 90% of the time under {np.quantile(null, 0.9):+.2f}, 95% under {np.quantile(null, 0.95):+.2f}, largest {null.max():+.2f}")
print(f"the real best {best:+.2f}: a shuffle did as well or better {100 * (null >= best).mean():.0f}% of the time")
# picked on two blocks, scored on the third
print("\npicked on two blocks (the best rule that loses in both and loses at most the limit of take profits), scored on the third:")
for out in range(3):
    tr = tuple(b for b in range(3) if b != out)
    bst, a, b, g2, t2, v2, gv2 = search(net, tp, blocks=tr, score_blocks=tr)
    top = np.dstack(np.unravel_index(np.argsort(-np.triu(gv2), axis=None)[:20], gv2.shape))[0]
    held = [g2[out][x, y] for x, y in top if gv2[x, y] > -1e8]
    nb = []
    for _ in range(100):
        p = np.arange(n)
        for bb in range(3):
            ix = np.where(blk == bb)[0]; p[ix] = rng.permutation(ix)
        nb.append(search(net[p], tp[p], blocks=tr, score_blocks=tr)[0])
    lab = names[a] if a == b else f"{names[a]}  AND  {names[b]}"
    print(f"   left out {'ABC'[out]}: best on the other two {bst:+.2f} (by luck: median {np.median(nb):+.2f}, 95% under {np.quantile(nb, 0.95):+.2f}); on {'ABC'[out]} it gains {g2[out][a, b]:+.2f}, loses {int(((C[a] * C[b]) * tp * (blk == out)).sum())} tp there | {lab}")
    print(f"      the 20 best on the other two: on {'ABC'[out]} their gain is {np.mean(held):+.2f} on average, {sum(1 for h in held if h > 0)} of {len(held)} above zero")
