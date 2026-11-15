# "Something more consistent and less dependent on luck that coins go to tp, even if profits drop a bit" (the owner,
# Nov 15). Every exit idea scored on steadiness: Beirut days Oct 22 - Nov 13 (23 full days), each day the mean of
# landings 4 / 8 / one block late. Per rule: total; days negative; worst day; the 3rd worst day; the deepest fall
# from a high; the share of the total made by the best 5 trades; the total without the best 5 and best 10 trades.
# Ideas: take profit 1.5-3.0 at once; part sales (25/50/75% at 1.2x-2.5x) with the rest at 3.0 or the timer; trailing
# stops (once at a, sell d under the high); stops; timers 300 / 600 s. Live four kinds (SOL 1, WBTC 2, PUMP 1, SPCX 1),
# 0.5 SOL, 2 open, raw. Picks are checked on the two halves (Oct 22 - Nov 1, Nov 2 - 13).
#   python3 -I steady.py SPD
import sys, os, datetime, itertools, collections
from multiprocessing import Pool
T0 = datetime.datetime(2026, 10, 21, 18, 30, tzinfo=datetime.timezone.utc).timestamp(); os.environ["FE_T0"] = str(T0)
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-14/float_exits"); sys.argv = sys.argv[:2] + ["0.5"]
import float_exits as F
import lib as L
KINDS = {"SOL": 1, "WBTC": 2, "PUMP": 1, "SPCX": 1}
ROWS = [r for r in F.rows if r["anchor"] in KINDS]
day = lambda t: datetime.datetime.fromtimestamp(t + 7200, datetime.timezone.utc).strftime("%m-%d")
DAYS = sorted({day(r["t"]) for r in ROWS} - {"10-21", "11-14"}); H1 = set(DAYS[:len(DAYS) // 2])
E = (30, 290, 1.5)
def sim(n, kw):
    out, open_ = [], []
    for r in ROWS:
        open_ = [x for x in open_ if x[0] > r["t"]]
        if len(open_) >= 2 or sum(1 for x in open_ if x[1] == r["anchor"]) >= KINDS[r["anchor"]]: continue
        net, why, held = L.model_partial(F.PREP[r["key"], n], 0.5, **kw)
        if why != "refused": open_.append((r["t"] + held, r["anchor"]))
        out.append((day(r["t"]), r["t"], net))
    return out
def ev(kw):
    runs = [sim(n, kw) for n in L.LAND]; d = collections.defaultdict(float); trades = []; dd = []
    for res in runs:
        for dy, t, net in res:
            if dy in DAYS: d[dy] += net / 3; trades.append(net / 3)
        cum = lo = hi = 0.0
        for dy, t, net in res:
            if dy not in DAYS: continue
            cum += net; hi = max(hi, cum); lo = min(lo, cum - hi)
        dd.append(lo)
    v = [d[x] for x in DAYS]; tr = sorted(trades, reverse=True); tot = sum(v); s = sorted(v)
    return kw, dict(tot=tot, neg=sum(1 for x in v if x < 0), worst=s[0], third=s[2], dd=sum(dd) / 3, top5=sum(tr[:15]) / max(tot, 1e-9),
                    wo5=sum(tr[15:]), wo10=sum(tr[30:]), h=(sum(d[x] for x in DAYS if x in H1), sum(d[x] for x in DAYS if x not in H1)),
                    hneg=(sum(1 for x in DAYS if x in H1 and d[x] < 0), sum(1 for x in DAYS if x not in H1 and d[x] < 0)))
K = lambda **k: dict(dict(tp1=None, frac=0, tp=3.0, hold=600, early=E, sl=None, trail=None), **k)
GRID = [K(tp=tp, hold=h) for tp in (1.5, 1.8, 2.0, 2.4, 3.0) for h in (300, 600)]
GRID += [K(tp1=a, frac=f, tp=tp, hold=h) for a in (1.2, 1.3, 1.4, 1.5, 1.7, 2.0, 2.5) for f in (0.25, 0.5, 0.75) for tp in (3.0, None) for h in (300, 600)]
GRID += [K(trail=(a, dd), tp=tp, hold=h) for a in (1.3, 1.5, 2.0) for dd in (0.2, 0.3, 0.4) for tp in (3.0, None) for h in (600, 1200)]
GRID += [K(tp1=a, frac=0.5, trail=(a, dd), tp=None, hold=h) for a in (1.3, 1.5, 2.0) for dd in (0.25, 0.4) for h in (600, 1200)]
GRID += [K(sl=s, hold=h) for s in (0.5, 0.6, 0.7, 0.8) for h in (300, 600)]
def lab(kw):
    p = []
    if kw["frac"]: p.append(f"sell {int(kw['frac'] * 100)}% at {kw['tp1']}x")
    if kw["trail"]: p.append(f"trail {int(kw['trail'][1] * 100)}% once {kw['trail'][0]}x")
    if kw["sl"]: p.append(f"stop {kw['sl']}x")
    p.append(f"tp {kw['tp']}" if kw["tp"] else "no tp"); p.append(f"{kw['hold']} s")
    return ", ".join(p)
if __name__ == "__main__":
    with Pool(4) as p: R = p.map(ev, GRID)
    live = next(r for r in R if r[0] == K())
    print(f"{len(ROWS)} buys, {len(DAYS)} full Beirut days (halves {DAYS[0]}-{max(H1)} and {min(set(DAYS) - H1)}-{DAYS[-1]}); {len(GRID)} rules; 0.5 SOL, 2 open")
    hdr = f"   {'rule':50s} | total  | days < 0 (halves) | worst | 3rd worst | deepest fall | best 5 trades' share | w/o best 5 | w/o best 10 | halves"
    row = lambda r: print(f"   {lab(r[0]):50s} | {r[1]['tot']:+6.2f} | {r[1]['neg']:2d} ({r[1]['hneg'][0]}, {r[1]['hneg'][1]})        | {r[1]['worst']:+5.2f} | {r[1]['third']:+5.2f}     | {r[1]['dd']:+5.2f}        | {100 * r[1]['top5']:4.0f}%                 | {r[1]['wo5']:+6.2f}     | {r[1]['wo10']:+6.2f}      | {r[1]['h'][0]:+6.2f} {r[1]['h'][1]:+6.2f}")
    print("== the live rule"); print(hdr); row(live)
    print("\n== the 15 steadiest (fewest negative days, then the best 3rd worst day), with total >= 60% of the live rule's")
    ok = [r for r in R if r[1]["tot"] >= 0.6 * live[1]["tot"]]
    for r in sorted(ok, key=lambda r: (r[1]["neg"], -r[1]["third"], -r[1]["tot"]))[:15]: row(r)
    print("\n== the 15 with the smallest deepest fall, total >= 60% of the live rule's")
    for r in sorted(ok, key=lambda r: (-r[1]["dd"], -r[1]["tot"]))[:15]: row(r)
    print("\n== the 15 least dependent on the best trades (total without the best 10)")
    for r in sorted(R, key=lambda r: -r[1]["wo10"])[:15]: row(r)
    print("\n== part sales at 1.2x / 1.3x / 1.4x (the owner's question), rest at tp 3.0, 600 s")
    for a in (1.2, 1.3, 1.4):
        for f in (0.25, 0.5, 0.75): row(next(r for r in R if r[0] == K(tp1=a, frac=f)))
