# Step 1: one row per copyable buy (781) with everything known when the bot sees wallet 4's buy, and the copy's result
# under the live rule (tp 3.0, 600 s, early 30-290 s under 1.5x) at each landing, no slot limit. Writes
# SKIPQ/features.json. Features: what we pay with, hops, its buy's size, the curve at its buy (share of the coin
# sold, the price move of its buy, the fee tier), the block before its buy (trades in its slot ahead of it), the coin
# before its buy (transactions and age, one RPC call a coin, cached), wallet 4's own state (buys in the last 10 / 60
# min, seconds since its last buy, its result on its last 5 closed coins), the hour, our entry premium by landing.
#   python3 -I features.py SPD SKIPQ
import sys, os, json, gzip, time, datetime, collections, urllib.request, concurrent.futures as cf
SPD, SKIPQ = sys.argv[1], sys.argv[2]
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp(); os.environ["FE_T0"] = str(T0)
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); sys.argv = ["x", SPD, "0.5"]
import float_exits as F, lib as L
import numpy as np
W4 = L.W4; WSOL = "So11111111111111111111111111111111111111112"
RULE = dict(tp=3.0, hold=600, early=(30, 290, 1.5), sl=None)
R = open("/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/month/.triton_url").read().strip()
os.makedirs(f"{SKIPQ}/prior", exist_ok=True)
def call(m, p, key):
    path = f"{SKIPQ}/prior/{key}.json.gz"
    if os.path.exists(path):
        try: return json.load(gzip.open(path))
        except Exception: os.remove(path)
    for k in range(6):
        try:
            req = urllib.request.Request(R, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"content-type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=60))
            if "error" in r: raise RuntimeError("rpc error")
            tmp = f"{path}.{os.getpid()}.tmp"
            with gzip.open(tmp, "wt") as f: json.dump(r["result"], f)
            os.replace(tmp, path); return r["result"]
        except Exception: time.sleep(1.5 * (k + 1))
    return None
# wallet 4's own trips (its SOL and priced tokens in and out per coin) for its recent form
px = json.load(open(f"{SPD}/prices.json")); trips = collections.defaultdict(lambda: dict(spent=0.0, back=0.0, held=0, first=None, last=None)); allbuys = []
for f in os.listdir(f"{SPD}/w4tx"):
    t = json.load(open(f"{SPD}/w4tx/{f}")); m = t["meta"]
    if m.get("err"): continue
    ks = t["transaction"]["message"]["accountKeys"] + sum(((m.get("loadedAddresses") or {}).get(x, []) for x in ("writable", "readonly")), [])
    if W4 not in ks: continue
    i = ks.index(W4); d = collections.defaultdict(int)
    for k, s in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in m.get(k) or []:
            if b.get("owner") == W4: d[b["mint"]] += s * int(b["uiTokenAmount"]["amount"])
    d = {k: v for k, v in d.items() if v}; sol = m["postBalances"][i] - m["preBalances"][i] + d.pop(WSOL, 0)
    coins = [k for k in d if k not in px]
    if len(coins) != 1: continue
    c = coins[0]; tr = trips[c]; v = sol + sum(a * px[k] for k, a in d.items() if k != c); tr["held"] += d[c]; bt = t["blockTime"]
    if d[c] > 0:
        tr["spent"] += -v; tr["first"] = min(tr["first"] or bt, bt); allbuys.append((bt, -v / 1e9))
    else: tr["back"] += v; tr["last"] = max(tr["last"] or bt, bt)
closed = sorted((tr["last"], (tr["back"] - tr["spent"]) / tr["spent"]) for tr in trips.values() if tr["held"] == 0 and tr["spent"] > 0 and tr["last"])
allbuys.sort(); big = [b for b in allbuys if b[1] >= 1.45]
rows = F.rows; rt = sorted(r["t"] for r in rows)
def prior(r):
    m, tr = F.P[r["key"]]
    k = next(i for i, e in enumerate(tr) if e["user"] == W4 and e["buy"] and e["slot"] == r["slot"])
    res = call("getSignaturesForAddress", [m, {"before": tr[k]["sig"], "limit": 1000}], f"{r['key']}")
    return res
with cf.ThreadPoolExecutor(12) as ex: PR = list(ex.map(prior, rows))
out = []
for r, pr in zip(rows, PR):
    m, tr = F.P[r["key"]]
    k = next(i for i, e in enumerate(tr) if e["user"] == W4 and e["buy"] and e["slot"] == r["slot"])
    its = tr[k]; t = its["t"]
    vq0 = its["vq"] - its["q"]; vt0 = its["vt"] * its["vq"] / vq0 if vq0 > 0 else its["vt"]
    ahead = tr[:k]                                             # trades in its slot before its buy (the path starts at its slot)
    f = dict(key=r["key"], t=t, anchor=r["anchor"], hops=r["hops"], how=r["how"], sol=r["sol"],
             blk=0 if r["t"] < L.T_STOP else 1 if r["t"] < datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp() else 2,
             day=datetime.datetime.fromtimestamp(r["t"] + 7200, datetime.timezone.utc).strftime("%m-%d"), hour=int((t % 86400) // 3600),
             bps=its["bps"], move=(vt0 / its["vt"]) ** 2, real=its.get("real"), sold=1 - (its.get("real") or 0) / 793.1e12,
             vq_sol=its["vq"] * r["sol"] * 1e9 / (its["q"] * (1 + its["bps"] / 1e4)) / 1e9,          # the curve's virtual quote reserve after its buy, in SOL at its rate
             ahead_n=len(ahead), ahead_buys=sum(1 for e in ahead if e["buy"]), ahead_sells=sum(1 for e in ahead if not e["buy"]),
             same_slot_after=sum(1 for e in tr[k + 1:] if e["slot"] == its["slot"]),
             w4_buys_10m=sum(1 for b in big if t - 600 <= b[0] < t), w4_buys_60m=sum(1 for b in big if t - 3600 <= b[0] < t),
             w4_all_buys_10m=sum(1 for b in allbuys if t - 600 <= b[0] < t),
             since_last=min((t - b[0] for b in big if b[0] < t), default=None))
    last5 = [c[1] for c in closed if c[0] < t][-5:]
    f["w4_last5"] = sum(last5) / len(last5) if last5 else None; f["w4_last5_won"] = sum(1 for x in last5 if x > 0) if last5 else None
    if pr is not None:
        f["prior_n"] = len(pr); bts = [x.get("blockTime") for x in pr if x.get("blockTime")]
        f["prior_capped"] = len(pr) >= 1000; f["age_s"] = (t - min(bts)) if bts else 0
        f["prior_60s"] = sum(1 for b in bts if b >= t - 60); f["prior_err"] = sum(1 for x in pr if x.get("err")) / max(1, len(pr))
    for n in L.LAND:
        p = F.PREP[r["key"], n]; net, why, held = L.model(p, 0.5, **RULE); tag = str(n)
        vt_e = p["ent"][0]; f[f"px_in_{tag}"] = (its["vt"] / vt_e) ** 2; f[f"net_{tag}"] = net; f[f"why_{tag}"] = why; f[f"held_{tag}"] = held
        w = p["age"] < 600; f[f"peak_{tag}"] = float(p["px"][w].max()) if w.any() else 1.0
    out.append(f)
json.dump(out, open(f"{SKIPQ}/features.json", "w"))
tp = sum(1 for f in out if f["why_4"] == "tp")
print(f"{len(out)} buys; prior history fetched for {sum(1 for f in out if 'prior_n' in f)}; take profits at landing 4: {tp}; sum of nets {sum(f['net_4'] for f in out):+.2f}")
