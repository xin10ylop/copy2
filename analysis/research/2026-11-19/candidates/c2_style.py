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
trades = sorted([e for l in open(f"{SP}/cands/{WL[:8]}_trades.jsonl") for e in (json.loads(l)["trades"] or [])], key=lambda e: e["t"])
m5 = open(os.path.join(here, "m5_confirm.py")).read().split("def S(v):")[0]; sys.argv = ["x", SP, WL]; exec(m5)

# c2 (Nov 19): an m16 candidate's FROZEN style (entry and exit picked on Nov 14-15) on its own history, the days m16
# never saw (before Nov 14 01:07 and after Nov 18 01:07 UTC) and the 4 days, by week; beside it the plain copy with the
# same exit. Paths fetched as p3 does (31 minutes from its buy, Triton).
#   STYLE="dip,0.05,60" EXIT="1.5,60,1" python3 -I c2_style.py SP WALLET T0 x > out/c2_<w8>.txt
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt/market"); import m14_dip_after as D
kind, dd, ww = os.environ["STYLE"].split(","); dd, ww = float(dd), int(ww); tp_, h_, tr_ = os.environ["EXIT"].split(",")
GI = D.GRID.index((float(tp_) if float(tp_) < 1e8 else 1e9, int(h_), tr_ == "1"))
A4, B4 = 1794618422, 1794963942
# NS: a random sample (seed 7) of its first buys of 0.5+ SOL, over the whole period (a very active wallet buys thousands)
import random
_first, _seen = [], set()
for e in trades:
    if e["buy"] and e["m"] not in _seen:
        _seen.add(e["m"]); r_ = rate_of(e["quote"])
        if r_ is not None and e["q"] * (1 + e["bps"] / 1e4) * r_ / 1e9 >= 0.5: _first.append(e)
NS = int(os.environ.get("NS", 0))
if NS and len(_first) > NS: _first = sorted(random.Random(7).sample(_first, NS), key=lambda e: e["t"])
print(f"{len(_first)} first buys of 0.5+ SOL in the sample" + (f" (of {len(_seen)} coins bought; NS={NS})" if NS else ""))
trades = _first
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
    pk = tr[k]["vq"] / tr[k]["vt"]
    j0 = next((i for i in range(k + 1, len(tr)) if tr[i]["slot"] > tr[k]["slot"]), None)
    if kind == "plain": j = j0
    elif kind == "dip": j = next((i for i in range(k + 1, len(tr)) if tr[i]["t"] - tr[k]["t"] <= ww and tr[i]["slot"] > tr[k]["slot"] and tr[i]["vq"] / tr[i]["vt"] <= (1 - dd) * pk), None)
    else: j = next((i for i in range(k + 1, len(tr)) if tr[i]["t"] - tr[k]["t"] >= ww), None)
    vs = D.grid_from(tr, k, j, r) if j is not None and j < len(tr) - 1 else None
    v0 = D.grid_from(tr, k, j0, r) if j0 is not None and j0 < len(tr) - 1 else None
    rows.append(dict(t=e["t"], v=vs[GI] if vs else None, v0=v0[GI] if v0 else None))
def show(lab, f):
    x = np.array([r["v"] for r in rows if f(r["t"]) and r["v"] is not None]); y = np.array([r["v0"] for r in rows if f(r["t"]) and r["v0"] is not None])
    if not len(x): print(f"   {lab}: no trades"); return
    k = max(1, round(0.02 * len(x)))
    print(f"   {lab}: style {len(x)} trades {x.sum():+.2f} SOL ({100 * x.mean() / 0.5:+.1f}%), w/o 2% {np.sort(x)[:-k].sum():+.2f} | plain copy same exit {len(y)} {y.sum():+.2f} ({100 * y.mean() / 0.5 if len(y) else 0:+.1f}%)")
print(f"{WL[:12]}: {len(rows)} buys of 0.5+ SOL since {dt.datetime.fromtimestamp(T0, dt.UTC):%m-%d}; style {kind} {dd} {ww}, exit {D.GRID[GI]}")
show("BEFORE the 4 days (unseen)", lambda t: t < A4); show("the 4 days (where it was picked)", lambda t: A4 <= t < B4); show("AFTER the 4 days (unseen)", lambda t: t >= B4)
import collections; wk = collections.defaultdict(list)
for r in rows:
    if r["v"] is not None: wk[dt.datetime.fromtimestamp(r["t"] - (r["t"] - 1792540800) % (7 * 86400), dt.UTC).strftime("%m-%d")].append(r["v"])
print("   by week (style): " + "  ".join(f"{w} {sum(v):+.2f} ({len(v)})" for w, v in sorted(wk.items())))
