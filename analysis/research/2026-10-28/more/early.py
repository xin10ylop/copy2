# Its early sells in the paper run (Oct 27-28, 9 copies closed "its_sell"): what our own exits (TP 2.0 / stop 0.8 /
# 1790 s from its buy) would have made had the engine ignored its sell, against selling right behind it. Each coin's
# curve trades from its buy to 1,800 s after (Triton: the bonding curve's signatures, getTransaction, TradeEvent as
# full_paths.py decodes it), its buy and sell from H9kuqGKN.jsonl (re-fetched to Oct 28 14:54). Both ways priced by
# sim.one (grid.py's model q, its costs): "follow" ends the path at its sale; "ignore" runs the path to 1,800 s (its own
# 2.5x cannot fire: it has sold). The paper's own net (history, Beirut table) beside them.
#   python3 -I early.py   ->  SPX/early_paths.json (cached)
import sys, os, json, datetime
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim
SP = sim.SP; SPX = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/more"
sys.path.insert(0, SP + "/month"); sys.path.insert(0, SP + "/rivalpnl"); sys.path.insert(0, "/home/user/rugsnipe/analysis")
import tri, common as C
from rugsnipe_analysis import events as E
W = sim.W
PAPER = {"BPhav4G4JBCRHqViJSFsAQEvZwb2iDUxmXXa7Hw3pump": -0.2958, "ChonQdJ8HVNNuVVCgYwLKs7tXX3FAPYSZ92i8igGgUS8": -0.1756,
         "FUCKKmZZ3m1fW1eG1w24YNUZky4BucUNmWYoux5cpUmP": -0.2468, "HytpiyuR3sVXGB5UqoqrnThCPH2X1tWVm5neep3Dpump": +0.1038,
         "6DS5ErwHfSfqKL8UakJmkxfb1SU5DHndbUEHy8nqpump": -0.3031, "DJXThGNtYLYyx5wVkQE6GuL4nyGGTimcEeitka8apump": -0.0623,
         "9hhXcHT9r7vgqDoe17JrnL5Z5on1meoYXP5NYTeWpump": +0.1424, "3j9ex53kQkZFYR8dWvJfKm5CSHT7mf3GALCGZwFkpump": +0.1429,
         "9ENc9LwFXmtUiAVNyYp5LqZMrEuZ3FWLAnmz5fD4pump": -0.1874}
OUT = f"{SPX}/early_paths.json"
have = json.load(open(OUT)) if os.path.exists(OUT) else {}
TXO = {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}
def legs(m):
    ev = sorted((r["s"], r["i"] or 0, r["bt"], t[2], t[4], t[6], r["sig"]) for r in sim.ROWS for t in r["tr"] if t[0] == m and t[1] == W)
    return ev[0], ev[1]
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
def fetch(m):
    if m in have: return m, have[m]
    b, s = legs(m); bc = C.bonding_curve(m); sigs, before = [], None
    for _ in range(40):
        o = {"limit": 1000, "until": b[6]}
        if before: o["before"] = before
        page = tri.rpc("getSignaturesForAddress", [bc, o], cache=False) or []
        sigs += [(p["signature"], p.get("blockTime") or 0) for p in page if not p.get("err")]
        if len(page) < 1000 or (page[-1].get("blockTime") or 0) < b[2]: break
        before = page[-1]["signature"]
    keep = [sg for sg, t in sigs if t <= b[2] + 1830][::-1]
    with ThreadPoolExecutor(8) as ex:
        txs = list(ex.map(lambda sg: tri.rpc("getTransaction", [sg, TXO], cache=False), keep))
    tr = []
    for tx in txs:
        if tx: tr += trades(tx, m)
    tr.sort(key=lambda r: (r[0], r[1]))
    return m, dict(path=tr, n=len(keep))
for m in PAPER:
    m, v = fetch(m); have[m] = v
json.dump(have, open(OUT, "w"))
f = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d %H:%M")
print(f"{'coin':9s} {'its buy UTC':12s} {'sold after':>10s} {'trades':>6s}  {'paper':>7s}  {'follow':>7s} {'ignore':>7s}  ignore exit        peak after its sell")
tot = {"paper": 0, "follow": 0, "ignore": 0}
for m, net in PAPER.items():
    b, s = legs(m); path = have[m]["path"]
    its = 1.5
    bd = dict(s=b[0], i=b[1], bt=b[2], tok=b[4], vt=b[5], v=its)
    sd = dict(s=s[0], i=s[1], bt=s[2], tok=s[4], vt=s[5])
    pf = [r for r in path if (r[0], r[1]) <= (s[0], s[1])]
    x = {"m": m, "kind": "pump, other quote", "tr": [bd, sd]}
    r_f = sim.one(x, pf)
    k_f = sim.KIND.get(m)
    last = path[-1]
    x2 = {"m": m, "kind": "pump, other quote", "tr": [bd, dict(s=last[0] + 1, i=0, bt=b[2] + 1800, tok=0, vt=last[5])]}
    r_i = sim.one(x2, path, lift=False)
    k_i = sim.KIND.get(m)
    after = [(b[5] / r[5]) ** 2 for r in path if (r[0], r[1]) > (s[0], s[1]) and r[6] and r[6] - b[2] <= 1790]
    tot["paper"] += net; tot["follow"] += r_f[2]; tot["ignore"] += r_i[2]
    print(f"{m[:8]:9s} {f(b[2]):12s} {s[2] - b[2]:9d}s {len(path):6d}  {net:+7.4f}  {r_f[2]:+7.3f} {r_i[2]:+7.3f}  {k_i:18s} {max(after) if after else 0:.2f}x")
print(f"{'total':9s} {'':12s} {'':10s} {'':6s}  {tot['paper']:+7.4f}  {tot['follow']:+7.3f} {tot['ignore']:+7.3f}   (ignore - follow {tot['ignore'] - tot['follow']:+.3f})")
