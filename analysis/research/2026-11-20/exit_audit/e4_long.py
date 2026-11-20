# The exit test over a longer time (Nov 20; the owner: "do the backtest on longer"): e1's model and exits on wallet 4's
# token-coin buys of 1.3+ SOL from its research corpus Oct 21 - Nov 14 01:07 UTC (allq / cq / since_stop / newq, loaded as
# market/m15f does: every trade for 31 minutes from its buy, true in-slot order, its SOL value from routable.json at the
# time) plus f1_paths.py's Nov 15 19:56 - Nov 20 17:12. Not covered: Nov 14 01:07 - Nov 15 19:56. The live exit was
# picked on Oct 21 - Nov 15 (in sample there); after Nov 15 19:29 it is out of sample. By week.
#   LK=SP/lk python3 -I e4_long.py SP > out/e4_long.txt
import sys, os, json, numpy as np, datetime as dt
SP = sys.argv[1]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt")
src = open("/home/user/copy2/analysis/research/2026-11-17/wallet_hunt/market/m15f_w4_dip_by_pay.py").read()
_argv = sys.argv; sys.argv = ["m15f", SP, "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"]
exec(src.split("import datetime as dt, numpy as np, collections")[0]); sys.argv = _argv
old = [r for r in rows if r["sol"] >= 1.3 and r["t"] < 1794618422]
exec(open("e1_exits.py").read().split("ps = [p for p")[0])   # e1's prep / exit_value (redefines H, first)
def prep_old(r):
    p = H.prep(r["tr"], r["k"], r["rate"], "slot+1", pmax=1.5)
    if p["refused"] or not len(p["px"]): return dict(refused=True, t=r["t"], m="", sol=r["sol"])
    vt0, vq0, b0 = p["ent"]; Q = STAKE * 1e9 / r["rate"]; net_in = Q * 1e4 / (1e4 + b0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq_r = p["vq"] + net_in; vt_r = p["vt"] * p["vq"] / vq_r
    p["val"] = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - p["bps"] / 1e4) * r["rate"] / 1e9 - STAKE - 0.0026 - COST
    p["prem"] = (r["tr"][r["k"]]["vt"] / vt0) ** 2; p["t"] = r["t"]; p["sol"] = r["sol"]; p["refused"] = False; return p
ps = [prep_old(r) for r in old] + [p for p in map(prep, coins) if p is not None]; ps.sort(key=lambda p: p["t"])
print(f"{len(ps)} copies: {len(old)} Oct 21 - Nov 14 01:07, {len(ps) - len(old)} Nov 15 19:56 - Nov 20 17:12 UTC; 1 SOL a copy")
V = {"live (sp 5/60, stall 180, its early sale, tp 4, 600 s)": {}, "its sale always, no sp": dict(its="always", sp=None),
     "its sale always (sp kept)": dict(its="always"), "no sp (its early sale)": dict(sp=None),
     "its sale always, no sp, no tp": dict(its="always", sp=None, tp=None)}
wk = lambda t: dt.datetime.fromtimestamp(t - (t - 1792540800) % (7 * 86400), dt.UTC).strftime("%m-%d")
weeks = sorted({wk(p["t"]) for p in ps}); after = np.array([p["t"] > dt.datetime(2026, 11, 15, 19, 29, tzinfo=dt.UTC).timestamp() for p in ps])
print(f"\n{'exit':52s} {'all':>7s} {'w/o 2%':>7s} {'before freeze':>13s} {'after':>7s}  by week ({', '.join(weeks)})")
for name, kw in V.items():
    x = np.array([exit_value(p, **kw) for p in ps]); k2 = max(1, round(0.02 * len(x)))
    byw = [x[[i for i, p in enumerate(ps) if wk(p["t"]) == w]].sum() for w in weeks]
    print(f"{name:52s} {x.sum():+7.2f} {np.sort(x)[:-k2].sum():+7.2f} {x[~after].sum():+13.2f} {x[after].sum():+7.2f}  " + "  ".join(f"{v:+.2f}" for v in byw))
print("copies a week: " + "  ".join(f"{w} {sum(1 for p in ps if wk(p['t']) == w)}" for w in weeks))
