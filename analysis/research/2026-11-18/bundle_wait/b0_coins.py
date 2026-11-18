# The ladder, the next angle (the owner, Nov 18: "when something fails find another solution, on and on"). The flip
# failed because the launch bundle (10 wallets, 21 SOL) sells into whoever buys after it (../churn/). The next idea: wait
# and buy only the coins whose bundle has NOT started selling. This step builds the coin table (no money is computed):
# every ladder coin of the six ladder wallets' studies, any date, its path in the true in-slot order; per coin the
# bundle (create-slot buyers in the transactions holding a ladder-size buy), the time of each bundle sale after the
# launch slot, and the path itself, saved for b1. Prints how many coins still have no bundle sale at 5/10/20/30/60 s.
#   python3 -I b0_coins.py SP W8:SUFFIX:RES ... > out/b0_coins.txt
import sys, os, json, gzip, collections, numpy as np
SP = sys.argv[1]; here = "/home/user/copy2/analysis/research/2026-11-17/winners"
src = open(f"{here}/wallet_study.py").read().split("def one(ix):")[0]; SIZES = (1.10, 1.54, 2.18)
seen = set(); coins = []
for arg in sys.argv[2:]:
    w, suf, res = arg.split(":"); os.environ["RES"] = res
    sys.argv = ["x", SP, w, "300", "1800"]; ns = {"__file__": f"{here}/wallet_study.py", "__name__": "ws"}; exec(compile(src, "wallet_study.py", "exec"), ns)
    cpath, own = ns["cpath"], ns["own"]   # w5_copy's cpath: true in-slot order since the Nov 18 fix
    for r in json.load(open(f"{SP}/winners/study_{w}{suf}.json")):
        if r["m"] in seen: continue
        b = next((e for e in own.get(r["m"], []) if e["buy"]), None)
        if not b: continue
        try: tr = cpath(r["m"], b["slot"], b["t"])
        except Exception: continue
        if not tr: continue
        seen.add(r["m"]); s0 = tr[0]["slot"]; cs = [e for e in tr if e["slot"] == s0]
        sigs = {e["sig"] for e in cs if e["buy"] and any(abs(e["q"] / 1e9 - s) <= 0.005 for s in SIZES)}
        W = {e["user"] for e in cs if e["sig"] in sigs and e["buy"]}
        if len(W) < 2: continue
        t0 = tr[0]["t"]; sells = [e["t"] - t0 for e in tr if e["slot"] > s0 and e["user"] in W and not e["buy"]]
        coins.append(dict(m=r["m"], w=w, t=r["t"], s0=s0, t0=t0, bundle=sorted(W), sells=sells, tr=tr))
coins.sort(key=lambda c: c["t"])
json.dump(coins, gzip.open(f"{SP}/bundle_coins.json.gz", "wt"))
S0 = 1794923340   # Nov 17 13:49 UTC, the end of the week screen
for name, C in (("before Nov 17 13:49", [c for c in coins if c["t"] < S0]), ("after", [c for c in coins if c["t"] >= S0])):
    print(f"{name}: {len(C)} coins; bundle wallets median {np.median([len(c['bundle']) for c in C]) if C else 0:.0f}")
    for x in (5, 10, 20, 30, 60):
        n0 = sum(1 for c in C if not any(s <= x for s in c["sells"])); print(f"   no bundle sale by {x:2d} s: {n0} ({n0 / max(1, len(C)):.0%})")
    fs = [min(c["sells"]) for c in C if c["sells"]]; print(f"   first bundle sale: median {np.median(fs) if fs else 0:.1f} s; quartiles {np.percentile(fs, 25) if fs else 0:.1f} / {np.percentile(fs, 75) if fs else 0:.1f} s")
