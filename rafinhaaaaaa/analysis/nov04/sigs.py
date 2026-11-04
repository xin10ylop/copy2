# Rafinhaaaaaa's signatures back to a time, public RPC: python3 -I sigs.py WALLET UNTIL_UNIX OUT_JSON
import json, sys, time, urllib.request
W, until, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
U = "https://api.mainnet-beta.solana.com"
def rpc(m, p):
    for i in range(8):
        try:
            b = json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode()
            r = json.loads(urllib.request.urlopen(urllib.request.Request(U, b, {"Content-Type": "application/json"}), timeout=60).read())
            if "result" in r: return r["result"]
        except Exception as e: pass
        time.sleep(3 * (i + 1))
    raise SystemExit("rpc failed")
allr, before = [], None
while True:
    p = {"limit": 1000}
    if before: p["before"] = before
    r = rpc("getSignaturesForAddress", [W, p])
    if not r: break
    allr += r; before = r[-1]["signature"]
    print(len(allr), r[-1].get("blockTime"), flush=True)
    if (r[-1].get("blockTime") or 0) < until: break
    time.sleep(0.5)
allr = [x for x in allr if (x.get("blockTime") or 0) >= until]
json.dump(allr, open(out, "w")); print("kept", len(allr), "ok", sum(1 for x in allr if not x.get("err")))
