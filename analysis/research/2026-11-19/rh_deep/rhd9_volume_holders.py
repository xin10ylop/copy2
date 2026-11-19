# Volume and holders as filters (Nov 19; the owner: "check volume and holders (nb of holders) maybe can be helpful").
# At the copied buy, from the coin's own trades before it: holders (addresses with tokens left), distinct buyers, ETH
# traded, trades, ETH traded in the last 60 s, the coin's age. Our copy under each wallet's live setting (exact model,
# landing 2/3/5 blocks, every coin). For each feature: our result by quintile on each half; then every "keep >= x" and
# "keep < x" (x = a quintile edge) picked on one half and scored on the other, both ways; a filter counts only if it
# beats no filter on BOTH halves when picked on the other.
#   python3 -I rhd9_volume_holders.py DIR GROUPS_JSON > out/rhd9_volume_holders.txt
import sys, os, json, collections, numpy as np
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
D, GJ = sys.argv[1], sys.argv[2]; DATA = R.Data(D)
T, H, S, ST, I = R.TP, R.HOLD, R.SPS, R.STALL, R.ITS
G = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
W = {"wallet 1": ({"0x9a3955a122ab8a649a8511df2dce169471fd0ec1"}, 0.1, 0.5, 1.5, (T.index(4), H.index(600), 0, 0, 0)),
     "wallet 2": ({"0x5bc235acecff3dde394f4bfc696f7c35efd502f0"}, 0.05, 0, 1.5, (T.index(3.5), H.index(600), S.index((10, 30)), 0, 0)),
     "wallet 3": ({"0xc54d3914f91f984d61b63d491f38934c4e706b79"}, 0.03, 0, 1e9, (T.index(2.5), H.index(300), S.index((8, 60)), ST.index(240), 0)),
     "group 4-8": (G, 0.02, 0.5, 1e9, (T.index(3.5), H.index(600), 0, ST.index(240), I.index("early")))}
FEAT = ["holders", "buyers", "ETH traded", "trades", "ETH last 60 s", "age s"]
def features(tr, k):
    bal = collections.defaultdict(float); buyers = set(); vol = 0.0; v60 = 0.0; t0 = tr[0]["t"]; tk = tr[k]["t"]
    for e in tr[:k]:
        bal[e["user"]] += e["tok"] if e["buy"] else -e["tok"]
        if e["buy"]: buyers.add(e["user"])
        vol += e["q"] / 1e9
        if e["t"] >= tk - 60: v60 += e["q"] / 1e9
    return [sum(1 for v in bal.values() if v > 1.0), len(buyers), vol, k, v60, tk - t0]
for name, (addrs, mn, mx, lim, ix) in W.items():
    rows = []
    for c in DATA.L:
        if c not in DATA.TR or not any(x[3] in addrs and x[2] for x in DATA.TR[c]): continue
        tr = DATA.path(c); k = next((j for j, e in enumerate(tr) if e["user"] in addrs and e["buy"]), None)
        if k is None or tr[k]["q"] / 1e9 < mn or tr[k]["t"] > DATA.t_end - 600: continue
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        if (mx and before >= mx) or tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue
        prems, vals = R.copy_one(tr, k)
        x = np.mean([vals[l][ix] if prems[l] <= lim else -0.0004 for l in range(len(vals))]) / R.RATE
        rows.append((tr[k]["t"], x, features(tr, k)))
    rows.sort(); t = np.array([r[0] for r in rows]); X = np.array([r[1] for r in rows]); F = np.array([r[2] for r in rows], float)
    A = t < np.median(t); B = ~A
    print(f"\n=== {name}: {len(rows)} copies, {100 * X.mean() / R.STAKE:+.1f}% a copy, {X.sum():+.3f} ETH (halves {X[A].sum():+.3f} / {X[B].sum():+.3f})")
    for f, fn in enumerate(FEAT):
        q = np.quantile(F[:, f], [0.2, 0.4, 0.6, 0.8]); b = np.searchsorted(q, F[:, f], side="right")
        cells = " | ".join(f"{100 * X[(b == i) & A].mean() / R.STAKE:+5.0f}% {100 * X[(b == i) & B].mean() / R.STAKE:+5.0f}%" if ((b == i) & A).any() and ((b == i) & B).any() else "   -" for i in range(5))
        print(f"   {fn:14s} quintile edges {', '.join(f'{v:.3g}' for v in q):30s} a copy (half 1 half 2) by quintile: {cells}")
    # filters picked on one half, scored on the other
    found = []
    for f, fn in enumerate(FEAT):
        edges = np.unique(np.quantile(F[:, f], [0.2, 0.4, 0.6, 0.8]))
        cands = [(f">= {x:.3g}", F[:, f] >= x) for x in edges] + [(f"< {x:.3g}", F[:, f] < x) for x in edges]
        for P, Q in ((A, B), (B, A)):
            lab, m = max(cands, key=lambda c: X[c[1] & P].sum())
            gain_pick, gain_test = X[m & P].sum() - X[P].sum(), X[m & Q].sum() - X[Q].sum()
            found.append((fn, lab, "1" if P is A else "2", gain_pick, gain_test, (m & Q).sum(), Q.sum()))
    print("   picked on one half -> scored on the other (ETH gained against no filter; copies kept):")
    for fn, lab, h, gp, gt, kept, tot in found:
        print(f"      {fn:14s} keep {lab:10s} picked on half {h}: {gp:+.3f} there, {gt:+.3f} on the other half ({kept}/{tot} copies kept){'  <- holds' if gt > 0 else ''}")
