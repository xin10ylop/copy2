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

# p5 (Nov 19; the owner: "maybe something else makes it work"): where the money goes. For each copy: our entry price
# against its own (the premium), the copy's CEILING (selling at the best moment after our entry, with hindsight), the copy
# had we bought at ITS price (landing 0), and the best grid exit under premium limits 1.05-1.5x (picked on one half).
# (was p4: the owner: "have you engineered the exit? make it work, or these are not the wallets"): every exit of the
# grid (take profit x hold x sell pressure x stall x its sale; holds from 10 s) and entry filters (its size, SOL or token
# coins) on our copy of the 8zqsUMty + FDhoU1DE trader, Nov 10-19, from the paths p3 fetched (cached). Picked on one half
# (Nov 10-14 or Nov 15-19, by the result without the best 2%), scored on the other.
#   python3 -I p4_exits.py SP 8zqsUMtyZUyX6W5MXs4WumXnnGa5sUuHQhqXRB9d8mMc 1794268800 x > out/p4_exits.txt
trades = sorted([e for l in open(f"{SP}/pair/{WL[:8]}_trades.jsonl") for e in (json.loads(l)["trades"] or [])], key=lambda e: e["t"])
m5 = open(os.path.join(here, "m5_confirm.py")).read().split("def S(v):")[0]; sys.argv = ["x", SP, WL]; exec(m5)
HOLD[:] = [10, 20, 30, 45, 60, 120, 180, 300, 600]
def ceiling(p):
    if p["refused"] or not len(p["px"]): return -0.0004
    vt0, vq0, b0 = p["ent"]; Q = 0.5e9 * p["hopf"] / p["rate"]; net_in = Q * 1e4 / (1e4 + b0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq, vt, b = p["vq"], p["vt"], p["bps"]; vq_r = vq + net_in; vt_r = vt * vq / vq_r
    return float(np.max((vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - b / 1e4) * p["rate"] * p["hopf"] / 1e9 - 0.5 - 0.0026))
seen, rows = set(), []
for e in trades:
    if not e["buy"] or e["m"] in seen: continue
    seen.add(e["m"]); r = rate_of(e["quote"])
    if r is None: continue
    sol = e["q"] * (1 + e["bps"] / 1e4) * r / 1e9
    if sol < 0.5: continue
    try: tr = cpath(e["m"], e["slot"], e["t"])
    except Exception: continue
    k = next((j for j, y in enumerate(tr) if y["user"] == WL and y["buy"] and y["slot"] == e["slot"]), None)
    if k is None: continue
    ps = [H.prep(tr, k, r, n, pmax=1000) for n in (4, 8, "slot+1")]
    for p in ps: p["rate"] = r
    p0 = H.prep(tr, k, r, 0, pmax=1000); p0["rate"] = r
    prems = [(tr[k]["vt"] / p["ent"][0]) ** 2 for p in ps]
    rows.append(dict(t=e["t"], prem=float(np.mean(prems)), ceil=float(np.mean([ceiling(p) for p in ps])) - COST, ceil0=ceiling(p0) - COST,
                     V=np.mean([copy_vals(p) for p in ps], axis=0) - COST, V0=copy_vals(p0) - COST))
t = np.array([r["t"] for r in rows]); A = t < np.median(t); V = np.array([r["V"].ravel() for r in rows]); V0 = np.array([r["V0"].ravel() for r in rows])
prem = np.array([r["prem"] for r in rows]); ce = np.array([r["ceil"] for r in rows]); ce0 = np.array([r["ceil0"] for r in rows])
pc = lambda x: 100 * x.mean() / 0.5
print(f"{len(rows)} copies; our entry against its price: median {np.median(prem):.2f}x, 75% {np.percentile(prem, 75):.2f}x, 90% {np.percentile(prem, 90):.2f}x")
print(f"\nTHE CEILING (sold at the best moment, hindsight): {ce.sum():+.2f} SOL ({pc(ce):+.1f}% a copy); halves {ce[A].sum():+.2f} / {ce[~A].sum():+.2f}")
print(f"   had we bought at ITS price: ceiling {ce0.sum():+.2f} SOL ({pc(ce0):+.1f}%)")
j = int(np.argmax(V.sum(0))); j0 = int(np.argmax(V0.sum(0)))
print(f"best single grid exit with hindsight: ours {V[:, j].sum():+.2f} SOL ({pc(V[:, j]):+.1f}%); at ITS price the best exit {V0[:, j0].sum():+.2f} ({pc(V0[:, j0]):+.1f}%)")
print("\npremium limit (skip copies landing above it): copies, best exit picked on half 1 -> half 2, picked on half 2 -> half 1, ceiling a copy")
def w2(x):
    k = max(1, round(0.02 * len(x))); return np.sort(x)[:-k].sum() if len(x) > k else x.sum()
for lim in (1.05, 1.1, 1.2, 1.3, 1.5, 99):
    f = prem <= lim; P, Qh = f & A, f & ~A
    if P.sum() < 5 or Qh.sum() < 5: print(f"   {lim:4}x: {f.sum()} copies (too few)"); continue
    j1 = int(np.argmax([w2(V[P, i]) for i in range(V.shape[1])])); j2 = int(np.argmax([w2(V[Qh, i]) for i in range(V.shape[1])]))
    print(f"   {lim:4}x: {f.sum():3d} copies | {V[P, j1].sum():+.2f} -> {V[Qh, j1].sum():+.2f} | {V[Qh, j2].sum():+.2f} -> {V[P, j2].sum():+.2f} | ceiling {pc(ce[f]):+.1f}%")
