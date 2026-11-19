# m15b: m15's checks (Nov 19): against the bot's live exits, neighbouring dips / windows / exits, replace or add-on.
# Wallet 4, buying the DIP after its buy, out of sample (Nov 19). m14 picked it on the 4 days (Nov 14-18): enter at the first
# trade within W s of its buy at or under 90% of the price its buy left (W = 60: picked exit tp x1.5, 900 s; W = 300:
# tp x1.5, 2400 s), blind days 3-4 +10.9% / +8.9% a trade. Here, FROZEN, on wallet 4's research corpus Oct 21 - Nov 16
# (allq / cq / since_stop / newq, 31 minutes of every trade from its buy, true in-slot order, routable buys of 0.5+ SOL)
# WITHOUT the 4 days (t < Nov 14 01:07 UTC), against the plain copy (the next slot) with the same exits, by week.
#   python3 -I m15_w4_dip.py SP H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg > ../out/m15_w4_dip.txt
# The full engineering of a found wallet's copy, every time (Nov 18, the owner: "buy size, holding time, tp, sell
# pressure, stall, its sell, tested at small increments, all combinations possible, and choosing logically, not only
# computing numbers"). Every combination of:
#   its buy size (min) 0.5 0.6 0.7 0.8 0.9 1.0 1.1 1.2 1.3 1.4 1.5 1.75 2.0 SOL | our price over its price (max) 1.1 1.25 1.5 none
#   take profit 1.5 2 2.5 3 3.5 4 5 6 8 none | time 60 120 180 300 450 600 s
#   sell pressure off or n in {3, 5, 8, 10} over w in {30, 60} s (from 30 s) | stall off 60 90 120 180 240 s
#   its sale: never / early (30-290 s under 1.5x) / always
# Our 0.5 SOL at the three landings (hunt_lib's fills: our buy's weight on the curve, the fee of its trade), 0.0345 SOL a
# round trip, take profit and the 1.5x of the early rule against ITS price (as the live bot), stall once back at its price.
# The choice, by logic: (1) every setting ranked by the SOL its WEAKER half makes without its best 2% of copies (halves by time); (2) smoothed: the mean of its
# neighbours one step either way on each part, so a lone spike cannot win (the middle of a plateau); (3) a part that
# changes nothing within the noise is set to its simplest value; (4) shown: each part varied alone around the choice,
# and the setting picked on the first half alone with its rank on the second (the overfitting check).
# Sources: the 4 days of float-quote coins on disk (paths_full); for TAB16RxX also its 14 earlier days, float-paid
# (tab/lk paths with the bot's scan).
#   python3 -I e8_engineer.py SP WALLET > ../out/e8_<wallet8>.txt
import sys, os, re, json, gzip, itertools, functools, numpy as np
SP, W = sys.argv[1], sys.argv[2]; PAY = os.environ.get("PAY", "float")   # float / wsol / all: which copies by what we pay with (the owner, Nov 18: "test with all coins, all sizes")
O = f"{SP}/market"; PD = f"{O}/paths_full"; COST = 0.0345 - 0.0026
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(here, "..")); import hunt_lib as H
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-18/churn"); import slot_order as SO
FLOATS = ("3NZ9JMVB", "pumpCmXq", "SPCXxcqX", "TTWofwAg", "DJTu7vi8", "98sMhvDw", "XsbEhLAt"); WSOL = "So11111111111111111111111111111111111111112"
SIZE = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.75, 2.0]; PREM = [1.1, 1.25, 1.5, 1e9]
TP = [1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 1e9]; HOLD = [60, 120, 180, 300, 450, 600]
SPS = [None] + [(n, w) for n in (3, 5, 8, 10) for w in (30, 60)]; STALL = [0, 60, 90, 120, 180, 240]; ITS = ["never", "early", "always"]
def first(m): i = np.flatnonzero(m); return int(i[0]) if len(i) else None
def copy_vals(p):
    """All TP x HOLD x SP x STALL x ITS values of one prepared landing (array of that shape), and its entry premium."""
    shape = (len(TP), len(HOLD), len(SPS), len(STALL), len(ITS))
    if p["refused"] or not len(p["px"]): return np.full(shape, -0.0004)
    vt0, vq0, bps0 = p["ent"]; Q = 0.5e9 * p["hopf"] / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    px, age = p["px"], p["age"]; n = len(px)
    vq, vt, b = p["vq"], p["vt"], p["bps"]; vq_r = vq + net_in; vt_r = vt * vq / vq_r
    val = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - b / 1e4) * p["rate"] * p["hopf"] / 1e9 - 0.5 - 0.0026   # selling at each trade
    BIG = 10 ** 9; trig = lambda i: BIG if i is None else min(i + 1, n - 1); at = lambda i: BIG if i is None else i   # a trigger sells at the next trade
    g = at(first(p["grad"]))
    tp_i = np.array([trig(first(px >= t)) if t < 1e8 else BIG for t in TP])
    h_i = np.array([at(first(age >= h)) for h in HOLD])
    s = np.concatenate([[0], np.cumsum(p["osell"])]); bb = np.concatenate([[0], np.cumsum(p["obuy"])])
    sp_i = []
    for sp in SPS:
        if sp is None: sp_i.append(BIG); continue
        lo = np.searchsorted(age, age - sp[1], side="left"); sp_i.append(trig(first(((s[1:] - s[lo]) - (bb[1:] - bb[lo]) >= sp[0]) & (age >= 30))))
    pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
    st_i = np.array([BIG if st == 0 else trig(first((pk >= 1.0) & (age - lasthi >= st))) for st in STALL])
    it_i = np.array([BIG, trig(first(p["sell"] & (age >= 30) & (age < 290) & (px < 1.5))), trig(first(p["sell"]))])
    E = functools.reduce(np.minimum, [tp_i[:, None, None, None, None], h_i[None, :, None, None, None], np.array(sp_i)[None, None, :, None, None],
                           st_i[None, None, None, :, None], it_i[None, None, None, None, :], np.full(shape, g)])
    return val[np.clip(E, 0, n - 1)]

sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt/market"); import m14_dip_after as D
rows = []
def add(tr, k, rate, sol, q8, cls):
    if sol < 0.5: return
    rows.append(dict(t=tr[k]["t"], tr=tr, k=k, rate=rate, cls=cls))
# source 3 (wallet 4): its research corpus, Oct 21 - Nov 16 (allq / cq / since_stop / newq: every trade for 31 minutes from
# its buy; the rate from routable.json's SOL value), true in-slot order; the 4 days above are then not added twice
if True:
    seen = set(); got = {}
    for d_ in ("allq", "cq", "since_stop", "newq"):
        try: P = json.load(gzip.open(f"{SP}/{d_}/paths.json.gz")); R_ = {f"{r['slot']}_{r['mint8']}": r for r in json.load(open(f"{SP}/{d_}/routable.json"))}
        except Exception: continue
        for kk, vv in P.items():
            if not vv or kk not in R_: continue
            m_, tr = vv
            if m_ in got and got[m_] >= len(tr): continue
            got[m_] = len(tr)
    INP = {}   # what the bot pays with: the planner's route input (scan_hops.out / scan.out); a coin quoted in a float is float-paid today (7 floats)
    for d_ in ("allq", "cq", "since_stop", "newq"):
        for f_ in ("scan_hops.out", "scan.out"):
            if not os.path.exists(f"{SP}/{d_}/{f_}"): continue
            for l in open(f"{SP}/{d_}/{f_}"):
                m = re.match(r"(\d+) (\S{8}) .*? quote (\S+) .*?ROUTABLE.*?input: (\w{8})", l)
                if m: INP.setdefault(f"{d_}/{m.group(1)}_{m.group(2)}", "float" if m.group(4) in FLOATS or m.group(3)[:8] in FLOATS else "wsol")
    for d_ in ("allq", "cq", "since_stop", "newq"):
        try: P = json.load(gzip.open(f"{SP}/{d_}/paths.json.gz")); R_ = {f"{r['slot']}_{r['mint8']}": r for r in json.load(open(f"{SP}/{d_}/routable.json"))}
        except Exception: continue
        for kk, vv in P.items():
            if not vv or kk not in R_: continue
            m_, tr = vv
            if got.get(m_) != len(tr) or not R_[kk].get("ok", True): continue   # routable only (the bot copies it)
            got[m_] = -1; tr = SO.reorder(tr)
            k = next((i for i, e in enumerate(tr) if e["user"] == W and e["buy"] and e["slot"] == R_[kk]["slot"]), None)
            if k is None or tr[k]["t"] in seen or tr[-1]["t"] - tr[k]["t"] < 600: continue
            rate = R_[kk]["sol"] * 1e9 / (tr[k]["q"] * (1 + tr[k]["bps"] / 1e4))
            q8 = str(R_[kk].get("quote", "?"))[:8]
            add(tr, k, rate, R_[kk]["sol"], q8, INP.get(f"{d_}/{kk}", "float" if q8 in FLOATS else "wsol"))

import datetime as dt, numpy as np, collections
CUT = 1794618422   # the 4 days start (Nov 14 01:07 UTC): nothing from there on
rows = [r for r in rows if r["t"] < CUT]; rows.sort(key=lambda r: r["t"])
G = D.GRID
LIVE = (TP.index(4), HOLD.index(600), SPS.index((5, 60)), STALL.index(180), ITS.index("early"))   # the bot's live exits
print(f"wallet 4: {len(rows)} buys of 0.5+ SOL before the 4 days; COST {D.COST}; halves at the median time")
T = np.array([r["t"] for r in rows]); MID = np.median(T)
live = []; dips = collections.defaultdict(dict)
for n_, r in enumerate(rows):
    tr, k, rate = r["tr"], r["k"], r["rate"]; pk = tr[k]["vq"] / tr[k]["vt"]
    ps = [H.prep(tr, k, rate, n, pmax=1000) for n in (4, 8, "slot+1")]
    prem = float(np.mean([(tr[k]["vt"] / p["ent"][0]) ** 2 for p in ps]))
    live.append(float(np.mean([copy_vals(p)[LIVE] for p in ps]) - COST) if prem <= 1.5 else -0.0004)
    for d in (0.05, 0.1, 0.15, 0.2):
        for w in (30, 60, 120, 300):
            j = next((i for i in range(k + 1, len(tr)) if tr[i]["t"] - tr[k]["t"] <= w and tr[i]["slot"] > tr[k]["slot"] and tr[i]["vq"] / tr[i]["vt"] <= (1 - d) * pk), None)
            if j is not None and j < len(tr) - 1:
                v = D.grid_from(tr, k, j, rate)
                if v: dips[(d, w)][n_] = v
live = np.array(live); A = T < MID
print(f"\nTHE BOT TODAY (plain copy, live exits tp 4 / 600 s / sp 5-60 / stall 180 / its early sale): {live.sum():+.2f} SOL ({100 * live.mean() / 0.5:+.1f}% a copy), halves {live[A].sum():+.2f} / {live[~A].sum():+.2f}")
j1 = G.index((1.5, 900, False))
print("\nDIP grid, exit tp 1.5 / 900 s (the frozen pick), out of sample: trades, a trade, halves")
for d in (0.05, 0.1, 0.15, 0.2):
    print(f"   dip {int(d * 100):2d}%: " + "   ".join(f"{w:3d} s {len(dips[(d, w)]):4d} {100 * np.mean([v[j1] for v in dips[(d, w)].values()]) / 0.5:+5.1f}% ({sum(v[j1] for n_, v in dips[(d, w)].items() if A[n_]):+.1f}/{sum(v[j1] for n_, v in dips[(d, w)].items() if not A[n_]):+.1f})" for w in (30, 60, 120, 300)))
print("\nEXITS around the pick, dip 10% within 60 s: a trade (halves)")
for tp in (1.5, 2, 3, 1e9):
    print(f"   tp {tp if tp < 1e8 else 'none':4}: " + "   ".join(f"{h:4d} s {100 * np.mean([v[G.index((tp, h, False))] for v in dips[(0.1, 60)].values()]) / 0.5:+5.1f}%" for h in (60, 300, 900, 2400)))
dd = dips[(0.1, 60)]
rep = np.array([dd[n_][j1] if n_ in dd else 0.0 for n_ in range(len(rows))]); addon = live + rep
print(f"\nREPLACE (only the dip trades): {rep.sum():+.2f} SOL on {len(dd)} trades; ADD-ON (the bot as today + a second buy on the dip): {addon.sum():+.2f} SOL, halves {addon[A].sum():+.2f} / {addon[~A].sum():+.2f}")
