# Jupiter's free API: how fast can a quote and its swap go back to back, and is the swap refused (429) when sent right
# after its quote? 12 pairs, 5 s apart; each pair: quote, then the swap at once (no gap). Payer = a funded wallet.
import json, sys, time, urllib.request
J = "https://lite-api.jup.ag/swap/v1"; SOL = "So11111111111111111111111111111111111111112"; USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
payer = sys.argv[1]; out = []
def call(url, body=None):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, json.dumps(body).encode() if body is not None else None, {"Content-Type": "application/json"})
        r = urllib.request.urlopen(req, timeout=20); return r.status, json.loads(r.read()), time.time() - t0
    except urllib.error.HTTPError as e: return e.code, None, time.time() - t0
    except Exception: return 0, None, time.time() - t0
for i in range(12):
    st1, q, l1 = call(f"{J}/quote?inputMint={SOL}&outputMint={USDC}&amount=100000000&slippageBps=2000")
    st2, l2 = None, None
    if st1 == 200:
        st2, s, l2 = call(f"{J}/swap", {"quoteResponse": q, "userPublicKey": payer, "wrapAndUnwrapSol": True,
                                        "dynamicComputeUnitLimit": True, "prioritizationFeeLamports": {"jitoTipLamports": 1000000}})
    out.append((st1, round(l1, 3), st2, round(l2, 3) if l2 else None)); print(out[-1], flush=True)
    time.sleep(5)
ok = [o for o in out if o[0] == 200 and o[2] == 200]
print(len(ok), "of 12 pairs ok; quote p50", sorted(o[1] for o in ok)[len(ok)//2] if ok else None, "swap p50", sorted(o[3] for o in ok)[len(ok)//2] if ok else None)
