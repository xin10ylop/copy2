# Search 2, step 1: every pump create from T0 to T1 (UTC), from the mint authority's signature list (account #1 of both
# create and create_v2), each landed create fetched and its CreateEvent read; only the coins priced in another token
# are kept (quote mint, creator, the create slot and time, the trades inside the create transaction).
#   python3 -I c1_creates.py "2026-11-08 13:00" "2026-11-12 13:00" [THREADS]  ->  LK/c1_sigs.json, LK/c1_creates.json
import sys, os, time, datetime, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib
ts = lambda s: datetime.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=datetime.timezone.utc).timestamp()
T0, T1 = ts(sys.argv[1]), ts(sys.argv[2]); TH = int(sys.argv[3]) if len(sys.argv) > 3 else 40
sp = lib.OUT + "/c1_sigs.json"
if os.path.exists(sp): S = lib.json.load(open(sp))
else:
    S, before = [], None
    while True:                                    # newest first; skip down to T1 first
        page = lib.sigs(lib.MINT_AUTH, before=before, cache=False)
        if not page: break
        before = page[-1]["signature"]
        S += [[p["signature"], p["slot"], p.get("blockTime"), p.get("err") is not None] for p in page if T0 <= (p.get("blockTime") or 0) < T1]
        if (page[-1].get("blockTime") or 0) < T0: break
        if len(S) and len(S) % 20000 < 1000: print(time.strftime("%H:%M:%S"), "listed", len(S), flush=True)
    lib.jdump(S, sp)
L = [r for r in S if not r[3]]
print(f"{len(S)} signatures, {len(L)} landed, {datetime.datetime.utcfromtimestamp(T0)} to {datetime.datetime.utcfromtimestamp(T1)} UTC", flush=True)
op = lib.OUT + "/c1_creates.json"
have = lib.json.load(open(op)) if os.path.exists(op) else {}
def one(r):
    sig, slot, bt, _ = r
    if sig in have: return sig, have[sig]
    try: t = lib.rpc("getTransaction", [sig, lib.TXO], cache=False)
    except Exception as e: return sig, dict(err=lib.red(e)[:120])
    if not t: return sig, dict(err="null")
    ev = lib.events(t); cr = [e for k, e in ev if k == "create"]
    if not cr: return sig, dict(nc=1)
    c = cr[0]
    if c.get("quote_mint") in lib.SOL_LIKE: return sig, dict(sol=1)
    tr = [e for k, e in ev if k == "trade" and e["mint"] == c["mint"]]
    return sig, dict(slot=slot, bt=bt, mint=c["mint"], quote=c.get("quote_mint"), user=c["user"], creator=c["creator"], vquote=c.get("vquote"),
                     depth=c.get("depth"), dev=[[e["user"], e["is_buy"], e.get("quote_amount"), e["tok"]] for e in tr])
t0 = time.time(); n = 0
todo = [r for r in L if r[0] not in have]
with ThreadPoolExecutor(TH) as ex:
    for sig, row in ex.map(one, todo):
        have[sig] = row; n += 1
        if n % 10000 == 0:
            print(time.strftime("%H:%M:%S"), n, "/", len(todo), f"{n/(time.time()-t0):.0f}/s", flush=True); lib.jdump(have, op)
lib.jdump(have, op)
rows = [have[r[0]] for r in L]
oq = [x for x in rows if "mint" in x]
print(f"{len(rows)} creates; errors {sum(1 for x in rows if 'err' in x)}; no CreateEvent {sum(1 for x in rows if 'nc' in x)}; "
      f"SOL {sum(1 for x in rows if 'sol' in x)}; other-quote {len(oq)} ({len(oq)/max(1,len(rows)-sum(1 for x in rows if 'err' in x or 'nc' in x)):.1%})")
for k, v in collections.Counter(x["quote"] for x in oq).most_common(20): print(f"  {k} {v}")
