# One candidate, the whole test in one run, staged so a bad wallet costs little (Nov 22; the owner: "run the top 60,
# filter as much as you can ... tp's in increments of 0.1, sell pressure all kinds, stall, holding time in increments, buy
# size and type floats or sol or both, when to sell after its sell and when not or never").
#  1. Its own history, DAYS days (Helius getTransactionsForAddress, successful transactions only, ../2026-11-19/candidates/
#     c1_fetch.py): its result on its own coins by day. STOP if it loses money itself (sum under 0) or is up on under half
#     of its days.
#  2. Seen = its OLDER half of first buys of 0.5+ SOL (up to NSEEN at random), our copy replayed on each coin (Helius,
#     ../2026-11-13/tab_exits/cmodel.py `HELIUS_URL`): 1 SOL landing in the slot after its buy, COST a round trip, a trigger
#     sells on the next trade, every setting of the grid below:
#       take profit (x its price) 1.2 to 5.0 by 0.1, or none (40) | timer 60 to 600 s by 30 (19)
#       sell pressure off, or N of 3 5 8 10 15 more sells than buys by others over W of 30 60 120 s, from 30 s (16)
#       stall (no new high for S s after the price passed our fill) off 60 90 120 180 240 300 (7)
#       its sale: never | always | early 30-290 s under 1.5x (live) | 30-290 s any price | 0-60 s | 0-120 s (6)
#       its buy at least 0.5 1.0 1.3 2.0 SOL (4) x the coin's quote: all | SOL | a token (a float) (3)
#       price limit (our fill / its price) 1.25 1.5 2.0 none (4)     = 24,514,560 settings
#     The pick: the most SOL on the seen half without its best 2% of copies, smoothed over each exit setting's neighbours
#     (one step either way on each of the five exit axes) so a lone spike is not picked. STOP if the pick is not above 0.
#  3. Unseen = its NEWER half (up to NUNSEEN at random), scored once with the seen pick (blind), and the live setting.
# With 24.5 million settings the seen half is always flattering: only the unseen line is evidence.
#   HELIUS_URL=... RPC_URL=... LK=SP/lk COST=0.0064 python3 -I w2_grid.py SP WALLET [NSEEN=60] [NUNSEEN=60] [DAYS=14]
import sys, os, json, random, collections, subprocess, datetime as dt, itertools, numpy as np, concurrent.futures as cf
SP, W = sys.argv[1], sys.argv[2]; NSEEN = int(sys.argv[3]) if len(sys.argv) > 3 else 60; NUN = int(sys.argv[4]) if len(sys.argv) > 4 else 60
DAYS = float(sys.argv[5]) if len(sys.argv) > 5 else 14
COST = float(os.environ.get("COST", 0.0345)); STAKE = 1.0; SOLM = "So11111111111111111111111111111111111111112"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../2026-11-13/tab_exits")); import cmodel as M
sys.path.insert(0, os.path.join(HERE, "../../2026-11-17/wallet_hunt")); import hunt_lib as H
C1 = os.path.join(HERE, "../../2026-11-19/candidates/c1_fetch.py")
def jup_prices(qs):
    import urllib.request, time
    P = {}
    for i in range(0, len(qs), 40):
        for a in range(4):
            try:
                P.update({k: v for k, v in json.load(urllib.request.urlopen("https://lite-api.jup.ag/price/v3?ids=" + ",".join(qs[i:i + 40] + [SOLM]), timeout=20)).items() if v}); break
            except Exception: time.sleep(5 * (a + 1))
    return P
# 1. its own history
sub = f"hist_{W[:8]}"; D = f"{SP}/{sub}"
if not os.path.exists(f"{D}/{W[:8]}_trades.jsonl"):
    r_ = subprocess.run([sys.executable, "-I", C1, SP, str(DAYS)], env={**os.environ, "SUB": sub, "WALLETS": W}, capture_output=True, text=True)
    cap = [l for l in r_.stdout.splitlines() if "CAPPED" in l]
    if cap: print(cap[0])
trades = [e for l in open(f"{D}/{W[:8]}_trades.jsonl") for e in (json.loads(l)["trades"] or [])]
sigs = sorted((t, s) for s, t in json.load(open(f"{D}/{W[:8]}_sigs.json")))
by = collections.defaultdict(list)
for e in trades: by[e["m"]].append(e)
P = jup_prices(sorted({e["quote"] for e in trades if e["quote"] and not e["quote"].startswith("1111")})); su = P.get(SOLM, {}).get("usdPrice")
rate_of = lambda q: 1.0 if not q or q.startswith("1111") else (P[q]["usdPrice"] / su * 1e9 / 10 ** P[q]["decimals"] if su and q in P and P[q].get("decimals") is not None else None)
day = collections.defaultdict(float); firsts = []
for m, es in by.items():
    es.sort(key=lambda e: (e["slot"], not e["buy"]))
    if not es[0]["buy"]: continue
    r = rate_of(es[0]["quote"])
    if r is None: continue
    day[dt.datetime.fromtimestamp(es[0]["t"], dt.UTC).strftime("%m-%d")] += sum((-1 if e["buy"] else 1) * e["q"] * r / 1e9 for e in es)
    if es[0]["q"] * r / 1e9 >= 0.5 and sigs and es[0]["t"] < sigs[-1][0] - 700:
        firsts.append(dict(m=m, slot=es[0]["slot"], t=es[0]["t"], rate=r, sol=es[0]["q"] * r / 1e9, tok=not (not es[0]["quote"] or es[0]["quote"].startswith("1111"))))
ds = sorted(day.items()); up = sum(1 for _, v in ds if v > 0); own = sum(day.values())
print(f"{W}: own result {own:+.2f} SOL over {len(ds)} days, up on {up}; {len(firsts)} first buys of 0.5+ SOL")
print("  by day: " + "  ".join(f"{d} {v:+.2f}" for d, v in ds))
if (own <= 0 or up < len(ds) / 2) and not os.environ.get("NOSTOP"):   # NOSTOP=1 (Nov 25): test the copies anyway
    print("STOP: it does not make money itself on most days"); sys.exit()
# 2-3. the grid on the seen half, then the unseen half
TP = [None] + [round(1.2 + 0.1 * i, 1) for i in range(39)]; HOLD = list(range(60, 601, 30))
SPS = [None] + [(n, w) for n in (3, 5, 8, 10, 15) for w in (30, 60, 120)]; STALL = [0, 60, 90, 120, 180, 240, 300]
ITS = [("never",), ("always",), ("early", 30, 290, 1.5), ("early", 30, 290, 1e9), ("early", 0, 60, 1e9), ("early", 0, 120, 1e9)]
MINS = [0.5, 1.0, 1.3, 2.0]; KINDS = ["all", "SOL", "token"]; LIMS = [1.25, 1.5, 2.0, 1e9]
SH = (len(TP), len(HOLD), len(SPS), len(STALL), len(ITS)); NS = int(np.prod(SH))
LIVE = (TP.index(4.0), HOLD.index(600), SPS.index((5, 60)), STALL.index(180), 2)
def first(c):
    i = int(np.argmax(c)) if len(c) else 0
    return i if len(c) and c[i] else None
def grid(c, tr):
    k = next((i for i, e in enumerate(tr) if e["user"] == W and e["buy"] and e["slot"] == c["slot"]), None)
    if k is None: return None
    p = H.prep(tr, k, c["rate"], "slot+1", pmax=1e9)
    if not len(p["px"]): return None
    vt0, vq0, b0 = p["ent"]; prem = (tr[k]["vt"] / vt0) ** 2
    Q = STAKE * 1e9 / c["rate"]; net_in = Q * 1e4 / (1e4 + b0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq_r = p["vq"] + net_in; vt_r = p["vt"] * p["vq"] / vq_r
    val = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - p["bps"] / 1e4) * c["rate"] / 1e9 - STAKE - COST
    px, age, n = p["px"], p["age"], len(p["px"]); BIG = 10 ** 9
    trig = lambda i: BIG if i is None else min(i + 1, n - 1); at = lambda i: BIG if i is None else i
    tp_i = np.array([trig(first(px >= t)) if t else BIG for t in TP]); h_i = np.array([at(first(age >= h)) for h in HOLD])
    s = np.concatenate([[0], np.cumsum(p["osell"])]); b = np.concatenate([[0], np.cumsum(p["obuy"])]); sp_i = []
    for sp in SPS:
        if sp is None: sp_i.append(BIG); continue
        lo = np.searchsorted(age, age - sp[1], side="left"); sp_i.append(trig(first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= sp[0]) & (age >= 30))))
    pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
    st_i = np.array([BIG if st == 0 else trig(first((pk >= prem) & (age - lasthi >= st))) for st in STALL])
    it_i = np.array([BIG if r_[0] == "never" else trig(first(p["sell"])) if r_[0] == "always" else
                     trig(first(p["sell"] & (age >= r_[1]) & (age < r_[2]) & (px < r_[3]))) for r_ in ITS])
    E = np.full(SH, min(at(first(p["grad"])), n - 1), dtype=np.int64)
    for arr in (tp_i[:, None, None, None, None], h_i[None, :, None, None, None], np.array(sp_i)[None, None, :, None, None],
                st_i[None, None, None, :, None], it_i[None, None, None, None, :]):
        E = np.minimum(E, arr)
    return dict(g=val[np.minimum(E, n - 1)].astype(np.float32).ravel(), prem=prem, sol=c["sol"], tok=c["tok"], t=c["t"])
def fetch(cs):
    anchor = lambda c: next((s for t, s in sigs if t >= c["t"] + 640), sigs[-1][1])
    with cf.ThreadPoolExecutor(int(os.environ.get("PATHS_AT_ONCE", 3))) as ex: paths = list(ex.map(lambda c: M.path(c["m"], c["slot"], anchor(c), threads=8), cs))
    return [g for g in (grid(c, tr) for c, tr in zip(cs, paths)) if g]
def stackg(rows): return np.stack([r_["g"] for r_ in rows])
def masked(rows, G, f):
    """setting values a copy (copies x settings) under one filter (its buy SOL floor, quote kind, price limit):
    a copy not taken counts 0, a refused buy -0.0004"""
    mn, kd, lim = f
    keep = np.array([r_["sol"] >= mn and (kd == "all" or (kd == "token") == r_["tok"]) for r_ in rows])
    ref = np.array([r_["prem"] > lim for r_ in rows])
    return np.where((keep & ~ref)[:, None], G, np.where((keep & ref)[:, None], np.float32(-0.0004), np.float32(0))), keep
FILTERS = list(itertools.product(MINS, KINDS, LIMS))
def wo2(V, n):
    k = max(1, round(0.02 * n)); return V.sum(0) - np.sort(np.partition(V, -k, axis=0)[-k:], axis=0).sum(0)
def smooth(v):
    a = v.reshape(SH); acc = a.copy(); cnt = 1
    for ax in range(5):
        if SH[ax] < 2: continue
        pad = np.concatenate([a.take([0], ax), a, a.take([-1], ax)], axis=ax)
        acc = acc + pad.take(range(0, SH[ax]), ax) + pad.take(range(2, SH[ax] + 2), ax); cnt += 2
    return (acc / cnt).ravel()
def name(f, j):
    tp, h, sp, st, it = (L_[i] for L_, i in zip((TP, HOLD, SPS, STALL, ITS), np.unravel_index(j, SH)))
    mn, kd, lim = f
    its = it[0] if it[0] != "early" else f"its sale {it[1]}-{it[2]} s" + (f" under {it[3]}x" if it[3] < 1e8 else "")
    return (f"tp {tp or 'none'}, {h} s, sell pressure {f'{sp[0]}/{sp[1]} s' if sp else 'off'}, stall {st or 'off'}, {its}; "
            f"its buy {mn}+ SOL, {kd} coins, limit {lim if lim < 1e8 else 'none'}x")
firsts.sort(key=lambda c: c["t"]); h = len(firsts) // 2
older, newer = firsts[:h], firsts[h:]; random.seed(7); random.shuffle(older); random.shuffle(newer)
seen = fetch(older[:NSEEN])
print(f"seen: {len(seen)} copies (its older {len(older)} first buys, {dt.datetime.fromtimestamp(firsts[0]['t'], dt.UTC):%m-%d} on), {len(TP) * len(HOLD) * len(SPS) * len(STALL) * len(ITS) * 48:,} settings")
if len(seen) < 10: print("STOP: under 10 seen copies"); sys.exit()
best = None; Gs = stackg(seen)
for f in FILTERS:
    V, keep = masked(seen, Gs, f)
    if keep.sum() < 10: continue
    w = wo2(V, keep.sum()); sm = smooth(w); j = int(np.argmax(sm))
    if best is None or sm[j] > best[0]: best = (sm[j], f, j, w[j], V[:, j].sum(), int(keep.sum()))
sm_, f, j, w_, s_, n_ = best
print(f"seen pick (smoothed): {name(f, j)}")
print(f"  seen: {s_:+.3f} SOL on {n_} copies ({100 * s_ / n_:+.1f}% a copy), without its best 2% {w_:+.3f}, its neighbours' mean {sm_:+.3f}")
lj = np.ravel_multi_index(LIVE, SH); Vl, kl = masked(seen, Gs, (1.3, "all", 1.5))
print(f"  the live setting on the seen half: {Vl[:, lj].sum():+.3f} SOL on {int(kl.sum())} copies")
if sm_ <= 0:
    print("STOP: the smoothed pick is not above 0 on the seen half"); sys.exit()
un = fetch(newer[:NUN])
if not un: print("no unseen copies"); sys.exit()
Gu = stackg(un); Vu, ku = masked(un, Gu, f); Vlu, klu = masked(un, Gu, (1.3, "all", 1.5)); n_u = int(ku.sum())
vu = Vu[:, j][ku]; srt = np.sort(vu)
print(f"unseen: {len(un)} copies; the seen pick on {n_u}: {vu.sum():+.3f} SOL ({100 * vu.mean():+.1f}% a copy), without its best 2% "
      f"{srt[:-max(1, round(0.02 * n_u))].sum():+.3f}; the live setting {Vlu[:, lj].sum():+.3f} SOL on {int(klu.sum())}")
print("RESULT: " + ("PASS (positive unseen, also without its best 2%)" if vu.sum() > 0 and srt[:-max(1, round(0.02 * n_u))].sum() > 0 else "FAIL"))
