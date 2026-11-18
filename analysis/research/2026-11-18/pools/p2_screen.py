# The pool hunt, step 2: from p1's pool trades (SP/pools/*.json.gz, the coins fetched so far), every wallet's first buy
# of a coin (0.3+ SOL) and our copy of it: buy D s after its buy at the pool's reserves after the last trade by then,
# 0.5 SOL; sell D s after it has sold half of what it bought (else at the end of the window, at the last reserves).
# Constant product on the pool's reserves, 0.3% a side, 0.01 SOL a round trip (a copy that does not race; also shown
# at 0.0345). Wallets with 50+ trades on one coin (volume bots) are left out. Picked on coins that graduated before
# Nov 15 00:00 UTC, judged on the coins after; the fair measures (best 2% out, bootstrap).
#   python3 -I p2_screen.py SP [D] > out/p2_screen.txt
import sys, os, glob, gzip, json, collections, bisect, numpy as np
SP = sys.argv[1]; D = float(sys.argv[2]) if len(sys.argv) > 2 else 3; T15 = 1794700800; FEE = 0.003; Q = 0.5e9
def copy(tr, ts, i_buy, t_sell):
    j = bisect.bisect_right(ts, tr[i_buy]["t"] + D) - 1
    if j < i_buy: j = i_buy
    rb, rq = tr[j]["rb"], tr[j]["rq"]; tok = rb - rb * rq / (rq + Q * (1 - FEE))
    k = bisect.bisect_right(ts, t_sell + D) - 1 if t_sell is not None else len(tr) - 1
    k = max(k, j); rb2, rq2 = tr[k]["rb"], tr[k]["rq"]; sol = rq2 - rq2 * rb2 / (rb2 + tok)
    return sol * (1 - FEE) / 1e9 - 0.5, tr[k]["t"] - tr[j]["t"]
rows = collections.defaultdict(list); ncoin = 0
for f in glob.glob(f"{SP}/pools/*.json.gz"):
    try: d = json.load(gzip.open(f))
    except Exception: continue
    tr = sorted(d["tr"], key=lambda e: (e["slot"], e["t"]))
    if len(tr) < 20: continue
    ncoin += 1; ts = [e["t"] for e in tr]; per = collections.defaultdict(list)
    for i, e in enumerate(tr): per[e["user"]].append(i)
    for u, ix in per.items():
        if len(ix) >= 50 or u == d["pool"]: continue
        b = next((i for i in ix if tr[i]["tok"] > 0 and -tr[i]["sol"] >= 0.3e9), None)
        if b is None: continue
        got = sum(tr[i]["tok"] for i in ix if i >= b and tr[i]["tok"] > 0 and tr[i]["t"] - tr[b]["t"] <= 600) or tr[b]["tok"]
        sold = 0; t_sell = None
        for i in ix:
            if i > b and tr[i]["tok"] < 0:
                sold += -tr[i]["tok"]
                if sold >= 0.5 * got: t_sell = tr[i]["t"]; break
        its = sum(tr[i]["sol"] for i in ix) / 1e9   # its own net SOL on the coin in the window (open tokens not valued)
        v, held = copy(tr, ts, b, t_sell)
        rows[u].append(dict(m=d["m"], t=tr[b]["t"], tmig=d["tmig"], size=-tr[b]["sol"] / 1e9, v=v, held=held, its=its, sold=t_sell is not None))
def S(v):
    v = np.array(v); n = len(v)
    if not n: return "   0"
    s = np.sort(v); k = max(1, round(0.02 * n)); return f"{n:3d} {v.sum():+6.2f} ({100 * v.mean() / 0.5:+6.1f}%) w/o 2% {s[:-k].sum() if n > 1 else 0:+6.2f}"
print(f"{ncoin} pool coins (20+ trades); {len(rows)} wallets with a 0.3+ SOL buy; D = {D:.0f} s; 0.01 SOL a round trip")
C = []
for u, R in rows.items():
    A = [r for r in R if r["tmig"] < T15]; B = [r for r in R if r["tmig"] >= T15]
    if len(A) < 6: continue
    va = np.array([r["v"] - 0.01 for r in A]); k = max(1, round(0.02 * len(va)))
    C.append((va.sum(), u, A, B, np.sort(va)[:-k].sum(), np.median([r["held"] for r in A])))
C.sort(reverse=True)
print(f"wallets with 6+ coins before Nov 15: {len(C)}; by our copy's total before Nov 15 (pick) -> after (judge):")
print("  wallet    | before: n, net (a copy), w/o 2%          | held med | its own net | after: n, net, w/o 2% | after at 0.0345")
for tot, u, A, B, wo, hm in C[:40]:
    print(f"  {u[:8]}  | {S([r['v'] - 0.01 for r in A])} | {hm:6.0f} s | {sum(r['its'] for r in A):+7.2f} | {S([r['v'] - 0.01 for r in B])} | {S([r['v'] - 0.0345 for r in B])}")
P = [c for c in C if c[0] > 0 and c[4] > 0 and c[5] >= 30]
print(f"\nPICKED (before Nov 15: positive, positive without the best 2%, held 30 s+ a median): {len(P)} wallets")
v = [r["v"] - 0.01 for c in P for r in c[3]]
if v:
    bs = np.random.default_rng(7).choice(np.array(v), size=(10000, len(v))).mean(axis=1)
    print(f"   their copies after Nov 15, pooled: {S(v)}; P(mean > 0) {np.mean(bs > 0):.1%}")
    for c in P: print(f"   {c[1]}: after {S([r['v'] - 0.01 for r in c[3]])}")
