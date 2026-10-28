# Every landed curve trade from its buy to its sell for its trips with a first buy of at least MIN_SOL (SOL value),
# both quotes: the whole price path, for exits of our own (fixed holds, trailing stops, take-profit ladders).
#   python3 -I full_paths.py WALLET MIN_SOL   ->  <w8>_fpaths.json  (resumable)
# score: MULTI=1 adds its one-buy several-sale coins; KINDS="pump, other quote" limits the trips to one kind, ROUTES=ABC to the routable ones (route_q.py); each trip also keeps n01, the number of landed curve
# transactions after its buy in its slot and the next (from the signature pages, so never sampled).
import sys, json, os, time
from concurrent.futures import ThreadPoolExecutor
SP0 = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"      # helpers: month/tri.py, rivalpnl
SP = __import__("os").environ.get("SP", "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/score")  # score: SP from the environment
sys.path.insert(0, SP0 + "/month"); sys.path.insert(0, SP0 + "/rivalpnl"); sys.path.insert(0, "/home/user/rugsnipe/analysis")
import tri, common as C
from rugsnipe_analysis import events as E
W = sys.argv[1]; MIN = float(sys.argv[2]); CAP = int(sys.argv[3]) if len(sys.argv) > 3 else 40
rows = [json.loads(l) for l in open(f"{SP}/h9long/{W[:8]}.jsonl")]
sig_of = {(t[0], r["s"], t[2]): r["sig"] for r in rows for t in r["tr"] if t[1] == W}
T = json.load(open(f"{SP}/h9long/{W[:8]}_trips.json"))
# score: MULTI=1 also takes coins it bought once and sold in several parts (the path runs to its LAST sale)
def onebuy(x): return x["tr"][0]["buy"] and not x["tr"][-1]["buy"] and sum(t["buy"] for t in x["tr"]) == 1 and len(x["tr"]) >= 2
pick = [x for x in T if not x["open"] and (len(x["tr"]) == 2 or (os.environ.get("MULTI") == "1" and onebuy(x))) and x["tr"][0]["buy"] and not x["tr"][-1]["buy"]
        and (x["tr"][0]["v"] or 0) >= MIN and x["kind"] in os.environ.get("KINDS", "pump, other quote|pump, SOL quote").split("|")]   # score: KINDS
if os.environ.get("ROUTES"):                       # score: only the buys route_q.py puts in these classes (e.g. ABC)
    os.environ["W"] = W; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from route_q import cls
    pick = [x for x in pick if cls(x) in os.environ["ROUTES"]]
OUT = f"{SP}/h9long/{W[:8]}_fpaths.json"
have = json.load(open(OUT)) if os.path.exists(OUT) else {}
TXO = {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}
def trades(tx, m):
    out = []
    ks = tx["transaction"]["message"]["accountKeys"] + (tx["meta"].get("loadedAddresses") or {}).get("writable", []) + (tx["meta"].get("loadedAddresses") or {}).get("readonly", [])
    for g in tx["meta"].get("innerInstructions") or []:
        for ix in g["instructions"]:
            if ks[ix["programIdIndex"]] != C.PUMP: continue
            raw = C.b58d(ix.get("data", ""))
            if raw[:8] == E.EVENT_IX_TAG and raw[8:16] == E.DISC_TRADE:
                try: e = E.decode_trade(raw[8:])
                except Exception: continue
                if e.mint == m: out.append([tx["slot"], tx.get("transactionIndex") or 0, e.user[:8], int(e.is_buy), e.token_amount, e.virtual_token_reserves, tx.get("blockTime")])
    return out
def one(x):
    m = x["m"]
    if m in have: return m, have[m]
    b, s = x["tr"][0], x["tr"][-1]                  # score: its last sale (= its only one unless MULTI)
    bs, ss = sig_of.get((m, b["s"], 1)), sig_of.get((m, s["s"], 0))
    if not bs or not ss: return m, None
    bc = C.bonding_curve(m); sigs, before = [], ss; slots = []
    for _ in range(10):
        page = tri.rpc("getSignaturesForAddress", [bc, {"limit": 1000, "before": before, "until": bs}], cache=False) or []
        sigs += [p["signature"] for p in page if not p.get("err")]
        slots += [p["slot"] for p in page if not p.get("err")]          # score: the frenzy count below
        if len(page) < 1000: break
        before = page[-1]["signature"]
    n01 = sum(1 for z in slots if z <= b["s"] + 1)     # score: landed curve transactions after its buy in its slot and the next
    if len(sigs) > 3000: return m, dict(skip=len(sigs), n01=n01)
    # sigs are newest first: keep the first 8 after its buy, the last 4 before its sell, and an even sample between
    # (at most CAP transactions a trip); the path's states between samples are not seen
    old = sigs[::-1]
    if len(old) > CAP:
        mid = old[8:-4]; k = max(1, len(mid) // (CAP - 12))
        old = old[:8] + mid[::k] + old[-4:]
    tr = []
    for sg in old:
        for k in range(2):
            try:
                tx = tri.rpc("getTransaction", [sg, TXO], cache=False)
                if tx: tr += trades(tx, m)
                break
            except Exception: pass
    tr.sort(key=lambda r: (r[0], r[1]))
    return m, dict(path=tr, n=len(sigs), sampled=len(sigs) > CAP, n01=n01)
n = 0
print(time.strftime("%H:%M:%S"), len(pick), "trips", flush=True)
with ThreadPoolExecutor(11) as ex:
    for m, v in ex.map(one, pick):
        have[m] = v; n += 1
        if n % 50 == 0: print(time.strftime("%H:%M:%S"), n, "/", len(pick), flush=True); json.dump(have, open(OUT, "w"))
json.dump(have, open(OUT, "w")); print("done", n, flush=True)
