# Winners first, the launch pickers (Nov 18, the owner: "having several wallet 4's can multiply everything"): w3_buyers.py
# left out the create slot and the next (snipers, bundles), which is exactly where wallet 4 buys (98% within 2 s). Here:
# a wallet's first buy on a coin in the create slot or the 2 slots after, 0.25+ SOL, not the creator, not inside the create
# transaction itself (a bundle); on the 1,495 graduated coins and the 3,000 controls of w2_trades.py (each control stands for
# n_rest / 3,000 coins). Its hit rate (graduated / its launch buys, misses estimated from the controls) against the base
# rate of launch buys; how long it holds (its first sale after the buy, within the 400 trades read); a Poisson tail.
# THE CHECK: the method must rank wallet 4 near the top, or it cannot see a wallet like it.
#   python3 -I w13_launch_pickers.py SP > out/w13_launch_pickers.txt
import sys, os, json, gzip, math, collections, statistics as st
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/attention"); import creates
SP = sys.argv[1]; W = f"{SP}/winners"; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
WSOL = "So11111111111111111111111111111111111111112"; SOLQ = {WSOL, "11111111111111111111111111111111", None, "?"}
sm = json.load(open(f"{W}/sample.json")); CR = creates.load(SP); cr = {m: v for m, (s, v) in CR.items()}; csig = {m: s for m, (s, v) in CR.items()}
PR = json.load(open(f"{SP}/market/prices.json")); sol_usd = PR[WSOL]["usdPrice"]
rate_of = lambda q: 1.0 if q in SOLQ else (PR[q]["usdPrice"] / sol_usd * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None)
WCTRL = sm["n_rest"] / len(sm["ctrl"]); B = collections.defaultdict(list); n = collections.Counter(); base = [0.0, 0.0]
for kind in ("grad", "ctrl"):
    for m in sm[kind]:
        f = f"{W}/paths/{m}.json.gz"
        if not os.path.exists(f) or m not in cr: continue
        tr = json.load(gzip.open(f)); n[kind] += 1; rate = rate_of(cr[m].get("quote"))
        if not tr or rate is None: continue
        g = kind == "grad"; w = 1.0 if g else WCTRL; seen = set(); any_launch = False
        for i, e in enumerate(tr):
            u = e["user"]
            if e["buy"] and u not in seen and u != cr[m].get("creator") and e["slot"] - cr[m]["slot"] <= 2 and e.get("sig") != csig[m]:
                sol = e["q"] * (1 + e["bps"] / 1e4) * rate / 1e9
                if sol >= 0.25:
                    nxt = next((y for y in tr[i + 1:] if y["user"] == u and not y["buy"]), None)
                    B[u].append(dict(m=m, g=g, t=e["t"], sol=sol, cr=cr[m].get("creator"), held=(nxt["t"] - e["t"]) if nxt else None)); any_launch = True
            seen.add(u)
        if any_launch: base[0] += w * g; base[1] += w
b0 = base[0] / base[1]
print(f"coins read: {n['grad']} graduated, {n['ctrl']} control (each stands for {WCTRL:.1f}); coins with a launch buy: graduated {b0:.2%} (the base)")
rows = []
for u, v in B.items():
    hits = [x for x in v if x["g"]]; miss = sum(1 for x in v if not x["g"]) * WCTRL
    if len(hits) < 3 or len({x["cr"] for x in hits}) < 3: continue
    N = len(hits) + miss; lam = b0 * N; k = len(hits)
    ptail = max(0.0, 1 - sum(math.exp(-lam + i * math.log(lam) - math.lgamma(i + 1)) for i in range(k))) if lam > 0 else 0.0
    held = [x["held"] for x in v if x["held"] is not None]
    rows.append(dict(u=u, k=k, N=N, rate=k / N, lift=(k / N) / b0, p=ptail, held=st.median(held) if held else None,
                     f30=sum(1 for h in held if h < 30) / len(v), never=sum(1 for x in v if x["held"] is None) / len(v), sol=st.median(x["sol"] for x in v)))
rows.sort(key=lambda r: r["p"])
w4 = next((i for i, r in enumerate(rows) if r["u"] == W4), None)
print(f"wallets with 3+ launch buys on graduated coins from 3+ creators: {len(rows)}; WALLET 4 ranks {None if w4 is None else w4 + 1} (by the chance of its hits)")
print("rank wallet   | hits / est. launch buys | hit rate | lift | P(by chance) | held med, sold <30 s, not sold in the window | SOL med")
for i, r in enumerate(rows[:60]):
    print(f"{i + 1:3d} {r['u'][:8]} | {r['k']:4d} / {r['N']:7.0f} | {r['rate']:6.1%} | {r['lift']:4.1f} | {r['p']:.1e} | "
          f"{'-' if r['held'] is None else f'{r['held']:5.0f} s'} {r['f30']:4.0%} {r['never']:4.0%} | {r['sol']:5.2f}{'  <- WALLET 4' if r['u'] == W4 else ''}")
if w4 is not None and w4 >= 60:
    r = rows[w4]; print(f"... {w4 + 1} {r['u'][:8]} | {r['k']} / {r['N']:.0f} | {r['rate']:.1%} | {r['lift']:.1f} | {r['p']:.1e}  <- WALLET 4")
json.dump(rows, open(f"{W}/w13_rows.json", "w"))
