# Did TAB16RxX change? (Nov 18, the owner: "it never performed this badly on the backtest, it is not a coincidence")
# Its own trades day by day since T0 (fetched, Alchemy, batched): coins, buy sizes, its own result per coin (quote in vs
# out), how long it holds, the share of its sales at 200-220 s, and which quote tokens.
#   RPC_URL=... python3 -I e15_tab_change.py SP WALLET T0
import sys, os, json, collections, statistics as st, datetime as dt
SP, WL, T0 = sys.argv[1], sys.argv[2], int(sys.argv[3])
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
tr = sorted([e for tx in txs if tx for e in ns["own_trades"](tx, WL)], key=lambda e: e["t"])
json.dump(tr, open(f"{SP}/market/tab_trades_since_{T0}.json", "w"))
C = collections.defaultdict(list)
for e in tr: C[e["m"]].append(e)
D = collections.defaultdict(list)
for m, es in C.items():
    b = [e for e in es if e["buy"]]; s = [e for e in es if not e["buy"]]
    if not b: continue
    t0 = b[0]["t"]; qin = sum(e["q"] for e in b); qout = sum(e["q"] for e in s)
    D[dt.datetime.fromtimestamp(t0, dt.UTC).strftime("%m-%d")].append(dict(quote=(b[0]["quote"] or "SOL")[:8], pct=100 * (qout / qin - 1) if s else None,
        hold=(s[0]["t"] - t0) if s else None, nb=len(b), ns=len(s), sz=b[0]["q"]))
print(f"{WL[:8]}: {len(sigs)} transactions since {dt.datetime.fromtimestamp(T0, dt.UTC):%m-%d}, {len(tr)} own trades")
print("day   | coins | its result a coin: mean / median / won | hold median s | sold 200-220 s | top quotes")
for d_ in sorted(D):
    x = D[d_]; p = [r["pct"] for r in x if r["pct"] is not None]; h = [r["hold"] for r in x if r["hold"] is not None]
    q = collections.Counter(r["quote"] for r in x).most_common(3)
    print(f"{d_} | {len(x):5d} | {st.mean(p) if p else 0:+6.1f}% / {st.median(p) if p else 0:+6.1f}% / {100 * sum(v > 0 for v in p) / max(1, len(p)):3.0f}% | "
          f"{st.median(h) if h else 0:6.0f} | {100 * sum(200 <= v <= 220 for v in h) / max(1, len(h)):3.0f}% | {q}")
