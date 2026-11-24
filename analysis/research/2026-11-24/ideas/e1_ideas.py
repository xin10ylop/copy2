# Can anything make each copied wallet better? (Nov 24; the owner: "for all the wallets, individually, check if there is
# anything to make it better ... buy pressure, the dip thing ... if some coins revive after we sell"). One wallet a run:
# its first buys (w2_grid.py's history; wallet 4: its 1.3+ SOL buys of token coins, as its unit copies), the cached coin paths only (its buy to ~375 s
# after: the Helius fetch stops 1,750 slots on), our copy at the end of the slot after its buy, 1 SOL, COST a round trip,
# refused over 1.5x its price. The unit's live exit is the baseline (simulated here; checked against w2_grid's value).
# The menu, fixed before any result:
#  P  buy pressure: wait S = 3/5/10/20 s after its buy; enter at the next trade only if other buys minus other sells
#     since its buy >= K = 3/6/10, else skip; then the live exit (12)
#  D  the dip entry instead of the copy: the price at or under (1 - d) of its price within 60 s, d = 10/20/30%: buy
#     there; exit the live exit, or wallet 4's dip leg (tp 1.5x our fill, to the path's end) (6)
#  T  a trailing stop on the live exit: armed at a peak of 1.5x / 2x its price, out when the price is (1 - f) of the
#     peak, f = 25/40% (4)
#  R  revival: after a live exit that is not the take profit, buy again when the price passes the highest it made while
#     we held, before the path ends; out at 1.5x that fill or the path's end (1, added to the copy); and how often the
#     price after our exit reaches 1.5x / 2x our exit price within the path
# Each variant against the baseline, copy by copy: SOL in all, in each of 4 time blocks, without the best 2%.
#   LK=SP/lk COST=0.0064 python3 -I e1_ideas.py SP WALLET UNIT     (UNIT: w4 | cq | all | token)
import sys, os, json, glob, gzip, numpy as np, datetime as dt
SP, W, UNIT = sys.argv[1], sys.argv[2], sys.argv[3]
TS = "/home/user/copy2/analysis/research/2026-11-20/tape_screen"
sys.argv = [sys.argv[0], SP, W, "0", "0", "14"]
src = open(f"{TS}/w2_grid.py").read().split("firsts.sort(key=lambda c: c[\"t\"]); h = len(firsts) // 2")[0]
src = src.replace('print("STOP: it does not make money itself on most days"); sys.exit()', 'pass')
# Nov 24 (uncopied groups): a lower buy floor (MINSOL), a band of its buy (BAND = lo,hi) and the coin's quote (QUOTE prefix)
src = src.replace('if es[0]["q"] * r / 1e9 >= 0.5 and', 'if es[0]["q"] * r / 1e9 >= float(os.environ.get("MINSOL", 0.5)) and')
g = {"__file__": f"{TS}/w2_grid.py", "__name__": "__main__"}
exec(compile(src, "w2_grid", "exec"), g)
firsts, COST, LK = g["firsts"], float(os.environ.get("COST", 0.0064)), os.environ["LK"]
if UNIT == "w4": firsts = [c for c in firsts if c["sol"] >= 1.3 and c["tok"]]   # its unit copies token coins only (copy_sol_coins off)
if UNIT == "token": firsts = [c for c in firsts if c["tok"]]
firsts.sort(key=lambda c: c["t"])
EXIT = {"w4": dict(tp=4.0, hold=600, sp=(5, 60), stall=180, early=(30, 290, 1.5)),
        "x": dict(tp=3.0, hold=420, sp=None, stall=240, early=None), "sol": dict(tp=2.0, hold=120, sp=None, stall=0, early=None)}
def ex_for(c): return EXIT["w4"] if UNIT == "w4" else EXIT["sol"] if (UNIT == "cq" and not c["tok"]) else EXIT["x"]
if os.environ.get("SOLX"):   # CqCAzte8's SOL-coin exit to try instead of tp 2x / 120 s: "tp,hold,stall"
    _tp, _h, _st = (float(x) for x in os.environ["SOLX"].split(",")); EXIT["sol"] = dict(tp=_tp, hold=_h, sp=None, stall=_st, early=None)
if os.environ.get("SOL_ONLY"): firsts = [c for c in firsts if not c["tok"]]
if os.environ.get("BAND"):
    _lo, _hi = (float(x) for x in os.environ["BAND"].split(",")); firsts = [c for c in firsts if _lo <= c["sol"] < _hi]
if os.environ.get("QUOTE"):
    _q = {m: sorted(es, key=lambda e: (e["slot"], not e["buy"]))[0]["quote"] or "" for m, es in g["by"].items()}
    firsts = [c for c in firsts if _q.get(c["m"], "").startswith(os.environ["QUOTE"])]
if os.environ.get("T_MIN"): firsts = [c for c in firsts if c["t"] > float(os.environ["T_MIN"])]   # buys after a time only (a blind check)
def copy(c, tr):
    k = next((i for i, e in enumerate(tr) if e["user"] == W and e["buy"] and e["slot"] == c["slot"]), None)
    if k is None: return None
    its = tr[k]; vta, t0 = its["vt"], its["t"]; rate = c["rate"]
    j = k + len([e for e in tr[k + 1:] if e["slot"] <= its["slot"] + 1])
    if j + 1 >= len(tr) - 1: return None
    T = tr[k:]                                                     # T[0]: its own buy (the state our entry may meet)
    px = np.array([(vta / e["vt"]) ** 2 for e in T]); age = np.array([e["t"] - t0 for e in T], float)
    ob = np.array([e["user"] != W and e["buy"] for e in T]); os_ = np.array([e["user"] != W and not e["buy"] for e in T])
    mine = np.array([e["user"] == W and not e["buy"] for e in T]); grad = np.array([e.get("real") == 0 for e in T])
    n = len(T); j0 = j - k                                        # our entry, an index into T
    def val(a, b):                                                # buy at T[a]'s state, sell at T[b]'s
        ea, eb = T[a], T[min(b, n - 1)]
        net_in = 1e9 / rate * 1e4 / (1e4 + ea["bps"]); tok = ea["vt"] - ea["vt"] * ea["vq"] / (ea["vq"] + net_in)
        vq_r = eb["vq"] + net_in; vt_r = eb["vt"] * eb["vq"] / vq_r
        return (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - eb["bps"] / 1e4) * rate / 1e9 - 1.0 - COST
    first = lambda m: int(np.argmax(m)) if m.any() else None
    cs, cb = np.concatenate([[0], np.cumsum(os_)]), np.concatenate([[0], np.cumsum(ob)])
    def live_exit(a, X, trail=None):
        """the exit index after an entry at T[a] under exit X (tp and stall against its price, hold from its buy)"""
        idx = np.arange(n); after = idx > a; c_ = []
        c_.append((first(after & (px >= X["tp"])), 1))
        c_.append((first(after & (age >= X["hold"])), 0))
        c_.append((first(after & grad), 0))
        if X["sp"]:
            lo = np.searchsorted(age, age - X["sp"][1], side="left")
            c_.append((first(after & (((cs[1:] - cs[lo]) - (cb[1:] - cb[lo])) >= X["sp"][0]) & (age >= 30)), 1))
        pk = np.maximum.accumulate(np.where(after, px, 0)); prem = px[a]
        if X["stall"]:
            newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
            c_.append((first(after & (pk >= prem) & (age - lasthi >= X["stall"])), 1))
        if X["early"]:
            e0, e1, eb = X["early"]; c_.append((first(after & mine & (age >= e0) & (age < e1) & (px < eb)), 1))
        if trail:
            arm, f = trail; c_.append((first(after & (pk >= arm) & (px <= pk * (1 - f))), 1))
        c_ = [(i + d, d) for i, d in c_ if i is not None]
        if not c_: return n - 1, "end"
        i, d = min(c_); return min(i, n - 1), ("tp" if d and px[i - d] >= X["tp"] else "other")
    X = ex_for(c)
    if px[j0] > 1.5: return dict(ref=True, t=c["t"])
    e, why = live_exit(j0, X); base = val(j0, e)
    out = dict(ref=False, t=c["t"], base=base, why=why)
    for S in (3, 5, 10, 20):                                      # P: buy pressure
        a = first(age >= S)
        for K in (3, 6, 10):
            if a is None: out[f"P {S}s >={K}"] = 0.0; continue
            press = cb[a + 1] - cs[a + 1]
            out[f"P {S}s >={K}"] = val(a, live_exit(a, X)[0]) if press >= K and px[a] <= 1.5 else 0.0
    for d in (0.1, 0.2, 0.3):                                      # D: the dip entry
        a = first((np.arange(n) > j0) & (age <= 60) & (px <= 1 - d))
        if a is None: out[f"D {int(d * 100)}% live"] = out[f"D {int(d * 100)}% leg"] = 0.0; continue
        out[f"D {int(d * 100)}% live"] = val(a, live_exit(a, X)[0])
        b = first((np.arange(n) > a) & (px >= 1.5 * px[a])); out[f"D {int(d * 100)}% leg"] = val(a, (b + 1) if b is not None else n - 1)
    for arm in (1.5, 2.0):                                        # T: a trailing stop
        for f in (0.25, 0.4): out[f"T {arm}x -{int(f * 100)}%"] = val(j0, live_exit(j0, X, trail=(arm, f))[0])
    r_ = 0.0; out["rev15"] = out["rev20"] = False                 # R: revival
    if why != "tp" and e < n - 2:
        hi = px[j0:e + 1].max(); later = px[e + 1:]
        out["rev15"], out["rev20"] = bool((later >= 1.5 * px[e]).any()), bool((later >= 2 * px[e]).any())
        a = first((np.arange(n) > e) & (px > hi))
        if a is not None:
            b = first((np.arange(n) > a) & (px >= 1.5 * px[a])); r_ = val(a, (b + 1) if b is not None else n - 1)
        out["R_n"] = a is not None
    out["R"] = base + r_
    return out
if os.environ.get("FETCH"):   # fetch the missing paths by RPC (no Helius) out to ANCHOR_S after its buy (Nov 24: 1,300 s, so
    # wallet 4's 600 s exit and a revival after it are inside the path; the Helius paths stop ~375 s after)
    import concurrent.futures as cf_
    AS = float(os.environ.get("ANCHOR_S", 1300)); sg = g["sigs"]
    anc = lambda c: next((s_ for t_, s_ in sg if t_ >= c["t"] + AS), sg[-1][1])
    todo = [c for c in firsts if not glob.glob(f"{LK}/paths/{c['slot']}_{c['m']}.json.gz") and c["t"] < sg[-1][0] - AS]
    with cf_.ThreadPoolExecutor(int(os.environ.get("PATHS_AT_ONCE", 8))) as ex_: list(ex_.map(lambda c: g["M"].path(c["m"], c["slot"], anc(c), threads=8), todo))
rows = []
for c in firsts:
    fs = glob.glob(f"{LK}/paths/{c['slot']}_{c['m']}.json.gz")
    if not fs: continue
    r = copy(c, json.load(gzip.open(fs[0])))
    if r: rows.append(r)
ok = [r for r in rows if not r["ref"]]
print(f"{W[:8]} ({UNIT}): {len(rows)} copies with a cached path of {len(firsts)} first buys; refused {len(rows) - len(ok)}; "
      f"{dt.datetime.fromtimestamp(rows[0]['t'], dt.UTC):%m-%d} to {dt.datetime.fromtimestamp(rows[-1]['t'], dt.UTC):%m-%d}")
B = np.array([r["base"] for r in ok]); blocks = np.array_split(np.arange(len(ok)), 4)
def wo2(v):
    k = max(1, round(0.02 * len(v))); return v.sum() - np.sort(v)[-k:].sum()
print(f"  baseline (the unit's live exit): {100 * B.mean():+.1f}% a copy, {B.sum():+.2f} SOL at 1 SOL, without the best 2% {wo2(B):+.2f}; "
      f"blocks " + " / ".join(f"{100 * B[b].mean():+.1f}" for b in blocks) + f"; exits: tp {sum(r['why'] == 'tp' for r in ok)}")
keys = [k_ for k_ in ok[0] if k_[:2] in ("P ", "D ", "T ") or k_ == "R"]
print(f"  {'variant':16s} {'SOL':>7s} {'vs base':>8s} {'w/o 2%':>7s} {'vs base':>8s}  blocks better   taken")
cands = []
for k_ in keys:
    V = np.array([r[k_] for r in ok]); dif = V - B
    bb = sum(1 for b in blocks if V[b].sum() > B[b].sum()); taken = int(np.sum(V != 0)) if k_[0] in "PD" else len(V)
    flag = " <- better in 4 of 4 and without the best 2%" if bb == 4 and wo2(V) > wo2(B) else (" <- 3 of 4" if bb == 3 and wo2(V) > wo2(B) else "")
    if flag: cands.append(k_)
    print(f"  {k_:16s} {V.sum():+7.2f} {dif.sum():+8.2f} {wo2(V):+7.2f} {wo2(V) - wo2(B):+8.2f}  {bb} of 4         {taken:4d}{flag}")
# the dip as an EXTRA leg beside the copy (how wallet 4's leg 2 ran, Nov 19-20): its own trades, block by block
for k_ in [k_ for k_ in keys if k_.startswith("D ")]:
    V = np.array([r[k_] for r in ok]); per = [V[b][V[b] != 0] for b in blocks]; t_ = V[V != 0]
    if len(t_): print(f"  extra leg {k_[2:]:9s} {len(t_):4d} trades {100 * t_.mean():+6.1f}% a trade, {t_.sum():+6.2f} SOL, w/o 2% {wo2(t_):+6.2f}; by block "
                      + " / ".join(f"{100 * p_.mean():+.1f}% ({len(p_)})" if len(p_) else "-" for p_ in per))
rv = [r for r in ok if r["why"] != "tp" and "R_n" in r]
if rv:
    print(f"  revival after a non-tp exit, within the path (~375 s after its buy): {len(rv)} exits with trades after; the price later "
          f"reached 1.5x our exit price on {np.mean([r['rev15'] for r in rv]):.0%}, 2x on {np.mean([r['rev20'] for r in rv]):.0%}; "
          f"the re-buy rule fired on {sum(r['R_n'] for r in rv)}")
print("  CANDIDATES: " + (", ".join(cands) if cands else "none"))
