# Step 3a: the launch tape and the 30-min price path of each coin in COINS_JSON ([mint, ...] or {mint: row}; rows from
# out/universe.json), from the coin's own pump TradeEvents (blib.listing / blib.trades, the code of ../w4rev/tape.py):
# every landed transaction of the create slot and the next two (up to 150; the fills of both execution models sit
# there); after them every transaction when there are at most FULL, else the first DENSE, NP evenly spaced over the rest
# and the last one at or before create + 1800 s. sim.py refines the gaps where an exit fires.
#   python3 -I t1_tapes.py COINS_JSON [THREADS=8] [FULL=80] [DENSE=25] [NP=40] -> tapes/<mint>.json
import sys, os, time, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib
TD = os.path.join(blib.HERE, "tapes")
def fetch(c, FULL=80, DENSE=25, NP=40):
    m = c["mint"]; fn = f"{TD}/{m}.json"
    if os.path.exists(fn): return "have"
    L, gaps = blib.listing(m, c["csig"], c["cbt"])
    s02 = [r for r in L if r[1] <= c["cslot"] + 2][:150]
    rest = [r for r in L if r[1] > c["cslot"] + 2]
    if len(rest) <= FULL: pick = rest
    else:
        pick = rest[:DENSE]; tail = rest[DENSE:]
        pick += [tail[int(i * (len(tail) - 1) / (NP - 1))] for i in range(NP)]
        last = [r for r in rest if r[2] <= c["cbt"] + 1800]
        if last: pick.append(last[-1])
    tr = {}
    for r in [[c["csig"], c["cslot"], c["cbt"]]] + s02 + pick:
        if r[0] in tr: continue
        x = blib.trades(r[0], m)
        if x is not None: tr[r[0]] = x
    blib.jdump(dict(n=len(L), n02=len(s02), gaps=gaps, sigs=L, tr=tr, full=len(rest) <= FULL), fn)
    return "ok"
if __name__ == "__main__":
    os.makedirs(TD, exist_ok=True)
    src = sys.argv[1]; TH = min(8, int(sys.argv[2]) if len(sys.argv) > 2 else 8)
    U = {r["mint"]: r for r in blib.jl(blib.OUT + "/universe.json")}
    C = blib.jl(src)
    ms = list(C) if isinstance(C, (list, dict)) else []
    todo = [m for m in ms if not os.path.exists(f"{TD}/{m}.json")]
    print(time.strftime("%H:%M:%S"), len(ms), "coins,", len(todo), "to do", flush=True)
    def one(m):
        try: return m, fetch(U[m] if m in U else dict(C[m], mint=m))
        except Exception as e: return m, "err " + blib.red(e)[:100]
    t0 = time.time(); n = 0; st = collections.Counter()
    with ThreadPoolExecutor(TH) as ex:
        for m, s in ex.map(one, todo):
            n += 1; st[s[:3]] += 1
            if s.startswith("err") and st["err"] <= 5: print("  ", m, s, flush=True)
            if n % 200 == 0: print(time.strftime("%H:%M:%S"), n, "/", len(todo), dict(st), f"calls {blib.calls()} cached {blib.NRO[0]}", flush=True)
    print(time.strftime("%H:%M:%S"), dict(st), f"calls {blib.calls()} (cached reads {blib.NRO[0]}) in {time.time()-t0:.0f} s")
