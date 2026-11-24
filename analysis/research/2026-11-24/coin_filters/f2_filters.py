# Does the coin at its buy tell a losing copy from a winning one? (Nov 24). f1_rows.py's copies of the six new wallets,
# each unit's own coins and live exit (CqCAzte8: all coins, token coins tp 3x / 420 s / stall 240, SOL coins tp 2x /
# 120 s; CgyPomTG, GqWfqfG6: all coins, tp 3x / 420 s / stall 240; 3XeFcZKS, 6LwMLkCe, 6nNzEg86: token coins, the same
# exit), 1 SOL a copy, refused over 1.5x its price (-0.0004). Each wallet's copies in time order cut in 4 blocks.
#  1. Each measure in 5 equal groups (pooled cut points): % a copy, and in how many of the 6 wallets the group is
#     positive. A filter can only help if one end is negative on most wallets.
#  2. 48 skip rules (6 measures x skip the lowest / highest 10 20 30 40%, cut points from the seen copies), picked on
#     blocks 1-2 of every wallet (the most SOL gained, without the best 2% of the skipped copies' losses), scored once on
#     blocks 3-4 (blind). Freed slots are not refilled (max_open 2 rarely binds at these rates).
#  3. Luck: the same pick with each wallet's measures shuffled among its copies (no information left), 300 times: the
#     blind gain a pick of 48 makes by chance, and how often chance beats the real pick.
#   python3 -I f2_filters.py DIR_OF_JSON
import sys, os, json, numpy as np
D = sys.argv[1]
UNITS = {"CqCAzte8": "all", "CgyPomTG": "all", "GqWfqfG6": "all", "3XeFcZKS": "token", "6LwMLkCe": "token", "6nNzEg86": "token"}
FEAT = {"prog": "curve progress (0 launch, 1 graduation)", "mcap": "market cap, SOL", "bps": "fee tier, bps",
        "size": "its buy, SOL", "impact": "its buy / curve quote", "ahead": "buyers in its slot before it"}
rows = []
for w, kind in UNITS.items():
    d = json.load(open(f"{D}/{w}.json")); ex = d["exits"]
    e_tok, e_sol = ex.index("tp 3x / 420 s / stall 240"), ex.index("tp 2x / 120 s")
    rs = [r for r in d["rows"] if kind == "all" or r["tok"]]
    for i, b in enumerate(np.array_split(np.arange(len(rs)), 4)):
        for j in b:
            r = rs[j]
            v = -0.0004 if r["prem"] > 1.5 else r["g"][e_tok if (r["tok"] or w != "CqCAzte8") else e_sol]
            rows.append(dict(w=w, blk=i, v=v, **{f: (np.nan if r.get(f) is None else float(r[f])) for f in FEAT}))
W = np.array([r["w"] for r in rows]); B = np.array([r["blk"] for r in rows]); V = np.array([r["v"] for r in rows])
X = {f: np.array([r[f] for r in rows]) for f in FEAT}
print(f"{len(rows)} copies, 6 wallets: " + ", ".join(f"{w} {np.sum(W == w)} ({100 * V[W == w].mean():+.1f}%)" for w in UNITS)
      + f"; all {100 * V.mean():+.1f}% a copy, {V.sum():+.2f} SOL at 1 SOL")
print("\n1. each measure in 5 equal groups: % a copy (n), wallets with the group positive (of those with 5+ copies in it)")
for f, lab in FEAT.items():
    x = X[f]; ok = ~np.isnan(x); qs = np.nanpercentile(x, [20, 40, 60, 80])
    grp = np.digitize(x, qs); cells = []
    for gi in range(5):
        m = ok & (grp == gi); pw = [V[m & (W == w)].mean() > 0 for w in UNITS if np.sum(m & (W == w)) >= 5]
        cells.append(f"{100 * V[m].mean():+5.1f}% ({m.sum():3d}) {sum(pw)}/{len(pw)}")
    print(f"  {lab:38s} cuts {', '.join(f'{q:.3g}' for q in qs)}\n     " + " | ".join(cells))
SEEN, BLIND = B <= 1, B >= 2
def wo2(v):
    if not len(v): return 0.0
    k = max(1, round(0.02 * len(v))); return v.sum() - np.sort(v)[-k:].sum()
RULES = [(f, side, q) for f in FEAT for side in ("low", "high") for q in (10, 20, 30, 40)]
def skipmask(x, f, side, q):
    s = x[SEEN & ~np.isnan(x)]
    if not len(s): return np.zeros(len(x), bool)
    t = np.percentile(s, q if side == "low" else 100 - q)
    return ~np.isnan(x) & ((x < t) if side == "low" else (x > t))
def pick(Xs):
    best = None
    for f, side, q in RULES:
        sk = skipmask(Xs[f], f, side, q); gain = -wo2(V[SEEN & sk])   # what skipping saved on the seen blocks
        if best is None or gain > best[0]: best = (gain, (f, side, q), sk)
    return best
gain, rule, sk = pick(X)
bl = -V[BLIND & sk].sum(); per = {w: -V[BLIND & sk & (W == w)].sum() for w in UNITS}
print(f"\n2. the pick on blocks 1-2: skip {rule[0]} {rule[1]}est {rule[2]}% -> seen gain {gain:+.2f} SOL "
      f"(skips {np.sum(SEEN & sk)} of {SEEN.sum()})")
print(f"   blind, blocks 3-4: {bl:+.2f} SOL (skips {np.sum(BLIND & sk)} of {BLIND.sum()}, their mean {100 * V[BLIND & sk].mean():+.1f}%); "
      f"per wallet: " + ", ".join(f"{w} {g:+.2f}" for w, g in per.items()) + f"; helps on {sum(g > 0 for g in per.values())} of 6")
print("   every rule's blind gain (seen gain), the top 10 by seen:")
tab = []
for f, side, q in RULES:
    m = skipmask(X[f], f, side, q); tab.append((-wo2(V[SEEN & m]), -V[BLIND & m].sum(), f, side, q, sum(-V[BLIND & m & (W == w)].sum() > 0 for w in UNITS)))
for sg, bg, f, side, q, nw in sorted(tab, reverse=True)[:10]:
    print(f"     skip {f:6s} {side:4s} {q}%: seen {sg:+6.2f}, blind {bg:+6.2f} SOL, blind helps {nw}/6 wallets")
print(f"   rules with a blind gain: {sum(1 for t in tab if t[1] > 0)} of {len(tab)}; both seen and blind: {sum(1 for t in tab if t[0] > 0 and t[1] > 0)}")
rng = np.random.default_rng(7); lb = []
for _ in range(300):
    Xs = {}
    for f in FEAT:
        x = X[f].copy()
        for w in UNITS:
            ix = np.where(W == w)[0]; x[ix] = x[rng.permutation(ix)]
        Xs[f] = x
    _, _, s_ = pick(Xs); lb.append(-V[BLIND & s_].sum())
lb = np.array(lb)
print(f"\n3. luck: the pick on shuffled measures, blind gain: median {np.median(lb):+.2f}, 90% {np.percentile(lb, 90):+.2f}, "
      f"95% {np.percentile(lb, 95):+.2f} SOL; chance beats the real pick {np.mean(lb >= bl):.0%} of the time")
