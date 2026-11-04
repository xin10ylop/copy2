# Price paths for the exit rules, from its buy to the earlier of its first sale and 30 min (we sell behind its first
# sale, so nothing after it matters), from the chain: the coin pool's landed transactions in that window
# (getSignaturesForAddress on the pool, until = its buy, before = its first sale, up to MAXPAGES pages of 1000),
# up to NPTS of them evenly spaced plus the first 3 behind its buy; each one's average price on that pool against
# its own average buy price, both in the coin's quote (pool side), and its side. Bounded: a spike between two
# sampled trades can be missed. When the pages run out before reaching its buy (a busy coin and a late first sale),
# GMGN 30 s candles instead (USD / its USD buy price), the candle that holds its buy by its close only.
# Output paths/<wallet>.json {sig0: {"src": "chain"|"cs", "n": landed txs in the window, "pts": [[t, hi, lo, close, side]]}}.
#   [GMGN_API_KEY=...] python3 -I paths_g1.py TRIPS_JSON [NPTS] [MAXPAGES]
import sys, os, json, time, subprocess, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g1lib import *
from concurrent.futures import ThreadPoolExecutor
src = sys.argv[1]; NPTS = int(sys.argv[2]) if len(sys.argv) > 2 else 25; MAXP = int(sys.argv[3]) if len(sys.argv) > 3 else 4
d = jl(src); w = d["wallet"]; ch = jl(f"{G1}/chain/{w}.json")
os.makedirs(G1 + "/paths", exist_ok=True); fn = f"{G1}/paths/{w}.json"
out = jl(fn) if os.path.exists(fn) else {}
calls = [0, 0]; lk = threading.Lock()
WIN = int(os.environ.get("PATHWIN", "3600"))   # the owner's limit: holds up to an hour (not days); was 1800
def candles(t):
    """30 s candles in pieces of at most 2850 s (GMGN returns at most 100 candles, the last 100 of the range: G4)"""
    a, b = t["t0"] - 30, min(t["sells"][0]["t"], t["t0"] + WIN) + 60
    out, x = None, a
    while x < b:
        y = min(b, x + 2850); part = candles1(t, x, y)
        if part is None: return out
        out = part if out is None else dict(src="cs", n=out["n"] + part["n"], pts=out["pts"] + [p for p in part["pts"] if not out["pts"] or p[0] > out["pts"][-1][0]])
        x = y
    return out
def candles1(t, a, b):
    for i in range(5):
        r = subprocess.run(["gmgn-cli", "market", "kline", "--chain", "sol", "--address", t["mint"], "--resolution", "30s",
                            "--from", str(a), "--to", str(b), "--raw"], capture_output=True, text=True, timeout=180)
        with lk: calls[1] += 1
        try:
            L = json.loads(r.stdout).get("list") or []
            pts = []
            for c in L:
                s = c["time"] // 1000; hi, lo, cl = float(c["high"]) / t["px0"], float(c["low"]) / t["px0"], float(c["close"]) / t["px0"]
                if s + 30 <= t["t0"]: continue
                if s < t["t0"]: hi = lo = cl                       # the candle holding its buy also holds the trades before it
                pts.append([s + 30, hi, lo, cl, None])
            return dict(src="cs", n=len(L), pts=pts)
        except Exception: time.sleep(20 * (i + 1))
    return None
def one(t):
    need = min(t["sells"][0]["t"] - t["t0"], WIN) if t["sells"] else 0
    if t["sig0"] in out and (out[t["sig0"]] or {}).get("win", min(need, 1800)) >= need: return     # done, long enough
    if not t["sells"] or not (t.get("s2") or t.get("s2k2") or t.get("s2k1")): return
    c = ch.get(t["sig0"]) or {}
    if not c.get("pools"): return
    pool = c["pools"][0]["pool"]; mine = c["pools"][0]["px"]; end = min(t["sells"][0]["t"], t["t0"] + WIN)
    before, got, reached = t["sells"][0]["sig"], [], False
    for page in range(MAXP):
        r = R.rpc("getSignaturesForAddress", [pool, {"before": before, "until": t["sig0"], "limit": 1000}]) or []
        with lk: calls[0] += 1
        got += r
        if len(r) < 1000: reached = True; break
        before = r[-1]["signature"]
    if not reached:
        res = candles(t)
    else:
        ok = [x for x in reversed(got) if not x.get("err") and (x.get("blockTime") or 0) <= end + 1]
        pick = ok[:3] + ([ok[3 + int(i * (len(ok) - 4) / (NPTS - 1))] for i in range(NPTS)] if len(ok) > NPTS + 3 else ok[3:])
        pts = []
        for x in pick:
            tx = R.tx_of(x["signature"]); R.TXC.pop(x["signature"], None)
            with lk: calls[0] += 1
            if not tx: continue
            for p in R.pools(tx, t["mint"]):
                if p[0] == pool:
                    m = p[1] / mine; pts.append([tx.get("blockTime") or x.get("blockTime"), m, m, m, p[5]]); break
        res = dict(src="chain", n=len(ok), pts=pts)
    if res: res["win"] = need                                  # how far this path reaches (s after its buy)
    with lk:
        out[t["sig0"]] = res
        if len(out) % 10 == 0: json.dump(out, open(fn, "w"))
with ThreadPoolExecutor(2) as ex: list(ex.map(one, d["trips"]))
json.dump(out, open(fn, "w"))
print(time.strftime("%H:%M:%S"), w[:8], len(out), "paths:", sum(1 for v in out.values() if v and v["src"] == "chain"), "chain,",
      sum(1 for v in out.values() if v and v["src"] == "cs"), "candles; calls chain", calls[0], "gmgn", calls[1], flush=True)
