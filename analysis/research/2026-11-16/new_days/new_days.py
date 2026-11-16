# The frozen setup on wallet 4's newest days, never used in any study (the owner, Nov 16: "go", after "see what works
# and what doesn't"). The backtest data ends Nov 15 13:04 UTC; here wallet 4's own buys from then to the fetch (NEW =
# fetch_w4.py from Nov 15 12:00, the bot's scan with the seven floats at 1.3+ SOL, build_rows.py, model.py's paths),
# with the live setup (tp 4.0, 600 s, its sale 30-290 s under 1.5x, sell_pressure [5, 60, 30], stall 180 s), 0.5 SOL,
# every copy and the bot's run (2 open, caps), against the same on the backtest's 1,238 buys. The question: on its
# newest coins, does copying wallet 4 still make money? And: is our live result what the model says for these hours?
#   python3 -I new_days.py NEW CQ ALL > out/new_days.txt
import sys, os, datetime, collections, random
import numpy as np
NEW = sys.argv[1]
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "buy_pressure")); sys.argv = [sys.argv[0], sys.argv[2], sys.argv[3]]
import buy_pressure as BP
from buy_pressure import L, R3, rule
from round3 import ROWS as OLD, PREP as OP, EX as OE
CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1, "TTWofwAg": 1, "DJTu7vi8": 1, "98sMhvDw": 1, "XsbEhLAt": 1}
L.NAMES.update({"TTWofwAg": "TTWofwAg", "DJTu7vi8": "DJTu7vi8", "98sMhvDw": "98sMhvDw", "XsbEhLAt": "XsbEhLAt"})
OURS = {L.W4, "Eao8T2Pk2aDzPWUFCA8si7oWd5ndFKfnX3HjYMpERst6"}
T_END = datetime.datetime(2026, 11, 15, 13, 4, tzinfo=datetime.timezone.utc).timestamp()
T_LIVE = datetime.datetime(2026, 11, 15, 19, 29, 51, tzinfo=datetime.timezone.utc).timestamp()
rows, P, info = L.load(NEW, T_END)
ROWS, PREP, EX = [], {}, {}
for r in rows:
    if r["anchor"] not in CAPS or r["sol"] < 1.3: continue
    ps = [L.prep(r, P, n) for n in L.LAND]
    if any(p is None for p in ps): continue
    tr = P[r["key"]][1]; k = next(i for i, e in enumerate(tr) if e["user"] == L.W4 and e["buy"] and e["slot"] == r["slot"])
    for n, p in zip(L.LAND, ps):
        PREP[r["key"], n] = p; rest = tr[len(tr) - len(p["px"]):]; j = len(tr) - len(p["px"]) - 1
        other = np.array([e["user"] not in OURS for e in rest], dtype=bool); sell = np.array([not e["buy"] for e in rest], dtype=bool) & other
        EX[r["key"], n] = dict(sell=sell, buy=other & ~sell, pin=(tr[k]["vt"] / tr[j]["vt"]) ** 2)
    ROWS.append(r)
SIGS, TP, HOLD, E = rule()
f = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d %H:%M")
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
def every(rows, prep, ex):
    out = []
    for r in rows:
        p, x = prep[r["key"], 4], ex[r["key"], 4]
        if p["refused"]: continue
        net, why, held = R3.model(p, x, 0.5, SIGS, TP, HOLD, E)
        a = p["age"]; m = a <= 600; pk = p["px"][m].max() if m.any() else 1.0
        out.append(dict(r=r, pc=100 * net / 0.5, tp=why == "tp", x3=pk >= 3.0, x4=pk >= 4.0, x2=pk >= 2.0, its=L.first(p["sell"]) is not None))
    return out
def run(rows, prep, ex):
    tot = 0; days = collections.defaultdict(float); n_c = 0
    for n in L.LAND:
        open_ = []
        for r in rows:
            open_ = [y for y in open_ if y[0] > r["t"]]
            if len(open_) >= 2 or sum(1 for y in open_ if y[1] == r["anchor"]) >= CAPS[r["anchor"]]: continue
            net, why, held = R3.model(prep[r["key"], n], ex[r["key"], n], 0.5, SIGS, TP, HOLD, E)
            if why != "refused": open_.append((r["t"] + held, r["anchor"]))
            tot += net / 3; days[day(r["t"])] += net / 3; n_c += 1 / 3
    return tot, days, n_c
def show(nm, v):
    pc = np.array([q["pc"] for q in v])
    return (f"   {nm:44s}: {len(v):4d} copies | {pc.mean():+6.1f}% a copy (median {np.median(pc):+6.1f}%) | won {100 * np.mean(pc > 0):4.1f}% | "
            f"reached 2x {100 * np.mean([q['x2'] for q in v]):4.1f}%, 3x {100 * np.mean([q['x3'] for q in v]):4.1f}%, 4x {100 * np.mean([q['x4'] for q in v]):4.1f}% within 600 s | take profits {sum(q['tp'] for q in v)}")
print(f"NEW: {len(ROWS)} copyable buys of 1.3+ SOL with a path, {f(ROWS[0]['t'])} to {f(ROWS[-1]['t'])} UTC; kinds {dict(collections.Counter(r['anchor'] for r in ROWS))}; load {info}")
hrs = (ROWS[-1]["t"] - ROWS[0]["t"]) / 3600
OLDV, NEWV = every(OLD, OP, OE), every(ROWS, PREP, EX)
print("== every copy (landing 4)")
print(show("the backtest, Oct 21 - Nov 15 13:04 UTC", OLDV))
for nm, lo, hi in (("the backtest's last 5 days (Nov 10-15)", datetime.datetime(2026, 11, 10, tzinfo=datetime.timezone.utc).timestamp(), T_END),):
    print(show(nm, [q for q in OLDV if lo <= q["r"]["t"] < hi]))
print(show("NEW: Nov 15 13:04 UTC on", NEWV))
print(show("NEW, before the frozen setup went live (19:29)", [q for q in NEWV if q["r"]["t"] < T_LIVE]))
print(show("NEW, since the frozen setup went live", [q for q in NEWV if q["r"]["t"] >= T_LIVE]))
x = np.array([q["pc"] for q in OLDV]); n = len(NEWV)
if n >= 10:
    w = np.array([x[i:i + n].mean() for i in range(len(x) - n + 1)])
    print(f"   runs of {n} consecutive copies in the backtest at {np.mean([q['pc'] for q in NEWV]):+.1f}% a copy or worse: {100 * np.mean(w <= np.mean([q['pc'] for q in NEWV])):.1f}%")
print("== the bot's run (2 open, caps), mean of three landings")
tot, days, nc = run(ROWS, PREP, EX)
print(f"   NEW: {nc:.0f} copies in {hrs:.1f} hours ({24 * nc / max(hrs, 1e-9):.1f} a day), net {tot:+.2f} SOL ({24 * tot / max(hrs, 1e-9):+.2f} a day); the backtest made +3.14 a day, 43 copies a day")
for k in sorted(days): print(f"      {k} (Beirut): {days[k]:+.2f} SOL")
live = [q for q in NEWV if q["r"]["t"] >= T_LIVE]
lt, ld, ln = run([r for r in ROWS if r["t"] >= T_LIVE], PREP, EX)
print(f"   since the frozen setup went live: the model's run {ln:.0f} copies, {lt:+.2f} SOL (our real 27 closed #38-#65: -1.0680 SOL)")
