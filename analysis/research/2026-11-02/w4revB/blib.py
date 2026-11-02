# Shared helper for w4revB (wallet 4's part B, bought at launch ourselves).
# - Triton JSON-RPC and the pump event decoders of the scan agent (../agents/scan/bin/crc.py: URL read from the old
#   scratchpad's month/.triton_url, never printed, redacted in errors), paced at MIN_GAP = 0.06 s.
# - Cache: every response is looked up first in the part-A agent's cache (../w4rev/cache) and the scan agent's cache
#   (../agents/scan/out/cache), read-only; new responses are written to this folder's cache/ only.
# - crow(): the create-row decoder of ../w4rev/s1b_crow.py; listing()/trades(): the tape code of ../w4rev/tape.py
#   (copied, so nothing is written into w4rev).
# - canonical PumpSwap pool derivation (../w4rev/lib.py, seeds as crates/pump-codec/src/pda.rs).
import os, sys, json, hashlib, gzip, bisect
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(G, "agents", "scan", "bin"))
import crc                                   # noqa: E402
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
crc.CACHE = os.path.join(HERE, "cache"); os.makedirs(crc.CACHE, exist_ok=True)
crc.OUT = OUT
crc.MIN_GAP = 0.06
RO_CACHES = [os.path.join(G, "w4rev", "cache"), os.path.join(G, "agents", "scan", "out", "cache")]
A_OUT = os.path.join(G, "w4rev", "out")      # the part-A agent's outputs (read-only)
SP0 = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
H9 = SP0 + "/h9long"
PUMP, PAMM, MINT_AUTH = crc.PUMP, crc.PUMPSWAP, crc.MINT_AUTH
WSOL = crc.WSOL; WBTC = "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh"; SOL_LIKE = crc.SOL_LIKE
W4 = crc.W4
events, keys_of, red, b58d, b58e = crc.events, crc.keys_of, crc.red, crc.b58d, crc.b58e
NRO = [0]
def rpc(method, params, cache=True):
    if cache:
        h = hashlib.sha1(json.dumps([method, params], sort_keys=True).encode()).hexdigest()
        for d in RO_CACHES:
            p = os.path.join(d, h[:2], h + ".json.gz")
            if os.path.exists(p):
                try:
                    v = json.load(gzip.open(p, "rt")); NRO[0] += 1; return v
                except Exception:
                    pass
    return crc.rpc(method, params, cache)
def tx(sig): return rpc("getTransaction", [sig, crc.TXO])
def sigs(addr, before=None, until=None, limit=1000, cache=True):
    o = {"limit": limit, "commitment": "confirmed"}
    if before: o["before"] = before
    if until: o["until"] = until
    return rpc("getSignaturesForAddress", [addr, o], cache=cache) or []
def calls(): return crc.NCALLS[0]
def jdump(o, p):
    tmp = p + ".tmp"; json.dump(o, open(tmp, "w")); os.replace(tmp, p)
def jl(p): return json.load(open(p))
# ---- canonical pools (../w4rev/lib.py)
_P = 2**255 - 19; _D = (-121665 * pow(121666, _P - 2, _P)) % _P
def on_curve(b):
    y = int.from_bytes(b, "little") & ((1 << 255) - 1)
    if y >= _P: return False
    y2 = y * y % _P; u = (y2 - 1) % _P; v = (_D * y2 + 1) % _P
    x2 = u * pow(v, _P - 2, _P) % _P
    return x2 == 0 or pow(x2, (_P - 1) // 2, _P) == 1
def find_pda(seeds, program):
    pid = b58d(program)
    for bump in range(255, -1, -1):
        h = hashlib.sha256(b"".join(seeds) + bytes([bump]) + pid + b"ProgramDerivedAddress").digest()
        if not on_curve(h): return b58e(h)
def pool_authority(m): return find_pda([b"pool-authority", b58d(m)], PUMP)
def canonical(m, q): return find_pda([b"pool", (0).to_bytes(2, "little"), b58d(pool_authority(m)), b58d(m), b58d(q)], PAMM)
assert canonical("2gLnaQN8Y73Qc62gMmX6WtJQjFnbvE7vgzUJ37WJpump", WSOL) == "8Xev4PoVsLfyt1A31cGUcGU9tW738MaGsB2MczezcgVf"
# ---- create row (../w4rev/s1b_crow.py)
def top_progs(t):
    out = []
    for ix in t["transaction"]["message"]["instructions"]:
        p = ix.get("programId")
        if p and p not in out: out.append(p)
    return out
def crow(t, sig):
    ev = events(t); cr = [e for k, e in ev if k == "create"]
    if not cr: return None
    c = cr[0]; m = c["mint"]; ks = keys_of(t)
    return dict(csig=sig, cslot=t["slot"], cbt=t.get("blockTime"), cidx=t.get("transactionIndex"), payer=ks[0],
                mint=m, quote=c.get("quote_mint"), user=c["user"], creator=c["creator"], name=c["name"][:64], sym=c["symbol"][:32],
                uri=c["uri"][:200], vquote=c.get("vquote"), vsol=c["vsol"], vtok=c["vtok"], depth=c.get("depth"),
                mayhem=c.get("mayhem"), cashback=c.get("cashback"), cfee=c.get("creator_fee_bps"), token_program=c.get("token_program"),
                dev=[[e["user"], e["is_buy"], e["sol"], e["tok"], e.get("quote_amount"), e["vtok"]] for k, e in ev if k == "trade" and e["mint"] == m],
                fee=(t.get("meta") or {}).get("fee"), progs=top_progs(t), nsig=len(t["transaction"].get("signatures") or []),
                cu=(t.get("meta") or {}).get("computeUnitsConsumed"))
# ---- tapes (../w4rev/tape.py): cursors are any landed signatures with a slot (mint authority, quote control)
_S = None
import threading
_LK = threading.Lock()
def _load():
    global _S, _SL, _BT
    with _LK:
        if _S is None:
            rows = {}
            for p in (A_OUT + "/s1_sigs.json", os.path.join(G, "agents", "scan", "out", "s1_sigs.json"), A_OUT + "/qc_sigs.json"):
                if os.path.exists(p):
                    for r in jl(p): rows[r[0]] = r
            S_ = sorted(rows.values(), key=lambda r: (r[1], r[2]))
            _SL = [r[1] for r in S_]; _BT = [r[2] for r in S_]; _S = S_
def cur_slot(slot):
    _load(); i = bisect.bisect_left(_SL, slot); return _S[min(i, len(_S) - 1)][0]
def cur_time(bt):
    _load(); i = bisect.bisect_left(_BT, bt); return _S[min(i, len(_S) - 1)][0]
def cursor_max_bt():
    _load(); return _BT[-1]
MAXP = 4
def _page_back(mint, before, csig, stop_bt):
    got = []
    for k in range(MAXP):
        page = sigs(mint, before=before, until=csig, limit=1000)
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
    L = sorted(got.values(), key=lambda r: r[1])
    order = {s: i for i, s in enumerate(got)}
    L.sort(key=lambda r: (r[1], -order[r[0]]))
    return L, gaps
def trades(sig, mint):
    t = tx(sig)
    if not t: return None
    out = []; k = 0
    for kind, e in events(t):
        if kind != "trade" or e["mint"] != mint: continue
        q = e.get("quote_amount") if e.get("quote_mint") not in SOL_LIKE and e.get("vquote") else e["sol"]
        vq = e.get("vquote") if e.get("quote_mint") not in SOL_LIKE and e.get("vquote") else e["vsol"]
        out.append([t["slot"], t.get("transactionIndex"), k, e["user"], int(e["is_buy"]), q, e["tok"], e["vtok"], vq, e.get("ix"), t.get("blockTime")])
        k += 1
    return out
# ---- periods: P1 = Oct 19-22, P2 = Oct 23-26 (creates to Oct 27 00:00 UTC)
P1_END = 1792713600        # 2026-10-23 00:00 UTC
T_LO = 1792368000          # 2026-10-19 00:00 UTC
T_HI = 1793059200          # 2026-10-27 00:00 UTC
def per(bt): return "P1" if bt < P1_END else "P2"
