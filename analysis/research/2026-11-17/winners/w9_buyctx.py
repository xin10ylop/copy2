# 6ua7w2Gv's deeper study (PREREG_6ua7w2Gv.md), the data: for each of its sampled buys, (1) the coin's create
# transaction, the attention study's signals (mayhem, tips in the create, the dev buy, the creator, its age at the buy),
# (2) the market on the coin in the 60 s before its buy (others' buys and sales, SOL in and out, distinct buyers).
# The coin's bonding-curve account's signatures (they stop at graduation; the mint's go on in the pool) are paged back to the create (at most PAGES pages of 1,000; a coin busier than that
# gets no create). RPC from RPC_URL, never printed; transactions cached under LK.
#   RPC_URL=... LK=SP/winners/lk python3 -I w9_buyctx.py SP WALLET8 STUDY_SUFFIX [PAGES=15]   -> SP/winners/ctx_<w8><suffix>.json
import sys, os, json, glob
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import lib
from solders.pubkey import Pubkey as P
curve = lambda m: str(P.find_program_address([b"bonding-curve", bytes(P.from_string(m))], P.from_string(lib.PUMP))[0])
SP, W8, SUF = sys.argv[1], sys.argv[2], sys.argv[3]; PAGES = int(sys.argv[4]) if len(sys.argv) > 4 else 15
R = json.load(open(f"{SP}/winners/study_{W8}{SUF}.json")); h = json.load(open(glob.glob(f"{SP}/winners/hist/{W8}*.json")[0]))
full = os.path.basename(glob.glob(f"{SP}/winners/hist/{W8}*.json")[0])[:-5]
slot_of = {(e["m"], e["t"]): e["slot"] for e in h["trades"] if e["buy"]}
CB = "ComputeBudget111111111111111111111111111111"; SYS = "11111111111111111111111111111111"
def create_feat(t, m):
    ks = lib.keys_of(t); meta = t["meta"]; ev = lib.events(t); cr = next((e for k, e in ev if k == "create"), None)
    if not cr or cr.get("mint") != m: return None
    tr = [e for k, e in ev if k == "trade" and e.get("mint") == m and e.get("is_buy")]
    tips = sum(ix["parsed"]["info"]["lamports"] for ix in t["transaction"]["message"]["instructions"]
               if ix.get("programId") == SYS and isinstance(ix.get("parsed"), dict) and ix["parsed"].get("type") == "transfer")
    return dict(t=t["blockTime"], slot=t["slot"], creator=cr["creator"], payer=ks[0], mayhem=cr.get("mayhem"), cfee=cr.get("creator_fee_bps"),
                dev_buy=sum(e["sol"] for e in tr if e["user"] in (cr["user"], cr["creator"], ks[0])) / 1e9, tips=tips / 1e9, name=cr["name"], symbol=cr["symbol"])
def one(r):
    m, t0 = r["m"], r["t"]; slot = slot_of.get((m, t0))
    pages, before, pre, done = 0, None, [], False
    while pages < PAGES:
        s = lib.sigs(curve(m), before=before, limit=1000); pages += 1
        if not s: done = True; break
        for x in s:
            if x.get("err") is None and x.get("blockTime") and t0 - 60 <= x["blockTime"] < t0 and (slot is None or x["slot"] < slot): pre.append(x["signature"])
        before = s[-1]["signature"]
        if len(s) < 1000: done = True; break
    cf = None
    if done and before:
        try: cf = create_feat(lib.tx(before), m)
        except Exception: cf = None
    ob = os_ = 0; qin = qout = 0.0; buyers = set()
    for sg in pre[:80]:
        try: t = lib.tx(sg)
        except Exception: continue
        for k, e in lib.events(t) if t else []:
            if k != "trade" or e.get("mint") != m or e["user"].startswith(W8): continue
            if e["is_buy"]: ob += 1; qin += e["sol"]; buyers.add(e["user"])
            else: os_ += 1; qout += e["sol"]
    return m, t0, dict(create=cf, pre_n=len(pre), pre_buys=ob, pre_sells=os_, pre_in=qin, pre_out=qout, pre_buyers=len(buyers))
out = {}
with ThreadPoolExecutor(12) as ex:
    for m, t0, d in ex.map(one, [r for r in R if not r["refused"]]): out[f"{m}:{t0}"] = d
json.dump(out, open(f"{SP}/winners/ctx_{W8}{SUF}.json", "w"))
print(f"{W8}: {len(out)} buys; create found {sum(1 for v in out.values() if v['create'])}")
