# Pons V2's curve math from its own trades (Nov 18). Hypothesis: a constant product on virtual reserves (as pump.fun),
# k = (V0 + Q)(T0 - S) with Q the net quote in and S the tokens sold; the docs fix 5/7 of 1B sold when Q reaches the
# 4.2 ETH threshold, so T0 = 714,285,714 * (V0 + 4.2) / 4.2 and only V0 is free. Grid over V0, two fee readings, error
# of each buy's predicted tokens out, on curves whose launch and every trade are in the data.
import sys, json, gzip, glob, numpy as np
D = sys.argv[1]; T = json.load(open(f"{D}/topics.json")); FACTORY = "0x7ed598bcef8bd9edd8c97a195c6d13f40801ec7e"
words = lambda d: [int(d[2 + 64 * i: 2 + 64 * (i + 1)], 16) for i in range((len(d) - 2) // 64)]
L, TR = {}, {}
for f in glob.glob(f"{D}/logs_*.json.gz"):
    for l in json.load(gzip.open(f)):
        t0 = l["topics"][0]
        if t0 == T["TokenLaunched"] and l["address"].lower() == FACTORY:
            w = words(l["data"])
            if len(w) >= 3 and w[0] == 0: L["0x" + l["topics"][2][-40:]] = int(l["blockNumber"], 16)
        elif t0 in (T["CurveBuy"], T["CurveSell"]):
            w = words(l["data"]); TR.setdefault(l["address"].lower(), []).append((int(l["blockNumber"], 16), int(l["logIndex"], 16), t0 == T["CurveBuy"], w))
cs = [c for c in L if c in TR][:300]; print(len(L), "ETH launches;", len(cs), "curves used")
SOLD = 1e9 * 5 / 7
for fee_mode in ("quoteIn includes the fee", "quoteIn excludes the fee"):
    best = None
    for V0 in np.concatenate([np.arange(0.2, 3, 0.05), np.arange(3, 12, 0.25)]):
        T0 = SOLD * (V0 + 4.2) / 4.2; err = []
        for c in cs:
            Q = S = 0.0
            for n, i, buy, w in sorted(TR[c])[:40]:
                if buy:
                    q = (w[0] - w[2]) / 1e18 if fee_mode.endswith("includes the fee") else w[0] / 1e18
                    pred = (T0 - S) - (T0 - S) * (V0 + Q) / (V0 + Q + q); got = w[1] / 1e18
                    if got > 0: err.append(abs(pred / got - 1))
                    Q += q; S += got
                else:
                    S -= w[0] / 1e18; Q -= (w[1] + w[2]) / 1e18 if fee_mode.endswith("includes the fee") else w[1] / 1e18
        e = float(np.median(err))
        if best is None or e < best[0]: best = (e, V0, T0, len(err))
    print(f"{fee_mode}: best V0 {best[1]:.2f} ETH, T0 {best[2]:,.0f}, median error of tokens out {100 * best[0]:.3f}% on {best[3]} buys")
