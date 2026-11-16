# The 31-minute path of each SOL-priced coin wallet 4 bought with MIN+ SOL (collect.py's list), by cmodel.path
# (model.py for any wallet), one file a coin in LK/paths; already there are kept. The anchor (a signature at least
# 1,880 s after its buy) is taken from wallet 4's own transactions on disk.
#   RPC_URL=... LK=<dir> python3 -I paths.py SOLQ MIN TXDIR [TXDIR ...]
import sys, os, json, time, bisect
from concurrent.futures import ThreadPoolExecutor
SOLQ, MIN, DIRS = sys.argv[1], float(sys.argv[2]), sys.argv[3:]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M
rows = [r for r in json.load(open(f"{SOLQ}/sol_buys.json")) if r["sol"] >= MIN]
sigs = []
for D in DIRS:
    for f in os.listdir(D):
        t = json.load(open(f"{D}/{f}")); sigs.append((t["blockTime"], t["transaction"]["signatures"][0]))
sigs.sort(); T = [s[0] for s in sigs]
def anchor(t):
    i = bisect.bisect_left(T, t + 1880); return sigs[min(i, len(sigs) - 1)][1]
need = [r for r in rows if not os.path.exists(f"{M.PC}/{r['slot']}_{r['mint']}.json.gz") and r["t"] + 1880 < T[-1]]
print(f"{len(rows)} coins with a first buy of {MIN}+ SOL; {len(need)} paths to fetch", flush=True)
n = [0]; t0 = time.time()
def getp(r):
    try: M.path(r["mint"], r["slot"], anchor(r["t"]), threads=6)
    except Exception as e: print("path failed", r["mint"][:8], str(e)[:60].replace(os.environ["RPC_URL"], "<rpc>"), flush=True); return
    n[0] += 1
    if n[0] % 25 == 0: print(f"{n[0]} paths, {time.time() - t0:.0f} s", flush=True)
with ThreadPoolExecutor(4) as ex: list(ex.map(getp, need))
print("done", len(os.listdir(M.PC)), flush=True)
