# What each copied wallet trades that its unit does not copy, and whether it makes money there (Nov 24; the owner: "for
# the remaining wallets, check if they are taking other trades that we don't take and making them money, except qqq").
# Each wallet's trades from its histories (the 14-day fetch of Nov 23-24 and the 3-day fetch of Nov 24, merged). Each coin
# goes in one group by its FIRST buy, as the units judge it: what the unit copies (its buy of MIN_SOL+, paid with SOL or
# a float we hold, and the coin kind the unit takes), else the first rule it fails: a token we don't hold, a SOL coin (the
# token-only units), its buy under MIN_SOL. Per group: the wallet's own result on the coins it sold out of (its sales
# minus its buys, re-buys included; token quotes at Jupiter's price now), coins, days up, and by size of its first buy.
#   python3 -I u1_groups.py UNITKIND MIN_SOL WALLET HIST_DIR [HIST_DIR ...]       (UNITKIND: all | token | sol)
import sys, json, glob, collections, urllib.request, datetime as dt, numpy as np
KIND, MIN, W, DIRS = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4:]
SOLM = "So11111111111111111111111111111111111111112"
FLOATS = {"3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh": "WBTC", "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn": "PUMP",
          "SPCXxcqXj6e5dJDVNovHN8744zkbhM2bYudU45BimGb": "SPCX", "TTWofwAge91oFhZs7kpQdyrVRkmevgM88xijGvQFbKo": "TTWO",
          "he1iusmfkpAdwvxLNGV8Y1iSbj4rUy6yMhEA3fotn9A": "hSOL", "98kfF7rmsg1QDUEoCqNE7g7M1FdrTt92TEp2CLzypump": "PAID",
          "Xsc9qvGR1efVDFGLrVsmkzv3qi45LTBjeUKSPmx9qEh": "NVDAx"}
seen, trades = set(), []
for d in DIRS:
    for f in glob.glob(f"{d}/*_trades.jsonl"):
        for l in open(f):
            for e in json.loads(l)["trades"] or []:
                k = (e["m"], e["slot"], e["buy"], e["q"], e["tok"])
                if k not in seen: seen.add(k); trades.append(e)
issol = lambda q: not q or q.startswith("1111")
qs = sorted({e["quote"] for e in trades if not issol(e["quote"])})
P = {}
for i in range(0, len(qs), 40):
    try: P.update({k: v for k, v in json.load(urllib.request.urlopen("https://lite-api.jup.ag/price/v3?ids=" + ",".join(qs[i:i + 40] + [SOLM]), timeout=20)).items() if v})
    except Exception: pass
su = (P.get(SOLM) or {}).get("usdPrice")
def rate(q):
    if issol(q): return 1.0
    v = P.get(q) or {}
    return v["usdPrice"] / su * 1e9 / 10 ** v["decimals"] if su and v.get("usdPrice") and v.get("decimals") is not None else None
by = collections.defaultdict(list)
for e in trades: by[e["m"]].append(e)
G = collections.defaultdict(list)                         # group -> [(day, own SOL, first-buy SOL)]
unpriced = 0
for m, es in by.items():
    es.sort(key=lambda e: (e["slot"], not e["buy"]))
    if not es[0]["buy"]: continue
    q = es[0]["quote"]; r = rate(q)
    if r is None: unpriced += 1; continue
    tin = sum(e["tok"] for e in es if e["buy"]); tout = sum(e["tok"] for e in es if not e["buy"])
    if tout < 0.99 * tin: continue                         # still holding: no result yet
    own = sum((e["q"] if not e["buy"] else -e["q"]) * rate(e["quote"]) / 1e9 for e in es if rate(e["quote"]))
    size = es[0]["q"] * r / 1e9; sol_coin = issol(q)
    if not sol_coin and q not in FLOATS: g = "a token we don't hold"
    elif KIND == "token" and sol_coin: g = "SOL coins (the unit takes token coins)"
    elif KIND == "sol" and not sol_coin: g = "token coins (the unit takes SOL coins)"
    elif size < MIN: g = f"its buy under {MIN} SOL"
    else: g = "COPIED by the unit"
    G[g].append((dt.datetime.fromtimestamp(es[0]["t"], dt.UTC).strftime("%m-%d"), own, size))
alld = sorted({d for v in G.values() for d, _, _ in v})
print(f"{W[:8]} ({KIND} coins, {MIN}+ SOL): {sum(len(v) for v in G.values())} coins sold out, {alld[0]} to {alld[-1]} UTC; {unpriced} coins in unpriced tokens left out")
print(f"  {'group':42s} {'coins':>6s} {'own SOL':>9s} {'a coin':>7s} {'days up':>8s}   by its first buy: under 0.25 | 0.25-0.5 | 0.5-1.3 | 1.3+ (coins, SOL)")
for g in sorted(G, key=lambda g: (g != "COPIED by the unit", g)):
    v = G[g]; own = np.array([x[1] for x in v]); days = collections.defaultdict(float)
    for d, o, _ in v: days[d] += o
    bands = []
    for lo, hi in ((0, 0.25), (0.25, 0.5), (0.5, 1.3), (1.3, 1e9)):
        b = [o for _, o, s in v if lo <= s < hi]; bands.append(f"{len(b)}, {sum(b):+.2f}" if b else "-")
    print(f"  {g:42s} {len(v):6d} {own.sum():+9.2f} {own.mean():+7.3f} {sum(1 for x in days.values() if x > 0):3d} of {len(days):<3d}   " + " | ".join(bands))
toks = collections.Counter()
for m, es in by.items():
    es.sort(key=lambda e: (e["slot"], not e["buy"]))
    if es[0]["buy"] and not issol(es[0]["quote"]) and es[0]["quote"] not in FLOATS: toks[es[0]["quote"][:8]] += 1
if toks: print("  tokens we don't hold, by its first buys: " + ", ".join(f"{k} {n}" for k, n in toks.most_common(6)))
