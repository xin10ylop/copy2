# Step 2a: each candidate's landed transactions since Nov 3 00:00 UTC (two weeks), into TXROOT/<first 8>/, the files
# named as fetch_more.py names them (SLOT_SIG20.json) so examples/scan.rs reads them. A busy wallet keeps only its
# newest MAXSIG signatures (default 6,000, the disk allowance: wallet 4 itself makes about 2,100 a day, so volume alone rules nothing out;
# the screen's hold rule is what keeps flippers out). RPC from the environment, never printed.
#   RPC_URL=... python3 -I fetch_cands.py CANDS.json TXROOT [MAXSIG]
import sys, json, os, time, datetime, urllib.request
from concurrent.futures import ThreadPoolExecutor
URL = os.environ["RPC_URL"]; CANDS, ROOT = sys.argv[1:3]; MAXSIG = int(sys.argv[3]) if len(sys.argv) > 3 else 6000
T0 = datetime.datetime(2026, 11, 3, tzinfo=datetime.timezone.utc).timestamp()
def call(m, p):
    for i in range(10):
        try:
            rq = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(rq, timeout=40))
            if "error" in r: raise RuntimeError("rpc error")
            return r["result"]
        except Exception: time.sleep(min(10, 1.5 * (i + 1)))
    raise RuntimeError(m)
for W in json.load(open(CANDS)):
    D = f"{ROOT}/{W[:8]}"; os.makedirs(D, exist_ok=True); SF = f"{D}/../{W[:8]}_sigs.json"
    if os.path.exists(SF): sigs = json.load(open(SF))
    else:
        sigs, before, over = [], None, False
        while True:
            p = {"limit": 1000}
            if before: p["before"] = before
            r = call("getSignaturesForAddress", [W, p])
            if not r: break
            sigs += [[s["signature"], s["slot"], s["blockTime"]] for s in r if not s["err"] and (s["blockTime"] or 0) >= T0]
            before = r[-1]["signature"]
            if (r[-1]["blockTime"] or 0) < T0: break
            if len(sigs) > MAXSIG: over = True; break
        json.dump(sigs, open(SF, "w"))
    sigs = sigs[:MAXSIG]                                      # newest first
    todo = [s for s in sigs if not os.path.exists(f"{D}/{s[1]}_{s[0][:20]}.json")]
    def get(s):
        t = call("getTransaction", [s[0], {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}])
        if t: json.dump(t, open(f"{D}/{s[1]}_{s[0][:20]}.json", "w"))
    t0 = time.time()
    with ThreadPoolExecutor(24) as ex: list(ex.map(get, todo))
    span = (max(s[2] for s in sigs) - min(s[2] for s in sigs)) / 86400 if sigs else 0
    print(f"{W[:8]}: {len(sigs)} landed signatures since Nov 3 ({len(sigs) / max(span, 1):.0f} a day), {len(todo)} fetched in {time.time() - t0:.0f} s", flush=True)
