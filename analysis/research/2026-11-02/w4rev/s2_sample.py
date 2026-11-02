# Step 1c: a seeded random sample of the landed mint-authority signatures of Oct 19 00:00 - Oct 27 00:00 UTC (out/s1_sigs.json;
# a bigger N contains a smaller one), each read and decoded (CreateEvent; trades in the create tx).
#   python3 -I s2_sample.py N [THREADS=10] [T_LO] [T_HI] -> out/s2_creates.json {sig: row}
import sys, os, time, random, collections, calendar
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
from s1b_crow import crow
N = int(sys.argv[1]); TH = int(sys.argv[2]) if len(sys.argv) > 2 else 10
lo = int(sys.argv[3]) if len(sys.argv) > 3 else calendar.timegm((2026, 10, 19, 0, 0, 0))
hi = int(sys.argv[4]) if len(sys.argv) > 4 else calendar.timegm((2026, 10, 27, 0, 0, 0))
S1 = lib.jl(lib.OUT + "/s1_sigs.json")
ok = sorted([r for r in S1 if not r[3] and lo <= r[2] < hi], key=lambda r: (r[1], r[0]))
rnd = random.Random(20261101); order = list(range(len(ok))); rnd.shuffle(order)
pick = [ok[i] for i in order[:N]]
op = lib.OUT + "/s2_creates.json"; have = lib.jl(op) if os.path.exists(op) else {}
def one(r):
    sig, slot, bt, _ = r
    if sig in have and "err" not in have[sig]: return sig, have[sig]
    try: t = lib.tx(sig)
    except Exception as e: return sig, dict(err=lib.red(e)[:120], slot=slot, bt=bt)
    if not t: return sig, dict(err="null", slot=slot, bt=bt)
    c = crow(t, sig)
    return sig, (c if c else dict(slot=slot, bt=bt, ncreate=0))
t0 = time.time(); n = 0
with ThreadPoolExecutor(TH) as ex:
    for sig, row in ex.map(one, pick):
        have[sig] = row; n += 1
        if n % 2000 == 0: print(time.strftime("%H:%M:%S"), n, "/", len(pick), f"{n/(time.time()-t0):.1f}/s calls {lib.crc.NCALLS[0]}", flush=True); lib.jdump(have, op)
lib.jdump(have, op)
R = [have[r[0]] for r in pick]
cr = [x for x in R if x.get("mint")]
print(f"{len(ok)} landed in the window; sampled {len(R)}: creates {len(cr)}, not a create {sum(1 for x in R if x.get('ncreate') == 0)}, errors {sum(1 for x in R if 'err' in x)}; calls {lib.crc.NCALLS[0]} in {time.time()-t0:.0f} s")
oq = [x for x in cr if x.get("quote") not in lib.SOL_LIKE]
print(f"other-quote {len(oq)} of {len(cr)}; top quotes:", collections.Counter((x['quote'] or '')[:8] for x in oq).most_common(15))
