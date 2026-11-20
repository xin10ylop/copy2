# The sell-pressure audit (Nov 20): on every coin of f1_paths.py (wallet 4's token-coin buys of 1.3+ SOL since the exit was
# frozen, Nov 15 19:29 UTC: data the live exit was never picked on), our copy at 1 SOL, landing in the slot after its buy
# (the bot fills there: "seen at its slot +0", filled the next), refused over 1.5x its price (max_premium 0.5), and every
# exit variant. The live exit: take profit 4x its price, 600 s from its buy, sell pressure = 5+ more sells than buys by the
# other traders over the last 60 s from 30 s on, stall = no new high for 180 s once the price has been at our fill, its
# early sale (30-290 s under 1.5x) followed; the coin's graduation sells. A trigger sells on the coin's next trade.
# 0.0345 SOL a round trip (the convention), 0.0004 a refused buy. Halves by time; without each set's best 2%.
#   LK=SP/lk python3 -I e1_exits.py SP > out/e1_exits.txt
import sys, os, json, gzip, numpy as np, datetime as dt
SP = sys.argv[1]; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; LK = os.environ["LK"]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt"); import hunt_lib as H
STAKE, COST = 1.0, 0.0345 - 0.0026
coins = json.load(open(f"{SP}/w4since/coins.json"))
def first(m):
    i = np.flatnonzero(m); return int(i[0]) if len(i) else None
def prep(c):
    f = f"{LK}/paths/{c['slot']}_{c['m']}.json.gz"
    if not os.path.exists(f): return None
    tr = json.load(gzip.open(f))
    k = next((i for i, e in enumerate(tr) if e["user"] == W4 and e["buy"] and e["slot"] == c["slot"]), None)
    if k is None: return None
    p = H.prep(tr, k, c["rate"], "slot+1", pmax=1.5)
    if p["refused"] or not len(p["px"]): return dict(refused=True, t=c["t"], m=c["m"], sol=c["its_sol"])
    vt0, vq0, b0 = p["ent"]; Q = STAKE * 1e9 / c["rate"]; net_in = Q * 1e4 / (1e4 + b0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq_r = p["vq"] + net_in; vt_r = p["vt"] * p["vq"] / vq_r
    p["val"] = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - p["bps"] / 1e4) * c["rate"] / 1e9 - STAKE - 0.0026 - COST
    p["prem"] = (tr[k]["vt"] / vt0) ** 2; p["t"] = c["t"]; p["m"] = c["m"]; p["sol"] = c["its_sol"]; p["refused"] = False
    return p
def exit_value(p, tp=4.0, hold=600, sp=(5, 60, 30), sp_below=False, stall=180, its="early"):
    if p["refused"]: return -0.0004
    px, age, n = p["px"], p["age"], len(p["px"]); BIG = 10 ** 9
    trig = lambda i: BIG if i is None else min(i + 1, n - 1); at = lambda i: BIG if i is None else i
    c = [at(first(p["grad"])), at(first(age >= hold)), n - 1]
    if tp: c.append(trig(first(px >= tp)))
    if sp:
        N, w, fr = sp; s = np.concatenate([[0], np.cumsum(p["osell"])]); b = np.concatenate([[0], np.cumsum(p["obuy"])])
        lo = np.searchsorted(age, age - w, side="left"); cond = ((s[1:] - s[lo]) - (b[1:] - b[lo]) >= N) & (age >= fr)
        if sp_below: cond &= px < p["prem"]
        c.append(trig(first(cond)))
    if stall:
        pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
        c.append(trig(first((pk >= p["prem"]) & (age - lasthi >= stall))))
    if its == "early": c.append(trig(first(p["sell"] & (age >= 30) & (age < 290) & (px < 1.5))))
    elif its == "always": c.append(trig(first(p["sell"])))
    return float(p["val"][min(c)])
ps = [p for p in map(prep, coins) if p is not None]; ps.sort(key=lambda p: p["t"])
print(f"{len(coins)} coins listed, {len(ps)} with a path ({sum(p['refused'] for p in ps)} refused at 1.5x); "
      f"{dt.datetime.fromtimestamp(ps[0]['t'], dt.UTC):%m-%d %H:%M} to {dt.datetime.fromtimestamp(ps[-1]['t'], dt.UTC):%m-%d %H:%M} UTC; 1 SOL a copy")
V = {"LIVE: sp 5/60 from 30 s, stall 180, its early sale": {},
     "no sell pressure": dict(sp=None),
     "no stall": dict(stall=0),
     "no sell pressure, no stall": dict(sp=None, stall=0),
     "sp 8/60": dict(sp=(8, 60, 30)), "sp 10/60": dict(sp=(10, 60, 30)), "sp 15/60": dict(sp=(15, 60, 30)),
     "sp 5/120": dict(sp=(5, 120, 30)), "sp 3/60": dict(sp=(3, 60, 30)), "sp 5/30": dict(sp=(5, 30, 30)),
     "sp 5/60 from 60 s": dict(sp=(5, 60, 60)), "sp 5/60 from 120 s": dict(sp=(5, 60, 120)),
     "sp only under our fill": dict(sp_below=True),
     "stall 120": dict(stall=120), "stall 240": dict(stall=240), "stall 300": dict(stall=300),
     "its sale always followed": dict(its="always"), "its sale always, no sp": dict(its="always", sp=None),
     "its sale always, no sp, no stall": dict(its="always", sp=None, stall=0), "its sale never": dict(its="never"),
     "tp 2": dict(tp=2.0), "tp 3": dict(tp=3.0), "no tp": dict(tp=None), "hold 300": dict(hold=300), "hold 900": dict(hold=900)}
h = len(ps) // 2
print(f"\n{'exit':45s} {'SOL':>8s} {'a copy':>8s} {'w/o best 2%':>11s} {'1st half':>9s} {'2nd half':>9s} {'won':>5s}")
res = {}
for name, kw in V.items():
    x = np.array([exit_value(p, **kw) for p in ps]); res[name] = x; k2 = max(1, round(0.02 * len(x)))
    print(f"{name:45s} {x.sum():+8.2f} {100 * x.mean() / STAKE:+7.1f}% {np.sort(x)[:-k2].sum():+11.2f} {x[:h].sum():+9.2f} {x[h:].sum():+9.2f} {int((x > 0).sum()):5d}")
# by day, live against no sell pressure
L, N0 = res["LIVE: sp 5/60 from 30 s, stall 180, its early sale"], res["no sell pressure"]
print("\nby UTC day: live | no sell pressure (copies)")
for d in sorted({dt.datetime.fromtimestamp(p["t"], dt.UTC).strftime("%m-%d") for p in ps}):
    ix = [i for i, p in enumerate(ps) if dt.datetime.fromtimestamp(p["t"], dt.UTC).strftime("%m-%d") == d]
    print(f"  {d}: {L[ix].sum():+6.2f} | {N0[ix].sum():+6.2f} ({len(ix)})")
# where the sell pressure fired, what it did against holding on (no sp, the rest live)
d = L - N0; fired = np.abs(d) > 1e-9
print(f"\nsell pressure changed the exit on {int(fired.sum())} of {len(ps)} copies: {d[fired].sum():+.2f} SOL "
      f"(helped {int((d > 1e-9).sum())}: {d[d > 1e-9].sum():+.2f}, hurt {int((d < -1e-9).sum())}: {d[d < -1e-9].sum():+.2f})")
# the leader against live, day by day and by thirds
A = res["its sale always, no sp"]
print("\nby UTC day: live | its sale always, no sp")
for d in sorted({dt.datetime.fromtimestamp(p["t"], dt.UTC).strftime("%m-%d") for p in ps}):
    ix = [i for i, p in enumerate(ps) if dt.datetime.fromtimestamp(p["t"], dt.UTC).strftime("%m-%d") == d]
    print(f"  {d}: {L[ix].sum():+6.2f} | {A[ix].sum():+6.2f} ({len(ix)})")
t3 = np.array_split(np.arange(len(ps)), 3)
print("thirds: " + "  ".join(f"{L[i].sum():+.2f} | {A[i].sum():+.2f}" for i in t3))
