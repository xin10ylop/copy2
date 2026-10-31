# Wallet 4's landed transactions from T0 to now, one RPC-json file each (the format of examples/scan.rs), through the
# Triton endpoint in SP/month/.triton_url (read, never printed).
#   python3 -I fetch_w4.py OUTDIR [T0_UTC "YYYY-MM-DD HH:MM"]
import json, sys, os, time, datetime, urllib.request, concurrent.futures as cf
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
R = open(f"{SP}/month/.triton_url").read().strip()
W = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
OUT = sys.argv[1]
T0 = datetime.datetime.strptime(sys.argv[2] if len(sys.argv) > 2 else "2026-10-28 18:30", "%Y-%m-%d %H:%M").replace(tzinfo=datetime.timezone.utc).timestamp()
def call(m, p):
    for k in range(8):
        try:
            req = urllib.request.Request(R, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"content-type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=60))
            if "error" in r: raise RuntimeError(str(r["error"])[:120])
            return r["result"]
        except Exception as e:
            time.sleep(1.5 * (k + 1))
    return None
sigs, before = [], None
while True:
    p = {"limit": 1000}
    if before: p["before"] = before
    r = call("getSignaturesForAddress", [W, p])
    if not r: break
    sigs += r; before = r[-1]["signature"]
    if (r[-1].get("blockTime") or 0) < T0: break
sel = [s for s in sigs if (s.get("blockTime") or 0) >= T0 and s["err"] is None]
f = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d %H:%M")
print(f"{len(sigs)} signatures read, {len(sel)} landed since {f(T0)} UTC; newest {f(sigs[0]['blockTime'])} UTC", flush=True)
have = {x.split("_")[1][:12] for x in os.listdir(OUT)}
def get(s):
    if s["signature"][:12] in have: return 0
    t = call("getTransaction", [s["signature"], {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}])
    if t is None: return 1
    json.dump(t, open(f"{OUT}/{t['slot']}_{s['signature'][:12]}.json", "w")); return 0
with cf.ThreadPoolExecutor(12) as ex:
    bad = sum(ex.map(get, sel))
print("saved; failed", bad)
