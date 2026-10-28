# Fresh study: the curve path after its buy for the trips that graduated before it sold (grad.py's list), up to the
# migration: every landed trade on the bonding curve (at most CAP transactions, oldest first, not sampled).
#   python3 -I grad_paths.py WALLET [CAP]   ->  <w8>_gpaths.json (a separate file: the main pipeline's paths are untouched)
import sys, json, os, time
from concurrent.futures import ThreadPoolExecutor
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/fresh3"
sys.path.insert(0, SP + "/month"); sys.path.insert(0, SP + "/rivalpnl"); sys.path.insert(0, "/home/user/rugsnipe/analysis")
import tri, common as C
from rugsnipe_analysis import events as E
W = sys.argv[1]; CAP = int(sys.argv[2]) if len(sys.argv) > 2 else 600
rows = [json.loads(l) for l in open(f"{SP}/h9long/{W[:8]}.jsonl")]
sig_of = {(t[0], r["s"], t[2]): r["sig"] for r in rows for t in r["tr"] if t[1] == W}
T = {x["m"]: x for x in json.load(open(f"{SP}/h9long/{W[:8]}_trips.json"))}
G = json.load(open(f"{SP}/h9long/{W[:8]}_grad.json"))
OUT = f"{SP}/h9long/{W[:8]}_gpaths.json"
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
def one(m):
    b = T[m]["tr"][0]; bs = sig_of.get((m, b["s"], 1))
    if not bs: return m, None
    bc = C.bonding_curve(m); sigs, before = [], None
    for _ in range(10):
        o = {"limit": 1000, "until": bs}
        if before: o["before"] = before
        page = tri.rpc("getSignaturesForAddress", [bc, o], cache=False) or []
        sigs += [p["signature"] for p in page if not p.get("err")]
        if len(page) < 1000: break
        before = page[-1]["signature"]
    old = sigs[::-1][:CAP]
    tr = []
    for sg in old:
        for k in range(2):
            try:
                tx = tri.rpc("getTransaction", [sg, TXO], cache=False)
                if tx: tr += trades(tx, m)
                break
            except Exception: pass
    tr.sort(key=lambda r: (r[0], r[1]))
    return m, dict(path=tr, n=len(sigs), cut=len(sigs) > CAP)
have = {}
print(time.strftime("%H:%M:%S"), len(G), "trips", flush=True)
with ThreadPoolExecutor(6) as ex:
    for m, v in ex.map(one, G):
        have[m] = v; print(time.strftime("%H:%M:%S"), m[:8], v and (len(v["path"]), v["n"], v["cut"]), flush=True)
json.dump(have, open(OUT, "w")); print("done", flush=True)
