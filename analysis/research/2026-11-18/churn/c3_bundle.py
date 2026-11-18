# The whole ladder (the owner, Nov 18: "is the whole ladder doing that?"). The ladder is not three wallets: the launch
# slot holds one or two bundled transactions with about ten wallets each buying (1.54, 2.18, 2.42 ... 3.49, 0.81, 1.10,
# 1.20 SOL). Per pooled coin (true in-slot order): the bundle = every create-slot buyer in a transaction that holds a
# ladder-size buy; its wallets, SOL in, and what the bundle wallets do in the next 120 s (sales, SOL out); the price at
# the end of the create slot over the bundle's first price; the high and the price 30 / 120 s later over the slot's end.
#   python3 -I c3_bundle.py SP W8:SUFFIX:RES ... > out/c3_bundle.txt
import sys, os, json, collections, numpy as np, datetime as d
SP = sys.argv[1]; S0 = int(os.environ.get("S0", 1794923340)); here = "/home/user/copy2/analysis/research/2026-11-17/winners"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import slot_order
src = open(f"{here}/wallet_study.py").read().split("def one(ix):")[0]; SIZES = (1.10, 1.54, 2.18)
seen = set(); rows = []
for arg in sys.argv[2:]:
    w, suf, res = arg.split(":"); os.environ["RES"] = res
    sys.argv = ["x", SP, w, "300", "1800"]; ns = {"__file__": f"{here}/wallet_study.py", "__name__": "ws"}; exec(compile(src, "wallet_study.py", "exec"), ns)
    cpath, own = ns["cpath"], ns["own"]
    for r in json.load(open(f"{SP}/winners/study_{w}{suf}.json")):
        if r["refused"] or r["t"] < S0 or r["m"] in seen: continue
        seen.add(r["m"]); b = next((e for e in own.get(r["m"], []) if e["buy"]), None)
        tr = slot_order.reorder(cpath(r["m"], b["slot"], b["t"])); s0 = tr[0]["slot"]; t0 = tr[0]["t"]
        cs = [e for e in tr if e["slot"] == s0]
        sigs = {e["sig"] for e in cs if e["buy"] and any(abs(e["q"] / 1e9 - s) <= 0.005 for s in SIZES)}
        bun = [e for e in cs if e["sig"] in sigs and e["buy"]]; W = {e["user"] for e in bun}
        px = lambda e: e["vq"] / e["vt"]; end = px(cs[-1]); p0 = px(bun[0]) if bun else end
        later = [e for e in tr if e["slot"] > s0 and e["t"] - t0 <= 120]
        bs = [e for e in later if e["user"] in W and not e["buy"]]; bb = [e for e in later if e["user"] in W and e["buy"]]
        ob = [e for e in later if e["user"] not in W and e["buy"]]
        def at(s): x = [e for e in tr if e["t"] - t0 <= s]; return px(x[-1]) / end
        hi = max([px(e) for e in later], default=end) / end
        rows.append(dict(m=r["m"], t=r["t"], ntx=len(sigs), nw=len(W), sol_in=sum(e["q"] for e in bun) / 1e9, rise=end / p0,
                         sells=len(bs), sol_out=sum(e["q"] for e in bs) / 1e9, rebuys=len(bb), out_n=len({e["user"] for e in ob}),
                         out_sol=sum(e["q"] for e in ob) / 1e9, p30=at(30), p120=at(120), hi=hi,
                         left=1 - sum(e["tok"] for e in bs) / max(1, sum(e["tok"] for e in bun))))
R = rows; f = lambda k: np.median([r[k] for r in R])
print(f"{len(R)} coins (Nov 17 13:49 on). Medians: bundle txs {f('ntx'):.0f}, wallets {f('nw'):.0f}, SOL in {f('sol_in'):.1f}, the price over the slot x{f('rise'):.2f}")
print(f"   in the 120 s after: bundle sales {f('sells'):.0f} ({f('sol_out'):.1f} SOL), bundle re-buys {f('rebuys'):.0f}, share of the bundle's tokens still held {f('left'):.0%}")
print(f"   outside buyers {f('out_n'):.0f} ({f('out_sol'):.1f} SOL); price over the slot's end: 30 s x{f('p30'):.2f}, 120 s x{f('p120'):.2f}, high x{f('hi'):.2f}")
print(f"   coins whose bundle sold within 120 s: {sum(1 for r in R if r['sells'] > 0)} of {len(R)}; sold over half its tokens: {sum(1 for r in R if r['left'] < 0.5)}")
print(f"   coins whose high in 120 s is 1.2x the slot's end or more: {sum(1 for r in R if r['hi'] >= 1.2)}; at 120 s still 1.2x+: {sum(1 for r in R if r['p120'] >= 1.2)}")
print("\nper coin: time, mint | bundle txs/wallets/SOL in, rise in the slot | 120 s: bundle sales (SOL), re-buys, tokens left | outside buyers (SOL) | price at 30 s, 120 s, high")
for r in sorted(R, key=lambda r: r["t"]):
    print(f"   {d.datetime.fromtimestamp(r['t'], d.UTC):%m-%d %H:%M} {r['m'][:8]} | {r['ntx']}tx {r['nw']:2d}w {r['sol_in']:5.1f} x{r['rise']:.2f} | {r['sells']:3d}s ({r['sol_out']:5.1f}) {r['rebuys']:2d}b {r['left']:4.0%} | {r['out_n']:3d} ({r['out_sol']:5.1f}) | x{r['p30']:.2f} x{r['p120']:.2f} hi x{r['hi']:.2f}")
