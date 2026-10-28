# Is there a PumpSwap pool from an anchor (wSOL, or the WBTC float) to each token its part-B buys paid in? For every
# token in SPX/quotes.json (class E) and SPX/routes.json (each hop's mints): the canonical pool route.rs looks for,
# canonical_pump_swap_pool(token, anchor) = ["pool", 0u16, pool_authority(token), token, anchor] (seeds as in
# crates/pump-codec/src/pda.rs), checked with getAccountInfo; and every other PumpSwap pool of the pair, either way
# round (getProgramAccounts, base_mint at byte 43, quote_mint at 75 of the 301-byte Pool account; vaults at 139 and
# 171). Reserves now (Oct 28) from the vaults; the SOL side of a WBTC pool at Jupiter's WBTC price. A 1 SOL hop's
# price impact on constant product is 1 / (R + 1), R the SOL side in SOL.   python3 -I pools.py  ->  SPX/pools.json
import sys, os, json, base64, urllib.request
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
SPX = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/more"
sys.path.insert(0, SP + "/month"); sys.path.insert(0, SP + "/rivalpnl")
import tri, common as C
PAMM, PUMP = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA", "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
WSOL, WBTC = "So11111111111111111111111111111111111111112", "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh"
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"   # deep against wSOL on PumpSwap: a possible middle hop
NM = {WSOL: "wsol", WBTC: "wbtc", USDC: "usdc"}
def pool_authority(m): return C.find_pda([b"pool-authority", C.b58d(m)], PUMP)
def canonical(m, q): return C.find_pda([b"pool", (0).to_bytes(2, "little"), C.b58d(pool_authority(m)), C.b58d(m), C.b58d(q)], PAMM)
# the derivation checked on a canonical pool seen in its own route (2gLnaQN8 / wSOL = 8Xev4PoV, creator 6Qy8Sdma)
assert canonical("2gLnaQN8Y73Qc62gMmX6WtJQjFnbvE7vgzUJ37WJpump", WSOL) == "8Xev4PoVsLfyt1A31cGUcGU9tW738MaGsB2MczezcgVf"
Qs = json.load(open(f"{SPX}/quotes.json")); Rt = json.load(open(f"{SPX}/routes.json"))
toks = set()
for q in Qs:
    if q["cls"] != "E": continue
    r = Rt.get(q["sig"]) or {}
    if q["pay"]: toks.add(q["pay"])
    for h in r.get("hops") or []:
        toks.update(h[1:3])
if os.path.exists(f"{SPX}/skips.json"):          # the paper run's skips (skips.py) add the tokens of Oct 27-28
    toks.update(o["pay"] for o in json.load(open(f"{SPX}/skips.json")) if o.get("pay"))
toks -= {WSOL, WBTC}
toks = {t for t in toks if not t.endswith("pump") or any(t == (Rt.get(q["sig"]) or {}).get("curve_quote") for q in Qs)}
ids = sorted(toks | {WSOL, WBTC, USDC})
px = {}
for k in range(0, len(ids), 50):
    with urllib.request.urlopen("https://lite-api.jup.ag/price/v3?ids=" + ",".join(ids[k:k + 50]), timeout=30) as f:
        px.update(json.load(f))
sol_usd = px[WSOL]["usdPrice"]; wbtc_sol = px[WBTC]["usdPrice"] / sol_usd
def bal(accts):
    out = {}
    for k in range(0, len(accts), 100):
        v = tri.rpc("getMultipleAccounts", [accts[k:k + 100], {"encoding": "jsonParsed"}], cache=False)["value"]
        for a, x in zip(accts[k:k + 100], v):
            try: out[a] = float(x["data"]["parsed"]["info"]["tokenAmount"]["uiAmountString"])
            except Exception: out[a] = None
    return out
res = {}
for t in sorted(toks):
    o = dict(jup_usd=(px.get(t) or {}).get("usdPrice"), pools={})
    for a in (WSOL, WBTC, USDC):
        cp = canonical(t, a)
        if a == t: continue
        o["canonical_" + NM[a]] = tri.rpc("getAccountInfo", [cp, {"encoding": "base64", "dataSlice": {"offset": 0, "length": 0}}], cache=False)["value"] is not None
        found = []
        for base, quote in ((t, a), (a, t)):
            r = tri.rpc("getProgramAccounts", [PAMM, {"encoding": "base64", "dataSlice": {"offset": 0, "length": 203},
                        "filters": [{"memcmp": {"offset": 43, "bytes": base}}, {"memcmp": {"offset": 75, "bytes": quote}}]}], cache=False)
            for p in r:
                d = base64.b64decode(p["account"]["data"][0])
                found.append(dict(pool=p["pubkey"], base=base, quote=quote, creator=C.b58e(d[11:43]), index=int.from_bytes(d[9:11], "little"),
                                  vb=C.b58e(d[139:171]), vq=C.b58e(d[171:203]), canonical=p["pubkey"] == cp))
        b = bal([f["vb"] for f in found] + [f["vq"] for f in found])
        for f in found:
            anc = b[f["vq"]] if f["quote"] == a else b[f["vb"]]
            f["anchor_reserve"] = anc
            f["sol_side"] = None if anc is None else (anc if a == WSOL else anc * wbtc_sol if a == WBTC else anc / sol_usd)
        found.sort(key=lambda f: -(f["sol_side"] or 0))
        o["pools"][NM[a]] = found
    res[t] = o
json.dump(dict(tokens=res, sol_usd=sol_usd, wbtc_sol=wbtc_sol), open(f"{SPX}/pools.json", "w"))
print(f"SOL ${sol_usd:.2f}, WBTC {wbtc_sol:.1f} SOL; {len(res)} tokens")
print(f"{'token':46s} {'jup $':>10s} {'canon wSOL':>10s} {'canon WBTC':>10s} {'wSOL pools':>10s} {'best SOL side':>13s} {'1 SOL impact':>12s} {'WBTC pools':>10s} {'USDC pools':>10s} {'best SOL side':>13s}")
for t, o in sorted(res.items(), key=lambda kv: -max([f["sol_side"] or 0 for f in kv[1]["pools"]["wsol"]] + [0])):
    ws, wb, wu = o["pools"]["wsol"], o["pools"]["wbtc"], o["pools"].get("usdc") or []
    bs = ws[0]["sol_side"] if ws else None; bb = wb[0]["sol_side"] if wb else None
    print(f"  {t:44s} {o['jup_usd'] or 0:10.4g} {str(o['canonical_wsol']):>10s} {str(o['canonical_wbtc']):>10s} {len(ws):10d} "
          f"{(bs or 0):13.1f} {(1 / (bs + 1) if bs else 1):12.2%} {len(wb):10d} {len(wu):10d} {(wu[0]['sol_side'] if wu else 0) or 0:13.1f}")
