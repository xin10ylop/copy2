# Step 2: fetch every landed create of step 1 and read its CreateEvent (quote mint, creator, the trades in the create tx).
#   python3 -I s2_quotes.py [LIMIT] [THREADS=24]  ->  OUT/s2_creates.json  {sig: row}; reruns read the cache.
import sys, os, time, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crc
LIM = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] != "all" else None
TH = int(sys.argv[2]) if len(sys.argv) > 2 else 24
S = [r for r in crc.json.load(open(crc.OUT + "/s1_sigs.json")) if not r[3]]
if LIM: S = S[:LIM]
op = crc.OUT + "/s2_creates.json"
have = crc.json.load(open(op)) if os.path.exists(op) else {}
def one(r):
    sig, slot, bt, _ = r
    if sig in have: return sig, have[sig]
    try: t = crc.tx(sig)
    except Exception as e: return sig, dict(err=crc.red(e)[:120])
    if not t: return sig, dict(err="null")
    ev = crc.events(t); cr = [e for k, e in ev if k == "create"]; tr = [e for k, e in ev if k == "trade"]
    ks = crc.keys_of(t)
    row = dict(slot=slot, bt=bt, idx=t.get("transactionIndex"), payer=ks[0], ncreate=len(cr))
    if cr:
        c = cr[0]; row.update(mint=c["mint"], quote=c.get("quote_mint"), user=c["user"], creator=c["creator"], sym=c["symbol"][:16],
                              vquote=c.get("vquote"), vsol=c["vsol"], vtok=c["vtok"], mayhem=c.get("mayhem"), depth=c.get("depth"))
        row["dev"] = [[e["user"], e["is_buy"], e["sol"], e["tok"], e.get("quote_amount")] for e in tr if e["mint"] == c["mint"]]
    return sig, row
t0 = time.time(); n = 0
with ThreadPoolExecutor(TH) as ex:
    for sig, row in ex.map(one, S):
        have[sig] = row; n += 1
        if n % 2000 == 0:
            print(time.strftime("%H:%M:%S"), n, "/", len(S), f"{n/(time.time()-t0):.0f}/s", flush=True); crc.jdump(have, op)
crc.jdump(have, op)
rows = [have[r[0]] for r in S]
print(f"{len(rows)} creates in {time.time()-t0:.0f} s; errors {sum(1 for x in rows if 'err' in x)}; no CreateEvent {sum(1 for x in rows if 'err' not in x and not x.get('ncreate'))}")
q = collections.Counter(x.get("quote") for x in rows if x.get("ncreate"))
tot = sum(q.values()); other = sum(v for k, v in q.items() if k not in crc.SOL_LIKE)
print(f"other-quote {other}/{tot} = {other/tot:.1%}")
for k, v in q.most_common(25): print(f"  {k} {v}")
