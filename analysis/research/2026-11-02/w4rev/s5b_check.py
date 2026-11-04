# Step 3d: how much does sampling the path cost? For N random wallet-4 picks with 120-400 transactions in 30 min (tapes
# that were sampled, not read in full), every transaction of the window is read (out/tapes_full/) and the simulation
# rerun on the full tape; the sampled-and-refined result (out/sim_picks.json) against the full one, per config.
#   python3 -I s5b_check.py [N=25]
import sys, os, json, random, shutil, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib, tape, s5_sim
from concurrent.futures import ThreadPoolExecutor
N = int(sys.argv[1]) if len(sys.argv) > 1 else 25; lib.crc.MIN_GAP = 0.03
C = lib.jl(lib.OUT + "/coins_picks.json"); S = lib.jl(lib.OUT + "/sim_picks.json")
FD = lib.OUT + "/tapes_full"; os.makedirs(FD, exist_ok=True)
cand = []
for m in sorted(C):
    fn = f"{s5_sim.TD}/{m}.json"
    if not os.path.exists(fn) or m not in S or "err" in S[m]: continue
    d = lib.jl(fn)
    if not d["full"] and 120 < d["n"] <= 400 and not d["gaps"]: cand.append(m)
pick = random.Random(5).sample(cand, min(N, len(cand)))
def fill(m):
    fo = f"{FD}/{m}.json"
    if os.path.exists(fo): return
    d = lib.jl(f"{s5_sim.TD}/{m}.json")
    for r in d["sigs"]:
        if r[0] not in d["tr"]: d["tr"][r[0]] = tape.trades(r[0], m) or []
    lib.jdump(d, fo)
with ThreadPoolExecutor(6) as ex: list(ex.map(fill, pick))
s5_sim.TD = FD
diff = {}
for m in pick:
    r = s5_sim.sim(dict(C[m], mint=m), 0)
    for k, v in r.items():
        if k.startswith("_") or k not in S[m]: continue
        diff.setdefault(k, []).append((S[m][k]["pnl"], v["pnl"], S[m][k]["kind"], v["kind"]))
print(f"{len(pick)} picks of {len(cand)} candidates (120-400 transactions in 30 min, sampled); reads {lib.crc.NCALLS[0]}")
print(f"{'config':14s} {'sampled total':>13s} {'full total':>10s} {'exit kind differs':>17s} {'median |diff|':>13s}")
for k in sorted(diff):
    L = diff[k]
    print(f"{k:14s} {sum(a for a, b, x, y in L):+13.3f} {sum(b for a, b, x, y in L):+10.3f} {sum(1 for a, b, x, y in L if x != y):17d} {statistics.median(abs(a - b) for a, b, x, y in L):13.4f}")
