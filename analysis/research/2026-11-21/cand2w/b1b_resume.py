# Finish one wallet's paths on the coin list already saved (coins.json: the 55 fetched + 95 drawn, 150), 8 at a time.
#   RPC_URL=... LK=SP/lk python3 -I b1b_resume.py SP WALLET
import sys, os, json, time, concurrent.futures as cf
SP, W = sys.argv[1], sys.argv[2]; D = f"{SP}/cand_{W[:8]}"; LK = os.environ["LK"]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M
coins = json.load(open(f"{D}/coins.json")); todo = [c for c in coins if not os.path.exists(f"{LK}/paths/{c['slot']}_{c['m']}.json.gz")]
print(f"{W[:8]}: {len(coins)} coins, {len(todo)} to fetch", flush=True); t0 = time.time()
def one(c):
    try: return len(M.path(c["m"], c["slot"], c["anchor"], threads=10))
    except Exception as x: return f"error {type(x).__name__}"
with cf.ThreadPoolExecutor(8) as ex:
    for i, n in enumerate(ex.as_completed([ex.submit(one, c) for c in todo]) if False else cf.as_completed([ex.submit(one, c) for c in todo])):
        if (i + 1) % 10 == 0 or i + 1 == len(todo): print(f"{i + 1}/{len(todo)} ({time.time() - t0:.0f} s)", flush=True)
