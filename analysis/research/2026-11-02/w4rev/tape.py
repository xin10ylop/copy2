# Launch tapes and price paths of a coin from the chain (Triton):
#   cursor(slot | time): a pump mint-authority or quote-control signature at or after it (out/s1_sigs.json, the scan
#     agent's Oct 29-31 list, out/qc_sigs.json to Nov 1 22:47), used as `before` (getSignaturesForAddress uses `before` for its slot).
#   listing(mint, csig, cbt, t_end): the landed signatures on the mint from its create to t_end s after it, oldest
#     first, paged by segment ([0, 60], (60, 300], (300, t_end]) with at most MAXP pages a segment.
#   trades(sig, mint): the coin's pump TradeEvents in one transaction, in order: [slot, idx, k, user, buy, q, tok, vt, vq, ix, bt]
#     (q = quote amount, or lamports on a SOL curve; vq = virtual quote, or virtual SOL, after the trade).
import os, sys, bisect, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
_S = None
def _load():
    global _S, _SL, _BT
    if _S is None:
        a = lib.jl(lib.OUT + "/s1_sigs.json")
        b = lib.jl(os.path.join(lib.HERE, "..", "agents", "scan", "out", "s1_sigs.json"))
        c = lib.jl(lib.OUT + "/qc_sigs.json")           # quote-control signatures: cursors up to Nov 1 22:47 UTC
        _S = sorted({r[0]: r for r in a + b + c}.values(), key=lambda r: (r[1], r[2]))
        _SL = [r[1] for r in _S]; _BT = [r[2] for r in _S]
def cur_slot(slot):
    _load(); i = bisect.bisect_left(_SL, slot); return _S[min(i, len(_S) - 1)][0]
def cur_time(bt):
    _load(); i = bisect.bisect_left(_BT, bt); return _S[min(i, len(_S) - 1)][0]
MAXP = 4
def _page_back(mint, before, csig, stop_bt):
    got, capped = [], False
    for k in range(MAXP):
        page = lib.sigs(mint, before=before, until=csig, limit=1000)
        got += page
        if len(page) < 1000: return got, False, True
        if (page[-1].get("blockTime") or 0) < stop_bt: return got, False, False
        before = page[-1]["signature"]
    return got, True, False
def listing(mint, csig, cbt, t_end=1830):
    """landed sigs (oldest first) [[sig, slot, bt]] from the create (excluded) to cbt + t_end; gaps where a segment hit MAXP"""
    segs = [(t_end, 300), (300, 60), (60, 0)]; got = {}; gaps = []
    for hi, lo in segs:
        rows, capped, reached = _page_back(mint, cur_time(cbt + hi), csig, cbt + lo)
        for p in rows:
            if p.get("err") is None and p.get("blockTime") is not None and p["blockTime"] <= cbt + t_end: got[p["signature"]] = [p["signature"], p["slot"], p["blockTime"]]
        if capped: gaps.append([lo, hi, min((p.get("blockTime") or 0) for p in rows) - cbt])
        if reached: break
    L = sorted(got.values(), key=lambda r: r[1])          # stable within a slot: kept in arrival order below
    order = {s: i for i, s in enumerate(got)}             # got's insertion order is newest first within each page
    L.sort(key=lambda r: (r[1], -order[r[0]]))
    return L, gaps
def trades(sig, mint):
    t = lib.tx(sig)
    if not t: return None
    out = []; k = 0
    for kind, e in lib.events(t):
        if kind != "trade" or e["mint"] != mint: continue
        q = e.get("quote_amount") if e.get("quote_mint") not in lib.SOL_LIKE and e.get("vquote") else e["sol"]
        vq = e.get("vquote") if e.get("quote_mint") not in lib.SOL_LIKE and e.get("vquote") else e["vsol"]
        out.append([t["slot"], t.get("transactionIndex"), k, e["user"], int(e["is_buy"]), q, e["tok"], e["vtok"], vq, e.get("ix"), t.get("blockTime")])
        k += 1
    return out
