# Step 1. Load the copy model once (float_exits / lib), run the live rule on every copyable buy at the three landings
# (each copy on its own: the slot limit is applied later, in common.py), and collect everything known about each buy
# at the moment the bot sees it (the row, its own trade, the trades before it in its block, wallet 4's recent buys
# and transactions, the coin's curve). Saves SKQ/base.pkl; prints the baseline run as a check against the earlier
# studies (+37.21 SOL over the 23 full Beirut days, steady/out/steady.txt).
#   python3 -I base.py SPD SKQ > out/base.txt
import os, sys, datetime, json, pickle, collections, statistics
SPD, SKQ = sys.argv[1], sys.argv[2]
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp(); os.environ["FE_T0"] = str(T0)
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); sys.argv = ["x", SPD, "0.5"]
import float_exits as F, lib as L
RULE = dict(tp=3.0, hold=600, early=(30, 290, 1.5), sl=None)
W4 = L.W4
REAL0 = 793_100_000_000_000                                  # a pump.fun curve's real tokens at launch (raw, 6 decimals)
rows = F.rows
print(len(rows), "rows", collections.Counter(r["anchor"] for r in rows))
# wallet 4's 1.45+ SOL buys (routable or not) and all its landed transactions (slots from the file names)
allbuys = sorted(json.load(open(f"{SPD}/routable.json")), key=lambda r: r["t"])
w4slots = sorted(int(f.split("_")[0]) for f in os.listdir(f"{SPD}/w4tx") if f.endswith(".json"))
import bisect
def w4_own(key):
    """wallet 4's own trades of the coin in the path: (closed at t or None, its return in quote)."""
    m, tr = F.P[key]; bq = sq = bt = st = 0.0; closed = None
    for e in tr:
        if e["user"] != W4: continue
        if e["buy"]: bq += e["q"]; bt += e["tok"]
        else:
            sq += e["q"]; st += e["tok"]
            if closed is None and bt > 0 and st >= 0.98 * bt: closed = e["t"]
    return closed, (sq / bq - 1) if bq else 0.0
OUT = []
for r in rows:
    key = r["key"]; m, tr = F.P[key]
    k = next(i for i, e in enumerate(tr) if e["user"] == W4 and e["buy"] and e["slot"] == r["slot"])
    its = tr[k]; rate = r["sol"] * 1e9 / (its["q"] * (1 + its["bps"] / 1e4))
    before = [e for e in tr[:k] if e["slot"] == r["slot"]]
    f = dict(sol=r["sol"], anchor=r["anchor"], hops=r["hops"], how=r["how"], quote=r["quote"], frm=r["frm"], bps=its["bps"],
             progress=1 - its["real"] / REAL0 if its["real"] else 1.0, graduated=its["real"] == 0,
             mcap=its["vq"] / its["vt"] * 1e15 * rate / 1e9,                         # SOL, at the price its buy left
             impact=((its["vt"] + its["tok"]) / its["vt"]) ** 2 - 1,                   # how much its buy moved the price
             share=its["tok"] / (its["vt"] + its["tok"]),
             nslot_before=len(before), nslot_sell_before=sum(1 for e in before if not e["buy"]),
             slot_buysol_before=sum(e["q"] for e in before if e["buy"]) * rate / 1e9,
             slot_users_before=len({e["user"] for e in before}),
             hour=datetime.datetime.fromtimestamp(r["t"], datetime.timezone.utc).hour,
             wday=datetime.datetime.fromtimestamp(r["t"] + 7200, datetime.timezone.utc).weekday())
    prev = [b for b in allbuys if b["t"] < r["t"]]
    f["w4_big_10m"] = sum(1 for b in prev if r["t"] - b["t"] <= 600)
    f["w4_big_60m"] = sum(1 for b in prev if r["t"] - b["t"] <= 3600)
    last20 = [b["sol"] for b in prev[-20:]]
    f["size_vs_recent"] = r["sol"] / statistics.median(last20) if last20 else 1.0
    f["coin_seen_before"] = any(b["mint8"] == r["mint8"] for b in prev)
    f["mins_since_last_big"] = (r["t"] - prev[-1]["t"]) / 60 if prev else 999
    i = bisect.bisect_left(w4slots, r["slot"]); f["w4_tx_1500slots"] = i - bisect.bisect_left(w4slots, r["slot"] - 1500)
    rec = dict(key=key, slot=r["slot"], t=r["t"], mint=m, mint8=r["mint8"], anchor=r["anchor"], f=f, res={}, pxin={})
    for n in L.LAND:
        p = F.PREP[key, n]; rec["res"][n] = L.model(p, 0.5, **RULE)
        vt0 = p["ent"][0]; rec["pxin"][n] = (its["vt"] / vt0) ** 2
    rec["w4own"] = w4_own(key)
    OUT.append(rec)
# what the bot could know from earlier copyable buys at time t: each one's paper result (every copy, landing 4)
# once it has closed, and wallet 4's own result on a coin once it has sold out of it
for rec in OUT:
    t = rec["t"]
    done = sorted([(q["t"] + q["res"][4][2], q) for q in OUT if q["t"] < t and q["res"][4][1] != "refused" and q["t"] + q["res"][4][2] < t], key=lambda x: x[0])
    last = [q["res"][4] for _, q in done[-10:]]
    rec["f"]["paper_last10_net"] = sum(x[0] for x in last) if last else 0.0
    rec["f"]["paper_last10_tp"] = sum(1 for x in last if x[1] == "tp")
    w = sorted([(q["w4own"][0], q["w4own"][1]) for q in OUT if q["t"] < t and q["w4own"][0] is not None and q["w4own"][0] < t])
    rec["f"]["w4_last10_ret"] = statistics.mean(x[1] for x in w[-10:]) if w else 0.0
pickle.dump(OUT, open(f"{SKQ}/base.pkl", "wb"))
# the baseline run, F.sim against the cached results
CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
for n in L.LAND:
    a = sum(x[1] for x in F.sim(rows, n, RULE, caps=CAPS)); print(f"landing {n}: F.sim net {a:+.4f}")
print("saved", len(OUT))
