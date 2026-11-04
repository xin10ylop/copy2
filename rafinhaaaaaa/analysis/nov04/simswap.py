# The copier's swap, built by Jupiter exactly as jup.rs asks for it (wrapAndUnwrapSol, dynamicComputeUnitLimit, a 0.001
# SOL Jito tip inside), simulated on mainnet (sigVerify off, recent blockhash replaced). Buy: 1 SOL -> coin, paid by a
# funded wallet that has never held the coin (its token account is created in the swap). Sale: a holder's tokens -> SOL.
#   python3 -I simswap.py PAYER MINT [MINT ...]
import json, sys, time, urllib.request, base64
RPC = "https://api.mainnet-beta.solana.com"; J = "https://lite-api.jup.ag/swap/v1"; SOL = "So11111111111111111111111111111111111111112"
last = [0.0]
def http(url, body=None):
    dt = time.time() - last[0]
    if dt < 1.2: time.sleep(1.2 - dt)
    last[0] = time.time()
    for i in range(4):
        try:
            req = urllib.request.Request(url, json.dumps(body).encode() if body is not None else None, {"Content-Type": "application/json"})
            return 200, json.loads(urllib.request.urlopen(req, timeout=30).read())
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(5 * (i + 1)); continue
            return e.code, e.read().decode()[:200]
        except Exception as e: time.sleep(2)
    return 0, None
def rpc(m, p):
    st, r = http(RPC, {"jsonrpc": "2.0", "id": 1, "method": m, "params": p})
    return (r or {}).get("result") if isinstance(r, dict) else None
def sim(user, inp, out, amt, slip):
    st, q = http(f"{J}/quote?inputMint={inp}&outputMint={out}&amount={amt}&slippageBps={slip}")
    if st != 200: return dict(stage="quote", http=st, body=str(q)[:120])
    route = " > ".join(r["swapInfo"]["label"] for r in q["routePlan"])
    st, s = http(f"{J}/swap", {"quoteResponse": q, "userPublicKey": user, "wrapAndUnwrapSol": True,
                               "dynamicComputeUnitLimit": True, "prioritizationFeeLamports": {"jitoTipLamports": 1000000}})
    if st != 200: return dict(stage="swap", http=st, body=str(s)[:120], route=route)
    raw = base64.b64decode(s["swapTransaction"])
    r = rpc("simulateTransaction", [s["swapTransaction"], {"sigVerify": False, "replaceRecentBlockhash": True, "encoding": "base64",
                                                          "commitment": "processed"}])
    v = (r or {}).get("value") or {}
    logs = v.get("logs") or []
    return dict(stage="sim", route=route, out=q["outAmount"], impact=q.get("priceImpactPct"), nsig=raw[0], ver=hex(raw[65]),
                size=len(raw), err=v.get("err"), cu=v.get("unitsConsumed"), cu_limit=s.get("computeUnitLimit"),
                tip_in=any("Transfer" in l for l in logs[:3]) or None, last=(logs[-1][:90] if logs else None))
def holder(mint):
    r = rpc("getTokenLargestAccounts", [mint])
    for a in (r or {}).get("value", [])[1:6]:                  # skip the largest (often the pool / curve)
        ai = rpc("getAccountInfo", [a["address"], {"encoding": "jsonParsed"}])
        try:
            inf = ai["value"]["data"]["parsed"]["info"]; own = inf["owner"]
            if int(inf["tokenAmount"]["amount"]) > 0:
                oi = rpc("getAccountInfo", [own, {"encoding": "base64"}])
                if oi and oi["value"] and oi["value"]["owner"] == "11111111111111111111111111111111" and oi["value"]["lamports"] > 10_000_000:
                    return own, int(inf["tokenAmount"]["amount"])
        except Exception: pass
    return None, 0
payer = sys.argv[1]
for m in sys.argv[2:]:
    b = sim(payer, SOL, m, 1_000_000_000, 2000)
    print(m[:8], "BUY ", json.dumps(b), flush=True)
    h, amt = holder(m)
    if h:
        s = sim(h, m, SOL, max(1, amt // 10), 5000)
        print(m[:8], "SELL", json.dumps(s), flush=True)
    else: print(m[:8], "SELL no plain-wallet holder found", flush=True)
