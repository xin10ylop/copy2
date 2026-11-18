# The predecessor's two cross-chain swaps (Oct 17 ~21:48 UTC): the transactions, their programs and the raw data.
import json, requests, datetime as dt
U = "https://api.mainnet-beta.solana.com"; S = requests.Session()
def call(m, p): return S.post(U, json={"jsonrpc": "2.0", "id": 1, "method": m, "params": p}, timeout=60).json().get("result")
W = "HxcdEi6CWzQtPCmM8E2maEZ3oYVGZxESqCWU1iPzmhVW"
pg = call("getSignaturesForAddress", [W, {"limit": 1000}])
hits = [s for s in pg if s["signature"][:8] in ("4MunAtQA", "wh2vUqbs")]
print("newest page", dt.datetime.fromtimestamp(pg[-1]["blockTime"], dt.UTC), "->", dt.datetime.fromtimestamp(pg[0]["blockTime"], dt.UTC), "hits", len(hits))
for s in hits:
    tx = call("getTransaction", [s["signature"], {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 1}])
    print("\n==", s["signature"], dt.datetime.fromtimestamp(tx["blockTime"], dt.UTC))
    for ix in tx["transaction"]["message"]["instructions"]:
        print("  ix", ix.get("programId"), ix.get("parsed", {}).get("type") if isinstance(ix.get("parsed"), dict) else "", "accounts", [a[:8] for a in ix.get("accounts", [])][:14], "data", (ix.get("data") or "")[:300])
    for l in tx["meta"]["logMessages"][:40]: print("  log", l[:220])
    json.dump(tx, open(f"xchain_{s['signature'][:8]}.json", "w"))
