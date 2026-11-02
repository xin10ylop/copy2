# Step 2c: each routable create's activity in its first 60 s (landed signatures on the mint, create excluded, capped at
# 1000; one getSignaturesForAddress call with `before` = a mint-authority signature 60 s later). Used only as the
# outcome of a creator's EARLIER coins (a feature known at the next create), never of the coin itself.
#   python3 -I s6b_activity.py [THREADS=12] -> out/act60.json {mint: n}
import sys, os, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib, tape
TH = int(sys.argv[1]) if len(sys.argv) > 1 else 12
lib.crc.MIN_GAP = 0.025
T = lib.jl(lib.OUT + "/table.json")
op = lib.OUT + "/act60.json"; have = lib.jl(op) if os.path.exists(op) else {}
def one(t):
    if t["mint"] in have: return t["mint"], have[t["mint"]]
    try:
        page = lib.sigs(t["mint"], before=tape.cur_time(t["cbt"] + 60), until=t["csig"], limit=1000)
        return t["mint"], sum(1 for p in page if p.get("err") is None and (p.get("blockTime") or 0) <= t["cbt"] + 60)
    except Exception as e:
        return t["mint"], None
t0 = time.time(); n = 0
with ThreadPoolExecutor(TH) as ex:
    for m, v in ex.map(one, T):
        have[m] = v; n += 1
        if n % 3000 == 0: print(time.strftime("%H:%M:%S"), n, "/", len(T), f"calls {lib.crc.NCALLS[0]}", flush=True); lib.jdump(have, op)
lib.jdump(have, op)
print(f"{len(have)} coins, {sum(1 for v in have.values() if v is None)} failed; calls {lib.crc.NCALLS[0]} in {time.time()-t0:.0f} s")
