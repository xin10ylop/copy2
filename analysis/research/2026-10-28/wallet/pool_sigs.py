# The privacy pool account 4AV2Qzp3: page its signatures back to Oct 17 12:00 UTC; save.
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
P = sys.argv[1]; STOP = int(sys.argv[2]); s = []; before = None
while True:
    p = tri.sigs(P, before=before, limit=1000); s += p
    print(len(s), ts(p[-1]["blockTime"]), flush=True)
    if len(p) < 1000 or p[-1]["blockTime"] < STOP or len(s) > 60000: break
    before = p[-1]["signature"]
json.dump([[x["signature"], x["slot"], x["blockTime"], bool(x.get("err"))] for x in s], open(OUT + f"/sigs_{P[:8]}.json", "w"))
