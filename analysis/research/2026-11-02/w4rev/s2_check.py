# Step 1e: is the quote-control list the list of other-quote creates? A seeded sample of N landed mint-authority
# signatures of Oct 19 - Oct 27 00:00 UTC (out/s1_sigs.json), each read: quote mint (CreateEvent) against membership in
# out/qc_sigs.json.   python3 -I s2_check.py [N=1500] -> out/s2_check.json, the other-quote share of all creates
import sys, os, time, random, calendar, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
from s1b_crow import crow
N = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
lo, hi = calendar.timegm((2026, 10, 19, 0, 0, 0)), calendar.timegm((2026, 10, 27, 0, 0, 0))
S1 = sorted([r for r in lib.jl(lib.OUT + "/s1_sigs.json") if not r[3] and lo <= r[2] < hi], key=lambda r: (r[1], r[0]))
QC = {r[0] for r in lib.jl(lib.OUT + "/qc_sigs.json")}
rnd = random.Random(7); pick = rnd.sample(S1, N)
def one(r):
    t = lib.tx(r[0]); c = crow(t, r[0]) if t else None
    return r[0], (dict(quote=c["quote"], depth=c["depth"], mint=c["mint"]) if c else None)
with ThreadPoolExecutor(10) as ex: res = dict(ex.map(one, pick))
lib.jdump(res, lib.OUT + "/s2_check.json")
c = collections.Counter()
for s, v in res.items():
    if v is None: c[("no create", s in QC)] += 1
    else: c[("SOL" if v["quote"] in lib.SOL_LIKE else "other", s in QC)] += 1
print(f"{N} sampled landed mint-authority signatures, Oct 19-27: (quote, in quote-control list) -> count")
for k in sorted(c): print("  ", k, c[k])
print(f"all landed creates Oct 19-27 00:00: {len(S1)}; landed quote-control signatures in the same window: {sum(1 for r in lib.jl(lib.OUT + '/qc_sigs.json') if not r[3] and lo <= r[2] < hi)}")
