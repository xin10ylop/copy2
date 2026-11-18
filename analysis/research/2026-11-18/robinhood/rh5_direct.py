# The direct screen on Robinhood Chain's Pons (Nov 18; the owner: "keep digging"): OUR copy of EVERY wallet with
# MINC+ first buys of MINQ+ ETH on ETH-quoted curves (rh4's curve model and landings), under four exits fixed before
# looking (wallet 4's live exit; its sale followed with tp 4; tp 2 in 120 s; held 600 s with no tp, sell pressure or
# stall), price limit 1.5x. PICK on the newer half, SCORE on the older half (SPLIT): a wallet passes when an exit makes
# money on both halves and the older half's copies make money without their best 2%. Then rh4 engineers the passers.
#   python3 -I rh5_direct.py DIR > out/rh5_direct.txt   (MINC=20 MINQ=0.05 STAKE=0.02 GAS=0.00004 SPLIT=unix)
import sys, os, collections, numpy as np, datetime as dt
from multiprocessing import Pool
here = os.path.dirname(os.path.abspath(__file__)); D = sys.argv[1]; MINC = int(os.environ.get("MINC", 20))
src = open(os.path.join(here, "rh4_copy.py")).read().split("for W in WS:")[0]
sys.argv = ["x", D, "0x0"]; exec(src)
EXITS = [("wallet 4's live exit", (TP.index(4), HOLD.index(600), SPS.index((5, 60)), STALL.index(180), ITS.index("early"))),
         ("its sale followed, tp 4", (TP.index(4), HOLD.index(600), SPS.index((5, 60)), STALL.index(180), ITS.index("always"))),
         ("tp 2 in 120 s", (TP.index(2), HOLD.index(120), 0, 0, 0)), ("held 600 s, no tp", (TP.index(1e9), HOLD.index(600), 0, 0, 0))]
ETHC = [c for c in L if c in TR]
firsts = collections.defaultdict(list)          # wallet -> [(curve, index of its first buy)]
PATHS = {}
for c in ETHC:
    tr = path(c); PATHS[c] = tr; seen = set()
    for j, e in enumerate(tr):
        if e["buy"] and e["user"] not in seen:
            seen.add(e["user"])
            if e["q"] / 1e9 >= MINQ and tr[-1]["t"] - e["t"] >= 600: firsts[e["user"]].append((c, j))
cand = {u: v for u, v in firsts.items() if len(v) >= MINC}
print(f"{len(ETHC)} ETH-quoted curves, {len(firsts)} wallets with a copyable first buy, {len(cand)} with {MINC}+")
def score(u):
    out = []
    for c, k in cand[u]:
        tr = PATHS[c]; ps = [H.prep(tr, k, RATE, n, pmax=1000) for n in (4, 8, "slot+1")]
        v = []
        for p in ps:
            p["rate"] = RATE; prem = (tr[k]["vt"] / p["ent"][0]) ** 2
            cv = copy_vals(p); v.append([(cv[ix] - COST) if prem <= 1.5 else -0.0004 for _, ix in EXITS])
        out.append((tr[k]["t"], np.mean(v, axis=0) / RATE))
    return u, out
with Pool(4) as pool: R = dict(pool.map(score, list(cand), chunksize=8))
SPLIT = float(os.environ["SPLIT"]) if os.environ.get("SPLIT") else np.median([t for v in R.values() for t, _ in v])
print(f"halves at {dt.datetime.fromtimestamp(SPLIT, dt.UTC):%m-%d %H:%M} UTC (older = score, newer = pick); our {STAKE} ETH a copy")
res = []
for u, v in R.items():
    T_ = np.array([t for t, _ in v]); X = np.array([x for _, x in v]); old, new = T_ < SPLIT, T_ >= SPLIT
    if old.sum() < 10 or new.sum() < 10: continue
    for e, (lab, _) in enumerate(EXITS):
        xo, xn = X[old, e], X[new, e]; k = max(1, round(0.02 * len(xo)))
        res.append(dict(u=u, ex=lab, n_old=int(old.sum()), n_new=int(new.sum()), new=xn.sum(), old=xo.sum(), old2=np.sort(xo)[:-k].sum(), pct_old=100 * xo.mean() / STAKE, pct_new=100 * xn.mean() / STAKE))
picked = [r for r in res if r["new"] > 0]; passed = [r for r in picked if r["old"] > 0 and r["old2"] > 0]
print(f"wallets with 10+ copies in each half: {len({r['u'] for r in res})}; (wallet, exit) pairs making money on the newer half: {len(picked)}; also on the older half without its best 2%: {len(passed)}")
print("\nPASSED (picked on the newer half, scored on the older), by the older half without its best 2%:")
for r in sorted(passed, key=lambda r: -r["old2"])[:30]:
    print(f"   {r['u']}  {r['ex']:24s} newer {r['n_new']:4d} copies {r['new']:+.4f} ETH ({r['pct_new']:+5.1f}%) | older {r['n_old']:4d} copies {r['old']:+.4f} ({r['pct_old']:+5.1f}%), w/o 2% {r['old2']:+.4f}")
print("\nFOR SCALE, the 10 best on the newer half that failed the older:")
for r in sorted([r for r in picked if r not in passed], key=lambda r: -r["new"])[:10]:
    print(f"   {r['u']}  {r['ex']:24s} newer {r['new']:+.4f} ({r['pct_new']:+5.1f}%) | older {r['old']:+.4f} ({r['pct_old']:+5.1f}%), w/o 2% {r['old2']:+.4f}")
