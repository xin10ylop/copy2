# Search 1 (+ 5): who else buys big, early, on the coins wallet 4 bought since Oct 28 (since_stop: routable.json and
# paths.json.gz, every trade for 31 minutes from its buy). Per coin: every buy worth MIN+ SOL (quote units at wallet 4's
# own rate at its buy) within WIN s of wallet 4's buy (paths start at its buy's slot, so a buy earlier in that slot
# counts too; earlier slots are not in the paths), and that buyer's first and last sale in the 31 minutes.
#   python3 -I s1_neighbours.py SPD [MIN 1.45] [WIN 5]
import sys, json, gzip, statistics, collections
SPD = sys.argv[1]; MIN = float(sys.argv[2]) if len(sys.argv) > 2 else 1.45; WIN = float(sys.argv[3]) if len(sys.argv) > 3 else 5
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
rows = {f"{r['slot']}_{r['mint8']}": r for r in json.load(open(f"{SPD}/routable.json")) if r["ok"]}
P = json.load(gzip.open(f"{SPD}/paths.json.gz"))
per = collections.defaultdict(list)   # wallet -> list of (coin, sol, dt to w4, slot gap, held s or None, sold all?, ahead?)
ncoin = 0
for key, (m, tr) in P.items():
    r = rows.get(key)
    if not r: continue
    k = next((i for i, e in enumerate(tr) if e["user"] == W4 and e["buy"] and e["slot"] == r["slot"]), None)
    if k is None: continue
    ncoin += 1; its = tr[k]; rate = r["sol"] * 1e9 / (its["q"] * (1 + its["bps"] / 1e4))
    seen = set()
    for i, e in enumerate(tr):
        if not e["buy"] or e["user"] == W4 or e["user"] in seen: continue
        if e["t"] - its["t"] > WIN: break
        sol = e["q"] * rate / 1e9
        if sol < MIN: continue
        seen.add(e["user"])
        bought = sum(x["tok"] for x in tr if x["user"] == e["user"] and x["buy"])
        sells = [x for x in tr[i + 1:] if x["user"] == e["user"] and not x["buy"]]
        sold = sum(x["tok"] for x in sells)
        per[e["user"]].append(dict(coin=m[:8], sol=sol, dt=e["t"] - its["t"], ds=e["slot"] - its["slot"], ahead=i < k,
                                   first=(sells[0]["t"] - e["t"]) if sells else None, last=(sells[-1]["t"] - e["t"]) if sells else None,
                                   nsell=len(sells), frac=sold / bought if bought else 0, nbuy=sum(1 for x in tr if x["user"] == e["user"] and x["buy"]),
                                   px=(e["vt"] and (its["vt"] / e["vt"]) ** 2)))
print(f"{ncoin} coins of wallet 4 (routable 1.45+ buys, Oct 28 - Nov 12) with its buy in the path; buyers of {MIN}+ SOL within {WIN} s of it")
print(f"{len(per)} wallets; {sum(1 for v in per.values() if len(v) >= 5)} on 5+ coins, {sum(1 for v in per.values() if len(v) >= 10)} on 10+")
med = lambda v: statistics.median(v) if v else None
print(f"{'wallet':45s} {'coins':>5s} {'SOL med':>7s} {'ahead':>5s} {'dt med':>6s} {'1st sale s p25/med/p75':>24s} {'held 120s+':>10s} {'no sale 31m':>11s} {'1 sale':>6s} {'multi-buy':>9s}")
out = []
for w, v in sorted(per.items(), key=lambda x: -len(x[1])):
    if len(v) < 3: continue
    fs = sorted(x["first"] for x in v if x["first"] is not None)
    q = lambda p: fs[min(int(p * len(fs)), len(fs) - 1)] if fs else None
    held = sum(1 for x in v if x["first"] is None or x["first"] >= 120)
    rec = dict(w=w, n=len(v), sol=med([x["sol"] for x in v]), ahead=sum(x["ahead"] for x in v), dt=med([x["dt"] for x in v]),
               f25=q(.25), f50=q(.5), f75=q(.75), held=held, nosale=sum(1 for x in v if x["first"] is None),
               one=sum(1 for x in v if x["nsell"] == 1), multi=sum(1 for x in v if x["nbuy"] > 1), coins=v)
    out.append(rec)
    fmt = lambda x: "-" if x is None else f"{x:.0f}"
    print(f"{w:45s} {len(v):5d} {rec['sol']:7.2f} {rec['ahead']:5d} {rec['dt']:6.1f} {fmt(rec['f25']):>7s}/{fmt(rec['f50']):>6s}/{fmt(rec['f75']):>7s} "
          f"{held:5d} {100*held/len(v):3.0f}% {rec['nosale']:11d} {rec['one']:6d} {rec['multi']:9d}")
json.dump(out, open(f"{SPD}/s1_neighbours_{MIN}.json", "w"))
