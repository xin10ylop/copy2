# Who receives the cash-out wallet's money (from w4_watch.py §6): for each address, its type (wallet or token
# account, and then its owner), balance, recent transactions, and whether it trades pump coins or looks like an
# exchange (many unrelated senders).
#   python3 -I dest_check.py PREFIX_OR_ADDRESS ...   (prefixes are resolved from EXzuWDVb's recent transactions)
import sys, json, time, urllib.request, datetime, collections
R = open("/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/month/.triton_url").read().strip()
EX = "EXzuWDVba3BQL14UYxSbvz1pZwZNYHXbyQwMBQutPFey"; PUMP = {"6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P", "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"}
def call(m, p):
    for k in range(5):
        try:
            req = urllib.request.Request(R, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"content-type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=60))
            if "error" in r: raise RuntimeError("rpc")
            return r["result"]
        except Exception: time.sleep(2 * (k + 1))
f = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d %H:%M")
full = set()
for x in call("getSignaturesForAddress", [EX, {"limit": 100}]) or []:
    tx = call("getTransaction", [x["signature"], {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}])
    if tx: full.update(k["pubkey"] for k in tx["transaction"]["message"]["accountKeys"])
for a in sys.argv[1:]:
    addr = next((k for k in full if k.startswith(a)), a)
    info = call("getAccountInfo", [addr, {"encoding": "jsonParsed"}])["value"]
    if info and isinstance(info["data"], dict) and info["data"].get("parsed", {}).get("type") == "account":
        owner = info["data"]["parsed"]["info"]["owner"]; print(f"{addr[:8]}: a token account of {owner}"); addr = owner
    sigs = call("getSignaturesForAddress", [addr, {"limit": 1000}]) or []
    pump = senders = 0; snd = collections.Counter()
    for s in sigs[:30]:
        tx = call("getTransaction", [s["signature"], {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}])
        if not tx: continue
        ks = [k["pubkey"] for k in tx["transaction"]["message"]["accountKeys"]]; pump += bool(set(ks) & PUMP); snd[ks[0]] += 1
    bal = (call("getBalance", [addr]) or {"value": 0})["value"] / 1e9
    print(f"{addr}: {bal:.2f} SOL; {len(sigs)}{'+' if len(sigs) == 1000 else ''} transactions" + (f", newest {f(sigs[0]['blockTime'])}, oldest of these {f(sigs[-1]['blockTime'])}" if sigs else "")
          + f"; of its last 30: {pump} touch pump, {len(snd)} different fee payers (top {[(k[:8], n) for k, n in snd.most_common(3)]})")
