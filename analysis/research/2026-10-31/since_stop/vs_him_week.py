# Last 7 days, on the coins wallet 4 closed (his_week.py's 100): our two exit policies against its real result, on one
# yardstick. The raw model is cautious, so it is also run on wallet 4 itself (its own price, selling right behind its
# sale, no take profit, no timer); our estimate = its real % + (our model % - its model %). 1 SOL a coin, every coin
# (no open-slot limit), price limit 1.25 as live. Landing: in its block 4 or 8 trades after it (live: 3, 7, 8), and
# a block late (every trade in its block and the next one ahead of us).
#   python3 -I vs_him_week.py SPD
import sys, os, io, contextlib, subprocess, re
SPD = sys.argv[1]; here = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD, "4"]; sys.path.insert(0, here); import copy_grid as G
# its real per-coin result: rerun his_week's sums per coin
import json, statistics
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; WSOL = "So11111111111111111111111111111111111111112"; WB = "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh"
END = max(r["t"] for r in G.M.rows); T0 = END - 7 * 86400
rs = {r["mint8"]: r for r in G.trips if T0 <= r["t"] <= END}
txs, rates = [], []
for f in os.listdir(f"{SPD}/w4tx"):
    t = json.load(open(f"{SPD}/w4tx/{f}")); m = t["meta"]
    if m.get("err") or not (T0 - 86400 <= t["blockTime"] <= END + 86400): continue
    ks = t["transaction"]["message"]["accountKeys"] + sum(((m.get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
    if W4 not in ks: continue
    i = ks.index(W4)
    def tb(w):
        d = {}
        for b in m.get(w) or []:
            if b.get("owner") == W4: d[b["mint"]] = d.get(b["mint"], 0) + int(b["uiTokenAmount"]["amount"])
        return d
    pre, post = tb("preTokenBalances"), tb("postTokenBalances")
    sol = (m["postBalances"][i] - m["preBalances"][i]) / 1e9 + (post.get(WSOL, 0) - pre.get(WSOL, 0)) / 1e9
    mv = {k: post.get(k, 0) - pre.get(k, 0) for k in set(pre) | set(post) if k != WSOL and post.get(k, 0) != pre.get(k, 0)}
    if list(mv) == [WB] and abs(sol) > 0.05: rates.append(abs(sol * 1e9 / mv[WB]))
    txs.append((sol, mv))
R = statistics.median(rates) / 1e9; his = {}
for sol, mv in txs:
    cs = [k for k in mv if k != WB and k[:8] in rs]
    if len(cs) != 1 or len([k for k in mv if k != WB]) != 1: 
        for k in cs: his.setdefault(k[:8], dict(net=0, spent=0, bad=True))["bad"] = True
        continue
    k = cs[0][:8]; c = his.setdefault(k, dict(net=0, spent=0, bad=False)); v = sol + mv.get(WB, 0) * R; c["net"] += v
    if mv[cs[0]] > 0: c["spent"] += -v
coins = [k for k, c in his.items() if not c["bad"] and c["spent"] > 0 and k in rs and f"{rs[k]['slot']}_{k}" in G.P]
real = 100 * sum(his[k]["net"] for k in coins) / sum(his[k]["spent"] for k in coins)
def run(n, **kw):
    v = []
    for k in coins:
        r = rs[k]; m, tr = G.P[f"{r['slot']}_{k}"]; o = G.M.model(r, m, tr, 1.0, n, **kw)
        if "net" in o: v.append((o["net"], o["exit"], k))
    return v
him = run(0, tp=None, sl=None, hold=10**9, follow=True, pmax=99); him_pct = 100 * sum(x[0] for x in him) / len(him)
print(f"{len(coins)} coins wallet 4 bought and closed, Nov 5 08:49 to Nov 12 08:49 Beirut")
print(f"  wallet 4, real:                       {real:+6.1f}% a trade (its own SOL in and out)")
print(f"  wallet 4 through the raw model:       {him_pct:+6.1f}%   -> the model sits {real - him_pct:.1f} points under reality")
POL = (("what we run (hold; tp 2.5, no stop, 30 min)", dict(tp=2.5, sl=None, hold=1790, follow=False, pmax=1.25)),
       ("sell right behind it (no tp, 30 min cap)", dict(tp=None, sl=None, hold=1790, follow=True, pmax=1.25)),
       ("sell right behind it, or tp 2.5 first", dict(tp=2.5, sl=None, hold=1790, follow=True, pmax=1.25)))
for lab, n in (("in its block, 4 trades after it", 4), ("in its block, 8 trades after it", 8), ("one block late", "slot+1")):
    print(f"\n== landing {lab}")
    print(f"   {'policy':44s} {'copies':>6s} {'model %':>8s} {'w/o best 2':>10s} {'ESTIMATE %':>10s} {'SOL at 1 SOL':>12s}  exits")
    for name, kw in POL:
        v = run(n, **kw); took = [x for x in v if x[1] != "refused"]
        pct = 100 * sum(x[0] for x in v) / len(took); s2 = sorted((x[0] for x in v), reverse=True)[2:]
        est = real + pct - him_pct; ex = {}
        for x in v: ex[x[1]] = ex.get(x[1], 0) + 1
        print(f"   {name:44s} {len(took):6d} {pct:+7.1f}% {100*sum(s2)/len(took):+9.1f}% {est:+9.1f}% {est*len(took)/100:+11.2f}  {ex}")
