# Which other tokens are worth holding as floats for wallet 4 (Nov 18, the owner: "any other floats to add?"): from
# the research corpus on disk (allq / cq / since_stop / newq, Oct 21 - Nov 17, no fetch), wallet 4's 1.3+ SOL buys of
# coins NOT priced in one of our 7 floats, by the token they are priced in: those the bot could not route ("NoAnchor":
# skipped live) and those it pays from wSOL through a pool. Each modelled as if that token were a float (a direct
# curve buy, no pool hop), the running setting, 0.5 SOL, mean of three landings, 0.0345 SOL a round trip.
import sys, os, json, gzip, re, collections, numpy as np, datetime as dt
SP = sys.argv[1]; here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(here, ".."))
sys.argv = ["x", SP, "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"]; exec(open(os.path.join(here, "e8_engineer.py")).read().split("rows = []")[0])
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; ix = (TP.index(4), HOLD.index(600), SPS.index((5, 60)), STALL.index(180), ITS.index("early"))
seen, out = set(), []
for d_ in ("newq", "since_stop", "cq", "allq"):
    try: P = json.load(gzip.open(f"{SP}/{d_}/paths.json.gz")); R = json.load(open(f"{SP}/{d_}/routable.json"))
    except Exception: continue
    for r in R:
        kk = f"{r['slot']}_{r['mint8']}"; q8 = str(r.get("quote"))[:8]
        if q8 in FLOATS or q8 == "So111111" or r["sol"] < 1.3 or kk in seen or not P.get(kk): continue
        seen.add(kk); m_, tr = P[kk]; tr = SO.reorder(tr)
        k = next((i for i, e in enumerate(tr) if e["user"] == W4 and e["buy"] and e["slot"] == r["slot"]), None)
        if k is None or tr[-1]["t"] - tr[k]["t"] < 600: continue
        rate = r["sol"] * 1e9 / (tr[k]["q"] * (1 + tr[k]["bps"] / 1e4)); ps = [H.prep(tr, k, rate, n, pmax=1.5) for n in (4, 8, "slot+1")]
        v = float(np.mean([copy_vals(p)[ix] for p in ps])) - COST
        out.append(dict(q=q8, t=tr[k]["t"], ok=r.get("ok", True), v=v))
days = (max(o["t"] for o in out) - min(o["t"] for o in out)) / 86400
print(f"wallet 4's 1.3+ SOL buys on coins priced in other tokens (not our floats, not SOL): {len(out)} over {days:.1f} days")
print("token     | buys | a day | not routable live | as a float: SOL  a copy  won | first half / second half")
tm = np.median([o["t"] for o in out])
for q, n in collections.Counter(o["q"] for o in out).most_common(15):
    v = np.array([o["v"] for o in out if o["q"] == q]); a = sum(o["v"] for o in out if o["q"] == q and o["t"] < tm); b = v.sum() - a
    print(f"{q} | {n:4d} | {n / days:5.2f} | {sum(not o['ok'] for o in out if o['q'] == q):4d} | {v.sum():+6.2f} {100 * v.mean() / 0.5:+6.1f}% {100 * np.mean(v > 0):3.0f}% | {a:+.2f} / {b:+.2f}")
