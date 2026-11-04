# The side wallets' own trades: each coin, time, SOL, and whether Rafinhaaaaaa traded the same coin within 10 min.
#   python3 -I side.py RAF_ROWS_JSON ADDR...
import json, sys, time, urllib.request, datetime
sys.path.insert(0, "/home/user/copy2/rafinhaaaaaa/analysis/final")
import g1lib as G
U = "https://api.mainnet-beta.solana.com"; last = [0.0]
def rpc(m, p):
    for i in range(8):
        dt = time.time() - last[0]
        if dt < 0.5: time.sleep(0.5 - dt)
        last[0] = time.time()
        try:
            b = json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode()
            r = json.loads(urllib.request.urlopen(urllib.request.Request(U, b, {"Content-Type": "application/json"}), timeout=60).read())
            if "result" in r: return r["result"]
        except Exception: pass
        time.sleep(3 * (i + 1))
raf = json.load(open(sys.argv[1])); f = lambda t: datetime.datetime.fromtimestamp(t, datetime.UTC).strftime("%m-%d %H:%M:%S")
for a in sys.argv[2:]:
    print("==", a)
    for s in reversed(rpc("getSignaturesForAddress", [a, {"limit": 40}]) or []):
        if s.get("err"): continue
        tx = rpc("getTransaction", [s["signature"], {"encoding": "json", "maxSupportedTransactionVersion": 1}])
        if not tx: continue
        k = G.keys_of(tx); m = tx["meta"]; i = k.index(a)
        dsol = (m["postBalances"][i] - m["preBalances"][i]) / 1e9
        coins = {}
        for side, sg in (("preTokenBalances", -1), ("postTokenBalances", 1)):
            for b in m.get(side) or []:
                if b.get("owner") == a and b["mint"] != G.WSOL: coins[b["mint"]] = coins.get(b["mint"], 0) + sg * float(b["uiTokenAmount"]["uiAmount"] or 0)
        coins = {c: v for c, v in coins.items() if abs(v) > 0}
        same = [r for c in coins for r in raf if r["mint"] == c and abs(r["t"] - tx["blockTime"]) < 600]
        note = (f"  its main wallet: {same[0]['side']} {abs(same[0]['sol']):.2f} SOL {same[0]['t'] - tx['blockTime']:+d} s" if same else "")
        print(f"  {f(tx['blockTime'])} {'it signed' if k[0] == a else 'other    '} {dsol:+8.3f} SOL {' '.join(c[:8] + ('+' if v > 0 else '-') for c, v in coins.items())} {G.venue(tx)}{note}")
