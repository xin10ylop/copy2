# A trailing stop (the owner, Nov 15 evening, watching #36 GGSWz3uu peak at 2.56x and fall to 1.42x: "manually I
# would have sold it by now"): once the price has reached `a` times OUR buy price, sell when it falls `d` under its
# high since our buy (the sale on the trade after the trigger, as tp and the early sale). On top of the live rule
# (tp 3.0, 600 s, early 30-290 s under 1.5x), with tp 3.0 / 4.0 / none and a 600 or 1200 s timer.
# The setup live since Nov 15 15:14 UTC: seven kinds (SOL, WBTC, PUMP, SPCX, TTWO, DJT, HYPE), min_sol 1.3 (1.45+ from
# ALL, 1.3-1.45 from CQ, as decomp/hype.py), every fee tier, 2 open, one at a time from SOL and each float but WBTC (2).
# 0.5 SOL; each figure the mean of the three landings. Blocks A (to Oct 29 12:02 UTC), B (to Nov 6 05:32), C (after).
# The honest test: pick the best trail on two blocks, score it on the third.
#   python3 -I trail.py CQ ALL > out/trail.txt
import sys, datetime, collections, itertools
CQ, ALL = sys.argv[1], sys.argv[2]
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); import lib as L
CAPS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1, "TTWofwAg": 1, "DJTu7vi8": 1, "98sMhvDw": 1}
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp()
TB = L.T_STOP; TC = datetime.datetime(2026, 11, 6, 5, 32, tzinfo=datetime.timezone.utc).timestamp()
blk = lambda r: 0 if r["t"] < TB else 1 if r["t"] < TC else 2
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
def pin(r, P, n):                                            # our buy price in its-price units (lib.prep's px_in)
    m, tr = P[r["key"]]
    k = next(i for i, e in enumerate(tr) if e["user"] == L.W4 and e["buy"] and e["slot"] == r["slot"])
    j = k + len([e for e in tr[k + 1:] if e["slot"] <= tr[k]["slot"] + 1]) if n == "slot+1" else min(k + n, len(tr) - 1)
    return (tr[k]["vt"] / tr[j]["vt"]) ** 2
PREP, PIN, ROWS = {}, {}, []
for SPD, lo, hi in ((ALL, 1.45, 1e9), (CQ, 1.3, 1.45)):
    rows, P, info = L.load(SPD, T0)
    for r in rows:
        if r["anchor"] not in CAPS or not (lo <= r["sol"] < hi): continue
        ps = [L.prep(r, P, n) for n in L.LAND]
        if any(p is None for p in ps): continue
        for n, p in zip(L.LAND, ps): PREP[r["key"], n] = p; PIN[r["key"], n] = pin(r, P, n)
        ROWS.append(r)
ROWS.sort(key=lambda r: r["t"])
def run(rule, n, rs=ROWS, stake=0.5):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x[0] > r["t"]]
        if len(open_) >= 2 or sum(1 for x in open_ if x[1] == r["anchor"]) >= CAPS[r["anchor"]]: continue
        kw = dict(rule); tr = kw.pop("trail")
        if tr: kw["trail"] = (tr[0] * PIN[r["key"], n], tr[1])
        net, why, held = L.model(PREP[r["key"], n], stake, **kw)
        if why != "refused": open_.append((r["t"] + held, r["anchor"]))
        out.append((r, net, why))
    return out
def score(rule):
    tot, blocks, wo5, days, whys = 0, [0, 0, 0], 0, collections.defaultdict(float), collections.Counter()
    for n in L.LAND:
        res = run(rule, n); v = sorted((x[1] for x in res), reverse=True)
        tot += sum(v) / 3; wo5 += sum(v[5:]) / 3
        for r, net, why in res: blocks[blk(r)] += net / 3; days[day(r["t"])] += net / 3; whys[why] += 1 / 3
    first, last = min(days), max(days); dv = sorted(x for k, x in days.items() if k not in (first, last))
    cum = hi = lo = 0.0
    for k in sorted(days): cum += days[k]; hi = max(hi, cum); lo = min(lo, cum - hi)
    return dict(tot=tot, b=blocks, wo5=wo5, neg=sum(1 for x in dv if x < 0), nd=len(dv), worst=dv[0], fall=lo, whys=whys)
LIVE = dict(tp=3.0, hold=600, early=(30, 290, 1.5), sl=None, trail=None)
GRID = [dict(LIVE, tp=tp, hold=h, trail=(a, d)) for tp, h, a, d in itertools.product((3.0, 4.0, None), (600, 1200), (1.2, 1.3, 1.5, 1.75, 2.0, 2.5), (0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5))]
GRID += [dict(LIVE, tp=tp, hold=h) for tp, h in ((4.0, 600), (None, 600), (3.0, 1200))]
lab = lambda k: (f"trail {int(k['trail'][1] * 100)}% once {k['trail'][0]}x, " if k["trail"] else "no trail, ") + (f"tp {k['tp']}" if k["tp"] else "no tp") + f", {k['hold']} s"
print(f"{len(ROWS)} buys (seven kinds, 1.3+ SOL, every fee tier), {datetime.datetime.fromtimestamp(ROWS[0]['t'], datetime.timezone.utc):%m-%d} to {datetime.datetime.fromtimestamp(ROWS[-1]['t'], datetime.timezone.utc):%m-%d %H:%M} UTC; {len(GRID) + 1} rules; 0.5 SOL, 2 open")
S = {lab(LIVE): (LIVE, score(LIVE))}
for k in GRID: S[lab(k)] = (k, score(k))
hdr = f"   {'rule':38s} | total  | A      B      C      | w/o best 5 | days<0 | worst | deepest fall | exits (a landing)"
row = lambda nm, s: f"   {nm:38s} | {s['tot']:+6.2f} | {s['b'][0]:+6.2f} {s['b'][1]:+6.2f} {s['b'][2]:+6.2f} | {s['wo5']:+6.2f}     | {s['neg']:2d}/{s['nd']} | {s['worst']:+5.2f} | {s['fall']:+5.2f}        | " + " ".join(f"{w} {c:.0f}" for w, c in s["whys"].most_common())
L0 = S[lab(LIVE)][1]
print("== the live rule\n" + hdr + "\n" + row(lab(LIVE), L0))
print("== the 25 best by total\n" + hdr)
for nm, (k, s) in sorted(S.items(), key=lambda x: -x[1][1]["tot"])[:25]: print(row(nm, s))
print("== ahead of the live rule in all three blocks\n" + hdr)
for nm, (k, s) in sorted(S.items(), key=lambda x: -x[1][1]["tot"]):
    if all(s["b"][i] > L0["b"][i] for i in range(3)): print(row(nm, s))
print("== the 15 with the fewest losing days (then the smallest fall)\n" + hdr)
for nm, (k, s) in sorted(S.items(), key=lambda x: (x[1][1]["neg"], -x[1][1]["fall"]))[:15]: print(row(nm, s))
print("== with tp 3.0 and 600 s as live, each trail (total; blocks)")
for a in (1.2, 1.3, 1.5, 1.75, 2.0, 2.5):
    print(f"   once {a}x: " + "  ".join(f"{int(d * 100)}% {S[lab(dict(LIVE, trail=(a, d)))][1]['tot']:+6.2f}" for d in (0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5)))
print(f"   (live, no trail: {L0['tot']:+.2f})")
print("== picked on two blocks, scored on the third (the gain over the live rule in the held-out block)")
gains = []
for held in range(3):
    other = [i for i in range(3) if i != held]
    best = max(S.items(), key=lambda x: sum(x[1][1]["b"][i] for i in other))
    g = best[1][1]["b"][held] - L0["b"][held]; gains.append(g)
    top10 = sorted(S.items(), key=lambda x: -sum(x[1][1]["b"][i] for i in other))[:10]
    g10 = sum(s["b"][held] - L0["b"][held] for nm, (k, s) in top10) / 10
    print(f"   held out {'ABC'[held]}: picked '{best[0]}' ({sum(best[1][1]['b'][i] for i in other) - sum(L0['b'][i] for i in other):+.2f} on the other two) -> {g:+.2f} on {'ABC'[held]}; the 10 best picks on average {g10:+.2f}")
print(f"   total out of sample: {sum(gains):+.2f} SOL")
