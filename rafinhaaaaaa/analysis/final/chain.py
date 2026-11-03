# Chain facts for each trip of a wallet (Triton through rescore2.rpc): its buy transaction (slot, block position, fee,
# tips, nonce, programs = venue, the coin's pool and quote, curve fill, SOL it spent, route), what came just before it
# on the coin (coin age from the coin's oldest signature, the trades in its slot ahead of it, the 3 transactions before
# it), and each sale (slot, SOL received, fee, tips). Output: chain/<wallet>.json, keyed by the buy signature.
#   python3 -I chain.py TRIPS_JSON [MAX_TRIPS]       (TRIPS_JSON: an s3 / s3q file or one of ours with "trips")
import sys, os, json, time, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g1lib import *
from concurrent.futures import ThreadPoolExecutor
src = sys.argv[1]; MAXT = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9
d = jl(src); w = d["wallet"]; os.makedirs(G1 + "/chain", exist_ok=True)
fn = f"{G1}/chain/{w}.json"
out = jl(fn) if os.path.exists(fn) else {}
calls = [0]; lk = threading.Lock()
def rpc(m, p):
    with lk: calls[0] += 1
    return R.rpc(m, p)
def tx(sig):
    with lk: calls[0] += 1
    return R.tx_of(sig)

def coin_age(mint, sig0):
    """(seconds from the coin's first signature to its buy, slots, transactions on the coin before its buy, exact?)"""
    before, n, oldest = sig0, 0, None
    for page in range(4):
        r = rpc("getSignaturesForAddress", [mint, {"limit": 1000, "before": before}])
        if r is None: return None
        n += len(r)
        if r: oldest = r[-1]
        if len(r) < 1000: return oldest, n, True
        before = r[-1]["signature"]
    return oldest, n, False

def info(t):
    s0 = tx(t["sig0"])
    if not s0: return None
    m = t["mint"]; meta = s0["meta"]
    ps = R.pools(s0, m)
    fee, prio, tips, cup, cul, nonce = fee_tip(s0, w)
    dc, dq, q = deltas(s0, w, m)
    sol = sol_change(s0, w)
    tokq = {}                                                  # its own token changes other than the coin and wSOL
    for side, sign in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in meta.get(side) or []:
            if b.get("owner") == w and b["mint"] not in (m, WSOL):
                tokq[b["mint"]] = tokq.get(b["mint"], 0.0) + sign * float(b["uiTokenAmount"]["uiAmount"] or 0)
    bp = block_pos(s0["slot"], t["sig0"], m)
    age = coin_age(m, t["sig0"])
    prev = []
    sigs_before = rpc("getSignaturesForAddress", [m, {"limit": 6, "before": t["sig0"]}]) or []
    for x in sigs_before[:3]:
        if x.get("err"): prev.append(dict(slot=x["slot"], err=True)); continue
        p = tx(x["signature"])
        if not p: continue
        pp = R.pools(p, m)
        sg = [k["pubkey"] if isinstance(k, dict) else k for k in (p["transaction"]["message"].get("accountKeys") or [])][:1]
        prev.append(dict(slot=p["slot"], bt=p.get("blockTime"), signer=sg[0] if sg else None, side=pp[0][5] if pp else None,
                         q=pp[0][3] if pp else None, quote=pp[0][2] if pp else None, px=pp[0][1] if pp else None,
                         venue=venue(p), create=any("Create" in (l or "") for l in (p["meta"].get("logMessages") or [])[:40])))
    sells = []
    for s in t["sells"]:
        x = tx(s["sig"])
        if not x: sells.append(None); continue
        f2, p2, tp2, _, _, n2 = fee_tip(x, w); pq = R.pools(x, m)
        sells.append(dict(slot=x["slot"], bt=x.get("blockTime"), sol=sol_change(x, w), fee=f2, prio=p2, tips=tp2, nonce=n2,
                          pool=pq[0][0] if pq else None, px=pq[0][1] if pq else None, Q=pq[0][6] if pq else None,
                          C=pq[0][7] if pq else None, venue=venue(x), err=bool(x["meta"].get("err"))))
    return dict(slot=s0["slot"], bt=s0.get("blockTime"), err=bool(meta.get("err")), fee=fee, prio=prio, tips=tips, cu_price=cup,
                cu_limit=cul, nonce=nonce, cu=meta.get("computeUnitsConsumed"), venue=venue(s0), nsig=len(s0["transaction"]["signatures"]),
                pools=[dict(pool=p[0], px=p[1], quote=p[2], dq=p[3], dc=p[4], side=p[5], Q=p[6], C=p[7]) for p in ps],
                its_dc=dc, its_dq=dq, its_q=q, sol=sol, tokq=tokq, block=bp,
                age=dict(first_slot=age[0]["slot"], first_bt=age[0].get("blockTime"), n_before=age[1], exact=age[2],
                         first_sig=age[0]["signature"]) if age and age[0] else None,
                prev=prev, sells=sells)

todo = [t for t in d["trips"] if t["sig0"] not in out][:MAXT]
done = [0]
def one(t):
    try: r = info(t)
    except Exception as e: r = dict(error=str(e)[:200])
    with lk:
        out[t["sig0"]] = r; done[0] += 1
        if done[0] % 20 == 0:
            json.dump(out, open(fn, "w")); print(time.strftime("%H:%M:%S"), w[:8], done[0], "of", len(todo), "calls", calls[0], flush=True)
    R.TXC.pop(t["sig0"], None)
with ThreadPoolExecutor(4) as ex: list(ex.map(one, todo))
json.dump(out, open(fn, "w"))
print(time.strftime("%H:%M:%S"), w[:8], "done", len(out), "trips, calls", calls[0], flush=True)
