# 6ua7w2Gv's deeper study, the exploration (PREREG_6ua7w2Gv.md): its sampled copies joined to w9_buyctx's context, each
# signal cut into fixed groups (not fitted cuts), every group under the exit sell pressure 5/60 and its own sale, by halves
# of time, at COST SOL a round trip (default 0.0345), with the share of the group the VIP alerted after its buy (the
# mechanism: its profit is in those coins).
#   python3 -I w10_explore.py SP WALLET8 SUFFIX > out/explore_<w8>.txt
import sys, os, json, numpy as np
SP, W8, SUF = sys.argv[1], sys.argv[2], sys.argv[3]; COST = float(os.environ.get("COST", 0.0345))
R = sorted((r for r in json.load(open(f"{SP}/winners/study_{W8}{SUF}.json")) if not r["refused"]), key=lambda r: r["t"])
CTX = json.load(open(f"{SP}/winners/ctx_{W8}{SUF}.json"))
VIP = {}
for f in (f"{SP}/tg/vip/meta.json", f"{SP}/tg/vip2/meta.json"):
    for m, v in json.load(open(f)).items(): VIP.setdefault(m, v["t"])
for r in R:
    r["ex"] = {k: v - (COST - 0.0026) for k, v in r["ex"].items()}; c = CTX.get(f"{r['m']}:{r['t']}") or {}; r["c"] = c; cr = c.get("create") or {}
    r["age"] = r["t"] - cr["t"] if cr else None; r["alert"] = VIP.get(r["m"]) is not None and 0 < VIP[r["m"]] - r["t"] <= 600
half = R[len(R) // 2]["t"]
def S(v):
    if not v: return "  0" + " " * 33
    s = sorted(v); return f"{len(v):3d} {sum(v):+6.2f} ({100 * np.mean(v) / 0.5:+6.1f}%) w/o5 {sum(s[:-5]) if len(s) > 5 else 0.0:+6.2f}"
print(f"{W8}: {len(R)} copies at {COST} SOL a round trip; with a create read {sum(1 for r in R if r['c'].get('create'))}; VIP alerted after its buy {sum(r['alert'] for r in R)}")
def show(name, key):
    G = {}
    for r in R: G.setdefault(key(r), []).append(r)
    print(f"\n{name}:   group | sell pressure 5/60: 1st half | 2nd half | its sale, all | VIP alerted after")
    for k in sorted(G, key=str):
        X = G[k]; a = [r["ex"]["sp5/60s"] for r in X if r["t"] < half]; b = [r["ex"]["sp5/60s"] for r in X if r["t"] >= half]
        print(f"   {str(k)[:22]:22s} {S(a)} | {S(b)} | {S([r['ex']['its-sale'] for r in X])} | {sum(r['alert'] for r in X) / len(X):4.0%}")
def cut(x, cuts):
    if x is None: return "unknown"
    for c in cuts:
        if x <= c: return f"<= {c:g}"
    return f"> {cuts[-1]:g}"
cr = lambda r: r["c"].get("create") or {}
show("mayhem", lambda r: cr(r).get("mayhem", "unknown"))
show("tips in the create (SOL)", lambda r: cut(cr(r).get("tips"), [0, 0.001]))
show("dev buy in the create (SOL)", lambda r: cut(cr(r).get("dev_buy"), [0, 0.5, 2]))
show("creator fee bps", lambda r: cr(r).get("cfee", "unknown"))
show("coin age at its buy (s)", lambda r: cut(r["age"], [10, 60, 300, 1800]))
show("curve sold at its buy", lambda r: cut(r["prog"], [0.2, 0.4, 0.6, 0.8]))
show("its size (SOL)", lambda r: cut(r["sol"], [0.4, 0.55, 0.8]))
show("others' buys in the 60 s before", lambda r: cut(r["c"].get("pre_buys"), [2, 5, 10, 20]))
show("distinct buyers in the 60 s before", lambda r: cut(r["c"].get("pre_buyers"), [2, 5, 10]))
show("net SOL in, 60 s before (in - out)", lambda r: cut((r["c"].get("pre_in", 0) - r["c"].get("pre_out", 0)) / 1e9 if r["c"] else None, [0, 2, 5, 10]))
show("sells / buys, 60 s before", lambda r: cut(r["c"]["pre_sells"] / max(1, r["c"]["pre_buys"]) if r["c"] else None, [0.25, 0.5, 1]))
show("hour (UTC)", lambda r: cut(r["hour"], [5, 11, 17]))
