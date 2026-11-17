# Winners first, step 4: the screen's candidates on their own history. Candidates (fixed before looking): from step 3,
# 3+ hits from 3+ creators and an estimated lift of 1.5+, the top 40 by hits. For each: its signatures back to Nov 3
# 00:00 UTC (the newest MAXSIG kept), every transaction fetched once and only its own pump TradeEvents kept
# (SP/winners/hist/<wallet>.json; resumable). Each first buy on a coin: its size in SOL (other quotes at Jupiter's price,
# as step 3), the curve's progress before it (real reserves after + tokens bought), and the coin's outcome now (its curve
# complete or not, getMultipleAccounts). Scored as in step 3 against the base rate b(p) of step 3 (SP/winners/bp.json):
# copyable buys = 0.25+ SOL, under half the curve sold. Three periods: before Nov 15 01:07 UTC (out of sample: the screen
# never saw it), the screen's 48 h, and after Nov 17 01:07.
# The RPC from RPC_URL, never printed.
#   RPC_URL=... python3 -I w4_history.py SP [MAXSIG=12000] > out/w4_history.txt
import sys, os, json, time, math, base64, struct, collections, statistics as st, urllib.request
from concurrent.futures import ThreadPoolExecutor
from solders.pubkey import Pubkey
SP = sys.argv[1]; MAXSIG = int(sys.argv[2]) if len(sys.argv) > 2 else 12000; W = f"{SP}/winners"; HD = f"{W}/hist"; os.makedirs(HD, exist_ok=True)
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M
URL = os.environ["RPC_URL"]; PUMP = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
T0, A, B = 1793664000, 1794704822, 1794877622          # Nov 3 00:00; the screen's 48 h = [A, B)
INIT_REAL = 793_100_000_000_000; WSOL = "So11111111111111111111111111111111111111112"
SOLQ = {WSOL, "11111111111111111111111111111111", None}
PR = json.load(open(f"{SP}/market/prices.json")); sol_usd = PR[WSOL]["usdPrice"]
def rate_of(q):
    if q in SOLQ: return 1.0
    return PR[q]["usdPrice"] / sol_usd * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None
bp = {float(k): v for k, v in json.load(open(f"{W}/bp.json")).items()}
b_of = lambda p: bp[max(b for b in bp if b <= p)]
rows = json.load(open(f"{W}/w3_rows.json"))
C = [r for r in rows if r["hits"] >= 3 and r["cr"] >= 3 and r["lift"] >= 1.5][:40]
def call(m, p):
    for i in range(8):
        try:
            rq = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(rq, timeout=60))
            if "error" in r: raise RuntimeError("rpc error")
            return r["result"]
        except Exception: time.sleep(1.5 * (i + 1))
    return None
POOL = ThreadPoolExecutor(64)
def own_trades(tx, w):
    out = []
    ks = tx["transaction"]["message"]["accountKeys"] + (tx["meta"].get("loadedAddresses") or {}).get("writable", []) + (tx["meta"].get("loadedAddresses") or {}).get("readonly", [])
    for g in tx["meta"].get("innerInstructions") or []:
        for ix in g["instructions"]:
            if ks[ix["programIdIndex"]] != M.lib.PUMP: continue
            raw = M.lib.b58d(ix.get("data", ""))
            if raw[:8] == M.E.EVENT_IX_TAG and raw[8:16] == M.E.DISC_TRADE:
                try: e = M.decode_trade(raw[16:])
                except Exception: continue
                if e["user"] == w and e.get("real") is not None:
                    out.append(dict(t=tx["blockTime"], slot=tx["slot"], m=e["mint"], buy=e["buy"], q=e["q"] if e.get("q") else e["sol"],
                                    quote=e.get("quote_mint"), tok=e["tok"], real=e["real"], bps=(e["fee_bps"] or 0) + (e["cfee_bps"] or 0)))
    return out
def history(w):
    f = f"{HD}/{w}.json"
    if os.path.exists(f): return json.load(open(f))
    sigs, before = [], None
    while len(sigs) < MAXSIG:
        pg = call("getSignaturesForAddress", [w, {"limit": 1000, **({"before": before} if before else {})}])
        if not pg: break
        sigs += [s for s in pg if s["err"] is None and (s.get("blockTime") or 0) >= T0]
        before = pg[-1]["signature"]
        if len(pg) < 1000 or (pg[-1].get("blockTime") or 0) < T0: break
    sigs = sigs[:MAXSIG]
    txs = list(POOL.map(lambda s: call("getTransaction", [s["signature"], M.TXO]), sigs))
    h = dict(n_sigs=len(sigs), t_first=sigs[-1]["blockTime"] if sigs else None, trades=[e for tx in txs if tx for e in own_trades(tx, w)])
    json.dump(h, open(f, "w")); return h
def curve(m): return str(Pubkey.find_program_address([b"bonding-curve", bytes(Pubkey.from_string(m))], PUMP)[0])
OUT = {}
def complete(ms):
    ms = [m for m in ms if m not in OUT]
    for i in range(0, len(ms), 100):
        r = call("getMultipleAccounts", [[curve(m) for m in ms[i:i + 100]], {"encoding": "base64"}])
        for m, a in zip(ms[i:i + 100], (r or {}).get("value") or [None] * 100):
            d = base64.b64decode(a["data"][0]) if a else b""
            OUT[m] = d[48] if len(d) >= 49 else None
def ptail(k, lam):   # P(X >= k), X ~ Poisson(lam)
    return 1 - sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k)) if lam > 0 else 0.0
print(f"{len(C)} candidates (3+ hits from 3+ creators, lift est 1.5+, top 40 by hits)")
print("wallet   | transactions since Nov 3 (from) | period: copyable buys, graduated, expected, lift, P(by chance) | very early (<2%), size med")
res = {}
for r in C:
    w = r["u"]; h = history(w)
    first = {}
    for e in sorted(h["trades"], key=lambda e: e["t"]):
        if e["buy"] and e["m"] not in first: first[e["m"]] = e
    complete(list(first))
    per = collections.defaultdict(list)
    for m, e in first.items():
        rate = rate_of(e["quote"])
        if rate is None or OUT.get(m) is None: continue
        sol = e["q"] * (1 + e["bps"] / 1e4) * rate / 1e9; p = max(0.0, (INIT_REAL - e["real"] - e["tok"]) / INIT_REAL)
        if sol < 0.25 or p >= 0.5: continue
        k = "before" if e["t"] < A else "screen" if e["t"] < B else "after"
        per[k].append(dict(m=m, g=OUT[m], p=p, sol=sol, t=e["t"]))
    res[w] = {k: v for k, v in per.items()}
    tf = time.strftime("%m-%d %H:%M", time.gmtime(h["t_first"])) if h["t_first"] else "-"
    parts = []
    for k in ("before", "screen", "after"):
        v = per.get(k, [])
        if not v: parts.append(f"{k}: 0"); continue
        g = sum(x["g"] for x in v); ex = sum(b_of(x["p"]) for x in v)
        parts.append(f"{k}: {len(v)}, {g}, {ex:.1f}, {g / ex if ex else 0:.1f}x, {ptail(g, ex):.3f}")
    allv = [x for v in per.values() for x in v]
    early = sum(x["p"] < 0.02 for x in allv) / len(allv) if allv else 0
    print(f"{w[:8]} | {h['n_sigs']:5d} ({tf}) | " + " | ".join(parts) + f" | {early:4.0%}, {st.median(x['sol'] for x in allv) if allv else 0:.2f}", flush=True)
    json.dump(res, open(f"{W}/w4_res.json", "w"))
