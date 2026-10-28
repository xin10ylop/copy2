# Step 3: for every other-quote coin of step 2, the signatures on its mint from its create up to now
# (getSignaturesForAddress until= the create signature, newest first, paged; capped at CAP pages), and the landed
# transactions in its create slot, +1, +2.
#   python3 -I s3_frenzy.py [THREADS=16] [CAP=8]  ->  OUT/s3_coins.json {mint: row}; OUT/s3_sigs/<mint>.json (landed sigs)
import sys, os, time, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crc
TH = int(sys.argv[1]) if len(sys.argv) > 1 else 16; CAP = int(sys.argv[2]) if len(sys.argv) > 2 else 8
C = crc.json.load(open(crc.OUT + "/s2_creates.json"))
coins = [(sig, r) for sig, r in C.items() if r.get("ncreate") and r.get("quote") not in crc.SOL_LIKE]
coins.sort(key=lambda x: x[1]["slot"])
SD = crc.OUT + "/s3_sigs"; os.makedirs(SD, exist_ok=True)
op = crc.OUT + "/s3_coins.json"
have = crc.json.load(open(op)) if os.path.exists(op) else {}
def one(x):
    csig, r = x; m = r["mint"]
    if m in have: return m, have[m]
    rows, before, capped = [], None, False
    for k in range(CAP):
        try: page = crc.sigs(m, before=before, until=csig, limit=1000, cache=before is not None)
        except Exception as e: return m, dict(err=crc.red(e)[:120])
        rows += page
        if len(page) < 1000: break
        before = page[-1]["signature"]
    else: capped = True
    landed = [[p["signature"], p["slot"], p.get("blockTime")] for p in rows if p.get("err") is None]
    crc.jdump(landed, f"{SD}/{m}.json")
    s0 = r["slot"]; by = collections.Counter(p[1] - s0 for p in landed if 0 <= p[1] - s0 <= 2)
    return m, dict(csig=csig, slot=s0, bt=r["bt"], quote=r["quote"], user=r["user"], sym=r.get("sym"), vquote=r.get("vquote"),
                   depth=r.get("depth"), n_all=len(rows), n_landed=len(landed), capped=capped,
                   s0=by.get(0, 0), s1=by.get(1, 0), s2=by.get(2, 0))
t0 = time.time(); n = 0
with ThreadPoolExecutor(TH) as ex:
    for m, row in ex.map(one, coins):
        have[m] = row; n += 1
        if n % 1000 == 0: print(time.strftime("%H:%M:%S"), n, "/", len(coins), f"{n/(time.time()-t0):.0f}/s", flush=True); crc.jdump(have, op)
crc.jdump(have, op)
rows = [have[r["mint"]] for _, r in coins]
fr = [x for x in rows if "err" not in x and x["s0"] + x["s1"] + x["s2"] >= 4]
print(f"{len(rows)} other-quote coins in {time.time()-t0:.0f} s; errors {sum(1 for x in rows if 'err' in x)}; capped {sum(1 for x in rows if x.get('capped'))}")
print(f"frenzy (>= 4 landed tx in create slot +0..+2, the create not counted): {len(fr)} = {len(fr)/len(rows):.1%}")
