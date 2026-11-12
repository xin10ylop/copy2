# How many landed signatures of a wallet no pull.py file holds yet (reads, changes nothing).   python3 -I missing.py W8
import sys, os, json, glob
SP = os.environ.get("SP", "/tmp/claude-0/-home-user-copy2/2a3626e5-937e-5580-9928-ee4cf7459077/scratchpad/lk/score")
w = sys.argv[1][:8]; have = set()
for fn in glob.glob(f"{SP}/h9long/{w}.jsonl*"):
    for l in open(fn):
        try: have.add(json.loads(l)["sig"])
        except Exception: pass
print(sum(1 for s, _, _, e in json.load(open(f"{SP}/h9long/{w}_sigs.json")) if not e and s not in have))
