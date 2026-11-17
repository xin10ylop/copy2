# Winners first, step 3: who buys the winners early, in a way we could copy. Rules fixed before looking:
#   a copyable early buy = a wallet's first buy on the coin, 0.25+ SOL (quote valued at Jupiter's price, as m3_screen),
#   not the creator, at least 2 slots after the create (the launch slot and the next are snipers and bundles), with the
#   curve under half sold before it (room to run: graduation from there is 5x or more on the curve's price).
#   base rate b(p) = of the coins whose curve reached progress p (within the trades fetched), the share that graduated;
#   the control coins weighted by (coins that did not graduate) / (control sample).
#   a wallet's score: its early buys on graduated coins (hits), from 3+ creators; its early buys on control coins scaled to
#   the whole market (an estimate of its misses); its hit rate against the base rate at its own entry points (lift).
# The hit rate here is only a screen: the real test is each wallet's own full history (step 4), on days before Nov 15.
#   python3 -I w3_buyers.py SP > out/w3_buyers.txt
import sys, os, json, gzip, collections, statistics as st
SP = sys.argv[1]; W = f"{SP}/winners"
INIT_REAL = 793_100_000_000_000; WSOL = "So11111111111111111111111111111111111111112"
SOLQ = {WSOL, "11111111111111111111111111111111", None, "?"}
oc = json.load(open(f"{W}/outcomes.json")); sm = json.load(open(f"{W}/sample.json"))
cr = {v["mint"]: v for v in json.load(open(f"{SP}/market/creates.json")).values() if v and v.get("mint")}
PR = json.load(open(f"{SP}/market/prices.json")); sol_usd = PR[WSOL]["usdPrice"]
def rate_of(q):   # lamports per raw quote unit
    if q in SOLQ: return 1.0
    return PR[q]["usdPrice"] / sol_usd * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None
WCTRL = sm["n_rest"] / len(sm["ctrl"])
prog = lambda e: max(0.0, (INIT_REAL - e["real"]) / INIT_REAL)
BINS = [0, .1, .2, .3, .4, .5]
reach = collections.Counter(); reach_g = collections.Counter(); n = {"grad": 0, "ctrl": 0}
B = collections.defaultdict(list); unpriced = 0
for kind in ("grad", "ctrl"):
    for m in sm[kind]:
        f = f"{W}/paths/{m}.json.gz"
        if not os.path.exists(f) or m not in cr: continue
        tr = json.load(gzip.open(f)); n[kind] += 1
        if not tr: continue
        g = kind == "grad"; w = 1.0 if g else WCTRL
        pk = max(prog(e) for e in tr)
        for b in BINS:
            if pk >= b: reach[b] += w; reach_g[b] += w * g
        rate = rate_of(cr[m].get("quote"))
        if rate is None: unpriced += 1; continue
        seen = set(); p_before = 0.0
        for e in tr:
            u = e["user"]
            if e["buy"] and u not in seen and u != cr[m].get("creator") and e["slot"] - cr[m]["slot"] >= 2 and p_before < 0.5:
                sol = e["q"] * (1 + e["bps"] / 1e4) * rate / 1e9
                if sol >= 0.25:
                    B[u].append(dict(m=m, g=g, p=p_before, t=e["t"], dt=e["t"] - cr[m]["t"], sol=sol, cr=cr[m].get("creator")))
            seen.add(u); p_before = prog(e)
bp = {b: reach_g[b] / reach[b] for b in BINS if reach[b]}
def b_of(p): return bp[max(b for b in BINS if b <= p)]
print(f"coins read: {n['grad']} graduated, {n['ctrl']} control (each control coin stands for {WCTRL:.1f}); {unpriced} unpriced left out")
print("base rate: of the coins whose curve reached p, the share that graduated")
for b in BINS: print(f"  p >= {b:.0%}: {reach[b]:9.0f} coins, {bp[b]:6.2%} graduated")
rows = []
for u, v in B.items():
    hits = [x for x in v if x["g"]]
    if len(hits) < 3 or len({x["cr"] for x in hits}) < 3: continue
    miss_seen = sum(1 for x in v if not x["g"]); miss_est = miss_seen * WCTRL
    exp = sum(b_of(x["p"]) for x in hits) + WCTRL * sum(b_of(x["p"]) for x in v if not x["g"])   # expected hits at its entries
    rate = len(hits) / (len(hits) + miss_est)
    rows.append(dict(u=u, hits=len(hits), cr=len({x["cr"] for x in hits}), miss_seen=miss_seen, miss_est=miss_est, rate=rate,
                     lift=len(hits) / exp if exp else 0, p=st.median(x["p"] for x in v), dt=st.median(x["dt"] for x in v),
                     sol=st.median(x["sol"] for x in v), days={x["t"] // 86400 for x in hits}))
rows.sort(key=lambda r: (-r["hits"], -r["rate"]))
print(f"\nwallets with 3+ early copyable buys on graduated coins, from 3+ creators: {len(rows)}")
print("wallet   | hits creators | control buys seen -> misses est | hit rate est | lift | entry p med, s after launch, SOL med")
for r in rows[:80]:
    print(f"{r['u'][:8]} | {r['hits']:4d} {r['cr']:4d} | {r['miss_seen']:4d} -> {r['miss_est']:6.0f} | {r['rate']:6.1%} | {r['lift']:4.1f} | "
          f"{r['p']:4.0%} {r['dt']:6.0f} s {r['sol']:5.2f}")
json.dump(rows, open(f"{W}/w3_rows.json", "w"), default=list)
json.dump({str(b): v for b, v in bp.items()}, open(f"{W}/bp.json", "w"))
