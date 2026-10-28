# Route class of a wallet's curve buy from the curve's QUOTE token (pull.py's "qm"), as rugsnipe-long's route.rs would
# find it, not from the wallet's own route (route_cls.py reads wallet 4's route, which other wallets do not share):
#   C  the curve is quoted in WBTC (we hold a WBTC float)
#   A  the quote has a canonical PumpSwap pool against wSOL (multihop from wSOL)
#   B  the quote has a canonical PumpSwap pool against WBTC only (multihop from the WBTC float)
#   E  neither (PUMP, CARDS, TTWO, USDC, xStocks ...: not routable through pump's own programs; 02-decomposition §2)
# The canonical pool is ../../../2026-10-28/more/pools.py's canonical(token, anchor) (seeds as crates/pump-codec pda.rs),
# checked with getAccountInfo and cached in SP/h9long/pools_q.json. ROUTECLS=wallet4 uses route_cls.py instead (the
# fresh study's class, for re-checking these copies on wallet 4's own data).
#   python3 -I route_q.py WALLET      (fetches the pools for every quote token the wallet's rows show, prints the mix)
import os, sys, json, collections
SP0 = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
SP = os.environ.get("SP", "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/score")
W = sys.argv[1] if __name__ == "__main__" else os.environ.get("W", "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg")
WSOL, WBTC = "So11111111111111111111111111111111111111112", "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh"
PAMM, PUMP = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA", "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
if os.environ.get("ROUTECLS") == "wallet4":
    sys.path.insert(0, "/home/user/copy2/analysis/research/2026-10-28/fresh")
    from route_cls import cls  # noqa: F401
else:
    sys.path.insert(0, SP0 + "/month"); sys.path.insert(0, SP0 + "/rivalpnl")
    import common as C
    QM = {}                                    # (coin, slot, is_buy) -> the curve's quote mint
    for l in open(f"{SP}/h9long/{W[:8]}.jsonl"):
        r = json.loads(l)
        for t in r["tr"]:
            if t[1] == W and t[0] in r.get("qm", {}): QM[(t[0], r["s"], t[2])] = r["qm"][t[0]]
    COIN_Q = {k[0]: v for k, v in QM.items()}
    PF = f"{SP}/h9long/pools_q.json"
    POOLS = json.load(open(PF)) if os.path.exists(PF) else {}
    def pool_authority(m): return C.find_pda([b"pool-authority", C.b58d(m)], PUMP)
    def canonical(m, q): return C.find_pda([b"pool", (0).to_bytes(2, "little"), C.b58d(pool_authority(m)), C.b58d(m), C.b58d(q)], PAMM)
    assert canonical("2gLnaQN8Y73Qc62gMmX6WtJQjFnbvE7vgzUJ37WJpump", WSOL) == "8Xev4PoVsLfyt1A31cGUcGU9tW738MaGsB2MczezcgVf"
    def pools(q):
        if q not in POOLS:
            import tri
            POOLS[q] = [bool((tri.rpc("getAccountInfo", [canonical(q, a), {"encoding": "base64", "dataSlice": {"offset": 0, "length": 8}}]) or {}).get("value"))
                        for a in (WSOL, WBTC)]
            json.dump(POOLS, open(PF, "w"))
        return POOLS[q]
    def quote_of(x):
        b = x["tr"][0]
        return QM.get((x["m"], b["s"], 1)) or COIN_Q.get(x["m"])
    def cls(x):
        q = quote_of(x)
        if not q: return "?"
        if q == WBTC: return "C"
        if q == WSOL: return "A"
        w, b = pools(q)
        return "A" if w else "B" if b else "E"
if __name__ == "__main__":
    qs = collections.Counter(COIN_Q.values())
    for q in qs: pools(q)
    print(f"{W[:8]}: {len(COIN_Q)} curves traded, {len(qs)} quote tokens")
    for q, n in qs.most_common(25):
        w, b = POOLS[q]
        print(f"   {q[:8]}  curves {n:5d}  canonical pool vs wSOL {w}  vs WBTC {b}  -> {'C' if q in (WBTC, WSOL) else 'A' if w else 'B' if b else 'E'}")
