# Per running unit, what pays for its wallet's buys over the last DAYS days (Nov 27; the owner: "any new floats to add?",
# then "check for each wallet"). Each coin is judged by the wallet's FIRST buy of it, at the unit's floor (min_sol) and in
# the unit's coin kind (token-only units skip SOL coins). The payment is SOL, a float we hold (copied), a token a PumpSwap
# pool joins to wSOL or a float (copied by the 3-hop route), or a token no route reaches (NOT copied: a float would open
# it). Per group: coins, the wallet's own result on the coins it sold out of (its sales minus its buys, token amounts at
# Jupiter's price now), days up. The no-route tokens are then ranked over all units.
#   python3 -I f1_wallets.py SP DAYS ROUTES [QUOTES_OUT]      (reads SP/histfl_<wallet8>/; QUOTES_OUT: write the quote
#   mints to check with quote_route PDAS_ONLY + ../../2026-11-26/uncopied2/u6_routes.py, then rerun with that ROUTES)
import sys, os, json, glob, time, collections, urllib.request, datetime as dt
SP, DAYS, ROUTES = sys.argv[1], float(sys.argv[2]), sys.argv[3]
QOUT = sys.argv[4] if len(sys.argv) > 4 else None
T0 = time.time() - DAYS * 86400
SOLM = "So11111111111111111111111111111111111111112"
FLOATS = {"3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh": "WBTC", "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn": "PUMP",
          "SPCXxcqXj6e5dJDVNovHN8744zkbhM2bYudU45BimGb": "SPCX", "TTWofwAge91oFhZs7kpQdyrVRkmevgM88xijGvQFbKo": "TTWO",
          "he1iusmfkpAdwvxLNGV8Y1iSbj4rUy6yMhEA3fotn9A": "hSOL", "98kfF7rmsg1QDUEoCqNE7g7M1FdrTt92TEp2CLzypump": "PAID",
          "Xsc9qvGR1efVDFGLrVsmkzv3qi45LTBjeUKSPmx9qEh": "NVDAx", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC",
          SOLM: "wSOL"}
# the units as they run on Nov 27 (config/*.live.example.toml: copy_wallet, min_sol, copy_sol_coins)
UNITS = [("qqq", "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg", "token", 1.3), ("eee", "CgyPomTGt9BFqnjBdRS38BCBUZvtMJDf3aKQy8sMTVKX", "all", 0.5),
         ("rrr", "3XeFcZKSn8WzqoDAm5vvgbdfkU82rMmhJfp1q4LXtnX6", "token", 0.5), ("ttt", "6LwMLkCeEAqYp9Pv33ujrgd9uF987zPXdGKr9Z9sebh5", "token", 0.5),
         ("yyy", "6nNzEg86rbY4J1Z6euDn9iQoih8uaSj6ZVZHZVvFxjJf", "token", 0.25), ("uuu", "GqWfqfG6Mt6RL8BKUWiBkirqzycUc15bgZVtFERQzxJ8", "all", 0.5),
         ("iii", "Bing35WCqmhUwFBJ9xVNfMoNpECj8vdWEr5hD5wYyobc", "all", 0.5), ("ooo", "HtHkKxYN43BdJ8QJU1srMa3bqjpncLFcZgVCX8yU3AJS", "all", 0.5),
         ("ppp", "3SiQo8MJMzXaZcJexMivmk5CRgrNxDUh4bDbgb3wFAmW", "token", 0.1), ("ddd", "E2XwSeqewRHqBZQZAnSn6NyC9pF17E9KWcFQzquUwZMi", "all", 0.5),
         ("fff", "E5CLHHz6R9ixCXr7Sh9ifwN1gxBNF6Cyoir6cTeDzA2M", "all", 0.5), ("hhh", "2GJUPUrkxs6RZfJCgRncf1Xq9Xe6MbuDynVaoiiPKoJ4", "all", 0.5)]
ROUTE = {l.split()[0]: " ".join(l.split()[1:]) for l in open(ROUTES) if l.strip()} if os.path.exists(ROUTES) else {}
issol = lambda q: not q or q.startswith("1111")
H = {}
for lab, W, kind, mn in UNITS:
    seen, tr = set(), []
    for f in glob.glob(f"{SP}/histfl_{W[:8]}/*_trades.jsonl"):
        for l in open(f):
            for e in json.loads(l)["trades"] or []:
                k = (e["m"], e["slot"], e["buy"], e["q"], e["tok"])
                if k not in seen: seen.add(k); tr.append(e)
    H[lab] = (W, kind, mn, tr)
qs = sorted({e["quote"] for *_, tr in H.values() for e in tr if not issol(e["quote"])})
if QOUT:
    open(QOUT, "w").write("\n".join(q for q in qs if q not in FLOATS) + "\n"); print(len(qs), "quote mints ->", QOUT); sys.exit()
P = {}
for i in range(0, len(qs), 40):
    for a in range(5):
        try: P.update({k: v for k, v in json.load(urllib.request.urlopen("https://lite-api.jup.ag/price/v3?ids=" + ",".join(qs[i:i + 40] + [SOLM]), timeout=20)).items() if v}); break
        except Exception: time.sleep(3 * (a + 1))
su = P[SOLM]["usdPrice"]
def rate(q):
    if issol(q): return 1.0
    v = P.get(q) or {}
    return v["usdPrice"] / su * 1e9 / 10 ** v["decimals"] if v.get("usdPrice") and v.get("decimals") is not None else None
tok = collections.defaultdict(lambda: dict(n=0, own=0.0, by=collections.Counter(), days=collections.defaultdict(float)))
print(f"last {DAYS:g} days; each unit's wallet, first buys at its floor and coin kind; own = the wallet's own SOL on the coins it sold out of\n")
for lab, (W, kind, mn, tr) in H.items():
    by = collections.defaultdict(list)
    for e in tr: by[e["m"]].append(e)
    G = collections.defaultdict(lambda: [0, 0.0, 0]); pays = collections.Counter(); unp = 0; span = [time.time(), 0]
    for m, es in by.items():
        es.sort(key=lambda e: (e["slot"], not e["buy"]))
        if not es[0]["buy"] or es[0]["t"] < T0: continue
        q = es[0]["quote"]; r = rate(q)
        if r is None: unp += 1; continue
        size = es[0]["q"] * r / 1e9
        if size < mn or (kind == "token" and issol(q)): continue
        span = [min(span[0], es[0]["t"]), max(span[1], es[0]["t"])]
        tin = sum(e["tok"] for e in es if e["buy"]); tout = sum(e["tok"] for e in es if not e["buy"])
        done = tout >= 0.99 * tin
        own = sum((e["q"] if not e["buy"] else -e["q"]) * rate(e["quote"]) / 1e9 for e in es if rate(e["quote"])) if done else 0.0
        if issol(q) or q == SOLM: g = "SOL"
        elif q in FLOATS: g = "float"; pays[FLOATS[q]] += 1
        elif ROUTE.get(q, "none").startswith("pool"): g = "pool route"
        else:
            g = "NO ROUTE"; t = tok[q]; t["n"] += 1; t["own"] += own; t["by"][lab] += 1
            t["days"][dt.datetime.fromtimestamp(es[0]["t"], dt.UTC).strftime("%m-%d")] += own
        G[g][0] += 1; G[g][1] += own; G[g][2] += done
    n = sum(v[0] for v in G.values()); hrs = max(1, (span[1] - span[0]) / 3600) if n else 0
    fr = f"{dt.datetime.fromtimestamp(span[0], dt.UTC):%m-%d %H:%M}" if n else "-"
    print(f"{lab} {W[:8]} ({kind} coins, {mn:g}+ SOL): {n} coins since {fr} UTC" + (f", {len(tr)} trades fetched" if tr else ", NO HISTORY")
          + (f", {unp} unpriced" if unp else ""))
    for g in ("SOL", "float", "pool route", "NO ROUTE"):
        if G[g][0]: print(f"    {g:10s} {G[g][0]:4d} coins ({100 * G[g][0] / n:4.1f}%)  own {G[g][1]:+7.2f} SOL on {G[g][2]} sold out")
    if pays: print("    floats used: " + ", ".join(f"{k} {v}" for k, v in pays.most_common()))
    nr = [(q, t["by"][lab]) for q, t in tok.items() if t["by"][lab]]
    if nr: print("    no-route tokens: " + ", ".join(f"{q[:8]} {c}" for q, c in sorted(nr, key=lambda x: -x[1])[:6]))
names = {}
for q in [q for q, _ in sorted(tok.items(), key=lambda x: -x[1]["n"])[:15]]:
    try:
        j = json.load(urllib.request.urlopen(f"https://lite-api.jup.ag/tokens/v2/search?query={q}", timeout=20))
        if j: names[q] = j[0].get("symbol", "?")
    except Exception: pass
print("\nthe tokens no route reaches, over all units, by the coins a float would open (first buy at the unit's floor):")
for q, t in sorted(tok.items(), key=lambda x: -x[1]["n"])[:15]:
    up = sum(1 for v in t["days"].values() if v > 0)
    print(f"  {q[:8]} {names.get(q, '?'):10s} {t['n']:4d} coins ({t['n'] / DAYS:4.1f} a day)  own {t['own']:+7.2f} SOL ({t['own'] / t['n']:+.3f} a coin)  days up {up} of {len(t['days'])}  by unit: "
          + ", ".join(f"{k} {v}" for k, v in t["by"].most_common()))
