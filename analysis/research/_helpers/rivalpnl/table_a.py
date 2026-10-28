import sys, os, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C, rival_stats as R
top = json.load(open(os.path.join(C.OUTD, "top12.json"))); F = json.load(open(os.path.join(C.OUTD, "failed.json")))
cc = json.load(open(os.path.join(C.OUTD, "create_count.json")))["ok"]
T07 = 1792713600 + 7 * 3600
creates_since07 = sum(v for h, v in cc.items() if int(h) >= 7)
res = {}
rows = [(w, F.get(w)) for w in top] + [(C.OUR, None)]
for w, f in rows:
    h = json.load(open(os.path.join(C.OUTD, f"hist_{w}.json")))
    if w == C.OUR:
        h["now"] = max(t["timestamp"] for t in h["txs"]); h["cutoff"] = 1792713600; f = dict(n_failed=77, mean_fee=(0.4291 + 0.0204) / 77 * 1e9)
    r = R.stats(w, h, f)
    # pick rate since 07:00 UTC (creates counted per hour from mint-authority signatures)
    m07 = sum(1 for d in r["mintmap"].values() if d["fb"] >= T07)
    t0 = max(T07, min(d["fb"] for d in r["mintmap"].values())) if r["mintmap"] else T07
    # creates in covered hours >= 07
    hrs = {datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%H") for t in range(int(t0), int(h["now"]), 600)}
    cr = sum(cc.get(x, 0) for x in hrs) or 1
    r["pick07"] = m07 / cr; r["m07"] = m07; r["cr07"] = cr
    res[w] = r
json.dump(res, open(os.path.join(C.OUTD, "table_a.json"), "w"))
print(f"{'wallet':10s} {'hrs':>5s} {'buys':>5s} {'mints':>5s} {'medSz':>6s} {'outBuy':>7s} {'inSell':>7s} {'fee':>6s} {'tips':>6s} {'svc':>5s} {'failF':>6s} {'nFail':>5s} {'PnLwin':>7s} {'net/24h':>7s} {'win':>5s} {'medRet':>7s} {'meanRet':>7s} {'hold':>5s} {'held':>4s} {'heldC':>6s} {'pick':>6s}")
for w, r in sorted(res.items(), key=lambda kv: -kv[1]["net_day"]):
    print(f"{w[:10]:10s} {r['hours']:5.1f} {r['n_buy']:5d} {r['mints']:5d} {r['med_size']:6.3f} {r['out_buys']:7.2f} {r['in_sells']:7.2f} {r['fees']:6.3f} {r['tips']:6.3f} {r['svc']:5.2f} {r['fail_fee']:6.3f} {r['n_failed'] or 0:5d} {r['pnl_mints']-r['fail_fee']:+7.2f} {r['net_day']:+7.2f} {r['win']:5.2f} {r['med_ret']:+7.3f} {r['mean_ret']:+7.3f} {str(r['med_hold']):>5s} {r['held']:4d} {r['held_cost']:6.2f} {r['pick07']*100:5.1f}%  cov {r['mints']}/{r['n_mints_all']} cleanCost {r['clean_cost']:.1f}")
for w, r in res.items(): print(w[:10], "tips", r["tip_kinds"], "srcs", r["srcs"], "multi", r["multi"], "p90hold", r["p90_hold"], "net_cash", round(r["net_cash"], 3), "pnl_mints", round(r["pnl_mints"], 3))
