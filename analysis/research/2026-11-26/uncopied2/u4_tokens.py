# The tokens no route reaches, over all ten wallets (Nov 26): the coins priced in each that a unit would copy if it held
# that token as a float (the wallet's first buy at its unit's MIN or more, the unit's coin kind), the wallets' own result
# on them, days up. With u3's sub-split of each not-copied group at the unit's MIN.
#   python3 -I u4_tokens.py ROUTES SP     (reads SP/hist26_<wallet>/)
import sys, json, glob, collections, urllib.request, datetime as dt
ROUTES, SP = sys.argv[1], sys.argv[2]
SOLM = "So11111111111111111111111111111111111111112"
ROUTE = {l.split()[0]: " ".join(l.split()[1:]) for l in open(ROUTES) if l.strip()}
UNITS = [("qqq", "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg", "token", 1.3), ("www", "CqCAzte8TwCDbCBrhjUpsfG6Au9pZPdrTXrVDidKHGAn", "all", 0.5),
         ("eee", "CgyPomTGt9BFqnjBdRS38BCBUZvtMJDf3aKQy8sMTVKX", "all", 0.5), ("rrr", "3XeFcZKSn8WzqoDAm5vvgbdfkU82rMmhJfp1q4LXtnX6", "token", 0.5),
         ("ttt", "6LwMLkCeEAqYp9Pv33ujrgd9uF987zPXdGKr9Z9sebh5", "token", 0.5), ("yyy", "6nNzEg86rbY4J1Z6euDn9iQoih8uaSj6ZVZHZVvFxjJf", "token", 0.5),
         ("uuu", "GqWfqfG6Mt6RL8BKUWiBkirqzycUc15bgZVtFERQzxJ8", "all", 0.5), ("iii", "Bing35WCqmhUwFBJ9xVNfMoNpECj8vdWEr5hD5wYyobc", "all", 0.5),
         ("ooo", "HtHkKxYN43BdJ8QJU1srMa3bqjpncLFcZgVCX8yU3AJS", "all", 0.5), ("ppp", "3SiQo8MJMzXaZcJexMivmk5CRgrNxDUh4bDbgb3wFAmW", "token", 0.5)]
issol = lambda q: not q or q.startswith("1111")
H = {}
for lab, W, kind, mn in UNITS:
    seen, tr = set(), []
    for l in open(f"{SP}/hist26_{W[:8]}/{W[:8]}_trades.jsonl"):
        for e in json.loads(l)["trades"] or []:
            k = (e["m"], e["slot"], e["buy"], e["q"], e["tok"])
            if k not in seen: seen.add(k); tr.append(e)
    H[lab] = (W, kind, mn, tr)
qs = sorted({e["quote"] for *_, tr in H.values() for e in tr if not issol(e["quote"])})
P = {}
for i in range(0, len(qs), 40):
    for a in range(5):   # retried: a refused batch left a float's coins (3SiQo8MJ's 210 TTWO coins) "unpriced"
        try: P.update({k: v for k, v in json.load(urllib.request.urlopen("https://lite-api.jup.ag/price/v3?ids=" + ",".join(qs[i:i + 40] + [SOLM]), timeout=20)).items() if v}); break
        except Exception: __import__("time").sleep(3 * (a + 1))
su = P[SOLM]["usdPrice"]
def rate(q):
    if issol(q): return 1.0
    v = P.get(q) or {}
    return v["usdPrice"] / su * 1e9 / 10 ** v["decimals"] if v.get("usdPrice") and v.get("decimals") is not None else None
tok = collections.defaultdict(lambda: dict(n=0, own=0.0, by=collections.Counter(), days=collections.defaultdict(float)))
sub = collections.defaultdict(lambda: [0, 0.0])
for lab, (W, kind, mn, tr) in H.items():
    by = collections.defaultdict(list)
    for e in tr: by[e["m"]].append(e)
    for m, es in by.items():
        es.sort(key=lambda e: (e["slot"], not e["buy"]))
        if not es[0]["buy"]: continue
        q = es[0]["quote"]; r = rate(q)
        if r is None: continue
        tin = sum(e["tok"] for e in es if e["buy"]); tout = sum(e["tok"] for e in es if not e["buy"])
        if tout < 0.99 * tin: continue
        own = sum((e["q"] if not e["buy"] else -e["q"]) * rate(e["quote"]) / 1e9 for e in es if rate(e["quote"]))
        size = es[0]["q"] * r / 1e9; sol = issol(q); how = "SOL" if sol else ROUTE.get(q, "none")
        big = size >= mn
        if not sol and how == "none":
            sub[(lab, "no route, at MIN+" if big else "no route, under MIN")][0] += 1; sub[(lab, "no route, at MIN+" if big else "no route, under MIN")][1] += own
            if big:
                t = tok[q]; t["n"] += 1; t["own"] += own; t["by"][lab] += 1
                t["days"][dt.datetime.fromtimestamp(es[0]["t"], dt.UTC).strftime("%m-%d")] += own
        elif kind == "token" and sol:
            k = (lab, "SOL coin, at MIN+" if big else "SOL coin, under MIN"); sub[k][0] += 1; sub[k][1] += own
print("not-copied groups at the unit's MIN or more (coins, the wallet's own SOL):")
for lab, *_ in UNITS:
    print(f"  {lab}: " + "   ".join(f"{g} {sub[(lab, g)][0]} ({sub[(lab, g)][1]:+.2f})" for g in ("no route, at MIN+", "SOL coin, at MIN+") if sub[(lab, g)][0]))
print("\nthe tokens no route reaches, by the coins our units would copy with it as a float (first buy at the unit's MIN+):")
names = {}
try:
    for q in [q for q, _ in sorted(tok.items(), key=lambda x: -x[1]["n"])[:15]]:
        j = json.load(urllib.request.urlopen(f"https://lite-api.jup.ag/tokens/v2/search?query={q}", timeout=20))
        if j: names[q] = j[0].get("symbol", "?")
except Exception: pass
for q, t in sorted(tok.items(), key=lambda x: -x[1]["n"])[:15]:
    up = sum(1 for v in t["days"].values() if v > 0)
    print(f"  {q[:8]} {names.get(q, '?'):10s} {t['n']:4d} coins  own {t['own']:+7.2f} SOL ({t['own'] / t['n']:+.3f} a coin)  days up {up} of {len(t['days'])}  by unit: " + ", ".join(f"{k} {v}" for k, v in t["by"].most_common()))
