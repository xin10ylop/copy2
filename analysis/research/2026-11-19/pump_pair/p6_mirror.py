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

# p6 (Nov 19; after p5: our entry is within 3% of its own and the ceiling is +52% a copy, so the money is in WHEN it
# sells): MIRROR its sales. Its position on the coin = both wallets' tokens; at each of its sales we sell the same
# fraction of ours, at the curve's state just before block (its sale's block + L), L = 1, 2, 3; whatever is left is sold
# at the path's end (31 minutes). Our entry: landing 4 / 8 trades or the next slot, 0.5 SOL. Halves.
# (was p5: the owner: "maybe something else makes it work"): where the money goes. For each copy: our entry price
# against its own (the premium), the copy's CEILING (selling at the best moment after our entry, with hindsight), the copy
# had we bought at ITS price (landing 0), and the best grid exit under premium limits 1.05-1.5x (picked on one half).
# (was p4: the owner: "have you engineered the exit? make it work, or these are not the wallets"): every exit of the
# grid (take profit x hold x sell pressure x stall x its sale; holds from 10 s) and entry filters (its size, SOL or token
# coins) on our copy of the 8zqsUMty + FDhoU1DE trader, Nov 10-19, from the paths p3 fetched (cached). Picked on one half
# (Nov 10-14 or Nov 15-19, by the result without the best 2%), scored on the other.
#   python3 -I p4_exits.py SP 8zqsUMtyZUyX6W5MXs4WumXnnGa5sUuHQhqXRB9d8mMc 1794268800 x > out/p4_exits.txt
trades = sorted([e for l in open(f"{SP}/pair/{WL[:8]}_trades.jsonl") for e in (json.loads(l)["trades"] or [])], key=lambda e: e["t"])
m5 = open(os.path.join(here, "m5_confirm.py")).read().split("def S(v):")[0]; sys.argv = ["x", SP, WL]; exec(m5)
PAIR = {"8zqsUMtyZUyX6W5MXs4WumXnnGa5sUuHQhqXRB9d8mMc", "FDhoU1DEGR2ts3Dza2srrFahYtzPXUeCNTK615BwVWTM"}
def mirror(tr, k, j, r, L):
    """our copy entered after tr[j] (state after j), mirroring the pair's sales; SOL result"""
    e0 = tr[j]; vt0, vq0, b0 = e0["vt"], e0["vq"], e0["bps"]; Q = 0.5e9 / r; net_in = Q * 1e4 / (1e4 + b0)
    tok = vt0 - vt0 * vq0 / (vq0 + net_in); left = 1.0; got = 0.0
    def value(i, frac):   # selling frac of our tokens into the state after trade i (our buy added to it)
        vq, vt, b = tr[i]["vq"], tr[i]["vt"], tr[i]["bps"]; vq_r = vq + net_in; vt_r = vt * vq / vq_r; t_ = tok * frac
        return (vq_r - vt_r * vq_r / (vt_r + t_)) * (1 - b / 1e4) * r / 1e9
    held = sum(x["tok"] * (1 if x["buy"] else -1) for x in tr[:j + 1] if x["user"] in PAIR)
    for i in range(j + 1, len(tr)):
        x = tr[i]
        if x["user"] not in PAIR: continue
        if x["buy"]: held += x["tok"]; continue
        if held <= 0 or left <= 1e-9: continue
        f = min(1.0, x["tok"] / held) * left; held -= x["tok"]
        m = next((q for q in range(i + 1, len(tr)) if tr[q]["slot"] >= x["slot"] + L), len(tr)) - 1
        got += value(max(m, i), f); left -= f
        if held <= 1e-6 * tok: break
    if left > 1e-9: got += value(len(tr) - 1, left)
    return got - 0.5 - 0.0026 - COST
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
    js = [min(k + 4, len(tr) - 1), min(k + 8, len(tr) - 1), next((q for q in range(k + 1, len(tr)) if tr[q]["slot"] > tr[k]["slot"]), len(tr) - 1)]
    nsell = sum(1 for x in tr[k + 1:] if x["user"] in PAIR and not x["buy"])
    rows.append(dict(t=e["t"], solq=e["quote"] in SOLQ, nsell=nsell, v={L: float(np.mean([mirror(tr, k, j, r, L) for j in js])) for L in (1, 2, 3)}))
t = np.array([r["t"] for r in rows]); A = t < np.median(t); pc = lambda x: 100 * x.mean() / 0.5
print(f"{len(rows)} copies; the pair's sales after its buy, a coin: median {np.median([r['nsell'] for r in rows]):.0f}, 90% {np.percentile([r['nsell'] for r in rows], 90):.0f}")
for L in (1, 2, 3):
    x = np.array([r["v"][L] for r in rows]); k2 = max(1, round(0.02 * len(x)))
    print(f"MIRROR its sales, ours landing {L} block(s) after each: {x.sum():+.2f} SOL ({pc(x):+.1f}% a copy), halves {x[A].sum():+.2f} / {x[~A].sum():+.2f}, w/o 2% {np.sort(x)[:-k2].sum():+.2f}, won {int((x > 0).sum())}")
    for lab, f in (("SOL coins", np.array([r["solq"] for r in rows])), ("token coins", ~np.array([r["solq"] for r in rows]))):
        print(f"      {lab}: {f.sum()} copies {x[f].sum():+.2f} ({pc(x[f]):+.1f}%), halves {x[f & A].sum():+.2f} / {x[f & ~A].sum():+.2f}")
