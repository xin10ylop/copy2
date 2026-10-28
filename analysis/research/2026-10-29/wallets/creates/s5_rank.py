# Step 5: rank the wallets that buy frenzy coins (other quote) in the create slot or the next.
#   python3 -I s5_rank.py [BIG_SOL=1.0] [TOP=20]  ->  OUT/s5_rank.json (every payer), stdout tables
# Size in SOL: quote_amount x (30 SOL / the coin's own initial virtual quote reserves): pump sets each quote's initial
# reserves to 30 SOL worth, updated with its price (SOL coins all start at 30 SOL virtual), so this is the SOL size of the same buy on a SOL
# curve. It is checked against SOL-funded multi_hop_swap buys (the payer's SOL change) per quote and corrected
# by that median where 5+ such buys exist (table "price check").
import sys, os, time, collections, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crc
BIG = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0; TOP = int(sys.argv[2]) if len(sys.argv) > 2 else 20
C2 = crc.json.load(open(crc.OUT + "/s2_creates.json"))
K = crc.json.load(open(crc.OUT + "/s3_coins.json")); TR = crc.json.load(open(crc.OUT + "/s4_trades.json"))
NAMES = {"pumpCmXq": "PUMP", "3NZ9JMVB": "WBTC", "WXMRyRZh": "WXMR", "EPjFWdd5": "USDC", "CARDSccU": "CARDS", "TTWofwAg": "TTWO",
         "A7bdiYdS": "A7bd", "SPCXxcqX": "SPCX", "7vfCXTUX": "WETH", "DJTu7vi8": "DJTu", "Pren1FvF": "Pren", "SNAPcESr": "SNAP"}
def qn(q): return NAMES.get(q[:8], q[:8])
creators = collections.Counter(r["user"] for r in C2.values() if r.get("ncreate"))
# ---- price per quote unit (lamports), config and checked
cfg = {}
for m, r in K.items():
    if "err" in r or not r.get("vquote"): continue
    cfg.setdefault(r["quote"], collections.Counter())[r["vquote"]] += 1
pq = {q: 30e9 / c.most_common(1)[0][0] for q, c in cfg.items()}       # the quote's usual setting (for display)
pc = {m: 30e9 / r["vquote"] for m, r in K.items() if "err" not in r and r.get("vquote")}   # each coin's own setting
chk = collections.defaultdict(list)
# a buy paid in SOL in its own transaction: the user's SOL (fee payer = user, fee removed) plus WSOL spent, its quote
# token not drawn down (bought in the same transaction or routed vault to vault), its only trade in the transaction
for m, L in TR.items():
    q = K[m]["quote"]
    for x in L:
        sg, sl, d, idx, fp, u, buy, tok, qa, vq, vt, ix, dsol, fee, ntop, wd, qd, nu = x
        if not buy or not qa or nu != 1 or (qd or 0) < -0.01 * qa: continue
        spent = -(wd or 0) + (-(dsol + (fee or 0)) if fp == u and dsol is not None else 0)
        eq = qa * pc[m]
        if spent > 0.05e9 and eq > 0.05e9: chk[q].append(spent / eq)
dep = {r["quote"]: r.get("depth") or 0 for r in K.values() if "err" not in r}
cls = {c: st.median([v for q, l in chk.items() if (dep.get(q, 0) > 0) == c for v in l] or [1.0]) for c in (False, True)}
corr = {q: st.median(v) for q, v in chk.items() if len(v) >= 3}
def factor(q): return corr.get(q, cls[dep.get(q, 0) > 0])
def lam(m, qa): return qa * pc[m] * factor(K[m]["quote"]) if qa else 0
print(f"price check (buys paid in SOL or WSOL in their own tx: SOL spent / config-priced size; > 1 includes fees, tips, rent):"
      f" {sum(len(v) for v in chk.values())} buys, {len(chk)} quotes, {len(corr)} with 3+; class medians plain token {cls[False]:.3f}, pump coin {cls[True]:.3f}")
for q, v in sorted(chk.items(), key=lambda kv: -len(kv[1]))[:15]:
    print(f"  {qn(q):8s} n={len(v):4d} median {st.median(v):.3f}  p25 {sorted(v)[len(v)//4]:.3f}  p75 {sorted(v)[3*len(v)//4]:.3f}"
          f"   config {pq[q]/1e9:.3e} SOL a unit")
# ---- per payer
P = collections.defaultdict(lambda: dict(coins={}, n_buys=0))
w4cal = []
for m, L in TR.items():
    r = K[m]; q = r["quote"]; dev = r["user"]
    tr = [x for x in L if x[1] is not None]
    for i, x in enumerate(tr):
        sg, sl, d, idx, fp, u, buy, tok, qa, vq, vt, ix, dsol, fee, ntop = x[:15]
        if not buy or d > 1 or u == dev: continue
        # trades by others in the two slots after this buy (its own slot after it, +1, +2)
        fol = sum(1 for y in tr[i + 1:] if y[1] <= sl + 2 and y[5] != u)
        fol_b = sum(1 for y in tr[i + 1:] if y[1] <= sl + 2 and y[5] != u and y[6])
        nb_before = len({y[5] for y in tr[:i] if y[6] and y[5] not in (dev, u)})   # distinct earlier buyers, dev excluded
        cidx = C2[r["csig"]].get("idx")
        bund = sg == r["csig"] or (d == 0 and cidx is not None and idx is not None and 0 < idx - cidx <= 5)
        c = P[u]["coins"].setdefault(m, dict(sol=0.0, d=d, slot=sl, idx=idx, sig=sg, fol=fol, fol_b=fol_b, rank=nb_before + 1,
                                             q=qn(q), ix=ix, bt=r["bt"], fp=fp, dev=dev, bund=bund, intx=sg == r["csig"]))
        c["sol"] += lam(m, qa) / 1e9; P[u]["n_buys"] += 1
rows = []
for u, p in P.items():
    cs = list(p["coins"].values()); big = [c for c in cs if c["sol"] >= BIG]
    rows.append(dict(user=u, n=len(cs), n_big=len(big), med_sol=st.median(c["sol"] for c in cs),
                     med_big=st.median(c["sol"] for c in big) if big else 0,
                     at0=sum(1 for c in cs if c["d"] == 0) / len(cs), fol=st.median(c["fol"] for c in cs),
                     fol_b=st.median(c["fol_b"] for c in cs), first=sum(1 for c in cs if c["rank"] == 1) / len(cs),
                     quotes=collections.Counter(c["q"] for c in cs).most_common(3),
                     routes=collections.Counter(c["ix"] for c in cs).most_common(2),
                     last=max(c["bt"] for c in cs), hours=len({c["bt"] // 3600 for c in cs}), creates=creators.get(u, 0),
                     feepayer_other=sum(1 for c in cs if c["fp"] != u),
                     devs=len({c["dev"] for c in cs}), bund=sum(1 for c in cs if c["bund"]) / len(cs),
                     intx=sum(1 for c in cs if c["intx"]) / len(cs),
                     dev_top=collections.Counter(c["dev"] for c in cs).most_common(1)[0][0]))
rows.sort(key=lambda r: (-r["n_big"], -r["n"]))
for r in rows: r["indep"] = r["devs"] >= 5 and r["bund"] < 0.5
# the wallet sharing most of its coins (bought at +0/+1): one operator's wallets buy the same coins in the same slots
cs_of = {u: set(p["coins"]) for u, p in P.items()}
by_coin = collections.defaultdict(set)
for u, cs in cs_of.items():
    for m in cs: by_coin[m].add(u)
for r in rows[:300] + [x for x in rows if x["user"] == crc.W4]:
    co = collections.Counter(v for m in cs_of[r["user"]] for v in by_coin[m] if v != r["user"])
    if co:
        v, k = co.most_common(1)[0]; r["co"] = v; r["co_share"] = k / r["n"]
    else: r["co"] = None; r["co_share"] = 0
crc.jdump(dict(rows=rows, coins={u: P[u]["coins"] for u in [r["user"] for r in rows[:200] + [x for x in rows if x["indep"]]] + [crc.W4] if u in P},
               pq=pq, pc=pc, corr={q: factor(q) for q in pq}, cls=cls, big=BIG), crc.OUT + "/s5_rank.json")
nf = len(TR); print(f"\n{nf} frenzy coins, {len(rows)} wallets bought one at +0/+1 (dev excluded), {sum(1 for r in rows if r['n_big'])} with a {BIG}+ SOL buy")
def line(i, r):
    print(f"{i:>3} {r['user']}  coins {r['n']:4d} big {r['n_big']:4d}  med {r['med_sol']:6.2f} (big {r['med_big']:5.2f})"
          f"  +0 {r['at0']:4.0%}  1st {r['first']:4.0%}  fol {r['fol']:4.1f}/{r['fol_b']:4.1f}  hrs {r['hours']:2d}"
          f"  last {time.strftime('%H:%M', time.gmtime(r['last']))}  cr {r['creates']}  devs {r['devs']:3d}  bund {r['bund']:4.0%}"
          f"  co {r.get('co_share', 0):4.0%} {str(r.get('co'))[:8]}  {r['quotes']} {r['routes']}")
print(f"\nINDEPENDENT buyers (coins of 5+ creators, under half bundled right after the create): "
      f"{sum(1 for r in rows if r['indep'])} wallets, {sum(1 for r in rows if r['indep'] and r['n_big'])} with a {BIG}+ SOL buy; by coins with a {BIG}+ SOL buy")
ind = [r for r in rows if r["indep"]]
for i, r in enumerate(ind[:TOP + 10]): line(i + 1, r)
for i, r in enumerate(ind):
    if r["user"] == crc.W4: print("wallet 4:"); line(i + 1, r)
print("\nby coins bought (any size), top 10 independent:")
for i, r in enumerate(sorted(ind, key=lambda r: -r["n"])[:10]): line(i + 1, r)
print(f"\nLAUNCH BUNDLES (coins of 1-2 creators, half or more bought right after the create, {BIG}+ SOL on 10+ coins), by creator:")
G = collections.defaultdict(list)
for r in rows:
    if r["devs"] <= 2 and r["bund"] >= 0.5 and r["n_big"] >= 10: G[r["dev_top"]].append(r)
for dv, rs in sorted(G.items(), key=lambda kv: -sum(r["n_big"] for r in kv[1])):
    print(f"  creator {dv}  coins {max(r['n'] for r in rs):3d}  wallets {len(rs)}: " +
          ", ".join(f"{r['user']} ({r['n_big']}, {r['med_sol']:.2f})" for r in rs))
