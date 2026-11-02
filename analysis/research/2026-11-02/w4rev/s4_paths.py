# Step 3a: the launch tape and the 30-min price path of each coin in COINS_JSON ({mint: {csig, cslot, cbt, ...}}), from
# the coin's own pump TradeEvents (tape.py): every landed transaction of its create slot and the next (up to 150); after
# them every transaction when there are at most FULL, else the first DENSE, NP evenly spaced over the rest and the last
# one at or before create + 1800 s. s5_sim.py refines the gaps where an exit fires.
#   python3 -I s4_paths.py COINS_JSON [THREADS=8] [GAP=0.03] [FULL=100] [DENSE=30] [NP=50] -> out/tapes/<mint>.json
import sys, os, time, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib, tape
src = sys.argv[1]; TH = int(sys.argv[2]) if len(sys.argv) > 2 else 8
lib.crc.MIN_GAP = float(sys.argv[3]) if len(sys.argv) > 3 else 0.03
FULL = int(sys.argv[4]) if len(sys.argv) > 4 else 100; DENSE = int(sys.argv[5]) if len(sys.argv) > 5 else 30
NP = int(sys.argv[6]) if len(sys.argv) > 6 else 50
C = lib.jl(src); TD = lib.OUT + "/tapes"; os.makedirs(TD, exist_ok=True)
def one(m):
    fn = f"{TD}/{m}.json"
    if os.path.exists(fn): return m, "have"
    c = C[m]
    try:
        L, gaps = tape.listing(m, c["csig"], c["cbt"])
        s01 = [r for r in L if r[1] <= c["cslot"] + 1][:150]
        rest = [r for r in L if r[1] > c["cslot"] + 1]
        if len(rest) <= FULL: pick = rest
        else:
            pick = rest[:DENSE]; tail = rest[DENSE:]
            pick += [tail[int(i * (len(tail) - 1) / (NP - 1))] for i in range(NP)]
            last = [r for r in rest if r[2] <= c["cbt"] + 1800]
            if last: pick.append(last[-1])
        tr = {}
        for r in [[c["csig"], c["cslot"], c["cbt"]]] + s01 + pick:
            if r[0] in tr: continue
            x = tape.trades(r[0], m)
            if x is not None: tr[r[0]] = x
        lib.jdump(dict(n=len(L), n01=len(s01), gaps=gaps, sigs=L, tr=tr, full=len(rest) <= FULL), fn)
        return m, "ok"
    except Exception as e:
        return m, "err " + lib.red(e)[:100]
t0 = time.time(); n = 0; st = collections.Counter()
todo = [m for m in C if not os.path.exists(f"{TD}/{m}.json")]
print(time.strftime("%H:%M:%S"), len(C), "coins,", len(todo), "to do", flush=True)
with ThreadPoolExecutor(TH) as ex:
    for m, s in ex.map(one, todo):
        n += 1; st[s[:3]] += 1
        if s.startswith("err") and st["err"] <= 5: print("  ", m, s, flush=True)
        if n % 200 == 0: print(time.strftime("%H:%M:%S"), n, "/", len(todo), dict(st), f"calls {lib.crc.NCALLS[0]}", flush=True)
print(time.strftime("%H:%M:%S"), dict(st), f"calls {lib.crc.NCALLS[0]} in {time.time()-t0:.0f} s")
