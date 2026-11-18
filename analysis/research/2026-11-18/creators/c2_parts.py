# Which part of wallet 4 carries the edge (Nov 18)? Its 1.3+ SOL buys on the 48 h fetched in full, our 0.5 SOL copy
# three ways, wallet 4's live model and 0.0345 SOL a round trip: (1) the live copy (land after ITS buy, follow ITS early
# sale), (2) the same landing, its sale never followed (early=None), (3) a buy at the launch (first trade after the
# create slot) with its sale followed. (1) vs (2): the value of its sale; (1) vs (3): the value of its moment.
#   python3 -I c2_parts.py SP > out/c2_parts.txt
import sys, os, json, gzip, numpy as np
SP = sys.argv[1]; O = f"{SP}/market"; PD = f"{O}/paths_full"
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt"); import hunt_lib as H
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; WSOL = "So11111111111111111111111111111111111111112"; COST = 0.0345 - 0.0026
L = {m: x for m, x in json.load(open(f"{O}/launches.json")).items() if x and os.path.exists(f"{PD}/{m}.json.gz")}
PR = json.load(open(f"{O}/prices.json")); sol_usd = PR[WSOL]["usdPrice"]
rate_of = lambda q: PR[q]["usdPrice"] / sol_usd * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None
R = []
for m, x in L.items():
    r = rate_of(x["quote"])
    if r is None: continue
    tr = json.load(gzip.open(f"{PD}/{m}.json.gz")); k = next((j for j, e in enumerate(tr) if e["user"] == W4 and e["buy"]), None)
    if k is None or tr[k]["q"] * (1 + tr[k]["bps"] / 1e4) * r / 1e9 < 1.3 or tr[-1]["t"] - tr[k]["t"] < 600: continue
    a = np.mean([H.model(H.prep(tr, k, r, n))[0] for n in (4, 8, "slot+1")]) - COST
    b = np.mean([H.model(H.prep(tr, k, r, n), early=None)[0] for n in (4, 8, "slot+1")]) - COST
    s0 = x["slot"]; kl = max(j for j, e in enumerate(tr) if e["slot"] <= s0)
    pl = H.prep(tr, kl, r, "slot+1", pmax=1000); n_ = len(pl["px"]); pl["sell"] = np.array([e["user"] == W4 and not e["buy"] for e in tr[len(tr) - n_:]], dtype=bool) if n_ else pl["sell"]   # wallet 4's sale on the launch path
    c = H.model(pl)[0] - COST if not pl["refused"] else 0
    R.append((a, b, c, k - kl))
A = np.array(R)
for i, name in enumerate(("(1) copy, its sale followed (live)", "(2) copy, its sale never followed", "(3) buy at launch, its sale followed")):
    v = A[:, i]; k2 = max(1, round(0.02 * len(v))); print(f"{name:40s}: {len(v)} {v.sum():+6.2f} SOL ({100 * v.mean() / 0.5:+6.1f}% a copy) w/o 2% {np.sort(v)[:-k2].sum():+6.2f}")
print(f"trades between the launch slot's end and wallet 4's buy: median {np.median(A[:, 3]):.0f}")
