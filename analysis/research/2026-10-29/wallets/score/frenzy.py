# Mark 8 for a wallet whose full paths were fetched without n01 (wallet 4's, fresh3): the landed transactions on the
# coin's bonding curve after its buy in its slot and the next, from getSignaturesForAddress(curve, until = its buy), paged
# back from its sale (the pages full_paths.py reads). Trips of coins priced in another token, first buy MIN+ SOL.
#   SP=<its data> python3 -I frenzy.py WALLET [MIN=1.45]   ->  score SP/h9long/<w8>_n01.json (never written into SP)
import sys, os, json, statistics as st
from concurrent.futures import ThreadPoolExecutor
SP0 = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
SP = os.environ.get("SP", "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/score")
OUTSP = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/score"
sys.path.insert(0, SP0 + "/month"); sys.path.insert(0, SP0 + "/rivalpnl")
import tri, common as C
W = sys.argv[1]; MIN = float(sys.argv[2]) if len(sys.argv) > 2 else 1.45
sig_of = {}
for l in open(f"{SP}/h9long/{W[:8]}.jsonl"):
    r = json.loads(l)
    for t in r["tr"]:
        if t[1] == W: sig_of[(t[0], r["s"], t[2])] = r["sig"]
T = {x["m"]: x for x in json.load(open(f"{SP}/h9long/{W[:8]}_trips.json"))}
FP = json.load(open(f"{SP}/h9long/{W[:8]}_fpaths.json"))
pick = [T[m] for m, v in FP.items() if v and T[m]["kind"] == "pump, other quote" and len(T[m]["tr"]) == 2 and (T[m]["tr"][0]["v"] or 0) >= MIN]
OUT = f"{OUTSP}/h9long/{W[:8]}_n01.json"
have = json.load(open(OUT)) if os.path.exists(OUT) else {}
def one(x):
    m = x["m"]; b, s = x["tr"]; bs, ss = sig_of.get((m, b["s"], 1)), sig_of.get((m, s["s"], 0))
    if not bs or not ss: return m, None
    bc = C.bonding_curve(m); slots, before = [], ss
    for _ in range(10):
        page = tri.rpc("getSignaturesForAddress", [bc, {"limit": 1000, "before": before, "until": bs}], cache=False) or []
        slots += [p["slot"] for p in page if not p.get("err")]
        if len(page) < 1000: return m, sum(1 for z in slots if z <= b["s"] + 1)
        before = page[-1]["signature"]
    return m, None
with ThreadPoolExecutor(8) as ex:
    for m, v in ex.map(one, [x for x in pick if x["m"] not in have]): have[m] = v
json.dump(have, open(OUT, "w"))
v = [have[x["m"]] for x in pick if have.get(x["m"]) is not None]
print(f"{W[:8]}: {len(v)} of {len(pick)} trips; landed curve transactions after its buy in its slot and the next: median {st.median(v)}, "
      f"p25 {sorted(v)[len(v) // 4]}, p75 {sorted(v)[3 * len(v) // 4]}, mean {st.mean(v):.2f}")
