# Step 1g: every landed quote-control create of [T_LO, T_HI) (out/qc_sigs.json; default Oct 19 00:00 - Oct 27 00:00 UTC),
# read and decoded (s1b_crow.crow), in a seeded random order so a partial run is a random sample.
#   python3 -I s2_qc_fetch.py [THREADS=16] [GAP=0.03] [T_LO] [T_HI] -> out/qc_creates.json {sig: row}
import sys, os, time, random, calendar, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
from s1b_crow import crow
TH = int(sys.argv[1]) if len(sys.argv) > 1 else 16
lib.crc.MIN_GAP = float(sys.argv[2]) if len(sys.argv) > 2 else 0.03
lo = int(sys.argv[3]) if len(sys.argv) > 3 else calendar.timegm((2026, 10, 19, 0, 0, 0))
hi = int(sys.argv[4]) if len(sys.argv) > 4 else calendar.timegm((2026, 10, 27, 0, 0, 0))
Q = sorted([r for r in lib.jl(lib.OUT + "/qc_sigs.json") if not r[3] and lo <= r[2] < hi], key=lambda r: (r[1], r[0]))
random.Random(11).shuffle(Q)
op = lib.OUT + f"/qc_creates_{lo}_{hi}.json"; have = lib.jl(op) if os.path.exists(op) else {}
todo = [r for r in Q if r[0] not in have or "err" in have[r[0]]]
print(time.strftime("%H:%M:%S"), len(Q), "landed quote-control signatures,", len(todo), "to read", flush=True)
def one(r):
    try: t = lib.tx(r[0])
    except Exception as e: return r[0], dict(err=lib.red(e)[:120], cslot=r[1], cbt=r[2])
    if not t: return r[0], dict(err="null", cslot=r[1], cbt=r[2])
    c = crow(t, r[0])
    return r[0], (c if c else dict(cslot=r[1], cbt=r[2], ncreate=0))
t0 = time.time(); n = 0
with ThreadPoolExecutor(TH) as ex:
    for sig, row in ex.map(one, todo):
        have[sig] = row; n += 1
        if n % 5000 == 0:
            print(time.strftime("%H:%M:%S"), n, "/", len(todo), f"{n/(time.time()-t0):.1f}/s calls {lib.crc.NCALLS[0]} errors {sum(1 for v in have.values() if 'err' in v)}", flush=True)
            lib.jdump(have, op)
lib.jdump(have, op)
R = [have[r[0]] for r in Q]
print(f"{len(R)} read: creates {sum(1 for x in R if x.get('mint'))}, not a create {sum(1 for x in R if x.get('ncreate') == 0)}, errors {sum(1 for x in R if 'err' in x)}; calls {lib.crc.NCALLS[0]} in {time.time()-t0:.0f} s")
