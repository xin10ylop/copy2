# Floats to add (Nov 24; the owner: "check if there are any important floats we should add"). For each copied wallet: its
# first buys big enough for its unit (wallet 4: 1.3+ SOL, token coins; the others 0.5+), paid with a token we do not hold:
# by token, how many, over which days, and the wallet's own result on those it sold out of (token prices at Jupiter now).
#   python3 -I u2_floats.py OUT.json  WALLET:MIN:HISTDIR[,HISTDIR] ...
import sys, json, glob, collections, urllib.request, datetime as dt
SOLM = "So11111111111111111111111111111111111111112"
HELD = {"3NZ9JMVB", "pumpCmXq", "SPCXxcqX", "TTWofwAg", "he1iusmf", "98kfF7rm", "Xsc9qvGR"}
issol = lambda q: not q or q.startswith("1111")
rows = []
for spec in sys.argv[2:]:
    W, MIN, dirs = spec.split(":"); MIN = float(MIN)
    seen, trades = set(), []
    for d in dirs.split(","):
        for f in glob.glob(f"{d}/*_trades.jsonl"):
            for l in open(f):
                for e in json.loads(l)["trades"] or []:
                    k = (e["m"], e["slot"], e["buy"], e["q"], e["tok"])
                    if k not in seen: seen.add(k); trades.append(e)
    by = collections.defaultdict(list)
    for e in trades: by[e["m"]].append(e)
    for m, es in by.items():
        es.sort(key=lambda e: (e["slot"], not e["buy"]))
        if es[0]["buy"] and not issol(es[0]["quote"]) and es[0]["quote"][:8] not in HELD:
            rows.append(dict(w=W[:8], q=es[0]["quote"], t=es[0]["t"], q_in=es[0]["q"], min=MIN, es=[(e["buy"], e["q"], e["tok"]) for e in es]))
qs = sorted({r["q"] for r in rows}); P = {}
for i in range(0, len(qs), 40):
    try: P.update({k: v for k, v in json.load(urllib.request.urlopen("https://lite-api.jup.ag/price/v3?ids=" + ",".join(qs[i:i + 40] + [SOLM]), timeout=20)).items() if v})
    except Exception: pass
su = (P.get(SOLM) or {}).get("usdPrice")
agg = collections.defaultdict(lambda: dict(n=0, days=set(), own=0.0, done=0, wallets=collections.Counter()))
for r in rows:
    v = P.get(r["q"]) or {}
    if not (su and v.get("usdPrice") and v.get("decimals") is not None): continue
    rate = v["usdPrice"] / su / 10 ** v["decimals"]
    if r["q_in"] * rate < r["min"]: continue
    a = agg[r["q"]]; a["n"] += 1; a["days"].add(dt.datetime.fromtimestamp(r["t"], dt.UTC).strftime("%m-%d")); a["wallets"][r["w"]] += 1
    tin = sum(x[2] for x in r["es"] if x[0]); tout = sum(x[2] for x in r["es"] if not x[0])
    if tout >= 0.99 * tin: a["done"] += 1; a["own"] += sum((x[1] if not x[0] else -x[1]) for x in r["es"]) * rate
out = sorted(((a["n"], q, a) for q, a in agg.items()), key=lambda x: -x[0])
print(f"{'token':10s} {'buys':>5s} {'days':>5s} {'own SOL (sold out)':>19s}  by wallet")
for n, q, a in out[:15]:
    print(f"{q[:8]:10s} {n:5d} {len(a['days']):5d} {a['own']:+10.2f} ({a['done']:3d})  " + ", ".join(f"{w} {c}" for w, c in a["wallets"].most_common()))
json.dump([dict(q=q, n=n, days=len(a["days"]), own=a["own"], wallets=dict(a["wallets"])) for n, q, a in out[:15]], open(sys.argv[1], "w"))
