# Search 2, step 2: the launch trades of every coin priced in another token from c1 (no frenzy filter): the landed
# signatures on its mint from its create to SLOTS slots later (getSignaturesForAddress with until= the create and
# before= a create signature of c1 at least SLOTS+1 slots later: the RPC uses `before` for its slot only, as
# ../../2026-10-29/wallets/creates/s3_frenzy.py), each fetched and its pump TradeEvents of the coin kept, with the buyer's
# SOL change in that transaction (to price the quote token from the buys paid in SOL, as the Oct 29 s4 step did).
#   python3 -I c2_launch.py [SLOTS=5] [THREADS=40]  ->  LK/c2_launch.json {mint: {create row, trades: [...]}}
import sys, os, time, bisect, collections
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib
SLOTS = int(sys.argv[1]) if len(sys.argv) > 1 else 5; TH = int(sys.argv[2]) if len(sys.argv) > 2 else 40
C = lib.json.load(open(lib.OUT + "/c1_creates.json"))
S1 = sorted((r for r in lib.json.load(open(lib.OUT + "/c1_sigs.json"))), key=lambda r: r[1]); SL = [r[1] for r in S1]
coins = sorted(((s, r) for s, r in C.items() if "mint" in r), key=lambda x: x[1]["slot"])
op = lib.OUT + "/c2_launch.json"
have = lib.json.load(open(op)) if os.path.exists(op) else {}
TXO = {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}
import cmodel
def sol_change(tx, who):
    ks = tx["transaction"]["message"]["accountKeys"] + sum(((tx["meta"].get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
    if who not in ks: return None, None
    i = ks.index(who); m = tx["meta"]
    d = m["postBalances"][i] - m["preBalances"][i] + (m["fee"] if i == 0 else 0)
    w = lambda k: sum(int(b["uiTokenAmount"]["amount"]) for b in m.get(k) or [] if b.get("owner") == who and b["mint"] == lib.WSOL)
    return d + w("postTokenBalances") - w("preTokenBalances"), i == 0
def qdrawn(tx, who, q):
    m = tx["meta"]; w = lambda k: sum(int(b["uiTokenAmount"]["amount"]) for b in m.get(k) or [] if b.get("owner") == who and b["mint"] == q)
    return w("preTokenBalances") - w("postTokenBalances")
def one(x):
    csig, r = x; m = r["mint"]
    if m in have: return m, have[m]
    i = bisect.bisect_left(SL, r["slot"] + SLOTS + 1)
    if i >= len(S1): return m, dict(err="too recent")
    try:
        page = lib.sigs(m, before=S1[i][0], until=csig, limit=1000, cache=False)
        sg = [p for p in page if p.get("err") is None and p["slot"] - r["slot"] <= SLOTS]
        tr = []
        for p in sg:
            tx = lib.rpc("getTransaction", [p["signature"], TXO], cache=False)
            if not tx: continue
            for e in cmodel.trades(tx, m):
                d, payer = sol_change(tx, e["user"])
                e.update(ds=tx["slot"] - r["slot"], idx=tx.get("transactionIndex"), solchg=d, payer=payer, qdrawn=qdrawn(tx, e["user"], r["quote"]),
                         fee=tx["meta"]["fee"], fail=None)
                tr.append(e)
    except Exception as e:
        return m, dict(err=lib.red(e)[:120])
    return m, dict(csig=csig, slot=r["slot"], bt=r["bt"], quote=r["quote"], creator=r["creator"], user=r["user"], vquote=r.get("vquote"),
                   depth=r.get("depth"), dev=r.get("dev"), nsig=len(sg), full=len(page) >= 1000, trades=tr)
t0 = time.time(); n = 0; todo = [x for x in coins if x[1]["mint"] not in have]
with ThreadPoolExecutor(TH) as ex:
    for f in as_completed([ex.submit(one, x) for x in todo]):
        mm, row = f.result(); have[mm] = row; n += 1
        if n % 2000 == 0: print(time.strftime("%H:%M:%S"), n, "/", len(todo), f"{n/(time.time()-t0):.0f} coins/s", flush=True); lib.jdump(have, op)
lib.jdump(have, op)
ok = [v for v in have.values() if "err" not in v]
print(f"{len(have)} coins, errors {len(have)-len(ok)}, trades in slots +0..+{SLOTS}: {sum(len(v['trades']) for v in ok)}; "
      f"coins with 1+ trade {sum(1 for v in ok if v['trades'])}; hit 1000 {sum(1 for v in ok if v['full'])}")
