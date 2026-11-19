# p3 (Nov 19): e14_live_vs_model.py run on the 8zqsUMty + FDhoU1DE trader, its SOL coins included (WITH_SOL=1): our copy of
# since T0 (fetched now, Alchemy, batched), each copy's 31-minute path, the model at the deployed setting (mean of the
# three landings), beside the box's journal (pasted, by coin prefix).
#   RPC_URL=... python3 -I e14_live_vs_model.py SP WALLET T0 "size,prem,tp,hold,sp,stall,its" PREFIX=NET,...
import sys, os, json, numpy as np, datetime as dt
here = '/home/user/copy2/analysis/research/2026-11-17/wallet_hunt/market'; SP, WL, T0, spec = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
sys.path.insert(0, '/home/user/copy2/analysis/research/2026-11-17/wallet_hunt'); sys.path.insert(0, here)
LIVE = dict(x.split("=") for x in sys.argv[5].split(",")) if len(sys.argv) > 5 else {}
sys.argv = ["x", SP, WL]; exec(open(os.path.join(here, "e8_engineer.py")).read().split("rows = []")[0])
here = '/home/user/copy2/analysis/research/2026-11-17/wallet_hunt/market'   # e8 sets here to this file's folder
src = open("/home/user/copy2/analysis/research/2026-11-17/winners/w4_history.py").read().split("def history")[0]
ns = {"__file__": "w4_history.py"}; sys.argv = ["x", SP]; exec(compile(src, "w4_history.py", "exec"), ns)
sigs, before = [], None
while True:
    pg = ns["call"]("getSignaturesForAddress", [WL, {"limit": 1000, **({"before": before} if before else {})}])
    if not pg: break
    sigs += [s for s in pg if s["err"] is None and (s.get("blockTime") or 0) >= T0]; before = pg[-1]["signature"]
    if len(pg) < 1000 or (pg[-1].get("blockTime") or 0) < T0: break
ch = [[x["signature"] for x in sigs[i:i + 100]] for i in range(0, len(sigs), 100)]
txs = [t for part in ns["POOL"].map(ns["_batch"], ch) for t in part]
trades = sorted([e for tx in txs if tx for e in ns["own_trades"](tx, WL)], key=lambda e: e["t"])
m5 = open(os.path.join(here, "m5_confirm.py")).read().split("def S(v):")[0]; sys.argv = ["x", SP, WL]; exec(m5)
z = spec.split(","); e_ix = (TP.index(1e9 if z[2] == "none" else float(z[2])), HOLD.index(int(z[3])), SPS.index(None if z[4] == "off" else tuple(int(x) for x in z[4].split("/"))),
                             STALL.index(0 if z[5] == "off" else int(z[5])), ITS.index(z[6]))
seen, out = set(), []
print(f"{WL[:8]}: {len(sigs)} transactions since {dt.datetime.fromtimestamp(T0, dt.UTC):%m-%d %H:%M} UTC, {sum(e['buy'] for e in trades)} buys; setting {spec}")
print("time UTC  coin      its SOL  quote     model SOL (4 / 8 / next slot)   live SOL")
for e in trades:
    if not e["buy"] or e["m"] in seen: continue
    seen.add(e["m"]); r = rate_of(e["quote"])
    if r is None: continue
    sol = e["q"] * (1 + e["bps"] / 1e4) * r / 1e9
    if sol < float(z[0]) or (e["quote"] in SOLQ and not os.environ.get("WITH_SOL")): continue
    try: tr = cpath(e["m"], e["slot"], e["t"])
    except Exception as x: print(f"{e['m'][:8]} no path: {x}"); continue
    k = next((j for j, y in enumerate(tr) if y["user"] == WL and y["buy"] and y["slot"] == e["slot"]), None)
    if k is None: continue
    ps = [H.prep(tr, k, r, n, pmax=1000) for n in (4, 8, "slot+1")]; v = [float(copy_vals(p)[e_ix]) - COST for p in ps]
    lv = LIVE.get(e["m"][:8], ""); out.append((np.mean(v), float(lv) if lv else None))
    print(f"{dt.datetime.fromtimestamp(e['t'], dt.UTC):%H:%M:%S}  {e['m'][:8]}  {sol:6.3f}  {e['quote'][:8]}  {np.mean(v):+.4f} ({v[0]:+.3f} / {v[1]:+.3f} / {v[2]:+.3f})   {lv or '-'}")
both = [(a, b) for a, b in out if b is not None]
print(f"\nmodel, every copy: {len(out)} copies {sum(a for a, _ in out):+.3f} SOL; on the coins the bot traded ({len(both)}): model {sum(a for a, _ in both):+.3f}, live {sum(b for _, b in both):+.3f}")
