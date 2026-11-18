# Our copy of a Robinhood Chain (Pons V2) wallet, on chain (Nov 18): the curve is a constant product on virtual
# reserves, V0 = 1.75 ETH and T0 = 714,285,714 * (V0 + 4.2) / 4.2 tokens, fee on top of the quote (rh3_curve_fit.py:
# 0.57% median error on 3,517 buys). Each ETH-quoted curve's trades become a path in hunt_lib's form (virtual reserves,
# fee + creator tax in bps, the block as the slot); a graduation ends the path (the v4 pool is not read: the model
# sells at the curve's last price). Our stake STAKE ETH, landing 4 / 8 trades after its buy or the next block (mean),
# gas GAS ETH a round trip; e8's full exit grid; week 1 against week 2.
#   python3 -I rh4_copy.py DIR WALLET [WALLET...] > out/rh4_<w>.txt   (STAKE=0.02 GAS=0.00004 MINQ=0.05)
import sys, os, json, gzip, glob, bisect, collections, numpy as np, datetime as dt
D, WS = sys.argv[1], sys.argv[2:]; STAKE = float(os.environ.get("STAKE", 0.02)); GAS = float(os.environ.get("GAS", 0.00004)); MINQ = float(os.environ.get("MINQ", 0.05))
E8 = "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt/market/e8_engineer.py"
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt"); sys.argv = ["x", "/tmp", "x"]
exec(open(E8).read().split("rows = []")[0].replace("here = os.path.dirname(os.path.abspath(__file__))", "here = os.path.dirname(E8)"))
RATE = 0.5 / STAKE                     # copy_vals' 0.5 "stake units" = STAKE ETH; quote unit = 1e-9 ETH
COST = GAS * RATE - 0.0026             # copy_vals already charges 0.0026 units
T = json.load(open(f"{D}/topics.json")); B = {int(k): v for k, v in json.load(open(f"{D}/blocks.json")).items()}; bk = sorted(B)
FACTORY = "0x7ed598bcef8bd9edd8c97a195c6d13f40801ec7e"; V0 = 1.75; T0 = 1e9 * 5 / 7 * (V0 + 4.2) / 4.2
def tm(n):
    i = min(max(bisect.bisect_left(bk, n), 1), len(bk) - 1); a, b = bk[i - 1], bk[i]; return B[a] + (B[b] - B[a]) * (n - a) / max(1, b - a)
words = lambda d: [int(d[2 + 64 * i: 2 + 64 * (i + 1)], 16) for i in range((len(d) - 2) // 64)]
L, TR, GRAD = {}, collections.defaultdict(list), {}
SEEN = set()
for f in glob.glob(f"{D}/logs_*.json.gz"):
    for l in json.load(gzip.open(f)):
        if (l["blockNumber"], l["logIndex"]) in SEEN: continue   # overlapping chunks (a later fetch from a newer tip)
        SEEN.add((l["blockNumber"], l["logIndex"])); t0 = l["topics"][0]
        if t0 == T["TokenLaunched"] and l["address"].lower() == FACTORY:
            w = words(l["data"])
            if len(w) >= 3 and w[0] == 0: L["0x" + l["topics"][2][-40:]] = "0x" + l["topics"][1][-40:]
        elif t0 == T["LaunchSwept"]: GRAD["0x" + l["topics"][1][-40:]] = int(l["blockNumber"], 16)
        elif t0 in (T["CurveBuy"], T["CurveSell"]):
            TR[l["address"].lower()].append((int(l["blockNumber"], 16), int(l["logIndex"], 16), t0 == T["CurveBuy"], "0x" + (l["topics"][2] if t0 == T["CurveBuy"] else l["topics"][1])[-40:], words(l["data"])))
WS = [w.lower() for w in WS]; mine = {c for c in L if any(x[3] in WS for x in TR.get(c, []))}
def path(c):
    Q = S = 0.0; out = []; g = GRAD.get(L[c])
    for n, i, buy, u, w in sorted(TR[c]):
        if buy: q, tok = w[0] / 1e18, w[1] / 1e18
        else: q, tok = w[1] / 1e18, w[0] / 1e18
        bps = 1e4 * (w[2] + w[3]) / max(1, w[0] if buy else w[1])
        vt0, vq0 = T0 - S, V0 + Q                     # the state before the trade (hunt_lib reads the state after: below)
        if buy: Q += q; S += tok
        else: Q -= q; S -= tok
        out.append(dict(slot=n, t=tm(n), user=u, buy=buy, q=q * 1e9, tok=tok, vt=T0 - S, vq=(V0 + Q) * 1e9, bps=bps, real=0 if (g and n >= g) else 1))
    return out
for W in WS:
    rows = []
    for c in mine:
        tr = path(c); k = next((j for j, e in enumerate(tr) if e["user"] == W and e["buy"]), None)
        if k is None or tr[k]["q"] / 1e9 < MINQ or tr[-1]["t"] - tr[k]["t"] < 600: continue
        ps = [H.prep(tr, k, RATE, n, pmax=1000) for n in (4, 8, "slot+1")]
        for p in ps: p["rate"] = RATE                 # 0.5e9 * hopf / rate quote units = STAKE ETH
        rows.append(dict(t=tr[k]["t"], sz=tr[k]["q"] / 1e9, prem=[(tr[k]["vt"] / p["ent"][0]) ** 2 for p in ps], vl=np.array([copy_vals(p) for p in ps]) - COST))
    if len(rows) < 20: print(f"\n{W}: {len(rows)} copies, too few"); continue
    rows.sort(key=lambda r: r["t"]); Tt = np.array([r["t"] for r in rows]); tmid = float(os.environ["SPLIT"]) if os.environ.get("SPLIT") else (min(tm(n) for n in bk) + max(tm(n) for n in bk)) / 2; A = Tt < tmid
    print(f"\n{W}: {len(rows)} copies of its first buys of {MINQ}+ ETH ({int(A.sum())} in week 1, {int((~A).sum())} in week 2), {dt.datetime.fromtimestamp(Tt.min(), dt.UTC):%m-%d} to {dt.datetime.fromtimestamp(Tt.max(), dt.UTC):%m-%d}; our {STAKE} ETH, {GAS} ETH gas a round trip; its buys median {np.median([r['sz'] for r in rows]):.3f} ETH")
    best = None; tot = both = 0
    for pm in (1.1, 1.25, 1.5, 1e9):
        V = np.array([np.mean([r["vl"][l] if r["prem"][l] <= pm else np.full(r["vl"][l].shape, -0.0004) for l in range(3)], axis=0) for r in rows]) / RATE   # ETH
        s1, s2 = V[A].sum(0), V[~A].sum(0); tot += s1.size; both += int(((s1 > 0) & (s2 > 0)).sum()); w = np.minimum(s1, s2); j = np.unravel_index(int(np.argmax(w)), w.shape)
        if best is None or w[j] > best[0]: best = (w[j], pm, j, s1[j], s2[j], V[(slice(None),) + j])
        if pm == 1.5:
            for lab, ix in (("wallet 4's live exit", (TP.index(4), HOLD.index(600), SPS.index((5, 60)), STALL.index(180), ITS.index("early"))),
                            ("its sale followed, tp 4", (TP.index(4), HOLD.index(600), SPS.index((5, 60)), STALL.index(180), ITS.index("always"))),
                            ("tp 2, 120 s", (TP.index(2), HOLD.index(120), 0, 0, 0))):
                x = V[(slice(None),) + ix]; print(f"   {lab:24s} (limit 1.5x): {x.sum():+.4f} ETH ({100 * x.mean() / STAKE:+.1f}% a copy), week 1 {x[A].sum():+.4f} / week 2 {x[~A].sum():+.4f}, won {100 * np.mean(x > 0):.0f}%")
    for spec in [x for x in os.environ.get("FIX", "").split(";") if x]:   # fixed settings "limit,tp,hold,sp,stall,its" scored on both periods
        z = spec.split(","); pm_ = 1e9 if z[0] == "none" else float(z[0])
        ix = (TP.index(1e9 if z[1] == "none" else float(z[1])), HOLD.index(int(z[2])), SPS.index(None if z[3] == "off" else tuple(int(v) for v in z[3].split("/"))), STALL.index(0 if z[4] == "off" else int(z[4])), ITS.index(z[5]))
        V_ = np.array([np.mean([r["vl"][l][ix] if r["prem"][l] <= pm_ else -0.0004 for l in range(3)]) for r in rows]) / RATE
        for lab, m_ in (("older period", A), ("newer period", ~A)):
            x_ = V_[m_]; k_ = max(1, round(0.02 * len(x_))); bs_ = np.random.default_rng(7).choice(x_, size=(10000, len(x_))).mean(1) if len(x_) else np.zeros(1)
            print(f"   FIXED {spec:28s} {lab}: {len(x_)} copies {x_.sum():+.4f} ETH ({100 * x_.mean() / STAKE:+.1f}% a copy), w/o 2% {np.sort(x_)[:-k_].sum():+.4f}, won {100 * np.mean(x_ > 0):.0f}%, P(mean>0) {100 * np.mean(bs_ > 0):.1f}%")
    w, pm, j, a1, a2, x = best; k2 = max(1, round(0.02 * len(x))); bs = np.random.default_rng(7).choice(x, size=(10000, len(x))).mean(1)
    print(f"   settings positive in both weeks: {both:,} of {tot:,}")
    print(f"   best by its weaker week (hindsight): limit {'none' if pm > 1e8 else pm}, tp {TP[j[0]] if TP[j[0]] < 1e8 else 'none'}, {HOLD[j[1]]} s, sp {SPS[j[2]] or 'off'}, stall {STALL[j[3]] or 'off'}, its sale {ITS[j[4]]}: "
          f"{x.sum():+.4f} ETH ({100 * x.mean() / STAKE:+.1f}% a copy), weeks {a1:+.4f} / {a2:+.4f}, w/o 2% {np.sort(x)[:-k2].sum():+.4f}, won {100 * np.mean(x > 0):.0f}%, P(mean>0) {100 * np.mean(bs > 0):.1f}%")
