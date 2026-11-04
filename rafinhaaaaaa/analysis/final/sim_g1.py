# Section E: its own exit rules read from its sales, ours placed just inside them, our stake, picked on P1 (days 1-4)
# and scored on P2 (days 5-7), also without P2's best 2 (the owner's process; copy2 backtests.md §6-§8).
#   entry: our buy K trades behind its buy (s2k2 = K 2, the live run's median of landed trades between, live_model3.py;
#          s2k1 / s2 (K 4) / s2k7 shown for the picked rule), price = its price x entry_base x (1 + stake x entry_imp1)
#   its levels (P1 first sales, chain multiples = pool price of its first sale / of its buy): its timer = the hold most
#          first sales end at (10 s bins, at least 25% of them), its take profit = the multiple most winning first
#          sales (>= 1.1x) end at (0.05 bins, at least 12%), its stop = the same below 0.95x (at least 10%) - derive.py
#   ours: take profit = f x its level, f in 0.6-1.0 (no level: 1.3 / 1.5 / 2 / 3x), stop = its stop + 0 / 0.05 / 0.1
#          (no level: 0.7 / 0.8 / 0.9), timer = its timer - 10 s (no timer: 300 / 1790 s / none), and always behind its
#          first sale (K trades behind it, the chain leg) when it sells before ours fire; each also "none"
#   path: paths_g1.py (chain trades sampled, its-price multiples); a level fills at the trade that crossed it x 0.99
#          / (1 + our impact) (live_model3.py: "avg 1%" matched the live fills), the timer at that trade's price
#   stake: 0.1 / 0.25 / 0.5 / 1 / 2 SOL / half its size / its size (cap 3); costs 0.0095 SOL a transaction x 2 + 1.25%
#          each way (also 0.003 a round trip, the live cost)
#   python3 -I sim_g1.py S3Q2_JSON [SOLUSD]
import sys, os, json, itertools, collections
import statistics as st
RACE = float(os.environ.get("RACE", "2"))   # s: a take profit crossed this close to its first sale counts as its sale first (copy2: at its 2.45x its sale came first on 83 of 126)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g1lib import jl, G1
src = sys.argv[1]; SOLUSD = float(sys.argv[2]) if len(sys.argv) > 2 else 98.5
d = jl(src); w = d["wallet"]; ch = jl(f"{G1}/chain/{w}.json"); P = jl(f"{G1}/paths/{w}.json")
mid = d["t0"] + float(os.environ.get("MID_DAYS", "4")) * 86400   # P1 = days 1-4 (MID_DAYS=21: 3 weeks, P2 = the 4th)
STAKES = [0.1, 0.25, 0.5, 1.0, 2.0, "half its size", "its size"]
def its_sol(t):
    c = ch.get(t["sig0"]) or {}; s = -(c.get("sol") or 0)
    return s if s > 0.01 else t["usd_in"] / SOLUSD
def stake_of(t, s):
    x = min(its_sol(t), 3.0)
    return max(0.05, x * 0.5 if s == "half its size" else x if s == "its size" else s)
def chain_mult(t, i):
    c = ch.get(t["sig0"]) or {}; ss = c.get("sells") or []
    g = t["sells"][i]["px"] / t["px0"]
    if c.get("pools") and i < len(ss) and ss[i] and ss[i].get("px") and ss[i].get("pool") == c["pools"][0]["pool"]:
        m = ss[i]["px"] / c["pools"][0]["px"]
        if g <= 0 or 1 / 3 <= m / g <= 3: return m                 # the chain's multiple, unless 3x off GMGN's: a unit mix-up
    return g
def first_leg(t, e):
    s0 = t["sells"][0]
    for fr, px, base, i1 in e.get("legs") or []:
        if px == s0["px"]: return base, i1
    return 0.97, e.get("entry_imp1") or 0.0
FIXED = float(os.environ.get("FIXED", "0.003"))    # fixed SOL a round trip: ~0.003 live (tip + priority fees; G1's replay
                                                   # matched live at it); the old 0.019 (0.0095 a transaction) was copy2's cautious number
AMMS = {"pump curve", "PumpSwap", "Raydium CLMM", "Raydium CPMM", "Raydium AMM", "Raydium AMM v4", "Orca", "Meteora DLMM",
        "Meteora DAMM", "Meteora DAMM v2", "Meteora DBC", "Raydium Launchpad", "LaunchLab"}
def fee(t):
    """swap fee a side, by venue (each hop of our route pays its pool): the pump curve 1.25% (0.95% protocol + 0.30% creator),
    PumpSwap and the other pools about 0.30%; a coin priced in another token adds the SOL -> quote hop"""
    v = (ch.get(t["sig0"]) or {}).get("venue") or []
    hops = [x for x in v if x in AMMS]
    if not hops: return 0.0125 + (0.003 if t["quote"] not in ("WSOL", "SOL") else 0.0)
    f = 0.0125 if "pump curve" in hops else 0.003
    return f + 0.003 * max(0, len(set(hops)) - 1)
def sim(t, key, tp, sl, timer, stake, fixed=None, K=2):
    fixed = FIXED if fixed is None else fixed
    e = t.get(key)
    if not e or broken(e): return None
    S = stake_of(t, stake); imp = 1 + S * (e.get("entry_imp1") or 0.0)
    ours = e["entry_base"] * imp
    pth = P.get(t["sig0"]); pts = (pth or {}).get("pts") or []
    t1 = t["sells"][0]["t"]; b1, i1 = first_leg(t, e)
    follow = chain_mult(t, 0) * b1 / (1 + S * i1)
    x = None
    for j, p in enumerate(pts):
        a, hi, lo, cl = p[0], p[1], p[2], p[3]
        if pth["src"] == "chain" and j < K: continue          # trades ahead of our landing
        if a >= t1: break                                      # its first sale came first: we sell behind it
        if sl and lo <= sl: x = min(lo, sl) * 0.99 / imp if pth["src"] == "chain" else sl * 0.97 / imp; break
        if tp and hi >= tp:
            if a >= t1 - RACE: break                                 # its own sale lands first (as fast as ours): behind it
            x = min(hi, 1.25 * tp) * 0.99 / imp if pth["src"] == "chain" else tp * 0.97 / imp; break
        if timer and a >= t["t0"] + timer: x = cl * 0.99 / imp; break
    if x is None and timer and t1 > t["t0"] + timer:         # the path ends at the hour: our timer sells at its last price
        x = pts[-1][3] * 0.99 / imp if pts else follow
    if x is None: x = follow
    g = x / ours
    return S * (g - 1 - fee(t) * (1 + g)) - fixed
def mode(vals, width, lo=None, hi=None, share=0.0, n=1):
    v = [x for x in vals if (lo is None or x >= lo) and (hi is None or x < hi)]
    if not v: return None, 0
    c = collections.Counter(round(x / width) * width for x in v); lvl, k = c.most_common(1)[0]
    return (lvl, k) if k >= share * n else (None, k)
def wo2(v): v = sorted(v); return sum(v[:-2]) if len(v) > 2 else 0.0
def broken(e):                                               # priced more than 3x off its own price, or impact out of range: a mixed-pool leg
    return (any(not (0.2 <= l[2] <= 3.0) or not (0.0 <= l[3] <= 1.0) for l in (e.get("legs") or []))
            or not (0.2 <= e["entry_base"] <= 3.0) or not (0.0 <= (e.get("entry_imp1") or 0) <= 1.0))
def mirror(t, key, S=1.0, fixed=None):
    """its sales mirrored at our stake, in time order, the fractions capped at our one position (its re-buys make
    rescore2's fractions of its peak add up past 1), each sale K trades behind it (the leg), sales past the 4 priced
    legs at its price x 0.97; costs 0.0095 x (1 + its sales, at most 3) + 1.25% each way"""
    e = t.get(key)
    if not e or broken(e): return None
    imp = 1 + S * (e.get("entry_imp1") or 0.0); ours = e["entry_base"] * imp; cum, x = 0.0, 0.0
    L = {round(l[1], 15): l for l in e.get("legs") or []}
    for i, s in enumerate(sorted(t["sells"], key=lambda s: s["t"])):
        fr = min(s["frac"], 1.0 - cum)
        if fr <= 0: break
        cum += fr; l = L.get(round(s["px"], 15))
        j = t["sells"].index(s)
        x += fr * chain_mult(t, j) * (l[2] / (1 + S * l[3]) if l else 0.97 / imp)
    g = x / ours; n = 1 + min(len(t["sells"]), 3)
    return S * (g - 1 - fee(t) * (1 + g)) - (FIXED if fixed is None else fixed)
def miskeyed(t):
    """keyed on the route's quote token, not the coin: its buy transaction leaves the wallet with (almost) none of the
    'coin' (chain), as on 2-hop routes where the quote is bought and spent in one transaction (another group's finding;
    their test, a symbol equal to another trip's quote, drops real coins named BTC / NVDA / HYPE and misses cbBTC, LLY ...)"""
    c = ch.get(t["sig0"]) or {}
    return (c.get("its_dc") or 0) <= 0.01 * t["peak"]
bad = [t for t in d["trips"] if miskeyed(t)] + [t for t in d["trips"] if t["usd_in"] < 0.10]   # + dust buys (another group's finding)
d["trips"] = [t for t in d["trips"] if not miskeyed(t) and t["usd_in"] >= 0.10]
def clean(pts):
    """drop points 5x off the last kept one (a pool owner shared by several pools mixes their prices: seen 684x)"""
    out = []
    for p in pts:
        ref = out[-1][3] if out else 1.0
        if 0.2 < p[3] / ref < 5 and p[1] < 50: out.append(p)
    return out
for k, v in P.items():
    if v and v.get("pts"): v["pts"] = clean(v["pts"])
ok = [t for t in d["trips"] if t["sells"] and t.get("s2k2") and P.get(t["sig0"])]
p1 = [t for t in ok if t["t0"] < mid]; p2 = [t for t in ok if t["t0"] >= mid]
allp1 = [t for t in d["trips"] if t["sells"] and t["t0"] < mid]
fs = [(chain_mult(t, 0), t["sells"][0]["t"] - t["t0"]) for t in allp1]; n = len(fs)
H, kh = mode([h for _, h in fs], 10, lo=20, share=0.25, n=n)
pre = [(m, h) for m, h in fs if not H or h < H - 30]          # its take profit and stop: first sales before its timer
TPi, kt = mode([m for m, _ in pre], 0.05, lo=1.1, share=0.12, n=len(pre))
SLi, kl = mode([m for m, _ in pre], 0.05, hi=0.95, share=0.10, n=len(pre))
if TPi and kt < 5: TPi = None                                 # a level needs at least 5 trips in its bin
if SLi and kl < 5: SLi = None
win = sorted(m for m, _ in fs if m >= 1.1)
print(f"== {w}: {len(ok)} trips priced with a path (P1 {len(p1)}, P2 {len(p2)}); its P1 first sales {n}; dropped as keyed on a quote token: {[t['sym'] for t in bad]}")
print(f"   its timer {H} ({kh} of {n}); before it ({len(pre)}): its take profit {TPi} ({kt} in the modal bin); its stop {SLi} ({kl}); winning first sales p25/50/75 "
      f"{[round(win[int(q * len(win))], 2) for q in (0.25, 0.5, 0.75)] if win else '-'}")
# where K trades behind lands in slots on this wallet's coins; our live copies (copy2, wallet 4, all 15 sends of Oct 28-29,
# deploy-frankfurt.md §6) landed 7 in its own slot and 8 in the next, so the K whose own-slot share is nearest 47% is the
# landing that matches our live speed (the first 7 sends alone were 5 / 2)
def _slots(key):
    e = [t[key]["entry_slot"] for t in ok if t.get(key) and t[key].get("entry_slot") is not None]
    return (sum(1 for x in e if x == 0) / len(e), sum(1 for x in e if x == 1) / len(e)) if e else (None, None)
_sl = {K_: _slots(key) for K_, key in ((1, "s2k1"), (2, "s2k2"), (4, "s2"), (7, "s2k7"))}
_ok = {K_: v for K_, v in _sl.items() if v[0] is not None}
KM = min(_ok, key=lambda K_: abs(_ok[K_][0] - 7 / 15)) if _ok else None
print("   landing by slot (its slot / next): " + "  ".join(f"K={K_} {v[0]:.0%}/{v[1]:.0%}" for K_, v in _ok.items())
      + f"  | live 47%/53% -> matched K={KM}")
tps = [None] + ([round(TPi * f, 3) for f in (0.6, 0.7, 0.8, 0.9, 1.0)] if TPi else [1.3, 1.5, 2.0, 2.5, 3.0])
sls = [None] + ([round(SLi + x, 3) for x in (0.0, 0.05, 0.1)] if SLi else [0.6, 0.7, 0.8, 0.9])
MAXHOLD = int(os.environ.get("MAXHOLD", "3590"))           # the owner's limit: up to an hour is fine, not days
tms = sorted({x for x in ([H - 10] if H and H - 10 <= MAXHOLD else []) + [300, 1790, MAXHOLD] if x <= MAXHOLD})
med = st.median(its_sol(t) for t in ok) if ok else 0
FIL = {"all": lambda t: True, "quote SOL": lambda t: t["quote"] in ("WSOL", "SOL"), "quote token": lambda t: t["quote"] not in ("WSOL", "SOL"),
       f"its buy >= {med:.2f} SOL": lambda t: its_sol(t) >= med, "its buy >= 1.45 SOL": lambda t: its_sol(t) >= 1.45,
       "1.45+ SOL, token quote": lambda t: its_sol(t) >= 1.45 and t["quote"] not in ("WSOL", "SOL")}
best = None; table = []
for (fn, ff), tp, sl, tm, stake in itertools.product(FIL.items(), tps, sls, tms, STAKES):
    a = [sim(t, "s2k2", tp, sl, tm, stake) for t in p1 if ff(t)]
    a = [x for x in a if x is not None]
    if len(a) < 8: continue
    r = (sum(a), fn, tp, sl, tm, stake, len(a)); table.append(r)
    if not best or r[0] > best[0]: best = r
if not best and not os.environ.get("FIXRULE"): print("   too few trips"); sys.exit()
if not best: best = (0.0, "all", None, None, None, 1.0, 0)
s1, fn, tp, sl, tm, stake, n1 = best; ff = FIL[fn]
if os.environ.get("FIXRULE"):                     # a rule picked on another window, scored here on every trip (out of sample)
    fx = os.environ["FIXRULE"].split("|"); val = lambda x: None if x in ("", "None", "-") else float(x)
    if fx[0].startswith("buy>="):
        lim = float(fx[0][5:]); fn = f"its buy >= {lim:.2f} SOL (fixed)"; ff = lambda t, lim=lim: its_sol(t) >= lim
    else: fn = next(k for k in FIL if k.startswith(fx[0])); ff = FIL[fn]
    tp, sl, tm = val(fx[1]), val(fx[2]), val(fx[3])
    stake = fx[4] if fx[4] in ("its size", "half its size") else float(fx[4])
    for K_, key in ((2, "s2k2"), (1, "s2k1"), (4, "s2"), (7, "s2k7")):
        v = [sim(t, key, tp, sl, tm, stake) for t in ok if ff(t)]; v = [x for x in v if x is not None]
        print(f"   FIXED RULE ({fn}; TP {tp} stop {sl} timer {tm}; stake {stake}) on every trip, K={K_}: {sum(v):+.2f} ({len(v)}) without best 2 {wo2(v):+.2f}"
              + (f"; a trip median {st.median(v):+.3f}" if v else ""))
    import collections as _c
    wk = _c.defaultdict(list)
    for t in ok:
        if ff(t):
            x = sim(t, "s2k2", tp, sl, tm, stake)
            if x is not None: wk[int((t["t0"] - d["t0"]) // (7 * 86400))].append(x)
    print("   by week (K=2):", "  ".join(f"week {k + 1}: {sum(v):+.2f} ({len(v)})" for k, v in sorted(wk.items())))
    sys.exit()
def score(key, fixed=None, K=2, per=p2):
    v = [sim(t, key, tp, sl, tm, stake, fixed, K) for t in per if ff(t)]; v = [x for x in v if x is not None]
    return sum(v), len(v), wo2(v)
b = score("s2k2")
print(f"   picked on P1: {fn}; stake {stake}; TP {tp or '-'} stop {sl or '-'} timer {tm or '-'} s; behind its first sale")
print(f"   K=2: P1 {s1:+.2f} ({n1})  P2 {b[0]:+.2f} ({b[1]})  P2 without best 2 {b[2]:+.2f}  | at 0.003 a round trip: P2 {score('s2k2', 0.003)[0]:+.2f}")
for key, K in (("s2k1", 1), ("s2", 4), ("s2k7", 7)):
    x1 = score(key, K=K, per=p1); x2 = score(key, K=K)
    print(f"   same rule, entry K={K}: P1 {x1[0]:+.2f} ({x1[1]})  P2 {x2[0]:+.2f} ({x2[1]})  P2 w/o 2 {x2[2]:+.2f}")
mir = lambda per, key="s2k2": sum(t[key]["copy"] * 1 for t in per if t.get(key))
mf = lambda per, key="s2k2": [x for x in (mirror(t, key) for t in per) if x is not None]
print(f"   mirror its sales at 1 SOL as rescore2 sums it (K=2): P1 {mir(p1):+.2f}  P2 {mir(p2):+.2f};  K=4: P1 {mir(p1, 's2'):+.2f}  P2 {mir(p2, 's2'):+.2f}")
print(f"   mirror fixed (fractions capped at our position, chain multiples, broken legs dropped), 1 SOL, K=2: P1 {sum(mf(p1)):+.2f} ({len(mf(p1))})  "
      f"P2 {sum(mf(p2)):+.2f} ({len(mf(p2))}) w/o 2 {wo2(mf(p2)):+.2f};  K=4: P1 {sum(mf(p1, 's2')):+.2f}  P2 {sum(mf(p2, 's2')):+.2f} w/o 2 {wo2(mf(p2, 's2')):+.2f}")
nb = sum(1 for t in ok if t.get("s2k2") and broken(t["s2k2"])); nf1 = sum(1 for t in ok if sum(s["frac"] for s in t["sells"]) > 1.02)
print(f"   model checks: broken legs (base < 0.2 or impact > 1 per SOL) {nb}; trips whose sale fractions add past 1 (re-buys) {nf1}")
nf = sum(1 for t in ok if not P[t["sig0"]] or P[t["sig0"]]["src"] != "chain")
print(f"   paths: {len(ok) - nf} chain, {nf} candles")
# best rule per filter on P1, scored on P2 (to see which slice holds up)
print("   best per filter (P1 pick -> P2, w/o best 2):")
for f2 in FIL:
    rs = [r for r in table if r[1] == f2]
    if not rs: continue
    r = max(rs, key=lambda r: r[0]); ff2 = FIL[f2]
    v = [sim(t, "s2k2", r[2], r[3], r[4], r[5]) for t in p2 if ff2(t)]; v = [x for x in v if x is not None]
    print(f"     {f2:22s} TP {r[2] or '-'} stop {r[3] or '-'} timer {r[4] or '-'} stake {r[5]}: P1 {r[0]:+.2f} ({r[6]}) -> P2 {sum(v):+.2f} ({len(v)}) w/o 2 {wo2(v):+.2f}")

for name, (fx, tp_, sl_, tm_, st_) in {"copy2's strategy-A rule": ("1.45+ SOL, token quote", 2.0, 0.8, 1790, 1.0)}.items():
    f3 = FIL[fx]
    a = [sim(t, "s2k2", tp_, sl_, tm_, st_) for t in p1 if f3(t)]; b2 = [sim(t, "s2k2", tp_, sl_, tm_, st_) for t in p2 if f3(t)]
    a = [x for x in a if x is not None]; b2 = [x for x in b2 if x is not None]
    print(f"   {name} ({fx}, TP {tp_} stop {sl_} timer {tm_} s, {st_} SOL): P1 {sum(a):+.2f} ({len(a)}) P2 {sum(b2):+.2f} ({len(b2)}) w/o 2 {wo2(b2):+.2f}")
