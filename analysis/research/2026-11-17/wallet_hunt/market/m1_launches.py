# Market scan, step 1-3 (the owner, Nov 17: "search on the chain with filters ... in an efficient way"): every pump
# launch of the last HOURS hours, independent of wallet 4.
#   1. every signature on pump's mint authority (TSLvdd..., in every create) -> the launches;
#   2. each landed create's transaction -> its CreateEvent: the quote mint, the creator (other-token coins kept);
#   3. each other-token coin: its signatures, paged back to its create (at most 10 pages) -> how many landed
#      transactions in its first WIN seconds. A dead coin costs nothing more.
# Out: SP/market/launches.json {mint: {slot, t, quote, creator, sigs: [[sig, slot, t], ...] oldest first, in WIN}}.
# The RPC from RPC_URL, never printed.
#   RPC_URL=... python3 -I m1_launches.py SP [HOURS=48] [WIN=2400]
import sys, os, json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
SP = sys.argv[1]; HOURS = float(sys.argv[2]) if len(sys.argv) > 2 else 48; WIN = int(sys.argv[3]) if len(sys.argv) > 3 else 2400
URL = os.environ["RPC_URL"]; O = f"{SP}/market"; os.makedirs(O, exist_ok=True)
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M, lib
MINT_AUTH = "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM"; WSOL = "So11111111111111111111111111111111111111112"
SOLQ = {WSOL, "11111111111111111111111111111111", None, "?"}   # a SOL curve's event carries the zero key as its quote
def call(m, p):
    for i in range(8):
        try:
            rq = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(rq, timeout=60))
            if "error" in r: raise RuntimeError("rpc error")
            return r["result"]
        except Exception: time.sleep(1.5 * (i + 1))
    return None
t0 = time.time()
f1 = f"{O}/creates_sigs.json"
if os.path.exists(f1): S = json.load(open(f1))
else:
    S, before = [], None
    while True:
        p = {"limit": 1000}
        if before: p["before"] = before
        r = call("getSignaturesForAddress", [MINT_AUTH, p])
        if not r: break
        S += [[x["signature"], x["slot"], x["blockTime"]] for x in r if not x["err"] and x.get("blockTime")]
        before = r[-1]["signature"]
        if S and S[0][2] - r[-1]["blockTime"] > HOURS * 3600: break
    S = [s for s in S if S[0][2] - s[2] <= HOURS * 3600]; json.dump(S, open(f1, "w"))
print(f"step 1: {len(S)} landed creates in {HOURS} h ({time.time() - t0:.0f} s)", flush=True)
CRE = M.E.DISC_CREATE if hasattr(M.E, "DISC_CREATE") else None
def create_of(s):
    tx = call("getTransaction", [s[0], M.TXO])
    if not tx: return None
    ks = tx["transaction"]["message"]["accountKeys"] + (tx["meta"].get("loadedAddresses") or {}).get("writable", []) + (tx["meta"].get("loadedAddresses") or {}).get("readonly", [])
    mints = {b["mint"] for b in (tx["meta"].get("postTokenBalances") or [])}
    trades = []
    for g in tx["meta"].get("innerInstructions") or []:
        for ix in g["instructions"]:
            if ks[ix["programIdIndex"]] != lib.PUMP: continue
            raw = lib.b58d(ix.get("data", ""))
            if raw[:8] == M.E.EVENT_IX_TAG and raw[8:16] == M.E.DISC_TRADE:
                try: trades.append(M.decode_trade(raw[16:]))
                except Exception: pass
    # the coin: a mint ending in its account list that the create made (pump mints are new: no pre balance); the quote
    # mint from its first trade event, else the one other mint in the transaction
    new = [b["mint"] for b in (tx["meta"].get("postTokenBalances") or []) if b["mint"] not in {x["mint"] for x in (tx["meta"].get("preTokenBalances") or [])}]
    coin = next((m for m in new if m.endswith("pump")), new[0] if new else None)
    q = next((e.get("quote_mint") for e in trades if e["mint"] == coin and e.get("quote_mint")), None)
    if q is None:
        others = [m for m in mints if m != coin]
        q = others[0] if len(others) == 1 else (WSOL if not others else "?")
    return dict(mint=coin, slot=s[1], t=s[2], quote=q, creator=ks[0]) if coin else None
f2 = f"{O}/creates.json"
C = json.load(open(f2)) if os.path.exists(f2) else {}
todo = [s for s in S if s[0] not in C]
with ThreadPoolExecutor(32) as ex:
    for s, r in zip(todo, ex.map(create_of, todo)): C[s[0]] = r
json.dump(C, open(f2, "w"))
other = {r["mint"]: r for r in C.values() if r and r["quote"] not in SOLQ}
import collections
print(f"step 2: {sum(1 for r in C.values() if r)} creates read, {len(other)} priced in another token ({time.time() - t0:.0f} s);"
      f" quotes {collections.Counter(r['quote'][:8] for r in other.values()).most_common(8)}", flush=True)
f3 = f"{O}/launches.json"
L = json.load(open(f3)) if os.path.exists(f3) else {}
def life(r):
    out, before = [], None
    for _ in range(10):
        p = {"limit": 1000}
        if before: p["before"] = before
        page = call("getSignaturesForAddress", [r["mint"], p])
        if not page: break
        out += page; before = page[-1]["signature"]
        if page[-1]["slot"] <= r["slot"] or len(page) < 1000: break
    if out and out[-1]["slot"] > r["slot"]: return None          # more than 10 pages: a mega coin, left out
    inwin = [[x["signature"], x["slot"], x["blockTime"]] for x in reversed(out) if not x["err"] and x.get("blockTime") and x["blockTime"] - r["t"] <= WIN]
    return dict(r, sigs=inwin)
todo = [r for m, r in other.items() if m not in L]
with ThreadPoolExecutor(32) as ex:
    for r, x in zip(todo, ex.map(life, todo)): L[r["mint"]] = x
json.dump(L, open(f3, "w"))
n = [len(x["sigs"]) for x in L.values() if x]
print(f"step 3: {len(n)} other-token coins listed ({time.time() - t0:.0f} s); landed transactions in their first {WIN} s:"
      f" {sum(n)} in all; coins with 30+ {sum(1 for k in n if k >= 30)} ({sum(k for k in n if k >= 30)} transactions), 100+ {sum(1 for k in n if k >= 100)}, 1000+ {sum(1 for k in n if k >= 1000)};"
      f" mega coins left out {sum(1 for x in L.values() if x is None)}", flush=True)
