# Does pump's multi_hop_swap take a pool that is not the canonical one? Every pool hop in its 663 routes is canonical
# (routes.json), and route.rs only looks for canonical pools. Simulated on mainnet now (simulateTransaction, no
# signature check, the payer wallet 4 itself, nothing sent): a 1-hop multi_hop_swap of 0.01 wSOL into USDC through
# the deepest USDC / wSOL PumpSwap pool (non-canonical, pools.py), into PUMP through the PUMP / USDC pool, and the
# same through a canonical pool from its own route (control). Accounts as crates/pump-codec/src/multihop.rs lays them out,
# the 13 fixed ones copied from its own transaction.   python3 -I sim_pool.py
import sys, json, base64, struct
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
SPX = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/more"
sys.path.insert(0, SP + "/month"); sys.path.insert(0, SP + "/rivalpnl")
import tri, common as C
W = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
WSOL, USDC, PUMPT = "So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn"
SPL, T22, SYS = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb", "11111111111111111111111111111111"
ATAP, PAMM = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL", "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
DISC = bytes.fromhex("2b644913e9f66f94")
def ata(o, m, p): return C.find_pda([C.b58d(o), C.b58d(p), C.b58d(m)], ATAP)
# its own class-A buy (wSOL -> canonical pool H74CYm / wSOL -> curve): the fixed accounts and the control pool
Qs = json.load(open(f"{SPX}/quotes.json")); Rt = json.load(open(f"{SPX}/routes.json"))
ref = next(q for q in reversed(Qs) if q["cls"] == "A" and (Rt.get(q["sig"]) or {}).get("hops"))
tx = tri.rpc("getTransaction", [ref["sig"], {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}], cache=False)
ks = tx["transaction"]["message"]["accountKeys"]
mh = next([ks[i] for i in ix["accounts"]] for ix in tx["transaction"]["message"]["instructions"] if ks[ix["programIdIndex"]] == PAMM)
fixed = mh[3:16]                     # global config .. event authority (index 3-15), uva and the wSOL buyback account in
ctrl = mh[16:21]                     # its first hop: base, quote (wSOL), canonical pool, vaults
def compile_legacy(payer, ixs):
    keys = {payer: [True, True]}
    for prog, accs, _ in ixs:
        keys.setdefault(prog, [False, False])
        for k, sgn, wr in accs:
            e = keys.setdefault(k, [False, False]); e[0] |= sgn; e[1] |= wr
    order = sorted(keys, key=lambda k: (k != payer, not keys[k][0], not keys[k][1]))
    hdr = bytes([sum(keys[k][0] for k in order), sum(keys[k][0] and not keys[k][1] for k in order),
                 sum(not keys[k][0] and not keys[k][1] for k in order)])
    cu = lambda n: bytes([n]) if n < 128 else bytes([n & 0x7f | 0x80, n >> 7])
    out = hdr + cu(len(order)) + b"".join(C.b58d(k).rjust(32, b"\0") for k in order) + b"\0" * 32 + cu(len(ixs))
    for prog, accs, data in ixs:
        out += bytes([order.index(prog)]) + cu(len(accs)) + bytes(order.index(k) for k, _, _ in accs) + cu(len(data)) + data
    return b"\x01" + b"\0" * 64 + out
def prog_of(m): return tri.rpc("getAccountInfo", [m, {"encoding": "base64", "dataSlice": {"offset": 0, "length": 0}}], cache=False)["value"]["owner"]
def run(name, hop, out_mint, amount=10_000_000):
    out_prog = prog_of(out_mint)
    w_in, w_out = ata(W, WSOL, SPL), ata(W, out_mint, out_prog)
    ixs = [(ATAP, [(W, 1, 1), (w_in, 0, 1), (W, 0, 0), (WSOL, 0, 0), (SYS, 0, 0), (SPL, 0, 0)], b"\x01"),
           (SYS, [(W, 1, 1), (w_in, 0, 1)], struct.pack("<IQ", 2, amount)),
           (SPL, [(w_in, 0, 1)], b"\x11"),
           (ATAP, [(W, 1, 1), (w_out, 0, 1), (W, 0, 0), (out_mint, 0, 0), (SYS, 0, 0), (out_prog, 0, 0)], b"\x01")]
    accs = [(W, 1, 1), (w_in, 0, 1), (w_out, 0, 1)] + [(k, 0, i in (2, 3)) for i, k in enumerate(fixed)]
    for h in hop:
        accs += [(h[0], 0, 0), (h[1], 0, 0), (h[2], 0, 1), (h[3], 0, 1), (h[4], 0, 1)]
    ixs.append((PAMM, accs, DISC + struct.pack("<QQ", amount, 1)))
    raw = compile_legacy(W, ixs)
    r = tri.rpc("simulateTransaction", [base64.b64encode(raw).decode(), {"encoding": "base64", "sigVerify": False,
                "replaceRecentBlockhash": True, "commitment": "processed"}], cache=False)["value"]
    logs = r.get("logs") or []
    print(f"   {name:58s} {len(raw)} bytes  err {r.get('err')}  units {r.get('unitsConsumed')}")
    for l in logs:
        if "Error" in l or "failed" in l or "error" in l.lower(): print("      ", l[:260])
PL = json.load(open(f"{SPX}/pools.json"))["tokens"]
u = PL[USDC]["pools"]["wsol"][0]; p = PL[PUMPT]["pools"]["usdc"][0]
print(f"fixed accounts from its buy {ref['sig'][:12]}; control pool {ctrl[2][:8]} (canonical)")
run("control: wSOL -> its canonical pool " + ctrl[0][:8], [ctrl], ctrl[0])
run(f"wSOL -> USDC through {u['pool'][:8]} (non-canonical, {u['sol_side']:.0f} SOL deep)",
    [[u["base"], u["quote"], u["pool"], u["vb"], u["vq"]]], USDC)
run(f"wSOL -> USDC -> PUMP through {u['pool'][:8]} and {p['pool'][:8]}",
    [[u["base"], u["quote"], u["pool"], u["vb"], u["vq"]], [p["base"], p["quote"], p["pool"], p["vb"], p["vq"]]], PUMPT)
