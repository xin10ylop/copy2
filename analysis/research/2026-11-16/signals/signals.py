# Sell on what the other holders do (the owner, Nov 15 evening: "analyze top 10 holders, if they sell, these
# things"). The paths start at wallet 4's buy, so a holder's whole bag is not known; what is known is every trade on
# the curve after it: who, buy or sell, how many tokens, how much SOL. A pump coin has 1,000,000,000 tokens; a
# top-10 holder of a young coin holds about 1-4% of them, so "a sell of 2%+ of the supply" is a top holder selling.
# Signals, each checked on every trade after our buy (wallet 4's own trades and ours left out; the sale on the trade
# after the signal, as the early sale and tp):
#   big     a sell of s% of the supply or more (a top holder dumping)
#   bigsum  sells of s% of the supply or more within w seconds, added up
#   cluster k different sellers within w seconds
#   flow    the coin's net SOL (buys - sells) over the last w seconds at -X SOL or worse
#   drain   sells minus buys since our buy at X SOL or more
#   each from age 0 or only after 30 s, and either at any price or only while under 1.5x (a winner keeps running)
# On top of the live rule (tp 3.0, 600 s, early 30-290 s under 1.5x). The setup and data as ../trail/trail.py: seven
# kinds, 1.3+ SOL, every fee tier, 2 open, caps; 0.5 SOL; mean of three landings; blocks A / B / C; picked on two
# blocks, scored on the third.
#   python3 -I signals.py CQ ALL > out/signals.txt
import sys, datetime, collections, itertools
import numpy as np
CQ, ALL = sys.argv[1], sys.argv[2]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); import lib as L
CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1, "TTWofwAg": 1, "DJTu7vi8": 1, "98sMhvDw": 1}
OURS = {L.W4, "Eao8T2Pk2aDzPWUFCA8si7oWd5ndFKfnX3HjYMpERst6"}
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp()
TB = L.T_STOP; TC = datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp()
blk = lambda r: 0 if r["t"] < TB else 1 if r["t"] < TC else 2
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
PREP, EX, ROWS = {}, {}, []
for SPD, lo, hi in ((ALL, 1.45, 1e9), (CQ, 1.3, 1.45)):
    rows, P, info = L.load(SPD, T0)
    for r in rows:
        if r["anchor"] not in CAPS or not (lo <= r["sol"] < hi): continue
        ps = [L.prep(r, P, n) for n in L.LAND]
        if any(p is None for p in ps): continue
        m, tr = P[r["key"]]
        k = next(i for i, e in enumerate(tr) if e["user"] == L.W4 and e["buy"] and e["slot"] == r["slot"])
        for n, p in zip(L.LAND, ps):
            PREP[r["key"], n] = p
            rest = tr[len(tr) - len(p["px"]):]               # the trades lib.prep keeps after our entry
            j = len(tr) - len(p["px"]) - 1
            other = np.array([e["user"] not in OURS for e in rest], dtype=bool)
            EX[r["key"], n] = dict(other=other, sell=np.array([not e["buy"] for e in rest], dtype=bool) & other,
                                   tok=np.array([e["tok"] / 1e15 for e in rest]),
                                   sol=np.array([e["q"] * p["rate"] / 1e9 * (1 if e["buy"] else -1) for e in rest]) * other,
                                   user=[e["user"] for e in rest], pin=(tr[k]["vt"] / tr[j]["vt"]) ** 2)
        ROWS.append(r)
ROWS.sort(key=lambda r: r["t"])
def trigger(p, x, sig):
    """index of the first trade where the signal fires, or None."""
    kind, a, w, age0, cap = sig; age = p["age"]; n = len(age)
    if n == 0: return None
    ok = (age >= age0) & ((p["px"] < cap * x["pin"]) if cap else True)
    if kind == "big": f = x["sell"] & (x["tok"] >= a)
    elif kind == "drain": f = np.cumsum(x["sol"]) <= -a
    else:
        lo = np.searchsorted(age, age - w, side="left"); f = np.zeros(n, dtype=bool)
        if kind == "flow":
            c = np.concatenate([[0], np.cumsum(x["sol"])]); f = (c[1:] - c[lo]) <= -a
        elif kind == "bigsum":
            c = np.concatenate([[0], np.cumsum(np.where(x["sell"], x["tok"], 0))]); f = (c[1:] - c[lo]) >= a
        elif kind == "cluster":
            idx = np.nonzero(x["sell"])[0]
            for i in idx:
                if len({x["user"][q] for q in idx if lo[i] <= q <= i}) >= a: f[i] = True; break
    return L.first(f & ok)
def model(p, x, stake, sig, tp=3.0, hold=600, early=(30, 290, 1.5)):
    if p["refused"]: return (-0.0004, "refused", 0)
    if sig is None: return L.model(p, stake, tp, hold, early, None)
    i = trigger(p, x, sig)
    if i is None: return L.model(p, stake, tp, hold, early, None)
    base = L.model(p, stake, tp, hold, early, None)            # the live exit; the signal only if it comes first
    if p["age"][min(i + 1, len(p["age"]) - 1)] >= base[2] and base[1] != "time" or p["age"][i] >= hold: return base
    if base[1] == "time" and p["age"][i] >= base[2]: return base
    vt0, vq0, bps0 = p["ent"]
    Q = stake * 1e9 * p["hopf"] / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    ex = min(i + 1, len(p["px"]) - 1)
    vq_r = p["vq"][ex] + net_in; vt_r = p["vt"][ex] * p["vq"][ex] / vq_r
    out = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - p["bps"][ex] / 1e4)
    return (out * p["rate"] * p["hopf"] / 1e9 - stake - 0.0026, "signal", int(p["age"][ex]))
def run(sig, n, stake=0.5):
    out, open_ = [], []
    for r in ROWS:
        open_ = [y for y in open_ if y[0] > r["t"]]
        if len(open_) >= 2 or sum(1 for y in open_ if y[1] == r["anchor"]) >= CAPS[r["anchor"]]: continue
        net, why, held = model(PREP[r["key"], n], EX[r["key"], n], stake, sig)
        if why != "refused": open_.append((r["t"] + held, r["anchor"]))
        out.append((r, net, why))
    return out
def score(sig):
    tot, blocks, wo5, days, whys = 0, [0, 0, 0], 0, collections.defaultdict(float), collections.Counter()
    for n in L.LAND:
        res = run(sig, n); v = sorted((y[1] for y in res), reverse=True)
        tot += sum(v) / 3; wo5 += sum(v[5:]) / 3
        for r, net, why in res: blocks[blk(r)] += net / 3; days[day(r["t"])] += net / 3; whys[why] += 1 / 3
    first, last = min(days), max(days); dv = sorted(y for k, y in days.items() if k not in (first, last))
    cum = hi = lo = 0.0
    for k in sorted(days): cum += days[k]; hi = max(hi, cum); lo = min(lo, cum - hi)
    return dict(tot=tot, b=blocks, wo5=wo5, neg=sum(1 for y in dv if y < 0), nd=len(dv), worst=dv[0], fall=lo, whys=whys)
SIGS = []
for age0, cap in itertools.product((0, 30), (None, 1.5)):
    SIGS += [("big", s, 0, age0, cap) for s in (0.01, 0.02, 0.03, 0.05)]
    SIGS += [("bigsum", s, w, age0, cap) for s in (0.03, 0.05, 0.08) for w in (10, 30)]
    SIGS += [("cluster", k, w, age0, cap) for k in (3, 5, 8) for w in (10, 30)]
    SIGS += [("flow", X, w, age0, cap) for X in (1.0, 2.0, 4.0) for w in (10, 30, 60)]
    SIGS += [("drain", X, 0, age0, cap) for X in (1.0, 3.0, 6.0)]
def lab(s):
    if s is None: return "live (no signal)"
    kind, a, w, age0, cap = s
    t = {"big": f"a sell of {a * 100:.0f}%+ of supply", "bigsum": f"{a * 100:.0f}%+ of supply sold in {w} s", "cluster": f"{a}+ sellers in {w} s",
         "flow": f"net flow -{a:g} SOL in {w} s", "drain": f"sells - buys {a:g} SOL since ours"}[kind]
    return t + (f", after {age0} s" if age0 else "") + (f", under {cap}x" if cap else "")
print(f"{len(ROWS)} buys (seven kinds, 1.3+ SOL, every fee tier); {len(SIGS)} signals; 0.5 SOL, 2 open; on top of tp 3.0, 600 s, early 30-290 s")
S = {lab(None): (None, score(None))}
for s in SIGS: S[lab(s)] = (s, score(s))
hdr = f"   {'rule':48s} | total  | A      B      C      | w/o best 5 | days<0 | worst | deepest fall | exits (a landing)"
row = lambda nm, s: f"   {nm:48s} | {s['tot']:+6.2f} | {s['b'][0]:+6.2f} {s['b'][1]:+6.2f} {s['b'][2]:+6.2f} | {s['wo5']:+6.2f}     | {s['neg']:2d}/{s['nd']} | {s['worst']:+5.2f} | {s['fall']:+5.2f}        | " + " ".join(f"{w} {c:.0f}" for w, c in s["whys"].most_common())
L0 = S[lab(None)][1]
print("== the live rule\n" + hdr + "\n" + row(lab(None), L0))
print("== the 25 best by total\n" + hdr)
for nm, (k, s) in sorted(S.items(), key=lambda q: -q[1][1]["tot"])[:25]: print(row(nm, s))
print("== ahead of the live rule in all three blocks\n" + hdr)
for nm, (k, s) in sorted(S.items(), key=lambda q: -q[1][1]["tot"]):
    if k and all(s["b"][i] > L0["b"][i] for i in range(3)): print(row(nm, s))
print("== the 10 with the fewest losing days (then the smallest fall)\n" + hdr)
for nm, (k, s) in sorted(S.items(), key=lambda q: (q[1][1]["neg"], -q[1][1]["fall"]))[:10]: print(row(nm, s))
print("== by family: the best of each and how many of its settings beat the live rule")
for fam in ("big", "bigsum", "cluster", "flow", "drain"):
    xs = [(nm, s) for nm, (k, s) in S.items() if k and k[0] == fam]
    b = max(xs, key=lambda q: q[1]["tot"])
    print(f"   {fam:8s}: {sum(1 for nm, s in xs if s['tot'] > L0['tot'])} of {len(xs)} ahead; best '{b[0]}' {b[1]['tot']:+.2f}")
print("== picked on two blocks, scored on the third (the gain over the live rule in the held-out block)")
gains = []
for held in range(3):
    other = [i for i in range(3) if i != held]
    rk = sorted(((nm, s) for nm, (k, s) in S.items() if k), key=lambda q: -sum(q[1]["b"][i] for i in other))
    g = rk[0][1]["b"][held] - L0["b"][held]; gains.append(g)
    g10 = sum(s["b"][held] - L0["b"][held] for nm, s in rk[:10]) / 10
    print(f"   held out {'ABC'[held]}: picked '{rk[0][0]}' ({sum(rk[0][1]['b'][i] - L0['b'][i] for i in other):+.2f} on the other two) -> {g:+.2f} on {'ABC'[held]}; the 10 best picks on average {g10:+.2f}")
print(f"   total out of sample: {sum(gains):+.2f} SOL")
