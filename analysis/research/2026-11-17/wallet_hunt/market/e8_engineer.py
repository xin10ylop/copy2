# The full engineering of a found wallet's copy, every time (Nov 18, the owner: "buy size, holding time, tp, sell
# pressure, stall, its sell, tested at small increments, all combinations possible, and choosing logically, not only
# computing numbers"). Every combination of:
#   its buy size (min) 0.5 0.6 0.7 0.8 0.9 1.0 1.1 1.2 1.3 1.4 1.5 1.75 2.0 SOL | our price over its price (max) 1.1 1.25 1.5 none
#   take profit 1.5 2 2.5 3 3.5 4 5 6 8 none | time 60 120 180 300 450 600 s
#   sell pressure off or n in {3, 5, 8, 10} over w in {30, 60} s (from 30 s) | stall off 60 90 120 180 240 s
#   its sale: never / early (30-290 s under 1.5x) / always
# Our 0.5 SOL at the three landings (hunt_lib's fills: our buy's weight on the curve, the fee of its trade), 0.0345 SOL a
# round trip, take profit and the 1.5x of the early rule against ITS price (as the live bot), stall once back at its price.
# The choice, by logic: (1) every setting ranked by its WEAKER half (halves by time); (2) smoothed: the mean of its
# neighbours one step either way on each part, so a lone spike cannot win (the middle of a plateau); (3) a part that
# changes nothing within the noise is set to its simplest value; (4) shown: each part varied alone around the choice,
# and the setting picked on the first half alone with its rank on the second (the overfitting check).
# Sources: the 4 days of float-quote coins on disk (paths_full); for TAB16RxX also its 14 earlier days, float-paid
# (tab/lk paths with the bot's scan).
#   python3 -I e8_engineer.py SP WALLET > ../out/e8_<wallet8>.txt
import sys, os, re, json, gzip, itertools, functools, numpy as np
SP, W = sys.argv[1], sys.argv[2]; PAY = os.environ.get("PAY", "float")   # PAY=wsol: only the copies paid from wSOL (the owner: "test with wsol too")
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
rows = []
def add(tr, k, rate, sol, quote8):
    ps = [H.prep(tr, k, rate, n, pmax=1000) for n in (4, 8, "slot+1")]
    prem = float(np.mean([(tr[k]["vt"] / p["ent"][0]) ** 2 for p in ps]))
    rows.append(dict(t=tr[k]["t"], sol=sol, prem=prem, q=quote8, v=np.mean([copy_vals(p) for p in ps], axis=0) - COST))
# source 1: the 4 days of float-quote coins
L = {}
for f_ in (f"{O}/launches_1794618422.json", f"{O}/launches.json", f"{O}/launches_1794877622.json"):
    L.update({m: x for m, x in json.load(open(f_)).items() if x and ((x["quote"][:8] in FLOATS) == (PAY == "float")) and os.path.exists(f"{PD}/{m}.json.gz")})   # PAY=wsol: the coins quoted in a token we hold no float of (reached from SOL when a pool exists)
PR = json.load(open(f"{O}/prices.json")); su = PR[WSOL]["usdPrice"]; rate_of = lambda q: PR[q]["usdPrice"] / su * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None
for m, x in L.items():
    r = rate_of(x["quote"]); tr = json.load(gzip.open(f"{PD}/{m}.json.gz")) if r else []
    k = next((j for j, e in enumerate(tr) if e["user"] == W), None)
    if k is None or not tr[k]["buy"] or tr[-1]["t"] - tr[k]["t"] < 600: continue
    sol = tr[k]["q"] * (1 + tr[k]["bps"] / 1e4) * r / 1e9
    if sol >= 0.5: add(tr, k, r, sol, x["quote"][:8])
# source 2 (TAB16RxX): its 14 earlier days, float-paid, the bot's own routes
if W.startswith("TAB16RxX") and os.path.exists(f"{SP}/tab2/scan_all.out"):
    TD = f"{SP}/tab/lk/paths"; files = {}
    for f in os.listdir(TD):
        s_, m_ = f.split(".")[0].split("_"); files[f"{s_}_{m_[:8]}"] = f
    last = {}
    for l in open(f"{SP}/tab2/scan_all.out"):
        m = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL from (\S+) quote (\S+) jupiter (\S+): ROUTABLE hops (\d+) how (\S+) .*?input: (\w{8})", l)
        if not m or float(m.group(3)) < 0.5 or ((m.group(9) == "So111111") != (PAY == "wsol")): continue
        key = f"{m.group(1)}_{m.group(2)}"
        if key not in files: continue
        tr = SO.reorder(json.load(gzip.open(f"{TD}/{files[key]}"))); k = next((i for i, e in enumerate(tr) if e["user"] == W and e["buy"] and e["slot"] == int(m.group(1))), None)
        if k is None or tr[k]["t"] >= 1794618422: continue
        if m.group(2) in last and tr[k]["t"] - last[m.group(2)] < 3600: last[m.group(2)] = tr[k]["t"]; continue
        last[m.group(2)] = tr[k]["t"]
        add(tr, k, float(m.group(3)) * 1e9 / (tr[k]["q"] * (1 + tr[k]["bps"] / 1e4)), float(m.group(3)), m.group(9))
# source 3 (wallet 4): its research corpus, Oct 21 - Nov 16 (allq / cq / since_stop / newq: every trade for 31 minutes from
# its buy; the rate from routable.json's SOL value), true in-slot order; the 4 days above are then not added twice
if W.startswith("H9kuqGKN"):
    seen = {r["t"] for r in rows}; got = {}
    for d_ in ("allq", "cq", "since_stop", "newq"):
        try: P = json.load(gzip.open(f"{SP}/{d_}/paths.json.gz")); R_ = {f"{r['slot']}_{r['mint8']}": r for r in json.load(open(f"{SP}/{d_}/routable.json"))}
        except Exception: continue
        for kk, vv in P.items():
            if not vv or kk not in R_: continue
            m_, tr = vv
            if m_ in got and got[m_] >= len(tr): continue
            got[m_] = len(tr)
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
            add(tr, k, rate, R_[kk]["sol"], str(R_[kk].get("quote", "?"))[:8])
rows.sort(key=lambda r: r["t"]); T = np.array([r["t"] for r in rows]); tmid = np.median(T) if len(T) else 0
V = np.array([r["v"] for r in rows]); SOL = np.array([r["sol"] for r in rows]); PRM = np.array([r["prem"] for r in rows]); A = T < tmid
import datetime as dt
print(f"{W}: {len(rows)} copies (0.5+ SOL, paid {'from wSOL' if PAY == 'wsol' else 'with a float'}), {dt.datetime.fromtimestamp(T.min(), dt.UTC):%m-%d} to {dt.datetime.fromtimestamp(T.max(), dt.UTC):%m-%d}; halves at {dt.datetime.fromtimestamp(tmid, dt.UTC):%m-%d %H:%M} UTC; 0.0345 SOL a round trip")
# the full grid: [size, prem, tp, hold, sp, stall, its]
full = len(SIZE) * len(PREM) * V[0].size; print(f"combinations: {full:,} ({len(SIZE)} sizes x {len(PREM)} price limits x {V[0].size:,} exits)")
MINN = 12
M1 = np.full((len(SIZE), len(PREM)) + V.shape[1:], np.nan); M2 = M1.copy(); MA = M1.copy(); NN = np.zeros((len(SIZE), len(PREM)), int)
for a, sz in enumerate(SIZE):
    for b_, pm in enumerate(PREM):
        f = (SOL >= sz) & (PRM <= pm); NN[a, b_] = f.sum()
        if (f & A).sum() >= MINN and (f & ~A).sum() >= MINN:
            M1[a, b_] = V[f & A].mean(axis=0); M2[a, b_] = V[f & ~A].mean(axis=0); MA[a, b_] = V[f].mean(axis=0)
weak = np.minimum(M1, M2)
def _edge(shape, d, sh):
    """1 where np.roll along axis d by sh brought a real neighbour, 0 where it wrapped around."""
    m = np.ones(shape); sl = [slice(None)] * len(shape); sl[d] = 0 if sh == 1 else -1; m[tuple(sl)] = 0; return m
# smoothing: the mean of the weaker half over each setting's neighbourhood (one step either way on every part)
ok = ~np.isnan(weak); wf = np.where(ok, weak, 0.0); num = wf.copy(); den = ok.astype(float)
for d in range(weak.ndim):   # the neighbours one step either way on each part (the edges count once)
    for sh in (-1, 1):
        num += np.roll(wf, sh, axis=d) * _edge(weak.shape, d, sh); den += np.roll(ok.astype(float), sh, axis=d) * _edge(weak.shape, d, sh)
smooth = np.where(ok & (den > 0.5 * (1 + 2 * weak.ndim) * 0.5), num / np.maximum(den, 1e-9), -np.inf)
idx = np.unravel_index(int(np.argmax(smooth)), smooth.shape)
def name(ix):
    a, b_, t, h, sp, st, it = ix
    return (f"its buy {SIZE[a]}+ SOL, price limit {'none' if PREM[b_] > 1e8 else str(PREM[b_]) + 'x'}, tp {'none' if TP[t] > 1e8 else str(TP[t]) + 'x'}, {HOLD[h]} s, "
            f"sell pressure {'off' if SPS[sp] is None else f'{SPS[sp][0]}/{SPS[sp][1]}s'}, stall {STALL[st] or 'off'}, its sale {ITS[it]}")
def stats(ix):
    a, b_ = ix[0], ix[1]; f = (SOL >= SIZE[a]) & (PRM <= PREM[b_]); v = V[f][(slice(None),) + tuple(ix[2:])]; s = np.sort(v); k = max(1, round(0.02 * len(v)))
    bs = np.random.default_rng(7).choice(v, size=(5000, len(v))).mean(axis=1)
    return f"{len(v)} copies | half 1 {100 * M1[ix] / 0.5:+.1f}% | half 2 {100 * M2[ix] / 0.5:+.1f}% | all {100 * MA[ix] / 0.5:+.1f}% | w/o 2% {s[:-k].sum():+.2f} SOL | P(mean>0) {100 * np.mean(bs > 0):.1f}%"
print(f"\nsettings positive on both halves: {np.nansum((M1 > 0) & (M2 > 0)):,} of {np.sum(ok):,} with {MINN}+ copies in each half")
print(f"\nTHE CHOICE (the best neighbourhood by the weaker half):\n   {name(idx)}\n   {stats(idx)}\n   its neighbourhood's weaker half: {100 * smooth[idx] / 0.5:+.1f}% a copy")
raw = np.unravel_index(int(np.nanargmax(np.where(ok, weak, -np.inf))), weak.shape)
print(f"\nthe single best weaker half (no smoothing): {name(raw)}\n   {stats(raw)}")
h1 = np.unravel_index(int(np.nanargmax(np.where(ok, M1, -np.inf))), M1.shape)
rank2 = int(np.sum(np.where(ok, M2, -np.inf) > M2[h1])) + 1
print(f"\nthe overfitting check: picked on half 1 alone: {name(h1)}\n   {stats(h1)}\n   its rank on half 2: {rank2:,} of {np.sum(ok):,}")
print("\nEACH PART VARIED ALONE (the others as chosen): half 1 / half 2 / all, a copy")
labels = [("its buy size", [f"{x}+" for x in SIZE]), ("price limit", ["1.1x", "1.25x", "1.5x", "none"]), ("take profit", [("none" if x > 1e8 else f"{x}x") for x in TP]),
          ("time", [f"{x}s" for x in HOLD]), ("sell pressure", ["off"] + [f"{n}/{w}s" for n, w in SPS[1:]]), ("stall", ["off"] + [f"{x}s" for x in STALL[1:]]), ("its sale", ITS)]
for d, (lab, vals) in enumerate(labels):
    print(f"  {lab}:")
    for j, vl in enumerate(vals):
        ix = list(idx); ix[d] = j; ix = tuple(ix)
        if np.isnan(MA[ix]): print(f"     {vl:8s}  too few copies"); continue
        mark = "   <- chosen" if j == idx[d] else ""
        print(f"     {vl:8s}  {100 * M1[ix] / 0.5:+6.1f}% / {100 * M2[ix] / 0.5:+6.1f}% / {100 * MA[ix] / 0.5:+6.1f}%  (copies {NN[ix[0], ix[1]]}){mark}")
