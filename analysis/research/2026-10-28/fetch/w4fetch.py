import json, sys, time, urllib.request, datetime, concurrent.futures as cf
R = "https://api.mainnet-beta.solana.com"
W = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
OUT = sys.argv[1]
T0 = datetime.datetime(2026, 10, 27, 9, 0, tzinfo=datetime.timezone.utc).timestamp()
T1 = datetime.datetime(2026, 10, 27, 13, 0, tzinfo=datetime.timezone.utc).timestamp()
def call(m, p):
    for k in range(8):
        try:
            req = urllib.request.Request(R, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"content-type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=30))
            if "error" in r: raise RuntimeError(r["error"])
            return r["result"]
        except Exception as e:
            time.sleep(1.5 * (k + 1))
    raise RuntimeError(f"{m} failed")
sigs, before = [], None
while True:
    p = {"limit": 1000}
    if before: p["before"] = before
    r = call("getSignaturesForAddress", [W, p])
    if not r: break
    sigs += r; before = r[-1]["signature"]
    if (r[-1].get("blockTime") or 0) < T0: break
sel = [s for s in sigs if T0 <= (s.get("blockTime") or 0) <= T1]
print(len(sigs), "signatures fetched,", len(sel), "between 09:00 and 13:00 UTC,", sum(s["err"] is None for s in sel), "landed ok")
def get(s):
    t = call("getTransaction", [s["signature"], {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}])
    json.dump(t, open(f"{OUT}/{t['slot']}_{s['signature'][:12]}.json", "w"))
with cf.ThreadPoolExecutor(3) as ex:
    list(ex.map(get, [s for s in sel if s["err"] is None]))
print("saved")
