# How does wallet 4 choose? Step 2 (Nov 18): what is visible at the launch on the coins it buys (1.3+ SOL) against the
# rest of the 48 h of other-token launches (paths_full, true in-slot order). Per coin, from the create slot and the
# next: the quote token, the creator's own buy (SOL), buyers and SOL in the create slot (wallet 4 excluded), buyers and
# SOL in the next slot, the price at the create slot's end over the first trade. Medians and shares, no rule yet.
#   python3 -I c3_features.py SP > out/c3_features.txt
import sys, os, json, gzip, collections, numpy as np
SP = sys.argv[1]; O = f"{SP}/market"; PD = f"{O}/paths_full"
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; WSOL = "So11111111111111111111111111111111111111112"
L = {m: x for m, x in json.load(open(f"{O}/launches.json")).items() if x and os.path.exists(f"{PD}/{m}.json.gz")}
PR = json.load(open(f"{O}/prices.json")); sol_usd = PR[WSOL]["usdPrice"]
rate_of = lambda q: PR[q]["usdPrice"] / sol_usd * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None
F = []
for m, x in L.items():
    r = rate_of(x["quote"])
    if r is None: continue
    try: tr = json.load(gzip.open(f"{PD}/{m}.json.gz"))
    except Exception: continue
    if not tr: continue
    s0 = x["slot"]; sol = lambda e: e["q"] * (1 + e["bps"] / 1e4) * r / 1e9
    cs = [e for e in tr if e["slot"] == s0 and e["buy"]]; n1 = [e for e in tr if e["slot"] == s0 + 1 and e["buy"]]
    dev = sum(sol(e) for e in cs if e["user"] == x["creator"])
    w4 = next((e for e in tr if e["user"] == W4 and e["buy"]), None)
    oth = [e for e in cs if e["user"] not in (W4, x["creator"])]
    F.append(dict(m=m, w4=bool(w4 and sol(w4) >= 1.3), q=x["quote"][:8], dev=dev, nb0=len({e["user"] for e in oth}), sol0=sum(sol(e) for e in oth),
                  nb1=len({e["user"] for e in n1 if e["user"] != W4}), sol1=sum(sol(e) for e in n1 if e["user"] != W4)))
A = [f for f in F if f["w4"]]; Bf = [f for f in F if not f["w4"]]
print(f"{len(F)} coins; wallet 4 bought {len(A)} (1.3+ SOL)")
for k, name in (("dev", "creator's own buy, SOL"), ("nb0", "other buyers in the create slot"), ("sol0", "their SOL"), ("nb1", "buyers in the next slot"), ("sol1", "their SOL")):
    a = np.array([f[k] for f in A]); b = np.array([f[k] for f in Bf])
    print(f"   {name:34s}: wallet 4's coins median {np.median(a):6.2f} (quartiles {np.percentile(a, 25):.2f}-{np.percentile(a, 75):.2f}) | the rest median {np.median(b):6.2f} ({np.percentile(b, 25):.2f}-{np.percentile(b, 75):.2f})")
qa = collections.Counter(f["q"] for f in A); qb = collections.Counter(f["q"] for f in Bf)
print("   quote token: share of wallet 4's coins / of the rest:", [(q, f"{100 * qa[q] / len(A):.0f}% / {100 * qb[q] / len(Bf):.0f}%") for q, _ in qa.most_common(6)])
json.dump(F, open(f"{SP}/launch_features.json", "w"))
