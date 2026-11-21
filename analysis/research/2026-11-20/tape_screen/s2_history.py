# The second check (Nov 21; the owner: "a wallet looks good but in fact doesn't work, how can we avoid that?"): each
# screen candidate against ITS OWN past, which the tape never showed. (1) Its own result day by day over DAYS days (its
# pump curve trades from the chain, candidates/c1_fetch.py; quote tokens at Jupiter's price now): a wallet that does not
# make money itself on most days is dropped. (2) Our copy on NCOPY of its past first buys of 0.5+ SOL at random (each
# coin's 31 minutes, tab_exits/cmodel.path; 1 SOL in the slot after its buy, refused over 1.5x, COST a round trip) under
# the screen's five fixed exits, the older and the newer half apart. Cheap: its own transactions plus NCOPY coins.
#   RPC_URL=... LK=SP/lk python3 -I s2_history.py SP WALLET[,WALLET...] [DAYS=14] [NCOPY=50] > out_s2.txt
import sys, os, json, subprocess, random, collections, urllib.request, datetime as dt, numpy as np, concurrent.futures as cf
SP, WS = sys.argv[1], sys.argv[2].split(","); DAYS = float(sys.argv[3]) if len(sys.argv) > 3 else 14; NC = int(sys.argv[4]) if len(sys.argv) > 4 else 50
COST = float(os.environ.get("COST", 0.0345)); STAKE = 1.0; SOLM = "So11111111111111111111111111111111111111112"
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-13/tab_exits"); import cmodel as M
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/wallet_hunt"); import hunt_lib as H
C1 = "/home/user/copy2/analysis/research/2026-11-19/candidates/c1_fetch.py"
def first(m):
    i = np.flatnonzero(m); return int(i[0]) if len(i) else None
def prices(qs):
    P = {}
    for i in range(0, len(qs), 40):
        try: P.update({k: v for k, v in json.load(urllib.request.urlopen("https://lite-api.jup.ag/price/v3?ids=" + ",".join(qs[i:i + 40] + [SOLM]), timeout=20)).items() if v})
        except Exception: pass
    return P
def exits(tr, k, rate):
    p = H.prep(tr, k, rate, "slot+1", pmax=1.5)
    if p["refused"] or not len(p["px"]): return None
    vt0, vq0, b0 = p["ent"]; Q = STAKE * 1e9 / rate; net_in = Q * 1e4 / (1e4 + b0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq_r = p["vq"] + net_in; vt_r = p["vt"] * p["vq"] / vq_r
    val = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - p["bps"] / 1e4) * rate / 1e9 - STAKE - COST
    px, age, n = p["px"], p["age"], len(p["px"]); prem = (tr[k]["vt"] / vt0) ** 2; BIG = 10 ** 9
    trig = lambda i: BIG if i is None else min(i + 1, n - 1); tm = lambda h: (lambda i: BIG if i is None else i)(first(age >= h))
    s = np.concatenate([[0], np.cumsum(p["osell"])]); b = np.concatenate([[0], np.cumsum(p["obuy"])])
    lo = np.searchsorted(age, age - 60, side="left"); sp = trig(first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= 5) & (age >= 30)))
    pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
    st = trig(first((pk >= prem) & (age - lasthi >= 180))); early = trig(first(p["sell"] & (age >= 30) & (age < 290) & (px < 1.5))); its = trig(first(p["sell"]))
    E = {"w4": min(trig(first(px >= 4)), tm(600), sp, st, early, n - 1), "its": min(its, tm(600), n - 1), "tp2": min(trig(first(px >= 2)), tm(120), n - 1),
         "held": min(tm(300), n - 1), "scalp": min(trig(first(px >= 1.5)), tm(60), n - 1)}
    return {e: 100 * float(val[i]) / STAKE for e, i in E.items()}
for W in WS:
    sub = f"hist_{W[:8]}"; D = f"{SP}/{sub}"
    if not os.path.exists(f"{D}/{W[:8]}_trades.jsonl"):
        subprocess.run([sys.executable, "-I", C1, SP, str(DAYS)], env={**os.environ, "SUB": sub, "WALLETS": W}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    trades = [e for l in open(f"{D}/{W[:8]}_trades.jsonl") for e in (json.loads(l)["trades"] or [])]
    sigs = sorted((t, s) for s, t in json.load(open(f"{D}/{W[:8]}_sigs.json")))
    by = collections.defaultdict(list)
    for e in trades: by[e["m"]].append(e)
    P = prices(sorted({e["quote"] for e in trades if e["quote"] and not e["quote"].startswith("1111")})); su = P.get(SOLM, {}).get("usdPrice")
    rate_of = lambda q: 1.0 if not q or q.startswith("1111") else (P[q]["usdPrice"] / su * 1e9 / 10 ** P[q]["decimals"] if su and q in P and P[q].get("decimals") is not None else None)
    day = collections.defaultdict(float); firsts = []
    for m, es in by.items():
        es.sort(key=lambda e: (e["slot"], not e["buy"]))
        if not es[0]["buy"]: continue
        r = rate_of(es[0]["quote"])
        if r is None: continue
        net = sum((-1 if e["buy"] else 1) * e["q"] * r / 1e9 for e in es)
        day[dt.datetime.fromtimestamp(es[0]["t"], dt.UTC).strftime("%m-%d")] += net
        if es[0]["q"] * r / 1e9 >= 0.5 and es[0]["t"] < sigs[-1][0] - 1900:
            firsts.append(dict(m=m, slot=es[0]["slot"], t=es[0]["t"], rate=r, anchor=next((s for t, s in sigs if t >= es[0]["t"] + 1890), sigs[-1][1])))
    ds = sorted(day.items()); up = sum(1 for _, v in ds if v > 0)
    print(f"\n{W}: {len(trades)} trades, {len(by)} coins over {len(ds)} days; its own result {sum(day.values()):+.2f} SOL, up on {up} of {len(ds)} days")
    print("  its own SOL by day: " + "  ".join(f"{d} {v:+.2f}" for d, v in ds))
    random.seed(7); pick = sorted(random.sample(firsts, min(NC, len(firsts))), key=lambda c: c["t"])
    with cf.ThreadPoolExecutor(8) as ex: paths = list(ex.map(lambda c: M.path(c["m"], c["slot"], c["anchor"], threads=10), pick))
    res = []
    for c, tr in zip(pick, paths):
        k = next((i for i, e in enumerate(tr) if e["user"] == W and e["buy"] and e["slot"] == c["slot"]), None)
        if k is None: continue
        r = exits(tr, k, c["rate"])
        if r: res.append((c["t"], r))
    if not res: print("  our copy: no copies"); continue
    h = len(res) // 2
    print(f"  our copy on {len(res)} of its past buys of 0.5+ SOL ({dt.datetime.fromtimestamp(res[0][0], dt.UTC):%m-%d} to {dt.datetime.fromtimestamp(res[-1][0], dt.UTC):%m-%d}), % a copy, older | newer half:")
    print("    " + "  ".join(f"{e} {np.mean([r[e] for _, r in res[:h]]):+.1f}|{np.mean([r[e] for _, r in res[h:]]):+.1f}" for e in ("w4", "its", "tp2", "held", "scalp")))
