# SolHouse VIP lab: the whole setup engineered on its calls, with no overfitting (the owner, Nov 17: "engineer everything
# properly ... entry and exit, test every increment ... sell pressure, market cap, holders, top 10 holders, fees ...
# logically with no overfitting"). The rules, fixed before any result:
#  1. Three periods by time: TRAIN (the first 50% of the calls), VAL (the next 25%), TEST (the last 25%). Everything is
#     chosen on TRAIN; it must hold on VAL; TEST is scored once, at the end, with what was chosen.
#  2. Plateaus, not peaks: a parameter is taken where it and its neighbours on the grid are all good on TRAIN.
#  3. Signs: each cut at its TRAIN median; kept only if the winner rate differs by 5 points or more, the same way, on
#     TRAIN and VAL. The filter: the number of kept signs a call passes, the minimum picked on TRAIN.
#  4. Every result also without the best 5 of its period.
# Data: the VIP sample's curve paths (tg_test.py with PRE=3600 FULL=900: from the coin's creation, every trade to 15 min
# after the call, 1 in 4 after) and pool paths (tg_pool.py). Our 0.5 SOL on the reserves (constant product), the fee each
# way (the curve's bps, 1% in a pool), 0.0026 SOL of transaction costs.
#   python3 -I tg_vip_lab.py TGDIR > out/tg_vip_lab.txt
import sys, os, json, gzip, statistics as st, itertools, numpy as np
TG = sys.argv[1]; D = f"{TG}/{os.environ.get('VDIR', 'vip')}"; STAKE = 0.5; SUPPLY = 1e15; HOLD = 3600
HOLDOUT = os.environ.get("HOLDOUT")   # a frozen rule (prereg_signs.json) applied to calls the lab never saw
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "tg_channel.py")).read().split("for cj in sorted(glob.glob")[0]
sys.argv = [sys.argv[0], TG]; ns = {}; exec(compile(src, "tg_channel.py", "exec"), ns); load = ns["load"]
meta = json.load(open(f"{D}/meta.json"))
ALLT = np.array(sorted(v["t"] for v in meta.values() if "t" in v))   # every VIP call's time (the whole export): the market's pace
def age_min(a):
    if not a: return 0.0
    n = float("".join(ch for ch in a if ch.isdigit() or ch == ".") or 0); return n * {"s": 1 / 60, "m": 1, "h": 60, "d": 1440}.get(a[-1], 1)
# ---- one row per call: arrays after the post, and the signs at the post / in its first 2 min
rows = []
for t, m, P in load(D):
    mt = meta.get(m, {}); pr = np.array([r[1] / r[2] for r in P]); T = np.array([r[0] for r in P], dtype=float)
    Q = np.array([r[1] for r in P], dtype=float); fee = np.array([r[3] for r in P])
    dq = np.concatenate([[0.0], np.diff(Q)])   # + a buy, - a sale (quote reserve change)
    k0 = int(np.searchsorted(T, t, side="right")) - 1
    if k0 < 0 or k0 >= len(P) - 1: continue
    p0 = pr[k0]; at = lambda o: pr[int(np.searchsorted(T, t + o, side="right")) - 1] / p0
    w = (T > t - 600) & (T <= t); w2 = (T > t) & (T <= t + 120)
    r = dict(t=t, m=m, tier=mt.get("tier"), T=T, pr=pr, Q=Q, B=np.array([x[2] for x in P], dtype=float), fee=fee, dq=dq, k0=k0, p0=p0,
             s_mc=mt.get("mc", 0), s_age=age_min(mt.get("age")), s_curve=float((mt.get("pool") or "").strip() == "Pump.fun"),
             s_spotted=mt.get("spotted", 0), s_vol=mt.get("vol", 0), s_txns=mt.get("txns", 0),
             s_run10=at(-600), s_run3=at(-180), s_run1=at(-60), s_n10=int(w.sum()), s_flow10=dq[w].sum() / 1e9,
             s_big10=max(dq[w].max() if w.any() else 0, 0) / 1e9, s_sell10=float((dq[w] < 0).mean()) if w.any() else 0.5,
             a_p60=at(60), a_p120=at(120), a_flow2=dq[w2].sum() / 1e9, a_sells2=int((dq[w2] < 0).sum()) - int((dq[w2] > 0).sum()))
    r["s_run10"], r["s_run3"], r["s_run1"] = 1 / r["s_run10"], 1 / r["s_run3"], 1 / r["s_run1"]   # price at the post over before
    r["s_accel"] = r["s_run1"] / max(r["s_run3"], 1e-9)   # (price at -3 min) / (price at -1 min): high = it did not climb in those 2 min
    r["s_hour"] = (t // 3600) % 24                         # UTC hour of the call
    r["s_pace"] = int(((ALLT > t - 3600) & (ALLT <= t)).sum()) if len(ALLT) else 0   # VIP calls in the hour before: a hot or quiet market
    hi_t = T[k0 + 1:][w2[k0 + 1:]]; hp = pr[k0 + 1:][w2[k0 + 1:]]
    r["a_stall"] = float(len(hp) == 0 or (t + 120) - hi_t[int(np.argmax(hp))] >= 90)
    f = f"{D}/paths/{m}.json.gz"   # holders, top 10, dev, bundle, fee: from the curve's trades since creation
    if os.path.exists(f):
        x = json.load(gzip.open(f))
        if x.get("from_creation") and x.get("tr"):
            bal = {}; tr = [e for e in x["tr"] if e["t"] <= t]; s0 = tr[0]["slot"] if tr else 0; bundle = 0.0
            for e in tr:
                bal[e["user"]] = bal.get(e["user"], 0) + (e["tok"] if e["buy"] else -e["tok"])
                if e["buy"] and e["slot"] <= s0 + 1 and e["user"] != x.get("creator"): bundle += e["tok"]
            h = sorted((v for v in bal.values() if v > SUPPLY * 1e-5), reverse=True)
            buys = [e for e in tr if e["buy"]]; cr = x.get("creator")
            r.update(s_holders=len(h), s_top10=sum(h[:10]) / SUPPLY, s_top1=(h[0] / SUPPLY if h else 0),
                     s_dev=max(bal.get(cr, 0), 0) / SUPPLY, s_devbuy=sum(e["tok"] for e in buys if e["user"] == cr and e["slot"] <= s0 + 1) / SUPPLY,
                     s_bundle=bundle / SUPPLY, s_fee=tr[-1]["bps"] if tr else 0,
                     s_devsold=float(any(e["user"] == cr and not e["buy"] for e in tr)),
                     s_buyers=len({e["user"] for e in buys}), s_avgbuy=(sum(e["q"] for e in buys) / len(buys) / 1e9 if buys else 0),
                     s_smallbuys=(sum(e["q"] < 0.05e9 for e in buys) / len(buys) if buys else 0),   # dust buys: bots and volume makers
                     s_prog=max(0.0, 1 - (tr[-1].get("real") or 793.1e12) / 793.1e12) if tr else 0,
                     s_sellers=len({e["user"] for e in tr if not e["buy"]}))
    rows.append(r)
rows.sort(key=lambda r: r["t"]); n = len(rows)
if HOLDOUT:
    F = json.load(open(HOLDOUT)); ks = [tuple(x) for x in F["signs"]]
    sc = lambda r: sum(1 for k, c, hi in ks if k in r and ((r[k] > c) if hi else (r[k] <= c)))
    half = rows[len(rows) // 2]["t"] if rows else 0
    print(f"HOLDOUT: {n} calls with a price path, never seen by the lab; frozen signs ({F['made_on']}): {', '.join(k for k, _, _ in ks)}")
    print("pre-registered before this data: primary = at least 8 of 10 signs, buy 3 s after the call, tp2 or 60 min; also shown: 6, 7, 9 and tp4")
    def run_(R, **ex):
        out = []
        for r in R:
            k = int(np.searchsorted(r["T"], r["t"] + 3, side="left"))
            if k < len(r["T"]) - 1 and r["pr"][k] <= 1.25 * r["p0"]: out.append(None)   # placeholder replaced below
        return out
    def S2(v):
        if not v: return "   0"
        s2 = sorted(v, reverse=True); return f"{len(v):4d} {sum(v):+7.2f} ({sum(v) / len(v) / STAKE:+6.1%}) w/o5 {sum(s2[5:]):+7.2f}"
    HOLD_ROWS = (rows, sc, half, S2)
TR, VA, TE = rows[: n // 2], rows[n // 2: 3 * n // 4], rows[3 * n // 4:]
fmt_t = lambda v: f"{v[0]['t']:.0f}-{v[-1]['t']:.0f}" if v else "-"
print(f"{n} VIP calls with a price path: TRAIN {len(TR)}, VAL {len(VA)}, TEST {len(TE)} (by time)")
# ---- the copy: entry index (delay or dip), exits vectorised over the path after it
def entry(r, delay=1, dip=None):
    T, pr = r["T"], r["pr"]; k = int(np.searchsorted(T, r["t"] + delay, side="left"))
    if dip is not None:
        ok = np.where((T >= r["t"] + 1) & (T <= r["t"] + 300) & (pr <= dip * r["p0"]))[0]
        if not len(ok): return None
        k = int(ok[0])
    if k >= len(T) - 1 or pr[k] > 1.25 * r["p0"]: return None
    return k
def trade(r, k, tp=None, sl=None, cap=3600, trail=None, sp=None, stall=None):
    T, pr, Q, B, fee, dq = r["T"], r["pr"], r["Q"], r["B"], r["fee"], r["dq"]
    inn = STAKE * 1e9 * (1 - fee[k]); tok = B[k] * inn / (Q[k] + inn); pe = pr[k]
    sl_ = slice(k + 1, len(T)); t_, p_ = T[sl_] - T[k], pr[sl_] / pe; cands = []
    def first(mask, d=1):
        i = np.argmax(mask) if mask.any() else None
        if i is not None and mask[i]: cands.append(min(k + 1 + i + d, len(T) - 1))
    first(t_ >= cap, 0)
    if tp: first(p_ >= tp)
    if sl: first(p_ <= sl)
    if trail:
        a, d = trail; pk = np.maximum.accumulate(p_); first((pk >= a) & (p_ <= pk * (1 - d)))
    if sp:
        nn, win = sp; s = np.cumsum(np.sign(-dq[sl_])); lo = np.searchsorted(t_, t_ - win, side="left")
        net = s - np.concatenate([[0], s])[lo]; first((net >= nn) & (t_ >= 30))
    if stall:
        pk = np.maximum.accumulate(p_); newhi = np.concatenate([[True], pk[1:] > pk[:-1]])
        last = np.maximum.accumulate(np.where(newhi, t_, -1e9)); first((pk >= 1.0) & (t_ - last >= stall))
    j = min(cands) if cands else len(T) - 1
    return Q[j] * tok / (B[j] + tok) * (1 - fee[j]) / 1e9 - STAKE - 0.0026
def run(R, ent=None, **ex):
    out = []
    for r in R:
        k = entry(r, **(ent or {}))
        if k is not None: out.append(trade(r, k, **ex))
    return out
def S(v):
    if not v: return "   0"
    s = sorted(v, reverse=True); return f"{len(v):4d} {sum(v):+7.2f} ({sum(v) / len(v) / STAKE:+6.1%}) w/o5 {sum(s[5:]):+7.2f}"
if HOLDOUT:
    rows, sc, half, S2 = HOLD_ROWS
    for N in (0, 6, 7, 8, 9):
        for ex in (dict(tp=2), dict(tp=4)):
            R = [r for r in rows if sc(r) >= N]; a = run([r for r in R if r["t"] < half], ent=dict(delay=3), **ex); b = run([r for r in R if r["t"] >= half], ent=dict(delay=3), **ex)
            print(f"  at least {N:2d}, {str(ex):12s}: all {S2(a + b)} | first half {S2(a)} | second half {S2(b)}")
    sys.exit(0)
# ---- 1. signs: winners (1.5x in the hour from the post) against losers
win = lambda r: r["pr"][r["k0"] + 1:][r["T"][r["k0"] + 1:] <= r["t"] + 3600].max() / r["p0"] >= 1.5 if (r["T"] > r["t"]).any() else False
for r in rows: r["win"] = win(r)
wr = lambda v: sum(r["win"] for r in v) / len(v) if v else float("nan")
print(f"\n1. SIGNS. winners (1.5x within the hour of the call): TRAIN {wr(TR):.0%}, VAL {wr(VA):.0%}, TEST {wr(TE):.0%}")
print("   by tier, TRAIN / VAL: " + ", ".join(f"{x} {wr([r for r in TR if r['tier'] == x]):.0%}/{wr([r for r in VA if r['tier'] == x]):.0%}" for x in ("Diamond", "Safe", "Gamble", "Gamble Risk")))
keys = sorted({k for r in rows for k in r if k[:2] in ("s_", "a_")}); kept = []
print("   sign        | cut      | winner rate low/high TRAIN | VAL        | n with it | kept")
for k in keys:
    a = [r for r in TR if k in r]; b = [r for r in VA if k in r]
    if len(a) < 20 or len(b) < 10: continue
    cut = st.median([r[k] for r in a]); L = lambda v: [r for r in v if r[k] <= cut]; Hh = lambda v: [r for r in v if r[k] > cut]
    da, db = wr(Hh(a)) - wr(L(a)), wr(Hh(b)) - wr(L(b))
    ok = all(x == x for x in (da, db)) and abs(da) >= 0.05 and abs(db) >= 0.05 and (da > 0) == (db > 0)
    if ok: kept.append((k, cut, da > 0))
    print(f"   {k:11s} | {cut:8.3g} | {wr(L(a)):4.0%} / {wr(Hh(a)):4.0%}              | {wr(L(b)):4.0%} / {wr(Hh(b)):4.0%} | {len(a) + len(b):4d} | {'YES: ' + ('high' if da > 0 else 'low') if ok else ''}")
pre = [x for x in kept if x[0].startswith("s_")]; post2 = [x for x in kept if x[0].startswith("a_")]
json.dump(dict(signs=[[k, float(c), bool(h)] for k, c, h in pre], made_on=f"{len(TR)} TRAIN + {len(VA)} VAL calls"), open(f"{D}/prereg_signs.json", "w"))
score = lambda r, ks: sum(1 for k, c, hi in ks if k in r and ((r[k] > c) if hi else (r[k] <= c)))
# ---- 2. the filter: at least N of the kept signs at the call (N picked on TRAIN, base exit tp2 / 60 min)
print(f"\n2. FILTER from the kept signs at the call ({len(pre)}: {', '.join(k for k, _, _ in pre)}); base trade: buy 1 s after, tp2, 60 min")
best_n, best_v = 0, None
for N in range(0, len(pre) + 1):
    a = run([r for r in TR if score(r, pre) >= N], tp=2); b = run([r for r in VA if score(r, pre) >= N], tp=2)
    print(f"   at least {N}: TRAIN {S(a)} | VAL {S(b)}")
    if len(a) >= 20 and (best_v is None or sum(a) / len(a) > best_v): best_n, best_v = N, sum(a) / len(a)
FIL = lambda R: [r for r in R if score(r, pre) >= best_n]
print(f"   picked on TRAIN: at least {best_n} (the best mean a copy with 20+ copies)")
# ---- 3. entry: delays and dips (filtered calls, base exit)
print("\n3. ENTRY (filtered calls, exit tp2 / 60 min)")
ents = [("delay %ds" % d, dict(delay=d)) for d in (1, 3, 5, 10, 20, 30, 60, 120)] + [("dip %.2f" % x, dict(dip=x)) for x in (0.95, 0.9, 0.85, 0.8)]
res = []
for name, e in ents:
    a = run(FIL(TR), ent=e, tp=2); b = run(FIL(VA), ent=e, tp=2); res.append((name, e, a, b))
    print(f"   {name:10s}: TRAIN {S(a)} | VAL {S(b)}")
def plateau(res):   # the best mean on TRAIN among those whose grid neighbours are positive on TRAIN too (20+ copies each)
    m = [sum(a) / len(a) if a and len(a) >= 20 else -9 for _, _, a, _ in res]; best = None
    for i in range(len(res)):
        nb = [m[j] for j in (i - 1, i, i + 1) if 0 <= j < len(res)]
        if min(nb) > 0 and (best is None or m[i] > m[best]): best = i
    return best if best is not None else int(np.argmax(m))
ENT = res[plateau(res)][1]; print(f"   picked (plateau on TRAIN): {res[plateau(res)][0]}")
# ---- 4. exits, one family at a time around the base, then together
print("\n4. EXITS (filtered calls, the picked entry)")
fam = {"tp": [dict(tp=x) for x in (1.2, 1.3, 1.5, 1.75, 2, 2.5, 3, 4, 5)],
       "stop": [dict(tp=2, sl=x) for x in (0.9, 0.8, 0.7, 0.6, 0.5)],
       "time": [dict(tp=2, cap=x * 60) for x in (2, 5, 10, 20, 30, 60)],
       "trail": [dict(tp=None, trail=(a, d)) for a in (1.2, 1.3, 1.5, 2) for d in (0.2, 0.3, 0.4)],
       "sell pressure": [dict(tp=2, sp=(nn, w)) for nn in (3, 5, 8, 12) for w in (30, 60)],
       "stall": [dict(tp=2, stall=x) for x in (60, 120, 180, 300)]}
chosen = {}
for f, grid in fam.items():
    res = []
    for ex in grid:
        a = run(FIL(TR), ent=ENT, **ex); b = run(FIL(VA), ent=ENT, **ex); res.append((str(ex), ex, a, b))
        print(f"   {f:13s} {str(ex):34s}: TRAIN {S(a)} | VAL {S(b)}")
    i = plateau(res); chosen[f] = res[i]; print(f"   -> {f}: {res[i][0]} (plateau on TRAIN)")
best = max(chosen.values(), key=lambda x: sum(x[2]) / max(1, len(x[2])))
print(f"\n   the best family on TRAIN: {best[0]}: TRAIN {S(best[2])} | VAL {S(best[3])}")
# ---- 5. TEST, once
FINAL = best[1]
print(f"\n5. TEST (the last 25%, never looked at): filter at least {best_n} of {len(pre)} signs, entry {ENT}, exit {FINAL}")
t1 = run(FIL(TE), ent=ENT, **FINAL); t0 = run(TE, tp=2)
print(f"   the setup: {S(t1)}")
print(f"   every call, buy 1 s after, tp2 (no setup): {S(t0)}")
