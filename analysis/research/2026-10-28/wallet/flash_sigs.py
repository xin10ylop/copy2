# FLASHX8D program: page its recent signatures (5 pages of 1,000), rate per hour.
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/wallet")
from w4lib import *
P = "FLASHX8DrLbgeR8FcfNV1F5krxYcYMUdBkrP1EPBtxB9"
ai = tri.rpc("getAccountInfo", [P, {"encoding": "base64", "dataSlice": {"offset": 0, "length": 0}}], cache=False)
print("account", {k: v for k, v in ai["value"].items() if k != "data"})
s = []; before = None
for k in range(5):
    p = tri.sigs(P, before=before, limit=1000); s += p; before = p[-1]["signature"]
    print("page", k, len(p), ts(p[0]["blockTime"]), "->", ts(p[-1]["blockTime"]), flush=True)
print("total", len(s), "span s", s[0]["blockTime"] - s[-1]["blockTime"], "failed", sum(1 for x in s if x.get("err")))
json.dump(s, open(OUT + "/flash_sigs.json", "w"))
