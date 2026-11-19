# "He is making much more than us" (Nov 19; the owner, after 15 live trades, 2 won: "i feel something is wrong ... also
# check if we get rid of the time"). For each live wallet, on the exact model (rhd_lib, landing 2/3/5 blocks, every coin):
#   - the LEADER'S OWN result on the coins we copy (its sales minus its buys on the coin; tokens it still holds valued at
#     the curve's last state), against our copy's
#   - the live setting, then the same with its sale followed (always / early), and the time limit from 60 s to none
#     (holds of 900, 1800, 3600 s and "none" added to the grid), each over the 41 days (halves), the last 7 and 3 days,
#     and today (UTC)
#   python3 -I rhd8_exit_redo.py DIR > out/rhd8_exit_redo.txt
import sys, os, numpy as np, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
R.HOLD[:] = [60, 120, 180, 300, 450, 600, 900, 1800, 3600, 10 ** 7]   # copy_vals reads the list at call time
D = sys.argv[1]; DATA = R.Data(D)
H = R.HOLD; T = R.TP; S = R.SPS; ST = R.STALL; I = R.ITS
LIVE = {1: ("0x9a3955a122ab8a649a8511df2dce169471fd0ec1", 0.1, 0.5, 1.5, (T.index(4), H.index(600), 0, 0, I.index("never"))),
        2: ("0x5bc235acecff3dde394f4bfc696f7c35efd502f0", 0.05, 0, 1.5, (T.index(3.5), H.index(600), S.index((10, 30)), 0, I.index("never"))),
        3: ("0xc54d3914f91f984d61b63d491f38934c4e706b79", 0.03, 0, 1e9, (T.index(2.5), H.index(300), S.index((8, 60)), ST.index(240), I.index("never")))}
TODAY = (DATA.t_end // 86400) * 86400
print(f"data {dt.datetime.fromtimestamp(DATA.t_start, dt.UTC):%m-%d %H:%M} to {dt.datetime.fromtimestamp(DATA.t_end, dt.UTC):%m-%d %H:%M} UTC; landing +{R.LANDB} blocks; our {R.STAKE} ETH")
def own(tr, addr):
    """the leader's own result on the coin: ETH out - ETH in, its tokens left valued at the last state (sold into it)"""
    ein = eout = tin = tout = 0.0
    for e in tr:
        if e["user"] != addr: continue
        if e["buy"]: ein += e["q"] / 1e9; tin += e["tok"]
        else: eout += e["q"] / 1e9; tout += e["tok"]
    left = max(0.0, tin - tout); last = tr[-1]
    if left > 0: q, t = last["vq"] / 1e9, last["vt"]; eout += (q - q * t / (t + left)) * 0.98
    return (eout - ein) / ein if ein > 0 else np.nan
for w, (addr, mn, mx, lim, ix) in LIVE.items():
    rows = []
    for c in DATA.L:
        if c not in DATA.TR or not any(x[3] == addr and x[2] for x in DATA.TR[c]): continue
        tr = DATA.path(c); k = next((j for j, e in enumerate(tr) if e["user"] == addr and e["buy"]), None)
        if k is None or tr[k]["q"] / 1e9 < mn or tr[k]["t"] > DATA.t_end - 600: continue
        before = (tr[k - 1]["vq"] / 1e9 - R.V0) if k else 0.0
        if (mx and before >= mx) or tr[k]["vq"] / 1e9 - R.V0 >= 3.8: continue
        prems, vals = R.copy_one(tr, k)
        V = np.mean([vals[l] if prems[l] <= lim else np.full(vals[l].shape, -0.0004) for l in range(len(vals))], axis=0) / R.RATE
        rows.append(dict(t=tr[k]["t"], V=V, own=own(tr, addr)))
    rows.sort(key=lambda r: r["t"]); Tt = np.array([r["t"] for r in rows]); X = np.array([r["V"] for r in rows]); OWN = np.array([r["own"] for r in rows])
    mid = np.median(Tt); masks = [("all", np.ones(len(Tt), bool)), ("half 1", Tt < mid), ("half 2", Tt >= mid), ("last 7 d", Tt >= DATA.t_end - 7 * 86400),
                                   ("last 3 d", Tt >= DATA.t_end - 3 * 86400), ("today", Tt >= TODAY)]
    print(f"\n=== wallet {w} {addr}: {len(rows)} copies (its buys {mn}+ ETH{', coins under ' + str(mx) + ' ETH' if mx else ''}, limit {'none' if lim > 1e8 else lim})")
    print(f"   {'':40s}" + "".join(f"{lab:>17s}" for lab, _ in masks))
    print(f"   {'THE LEADER ITSELF on these coins':40s}" + "".join(f"{100 * np.nanmean(OWN[m]):+8.1f}% ({m.sum():4d})" for lab, m in masks))
    def row(lab, ix_):
        x = X[(slice(None),) + tuple(ix_)]
        print(f"   {lab:40s}" + "".join(f"{100 * x[m].mean() / R.STAKE:+8.1f}% {x[m].sum():+7.3f}" if m.any() else f"{'':>17s}" for _, m in masks))
    row("LIVE setting (ours)", ix)
    for its in ("early", "always"):
        j = list(ix); j[4] = I.index(its); row(f"live, its sale {its}", j)
    for h in H:
        j = list(ix); j[1] = H.index(h); row(f"live, time {'none' if h > 1e6 else str(h) + ' s'}", j)
    for its in ("early", "always"):
        j = list(ix); j[4] = I.index(its); j[1] = H.index(10 ** 7); row(f"its sale {its}, time none", j)
    # the best by the weaker half, its sale and time free (the rest of the live setting kept)
    best = None
    for a in range(len(I)):
        for b in range(len(H)):
            j = list(ix); j[4] = a; j[1] = b; x = X[(slice(None),) + tuple(j)]; v = min(x[Tt < mid].sum(), x[Tt >= mid].sum())
            if best is None or v > best[0]: best = (v, j)
    row(f"best by the weaker half: its {I[best[1][4]]}, time {'none' if H[best[1][1]] > 1e6 else H[best[1][1]]}", best[1])
print("\n(each cell: our result a copy, then the ETH in all; the leader's own: its mean % on the coin, copies in brackets)")
