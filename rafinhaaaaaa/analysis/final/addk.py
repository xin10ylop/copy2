# Adds s2k2 (our buy and sales K = 2 trades behind: the live run's median of landed coin trades on the pool between
# wallet 4's buy and ours, live_model.py) to every trip of an s3q2 file, with reprice.py's scoring and fallbacks.
#   python3 -I addk.py S3Q2_JSON [K]
import sys, os, json, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reprice as RP
from concurrent.futures import ThreadPoolExecutor
fn = sys.argv[1]; K = int(sys.argv[2]) if len(sys.argv) > 2 else 2
d = json.load(open(fn)); w = d["wallet"]; key = f"s2k{K}"
def one(t):
    if key in t or not (t.get("s2") or t.get("s2k1") or t.get("s2k7")): return
    try: t[key] = RP.score(w, t, False, K)[0]
    except Exception as e: t[key] = None
    RP.SEQ.clear() if len(RP.SEQ) > 2000 else None
    RP.R.TXC.pop(t["sig0"], None)
with ThreadPoolExecutor(3) as ex: list(ex.map(one, d["trips"]))
json.dump(d, open(fn, "w"))
ok = [t for t in d["trips"] if t.get(key)]
print(w[:8], key, len(ok), "priced, copy at 1 SOL %+.2f" % sum(t[key]["copy"] for t in ok), flush=True)
