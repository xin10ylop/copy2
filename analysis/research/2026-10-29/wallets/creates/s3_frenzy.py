# Step 3: for every other-quote coin of step 2, the signatures on its mint in its first slots: getSignaturesForAddress
# with until= its create signature and before= the first create signature of step 1 at least 4 slots later (the RPC
# uses `before` only for its slot, so any transaction works). One call a coin (paged if 1,000 come back).
# The first version paged back from the newest signature and could not reach the launch of busy coins (63 of the first
# 2,241 hit its 8-page cap); this one costs one call whatever the coin did later.
#   python3 -I s3_frenzy.py [THREADS=16]  ->  OUT/s3_coins.json {mint: row}; OUT/s3_sigs/<mint>.json (landed sigs, slots +0..)
import sys, os, time, bisect, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crc
TH = int(sys.argv[1]) if len(sys.argv) > 1 else 16
C = crc.json.load(open(crc.OUT + "/s2_creates.json"))
S1 = sorted(crc.json.load(open(crc.OUT + "/s1_sigs.json")), key=lambda r: r[1]); SL = [r[1] for r in S1]
coins = [(sig, r) for sig, r in C.items() if r.get("ncreate") and r.get("quote") not in crc.SOL_LIKE]
coins.sort(key=lambda x: x[1]["slot"])
SD = crc.OUT + "/s3_sigs"; os.makedirs(SD, exist_ok=True)
op = crc.OUT + "/s3_coins.json"
have = crc.json.load(open(op)) if os.path.exists(op) else {}
def one(x):
    csig, r = x; m = r["mint"]
    if m in have: return m, have[m]
    i = bisect.bisect_left(SL, r["slot"] + 4)
    if i >= len(S1): return m, dict(err="too recent")
    before, bslot = S1[i][0], S1[i][1]; rows = []
    for k in range(5):
        try: page = crc.sigs(m, before=before, until=csig, limit=1000)
        except Exception as e: return m, dict(err=crc.red(e)[:120])
        rows += page
        if len(page) < 1000: break
        before = page[-1]["signature"]
    landed = [[p["signature"], p["slot"], p.get("blockTime")] for p in rows if p.get("err") is None]
    crc.jdump(landed, f"{SD}/{m}.json")
    s0 = r["slot"]; by = collections.Counter(p[1] - s0 for p in landed if 0 <= p[1] - s0 <= 3)
    return m, dict(csig=csig, slot=s0, bt=r["bt"], quote=r["quote"], user=r["user"], sym=r.get("sym"), vquote=r.get("vquote"),
                   depth=r.get("depth"), bslot=bslot - s0, n_listed=len(rows), n_failed=sum(1 for p in rows if p.get("err") is not None),
                   s0=by.get(0, 0), s1=by.get(1, 0), s2=by.get(2, 0), s3=by.get(3, 0))
t0 = time.time(); n = 0
with ThreadPoolExecutor(TH) as ex:
    for m, row in ex.map(one, coins):
        have[m] = row; n += 1
        if n % 1000 == 0: print(time.strftime("%H:%M:%S"), n, "/", len(coins), f"{n/(time.time()-t0):.0f}/s", flush=True); crc.jdump(have, op)
crc.jdump(have, op)
rows = [have[r["mint"]] for _, r in coins]; ok = [x for x in rows if "err" not in x]
fr = [x for x in ok if x["s0"] + x["s1"] + x["s2"] >= 4]
print(f"{len(rows)} other-quote coins in {time.time()-t0:.0f} s; errors {len(rows)-len(ok)}")
print(f"frenzy (>= 4 landed tx in create slot +0..+2, the create not counted): {len(fr)} = {len(fr)/len(ok):.1%}")
h = collections.Counter(min(x['s0'] + x['s1'] + x['s2'], 30) // 5 * 5 for x in ok)
print("landed tx in +0..+2 (bins of 5):", sorted(h.items()))
