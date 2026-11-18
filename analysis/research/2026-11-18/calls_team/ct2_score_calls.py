# Our copy of a Telegram call, on chain (Nov 18): for each call of ct1 on a pump coin still on its SOL curve, the
# coin's trades from 2 minutes before to 16 minutes after the call (the curve's signatures, paged back from now at most
# PAGES pages, then batched getTransaction: no history beyond the window), true in-slot order; our 0.5 SOL buy lands 4
# or 8 trades after the market state DELAY s after the call, or in the next slot (the mean of the three), 0.0345 SOL a
# round trip, refused above the price limit; every exit of e8 (tp x time x sell pressure x stall; no "its sale": a
# caller has no sale on chain we know). Halves by time. Out: ../../2026-11-17/wallet_hunt/out style text.
#   RPC_URL=... python3 -I ct2_score_calls.py SP > out/ct2.txt
import sys, os, json, gzip, numpy as np, datetime as dt, collections
SP = sys.argv[1]; DELAY = float(os.environ.get("DELAY", 3)); PAGES = int(os.environ.get("PAGES", 6))
E8 = "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt/market/e8_engineer.py"
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt"); sys.argv = ["x", SP, "x"]; exec(open(E8).read().split("rows = []")[0].replace("here = os.path.dirname(os.path.abspath(__file__))", "here = os.path.dirname(E8)"))          # copy_vals, TP, HOLD, SPS, STALL, H, SO, COST
W5 = "/home/user/copy2/analysis/research/2026-11-17/winners/w5_copy.py"
ns = {"__file__": W5}; sys.argv = ["x", SP, "6ua7w2Gv"]; exec(compile(open(W5).read().split("EX = [")[0], "w5_copy.py", "exec"), ns)
call, _txs, curve, M = ns["call"], ns["_txs"], ns["curve"], ns["M"]
CD = f"{SP}/ct/paths"; os.makedirs(CD, exist_ok=True)
# the PumpSwap pool of a graduated coin (2026-11-18/pools/p1_fetch.py's reader: the pool's balances after each trade,
# each signer's token and SOL change); a pool row is put in the curve's form (vt = the pool's tokens, vq = its SOL:
# the same constant product), 30 bps a trade (PumpSwap's LP + protocol + creator fees, about)
PF = open("/home/user/copy2/analysis/research/2026-11-18/pools/p1_fetch.py").read()
pns = {}; exec(PF[PF.index("PUMP = Pubkey"):PF.index("def one(item)")].replace("URL", "RPC"), dict(pns, RPC=os.environ["RPC_URL"], Pubkey=__import__("solders.pubkey", fromlist=["Pubkey"]).Pubkey, time=__import__("time"), os=os, json=json), pns) if False else None
_g = {"RPC": os.environ["RPC_URL"], "time": __import__("time"), "os": os, "json": json}
exec("from solders.pubkey import Pubkey\n" + PF[PF.index("PUMP = Pubkey"):PF.index("def one(item)")].replace("URL", "RPC"), _g)
def pool_path(m, t):
    f = f"{CD}/{m}_{int(t)}_pool.json.gz"
    if os.path.exists(f): return json.load(gzip.open(f))
    pool, sigs, before, reached = _g["pool_of"](m), [], None, False
    for _ in range(PAGES + 4):
        pg = call("getSignaturesForAddress", [pool, {"limit": 1000, **({"before": before} if before else {})}])
        if not pg: reached = True; break
        sigs += [s for s in pg if s["err"] is None and t - 120 <= (s.get("blockTime") or 0) <= t + 960]
        before = pg[-1]["signature"]
        if len(pg) < 1000 or (pg[-1].get("blockTime") or 0) < t - 120: reached = True; break
    tr = None
    if reached:
        sigs = sorted(sigs, key=lambda s: s["slot"]); tr = []
        for s_, tx in zip(sigs, _txs(sigs) if sigs else []):
            for e in _g["trades"](tx, m, pool):
                tr.append(dict(slot=e["slot"], t=e["t"], sig=s_["signature"], user=e["user"], buy=e["tok"] > 0, q=abs(e["sol"]), tok=abs(e["tok"]),
                               vt=e["rb"], vq=e["rq"], bps=30, real=1))
    with gzip.open(f + ".tmp", "wt") as fh: json.dump(tr, fh)
    os.replace(f + ".tmp", f); return tr
def path(m, t):
    f = f"{CD}/{m}_{int(t)}.json.gz"
    if os.path.exists(f): return json.load(gzip.open(f))
    c, sigs, before, reached = curve(m), [], None, False
    for _ in range(PAGES):
        pg = call("getSignaturesForAddress", [c, {"limit": 1000, **({"before": before} if before else {})}])
        if not pg: reached = True; break
        sigs += [s for s in pg if s["err"] is None and t - 120 <= (s.get("blockTime") or 0) <= t + 960]
        before = pg[-1]["signature"]
        if len(pg) < 1000 or (pg[-1].get("blockTime") or 0) < t - 120: reached = True; break
    if not reached: tr = None
    else:
        sigs = sorted(sigs, key=lambda s: s["slot"]); tr = SO.reorder([e for tx in _txs(sigs) if tx for e in M.trades(tx, m)]) if sigs else []
    with gzip.open(f + ".tmp", "wt") as fh: json.dump(tr, fh)
    os.replace(f + ".tmp", f); return tr
C = json.load(open(f"{SP}/ct/calls.json")); now = max(x["t"] for x in C)
C = [x for x in C if x["mint"].endswith("pump") and x["t"] <= now - 1000]
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(6) as ex: P = list(ex.map(lambda x: path(x["mint"], x["t"]), C))
# a coin with no curve trade around the call: its pool (graduated before the call)
def near(tr, t): return tr is not None and any(e["t"] >= t - 120 for e in tr)
need = [i for i, (x, tr) in enumerate(zip(C, P)) if tr is not None and not near(tr, x["t"])]
with ThreadPoolExecutor(6) as ex: PP = dict(zip(need, ex.map(lambda i: pool_path(C[i]["mint"], C[i]["t"]), need)))
VEN = ["curve"] * len(C)
for i, tr in PP.items():
    if tr: P[i] = tr; VEN[i] = "pool"
rows, why = [], collections.Counter()
for x, tr, ven in zip(C, P, VEN):
    if tr is None: why["too busy to page back (skipped)"] += 1; continue
    tr = [e for e in tr if e["t"] >= x["t"] - 120]
    if not tr: why["no curve trade near the call (graduated or dead)"] += 1; continue
    if ven == "curve" and not (2.9e10 <= tr[0]["vq"] <= 1.2e11): why["not a SOL curve (priced in another token)"] += 1; continue
    k = max([i for i, e in enumerate(tr) if e["t"] <= x["t"] + DELAY] or [0])
    if tr[-1]["t"] - tr[k]["t"] < 30: why["under 30 s of trades after the call"] += 1
    ps = [H.prep(tr, k, 1.0, n, pmax=1000) for n in (4, 8, "slot+1")]
    vl = np.array([copy_vals(p)[:, :, :, :, 0] for p in ps]) - COST          # its sale: never
    rows.append(dict(c=x["caller"], t=x["t"], o=x["order"] or 99, ven=ven, prem=[(tr[k]["vt"] / p["ent"][0]) ** 2 for p in ps], vl=vl,
                     mc=tr[k]["vq"] / tr[k]["vt"] * 1e6 * 1e9 / 1e9))
print(f"{len(C)} calls on pump coins at least 1,000 s old; modelled {len(rows)}; not modelled: {dict(why)}")
rows.sort(key=lambda r: r["t"]); T = np.array([r["t"] for r in rows]); A = T < np.median(T)
print(f"from {dt.datetime.fromtimestamp(T.min(), dt.UTC):%m-%d %H:%M} to {dt.datetime.fromtimestamp(T.max(), dt.UTC):%m-%d %H:%M} UTC; halves at {dt.datetime.fromtimestamp(np.median(T), dt.UTC):%m-%d %H:%M}; our buy {DELAY:.0f} s after the call, then 4 / 8 trades or the next slot")
PM = [1.1, 1.25, 1.5, 1e9]
def V(sel, pm):
    """(copies, exits) values for the rows in sel at price limit pm (refused per landing)."""
    out = []
    for r in (r for r, s in zip(rows, sel) if s):
        out.append(np.mean([r["vl"][l] if r["prem"][l] <= pm else np.full(r["vl"][l].shape, -0.0004) for l in range(3)], axis=0))
    return np.array(out)
def name(ix, pm): t, h, sp, st = ix; return f"limit {'none' if pm > 1e8 else str(pm) + 'x'}, tp {'none' if TP[t] > 1e8 else str(TP[t]) + 'x'}, {HOLD[h]} s, sell pressure {'off' if SPS[sp] is None else f'{SPS[sp][0]}/{SPS[sp][1]}s'}, stall {STALL[st] or 'off'}"
def show(lab, sel):
    sel = np.array(sel); n = sel.sum()
    if n < 10: print(f"\n{lab}: {n} copies, too few"); return
    best = None; pos = both = tot = 0
    for pm in PM:
        v = V(sel, pm); a, b = V(sel & A, pm), V(sel & ~A, pm)
        if not len(a) or not len(b): continue
        s, s1, s2 = v.sum(0), a.sum(0), b.sum(0); tot += s.size; pos += int((s > 0).sum()); both += int(((s1 > 0) & (s2 > 0)).sum())
        w = np.minimum(s1, s2); j = np.unravel_index(int(np.argmax(w)), w.shape)
        if best is None or w[j] > best[0]: best = (w[j], pm, j, s[j], s1[j], s2[j], v[(slice(None),) + j])
    if best is None: print(f"\n{lab}: {n} copies, one half empty"); return
    w, pm, j, s, s1, s2, x = best; bs = np.random.default_rng(7).choice(x, size=(10000, len(x))).mean(1); k = max(1, round(0.02 * len(x)))
    print(f"\n{lab}: {n} copies (halves {int((sel & A).sum())} / {int((sel & ~A).sum())}); settings making money {pos:,} of {tot:,}, on both halves {both:,}")
    print(f"   best by its weaker half (hindsight): {name(j, pm)}: {s:+.2f} SOL ({100 * x.mean() / 0.5:+.1f}% a copy), halves {s1:+.2f} / {s2:+.2f}, w/o 2% {np.sort(x)[:-k].sum():+.2f}, won {100 * np.mean(x > 0):.0f}%, P(mean>0) {100 * np.mean(bs > 0):.1f}%")
    for lab2, spec in (("wallet 4's exit", (TP.index(4), HOLD.index(600), SPS.index((5, 60)), STALL.index(180))), ("quick: tp 2x, 120 s", (TP.index(2), HOLD.index(120), 0, 0))):
        x = V(sel, 1.5)[(slice(None),) + spec]; print(f"   {lab2} (limit 1.5x): {x.sum():+.2f} SOL ({100 * x.mean() / 0.5:+.1f}% a copy), won {100 * np.mean(x > 0):.0f}%")
show("ALL CALLS", [True] * len(rows))
show("CALLED FIRST (#1)", [r["o"] == 1 for r in rows])
show("CALLED LATER (#2+)", [r["o"] != 1 for r in rows])
show("ON THE CURVE AT THE CALL", [r["ven"] == "curve" for r in rows])
show("IN THE POOL AT THE CALL (graduated)", [r["ven"] == "pool" for r in rows])
for c in sorted({r["c"] for r in rows}): show(f"caller {c}", [r["c"] == c for r in rows])
