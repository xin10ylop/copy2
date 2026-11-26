# The routes again, checked in batches with retries (Nov 26): quote_route's one-by-one lookups read a refused request as
# "no pool" (FIONA read "none" with its canonical PumpSwap pool to wSOL live; two runs disagreed on 57 tokens). Input:
# quote_route PDAS_ONLY=1 lines "MINT ANCHOR POOL"; a pool exists when its account is owned by PumpSwap. Prints
# "MINT anchor|pool ANCHOR8|none" as quote_route does (USDC is a float since Nov 26: an anchor).
#   RPC_URL=... python3 -I u6_routes.py PDAS FLOATS_COMMA
import sys, os, json, time, urllib.request, collections
PDAS, FLOATS = sys.argv[1], set(sys.argv[2].split(",")) | {"So11111111111111111111111111111111111111112"}
PS = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"; URL = os.environ["RPC_URL"]
rows = [l.split() for l in open(PDAS) if l.strip()]
pools = sorted({r[2] for r in rows}); owner = {}
for i in range(0, len(pools), 100):
    part = pools[i:i + 100]
    for a in range(10):
        try:
            j = json.load(urllib.request.urlopen(urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": "getMultipleAccounts", "params": [part, {"encoding": "base64", "dataSlice": {"offset": 0, "length": 0}}]}).encode(), {"Content-Type": "application/json"}), timeout=60))
            vals = j["result"]["value"]; break
        except Exception: time.sleep(2 * (a + 1))
    else: raise SystemExit("RPC refused 10 times")
    for p, v in zip(part, vals): owner[p] = v and v.get("owner")
by = collections.OrderedDict()
for m, a, p in rows: by.setdefault(m, []).append((a, p))
for m, ps in by.items():
    if m in FLOATS: print(m, "anchor"); continue
    hit = next((a for a, p in ps if owner.get(p) == PS), None)
    print(m, f"pool {hit[:8]}" if hit else "none")
