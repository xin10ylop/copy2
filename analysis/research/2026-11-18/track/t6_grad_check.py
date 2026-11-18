# The check of the pooled ladder's result (t4_pool, coins after Nov 17 13:49 UTC): wallet_study's sim sells a coin that
# graduates at the curve's last price, with no haircut (the Nov 17 audit: a pool price can differ; tg_channel uses 0.8x).
# For each pooled coin: does the copy's exit fall at the graduation (sp10/60s and trail1.3/25%), and the result with the
# graduation exit at 0.8x and 0.5x of the curve's last value. Also our entry over the first ladder buy's price.
#   python3 -I t6_grad_check.py SP W8:SUFFIX:RES ... > out/t6_grad_check.txt
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
        gi = H.first(p["grad"]); e0 = (tr[k]["vt"] / p["ent"][0]) ** 2
        res_ = {}
        for name, kw in (("sp10/60s", dict(sp=(10, 60))), ("trail1.3/25%", dict(trail=(1.3, 0.25))), ("FLIP ours x1.2 cap 30s", dict(tp=1.2 * e0, hold=30))):
            v = sim(p, **kw)
            # the same exit with the graduation removed: where would it sell instead (None = held to the end of the data)?
            q = dict(p); q["grad"] = np.zeros_like(p["grad"]); v_nog = sim(q, **kw)
            res_[name] = (v, v_nog)
        out.append(dict(w=w, t=r["t"], grad_at=None if gi is None else float(p["age"][gi]), e0=e0, res=res_))
n = len(out); g = [o for o in out if o["grad_at"] is not None]
print(f"{n} pooled coins after the cutoff; the curve completed within the data for {len(g)} ({len(g) / max(1, n):.0%}), a median {np.median([o['grad_at'] for o in g]) if g else 0:.0f} s after the ladder")
print(f"our entry over the ladder buy's price: median {np.median([o['e0'] for o in out]):.2f}x")
for name in ("sp10/60s", "trail1.3/25%", "FLIP ours x1.2 cap 30s"):
    v = np.array([o["res"][name][0] - 0.0319 for o in out]); vg = np.array([o["res"][name][0] - 0.0319 for o in g])
    print(f"\n{name}: all {n}: {v.sum():+.2f} SOL ({100 * v.mean() / 0.5:+.1f}% a copy); on the coins that completed: {vg.sum():+.2f} ({100 * vg.mean() / 0.5 if len(vg) else 0:+.1f}%)")
    for hc in (0.8, 0.5):
        # a copy that sold AT the graduation gets the haircut: value + 0.5 + cost is what it received; scale that part
        adj = []
        for o in out:
            val = o["res"][name][0]; nog = o["res"][name][1]
            at_grad = o["grad_at"] is not None and abs(val - nog) > 1e-9   # the graduation set the exit
            adj.append(((val + 0.5 + 0.0026) * hc - 0.5 - 0.0026 if at_grad else val) - 0.0319)
        a = np.array(adj); print(f"   graduation sold at {hc}x of the curve's last value: {a.sum():+.2f} SOL ({100 * a.mean() / 0.5:+.1f}% a copy); exits set by the graduation: {sum(1 for o in out if o['grad_at'] is not None and abs(o['res'][name][0] - o['res'][name][1]) > 1e-9)}")

v = np.array([o["res"]["FLIP ours x1.2 cap 30s"][0] - 0.0319 for o in out]); h = len(v) // 2; k = max(1, round(0.02 * len(v)))
bs = np.random.default_rng(7).choice(v, size=(10000, len(v))).mean(axis=1)
print(f"\nTHE FROZEN FLIP after the cutoff: {len(v)} coins, {v.sum():+.2f} SOL ({100 * v.mean() / 0.5:+.1f}% a copy); halves {100 * v[:h].mean() / 0.5:+.1f}% / {100 * v[h:].mean() / 0.5:+.1f}%; without the best 2% {np.sort(v)[:-k].sum():+.2f}; P(mean > 0) {np.mean(bs > 0):.1%}")
