# Quick fingerprint check of many wallets: newest 100 signatures, up to 15 of their own landed txs: how many tip exactly
# 1,067,000 or 1,010,000 lamports (wallet 4's two tip sizes), how many start with AdvanceNonceAccount, how many touch pump.
# Usage: fpscan.py LIST.json OUT.json
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
from concurrent.futures import ThreadPoolExecutor
L = json.load(open(sys.argv[1])); res = {}
def one(A):
    try:
        s = [x for x in tri.sigs(A, limit=100) if not x.get("err")]
        n = 0; tip = 0; nonce = 0; pump = 0
        for x in s[:15]:
            t = tri.tx(x["signature"])
            if not t: continue
            ks = keys_of(t)
            if ks[0] != A: continue
            n += 1; m = t["transaction"]["message"]; ix0 = m["instructions"][0]
            if ks[ix0["programIdIndex"]] == SYS and b58d(ix0.get("data", ""))[:4] == b"\x04\x00\x00\x00": nonce += 1
            if PUMP in ks or PUMPSWAP in ks: pump += 1
            if any(b in TIPS and a == A and l in (1067000, 1010000) for k, a, b, l, mm, d, inn in transfers(t)): tip += 1
        return A, dict(sigs=len(s), own=n, w4tip=tip, nonce=nonce, pump=pump)
    except Exception as e:
        return A, dict(err=str(e)[:80])
with ThreadPoolExecutor(6) as ex:
    for k, (A, r) in enumerate(ex.map(one, L)):
        res[A] = r
        if r.get("w4tip") or (r.get("nonce", 0) >= 3 and r.get("pump", 0) >= 3): print("FLAG", A, r, flush=True)
        if k % 25 == 0: print(k, "/", len(L), flush=True)
json.dump(res, open(sys.argv[2], "w"))
print("done", len(res), "with a wallet-4 tip size:", sum(1 for r in res.values() if r.get("w4tip")))
