# Telegram call test, step 3: the calls that were trading in a pool at the post (a pump coin graduated before it, or
# another venue). The pool: DexScreener's SOL pair for the coin (the one with the most liquidity; public API, no key). Its
# price after every swap from its own vault balances in the transaction (the two token accounts the pool owns: the coin
# and wrapped SOL), so any constant-product pool works (PumpSwap and others whose vaults the pool owns); a pool whose
# vaults it does not own is counted, not modelled. Signatures newest first back past the post (at most 30 pages: a pool
# busier than that is counted, not modelled); swaps from the post to an hour after. Cached in DIR/pools/.
# Our copy: 0.5 SOL at the first swap DELAY s or more after the post, against the pool's reserves (constant product), a fee
# of FEE each way and 0.0026 SOL of transaction costs; refused past 1.25x the price at the post. Exits fixed: tp2/tp3/tp5
# (else 60 min), t10/t30/t60. Each: copies, net, a copy, won, without the best 5, halves by time.
# The RPC from RPC_URL, never printed.
#   RPC_URL=... python3 -I tg_pool.py DIR [DELAY=1] [FEE=0.01]
import sys, os, json, gzip, time, base64, urllib.request, collections
from concurrent.futures import ThreadPoolExecutor
from solders.pubkey import Pubkey
D = sys.argv[1]; DELAY = float(sys.argv[2]) if len(sys.argv) > 2 else 1; FEE = float(sys.argv[3]) if len(sys.argv) > 3 else 0.01
URL = os.environ["RPC_URL"]; WSOL = "So11111111111111111111111111111111111111112"; HOLD = 3600; PD = f"{D}/pools"; os.makedirs(PD, exist_ok=True)
PUMP = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"); TOK = {"TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"}
def call(m, p):
    for i in range(8):
        try:
            rq = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(rq, timeout=60))
            if "error" in r: raise RuntimeError("rpc error")
            return r["result"]
        except Exception: time.sleep(1.5 * (i + 1))
    return None
def valid(a):
    try: Pubkey.from_string(a); return True
    except Exception: return False
calls = [c for c in json.load(open(f"{D}/calls.json")) if valid(c[0])]; addrs = [a for a, _, _ in calls]; mint = {}
for i in range(0, len(addrs), 100):
    r = call("getMultipleAccounts", [addrs[i:i + 100], {"encoding": "base64"}])
    for a, x in zip(addrs[i:i + 100], (r or {}).get("value") or []):
        d = base64.b64decode(x["data"][0]) if x else b""
        mint[a] = bool(x) and x["owner"] in TOK and (len(d) == 82 or (len(d) > 165 and d[165] == 1))
bymsg = collections.OrderedDict()
for a, t, txt in calls:
    if mint.get(a) and (t, txt) not in bymsg: bymsg[(t, txt)] = a
C = [(a, t) for (t, _), a in bymsg.items()]
def curve_state(m, t):   # 'curve' if its pump curve traded after the post (step 2 models it), else 'pool'
    c = str(Pubkey.find_program_address([b"bonding-curve", bytes(Pubkey.from_string(m))], PUMP)[0])
    acc = call("getAccountInfo", [c, {"encoding": "base64"}])
    if not acc or not acc.get("value"): return "pool"
    d = base64.b64decode(acc["value"]["data"][0])
    if not (len(d) > 48 and d[48] == 1): return "curve"
    f = f"{D}/paths/{m}.json.gz"   # step 2's cache knows whether the curve completed before the post
    if os.path.exists(f):
        x = json.load(gzip.open(f))
        if x.get("last_t") and x["last_t"] >= t: return "curve"
    return "pool"
def pair_of(m):
    for i in range(4):
        try:
            d = json.load(urllib.request.urlopen(f"https://api.dexscreener.com/latest/dex/tokens/{m}", timeout=30))
            ps = [p for p in d.get("pairs") or [] if p.get("chainId") == "solana" and p["quoteToken"]["address"] == WSOL and p["baseToken"]["address"] == m]
            ps.sort(key=lambda p: -(p.get("liquidity") or {}).get("usd", 0) or 0)
            return (ps[0]["pairAddress"], ps[0]["dexId"]) if ps else (None, None)
        except Exception: time.sleep(2 * (i + 1))
    return None, None
POOL = ThreadPoolExecutor(48)
def path(m, t):
    f = f"{PD}/{m}.json.gz"
    if os.path.exists(f): return json.load(gzip.open(f))
    out = dict(state=curve_state(m, t))
    if out["state"] == "pool":
        pa, dex = pair_of(m); out.update(pair=pa, dex=dex)
        if pa:
            sigs, before, reached = [], None, False
            for _ in range(30):
                pg = call("getSignaturesForAddress", [pa, {"limit": 1000, **({"before": before} if before else {})}])
                if not pg: reached = True; break
                sigs += [s for s in pg if s["err"] is None]; before = pg[-1]["signature"]
                if len(pg) < 1000 or (pg[-1].get("blockTime") or 0) < t - 60: reached = True; break
            out["reached"] = reached
            win = sorted((s for s in sigs if t - 60 <= (s.get("blockTime") or 0) <= t + HOLD + 60), key=lambda s: s["slot"])
            txs = list(POOL.map(lambda s: call("getTransaction", [s["signature"], {"encoding": "json", "maxSupportedTransactionVersion": 0}]), win))
            px = []
            for tx in txs:
                if not tx: continue
                bal = {b["mint"]: int(b["uiTokenAmount"]["amount"]) for b in tx["meta"].get("postTokenBalances") or [] if b.get("owner") == pa}
                if m in bal and WSOL in bal and bal[m] > 0: px.append([tx["blockTime"], bal[WSOL], bal[m]])
            out["px"] = px
    with gzip.open(f + ".tmp", "wt") as fh: json.dump(out, fh)
    os.replace(f + ".tmp", f); return out
with ThreadPoolExecutor(6) as ex: P = list(ex.map(lambda c: path(*c), C))
cnt = collections.Counter(); rows = []
for (m, t), p in zip(C, P):
    if p["state"] != "pool": cnt["on the curve at the post (step 2)"] += 1; continue
    if not p.get("pair"): cnt["no SOL pool found"] += 1; continue
    if not p.get("reached"): cnt["pool too busy to reach the post"] += 1; continue
    px = p.get("px") or []
    if not px: cnt["no swap read in the hour (pool does not own its vaults, or dead)"] += 1; continue
    k0 = [x for x in px if x[0] <= t]; k = [i for i, x in enumerate(px) if x[0] >= t + DELAY]
    if not k: cnt["no swap after the post"] += 1; continue
    q0, b0 = (k0[-1][1], k0[-1][2]) if k0 else (px[0][1], px[0][2]); p0 = q0 / b0
    cnt["modelled"] += 1; rows.append((t, m, p0, px[k[0]:]))
def run(p0, path, ex, stake=0.5):
    t0, q, b = path[0]; pe = q / b
    if pe > 1.25 * p0: return None
    inn = stake * 1e9 * (1 - FEE); tok = b * inn / (q + inn)
    def sell(i): _, q2, b2 = path[i]; return q2 * tok / (b2 + tok) * (1 - FEE) / 1e9 - stake - 0.0026
    cap = {"t10": 600, "t30": 1800}.get(ex, HOLD)
    for i, (tt, q2, b2) in enumerate(path):
        if tt - t0 >= cap: return sell(i)
        if ex.startswith("tp") and (q2 / b2) >= float(ex[2:]) * p0: return sell(min(i + 1, len(path) - 1))
    return sell(len(path) - 1)
print(f"{len(C)} calls; buy {DELAY:.0f} s after the post, fee {FEE:.1%} each way")
print("  " + ", ".join(f"{k}: {v}" for k, v in cnt.most_common()))
print("exit    | copies, net SOL, a copy, won | w/o best 5 | 1st half / 2nd half")
rows.sort()
for ex in ["tp2", "tp3", "tp5", "t10", "t30", "t60"]:
    v = [(t, run(p0, pa, ex)) for t, _, p0, pa in rows]; v = [(t, x) for t, x in v if x is not None]
    if not v: print(f"{ex:7s} | 0"); continue
    xs = [x for _, x in v]; s = sorted(xs, reverse=True); h = len(v) // 2
    print(f"{ex:7s} | {len(v):3d}, {sum(xs):+6.2f}, {sum(xs) / len(xs) / 0.5:+6.1%}, {sum(x > 0 for x in xs) / len(xs):3.0%} | {sum(s[5:]):+6.2f} | "
          f"{sum(x for _, x in v[:h]):+6.2f} / {sum(x for _, x in v[h:]):+6.2f}")
