# Winners first, step 1 (the owner, Nov 17: "find edge with traders that buy big good coins ... then we engineer the
# copy and the exit"). The outcome of every pump launch of the market scan's 48 h (SP/market/creates.json, from
# ../wallet_hunt/market/m1_launches.py): its bonding curve read now (getMultipleAccounts, 100 a call). complete = the
# curve filled and the coin migrated (graduated); otherwise real_quote_reserves = how far it got... at the end (not its peak).
# Out: SP/winners/outcomes.json {mint: [complete 0/1, real_quote_reserves, quote, t, creator]}.
# The RPC from RPC_URL, never printed.
#   RPC_URL=... python3 -I w1_outcomes.py SP
import sys, os, json, base64, struct, urllib.request, concurrent.futures as cf
from solders.pubkey import Pubkey
SP = sys.argv[1]; OUT = f"{SP}/winners"; os.makedirs(OUT, exist_ok=True)
URL = os.environ["RPC_URL"]; PUMP = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
def rpc(method, params):
    for _ in range(6):
        try:
            rq = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
                                        {"Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(rq, timeout=60))["result"]
        except Exception: pass
    return None
cr = json.load(open(f"{SP}/market/creates.json"))
coins = {}
for v in cr.values():
    if v and v.get("mint"): coins[v["mint"]] = v
mints = sorted(coins)
def curve(m): return str(Pubkey.find_program_address([b"bonding-curve", bytes(Pubkey.from_string(m))], PUMP)[0])
def batch(ms):
    r = rpc("getMultipleAccounts", [[curve(m) for m in ms], {"encoding": "base64"}]); out = {}
    if r is None: return out
    for m, a in zip(ms, r["value"]):
        d = base64.b64decode(a["data"][0]) if a else b""
        if len(d) < 49: out[m] = None; continue   # no curve (never created, or closed)
        vtr, vqr, rtr, rqr, sup = struct.unpack_from("<5Q", d, 8)
        out[m] = [d[48], rqr]
    return out
res = {}
with cf.ThreadPoolExecutor(16) as ex:
    for o in ex.map(batch, [mints[i:i + 100] for i in range(0, len(mints), 100)]): res.update(o)
O = {m: (res[m] + [coins[m].get("quote"), coins[m]["t"], coins[m].get("creator")]) for m in mints if res.get(m)}
json.dump(O, open(f"{OUT}/outcomes.json", "w"))
SOLQ = {"So11111111111111111111111111111111111111112", "11111111111111111111111111111111", None, "?"}
for name, f in (("SOL-priced", lambda q: q in SOLQ), ("other-token", lambda q: q not in SOLQ)):
    v = [x for x in O.values() if f(x[2])]; g = sum(x[0] for x in v)
    print(f"{name:12s}: {len(v):6d} launches, graduated {g:5d} ({100 * g / max(1, len(v)):.2f}%)")
print(f"read {len(O)} of {len(mints)} curves")
