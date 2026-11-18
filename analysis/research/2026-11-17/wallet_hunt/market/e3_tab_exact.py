# TAB16RxX under the exact config to deploy (Nov 18): hunt_lib's live model (wallet 4's live exits: tp 4.0, 600 s,
# sell pressure [5, 60, 30], stall 180 s once back at our fill) with its sale never followed (early=None), against
# the live model as it is (its sale followed 30-290 s under 1.5x). All its 0.5+ SOL first buys on the 4 days of
# float-quote coins, 0.5 SOL, the mean of the three landings, 0.0345 SOL a round trip; days 1-2 / 3-4 at Nov 16 01:07 UTC.
#   python3 -I e3_tab_exact.py SP LAUNCHES,... > ../out/e3_tab_exact.txt
import sys, os, json, gzip, numpy as np
SP = sys.argv[1]; O = f"{SP}/market"; PD = f"{O}/paths_full"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); import hunt_lib as H
TAB = "TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3"; WSOL = "So11111111111111111111111111111111111111112"; COST = 0.0345 - 0.0026; MID = 1794791222
FLOATS = ("3NZ9JMVB", "pumpCmXq", "SPCXxcqX", "TTWofwAg", "DJTu7vi8", "98sMhvDw", "XsbEhLAt"); L = {}
for f_ in sys.argv[2].split(","): L.update({m: x for m, x in json.load(open(f_)).items() if x and x["quote"][:8] in FLOATS and os.path.exists(f"{PD}/{m}.json.gz")})
PR = json.load(open(f"{O}/prices.json")); su = PR[WSOL]["usdPrice"]; rate = lambda q: PR[q]["usdPrice"] / su * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None
R = []
for m, x in L.items():
    r = rate(x["quote"]); tr = json.load(gzip.open(f"{PD}/{m}.json.gz")) if r else []
    i = next((j for j, e in enumerate(tr) if e["user"] == TAB), None)
    if i is None or not tr[i]["buy"] or tr[i]["q"] * (1 + tr[i]["bps"] / 1e4) * r / 1e9 < 0.5 or tr[-1]["t"] - tr[i]["t"] < 600: continue
    a = np.mean([H.model(H.prep(tr, i, r, n), early=None)[0] for n in (4, 8, "slot+1")]) - COST
    b = np.mean([H.model(H.prep(tr, i, r, n))[0] for n in (4, 8, "slot+1")]) - COST
    R.append((tr[i]["t"], a, b, x["quote"][:8]))
def S(v):
    v = np.array(v); n = len(v); s = np.sort(v); k = max(1, round(0.02 * n)); bs = np.random.default_rng(7).choice(v, size=(10000, n)).mean(axis=1)
    return f"{n:3d} {v.sum():+6.2f} SOL ({100 * v.mean() / 0.5:+6.1f}% a copy) w/o 2% {s[:-k].sum():+6.2f} | won {100 * np.mean(v > 0):3.0f}% | P(mean>0) {100 * np.mean(bs > 0):5.1f}%"
for j, name in ((1, "TO DEPLOY: live exits, its sale never followed"), (2, "the live model as it is (its sale followed 30-290 s)")):
    print(f"{name}:")
    print(f"   days 1-2: {S([z[j] for z in R if z[0] < MID])}")
    print(f"   days 3-4: {S([z[j] for z in R if z[0] >= MID])}")
    print(f"   all 4:    {S([z[j] for z in R])}")
import collections; print("quotes:", collections.Counter(z[3] for z in R).most_common())
