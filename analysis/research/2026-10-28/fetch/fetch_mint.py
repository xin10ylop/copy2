# fetch_mint.py MINT FROM_UTC TO_UTC OUTDIR: a coin's transactions between two UTC times (YYYY-MM-DDTHH:MM:SS)
import json, sys, time, urllib.request, datetime, os, concurrent.futures as cf
R = "https://api.mainnet-beta.solana.com"
M, A, B, OUT = sys.argv[1:5]
ts = lambda s: datetime.datetime.fromisoformat(s).replace(tzinfo=datetime.timezone.utc).timestamp()
T0, T1 = ts(A), ts(B)
os.makedirs(OUT, exist_ok=True)
def call(m, p):
    for k in range(14):
        try:
            req = urllib.request.Request(R, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"content-type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=30))
            if "error" in r: raise RuntimeError(r["error"])
            return r["result"]
        except Exception:
            time.sleep(min(2.0 * (k + 1), 15))
    return None
sigs, before = [], None
while True:
    p = {"limit": 1000}
    if before: p["before"] = before
    r = call("getSignaturesForAddress", [M, p])
    if not r: break
    sigs += r; before = r[-1]["signature"]
    if (r[-1].get("blockTime") or 0) < T0: break
sel = [s for s in sigs if T0 <= (s.get("blockTime") or 0) <= T1 and s["err"] is None]
have = {f.split("_")[1][:12] for f in os.listdir(OUT)}
def get(s):
    if s["signature"][:12] in have: return
    t = call("getTransaction", [s["signature"], {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}])
    if t: json.dump(t, open(f"{OUT}/{t['slot']}_{s['signature'][:12]}.json", "w"))
with cf.ThreadPoolExecutor(2) as ex: list(ex.map(get, sel))
print(M[:8], len(sigs), "signatures read,", len(sel), "in the window, saved", len(os.listdir(OUT)))
