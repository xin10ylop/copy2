# Holders and volume as an EXIT (Nov 19; the live trades: every coin had 1 holder at the leader's buy, so nothing to
# filter on; 60 s later the winner had 24 holders and most losers 3-9). Rule: T s after its buy, if the coin has fewer
# than N holders (or under V ETH traded since its launch), sell then (the live setting's exits still apply before T);
# else keep the live setting. Exact model, landing 2/3/5 blocks. Each rule picked on one half, scored on the other.
#   python3 -I rhd10_holders_exit.py DIR GROUPS_JSON > out/rhd10_holders_exit.txt
import sys, os, json, collections, numpy as np
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
D, GJ = sys.argv[1], sys.argv[2]; DATA = R.Data(D)
T_, H, S, ST, I = R.TP, R.HOLD, R.SPS, R.STALL, R.ITS
G = {m.split(":")[1] for m in json.load(open(GJ))["0xe3fdae6c"]}
W = {"wallet 1": ({"0x9a3955a122ab8a649a8511df2dce169471fd0ec1"}, 0.1, 0.5, 1.5, (T_.index(4), H.index(600), 0, 0, 0)),
     "wallet 2": ({"0x5bc235acecff3dde394f4bfc696f7c35efd502f0"}, 0.05, 0, 1.5, (T_.index(3.5), H.index(600), S.index((10, 30)), 0, 0)),
     "wallet 3": ({"0xc54d3914f91f984d61b63d491f38934c4e706b79"}, 0.03, 0, 1e9, (T_.index(2.5), H.index(300), S.index((8, 60)), ST.index(240), 0)),
     "group 4-8": (G, 0.02, 0.5, 1e9, (T_.index(3.5), H.index(600), 0, ST.index(240), I.index("early")))}
TS = [60, 120, 180]; HS = [3, 5, 8, 10, 12, 15, 20, 25]; VS = [0.2, 0.3, 0.5, 0.75, 1.0, 1.5]
def at(tr, t):
    bal = collections.defaultdict(float); vol = 0.0
    for e in tr:
        if e["t"] > t: break
        bal[e["user"]] += e["tok"] if e["buy"] else -e["tok"]; vol += e["q"] / 1e9
    return sum(1 for v in bal.values() if v > 1.0), vol
for name, (addrs, mn, mx, lim, ix) in W.items():
    rows = []
    for c in DATA.L:
        if c not in DATA.TR or not any(x[3] in addrs and x[2] for x in DATA.TR[c]): continue
        tr = DATA.path(c); k = next((j for j, e in enumerate(tr) if e["user"] in addrs and e["buy"]), None)
        if k is None or tr[k]["q"] / 1e9 < mn or tr[k]["t"] > DATA.t_end - 600: continue
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        if (mx and before >= mx) or tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue
        prems, vals = R.copy_one(tr, k)
        V = np.mean([vals[l] if prems[l] <= lim else np.full(vals[l].shape, -0.0004) for l in range(len(vals))], axis=0) / R.RATE
        live = V[tuple(ix)]; early = {}
        for t in TS:
            j = list(ix); j[1] = H.index(t)
            if H[ix[1]] <= t: early[t] = live          # the live time limit comes first: no change
            else: early[t] = V[tuple(j)]
        rows.append(dict(t=tr[k]["t"], live=live, early=early, f={t: at(tr, tr[k]["t"] + t) for t in TS}))
    rows.sort(key=lambda r: r["t"]); t = np.array([r["t"] for r in rows]); A = t < np.median(t); B = ~A
    live = np.array([r["live"] for r in rows])
    print(f"\n=== {name}: {len(rows)} copies, live {100 * live.mean() / R.STAKE:+.1f}% a copy, {live.sum():+.3f} ETH (halves {live[A].sum():+.3f} / {live[B].sum():+.3f})")
    rules = []
    for T in TS:
        E = np.array([r["early"][T] for r in rows])
        for kind, th_list, fi in (("holders", HS, 0), ("ETH traded", VS, 1)):
            F = np.array([r["f"][T][fi] for r in rows])
            for th in th_list:
                x = np.where(F < th, E, live); rules.append((f"at {T:3d} s, {kind} < {th}: sell", x, (F < th).mean()))
    for P, Q, lab in ((A, B, "half 1 -> half 2"), (B, A, "half 2 -> half 1")):
        best = max(rules, key=lambda r: r[1][P].sum())
        print(f"   picked on {lab}: '{best[0]}' (sells early {100 * best[2]:.0f}% of copies): {best[1][P].sum() - live[P].sum():+.3f} ETH on the pick half, "
              f"{best[1][Q].sum() - live[Q].sum():+.3f} on the other{'  <- holds' if best[1][Q].sum() > live[Q].sum() and best[1][P].sum() > live[P].sum() else ''}")
    good = [(n_, x, s_) for n_, x, s_ in rules if x[A].sum() > live[A].sum() and x[B].sum() > live[B].sum()]
    print(f"   rules better than live on BOTH halves: {len(good)} of {len(rules)}")
    for n_, x, s_ in sorted(good, key=lambda r: -min(r[1][A].sum() - live[A].sum(), r[1][B].sum() - live[B].sum()))[:6]:
        print(f"      {n_:34s} sells early {100 * s_:3.0f}%: {100 * x.mean() / R.STAKE:+.1f}% a copy, halves {x[A].sum() - live[A].sum():+.3f} / {x[B].sum() - live[B].sum():+.3f} ETH against live")
