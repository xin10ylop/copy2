# Winners first, step 5: engineer the copy of a wallet that passed step 4. For each of its copyable buys (w4_res.json),
# the coin's curve trades from its buy to an hour after (the curve's signatures, newest first, back to its buy's slot, at
# most 10 pages; cached in SP/winners/cpaths/), and our copy at 0.5 SOL landing in the next slot after its buy (refused
# past 1.25x; hunt_lib.prep) under a fixed set of exits, the same for every wallet (never tuned to one):
#   mirror  : its first sale; else graduation; else 60 min
#   grad    : graduation (sold at the curve's last price, as hunt_lib); else 60 min
#   live    : the live setup (hunt_lib.model: tp 4, its sale 30-290 s under 1.5x, sell_pressure, stall 180 s, 600 s)
#   tp2/tp3/tp5 : that multiple; else graduation; else 60 min
#   signals : sell_pressure [5, 60, 30] or stall 180 s; else graduation; else 60 min
# An exit is picked on the first half of the period before Nov 15 and scored on its second half and on the later days;
# every result also without the best 5. The RPC from RPC_URL, never printed.
#   RPC_URL=... python3 -I w5_copy.py SP WALLET[,WALLET...] > out/w5_copy.txt
import sys, os, json, gzip, time, urllib.request, numpy as np
from concurrent.futures import ThreadPoolExecutor
from solders.pubkey import Pubkey
SP = sys.argv[1]; WS = sys.argv[2].split(","); W = f"{SP}/winners"; CP = os.environ.get("CPDIR", f"{W}/cpaths"); CP0 = f"{W}/cpaths"; os.makedirs(CP, exist_ok=True)   # CPDIR + SAMPLE: a sampled cache (Nov 18)
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt"); import hunt_lib as H
URL = os.environ["RPC_URL"]; PUMP = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"); HOLD = int(os.environ.get("HOLD", 3600))
WSOL = "So11111111111111111111111111111111111111112"; SOLQ = {WSOL, "11111111111111111111111111111111", None}
PR = json.load(open(f"{SP}/market/prices.json")); sol_usd = PR[WSOL]["usdPrice"]
def rate_of(q):
    if q in SOLQ: return 1.0
    return PR[q]["usdPrice"] / sol_usd * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None
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
def curve(m): return str(Pubkey.find_program_address([b"bonding-curve", bytes(Pubkey.from_string(m))], PUMP)[0])
def cpath(m, slot, t):
    f = f"{CP}/{slot}_{m}.json.gz"
    if os.path.exists(f): return json.load(gzip.open(f))
    if os.path.exists(f"{CP0}/{slot}_{m}.json.gz"): return json.load(gzip.open(f"{CP0}/{slot}_{m}.json.gz"))   # a full path is fine too
    c, sigs, before = curve(m), [], None
    for _ in range(10):
        pg = call("getSignaturesForAddress", [c, {"limit": 1000, **({"before": before} if before else {})}])
        if not pg: break
        sigs += [s for s in pg if s["err"] is None and s["slot"] >= slot and (s.get("blockTime") or 0) <= t + HOLD + 60]
        before = pg[-1]["signature"]
        if len(pg) < 1000 or pg[-1]["slot"] < slot: break
    sigs = sorted(sigs, key=lambda s: s["slot"])
    if os.environ.get("SAMPLE"):   # every trade to FULL s after t, then 1 in SAMPLE (prices only: no sell-pressure counts)
        SM, FU = int(os.environ["SAMPLE"]), int(os.environ.get("FULL", 60))
        sigs = [s for i, s in enumerate(sigs) if (s.get("blockTime") or 0) <= t + FU or i % SM == 0 or i == len(sigs) - 1]
    txs = list(POOL.map(lambda s: call("getTransaction", [s["signature"], M.TXO]), sigs))
    tr = [e for tx in txs if tx for e in M.trades(tx, m)]
    with gzip.open(f + ".tmp", "wt") as fh: json.dump(tr, fh)
    os.replace(f + ".tmp", f); return tr
def run(p, ex, stake=0.5):
    if ex == "live": return H.model(p)[0]
    if p["refused"]: return -0.0004
    vt0, vq0, bps0 = p["ent"]; Q = stake * 1e9 / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    def out(i):
        vq, vt, b = (vq0, vt0, bps0) if i is None else (p["vq"][i], p["vt"][i], p["bps"][i])
        vq_r = vq + net_in; vt_r = vt * vq / vq_r
        return (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - b / 1e4) * p["rate"] / 1e9 - stake - 0.0026
    n = len(p["px"])
    if n == 0: return out(None)
    px, age = p["px"], p["age"]; c = []
    i = H.first(p["grad"]); c += [(i, 0)] if i is not None else []
    if ex == "mirror": i = H.first(p["sell"]); c += [(i, 1)] if i is not None else []
    if ex.startswith("tp"): i = H.first(px >= float(ex[2:])); c += [(i, 1)] if i is not None else []
    if ex == "signals":
        lo = np.searchsorted(age, age - 60, side="left"); s = np.concatenate([[0], np.cumsum(p["osell"])]); b = np.concatenate([[0], np.cumsum(p["obuy"])])
        i = H.first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= 5) & (age >= 30)); c += [(i, 1)] if i is not None else []
        pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
        i = H.first((pk >= 1.0) & (age - lasthi >= 180)); c += [(i, 1)] if i is not None else []
    i = H.first(age >= HOLD); c += [(i, 0)] if i is not None else []
    if not c: return out(n - 1)
    i, d = min(c); return out(min(i + d, n - 1))
EX = ["mirror", "grad", "live", "tp2", "tp3", "tp5", "signals"]
res = json.load(open(os.environ.get("RES", f"{W}/w4_res.json")))
def summ(v):
    if not v: return "   0"
    s = sorted(v, reverse=True); return f"{len(v):4d} {sum(v):+7.2f} ({sum(v) / len(v) / 0.5:+6.1%}) w/o5 {sum(s[5:]):+6.2f}"
for w in WS:
    full = next(k for k in res if k.startswith(w)); h = json.load(open(f"{W}/hist/{full}.json"))
    buys = {}
    for e in sorted(h["trades"], key=lambda e: e["t"]):
        if e["buy"] and e["m"] not in buys: buys[e["m"]] = e
    R = {k: [] for k in ("before", "screen", "after")}
    items = [(k, x) for k, v in res[full].items() for x in v]
    if os.environ.get("LIMIT"):   # a random sample of the copies (seed 7), for wallets with hundreds
        import random; random.Random(7).shuffle(items); items = items[:int(os.environ["LIMIT"])]
    def one(kx):
        k, x = kx; e = buys[x["m"]]; rate = rate_of(e["quote"])
        tr = cpath(x["m"], e["slot"], e["t"])
        idx = next((i for i, y in enumerate(tr) if y["user"] == full and y["buy"] and y["slot"] == e["slot"]), None)
        if idx is None or idx >= len(tr) - 1 or rate is None: return None
        p = H.prep(tr, idx, rate, "slot+1")
        return k, x["t"], {ex: run(p, ex) for ex in EX}
    with ThreadPoolExecutor(6) as ex_: out = [o for o in ex_.map(one, items) if o]
    for k, t, r in out: R[k].append((t, r))
    bf = sorted(R["before"]); half = len(bf) // 2
    print(f"\n{full}: {len(out)} copies modelled of {len(items)} (slot+1, 0.5 SOL)")
    print(f"  exit    | before, 1st half          | before, 2nd half          | the 48 h                  | after")
    for ex in EX:
        print(f"  {ex:7s} | " + " | ".join(summ([r[ex] for _, r in part]) for part in (bf[:half], bf[half:], sorted(R["screen"]), sorted(R["after"]))), flush=True)
