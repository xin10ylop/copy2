# Route class of a curve from its QUOTE mint, as rugsnipe-long's route.rs would find it (copy2
# analysis/research/2026-10-29/wallets/score/route_q.py): C = quoted in WBTC (a WBTC float); A = the quote has a canonical
# PumpSwap pool against wSOL (multihop from wSOL); B = against WBTC only (multihop from the WBTC float); E = neither;
# S = SOL. The canonical pool is ["pool", 0u16, pool_authority(quote), quote, anchor] (crates/pump-codec/src/pda.rs),
# checked with getAccountInfo (state on Nov 1) and cached in out/pools_q.json.
import os, sys, json
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
PF = lib.OUT + "/pools_q.json"
POOLS = lib.jl(PF) if os.path.exists(PF) else {}
def _fetch(q):
    return q, [bool((lib.rpc("getAccountInfo", [lib.canonical(q, a), {"encoding": "base64", "dataSlice": {"offset": 0, "length": 8}}]) or {}).get("value"))
               for a in (lib.WSOL, lib.WBTC)]
def ensure(qs):
    todo = sorted({q for q in qs if q and q not in POOLS and q not in lib.SOL_LIKE and q != lib.WBTC})
    if todo:
        with ThreadPoolExecutor(8) as ex:
            for q, v in ex.map(_fetch, todo): POOLS[q] = v
        lib.jdump(POOLS, PF)
def cls(q):
    if q in lib.SOL_LIKE: return "S"
    if q == lib.WBTC: return "C"
    if q not in POOLS: ensure([q])
    w, b = POOLS[q]
    return "A" if w else "B" if b else "E"
