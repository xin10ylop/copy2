# The create slot of every coin a wallet first bought on a pump curve priced in another token for MIN+ SOL (trips.py's
# first trade a buy, its SOL value): the oldest signature on the coin's bonding curve before its buy (pages back from its
# buy; ../../../2026-10-28/more/age.py does the same for wallet 4: 322 of 323 big buys under 2 s). A curve with more
# than 3,000 signatures before its buy is marked old (no slot).
#   python3 -I create.py WALLET [MIN_SOL=0.5]   ->  SP/h9long/<w8>_create.json {coin: [create slot, create time, trades before, old]}
import sys, os, json, time
from concurrent.futures import ThreadPoolExecutor
SP0 = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"      # helpers: month/tri.py, rivalpnl
SP = os.environ.get("SP", "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/score")
sys.path.insert(0, SP0 + "/month"); sys.path.insert(0, SP0 + "/rivalpnl")
import tri, common as C
W = sys.argv[1]; MIN = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
sig_of = {}
for l in open(f"{SP}/h9long/{W[:8]}.jsonl"):
    r = json.loads(l)
    for t in r["tr"]:
        if t[1] == W and t[2]: sig_of.setdefault((t[0], r["s"]), r["sig"])
T = json.load(open(f"{SP}/h9long/{W[:8]}_trips.json"))
pick = [x for x in T if x["kind"] == "pump, other quote" and x["tr"] and x["tr"][0]["buy"] and (x["tr"][0]["v"] or 0) >= MIN]
OUT = f"{SP}/h9long/{W[:8]}_create.json"
have = json.load(open(OUT)) if os.path.exists(OUT) else {}
def one(x):
    m = x["m"]; b = x["tr"][0]; before = sig_of.get((m, b["s"]))
    if not before: return m, None
    bc = C.bonding_curve(m); oldest = None; n = 0
    for _ in range(3):
        page = tri.rpc("getSignaturesForAddress", [bc, {"limit": 1000, "before": before}], cache=False) or []
        n += len(page)
        if page: oldest = page[-1]; before = page[-1]["signature"]
        if len(page) < 1000: return m, [oldest["slot"], oldest.get("blockTime"), n, False] if oldest else [b["s"], b["bt"], 0, False]
    return m, [None, None, n, True]
todo = [x for x in pick if x["m"] not in have]
print(time.strftime("%H:%M:%S"), len(pick), "coins,", len(todo), "to fetch", flush=True)
with ThreadPoolExecutor(12) as ex:
    for k, (m, v) in enumerate(ex.map(one, todo)):
        have[m] = v
        if k % 200 == 0: json.dump(have, open(OUT, "w")); print(time.strftime("%H:%M:%S"), k, "/", len(todo), flush=True)
json.dump(have, open(OUT, "w")); print("done", len(have), flush=True)
