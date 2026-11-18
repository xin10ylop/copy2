# Where are the ladder's rungs (the buys at 1.10 / 1.54 / 2.18 SOL) relative to the studied wallet's buy, and where
# did the frozen flip's model put our entry? The audit (c0) found the first trade after our entry at a median 1.95x our
# entry: the model entered before rungs that came later. Per pooled coin: the rungs' slots (offset from the create
# slot) and their order around our model entry; the live detector's view (rungs in the create slot: it fires at 2).
#   python3 -I c1_rungs.py SP W8:SUFFIX:RES ... > out/c1_rungs.txt
import sys, os, json, collections, numpy as np
SP = sys.argv[1]; S0 = int(os.environ.get("S0", 1794923340)); here = "/home/user/copy2/analysis/research/2026-11-17/winners"
src = open(f"{here}/wallet_study.py").read().split("def one(ix):")[0]; SIZES = (1.10, 1.54, 2.18)
seen = set(); rows = []
for arg in sys.argv[2:]:
    w, suf, res = arg.split(":"); os.environ["RES"] = res
    sys.argv = ["x", SP, w, "300", "1800"]; ns = {"__file__": f"{here}/wallet_study.py", "__name__": "ws"}; exec(compile(src, "wallet_study.py", "exec"), ns)
    cpath, H, own, full, rate_of = ns["cpath"], ns["H"], ns["own"], ns["full"], ns["rate_of"]
    for r in json.load(open(f"{SP}/winners/study_{w}{suf}.json")):
        if r["refused"] or r["t"] < S0 or r["m"] in seen: continue
        seen.add(r["m"]); b = next((e for e in own.get(r["m"], []) if e["buy"]), None)
        tr = cpath(r["m"], b["slot"], b["t"]); k = next((j for j, y in enumerate(tr) if y["user"] == full and y["buy"] and y["slot"] == b["slot"]), None)
        s0 = min(e["slot"] for e in tr)   # the create slot (the path starts at the launch)
        rung = [(j, e) for j, e in enumerate(tr[:400]) if e["buy"] and any(abs(e["q"] / 1e9 - s) <= 0.005 for s in SIZES) and e["slot"] <= s0 + 5]
        j_ent = k + len([e for e in tr[k + 1:] if e["slot"] <= b["slot"] + 1])   # the model's entry: after the last trade of slot+1? (t5's j)
        ent_slot = b["slot"] + 1
        rows.append(dict(m=r["m"], w=w, s0=s0, its=b["slot"] - s0, rungs=[(e["slot"] - s0, round(e["q"] / 1e9, 2), j) for j, e in rung],
                         in_create=len({e["user"] for j, e in rung if e["slot"] == s0}), after_entry=sum(1 for j, e in rung if e["slot"] >= ent_slot)))
print(f"{len(rows)} coins")
print("its buy's slot, offset from the create slot:", dict(collections.Counter(r["its"] for r in rows)))
print("rungs in the create slot (the live detector fires at 2+):", dict(sorted(collections.Counter(r["in_create"] for r in rows).items())))
print("rungs landing in or after the model's entry slot (create + 1 or later):", dict(sorted(collections.Counter(r["after_entry"] for r in rows).items())))
print("\nper coin: the rungs as (slot offset, SOL)")
for r in rows: print(f"   {r['m'][:8]} {r['w']:8s} its +{r['its']} | {[(s, q) for s, q, j in r['rungs']]}")
