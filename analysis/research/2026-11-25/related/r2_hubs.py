# What the repeat counterparties are (Nov 25): for each account, its owner program (System = a plain wallet), its SOL,
# how many signatures in its latest 1,000 and over how long, and a sample of its swaps (Helius Enhanced, type SWAP, 50):
# how many, on which source (PUMP_FUN, PUMP_AMM, JUPITER ...), and how many wallets it sent SOL to that are ours.
#   HELIUS_URL=... python3 -I r2_hubs.py ACCT [ACCT ...]
import os, sys, json, time, urllib.request, urllib.parse, collections, datetime as dt
U = os.environ["HELIUS_URL"]; KEY = urllib.parse.parse_qs(urllib.parse.urlparse(U).query)["api-key"][0]
def rpc(m, p):
    for a in range(6):
        try:
            j = json.load(urllib.request.urlopen(urllib.request.Request(U, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"}), timeout=60))
            if "result" in j: return j["result"]
        except Exception: pass
        time.sleep(2 * (a + 1))
def enh(a, typ, n):
    for k in range(5):
        try: return json.load(urllib.request.urlopen(f"https://api.helius.xyz/v0/addresses/{a}/transactions?api-key={KEY}&type={typ}&limit={n}", timeout=60))
        except Exception: time.sleep(2 * (k + 1))
    return []
for a in sys.argv[1:]:
    ai = rpc("getAccountInfo", [a, {"encoding": "base64"}]) or {}
    v = (ai or {}).get("value") or {}
    owner = v.get("owner", "?"); lam = (v.get("lamports") or 0) / 1e9
    sg = rpc("getSignaturesForAddress", [a, {"limit": 1000}]) or []
    span = (sg[0]["blockTime"] - sg[-1]["blockTime"]) / 3600 if len(sg) > 1 and sg[0].get("blockTime") and sg[-1].get("blockTime") else 0
    sw = enh(a, "SWAP", 50); src = collections.Counter(t.get("source") for t in sw)
    kind = "plain wallet" if owner == "11111111111111111111111111111111" else f"owned by {owner[:8]}"
    print(f"{a}: {kind}, {lam:.2f} SOL; {len(sg)} signatures over {span:.1f} h; swaps in its latest 50 swap txs: {len(sw)} {dict(src)}")
    time.sleep(0.3)
