# Page wallet 4's signatures back from the oldest one in H9kuqGKN_sigs.json to its first transaction.
# Output: wallet/w4_oldsigs.jsonl, one page per line: [[sig, slot, bt, err], ...]. Resumable. Stops at 150,000.
import sys, json, os, time
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
sys.path.insert(0, SP + "/month"); import tri
W = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
OUT = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet/w4_oldsigs.jsonl"
base = json.load(open(SP + "/h9long/H9kuqGKN_sigs.json"))
before = base[-1][0]; n = 0
if os.path.exists(OUT):
    for l in open(OUT):
        p = json.loads(l); n += len(p)
        if p: before = p[-1][0]
print("start before", before[:12], "have", n, flush=True)
while n < 150000:
    r = tri.sigs(W, before=before, limit=1000)
    if not r: print("END: no more signatures", flush=True); break
    page = [[x["signature"], x["slot"], x.get("blockTime"), bool(x.get("err"))] for x in r]
    with open(OUT, "a") as f: f.write(json.dumps(page) + "\n")
    n += len(page); before = page[-1][0]
    print(time.strftime("%H:%M:%S"), n, "oldest bt", page[-1][2], time.strftime("%Y-%m-%d %H:%M", time.gmtime(page[-1][2] or 0)), flush=True)
    if len(r) < 1000: print("END: short page", flush=True); break
print("total", n)
