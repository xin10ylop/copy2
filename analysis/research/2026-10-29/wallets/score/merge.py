# Folds pull.py's shard files (<w8>.jsonl.k) into <w8>.jsonl: one row per signature, broken lines (a killed writer) dropped.
#   python3 -I merge.py WALLET
import sys, os, json, glob
SP = os.environ.get("SP", "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/score")
W = sys.argv[1]; OUT = f"{SP}/h9long/{W[:8]}.jsonl"
rows, bad = {}, 0
for fn in [f for f in [OUT] + sorted(glob.glob(OUT + ".*")) if os.path.exists(f)]:
    for l in open(fn):
        try: r = json.loads(l); rows[r["sig"]] = l if l.endswith("\n") else l + "\n"
        except Exception: bad += 1
open(OUT + ".tmp", "w").writelines(rows.values()); os.replace(OUT + ".tmp", OUT)
for fn in glob.glob(OUT + ".[0-9]*"): os.remove(fn)
sigs = json.load(open(f"{SP}/h9long/{W[:8]}_sigs.json")); landed = {s for s, _, _, e in sigs if not e}
print(f"{W[:8]}: {len(rows)} rows, {bad} broken lines dropped, {len(landed - set(rows))} landed signatures still missing")
