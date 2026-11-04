# Step 3 pipeline: for each coin of COINS_JSON (in its order), fetch its tape (t1_tapes.fetch, FULL / DENSE / NP) if
# missing, then simulate it (sim.sim, refinement budget BUDGET reads). Results -> out/sim.json {mint: {cfg: result}}.
# RESIM=1 re-simulates coins already in out/sim.json (e.g. after jup.json grew); FRESH=1 runs the P3 coins (u3_fresh_sample.py).
#   python3 -I p1_run.py COINS_JSON [THREADS=8] [BUDGET=40] [FULL=40] [DENSE=15] [NP=25]
import sys, os, time, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib, t1_tapes, sim
src = sys.argv[1]; TH = min(8, int(sys.argv[2]) if len(sys.argv) > 2 else 8)
BUDGET = int(sys.argv[3]) if len(sys.argv) > 3 else 40
FULL = int(sys.argv[4]) if len(sys.argv) > 4 else 40; DENSE = int(sys.argv[5]) if len(sys.argv) > 5 else 15
NP = int(sys.argv[6]) if len(sys.argv) > 6 else 25
RESIM = os.environ.get("RESIM") == "1"
FRESH = os.environ.get("FRESH") == "1"                 # P3 coins: rows from out/fresh_table.json, results to out/sim_fresh.json
U = {r["mint"]: r for r in blib.jl(blib.OUT + ("/fresh_table.json" if FRESH else "/universe.json"))}
ms = blib.jl(src)
op = blib.OUT + ("/sim_fresh.json" if FRESH else "/sim.json"); have = blib.jl(op) if os.path.exists(op) else {}
todo = [m for m in ms if RESIM or m not in have or "err" in have[m]]
print(time.strftime("%H:%M:%S"), len(ms), "coins,", len(todo), "to do", flush=True)
def one(m):
    c = U[m]
    try:
        t1_tapes.fetch(c, FULL, DENSE, NP)
        return m, sim.sim(c, BUDGET)
    except Exception as e:
        return m, dict(err=blib.red(e)[:160])
t0 = time.time(); n = 0
with ThreadPoolExecutor(TH) as ex:
    for m, r in ex.map(one, todo):
        have[m] = r; n += 1
        if n % 200 == 0:
            print(time.strftime("%H:%M:%S"), n, "/", len(todo), f"calls {blib.calls()} cached {blib.NRO[0]} errors {sum(1 for v in have.values() if 'err' in v)}"
                  f" ({n / (time.time() - t0):.2f} coins/s)", flush=True)
            blib.jdump(have, op)
blib.jdump(have, op)
print(time.strftime("%H:%M:%S"), f"{len(have)} simulated ({sum(1 for v in have.values() if 'err' in v)} errors), reads {sum(v.get('_reads', 0) for v in have.values())}, calls {blib.calls()} in {time.time()-t0:.0f} s")
