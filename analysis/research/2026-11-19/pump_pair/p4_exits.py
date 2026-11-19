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

# p4 (Nov 19; the owner: "have you engineered the exit? make it work, or these are not the wallets"): every exit of the
# grid (take profit x hold x sell pressure x stall x its sale; holds from 10 s) and entry filters (its size, SOL or token
# coins) on our copy of the 8zqsUMty + FDhoU1DE trader, Nov 10-19, from the paths p3 fetched (cached). Picked on one half
# (Nov 10-14 or Nov 15-19, by the result without the best 2%), scored on the other.
#   python3 -I p4_exits.py SP 8zqsUMtyZUyX6W5MXs4WumXnnGa5sUuHQhqXRB9d8mMc 1794268800 x > out/p4_exits.txt
trades = sorted([e for l in open(f"{SP}/pair/{WL[:8]}_trades.jsonl") for e in (json.loads(l)["trades"] or [])], key=lambda e: e["t"])
m5 = open(os.path.join(here, "m5_confirm.py")).read().split("def S(v):")[0]; sys.argv = ["x", SP, WL]; exec(m5)
HOLD[:] = [10, 20, 30, 45, 60, 120, 180, 300, 600]
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
    prem = float(np.mean([(tr[k]["vt"] / p["ent"][0]) ** 2 for p in ps]))
    V = np.mean([np.where(prem <= 1.5, copy_vals(p), -0.0004) for p in ps], axis=0) - COST
    rows.append(dict(t=e["t"], sol=sol, solq=e["quote"] in SOLQ, V=V))
import itertools
t = np.array([r["t"] for r in rows]); A = t < np.median(t); V = np.array([r["V"] for r in rows]).reshape(len(rows), -1)
shape = rows[0]["V"].shape; names = list(itertools.product([("none" if x > 1e8 else x) for x in TP], HOLD, [("off" if x is None else "%d/%d" % x) for x in SPS], STALL, ITS))
def w2(x):
    k = max(1, round(0.02 * len(x))); return np.sort(x)[:-k].sum() if len(x) > k else x.sum()
print(f"{WL[:8]}: {len(rows)} copies Nov 10-19 (its 0.5+ SOL buys, priced), halves at {dt.datetime.fromtimestamp(np.median(t), dt.UTC):%m-%d %H:%M} UTC; {V.shape[1]} exits")
filters = {"all": np.ones(len(rows), bool), "SOL coins": np.array([r["solq"] for r in rows]), "token coins": ~np.array([r["solq"] for r in rows]),
           "its 1+ SOL": np.array([r["sol"] >= 1 for r in rows]), "its 2+ SOL": np.array([r["sol"] >= 2 for r in rows])}
for fn, f in filters.items():
    P, Q = f & A, f & ~A
    if P.sum() < 10 or Q.sum() < 10: continue
    sP = np.array([w2(V[P, j]) for j in range(V.shape[1])]); sQ = np.array([w2(V[Q, j]) for j in range(V.shape[1])])
    both = int(((V[P].sum(0) > 0) & (V[Q].sum(0) > 0) & (sP > 0) & (sQ > 0)).sum())
    j1, j2 = int(np.argmax(sP)), int(np.argmax(sQ))
    print(f"\n== {fn}: {P.sum()} / {Q.sum()} copies in the halves; exits positive on BOTH halves and w/o 2%: {both} of {V.shape[1]}")
    print(f"   picked on half 1: {names[j1]}: half 1 {V[P, j1].sum():+.2f} SOL ({100 * V[P, j1].mean() / 0.5:+.1f}%) -> half 2 {V[Q, j1].sum():+.2f} ({100 * V[Q, j1].mean() / 0.5:+.1f}%)")
    print(f"   picked on half 2: {names[j2]}: half 2 {V[Q, j2].sum():+.2f} SOL ({100 * V[Q, j2].mean() / 0.5:+.1f}%) -> half 1 {V[P, j2].sum():+.2f} ({100 * V[P, j2].mean() / 0.5:+.1f}%)")
    best = int(np.argmax(np.minimum(sP, sQ))); print(f"   the best on both at once (hindsight): {names[best]}: {V[P, best].sum():+.2f} / {V[Q, best].sum():+.2f}, w/o 2% {sP[best]:+.2f} / {sQ[best]:+.2f}")
