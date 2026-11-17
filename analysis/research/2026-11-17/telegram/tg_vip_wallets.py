# Wallets that are in the VIP's winners BEFORE the alert (the owner, Nov 17: "analyze the VIP coins, see which are
# successful, then see if there are any wallets that are on all of them ... find the scaled wallet through that"). The
# VIP's alerts as a map: every alerted coin on a SOL curve with its trades from creation (the VIP folders' caches), its
# outcome after the alert (success = the price reached 2x the alert's within the hour; dead = under 0.5x an hour after),
# and every wallet's first buy BEFORE the alert (5 s or more before, 0.2+ SOL, not the creator). A wallet is listed with
# 10+ such coins from 5+ creators: how many of its coins succeeded against the base rate, how many died, how early it was,
# its size, and its own result on these coins (what its sales brought minus its buys, tokens left counted at 0).
# This is a map, not a test: the VIP coins are a chosen set, so a listed wallet's FULL history (all its coins, alerted or
# not) is the real check, as for wallet 4. Wallet 4 is shown wherever it ranks (the sanity check).
#   python3 -I tg_vip_wallets.py TGDIR > out/tg_vip_wallets.txt
import sys, os, json, gzip, collections, statistics as st, numpy as np
TG = sys.argv[1]; here = os.path.dirname(os.path.abspath(__file__)); W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
cns = {}; sys.argv = ["x", TG]; exec(open(os.path.join(here, "tg_channel.py")).read().split("for cj in sorted(glob.glob")[0], cns); order_slots = cns["order_slots"]
meta = {}
for f in (f"{TG}/vip/meta.json", f"{TG}/vip2/meta.json"):
    for m, v in json.load(open(f)).items(): meta.setdefault(m, v)
seen, coins = set(), []
for d in ("vip", "vip_rest", "vip_h1", "vip_h1b", "vip2"):
    pd = f"{TG}/{d}/paths"
    if not os.path.isdir(pd): continue
    for fn in os.listdir(pd):
        m = fn[:-8]
        if m in seen or m not in meta: continue
        x = json.load(gzip.open(f"{pd}/{fn}"))
        if x.get("venue") != "pump" or not x.get("tr") or not x.get("from_creation"): continue
        tr = order_slots(x["tr"])
        if not 25e9 < tr[0]["vq"] * tr[0]["vt"] / 1.073e15 < 35e9: continue
        ta = meta[m]["t"]; pre = [e for e in tr if e["t"] <= ta]; aft = [e for e in tr if ta < e["t"] <= ta + 3600]
        if not pre or not aft: continue
        p0 = pre[-1]["vq"] / pre[-1]["vt"]; pk = max(e["vq"] / e["vt"] for e in aft) / p0; end = aft[-1]["vq"] / aft[-1]["vt"] / p0
        seen.add(m); coins.append(dict(m=m, ta=ta, tr=tr, creator=x.get("creator"), ok=pk >= 2, dead=end < 0.5))
base = np.mean([c["ok"] for c in coins]); print(f"{len(coins)} VIP coins on a SOL curve with trades from creation; success (2x within the hour of the alert) {base:.0%}, dead {np.mean([c['dead'] for c in coins]):.0%}")
W = collections.defaultdict(list)
for c in coins:
    first = {}
    for e in c["tr"]:
        if e["buy"] and e["user"] not in first: first[e["user"]] = e
    for u, e in first.items():
        if u == c["creator"] or e["t"] > c["ta"] - 5 or e["q"] < 0.2e9: continue
        mine = [x for x in c["tr"] if x["user"] == u]
        got = sum(x["q"] for x in mine if not x["buy"]) - sum(x["q"] for x in mine if x["buy"])
        sold_before = any(not x["buy"] and x["t"] <= c["ta"] for x in mine)
        W[u].append(dict(ok=c["ok"], dead=c["dead"], lead=c["ta"] - e["t"], sol=e["q"] / 1e9, cr=c["creator"], net=got / 1e9, sold_before=sold_before, launch=e["slot"] <= c["tr"][0]["slot"] + 1))
rows = []
for u, v in W.items():
    if len(v) < 10 or len({x["cr"] for x in v}) < 5: continue
    n = len(v); ok = sum(x["ok"] for x in v)
    rows.append(dict(u=u, n=n, ok=ok, rate=ok / n, dead=sum(x["dead"] for x in v) / n, lead=st.median(x["lead"] for x in v), sol=st.median(x["sol"] for x in v),
                     net=sum(x["net"] for x in v), soldb=np.mean([x["sold_before"] for x in v]), launch=np.mean([x["launch"] for x in v])))
rows.sort(key=lambda r: (-(r["rate"] - base) * np.sqrt(r["n"]), -r["ok"]))
print(f"{len(rows)} wallets with 10+ early buys on these coins from 5+ creators; ranked by success above the base rate, weighted by how many coins\n")
print("wallet   | coins | succeeded (rate) | died | in before the alert (median) | size | sold before the alert | launch slot | its own net on them")
for i, r in enumerate(rows):
    if i < 40 or r["u"] == W4:
        print(f"{'>W4<' if r['u'] == W4 else '':4s}{r['u'][:8]} {i + 1:3d}. | {r['n']:4d} | {r['ok']:3d} ({r['rate']:4.0%}) | {r['dead']:4.0%} | {r['lead']:6.0f} s | {r['sol']:5.2f} | {r['soldb']:4.0%} | {r['launch']:4.0%} | {r['net']:+8.2f} SOL")
w4 = next((i for i, r in enumerate(rows) if r["u"] == W4), None)
print(f"\nwallet 4: {'rank ' + str(w4 + 1) + ' of ' + str(len(rows)) if w4 is not None else 'not listed (under 10 early buys on these coins, or none)'}; its early buys here: {len(W.get(W4, []))}")
json.dump(rows[:200], open(f"{TG}/vip_wallets_rows.json", "w"))
