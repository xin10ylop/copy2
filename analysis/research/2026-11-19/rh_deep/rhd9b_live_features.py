# The live trades (Nov 19) with the coin's volume and holders at the leader's buy and 60 s after it, against our result
# (journal) and the model's (rhd6). For reading, not for picking: 16 trades decide nothing.
#   python3 -I rhd9b_live_features.py DIR > out/rhd9b_live_features.txt
import sys, os, collections, numpy as np
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
DATA = R.Data(sys.argv[1]); ME = "0x35bb5c55a531d14213380fd978a501f0e239a77e"
L = {1: "0x9a3955a122ab8a649a8511df2dce169471fd0ec1", 2: "0x5bc235acecff3dde394f4bfc696f7c35efd502f0", 3: "0xc54d3914f91f984d61b63d491f38934c4e706b79"}
J = {1: (1, "0x5b0e4f50", 5.3), 2: (3, "0xadd10db6", -2.3), 3: (1, "0x69bae698", -25.4), 4: (3, "0x3a227ce5", -24.6), 5: (2, "0x11efe1a6", -13.3), 6: (3, "0x4196e3bb", -23.4),
     8: (2, "0xc6664449", 83.5), 9: (2, "0x2ff7d4b7", -25.7), 10: (2, "0x69453a1c", -15.2), 11: (1, "0xc983a044", -36.7), 12: (2, "0x4ff3da98", -22.3), 13: (1, "0xca5c7f4b", -15.9),
     14: (2, "0x7bf345a4", -39.4), 15: (1, "0xfc961f3d", -26.8), 16: (2, "0x3a50027d", -24.4)}
cv_of = {c[:10]: c for c in DATA.TR}
def state(tr, upto_t):
    bal = collections.defaultdict(float); vol = 0.0; n = 0
    for e in tr:
        if e["t"] > upto_t: break
        bal[e["user"]] += e["tok"] if e["buy"] else -e["tok"]; vol += e["q"] / 1e9; n += 1
    return sum(1 for v in bal.values() if v > 1.0), vol, n
print(f"{'#':>2} {'w':>1} {'coin':10s} {'age at its buy':>14s} | {'holders / ETH traded / trades at its buy':>40s} | {'60 s after':>26s} | {'live':>7s}")
for i, (w, c10, live) in J.items():
    cv = cv_of.get(c10)
    if not cv: print(f"{i:>2} {w} {c10}: not in the data"); continue
    tr = DATA.path(cv); k = next((j for j, e in enumerate(tr) if e["user"] == L[w] and e["buy"]), None)
    if k is None: print(f"{i:>2} {w} {c10}: its buy not found"); continue
    h0, v0, n0 = state(tr, tr[k]["t"] - 1e-6); h1, v1, n1 = state(tr, tr[k]["t"] + 60)
    print(f"{i:>2} {w} {c10} {tr[k]['t'] - tr[0]['t']:12.1f} s | {h0:12d} {v0:12.4f} {n0:12d} | {h1:7d} {v1:9.4f} {n1:7d} | {live:+6.1f}%")
