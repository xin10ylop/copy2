# The audit of the frozen flip's +51% (Nov 18): a take profit at 1.2x our entry cannot average +51% unless the exits
# fill far above 1.2x. Per pooled coin (t6's inputs): our entry over its price (e0), the exit index and reason, the
# price at the trigger and at the fill, the fill's age, the copy's value; and how many copies fill above 1.5x.
#   python3 -I c0_flip_audit.py SP W8:SUFFIX:RES ... > out/c0_flip_audit.txt
import sys, os, json, numpy as np
SP = sys.argv[1]; S0 = int(os.environ.get("S0", 1794923340)); here = "/home/user/copy2/analysis/research/2026-11-17/winners"
src = open(f"{here}/wallet_study.py").read().split("def one(ix):")[0]
seen = set(); out = []
for arg in sys.argv[2:]:
    w, suf, res = arg.split(":"); os.environ["RES"] = res
    sys.argv = ["x", SP, w, "300", "1800"]; ns = {"__file__": f"{here}/wallet_study.py", "__name__": "ws"}; exec(compile(src, "wallet_study.py", "exec"), ns)
    sim, cpath, H, own, full, rate_of = ns["sim"], ns["cpath"], ns["H"], ns["own"], ns["full"], ns["rate_of"]
    for r in json.load(open(f"{SP}/winners/study_{w}{suf}.json")):
        if r["refused"] or r["t"] < S0 or r["m"] in seen: continue
        seen.add(r["m"]); b = next((e for e in own.get(r["m"], []) if e["buy"]), None)
        tr = cpath(r["m"], b["slot"], b["t"]); k = next((j for j, y in enumerate(tr) if y["user"] == full and y["buy"] and y["slot"] == b["slot"]), None)
        p = H.prep(tr, k, rate_of(b["quote"]), "slot+1", pmax=1000)
        e0 = (tr[k]["vt"] / p["ent"][0]) ** 2; v = sim(p, tp=1.2 * e0, hold=30) - 0.0319
        px, age = p["px"], p["age"]; n = len(px)
        it = H.first(px >= 1.2 * e0); ih = H.first(age >= 30)
        if it is not None and (ih is None or it < ih): why, i = "tp", min(it + 1, n - 1)
        elif ih is not None: why, i = "30s", ih
        else: why, i = "end", n - 1
        out.append(dict(m=r["m"], t=r["t"], e0=e0, why=why, n=n, trig=float(px[it]) / e0 if it is not None else None,
                        fill=float(px[i]) / e0 if n else None, age=float(age[i]) if n else None, v=v, first=float(px[0]) / e0 if n else None))
v = np.array([o["v"] for o in out])
print(f"{len(out)} coins, {v.sum():+.2f} SOL ({100 * v.mean() / 0.5:+.1f}% a copy at 0.5 SOL)")
print("exit reason:", {w: sum(1 for o in out if o["why"] == w) for w in ("tp", "30s", "end")})
fl = np.array([o["fill"] or 0 for o in out])
for a, b_ in ((0, 0.9), (0.9, 1.0), (1.0, 1.1), (1.1, 1.2), (1.2, 1.5), (1.5, 3), (3, 1e9)):
    s = (fl >= a) & (fl < b_); print(f"   fill over our entry {a:>4}-{b_:<6}: {s.sum():3d} coins, {v[s].sum():+7.2f} SOL")
print("\nthe first trade after our entry over our entry: median", round(float(np.median([o["first"] for o in out if o["first"]])), 3))
print("\nper coin (time UTC, mint, e0 = our entry over its price, exit, the trigger and fill over our entry, fill age, value):")
import datetime as d
for o in sorted(out, key=lambda o: o["t"]):
    print(f"   {d.datetime.fromtimestamp(o['t'], d.UTC):%m-%d %H:%M} {o['m'][:8]} e0 {o['e0']:5.2f} {o['why']:3s} n={o['n']:4d} first {o['first'] or 0:5.2f} trig {o['trig'] or 0:5.2f} fill {o['fill'] or 0:5.2f} @{o['age'] or 0:5.1f}s {o['v']:+.3f}")
