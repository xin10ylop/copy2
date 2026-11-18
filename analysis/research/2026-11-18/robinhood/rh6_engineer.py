# The full engineering of a Robinhood Chain (Pons) copy (Nov 18; the owner: "everything: stall, sell pressure, buy
# size, types of coins, tp's, hold time, its sell, all tested across small increments"). rh4's curve model and
# landings; every combination of:
#   its buy size (min, ETH) 0.03 0.05 0.075 0.1 0.15 0.2 0.3 0.5 | coin type: the curve's progress when it buys (ETH in
#   the curve: any, under 0.5, 0.5-1.5, 1.5-3, 3+ of the 4.2 to graduate) | price limit 1.1 1.25 1.5 none
#   take profit 1.5 2 2.5 3 3.5 4 5 6 8 none | time 60 120 180 300 450 600 s | sell pressure off, 3/5/8/10 over 30/60 s
#   stall off 60 90 120 180 240 s | its sale never / early (30-290 s under 1.5x) / always
# Chosen as e8: by the SOL... here ETH... the WEAKER half makes without its best 2%, smoothed over the neighbours; each
# part varied alone, each size band and coin type alone, the setting picked on one half scored on the other.
#   python3 -I rh6_engineer.py DIR WALLET > out/rh6_<w>.txt   (STAKE GAS SPLIT as rh4)
import sys, os, collections, numpy as np, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); D, WAL = sys.argv[1], sys.argv[2].lower()
src = open(os.path.join(here, "rh4_copy.py")).read().split("for W in WS:")[0]
os.environ["MINQ"] = "0.03"; sys.argv = ["x", D, WAL]; exec(src)
SIZES = [0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.5]; PROG = [("any", 0, 9), ("<0.5", 0, 0.5), ("0.5-1.5", 0.5, 1.5), ("1.5-3", 1.5, 3), ("3+", 3, 9)]; PMS = [1.1, 1.25, 1.5, 1e9]
rows = []
for c in mine:
    tr = path(c); k = next((j for j, e in enumerate(tr) if e["user"] == WAL and e["buy"]), None)
    if k is None or tr[k]["q"] / 1e9 < 0.03 or tr[-1]["t"] - tr[k]["t"] < 600: continue
    if os.environ.get("LANDB"):   # our buy lands D blocks after its buy, for each D (never inside its block): a copier sees the block, then sends
        js = [next((j for j in range(k + 1, len(tr)) if tr[j]["slot"] >= tr[k]["slot"] + int(d_)), None) for d_ in os.environ["LANDB"].split(",")]
        if any(j is None for j in js): continue
        ps = [H.prep(tr, k, RATE, j - k, pmax=1000) for j in js]
    else: ps = [H.prep(tr, k, RATE, n, pmax=1000) for n in (4, 8, "slot+1")]
    for p in ps: p["rate"] = RATE
    rows.append(dict(t=tr[k]["t"], sz=tr[k]["q"] / 1e9, prog=tr[k]["vq"] / 1e9 - V0 - tr[k]["q"] / 1e9, prem=[(tr[k]["vt"] / p["ent"][0]) ** 2 for p in ps], vl=[copy_vals(p) - COST for p in ps]))
rows.sort(key=lambda r: r["t"]); Tt = np.array([r["t"] for r in rows]); N = len(rows)
SPLIT = float(os.environ["SPLIT"]) if os.environ.get("SPLIT") else float(np.median(Tt)); A = Tt < SPLIT
print(f"[landing: {('blocks +' + os.environ['LANDB']) if os.environ.get('LANDB') else '4 / 8 trades or the next block'}] " + f"{WAL}: {N} copies of its first buys of 0.03+ ETH, {dt.datetime.fromtimestamp(Tt.min(), dt.UTC):%m-%d} to {dt.datetime.fromtimestamp(Tt.max(), dt.UTC):%m-%d}; halves at {dt.datetime.fromtimestamp(SPLIT, dt.UTC):%m-%d %H:%M} UTC ({int(A.sum())} / {int((~A).sum())}); our {STAKE} ETH, {GAS} ETH gas a round trip")
SZ = np.array([r["sz"] for r in rows]); PG = np.array([r["prog"] for r in rows])
VP = {pm: np.array([np.mean([r["vl"][l] if r["prem"][l] <= pm else np.full(r["vl"][l].shape, -0.0004) for l in range(3)], axis=0) for r in rows]) / RATE for pm in PMS}   # ETH
ex_shape = VP[1.5].shape[1:]; MINN = 15
S1 = np.full((len(SIZES), len(PROG), len(PMS)) + ex_shape, np.nan); S2 = S1.copy(); SA = S1.copy(); M1 = S1.copy(); M2 = S1.copy(); NN = np.zeros((len(SIZES), len(PROG), len(PMS)), int)
def w2(X):
    k = max(1, round(0.02 * len(X))); return X.sum(0) - np.partition(X, len(X) - k, axis=0)[len(X) - k:].sum(0)
for a, sz in enumerate(SIZES):
    for b, (_, lo, hi) in enumerate(PROG):
        for c_, pm in enumerate(PMS):
            f = (SZ >= sz) & (PG >= lo) & (PG < hi); NN[a, b, c_] = f.sum()
            if (f & A).sum() >= MINN and (f & ~A).sum() >= MINN:
                X = VP[pm]; S1[a, b, c_], S2[a, b, c_] = w2(X[f & A]), w2(X[f & ~A]); SA[a, b, c_] = X[f].sum(0); M1[a, b, c_], M2[a, b, c_] = X[f & A].mean(0), X[f & ~A].mean(0)
weak = np.minimum(S1, S2); ok = ~np.isnan(weak); wf = np.where(ok, weak, 0.0); num = wf.copy(); den = ok.astype(float)
def edge(shape, d, sh):
    m = np.ones(shape); sl = [slice(None)] * len(shape); sl[d] = 0 if sh == 1 else -1; m[tuple(sl)] = 0; return m
for d in range(weak.ndim):
    for sh in (-1, 1): num += np.roll(wf, sh, axis=d) * edge(weak.shape, d, sh); den += np.roll(ok.astype(float), sh, axis=d) * edge(weak.shape, d, sh)
smooth = np.where(ok & (den > 0.25 * (1 + 2 * weak.ndim)), num / np.maximum(den, 1e-9), -np.inf)
idx = np.unravel_index(int(np.argmax(smooth)), smooth.shape)
def name(ix):
    a, b, c_, t, h, sp, st, it = ix
    return (f"its buy {SIZES[a]}+ ETH, coin {PROG[b][0]} ETH in the curve, limit {'none' if PMS[c_] > 1e8 else str(PMS[c_]) + 'x'}, tp {'none' if TP[t] > 1e8 else str(TP[t]) + 'x'}, {HOLD[h]} s, "
            f"sell pressure {'off' if SPS[sp] is None else f'{SPS[sp][0]}/{SPS[sp][1]}s'}, stall {STALL[st] or 'off'}, its sale {ITS[it]}")
def stats(ix):
    a, b, c_ = ix[:3]; f = (SZ >= SIZES[a]) & (PG >= PROG[b][1]) & (PG < PROG[b][2]); x = VP[PMS[c_]][f][(slice(None),) + tuple(ix[3:])]
    bs = np.random.default_rng(7).choice(x, size=(10000, len(x))).mean(1); k = max(1, round(0.02 * len(x)))
    return (f"{len(x)} copies ({int((f & A).sum())} / {int((f & ~A).sum())}) | {x.sum():+.4f} ETH ({100 * x.mean() / STAKE:+.1f}% a copy) | halves {x[A[f]].sum():+.4f} / {x[~A[f]].sum():+.4f}"
            f" | w/o 2% {np.sort(x)[:-k].sum():+.4f} | won {100 * np.mean(x > 0):.0f}% | P(mean>0) {100 * np.mean(bs > 0):.1f}%")
print(f"\nsettings making money on both halves: {int(np.nansum((M1 > 0) & (M2 > 0))):,} of {int(ok.sum()):,} with {MINN}+ copies a half")
print(f"\nTHE CHOICE (the best neighbourhood by the weaker half without its best 2%):\n   {name(idx)}\n   {stats(idx)}")
raw = np.unravel_index(int(np.nanargmax(np.where(ok, weak, -np.inf))), weak.shape); print(f"\nthe single best (no smoothing): {name(raw)}\n   {stats(raw)}")
for lab, P_, Q_ in (("picked on the OLDER half, scored on the newer", S1, S2), ("picked on the NEWER half, scored on the older", S2, S1)):
    h = np.unravel_index(int(np.nanargmax(np.where(ok, P_, -np.inf))), P_.shape); rk = int(np.sum(np.where(ok, Q_, -np.inf) > Q_[h])) + 1
    print(f"\n{lab}: {name(h)}\n   {stats(h)}\n   its rank on the other half: {rk:,} of {int(ok.sum()):,}")
labels = [("its buy size", [f"{x}+" for x in SIZES]), ("coin type (ETH in the curve at its buy)", [p[0] for p in PROG]), ("price limit", ["1.1x", "1.25x", "1.5x", "none"]),
          ("take profit", [("none" if x > 1e8 else f"{x}x") for x in TP]), ("time", [f"{x}s" for x in HOLD]), ("sell pressure", ["off"] + [f"{n}/{w}s" for n, w in SPS[1:]]),
          ("stall", ["off"] + [f"{x}s" for x in STALL[1:]]), ("its sale", ITS)]
print("\nEACH PART VARIED ALONE (the others as chosen): a copy half 1 / half 2 | ETH all | w/o 2% ETH half 1 / half 2")
for d, (lab, vals) in enumerate(labels):
    print(f"  {lab}:")
    for j, vl in enumerate(vals):
        ix = list(idx); ix[d] = j; ix = tuple(ix)
        if np.isnan(SA[ix]): print(f"     {vl:9s} too few copies"); continue
        print(f"     {vl:9s} {100 * M1[ix] / STAKE:+6.1f}% / {100 * M2[ix] / STAKE:+6.1f}% | {SA[ix]:+.4f} | {S1[ix]:+.4f} / {S2[ix]:+.4f}  (copies {NN[ix[:3]]}){'   <- chosen' if j == idx[d] else ''}")
print("\nWHAT EACH SIZE BAND AND COIN TYPE ADDS ALONE (the chosen exit and limit): copies | a copy half 1 / half 2 | ETH")
X = VP[PMS[idx[2]]][(slice(None),) + tuple(idx[3:])]
for j, sz in enumerate(SIZES):
    hi = SIZES[j + 1] if j + 1 < len(SIZES) else 1e9; f = (SZ >= sz) & (SZ < hi)
    if f.sum() >= 5: print(f"     buy [{sz}, {hi if hi < 1e8 else 'up'}): {f.sum():4d} | {100 * X[f & A].mean() / STAKE if (f & A).any() else 0:+6.1f}% / {100 * X[f & ~A].mean() / STAKE if (f & ~A).any() else 0:+6.1f}% | {X[f].sum():+.4f}")
for lab, lo, hi in PROG[1:]:
    f = (PG >= lo) & (PG < hi)
    if f.sum() >= 5: print(f"     coin {lab:8s}: {f.sum():4d} | {100 * X[f & A].mean() / STAKE if (f & A).any() else 0:+6.1f}% / {100 * X[f & ~A].mean() / STAKE if (f & ~A).any() else 0:+6.1f}% | {X[f].sum():+.4f}")
