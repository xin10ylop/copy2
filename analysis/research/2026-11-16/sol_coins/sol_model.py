# Wallet 4's 1.3+ SOL buys of SOL-priced coins, copied with the live setup (the owner, Nov 16: "study now"). Each coin
# from its path (paths.py): our buy N trades after its own (4 / 8 / the next slot), refused past 1.25x the price its
# buy left, straight from the curve with SOL (no hop), then tp 4.0, its sale followed 30-290 s under 1.5x,
# sell_pressure [5, 60, 30], stall 180 s, 600 s; 0.5 SOL, 0.0026 SOL a round trip. Every copy (no slot limit), by its
# buy size, by block (A to Oct 29 12:02 UTC, B to Nov 6 05:32, C to Nov 15 13:04, D after: the days no study used),
# launch buys apart; against wallet 4's own result on the same coins.
#   python3 -I sol_model.py SOLQ PATHS > out/sol_model.txt
import sys, os, json, gzip, datetime, collections, random
import numpy as np
SOLQ, PATHS = sys.argv[1], sys.argv[2]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); import lib as L
ME = "Eao8T2Pk2aDzPWUFCA8si7oWd5ndFKfnX3HjYMpERst6"; OURS = {L.W4, ME}
TB = L.T_STOP; TC = datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp(); TD = datetime.datetime(2026, 11, 15, 13, 4, tzinfo=datetime.timezone.utc).timestamp()
blk = lambda t: "A" if t < TB else "B" if t < TC else "C" if t < TD else "D"
files = {f.split(".")[0]: f for f in os.listdir(PATHS)}
ROWS, PREP, EX = [], {}, {}
for c in json.load(open(f"{SOLQ}/sol_buys.json")):
    if c["sol"] < 1.3: continue
    key = f"{c['slot']}_{c['mint']}"
    if key not in files: continue
    tr = json.load(gzip.open(f"{PATHS}/{files[key]}"))
    k = next((i for i, e in enumerate(tr) if e["user"] == L.W4 and e["buy"] and e["slot"] == c["slot"]), None)
    if k is None: continue
    r = dict(slot=c["slot"], sol=c["sol"], hops=1, key=key, t=c["t"], c=c); P = {key: (c["mint"], tr)}
    ok = True
    for n in L.LAND:
        p = L.prep(r, P, n)
        if p is None: ok = False; break
        p["rate"] = 1.0                                       # SOL coin: lamports in, lamports out
        rest = tr[len(tr) - len(p["px"]):]; j = len(tr) - len(p["px"]) - 1
        other = np.array([e["user"] not in OURS for e in rest], dtype=bool); sell = np.array([not e["buy"] for e in rest], dtype=bool) & other
        PREP[key, n] = p; EX[key, n] = dict(sell=sell, buy=other & ~sell, pin=(tr[k]["vt"] / tr[j]["vt"]) ** 2)
    if ok: ROWS.append(r)
ROWS.sort(key=lambda r: r["t"])
def trig(p, x):
    age = p["age"]
    if not len(age): return None, None
    px = p["px"] / x["pin"]; lo = np.searchsorted(age, age - 60, side="left")
    s = np.concatenate([[0], np.cumsum(x["sell"])]); b = np.concatenate([[0], np.cumsum(x["buy"])])
    pr = L.first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= 5) & (age >= 30))
    pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); last = np.maximum.accumulate(np.where(newhi, age, -1e9))
    return pr, L.first((pk >= 1.0) & (age - last >= 180))
def model(p, x, stake=0.5, tp=4.0, hold=600, early=(30, 290, 1.5), signals=True):
    if p["refused"]: return (-0.0004, "refused", 0)
    base = L.model(p, stake, tp, hold, early, None)
    if not signals: return base
    pr, st = trig(p, x); t = [(i, w) for i, w in ((pr, "sell_pressure"), (st, "stall")) if i is not None]
    if not t: return base
    i, why = min(t)
    if p["age"][i] >= hold: return base
    ex = min(i + 1, len(p["px"]) - 1)
    if p["age"][ex] > base[2] or (p["age"][ex] == base[2] and base[1] != "time"): return base
    vt0, vq0, bps0 = p["ent"]; Q = stake * 1e9 * p["hopf"] / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq_r = p["vq"][ex] + net_in; vt_r = p["vt"][ex] * p["vq"][ex] / vq_r; out = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - p["bps"][ex] / 1e4)
    return (out * p["rate"] * p["hopf"] / 1e9 - stake - 0.0026, why, int(p["age"][ex]))
def every(rows, **kw):
    v = []
    for r in rows:
        res = [model(PREP[r["key"], n], EX[r["key"], n], **kw) for n in L.LAND]
        v.append(dict(r=r, net=sum(q[0] for q in res) / 3, why=res[0][1], refused=res[0][1] == "refused"))
    return v
def show(nm, v):
    if not v: return f"   {nm:44s}:    0"
    nets = sorted((q["net"] for q in v), reverse=True); c = [q for q in v if not q["refused"]]
    b = {k: sum(q["net"] for q in v if blk(q["r"]["t"]) == k) for k in "ABCD"}
    its = [q["r"]["c"] for q in v if q["r"]["c"]["nsells"]]
    itsp = 100 * sum(x["sell_sol"] - x["buy_sol"] for x in its) / max(1e-9, sum(x["buy_sol"] for x in its))
    return (f"   {nm:44s}: {len(v):4d} buys, {len(c):4d} copied | net {sum(nets):+7.2f} SOL, {100 * sum(nets) / max(1, len(c)) / 0.5:+6.1f}% a copy, won {100 * sum(1 for q in c if q['net'] > 0) / max(1, len(c)):4.1f}%,"
            f" tp {sum(1 for q in c if q['why'] == 'tp')} | w/o best 5 {sum(nets[5:]):+7.2f} | A {b['A']:+6.2f} B {b['B']:+6.2f} C {b['C']:+6.2f} D {b['D']:+6.2f} | wallet 4 on them {itsp:+5.1f}%")
f = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d %H:%M")
print(f"{len(ROWS)} SOL-priced coins with a first buy of 1.3+ SOL and a path, {f(ROWS[0]['t'])} to {f(ROWS[-1]['t'])} UTC; blocks " + " / ".join(f"{k} {sum(1 for r in ROWS if blk(r['t']) == k)}" for k in "ABCD"))
V = every(ROWS)
print("== every copy, the live setup (mean of three landings)")
print(show("all", V))
for lo, hi in ((1.3, 1.5), (1.5, 2.0), (2.0, 3.0), (3.0, 99)): print(show(f"its buy {lo}-{hi} SOL", [q for q in V if lo <= q["r"]["sol"] < hi]))
print(show("launch buys (under 1% of the curve sold before)", [q for q in V if q["r"]["c"]["sold_before"] < 0.01]))
print(show("later buys", [q for q in V if q["r"]["c"]["sold_before"] >= 0.01]))
print("== other exits on the same copies (all)")
for nm, kw in (("tp 4, 600 s, its early sale, no signals", dict(signals=False)), ("tp 3, live otherwise", dict(tp=3.0)), ("tp 2, live otherwise", dict(tp=2.0)),
               ("its sale never followed, signals on", dict(early=None)), ("timer 300 s", dict(hold=300))):
    print(show(nm, every(ROWS, **kw)))
x = np.array([q["net"] for q in V if not q["refused"]]); random.seed(7)
dr = sorted(np.mean(np.random.default_rng(i).choice(x, len(x))) for i in range(2000))
print(f"== the mean a copy when the copies are drawn again: 5% {100 * dr[100] / 0.5:+.1f}%, median {100 * dr[1000] / 0.5:+.1f}%, 95% {100 * dr[1900] / 0.5:+.1f}% (the copies we copy now: +13.6% a copy)")
