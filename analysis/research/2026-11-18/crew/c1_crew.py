# The pre-alert crew (the owner, Nov 18: "when something fails find another solution, on and on"). 6ua7w2Gv, q2q38wAb and
# q2jJy82z made money only on coins the SolHouse VIP alerted ~70-80 s after their buy. Are the VIP-map wallets (the 8 of
# winners/w4_history on the VIP coins) one crew, whose joint buying predicts the alert? For every coin bought by any of them
# (their histories, SP/winners/hist), inside the VIP exports' spans: how many crew wallets bought it within 120 s of the
# first crew buy, and whether the VIP alerted it within 10 min after that first buy. If 2+ crew buys predict the alert far
# better than 1, the crew is a trigger: buy on the 2nd crew buy, sell into the alert.
#   python3 -I c1_crew.py SP > out/c1_crew.txt
import sys, json, glob, os, collections
SP = sys.argv[1]
CREW = ["6ua7w2Gv", "q2q38wAb", "q2jJy82z", "7777P2fk", "GKd5EMzR", "6Z91Dgiz", "6anjqMeW", "2NUMEzNh"]
VIP, SPANS = {}, []
for f in (f"{SP}/tg/vip/meta.json", f"{SP}/tg/vip2/meta.json"):
    mv = json.load(open(f)); ts = [v["t"] for v in mv.values()]; SPANS.append((min(ts), max(ts) - 600))
    for m, v in mv.items(): VIP.setdefault(m, v["t"])
cover = lambda t: any(a <= t <= b for a, b in SPANS)
buys = collections.defaultdict(list)   # coin -> [(t, wallet)]
for w in CREW:
    f = glob.glob(f"{SP}/winners/hist/{w}*.json")
    if not f: print("no history:", w); continue
    first = {}
    for e in sorted(json.load(open(f[0]))["trades"], key=lambda e: e["t"]):
        if e["buy"]: first.setdefault(e["m"], e["t"])
    for m, t in first.items(): buys[m].append((t, w))
rows = []
for m, v in buys.items():
    v.sort(); t0 = v[0][0]
    if not cover(t0): continue
    n = len({w for t, w in v if t - t0 <= 120}); a = VIP.get(m)
    rows.append(dict(m=m, t=t0, n=n, crew=sorted({w for t, w in v if t - t0 <= 120}), alerted=a is not None and 0 < a - t0 <= 600,
                     before=a is not None and a <= t0, lag=(a - t0) if a else None, t2=(v[1][0] - t0) if len(v) > 1 else None))
json.dump(rows, open(f"{SP}/crew_rows.json", "w"))
print(f"{len(rows)} coins bought by the crew inside the VIP exports' spans")
for n in sorted({r["n"] for r in rows}):
    X = [r for r in rows if r["n"] == n]; al = [r for r in X if r["alerted"]]
    lag = sorted(r["lag"] for r in al); t2 = sorted(r["t2"] for r in X if r["t2"] is not None and r["t2"] <= 120)
    print(f"   {n} crew wallet(s) within 120 s: {len(X):5d} coins, alerted after {len(al):4d} ({len(al) / len(X):5.1%}), already alerted before {sum(r['before'] for r in X):4d}"
          f" | alert {lag[len(lag) // 2] if lag else '-'} s after the first crew buy | 2nd crew buy {t2[len(t2) // 2] if t2 else '-'} s after the first")
pairs = collections.Counter(tuple(r["crew"]) for r in rows if r["n"] >= 2)
print("\nwhich wallets buy together (2+ within 120 s):", [(tuple(w[:4] for w in k), c) for k, c in pairs.most_common(8)])
