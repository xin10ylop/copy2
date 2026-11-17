# Telegram call test, step 2: each call (calls.json) on the chain, and our copy of it.
#  - Which addresses are token mints (getMultipleAccounts); a message's call = its first mint (a bot's forwarded card also
#    lists pools and wallets).
#  - A pump coin (its bonding curve exists): the curve's trades from 10 min before the call to an hour after (signatures
#    newest first, back past the call; cached in DIR/paths/). If the curve had completed before the call, the coin traded in
#    its pool at the call: not modelled here (counted). Other venues (Raydium LaunchLab, Meteora...): counted, not modelled.
#  - The time zone check: a call cannot be before the coin's first trade (counted per zone).
#  - Our copy: 0.5 SOL bought at the first trade DELAY seconds or more after the post (DELAY 3: a bot reading the channel),
#    refused if the price is already 1.25x the price at the post; exits fixed, the same as the wallet tests (w5_copy):
#    tp2/tp3/tp5 (else graduation, else 60 min), grad (else 60 min), t10/t30 (sell at 10/30 min), signals (sell_pressure
#    [5, 60, 30] or stall 180 s, else graduation, else 60 min). Graduation = sold at the curve's last price.
#  - Each exit: copies, net, a copy, won, without the best 5, first half / second half by time.
# The RPC from RPC_URL, never printed.
#   RPC_URL=... python3 -I tg_test.py DIR [DELAY=3] > out/<channel>.txt
import sys, os, json, gzip, time, base64, urllib.request, collections, numpy as np
from concurrent.futures import ThreadPoolExecutor
from solders.pubkey import Pubkey
D = sys.argv[1]; DELAY = float(sys.argv[2]) if len(sys.argv) > 2 else 3; PC = f"{D}/paths"; os.makedirs(PC, exist_ok=True)
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt"); import hunt_lib as H
URL = os.environ["RPC_URL"]; PUMP = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"); HOLD = 3600
TOK = {"TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"}
def call(m, p):
    for i in range(8):
        try:
            rq = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(rq, timeout=60))
            if "error" in r: raise RuntimeError("rpc error")
            return r["result"]
        except Exception: time.sleep(1.5 * (i + 1))
    return None
POOL = ThreadPoolExecutor(48)
def valid(a):
    try: Pubkey.from_string(a); return True
    except Exception: return False   # a base58 word that is not a 32-byte key would fail the whole batch
calls = [c for c in json.load(open(f"{D}/calls.json")) if valid(c[0])]; addrs = [a for a, _, _ in calls]
info = {}
for i in range(0, len(addrs), 100):
    r = call("getMultipleAccounts", [addrs[i:i + 100], {"encoding": "base64"}])
    for a, x in zip(addrs[i:i + 100], (r or {}).get("value") or []):
        d = base64.b64decode(x["data"][0]) if x else b""   # a mint: 82 bytes, or a Token-2022 mint with extensions (type byte 1)
        info[a] = bool(x) and x["owner"] in TOK and (len(d) == 82 or (len(d) > 165 and d[165] == 1))
bymsg = collections.OrderedDict()
for a, t, txt in calls:
    if info.get(a) and (t, txt) not in bymsg: bymsg[(t, txt)] = a
C = [(a, t) for (t, _), a in bymsg.items()]
def curve(m): return str(Pubkey.find_program_address([b"bonding-curve", bytes(Pubkey.from_string(m))], PUMP)[0])
def get(at):
    m, t = at; f = f"{PC}/{m}.json.gz"
    if os.path.exists(f): return json.load(gzip.open(f))
    c = curve(m); acc = call("getAccountInfo", [c, {"encoding": "base64"}])
    if not acc or not acc.get("value"): out = dict(venue="other")
    else:
        sigs, before, first_t = [], None, None
        for _ in range(15):
            pg = call("getSignaturesForAddress", [c, {"limit": 1000, **({"before": before} if before else {})}])
            if not pg: break
            sigs += [s for s in pg if s["err"] is None]; before = pg[-1]["signature"]
            if len(pg) < 1000 or (pg[-1].get("blockTime") or 0) < t - 600: break
        first_t = min((s["blockTime"] for s in sigs if s.get("blockTime")), default=None) if len(sigs) % 1000 else None
        win = sorted((s for s in sigs if t - 600 <= (s.get("blockTime") or 0) <= t + HOLD + 60), key=lambda s: s["slot"])
        last_t = max((s["blockTime"] for s in sigs if s.get("blockTime")), default=None)
        txs = list(POOL.map(lambda s: call("getTransaction", [s["signature"], M.TXO]), win))
        tr = [e for tx in txs if tx for e in M.trades(tx, m)]
        d = base64.b64decode(acc["value"]["data"][0]); complete = len(d) > 48 and d[48] == 1
        out = dict(venue="pump", tr=tr, first_t=first_t, last_t=last_t, complete=complete)
    with gzip.open(f + ".tmp", "wt") as fh: json.dump(out, fh)
    os.replace(f + ".tmp", f); return out
with ThreadPoolExecutor(6) as ex: P = list(ex.map(get, C))
cnt = collections.Counter(); rows = []
for (m, t), p in zip(C, P):
    if p["venue"] != "pump": cnt["other venue"] += 1; continue
    if p["first_t"] and t < p["first_t"] - 5: cnt["call before the coin's first trade (zone?)"] += 1
    tr = p["tr"]
    if p["complete"] and p["last_t"] and p["last_t"] < t: cnt["graduated before the call (pool)"] += 1; continue
    k = next((i for i, e in enumerate(tr) if e["t"] >= t + DELAY), None)
    if k is None or not tr: cnt["no curve trade after the call"] += 1; continue
    k0 = max([i for i, e in enumerate(tr) if e["t"] <= t] or [0])
    # the post's price is the leader: H.prep with the trade at the post as "its buy" and our landing at k
    rate = 1.0 if 25e9 < tr[0]["vq"] * tr[0]["vt"] / 1.073e15 < 35e9 else None
    if rate is None: cnt["curve priced in another token (not modelled)"] += 1; continue
    p0 = H.prep(tr, k0, rate, max(1, k - k0))
    cnt["modelled"] += 1; rows.append((t, m, p0))
WHY = {}
STAKE = float(os.environ.get("STAKE", 0.5))
def run(p, ex, stake=None, key=None):
    stake = stake or STAKE
    if p["refused"]: return None
    vt0, vq0, bps0 = p["ent"]; net_in = stake * 1e9 * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    def out(i):
        vq, vt, b = (vq0, vt0, bps0) if i is None else (p["vq"][i], p["vt"][i], p["bps"][i])
        vq_r = vq + net_in; vt_r = vt * vq / vq_r
        return (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - b / 1e4) / 1e9 - stake - 0.0026
    n = len(p["px"])
    if n == 0: return out(None)
    px, age = p["px"], p["age"]; c = []   # px: the price over the price at the post
    i = H.first(p["grad"]); c += [(i, 0)] if i is not None else []
    if ex.startswith("tp"): i = H.first(px >= float(ex[2:])); c += [(i, 1)] if i is not None else []
    if ex == "signals":
        lo = np.searchsorted(age, age - 60, side="left"); s = np.concatenate([[0], np.cumsum(p["osell"])]); b = np.concatenate([[0], np.cumsum(p["obuy"])])
        i = H.first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= 5) & (age >= 30)); c += [(i, 1)] if i is not None else []
        pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
        i = H.first((pk >= 1.0) & (age - lasthi >= 180)); c += [(i, 1)] if i is not None else []
    cap = {"t10": 600, "t30": 1800}.get(ex, HOLD)
    i = H.first(age >= cap); c += [(i, 0)] if i is not None else []
    if not c: j = n - 1; why = "end of data"
    else:
        i, d = min(c); j = min(i + d, n - 1)
        why = "graduated" if p["grad"][j - d] and d == 0 and age[i] < cap else ("time" if d == 0 else ex)
    if key is not None: WHY[key] = (why, float(age[j] - p["last"]), float(px[j]))
    return out(j)
print(f"{len(calls)} addresses, {sum(info.values())} of them mints; {len(C)} calls (a message's first mint); buy {DELAY:.0f} s after the post")
print("  " + ", ".join(f"{k}: {v}" for k, v in cnt.most_common()))
ref = sum(1 for _, _, p in rows if p["refused"])
print(f"  refused (already 1.25x the post's price when we land): {ref}")
print("exit    | copies, net SOL, a copy, won | w/o best 5 | 1st half / 2nd half")
rows.sort()
for ex in ["tp2", "tp3", "tp5", "grad", "t10", "t30", "signals"]:
    v = [(t, run(p, ex)) for t, _, p in rows]; v = [(t, x) for t, x in v if x is not None]
    if not v: print(f"{ex:7s} | 0"); continue
    xs = [x for _, x in v]; s = sorted(xs, reverse=True); h = len(v) // 2
    print(f"{ex:7s} | {len(v):3d}, {sum(xs):+6.2f}, {sum(xs) / len(xs) / STAKE:+6.1%}, {sum(x > 0 for x in xs) / len(xs):3.0%} | {sum(s[5:]):+6.2f} | "
          f"{sum(x for _, x in v[:h]):+6.2f} / {sum(x for _, x in v[h:]):+6.2f}")
if os.environ.get("DETAIL"):
    ex = os.environ["DETAIL"]; print(f"\nper copy, exit {ex}: post (UTC), coin, net SOL, why it sold, held s, price at the sale / at the post")
    for t, m, p in rows:
        x = run(p, ex, key=m)
        if x is None: print(f"  {time.strftime('%m-%d %H:%M', time.gmtime(t))} {m[:8]} refused"); continue
        w, held, pxs = WHY[m]; print(f"  {time.strftime('%m-%d %H:%M', time.gmtime(t))} {m[:8]} {x:+.3f} {w:10s} {held:6.0f} s {pxs:5.2f}x")
