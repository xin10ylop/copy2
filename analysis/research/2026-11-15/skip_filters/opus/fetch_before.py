# Fetch each copyable coin's history BEFORE wallet 4's buy (for the "coin age / activity before" filters):
# getSignaturesForAddress(mint, before = its buy's signature, limit = 1000), one request a coin, cached as JSON under
# SKQ/before/<key>.json [slot, blockTime, landed ok, signature]. Then the coin's first transaction (its creation; every coin
# here has under 1000 before its buy) with getTransaction, cached as SKQ/create/<key>.json. At most 12 requests at once. The RPC URL is read from the scratchpad file, never printed.
#   python3 -I fetch_before.py SPD SKQ
import sys, os, json, gzip, urllib.request, concurrent.futures, time
SPD, SKQ = sys.argv[1], sys.argv[2]
URL = open("/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/month/.triton_url").read().strip()
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
os.makedirs(f"{SKQ}/before", exist_ok=True)
P = json.load(gzip.open(f"{SPD}/paths.json.gz"))
def rpc(method, params):
    body = json.dumps(dict(jsonrpc="2.0", id=1, method=method, params=params)).encode()
    for a in range(5):
        try:
            req = urllib.request.Request(URL, body, {"Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:
            err = type(e).__name__; time.sleep(2 + 3 * a)
    raise RuntimeError("rpc failed: " + err)
def one(key):
    out = f"{SKQ}/before/{key}.json"
    if os.path.exists(out): return "cached"
    mint, tr = P[key]; slot = int(key.split("_")[0])
    sig = next(e["sig"] for e in tr if e["user"] == W4 and e["buy"] and e["slot"] == slot)
    r = rpc("getSignaturesForAddress", [mint, {"before": sig, "limit": 1000}])
    if "result" not in r: return "error " + str(r.get("error", {}).get("code"))
    json.dump(dict(mint=mint, sig=sig, res=[[x["slot"], x.get("blockTime"), x["err"] is None, x["signature"]] for x in r["result"]]), open(out, "w"))
    return "ok"
def create(key):
    out = f"{SKQ}/create/{key}.json"
    if os.path.exists(out): return "cached"
    b = json.load(open(f"{SKQ}/before/{key}.json"))["res"]
    if not b or len(b) >= 1000: return "none"
    sig = b[-1][3]
    r = rpc("getTransaction", [sig, {"encoding": "json", "maxSupportedTransactionVersion": 1}])
    if not r.get("result"): return "error"
    json.dump(r["result"], open(out, "w")); return "ok"
if __name__ == "__main__":
    keys = [k for k, v in P.items() if v]
    with concurrent.futures.ThreadPoolExecutor(12) as ex:
        res = list(ex.map(one, keys))
    import collections; print(len(keys), "coins, signatures before its buy:", collections.Counter(res))
    os.makedirs(f"{SKQ}/create", exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(12) as ex:
        res = list(ex.map(create, keys))
    print("creation transactions:", collections.Counter(res))
