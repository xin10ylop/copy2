# Attention study, step 1 (the owner, Nov 17: "what makes a memecoin successful ... isnt there something that predicts
# attention?"): the outcome of every pump launch of the 48 h in SP/market/creates.json (Nov 15 01:07 - Nov 17 01:07 UTC),
# read now from its bonding curve account: graduated (complete) or not, and how far the curve got (real token reserve
# left). getMultipleAccounts, 100 a call. The RPC from RPC_URL, never printed.
#   RPC_URL=... python3 -I a1_outcomes.py SP     -> SP/attn/outcomes.json {mint: [complete, progress] or None}
import sys, os, json, base64, struct, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from solders.pubkey import Pubkey as P
SP = sys.argv[1]; O = f"{SP}/attn"; os.makedirs(O, exist_ok=True); URL = os.environ["RPC_URL"]
PUMP = P.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
C = json.load(open(f"{SP}/market/creates.json")); mints = sorted({v["mint"] for v in C.values() if v})
def call(m, p):
    for i in range(8):
        try:
            rq = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(rq, timeout=60))
            if "error" in r: raise RuntimeError(str(r["error"])[:100])
            return r["result"]
        except Exception: time.sleep(1.5 * (i + 1))
    raise RuntimeError(m)
pda = lambda m: str(P.find_program_address([b"bonding-curve", bytes(P.from_string(m))], PUMP)[0])
def batch(ms):
    r = call("getMultipleAccounts", [[pda(m) for m in ms], {"encoding": "base64"}])["value"]; out = {}
    for m, a in zip(ms, r):
        if not a: out[m] = None; continue
        d = base64.b64decode(a["data"][0])
        if len(d) < 49: out[m] = None; continue   # an account with no curve data (lamports only): unknown
        vt, vq, rt, rq, sup = struct.unpack_from("<5Q", d, 8)
        out[m] = [bool(d[48]), 1 - rt / 793.1e12 if not d[48] else 1.0]
    return out
res = {}
with ThreadPoolExecutor(8) as ex:
    for o in ex.map(batch, [mints[i:i + 100] for i in range(0, len(mints), 100)]): res.update(o)
json.dump(res, open(f"{O}/outcomes.json", "w"))
ok = [v for v in res.values() if v]; print(f"{len(mints)} launches, {len(ok)} curves read, graduated {sum(v[0] for v in ok)} ({sum(v[0] for v in ok) / len(ok):.2%})")
