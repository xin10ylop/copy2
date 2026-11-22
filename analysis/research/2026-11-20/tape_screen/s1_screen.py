# The wallet screen on the pump tape (Nov 20; the owner: "do a study until now so we know what to do in a couple of
# days"). Reads the recorder's hourly files (tape/t1_record.py: every pump curve trade, in arrival order) in one pass,
# keeping only the last ~31 minutes of each coin that some wallet bought into, so two days of tape fit in a few hundred MB.
# For every wallet's FIRST buy of a coin of MIN_SOL+ (non-SOL quotes valued at Jupiter's price now), our copy: STAKE SOL
# landing at the end of the slot after its buy, refused over 1.5x its price, 0.0345 SOL a round trip, and five fixed
# exits (no fitting per wallet):
#   w4   = wallet 4's live exit: tp 4x its price, 600 s, 5+ more sells than buys over 60 s (from 30 s), stall 180 s from our
#          fill, its sale followed 30-290 s under 1.5x
#   its  = sell when it sells (its first sale), else 600 s
#   tp2  = tp 2x, 120 s        held = 300 s        scalp = tp 1.5x, 60 s
# Per wallet: copies, each exit's mean in each half of the tape (by time). The pick: the exit best on the FIRST half,
# scored on the SECOND (blind). Also the pooled mean of every copy (what a random wallet gives) and wallet 4's line.
#   python3 -I s1_screen.py TAPE_DIR [MIN_SOL=0.5] [MIN_COPIES=10] > screen.txt     (on the box: nice -n 19)
import sys, os, json, gzip, glob, heapq, collections, urllib.request, numpy as np
MIN_HOLD = float(os.environ.get("MIN_HOLD", 20))   # wallets whose median holding (buy to its first sale) is shorter: speed traders, left out
D = sys.argv[1]; MIN_SOL = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5; MINN = int(sys.argv[3]) if len(sys.argv) > 3 else 10
STAKE, PMAX, WIN = 0.5, 1.5, 1860
COST = float(os.environ.get("COST", 0.0345))   # the convention; the live bot pays ~0.0064 a round trip (journal: paid -0.0032 a buy)
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; SOLQ = "11111111111111111111111111111111"; WSOL = "So11111111111111111111111111111111111111112"
files = sorted((f for f in glob.glob(f"{D}/tape_*.jsonl*") if "broken" not in f), key=lambda f: (os.path.basename(f).split("_")[1], f))
def rows():
    for f in files:
        op = gzip.open if f.endswith(".gz") else open
        try:
            with op(f, "rt") as fh:
                for l in fh:
                    try: r = json.loads(l)
                    except Exception: continue          # a line cut by a restart
                    if r.get("k") == "t" and 1.7e9 < (r.get("ts") or 0) < 1.9e9: yield r   # a few events decode a wrong time
        except EOFError: pass                           # the hour being written
# quote token prices (SOL per raw unit), once
quotes = collections.Counter()
for i, r in enumerate(rows()):
    if r["quote_mint"] != SOLQ: quotes[r["quote_mint"]] += 1
    if i > 3_000_000: break
RATE = {SOLQ: 1.0}
ids = [q for q, _ in quotes.most_common(200)]
# Jupiter's prices, retried, and kept in a file: a run whose fetch fails (HTTP 429) uses the last good prices instead of
# silently leaving every token coin out (Nov 21: a run counted 97,670 copies against 151,229 the run before)
PC = os.environ.get("PRICE_CACHE", "/tmp/tape_prices.json")
pr = {}
for i in range(0, len(ids), 40):
    for attempt in range(4):
        try:
            pr.update({k: v for k, v in json.load(urllib.request.urlopen("https://lite-api.jup.ag/price/v3?ids=" + ",".join(ids[i:i + 40] + [WSOL]), timeout=20)).items() if v})
            break
        except Exception: __import__("time").sleep(3 * (attempt + 1))
old = {}
try: old = json.load(open(PC))
except Exception: pass
for k, v in old.items(): pr.setdefault(k, v)
try: json.dump(pr, open(PC, "w"))
except Exception: pass
su = (pr.get(WSOL) or {}).get("usdPrice")
for q in ids:
    v = pr.get(q) or {}
    if su and v.get("usdPrice") and v.get("decimals") is not None: RATE[q] = v["usdPrice"] / su * 1e9 / 10 ** v["decimals"]
print(f"prices: {len(RATE) - 1} of the {len(ids)} commonest quote tokens priced", file=sys.stderr)
# one pass: per coin the trades since its oldest open watch; a watch = (wallet, coin, index of its buy)
buf = collections.defaultdict(list); watches = collections.defaultdict(list); due = []; seen = set(); out = []
def tup(r):
    q = r["quote_amount"] or 0; b = r["fee_bps"] or 0
    return (r["slot"], r["ts"], r["user"], bool(r["is_buy"]), q, r["vtok"], r["vquote"], b + 1e4 * (r["creator_fee"] or 0) / max(1, q))
def first(m):
    i = np.flatnonzero(m); return int(i[0]) if len(i) else None
def model(tr, k, rate, user):
    s0 = tr[k][0]; j = k
    while j + 1 < len(tr) and tr[j + 1][0] <= s0 + 1: j += 1
    if j == k or j >= len(tr) - 1: return None
    vta = tr[k][5]; ent = tr[j]; prem = (vta / ent[5]) ** 2
    if prem > PMAX: return "refused"
    rest = tr[j + 1:]; t0 = tr[k][1]
    vt = np.array([e[5] for e in rest], float); vq = np.array([e[6] for e in rest], float); bps = np.array([e[7] for e in rest], float)
    age = np.array([e[1] - t0 for e in rest], float); px = (vta / vt) ** 2; n = len(rest)
    Q = STAKE * 1e9 / rate; net_in = Q * 1e4 / (1e4 + ent[7]); tok = ent[5] - ent[5] * ent[6] / (ent[6] + net_in)
    vq_r = vq + net_in; vt_r = vt * vq / vq_r
    val = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - bps / 1e4) * rate / 1e9 - STAKE - COST
    its_sell = np.array([e[2] == user and not e[3] for e in rest]); other = np.array([e[2] != user for e in rest])
    sell = np.array([not e[3] for e in rest])
    BIG = 10 ** 9; trig = lambda i: BIG if i is None else min(i + 1, n - 1); at = lambda i: BIG if i is None else i
    tm = lambda h: at(first(age >= h))
    s = np.concatenate([[0], np.cumsum(other & sell)]); b = np.concatenate([[0], np.cumsum(other & ~sell)])
    lo = np.searchsorted(age, age - 60, side="left"); sp = trig(first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= 5) & (age >= 30)))
    pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
    st = trig(first((pk >= prem) & (age - lasthi >= 180)))
    early = trig(first(its_sell & (age >= 30) & (age < 290) & (px < 1.5))); its = trig(first(its_sell))
    ex = {"w4": min(trig(first(px >= 4)), tm(600), sp, st, early, n - 1), "its": min(its, tm(600), n - 1),
          "tp2": min(trig(first(px >= 2)), tm(120), n - 1), "held": min(tm(300), n - 1), "scalp": min(trig(first(px >= 1.5)), tm(60), n - 1)}
    o = {k_: float(val[i]) for k_, i in ex.items()}; fi = first(its_sell); o["held"] = o["held"]; o["_its_hold"] = float(age[fi]) if fi is not None else 9e9
    return o
EX = ["w4", "its", "tp2", "held", "scalp"]
def settle(now):
    while due and due[0][0] <= now:
        _, m, wid = heapq.heappop(due)
        w = watches[m].pop(0) if watches[m] and watches[m][0][3] == wid else None
        if w is None:
            ws = watches[m]; idx = next((i for i, x in enumerate(ws) if x[3] == wid), None)
            if idx is None: continue
            w = ws.pop(idx)
        user, k, t0, _, rate, sol = w; tr = buf[m]
        r = model(tr, k, rate, user)
        if r is not None: out.append((user, t0, sol, r, m, rate == 1.0))
        if watches[m]:   # trim the coin's buffer to its oldest open watch
            cut = min(x[1] for x in watches[m])
            if cut > 0:
                buf[m] = tr[cut:]
                watches[m] = [(u, kk - cut, t, i, ra, so) for u, kk, t, i, ra, so in watches[m]]
        else: del buf[m]; del watches[m]
own = {}   # (wallet, coin) -> [SOL in, SOL out, tokens in, tokens out]
# launch bundles (Nov 21, GYhRMtoD: +249.94 SOL itself in 5 days, every buy in the coin's create slot with the same ~10
# wallets): a coin's create slot = its first slot on the tape when the curve was still untouched (virtual tokens before
# that trade 1.0725e15+, pump's start is 1.073e15); a first buy in that slot is a create-slot buy, which a copy can't reach
launch = {}; cslot = set()
n_rows = 0; wid = 0; t_first = None; t_last = 0
for r in rows():
    n_rows += 1; m = r["mint"]; t = r["ts"]; t_first = t_first or t; t_last = max(t_last, t)
    if m not in launch:
        pre = (r["vtok"] or 0) + ((r["tok"] or 0) if r["is_buy"] else -(r["tok"] or 0))
        launch[m] = r["slot"] if pre >= 1.0725e15 else None
    settle(t - WIN)
    if m in buf: buf[m].append(tup(r))
    o = own.get((r["user"], m))
    if o is not None:
        v = (r["quote_amount"] or 0) * o[4] / 1e9
        if r["is_buy"]: o[0] += v; o[2] += r["tok"] or 0
        else: o[1] += v; o[3] += r["tok"] or 0
    if r["is_buy"] and r["user"] != "" and (r["user"], m) not in seen:
        seen.add((r["user"], m)); rate = RATE.get(r["quote_mint"])
        sol = (r["quote_amount"] or 0) * rate / 1e9 if rate else 0
        if rate and sol >= MIN_SOL:
            if m not in buf: buf[m] = [tup(r)]
            wid += 1; watches[m].append((r["user"], len(buf[m]) - 1, t, wid, rate, sol)); heapq.heappush(due, (t + WIN, m, wid))
            vt_a = r["vtok"]; impact = ((vt_a + (r["tok"] or 0)) / vt_a) ** 2 - 1 if vt_a else 0   # how far its own buy moved the price
            own[(r["user"], m)] = [sol, 0.0, r["tok"] or 0, 0, rate, impact]
            if launch.get(m) == r["slot"]: cslot.add((r["user"], m))
settle(t_last - WIN)   # the last 31 minutes stay out: not finished
print(f"tape: {len(files)} files, {n_rows:,} trades, {t_first} to {t_last} ({(t_last - t_first) / 3600:.1f} h); "
      f"{len(out):,} copies of first buys of {MIN_SOL}+ SOL ({sum(1 for x in out if x[3] == 'refused'):,} refused over {PMAX}x)")
mid = t_first + (t_last - WIN - t_first) / 2
ok = [x for x in out if x[3] != "refused"]
pool = {e: np.mean([x[3][e] for x in ok]) / STAKE * 100 for e in EX}
print("every copy pooled (a random wallet), % a copy: " + "  ".join(f"{e} {v:+.1f}%" for e, v in pool.items()))
by = collections.defaultdict(list)
for x in out: by[x[0]].append(x)
# One wallet from the tape alone (Nov 21, 4vw54BmA: its address carries ~11,000 failed transactions a minute, so its
# history cannot be read from the chain cheaply; the tape keeps successful trades only): WALLET=... prints, day by day
# (UTC), its own result on its first-bought coins of MIN_SOL+ (sold out, and still held at cost) and our copy under the
# five exits, then stops. No Triton.
# The hot hand (Nov 22, the owner: "if a wallet is having a good streak it will keep going, super short term"):
# STREAK=1 asks, at each copy, how this wallet's copies did over the last LOOK hours, counting only copies already
# closed (bought 600 s+ before: the longest exit), and whether a hot wallet's next copy beats the rest. Walk-forward:
# nothing from after the buy is used. Each rule is reported on the two halves of the tape apart. No Triton.
if os.environ.get("STREAK"):
    import bisect
    def streak(e, look_h, k, thr, fast):
        res = {"hot": [[], []], "rest": [[], []]}
        for u, xs in by.items():
            xs = sorted(xs, key=lambda x: x[1]); ts = [x[1] for x in xs]
            for i, x in enumerate(xs):
                j = bisect.bisect_right(ts, x[1] - 600); lo = bisect.bisect_left(ts, x[1] - look_h * 3600)
                past = [y for y in xs[lo:j] if y[3] != "refused"]
                if x[3] == "refused": continue
                v = x[3][e] / STAKE * 100; half = 0 if x[1] < mid else 1
                hot = len(past) >= k and np.mean([y[3][e] for y in past[-k:]]) / STAKE * 100 > thr
                if hot and fast:   # its own holding so far: a wallet out in under MIN_HOLD s is a speed trader, not hot
                    hh = [y[3]["_its_hold"] for y in past if y[3]["_its_hold"] < 9e8]
                    hot = bool(hh) and np.median(hh) >= MIN_HOLD
                res["hot" if hot else "rest"][half].append(v)
        return res
    print("\nthe hot hand: a wallet's next copy after its last k closed copies (within LOOK h) averaged over thr% (% a copy)")
    print(f"{'exit':6s} {'look':>4s} {'k':>3s} {'thr':>4s} {'speed out':>9s}   {'hot: n, half 1 / half 2':>28s}   {'the rest: half 1 / half 2':>26s}")
    for e in EX:
        for look_h in (2, 6):
            for k in (3, 5):
                for thr in (0, 20):
                    for fast in (False, True):
                        r_ = streak(e, look_h, k, thr, fast); h, o = r_["hot"], r_["rest"]
                        mm = lambda a: f"{np.mean(a):+6.1f}" if a else "   nan"
                        print(f"{e:6s} {look_h:4d} {k:3d} {thr:4d} {str(fast):>9s}   n {len(h[0]):5d}/{len(h[1]):5d} {mm(h[0])} / {mm(h[1])}   "
                              f"n {len(o[0]):6d}/{len(o[1]):6d} {mm(o[0])} / {mm(o[1])}")
    sys.exit()
WALLET = os.environ.get("WALLET")
if WALLET:
    import datetime as dt_
    xs = by.get(WALLET, []); day = lambda t: dt_.datetime.fromtimestamp(t, dt_.timezone.utc).strftime("%m-%d")
    coin_day = {x[4]: day(x[1]) for x in xs}
    print(f"\n{WALLET}: {len(xs)} copies on the tape ({sum(1 for x in xs if x[3] == 'refused')} refused over {PMAX}x)")
    print(f"{'day':6s} {'copies':>6s} {'own sold-out':>13s} {'own held':>9s}   our copy, % a copy: " + " ".join(f"{e:>6s}" for e in EX))
    for d in sorted(set(coin_day.values())):
        dx = [x for x in xs if day(x[1]) == d]; ok_ = [x for x in dx if x[3] != "refused"]
        oc = [own[(WALLET, m)] for m, dd in coin_day.items() if dd == d and (WALLET, m) in own]
        sold = sum(o[1] - o[0] for o in oc if o[3] >= 0.99 * o[2]); held = sum(o[1] - o[0] for o in oc if o[3] < 0.99 * o[2])
        mv = {e: np.mean([x[3][e] for x in ok_]) / STAKE * 100 if ok_ else float("nan") for e in EX}
        print(f"{d:6s} {len(dx):6d} {sold:+13.2f} {held:+9.2f}   " + " ".join(f"{mv[e]:+6.1f}" for e in EX))
    okall = [x for x in xs if x[3] != "refused"]
    if okall: print("all    " + f"{len(xs):6d}" + " " * 25 + " ".join(f"{np.mean([x[3][e] for x in okall]) / STAKE * 100:+6.1f}" for e in EX))
    sys.exit()
# each wallet tuned on half 1 (the owner: "each wallet can be tweaked"): its buy floor 0.5 / 1 / 1.5 / 2 SOL x the coins
# all / SOL-quoted / token-quoted x the five exits = 60 choices, a choice needing 5+ copies in each half; scored on half 2
FLOORS = [float(x) for x in os.environ.get("FLOORS", str(MIN_SOL)).split(",")]; KINDS = {"all": lambda x: True, "SOL": lambda x: x[5], "token": lambda x: not x[5]}
def vv(xs_, e): return np.mean([x[3][e] if x[3] != "refused" else -0.0004 for x in xs_]) / STAKE * 100
def tune(h1, h2):
    best = None
    for fl in FLOORS:
        for kn, f in KINDS.items():
            a = [x for x in h1 if x[2] >= fl and f(x)]; b = [x for x in h2 if x[2] >= fl and f(x)]
            if len(a) < 5 or len(b) < 5: continue
            for e in EX:
                v1 = vv(a, e)
                if best is None or v1 > best[0]: best = (v1, fl, kn, e, len(a), len(b), vv(b, e))
    return best
res = []; fast = 0; flat = 0; loser = 0; bundle = 0; own_of = {}; elig = []; jumpy = 0
BUNDLE = float(os.environ.get("BUNDLE", 0.5))   # a wallet with this share or more of its copies bought in the create slot: a launch bundle, left out
OWN_MIN = float(os.environ.get("OWN_MIN", 0))   # a wallet that loses money itself on its sold-out tape coins is left out
def hold_of(xs):
    h = [x[3]["_its_hold"] for x in xs if x[3] != "refused"]
    return float(np.median(h)) if h else 9e9
for u, xs in by.items():
    if len(xs) < MINN: continue
    if hold_of(xs) < MIN_HOLD: fast += 1; continue
    if np.mean([(u, x[4]) in cslot for x in xs]) >= BUNDLE: bundle += 1; continue
    oc = [own[(u, x[4])] for x in xs if (u, x[4]) in own]; done_ = [o for o in oc if o[3] >= 0.99 * o[2]]
    own_sol = sum(o[1] - o[0] for o in done_); own_of[u] = (own_sol, len(done_), float(np.median([o[5] for o in oc])) if oc else 0)
    # Nov 22, the owner: rank also by what the wallets MADE, with only the can't-copy filters (speed, bundles, flat, and
    # coins that jump past the price limit before our copy lands on most of its buys): the TOPOWN list
    if np.mean([x[3] == "refused" for x in xs]) > 0.5: jumpy += 1; continue
    if np.std([x[3]["w4"] for x in xs if x[3] != "refused"] or [0]) >= 0.02 * STAKE:
        # Nov 22 (after the overfitting lesson): no tuning; the mean of our copy over the 5 fixed exits, all its copies
        mv = float(np.mean([np.mean([x[3][e] for e in EX]) if x[3] != "refused" else -0.0004 for x in xs])) / STAKE * 100
        elig.append((own_sol, u, mv, len(xs)))
    if done_ and own_sol < OWN_MIN: loser += 1; continue
    if np.std([x[3]["w4"] for x in xs if x[3] != "refused"] or [0]) < 0.02 * STAKE: flat += 1; continue   # coins that never move
    h1 = [x for x in xs if x[1] < mid]; h2 = [x for x in xs if x[1] >= mid]
    t = tune(h1, h2)
    if t is None: continue
    v1, fl, kn, e, n1, n2, v2 = t
    shrunk = (n2 * v2 + 30 * pool[e]) / (n2 + 30)      # a small sample is pulled toward what a random wallet makes
    res.append((shrunk, u, n1, n2, f"{fl}+ {kn} {e}", v1, np.median([x[2] for x in xs]), {e_: vv(xs, e_) for e_ in EX}, v2))
res.sort(reverse=True)
print(f"\n{fast} wallets with {MINN}+ copies left out as speed traders (median holding under {MIN_HOLD:.0f} s), {flat} as flat (their coins never move: bundles)")
print(f"{bundle} left out as launch bundles ({BUNDLE:.0%}+ of their copies bought in the coin's create slot)")
print(f"{loser} left out as losing money themselves on their sold-out coins of the tape (own result under {OWN_MIN} SOL)")
print(f"token coins priced: {len(RATE) - 1} quote tokens")
print(f"{len(res)} wallets with {MINN}+ copies, each tuned on half 1 (buy floor x coin kind x exit, 5+ copies a half), scored on half 2:")
print("ranked by the second half shrunk toward the pooled mean (30 copies of weight): a wallet must beat a random one on many copies")
print(f"{'wallet':44s} {'n1':>4s} {'n2':>4s} {'choice':>18s} {'half 1':>7s} {'half 2':>7s} {'score':>7s} {'its SOL':>7s} {'holds':>6s} {'own SOL':>8s} {'impact':>7s}   all its 0.5+ copies by exit")
for sc, u, n1, n2, pick, h1v, med, allv, h2v in res[:30]:
    hh = hold_of(by[u]); hs = f"{hh:5.0f}s" if hh < 1e8 else "  none"; os_, nd, im = own_of.get(u, (0, 0, 0))
    print(f"{u:44s} {n1:4d} {n2:4d} {pick:>18s} {h1v:+6.1f}% {h2v:+6.1f}% {sc:+6.1f}% {med:7.2f} {hs:>6s} {os_:+8.2f} {100 * im:+6.1f}%   " + " ".join(f"{e} {allv[e]:+.0f}%" for e in EX))
print("own SOL = its own result on its sold-out coins of the tape; impact = how far its own buy moved the price (median)")
TOPN = int(os.environ.get("TOPN", 30))   # the candidate list for the history tests (Nov 22: the top 60), one line to paste
print(f"TOP{TOPN}: " + ",".join(r_[1] for r_ in res[:TOPN]))
elig.sort(reverse=True)
print(f"{jumpy} left out as jumpy (over half their copies refused over {PMAX}x); by their own result: " +
      ", ".join(f"{u[:8]} {o:+.1f}" for o, u, _, _ in elig[:10]))
print(f"TOPOWN{TOPN}: " + ",".join(u for o, u, _, _ in elig[:TOPN] if o > 0))
# TOPMEAN: the can't-copy filters only (speed, bundles, flat, jumpy), ranked by the mean of our copy over the 5 fixed exits,
# shrunk toward every copy's mean (30 copies of weight): an edge under any exit, as wallet 4's is; no picking
pm = float(np.mean([np.mean([x[3][e] for e in EX]) if x[3] != "refused" else -0.0004 for x in out])) / STAKE * 100
rk = sorted(((n * mv + 30 * pm) / (n + 30), u, mv, n, o) for o, u, mv, n in elig)[::-1]
print(f"\nby the mean over the 5 fixed exits (no tuning; every copy's mean {pm:+.1f}%), the can't-copy filters only ({len(elig)} wallets):")
for sc, u, mv, n, o in rk[:15]: print(f"  {u:44s} {n:4d} copies  mean {mv:+6.1f}%  shrunk {sc:+6.1f}%  own {o:+7.2f} SOL")
print(f"TOPMEAN{TOPN}: " + ",".join(u for sc, u, mv, n, o in rk[:TOPN]))
json.dump([dict(wallet=r_[1], choice=r_[4], n1=r_[2], n2=r_[3], half1=r_[5], half2=r_[8], score=r_[0]) for r_ in res[:TOPN]],
          open(os.environ.get("TOP_JSON", "/tmp/screen_top.json"), "w"))
up = sum(1 for r_ in res if r_[8] > 0 and r_[5] > 0)
print(f"\nwallets up on both halves: {up} of {len(res)}")
w4 = [r_ for r_ in res if r_[1] == W4]
if w4: print("wallet 4:", w4[0][2:6], {e: round(v, 1) for e, v in w4[0][7].items()})
else: print(f"wallet 4: {len(by.get(W4, []))} copies (under {MINN} or one half short)")
# Chance: the same pick on pseudo-wallets (each real wallet's copy counts per half, drawn at random from the copies of
# that half of the wallets that passed the filters, not from every copy: speed traders and losers would set chance too
# low; NULL_DRAWS draws, 20 by default). As many pseudo-wallets "up on both halves" as real ones = nothing found.
rng = np.random.default_rng(7)
kept = [x for r_ in res for x in by[r_[1]]]
H1 = [x for x in kept if x[1] < mid]; H2 = [x for x in kept if x[1] >= mid]
ND = int(os.environ.get("NULL_DRAWS", 20))
null_up = []; null_top = []
for _ in range(ND):
    up_ = 0; h2s = []
    for u in [r_[1] for r_ in res]:
        xs = by[u]; n1 = sum(1 for x in xs if x[1] < mid); n2 = len(xs) - n1
        a = [H1[i] for i in rng.integers(0, len(H1), n1)]; b = [H2[i] for i in rng.integers(0, len(H2), n2)]
        # pseudo copies keep the real wallet's own sizes and coin kinds, so the tuning has the same room
        a = [(x[0], x[1], y[2], x[3], x[4], y[5]) for x, y in zip(a, [x for x in xs if x[1] < mid])]
        b = [(x[0], x[1], y[2], x[3], x[4], y[5]) for x, y in zip(b, [x for x in xs if x[1] >= mid])]
        t = tune(a, b)
        if t is None: continue
        h2s.append(t[6]); up_ += t[0] > 0 and t[6] > 0
    null_up.append(up_); null_top.append(sorted(h2s)[-30] if len(h2s) >= 30 else float("nan"))
print(f"chance (pseudo-wallets of random copies of the kept wallets, {ND} draws): up on both halves {np.mean(null_up):.0f} "
      f"(range {min(null_up)}-{max(null_up)}, real {up}; {sum(1 for v in null_up if v >= up)} of {ND} draws reach the real count); "
      f"the 30th best half 2 {np.mean(null_top):+.1f}% (real: {sorted(r_[8] for r_ in res)[-30] if len(res) > 29 else float('nan'):+.1f}%)")
# Linked wallets: among the top 60 of the list, pairs that bought the same coins (30%+ of the smaller one's coins): one
# trader with several wallets is one candidate, and its wallets together give more copies
coins_of = collections.defaultdict(set)
for x in out: coins_of[x[0]].add(x[4])
top = [r_[1] for r_ in res[:60]]; pairs = []
for i, a in enumerate(top):
    for b in top[i + 1:]:
        sh = len(coins_of[a] & coins_of[b])
        if sh and sh >= 0.3 * min(len(coins_of[a]), len(coins_of[b])): pairs.append((sh, a, b))
print(f"linked pairs among the top 60 (same coins, 30%+): {len(pairs)}")
for sh, a, b in sorted(pairs, reverse=True)[:15]:
    print(f"  {a[:8]} + {b[:8]}: {sh} coins in common ({len(coins_of[a])} / {len(coins_of[b])})")
