# since_stop/model.py for any wallet W: the same trade decoder, path and copy model (exact constant-product quotes on
# the TradeEvent reserves with their fee bps, price model q, 0.3% a pool hop each way, 0.0026 SOL a round trip, 0.0004 a
# refused buy, the buy limit 1.25x the price its buy left; landing N trades after its buy or "slot+1"), changed only
# where it named wallet 4: its buy and its sale are W's. Paths: every landed trade on the coin's curve from W's buy slot
# to 31 minutes (1,880 s) after it, in block order for its slot and the next two (getBlock), as model.py builds them.
#   import cmodel as M; M.path(W, mint, slot, t, anchor_sig) -> trades; M.model(W, r, tr, stake, n, **exits)
import sys, os, json, gzip, struct, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib
sys.path.insert(0, "/home/user/rugsnipe/analysis"); from rugsnipe_analysis import events as E
PC = lib.OUT + "/paths"; os.makedirs(PC, exist_ok=True)
TXO = {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}
B58 = lib._B58
def b58(b): return lib.b58e(b)
def decode_trade(d):                                    # model.py's decode_trade, verbatim
    o = [0]
    def take(n):
        if o[0] + n > len(d): raise IndexError
        v = d[o[0]:o[0] + n]; o[0] += n; return v
    left = lambda: len(d) - o[0]
    u64 = lambda: struct.unpack("<Q", take(8))[0]
    opt = lambda f: f() if left() else None
    e = dict(mint=b58(take(32)), sol=u64(), tok=u64(), buy=take(1)[0] == 1, user=b58(take(32)), ts=struct.unpack("<q", take(8))[0],
             vsol=u64(), vt=u64())
    e["real_sol"] = opt(u64); e["real"] = opt(u64); opt(lambda: take(32)); e["fee_bps"] = opt(u64); opt(u64)
    opt(lambda: take(32)); e["cfee_bps"] = opt(u64); opt(u64); opt(lambda: take(1)); opt(u64); opt(u64); opt(u64); opt(u64)
    if left(): n = struct.unpack("<I", take(4))[0]; take(n)
    opt(lambda: take(1)); opt(u64); opt(u64); opt(u64); opt(u64)
    if left(): n = struct.unpack("<I", take(4))[0]; take(34 * n)
    e["quote_mint"] = opt(lambda: b58(take(32))); e["q"] = opt(u64); e["vq"] = opt(u64)
    return e
def trades(tx, m):
    out = []
    ks = tx["transaction"]["message"]["accountKeys"] + (tx["meta"].get("loadedAddresses") or {}).get("writable", []) + (tx["meta"].get("loadedAddresses") or {}).get("readonly", [])
    for g in tx["meta"].get("innerInstructions") or []:
        for ix in g["instructions"]:
            if ks[ix["programIdIndex"]] != lib.PUMP: continue
            raw = lib.b58d(ix.get("data", ""))
            if raw[:8] == E.EVENT_IX_TAG and raw[8:16] == E.DISC_TRADE:
                try: e = decode_trade(raw[16:])
                except Exception: continue
                if e["mint"] == m:
                    out.append(dict(slot=tx["slot"], t=tx["blockTime"], sig=tx["transaction"]["signatures"][0], user=e["user"], buy=e["buy"],
                                    q=e["q"] if e.get("q") else e["sol"], tok=e["tok"], vt=e["vt"], vq=e["vq"] if e.get("vq") else e["vsol"],
                                    bps=(e["fee_bps"] or 0) + (e["cfee_bps"] or 0), real=e["real"]))
    return out
def path(m, slot, anchor, threads=12):
    """every landed trade on mint m from `slot` back from `anchor` (a signature at least 1,880 s after the buy: any
    signature works, the RPC uses its slot), in block order; cached per coin."""
    p = f"{PC}/{slot}_{m}.json.gz"
    if os.path.exists(p): return json.load(gzip.open(p))
    sigs, before = [], anchor
    for _ in range(40):
        page = lib.sigs(m, before=before, cache=False)
        if not page: break
        sigs += [x for x in page if x["err"] is None and x["slot"] >= slot]
        if page[-1]["slot"] < slot or len(page) < 1000: break
        before = page[-1]["signature"]
    with cf.ThreadPoolExecutor(threads) as ex:
        txs = list(ex.map(lambda x: lib.rpc("getTransaction", [x["signature"], TXO], cache=False), sigs))
    tr = [e for tx in txs if tx for e in trades(tx, m)]
    order = {}
    for s in (slot, slot + 1, slot + 2):
        b = lib.rpc("getBlock", [s, {"encoding": "json", "transactionDetails": "signatures", "maxSupportedTransactionVersion": 1, "rewards": False}], cache=False)
        if b: order.update({sg: (s, i) for i, sg in enumerate(b["signatures"])})
    tr.sort(key=lambda e: order.get(e["sig"], (e["slot"], 10**6)))
    lib.jdump(tr, p + ".json"); 
    with gzip.open(p + ".tmp", "wt") as f: json.dump(tr, f)
    os.replace(p + ".tmp", p); os.remove(p + ".json")
    return tr
def its_buy(W, r, tr):
    return next((i for i, e in enumerate(tr) if e["user"] == W and e["buy"] and e["slot"] == r["slot"]), None)
def model(W, r, tr, stake, n, tp=2.0, sl=0.8, hold=1790, follow=False, pmax=1.25, trail=None):
    """model.py's model() with W for wallet 4 (and exit_search.py's follow-below-x and trailing stop: follow=True or a
    price; trail=None or a fraction of the peak). r: slot, t, sol (W's SOL spent on the buy)."""
    k = its_buy(W, r, tr)
    if k is None: return dict(note="its buy not found")
    its = tr[k]; vta = its["vt"]; t0 = its["t"]
    rate = r["sol"] * 1e9 / (its["q"] * (1 + its["bps"] / 1e4))
    if isinstance(n, str) and n.startswith("slot+"):          # every trade in its block and the next n-1 ahead of us
        ahead = [e for e in tr[k + 1:] if e["slot"] <= its["slot"] + int(n[5:])]; j = k + len(ahead)
    else:
        j = min(k + n, len(tr) - 1)
    ent = tr[j]; px_in = (vta / ent["vt"]) ** 2
    if px_in > pmax: return dict(exit="refused", px_in=px_in, net=-0.0004)
    Q = stake * 1e9 * (1 - 0.003) / rate; net_in = Q * 1e4 / (1e4 + ent["bps"])
    tok = ent["vt"] - ent["vt"] * ent["vq"] / (ent["vq"] + net_in)
    fol = (1e9 if follow is True else follow) if follow else None
    ex, why, peak = None, "time", px_in
    for i in range(j + 1, len(tr)):
        e = tr[i]; px = (vta / e["vt"]) ** 2; peak = max(peak, px)
        if e.get("real") == 0: why, ex = "graduated", i; break
        if fol is not None and e["user"] == W and not e["buy"] and px < fol: why, ex = "its_sell", min(i + 1, len(tr) - 1); break
        if tp and px >= tp: why, ex = "tp", min(i + 1, len(tr) - 1); break
        if sl and px <= sl: why, ex = "stop", min(i + 1, len(tr) - 1); break
        if trail and peak >= 1.3 and px <= peak * trail: why, ex = "trail", min(i + 1, len(tr) - 1); break
        if e["t"] - t0 >= hold: why, ex = "time", i; break
    if ex is None: ex = len(tr) - 1
    x = tr[ex]
    vq_r = x["vq"] + net_in; vt_r = x["vt"] * x["vq"] / vq_r
    out = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - x["bps"] / 1e4)
    sol = out * rate * (1 - 0.003) / 1e9
    return dict(exit=why, px_in=px_in, px_out=(vta / x["vt"]) ** 2, peak=peak, held=x["t"] - t0, net=sol - stake - 0.0026, trades_ahead=j - k)
