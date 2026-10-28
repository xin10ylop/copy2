# Every signature of a wallet back to T0 (landed and failed), newest first -> SP/h9long/<w8>_sigs.json
# (copy of ../../../2026-10-27/h9long/sigs.py: SP from the environment; MAXN stops paging after that many signatures and
# says so, for wallets far busier than wallet 4)       python3 -I sigs.py WALLET T0 [MAXN]
import sys, os, json, time
SP0 = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"      # helpers: month/tri.py
SP = os.environ.get("SP", "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/score")
sys.path.insert(0, SP0 + "/month")
import tri
W = sys.argv[1]; T0 = int(sys.argv[2]); MAXN = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 9
out, before = [], None
while True:
    o = {"limit": 1000}
    if before: o["before"] = before
    page = tri.rpc("getSignaturesForAddress", [W, o], cache=False) or []
    out += [[x["signature"], x["slot"], x.get("blockTime") or 0, x.get("err") is not None] for x in page]
    if not page: break
    print(time.strftime("%H:%M:%S"), len(out), page[-1].get("blockTime"), flush=True)
    if len(page) < 1000 or (page[-1].get("blockTime") or 0) < T0: break
    if len(out) >= MAXN: print("stopped at MAXN", MAXN, "oldest", page[-1].get("blockTime"), flush=True); break
    before = page[-1]["signature"]
out = [x for x in out if x[2] >= T0]
os.makedirs(f"{SP}/h9long", exist_ok=True)
json.dump(out, open(f"{SP}/h9long/{W[:8]}_sigs.json", "w"))
print("total", len(out), "landed", sum(1 for x in out if not x[3]), "oldest", min(x[2] for x in out) if out else None)
