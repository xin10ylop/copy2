# What each copied wallet buys that its unit does not copy, by the rule that stops it (Nov 26; the owner: "check each one
# the coins we dont copy either by size or floats or sol or 3 step routes"). ../../2026-11-24/uncopied/u1_groups.py with
# the units as they run since the router fix (b90c446): a buy is valued whatever it pays with, so a coin priced in a token
# is copied when a route reaches that token: the token is wrapped SOL or a float, or a PumpSwap pool joins it to one
# (quote_route example, ROUTES file). Each coin goes in one group by the wallet's FIRST buy of it: COPIED, else the first
# rule it fails: priced in a token no route reaches, a SOL coin (the token-only units), its buy under MIN (0.25-MIN and
# under 0.25). Per group: the wallet's own result on the coins it sold out of (its sales minus its buys; token quotes at
# Jupiter's price now), coins, days up. Curve trades only (its PumpSwap buys are not in these histories).
#   python3 -I u3_groups.py UNITKIND MIN_SOL WALLET ROUTES HIST_DIR       (UNITKIND: all | token)
import sys, json, glob, collections, urllib.request, datetime as dt, numpy as np
KIND, MIN, W, ROUTES, D = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
T_MIN = float(__import__("os").environ.get("T_MIN", 0))   # first buys after this time only (Nov 26: 3SiQo8MJ since Nov 25)
SOLM = "So11111111111111111111111111111111111111112"
ROUTE = {l.split()[0]: " ".join(l.split()[1:]) for l in open(ROUTES) if l.strip()}
NAMES = {"3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh": "WBTC", "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn": "PUMP",
         "SPCXxcqXj6e5dJDVNovHN8744zkbhM2bYudU45BimGb": "SPCX", "TTWofwAge91oFhZs7kpQdyrVRkmevgM88xijGvQFbKo": "TTWO",
         "he1iusmfkpAdwvxLNGV8Y1iSbj4rUy6yMhEA3fotn9A": "hSOL", "98kfF7rmsg1QDUEoCqNE7g7M1FdrTt92TEp2CLzypump": "PAID",
         "Xsc9qvGR1efVDFGLrVsmkzv3qi45LTBjeUKSPmx9qEh": "NVDAx", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC"}
seen, trades = set(), []
for f in glob.glob(f"{D}/*_trades.jsonl"):
    for l in open(f):
        for e in json.loads(l)["trades"] or []:
            k = (e["m"], e["slot"], e["buy"], e["q"], e["tok"])
            if k not in seen: seen.add(k); trades.append(e)
issol = lambda q: not q or q.startswith("1111")
qs = sorted({e["quote"] for e in trades if not issol(e["quote"])})
P = {}
for i in range(0, len(qs), 40):
    for a in range(5):   # retried: a refused batch left a float's coins (3SiQo8MJ's 210 TTWO coins) "unpriced"
        try: P.update({k: v for k, v in json.load(urllib.request.urlopen("https://lite-api.jup.ag/price/v3?ids=" + ",".join(qs[i:i + 40] + [SOLM]), timeout=20)).items() if v}); break
        except Exception: __import__("time").sleep(3 * (a + 1))
su = (P.get(SOLM) or {}).get("usdPrice")
def rate(q):
    if issol(q): return 1.0
    v = P.get(q) or {}
    return v["usdPrice"] / su * 1e9 / 10 ** v["decimals"] if su and v.get("usdPrice") and v.get("decimals") is not None else None
by = collections.defaultdict(list)
for e in trades: by[e["m"]].append(e)
G = collections.defaultdict(list); unpriced = 0; holding = 0; noroute_tok = collections.Counter(); copied_how = collections.Counter()
for m, es in by.items():
    es.sort(key=lambda e: (e["slot"], not e["buy"]))
    if not es[0]["buy"] or es[0]["t"] < T_MIN: continue
    q = es[0]["quote"]; r = rate(q)
    if r is None: unpriced += 1; continue
    tin = sum(e["tok"] for e in es if e["buy"]); tout = sum(e["tok"] for e in es if not e["buy"])
    if tout < 0.99 * tin: holding += 1; continue
    own = sum((e["q"] if not e["buy"] else -e["q"]) * rate(e["quote"]) / 1e9 for e in es if rate(e["quote"]))
    size = es[0]["q"] * r / 1e9; sol_coin = issol(q); how = "SOL" if sol_coin else ROUTE.get(q, "none")
    if not sol_coin and how == "none": g = "token coin, no route to its token"; noroute_tok[NAMES.get(q, q[:8])] += 1
    elif KIND == "token" and sol_coin: g = "SOL coin (the unit takes token coins)"
    elif size < 0.25: g = "its buy under 0.25 SOL"
    elif size < MIN: g = f"its buy 0.25-{MIN} SOL"
    else:
        g = "COPIED by the unit"
        if __import__("os").environ.get("LIST"): print("   copied", __import__("time").strftime("%m-%d %H:%M", __import__("time").gmtime(es[0]["t"])), m[:8], f"{size:.2f} SOL", f"own {own:+.3f}")
        copied_how["SOL coin" if sol_coin else "float/anchor" if how == "anchor" else "pool+curve (a hop more)"] += 1
    G[g].append((dt.datetime.fromtimestamp(es[0]["t"], dt.UTC).strftime("%m-%d"), own, size))
alld = sorted({d for v in G.values() for d, _, _ in v})
print(f"{W[:8]} (unit: {KIND} coins, {MIN}+ SOL): {sum(len(v) for v in G.values())} coins sold out, {alld[0]} to {alld[-1]} UTC; "
      f"{unpriced} in unpriced tokens and {holding} still held left out")
print(f"  {'group':40s} {'coins':>6s} {'own SOL':>9s} {'a coin':>7s} {'days up':>8s}")
for g in sorted(G, key=lambda g: (g != "COPIED by the unit", g)):
    v = G[g]; own = np.array([x[1] for x in v]); days = collections.defaultdict(float)
    for d, o, _ in v: days[d] += o
    print(f"  {g:40s} {len(v):6d} {own.sum():+9.2f} {own.mean():+7.3f} {sum(1 for x in days.values() if x > 0):3d} of {len(days):<3d}")
if copied_how: print("  copied, by route: " + ", ".join(f"{k} {n}" for k, n in copied_how.most_common()))
if noroute_tok: print("  tokens no route reaches: " + ", ".join(f"{k} {n}" for k, n in noroute_tok.most_common(6)))
