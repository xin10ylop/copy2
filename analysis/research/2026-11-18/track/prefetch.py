# A second fetcher on another RPC for a running study (the owner, Nov 18: "use triton too to be faster"): it walks the same
# list of coins from the other end and fills the same path cache (w5_copy's cpath: one file per coin), so the study finds
# them cached. Results are unchanged; only the fetching is shared.
#   RPC_URL=... HOLD=... python3 -I prefetch.py SP crew                          (the crew coins of crew/c2_money.py)
#   RPC_URL=... HOLD=1800 RES=... python3 -I prefetch.py SP study WALLET8 N      (a wallet_study.py run)
import sys, os, json, glob, random
from concurrent.futures import ThreadPoolExecutor
SP, kind = sys.argv[1], sys.argv[2]; ARGS = list(sys.argv)
here = "/home/user/copy2/analysis/research/2026-11-17/winners"; src = open(f"{here}/w5_copy.py").read().split("EX = [")[0]
W8 = sys.argv[3] if kind == "study" else "6ua7w2Gv"
sys.argv = ["x", SP, W8]; ns = {"__file__": f"{here}/w5_copy.py"}; exec(compile(src, "w5_copy.py", "exec"), ns); cpath = ns["cpath"]
jobs = []
if kind == "crew":
    CREW = ["6ua7w2Gv", "q2q38wAb", "q2jJy82z", "7777P2fk", "GKd5EMzR", "6Z91Dgiz", "6anjqMeW", "2NUMEzNh"]; first = {}
    for w in CREW:
        for e in sorted(json.load(open(glob.glob(f"{SP}/winners/hist/{w}*.json")[0]))["trades"], key=lambda e: e["t"]):
            if e["buy"]: first.setdefault((e["m"], w), e)
    for r in json.load(open(f"{SP}/crew_rows.json")):
        if r["n"] >= 3:
            e0 = min((first[(r["m"], w)] for w in r["crew"]), key=lambda e: e["t"]); jobs.append((r["m"], e0["slot"], e0["t"]))
else:
    N = int(ARGS[4]); res = json.load(open(os.environ["RES"])); full = next(k for k in res if k.startswith(W8))
    h = json.load(open(glob.glob(f"{SP}/winners/hist/{W8}*.json")[0])); own = {}
    for e in sorted(h["trades"], key=lambda e: e["t"]): own.setdefault(e["m"], []).append(e)
    items = [x for v in res[full].values() for x in v]; random.Random(7).shuffle(items); items = items[:N]
    for x in items:
        b = next((e for e in own.get(x["m"], []) if e["buy"]), None)
        if b: jobs.append((x["m"], b["slot"], b["t"]))
if os.environ.get("SHUFFLE"): random.Random(int(os.environ["SHUFFLE"])).shuffle(jobs); print(f"{len(jobs)} coins, shuffled (seed {os.environ['SHUFFLE']})", flush=True)
else: jobs.reverse(); print(f"{len(jobs)} coins, from the end", flush=True)
def get(j):
    try: cpath(*j)
    except Exception: pass
with ThreadPoolExecutor(6) as ex: list(ex.map(get, jobs))
print("done", flush=True)
