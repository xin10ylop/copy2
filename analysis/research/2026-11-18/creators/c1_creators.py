# How does wallet 4 choose? Hypothesis 1 (Nov 18): it follows creators. On the 48 h of other-token launches fetched in
# full (SP/market/paths_full, true in-slot order), a launch buy on every coin: our 0.5 SOL at the first trade after the
# create slot (hunt_lib prep "slot+1" from the create slot's last trade, no price refusal), wallet 4's live model, 0.0345
# SOL a round trip. Then by the coin's creator: (a) coins wallet 4 bought (1.3+ SOL), (b) coins of a creator wallet 4
# bought BEFORE this launch that wallet 4 did not buy, (c) every other coin. If (b) makes money, following wallet 4's
# creators multiplies its edge.
#   python3 -I c1_creators.py SP > out/c1_creators.txt
import sys, os, json, gzip, glob, collections, numpy as np
from multiprocessing import Pool
SP = sys.argv[1]; O = f"{SP}/market"; PD = f"{O}/paths_full"
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt"); import hunt_lib as H
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; WSOL = "So11111111111111111111111111111111111111112"
L = {m: x for m, x in json.load(open(f"{O}/launches.json")).items() if x and os.path.exists(f"{PD}/{m}.json.gz")}
PR = json.load(open(f"{O}/prices.json")); sol_usd = PR[WSOL]["usdPrice"]
rate_of = lambda q: PR[q]["usdPrice"] / sol_usd * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None
COST = 0.0345 - 0.0026
def one(m):
    x = L[m]; r = rate_of(x["quote"])
    if r is None: return None
    try: tr = json.load(gzip.open(f"{PD}/{m}.json.gz"))
    except Exception: return None
    if len(tr) < 3: return None
    s0 = x["slot"]; k = max((j for j, e in enumerate(tr) if e["slot"] <= s0), default=None)
    if k is None or tr[-1]["t"] - tr[k]["t"] < 300: return None
    p = H.prep(tr, k, r, "slot+1", pmax=1000)
    v = H.model(p, early=None)[0] - COST if not p["refused"] else None   # no "its sale" at a launch buy (the Nov 18 fix: a random trader's sale was followed)
    w4 = [e for e in tr if e["user"] == W4 and e["buy"]]
    w4sol = (w4[0]["q"] * (1 + w4[0]["bps"] / 1e4) * r / 1e9) if w4 else 0
    return m, x["creator"], x["t"], v, w4sol
if __name__ == "__main__":
    with Pool(8) as P: R = [z for z in P.map(one, sorted(L), chunksize=20) if z and z[3] is not None]
    R.sort(key=lambda z: z[2]); seen_cr = set(); A, Bc, C = [], [], []
    for m, cr, t, v, w4sol in R:
        if w4sol >= 1.3: A.append(v)
        elif cr in seen_cr: Bc.append(v)
        else: C.append(v)
        if w4sol >= 1.3: seen_cr.add(cr)
    def S(v):
        v = np.array(v); n = len(v)
        if not n: return "  0"
        s = np.sort(v); k = max(1, round(0.02 * n)); bs = np.random.default_rng(7).choice(v, size=(5000, n)).mean(axis=1)
        return f"{n:5d} {v.sum():+8.2f} SOL ({100 * v.mean() / 0.5:+6.1f}% a buy) w/o 2% {s[:-k].sum():+8.2f} | won {100 * np.mean(v > 0):3.0f}% | P(mean>0) {100 * np.mean(bs > 0):5.1f}%"
    cc = collections.Counter(cr for m, cr, t, v, w in R)
    print(f"{len(R)} coins with a launch buy modelled; {len(cc)} creators ({sum(1 for c in cc.values() if c >= 2)} with 2+ coins in the 48 h)")
    print(f"(a) coins wallet 4 bought (1.3+ SOL), our buy at launch:      {S(A)}")
    print(f"(b) later coins of creators wallet 4 had bought, it skipped: {S(Bc)}")
    print(f"(c) every other coin:                                         {S(C)}")
    print(f"wallet 4's coins whose creator made 2+ coins in the 48 h: {sum(1 for m, cr, t, v, w in R if w >= 1.3 and cc[cr] >= 2)} of {len(A)}")
