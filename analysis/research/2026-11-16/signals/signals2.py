# Round 2 (the owner, Nov 15 evening: "test more than that, 40, 50, 60" and "also test timing, how fast it drops and
# rises, along with holders and who is buying and selling"). Same data, setup and scoring as signals.py (loader.py).
# On top of the live rule (tp 3.0 or 4.0 or none, 600 s, early 30-290 s under 1.5x):
#   trail   once the price reached a times our buy, sell when it is d under its high since our buy (d 40-70%)
#   fall    the price fell d from its high of the last w seconds (how fast it drops)
#   stall   once it reached a, no new high for T seconds (the rise has stopped)
#   insider a sell of s% of the supply by a wallet that did not buy after us (held from before: dev, snipers, early
#           buyers), or the same added up over 30 s
#   flipper the same by wallets that bought after us
#   sellers sellers outnumber buyers by k or more over the last w seconds
#   extend  how fast it rises: at the 600 s timer, if buyers brought X SOL or more net in the last 60 s, hold to 1200 s
#           (tp and the early sale still apply)
#   python3 -I signals2.py CQ ALL > out/signals2.txt
import sys, collections, itertools
import numpy as np
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from loader import *
for key_n, x in EX.items():                                 # who: did the seller buy after our entry?
    seen, ins = set(), np.zeros(len(x["user"]), dtype=bool)
    for i, u in enumerate(x["user"]):
        if x["sell"][i] and u not in seen: ins[i] = True
        if x["other"][i] and not x["sell"][i] and x["sol"][i] > 0: seen.add(u)
    x["ins"] = ins; x["buy"] = x["other"] & ~x["sell"] & (x["sol"] > 0)
def trigger(p, x, sig):
    kind, a, w, cap = sig; age, px = p["age"], p["px"] / x["pin"]; n = len(age)
    if n == 0: return None
    ok = age >= 30 if kind not in ("trail", "fall", "stall") else np.ones(n, dtype=bool)
    if cap: ok = ok & (px < cap)
    if kind == "trail":
        pk = np.maximum.accumulate(px); f = (pk >= a) & (px <= pk * (1 - w))
    elif kind == "fall":                                     # a = the fall, w = the window
        lo = np.searchsorted(age, age - w, side="left")
        f = np.array([px[i] <= px[lo[i]:i + 1].max() * (1 - a) for i in range(n)])
    elif kind == "stall":                                    # a = level, w = seconds without a new high
        pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]])
        last = np.maximum.accumulate(np.where(newhi, age, -1e9)); f = (pk >= a) & (age - last >= w)
    elif kind in ("insider", "flipper", "insum", "flipsum"):
        who = x["ins"] if kind in ("insider", "insum") else x["sell"] & ~x["ins"]
        if kind in ("insider", "flipper"): f = who & (x["tok"] >= a)
        else:
            lo = np.searchsorted(age, age - 30, side="left"); c = np.concatenate([[0], np.cumsum(np.where(who, x["tok"], 0))]); f = (c[1:] - c[lo]) >= a
    elif kind == "sellers":
        lo = np.searchsorted(age, age - w, side="left"); s = np.concatenate([[0], np.cumsum(x["sell"])]); b = np.concatenate([[0], np.cumsum(x["buy"])])
        f = (s[1:] - s[lo]) - (b[1:] - b[lo]) >= a
    return L.first(f & ok)
def model(p, x, stake, sig, tp):
    if p["refused"]: return (-0.0004, "refused", 0)
    hold = 600
    if sig and sig[0] == "extend":
        m = (p["age"] > 540) & (p["age"] <= 600)
        if (x["sol"][m].sum() if m.any() else 0) >= sig[1]: hold = 1200
        return L.model(p, stake, tp, hold, (30, 290, 1.5), None)
    base = L.model(p, stake, tp, hold, (30, 290, 1.5), None)
    if not sig: return base
    i = trigger(p, x, sig)
    if i is None or p["age"][i] >= hold: return base
    ex = min(i + 1, len(p["px"]) - 1)
    if p["age"][ex] > base[2] or (p["age"][ex] == base[2] and base[1] != "time"): return base
    vt0, vq0, bps0 = p["ent"]
    Q = stake * 1e9 * p["hopf"] / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq_r = p["vq"][ex] + net_in; vt_r = p["vt"][ex] * p["vq"][ex] / vq_r
    out = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - p["bps"][ex] / 1e4)
    return (out * p["rate"] * p["hopf"] / 1e9 - stake - 0.0026, "signal", int(p["age"][ex]))
def run(sig, tp, n, stake=0.5):
    out, open_ = [], []
    for r in ROWS:
        open_ = [y for y in open_ if y[0] > r["t"]]
        if len(open_) >= 2 or sum(1 for y in open_ if y[1] == r["anchor"]) >= CAPS[r["anchor"]]: continue
        net, why, held = model(PREP[r["key"], n], EX[r["key"], n], stake, sig, tp)
        if why != "refused": open_.append((r["t"] + held, r["anchor"]))
        out.append((r, net, why))
    return out
def score(sig, tp):
    tot, blocks, wo5, days, whys = 0, [0, 0, 0], 0, collections.defaultdict(float), collections.Counter()
    for n in L.LAND:
        res = run(sig, tp, n); v = sorted((y[1] for y in res), reverse=True)
        tot += sum(v) / 3; wo5 += sum(v[5:]) / 3
        for r, net, why in res: blocks[blk(r)] += net / 3; days[day(r["t"])] += net / 3; whys[why] += 1 / 3
    first, last = min(days), max(days); dv = sorted(y for k, y in days.items() if k not in (first, last))
    cum = hi = lo = 0.0
    for k in sorted(days): cum += days[k]; hi = max(hi, cum); lo = min(lo, cum - hi)
    return dict(tot=tot, b=blocks, wo5=wo5, neg=sum(1 for y in dv if y < 0), nd=len(dv), worst=dv[0], fall=lo, whys=whys)
SIGS = [("trail", a, d, None) for a in (1.2, 1.5, 2.0, 2.5, 3.0) for d in (0.4, 0.5, 0.6, 0.7)]
SIGS += [("fall", d, w, cap) for d in (0.2, 0.3, 0.4, 0.5) for w in (5, 10, 30, 60) for cap in (None, 1.5)]
SIGS += [("stall", a, T, None) for a in (1.0, 1.3, 1.5, 2.0) for T in (60, 120, 180, 300)]
SIGS += [(k, s, 0, cap) for k in ("insider", "flipper") for s in (0.01, 0.02, 0.03, 0.05) for cap in (None, 1.5)]
SIGS += [(k, s, 30, cap) for k in ("insum", "flipsum") for s in (0.03, 0.05, 0.08) for cap in (None, 1.5)]
SIGS += [("sellers", k, w, cap) for k in (3, 5, 10) for w in (10, 30, 60) for cap in (None, 1.5)]
SIGS += [("extend", X, 0, None) for X in (0.0, 1.0, 3.0)]
def lab(s, tp):
    t = "live" if s is None else {"trail": lambda: f"trail {s[2] * 100:.0f}% once {s[1]}x", "fall": lambda: f"falls {s[1] * 100:.0f}% within {s[2]} s",
         "stall": lambda: f"no new high {s[2]} s once {s[1]}x", "insider": lambda: f"holder from before sells {s[1] * 100:.0f}%+", "flipper": lambda: f"later buyer sells {s[1] * 100:.0f}%+",
         "insum": lambda: f"holders from before sell {s[1] * 100:.0f}%+ in 30 s", "flipsum": lambda: f"later buyers sell {s[1] * 100:.0f}%+ in 30 s",
         "sellers": lambda: f"{s[1]}+ more sellers than buyers in {s[2]} s", "extend": lambda: f"hold to 1200 s if +{s[1]:g} SOL net buying at 600 s"}[s[0]]()
    if s and s[3]: t += f", under {s[3]}x"
    return t + f" | tp {tp if tp else 'none'}"
TPS = (3.0, 4.0, None)
print(f"{len(ROWS)} buys (seven kinds, 1.3+ SOL, every fee tier); {len(SIGS)} signals x {len(TPS)} take profits; 0.5 SOL, 2 open; 600 s, early 30-290 s")
S = {}
for tp in TPS:
    S[lab(None, tp)] = ((None, tp), score(None, tp))
    for s in SIGS: S[lab(s, tp)] = ((s, tp), score(s, tp))
hdr = f"   {'rule':58s} | total  | A      B      C      | w/o best 5 | days<0 | worst | fall  | exits (a landing)"
row = lambda nm, s: f"   {nm:58s} | {s['tot']:+6.2f} | {s['b'][0]:+6.2f} {s['b'][1]:+6.2f} {s['b'][2]:+6.2f} | {s['wo5']:+6.2f}     | {s['neg']:2d}/{s['nd']} | {s['worst']:+5.2f} | {s['fall']:+5.2f} | " + " ".join(f"{w} {c:.0f}" for w, c in s["whys"].most_common())
L0 = S[lab(None, 3.0)][1]
print("== the live rule, and tp 4.0 / no tp alone\n" + hdr)
for tp in TPS: print(row(lab(None, tp), S[lab(None, tp)][1]))
print("== the 30 best by total\n" + hdr)
for nm, (k, s) in sorted(S.items(), key=lambda q: -q[1][1]["tot"])[:30]: print(row(nm, s))
print("== with tp 3.0, by family: settings ahead of live / all, the best, and the best on losing days")
for fam in ("trail", "fall", "stall", "insider", "flipper", "insum", "flipsum", "sellers", "extend"):
    xs = [(nm, s) for nm, (k, s) in S.items() if k[0] and k[0][0] == fam and k[1] == 3.0]
    b = max(xs, key=lambda q: q[1]["tot"]); c = min(xs, key=lambda q: (q[1]["neg"], -q[1]["tot"]))
    print(f"   {fam:8s}: {sum(1 for nm, s in xs if s['tot'] > L0['tot'])}/{len(xs)} ahead; best '{b[0]}' {b[1]['tot']:+.2f} (A {b[1]['b'][0]:+.2f} B {b[1]['b'][1]:+.2f} C {b[1]['b'][2]:+.2f}); fewest losing days '{c[0]}' {c[1]['neg']}/{c[1]['nd']}, {c[1]['tot']:+.2f}")
print("== trails, tp 3.0 (total)")
for a in (1.2, 1.5, 2.0, 2.5, 3.0): print(f"   once {a}x: " + "  ".join(f"{d * 100:.0f}% {S[lab(('trail', a, d, None), 3.0)][1]['tot']:+6.2f}" for d in (0.4, 0.5, 0.6, 0.7)))
print(f"   (live {L0['tot']:+.2f})")
print("== ahead of the live rule in all three blocks\n" + hdr)
for nm, (k, s) in sorted(S.items(), key=lambda q: -q[1][1]["tot"]):
    if k != (None, 3.0) and all(s["b"][i] > L0["b"][i] for i in range(3)): print(row(nm, s))
print("== picked on two blocks out of all of them, scored on the third (gain over live in the held-out block)")
gains = []
for held in range(3):
    other = [i for i in range(3) if i != held]
    rk = sorted(((nm, s) for nm, (k, s) in S.items() if k != (None, 3.0)), key=lambda q: -sum(q[1]["b"][i] for i in other))
    g = rk[0][1]["b"][held] - L0["b"][held]; gains.append(g)
    g10 = sum(s["b"][held] - L0["b"][held] for nm, s in rk[:10]) / 10
    print(f"   held out {'ABC'[held]}: picked '{rk[0][0]}' ({sum(rk[0][1]['b'][i] - L0['b'][i] for i in other):+.2f} on the other two) -> {g:+.2f}; the 10 best picks on average {g10:+.2f}")
print(f"   total out of sample: {sum(gains):+.2f} SOL")
