# Are the two path sources the same? (Nov 18: every wallet scored on cpath paths, w5_copy's fetcher, has failed, while
# the screen's paths_full looked good.) The same copies, the same model and setting, on both: TAB16RxX's buys in the
# screen's days (in paths_full), each fetched again with cpath (Alchemy).
#   RPC_URL=... python3 -I e16_path_check.py SP WALLET "size,prem,tp,hold,sp,stall,its" [N]
import sys, os, json, gzip, numpy as np
here = os.path.dirname(os.path.abspath(__file__)); SP, WL, spec = sys.argv[1], sys.argv[2], sys.argv[3]; N = int(sys.argv[4]) if len(sys.argv) > 4 else 60
sys.argv = ["x", SP, WL]; exec(open(os.path.join(here, "e8_engineer.py")).read().split("rows = []")[0])
m5 = open(os.path.join(here, "m5_confirm.py")).read().split("def S(v):")[0]; sys.argv = ["x", SP, WL]; exec(m5)
z = spec.split(","); e_ix = (TP.index(float(z[2])), HOLD.index(int(z[3])), SPS.index(None if z[4] == "off" else tuple(int(x) for x in z[4].split("/"))), STALL.index(int(z[5])), ITS.index(z[6]))
L = {}
for f_ in (f"{O}/launches_1794618422.json", f"{O}/launches.json", f"{O}/launches_1794877622.json"): L.update({m: x for m, x in json.load(open(f_)).items() if x and os.path.exists(f"{PD}/{m}.json.gz")})
out = []
for m, x in L.items():
    if x["quote"][:8] not in FLOATS: continue
    r = rate_of(x["quote"]); tr = json.load(gzip.open(f"{PD}/{m}.json.gz")) if r else []
    k = next((j for j, e in enumerate(tr) if e["user"] == WL), None)
    if k is None or not tr[k]["buy"] or tr[-1]["t"] - tr[k]["t"] < 600 or tr[k]["q"] * (1 + tr[k]["bps"] / 1e4) * r / 1e9 < 0.5: continue
    out.append((tr[k]["t"], m, tr, k, r))
out.sort(); out = out[-N:]
a_, b_, rows_ = [], [], []
for t, m, tr, k, r in out:
    va = np.mean([copy_vals(H.prep(tr, k, r, n, pmax=1000))[e_ix] for n in (4, 8, "slot+1")]) - COST
    try: t2 = cpath(m, tr[k]["slot"], tr[k]["t"])
    except Exception as x: print(m[:8], "cpath failed", x); continue
    k2 = next((j for j, e in enumerate(t2) if e["user"] == WL and e["buy"] and e["slot"] == tr[k]["slot"]), None)
    if k2 is None: print(m[:8], "its buy not in the cpath path"); continue
    vb = np.mean([copy_vals(H.prep(t2, k2, r, n, pmax=1000))[e_ix] for n in (4, 8, "slot+1")]) - COST
    w = [e for e in tr if tr[k]["t"] <= e["t"] <= tr[k]["t"] + 600]; w2 = [e for e in t2 if tr[k]["t"] <= e["t"] <= tr[k]["t"] + 600]
    a_.append(va); b_.append(vb); rows_.append((m[:8], va, vb, len(w), len(w2), k, k2))
print(f"{len(a_)} copies scored on both: paths_full {sum(a_):+.3f} SOL, cpath {sum(b_):+.3f} SOL; same within 0.005 SOL: {sum(abs(x - y) < 0.005 for x, y in zip(a_, b_))}")
print("coin      paths_full   cpath   trades in 600 s (full / cpath)  its index (full / cpath)")
for r_ in rows_:
    if abs(r_[1] - r_[2]) >= 0.005: print(f"{r_[0]}  {r_[1]:+.4f}  {r_[2]:+.4f}   {r_[3]} / {r_[4]}   {r_[5]} / {r_[6]}")
