# The coin's age at its buy: the oldest signature on the coin's bonding curve (its create) against its buy, for its
# big buys in grid.py's set and the band (1.45+ SOL, other quotes, a path). getSignaturesForAddress pages back from
# its buy (Triton).   python3 -I age.py   ->  SPX/age.json (resumable)
import sys, os, json
from concurrent.futures import ThreadPoolExecutor
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
SPX = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/more"
sys.path.insert(0, SP + "/month"); sys.path.insert(0, SP + "/rivalpnl")
import tri, common as C
Qs = [q for q in json.load(open(f"{SPX}/quotes.json")) if q["path"]]
OUT = f"{SPX}/age.json"
have = json.load(open(OUT)) if os.path.exists(OUT) else {}
def one(q):
    bc = C.bonding_curve(q["m"]); before = q["sig"]; oldest = None; n = 0
    for _ in range(30):
        page = tri.rpc("getSignaturesForAddress", [bc, {"limit": 1000, "before": before}], cache=False) or []
        n += len(page)
        if page: oldest = page[-1]; before = page[-1]["signature"]
        if len(page) < 1000: break
    return q["m"], dict(create_bt=oldest["blockTime"] if oldest else None, before_n=n, buy_bt=q["bt"])
todo = [q for q in Qs if q["m"] not in have]
with ThreadPoolExecutor(8) as ex:
    for k, (m, v) in enumerate(ex.map(one, todo)):
        have[m] = v
        if k % 100 == 0: json.dump(have, open(OUT, "w")); print(k, "/", len(todo), flush=True)
json.dump(have, open(OUT, "w")); print("done", len(have))
