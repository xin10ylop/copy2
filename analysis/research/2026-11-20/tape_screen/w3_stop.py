# Would a stop loss help CqCAzte8's live exits? (Nov 23; the owner, after a -70% SOL-coin copy: "test if we should add a
# stop loss, because there is no sell pressure"). Every first buy of 0.5+ SOL (the coins' trades cached by w3_robust.py),
# the live exits: token coins tp 3x / 420 s / stall 240, SOL coins tp 2x / 120 s; refused over 1.5x. The stop as the bot
# has it (pos.rs exit_due_fill): the price at or under STOP x ITS buy price (not our fill), sold at the next trade. Each
# stop level in the 4 time blocks of its buys, % a copy at 1 SOL, and without the best 2% in SOL.
#   RPC_URL=... LK=SP/lk COST=0.0064 python3 -I w3_stop.py SP WALLET
import sys, os, numpy as np
SP, W = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [sys.argv[0], SP, W, "0", "0", "14"]
exec(open(os.path.join(HERE, "w2_grid.py")).read().split("firsts.sort(key=lambda c: c[\"t\"]); h = len(firsts) // 2")[0])
STOPS = [0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4]
def one(c, tr):
    k = next((i for i, e in enumerate(tr) if e["user"] == W and e["buy"] and e["slot"] == c["slot"]), None)
    if k is None: return None
    p = H.prep(tr, k, c["rate"], "slot+1", pmax=1e9)
    if not len(p["px"]): return None
    vt0, vq0, b0 = p["ent"]; prem = (tr[k]["vt"] / vt0) ** 2
    if prem > 1.5: return dict(t=c["t"], tok=c["tok"], v=np.full(len(STOPS), -0.0004), ref=True)
    Q = STAKE * 1e9 / c["rate"]; net_in = Q * 1e4 / (1e4 + b0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq_r = p["vq"] + net_in; vt_r = p["vt"] * p["vq"] / vq_r
    val = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - p["bps"] / 1e4) * c["rate"] / 1e9 - STAKE - COST
    px, age, n = p["px"], p["age"], len(p["px"]); BIG = 10 ** 9
    trig = lambda i: BIG if i is None else min(i + 1, n - 1); at = lambda i: BIG if i is None else i
    tp, hold, stall = (3.0, 420, 240) if c["tok"] else (2.0, 120, 0)
    pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
    base = min(trig(first(px >= tp)), at(first(age >= hold)), at(first(p["grad"])), n - 1,
               trig(first((pk >= prem) & (age - lasthi >= stall))) if stall else BIG)
    v = [val[min(base, trig(first(px <= s)) if s else BIG)] for s in STOPS]
    return dict(t=c["t"], tok=c["tok"], v=np.array(v), ref=False, low=float(px[:base + 1].min()), prem=prem)
firsts.sort(key=lambda c: c["t"])
rows = []
for i in range(0, len(firsts), 30):
    cs = firsts[i:i + 30]
    with cf.ThreadPoolExecutor(3) as ex: paths = list(ex.map(lambda c: M.path(c["m"], c["slot"], next((s for t, s in sigs if t >= c["t"] + 640), sigs[-1][1]), threads=8), cs))
    rows += [r for r in (one(c, tr) for c, tr in zip(cs, paths)) if r]
rows.sort(key=lambda r: r["t"])
if os.environ.get("DUMP"): import pickle; pickle.dump(rows, open(os.environ["DUMP"], "wb"))
def wo2(v):
    k = max(1, round(0.02 * len(v))); return v.sum() - np.sort(v)[-k:].sum()
print(f"{W[:8]}: {len(rows)} copies of its first buys of 0.5+ SOL ({sum(r['ref'] for r in rows)} refused over 1.5x); the live exits; 1 SOL a copy")
for kd, sel in (("token coins (tp 3x / 420 s / stall 240)", True), ("SOL coins (tp 2x / 120 s)", False)):
    R = [r for r in rows if r["tok"] == sel]; V = np.stack([r["v"] for r in R]); bl = np.array_split(np.arange(len(R)), 4)
    low = np.array([r.get("low", 1) for r in R if not r["ref"]])
    print(f"\n{kd}: {len(R)} copies; the lowest price before the exit (x its buy): under 0.9 on {np.mean(low < 0.9):.0%}, "
          f"under 0.7 on {np.mean(low < 0.7):.0%}, under 0.5 on {np.mean(low < 0.5):.0%}")
    print(f"  {'stop':>8s}  {'block 1':>8s} {'block 2':>8s} {'block 3':>8s} {'block 4':>8s}  {'all, % a copy':>14s} {'SOL':>8s} {'w/o 2%':>8s}")
    for j, s in enumerate(STOPS):
        print(f"  {('none' if not s else f'{s}x'):>8s}  " + " ".join(f"{100 * V[b, j].mean():+7.1f}%" for b in bl)
              + f"  {100 * V[:, j].mean():+13.1f}% {V[:, j].sum():+8.2f} {wo2(V[:, j]):+8.2f}")
