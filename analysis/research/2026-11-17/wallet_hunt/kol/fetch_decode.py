# The leaderboard wallets worth a closer look, by a rule fixed before looking at their trades: seen in the last 6 hours;
# at least 100 landed of its newest 1,000 signatures (a wallet whose transactions mostly fail is racing for a slot);
# 2-150 closed trades a day on the leaderboard's own count (30 days, else 7 days); in profit there. Each one's newest
# MAXSIG landed transactions are fetched into SP/kol/tx/<w8>/, then every pump curve trade of its own is decoded
# (cmodel.decode_trade: SOL-priced and other-token curves alike) -> SP/kol/trades.json. RPC from RPC_URL, not printed.
#   RPC_URL=... python3 -I kol/fetch_decode.py SP [MAXSIG]
import sys, os, json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
SP = sys.argv[1]; MAXSIG = int(sys.argv[2]) if len(sys.argv) > 2 else 2500; URL = os.environ["RPC_URL"]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M, lib
A = json.load(open(f"{SP}/kol_activity.json")); now = time.time(); pick = []
for w, a in A.items():
    p = {int(k): v for k, v in a["p"].items()}; tf = 30 if 30 in p else 7
    a_day = (p[tf][1] + p[tf][2]) / tf
    if now - a["last"] < 6 * 3600 and a["landed"] >= 100 and 2 <= a_day <= 150 and p[tf][0] > 0: pick.append(w)
print(f"{len(pick)} of {len(A)} wallets picked: {' '.join(w[:8] for w in pick)}", flush=True)
def call(m, p):
    for i in range(8):
        try:
            rq = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(rq, timeout=40))
            if "error" in r: raise RuntimeError("rpc error")
            return r["result"]
        except Exception: time.sleep(1.5 * (i + 1))
    return None
out = {}
for w in pick:
    D = f"{SP}/kol/tx/{w[:8]}"; os.makedirs(D, exist_ok=True); sigs, before = [], None
    while len(sigs) < MAXSIG:
        p = {"limit": 1000}
        if before: p["before"] = before
        r = call("getSignaturesForAddress", [w, p])
        if not r: break
        sigs += [s for s in r if not s["err"]]; before = r[-1]["signature"]
        if len(r) < 1000: break
    sigs = sigs[:MAXSIG]
    def get(s):
        f = f"{D}/{s['slot']}_{s['signature'][:20]}.json"
        if os.path.exists(f): return json.load(open(f))
        t = call("getTransaction", [s["signature"], M.TXO])
        if t: json.dump(t, open(f, "w"))
        return t
    with ThreadPoolExecutor(24) as ex: txs = [t for t in ex.map(get, sigs) if t]
    T = []
    for tx in txs:
        ks = tx["transaction"]["message"]["accountKeys"] + (tx["meta"].get("loadedAddresses") or {}).get("writable", []) + (tx["meta"].get("loadedAddresses") or {}).get("readonly", [])
        for g in tx["meta"].get("innerInstructions") or []:
            for ix in g["instructions"]:
                if ks[ix["programIdIndex"]] != lib.PUMP: continue
                raw = lib.b58d(ix.get("data", ""))
                if raw[:8] != M.E.EVENT_IX_TAG or raw[8:16] != M.E.DISC_TRADE: continue
                try: e = M.decode_trade(raw[16:])
                except Exception: continue
                if e["user"] != w: continue
                T.append(dict(slot=tx["slot"], t=tx["blockTime"], mint=e["mint"], buy=e["buy"], sol=e["sol"], q=e.get("q"), quote=e.get("quote_mint"), tok=e["tok"]))
    span = (sigs[0]["blockTime"] - sigs[-1]["blockTime"]) / 3600 if sigs else 0
    out[w] = dict(name=A[w]["name"], span_h=span, n_tx=len(txs), trades=sorted(T, key=lambda x: (x["slot"], x["t"])))
    print(f"{w[:8]} {A[w]['name'][:14]:14s}: {len(txs)} transactions over {span:.0f} h, {len(T)} pump curve trades of its own", flush=True)
    json.dump(out, open(f"{SP}/kol/trades.json", "w"))
