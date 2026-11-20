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
D = sys.argv[1]; MIN_SOL = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5; MINN = int(sys.argv[3]) if len(sys.argv) > 3 else 10
STAKE, COST, PMAX, WIN = 0.5, 0.0345, 1.5, 1860
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
try:
    pr = {}
    for i in range(0, len(ids), 40):
        pr.update(json.load(urllib.request.urlopen("https://lite-api.jup.ag/price/v3?ids=" + ",".join(ids[i:i + 40] + [WSOL]), timeout=20)))
    su = pr[WSOL]["usdPrice"]
    for q in ids:
        if (pr.get(q) or {}).get("usdPrice") and (pr.get(q) or {}).get("decimals") is not None: RATE[q] = pr[q]["usdPrice"] / su * 1e9 / 10 ** pr[q]["decimals"]
except Exception as x: print(f"prices: {type(x).__name__}; non-SOL coins left out", file=sys.stderr)
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
    return {k_: float(val[i]) for k_, i in ex.items()}
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
        if r is not None: out.append((user, t0, sol, r))
        if watches[m]:   # trim the coin's buffer to its oldest open watch
            cut = min(x[1] for x in watches[m])
            if cut > 0:
                buf[m] = tr[cut:]
                watches[m] = [(u, kk - cut, t, i, ra, so) for u, kk, t, i, ra, so in watches[m]]
        else: del buf[m]; del watches[m]
n_rows = 0; wid = 0; t_first = None; t_last = 0
for r in rows():
    n_rows += 1; m = r["mint"]; t = r["ts"]; t_first = t_first or t; t_last = max(t_last, t)
    settle(t - WIN)
    if m in buf: buf[m].append(tup(r))
    if r["is_buy"] and r["user"] != "" and (r["user"], m) not in seen:
        seen.add((r["user"], m)); rate = RATE.get(r["quote_mint"])
        sol = (r["quote_amount"] or 0) * rate / 1e9 if rate else 0
        if rate and sol >= MIN_SOL:
            if m not in buf: buf[m] = [tup(r)]
            wid += 1; watches[m].append((r["user"], len(buf[m]) - 1, t, wid, rate, sol)); heapq.heappush(due, (t + WIN, m, wid))
settle(t_last - WIN)   # the last 31 minutes stay out: not finished
print(f"tape: {len(files)} files, {n_rows:,} trades, {t_first} to {t_last} ({(t_last - t_first) / 3600:.1f} h); "
      f"{len(out):,} copies of first buys of {MIN_SOL}+ SOL ({sum(1 for x in out if x[3] == 'refused'):,} refused over {PMAX}x)")
mid = t_first + (t_last - WIN - t_first) / 2
ok = [x for x in out if x[3] != "refused"]
pool = {e: np.mean([x[3][e] for x in ok]) / STAKE * 100 for e in EX}
print("every copy pooled (a random wallet), % a copy: " + "  ".join(f"{e} {v:+.1f}%" for e, v in pool.items()))
by = collections.defaultdict(list)
for x in out: by[x[0]].append(x)
res = []
for u, xs in by.items():
    if len(xs) < MINN: continue
    h1 = [x for x in xs if x[1] < mid]; h2 = [x for x in xs if x[1] >= mid]
    if len(h1) < MINN // 2 or len(h2) < MINN // 2: continue
    v = lambda xs_, e: np.mean([x[3][e] if x[3] != "refused" else -0.0004 for x in xs_]) / STAKE * 100
    pick = max(EX, key=lambda e: v(h1, e))
    res.append((v(h2, pick), u, len(h1), len(h2), pick, v(h1, pick), np.median([x[2] for x in xs]), {e: v(xs, e) for e in EX}))
res.sort(reverse=True)
print(f"\n{len(res)} wallets with {MINN}+ copies ({MINN // 2}+ in each half); the exit picked on half 1, scored on half 2:")
print(f"{'wallet':44s} {'n1':>4s} {'n2':>4s} {'exit':>5s} {'half 1':>7s} {'half 2':>7s} {'its SOL':>7s}   all copies by exit")
for h2v, u, n1, n2, pick, h1v, med, allv in res[:30]:
    print(f"{u:44s} {n1:4d} {n2:4d} {pick:>5s} {h1v:+6.1f}% {h2v:+6.1f}% {med:7.2f}   " + " ".join(f"{e} {allv[e]:+.0f}%" for e in EX))
up = sum(1 for r_ in res if r_[0] > 0 and r_[5] > 0)
print(f"\nwallets up on both halves: {up} of {len(res)}")
w4 = [r_ for r_ in res if r_[1] == W4]
if w4: print("wallet 4:", w4[0][2:6], {e: round(v, 1) for e, v in w4[0][7].items()})
else: print(f"wallet 4: {len(by.get(W4, []))} copies (under {MINN} or one half short)")
