# Market scan, step 5: every wallet's buys on the live other-token coins of the 48 hours (paths from m2_trades.py),
# valued in SOL at Jupiter's price of the quote token (fetched once, SP/market/prices.json), and the rule fixed before
# looking (the lessons of Oct 29 and TAB16RxX):
#   a buy of 0.9+ SOL, its first on the coin (the discovery pass keeps each coin's first 300 transactions: our copy is
#   modelled only where 600 s of path follow the buy, and marked tentative; the full test is on its own history);
#   kept: 10+ such buys on 8+ coins from 4+ creators (not one creator's insider or bundle); under half of them in the
#   create slot or the next (racing the launch is speed, not picking); median first sale 45+ s after its buy and under
#   40% sold within 30 s (a flipper is out before we land).
# Then our copy of each kept wallet's buys (hunt_lib: landing 4 / 8 trades or the next slot after its buy, refused past
# 1.25x, tp 4.0, its sale followed 30-290 s under 1.5x, sell_pressure [5, 60, 30], stall 180 s, 600 s, 0.5 SOL; and the
# same with its sale never followed), every copy; halves by time; without the best 5. Wallet 4 is shown for reference.
#   python3 -I m3_screen.py SP > ../out/market_screen.txt
#   LAUNCH=1 python3 -I m3_screen.py SP > ../out/market_screen_launch.txt   (launch buyers kept instead)
#   LAUNCH=1 MINSOL=0.5 MINBUYS=6 MINCOINS=6 MINCRE=3 SUFFIX=_wide python3 -I m3_screen.py SP > ../out/market_screen_launch_wide.txt
import sys, os, json, gzip, collections, urllib.request
import numpy as np
SP = sys.argv[1]; O = f"{SP}/market"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); import hunt_lib as H
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; ME = H.ME; WSOL = "So11111111111111111111111111111111111111112"
L = {m: x for m, x in json.load(open(f"{O}/launches.json")).items() if x and os.path.exists(f"{O}/paths/{m}.json.gz")}
pf = f"{O}/prices.json"
if os.path.exists(pf): PR = json.load(open(pf))
else:
    ids = sorted({x["quote"] for x in L.values()} | {WSOL}); PR = {}
    for i in range(0, len(ids), 50):
        r = json.load(urllib.request.urlopen(f"https://lite-api.jup.ag/price/v3?ids={','.join(ids[i:i + 50])}", timeout=30))
        PR.update({k: v for k, v in r.items() if v and v.get("usdPrice")})
    json.dump(PR, open(pf, "w"))
sol_usd = PR[WSOL]["usdPrice"]
rate_of = lambda q: PR[q]["usdPrice"] / sol_usd * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None   # lamports per raw unit
# MINSOL / MINBUYS / MINCOINS / MINCRE (Nov 17, "maybe there are wallets even better than wallet 4"): a wider net, same hold rule
MINSOL = float(os.environ.get("MINSOL", 0.9)); MINBUYS = int(os.environ.get("MINBUYS", 10)); MINCOINS = int(os.environ.get("MINCOINS", 8)); MINCRE = int(os.environ.get("MINCRE", 4))
B = collections.defaultdict(list); unpriced = 0; t_all = []
for m, x in L.items():
    rate = rate_of(x["quote"])
    if rate is None: unpriced += 1; continue
    tr = json.load(gzip.open(f"{O}/paths/{m}.json.gz"))
    if not tr: continue
    t_end = tr[-1]["t"]; seen = set(); t_all.append(x["t"])
    for i, e in enumerate(tr):
        u = e["user"]
        if not e["buy"] or u in seen or u == ME: seen.add(u); continue
        seen.add(u)
        sol = e["q"] * (1 + e["bps"] / 1e4) * rate / 1e9
        if sol < MINSOL: continue
        nxt = next((y for y in tr[i + 1:] if y["user"] == u and not y["buy"]), None)
        B[u].append(dict(m=m, t=e["t"], sol=sol, creator=x["creator"], launch=e["slot"] - x["slot"] <= 1, held=(nxt["t"] - e["t"]) if nxt else None, i=i, rate=rate,
                         full=t_end - e["t"] >= 600))
print(f"{len(L)} live coins with a path ({unpriced} with an unpriced quote left out); {len(B)} wallets with a {MINSOL}+ SOL first buy")
t_mid = np.median(t_all)
# LAUNCH=1 (Nov 17, the owner: "plenty of wallet 4's we are not finding"): keep the launch buyers instead, wallet 4's own class
LAUNCH = os.environ.get("LAUNCH") == "1"
def keep(v):
    held = [y["held"] if y["held"] is not None else 1e9 for y in v]
    return (len(v) >= MINBUYS and len({y["m"] for y in v}) >= MINCOINS and len({y["creator"] for y in v}) >= MINCRE and (sum(y["launch"] for y in v) / len(v) >= 0.5) == LAUNCH
            and np.median(held) >= 45 and sum(1 for h in held if h < 30) / len(v) < 0.4)
K = {u: v for u, v in B.items() if keep(v) or u == W4}
print(f"kept by the rule: {len(K) - (W4 in K)} wallets (+ wallet 4 for reference)")
cache = {}
def path(m):
    if m not in cache: cache[m] = json.load(gzip.open(f"{O}/paths/{m}.json.gz"))
    return cache[m]
rows = []
for u, v in K.items():
    for y in v:
        if not y["full"]: y["net"] = y["net2"] = 0.0; y["why"] = "short"; continue
        tr = path(y["m"]); r1, r2 = [], []
        for n in (4, 8, "slot+1"):
            p = H.prep(tr, y["i"], y["rate"], n); r1.append(H.model(p)); r2.append(H.model(p, early=None))
        y["net"] = sum(q[0] for q in r1) / 3; y["net2"] = sum(q[0] for q in r2) / 3; y["why"] = r1[0][1]
    nets = sorted((y["net"] for y in v if y["full"]), reverse=True); c = [y for y in v if y["why"] not in ("refused", "short")]
    held = [y["held"] for y in v if y["held"] is not None]
    rows.append((sum(nets), u, len(v), len({y["m"] for y in v}), len({y["creator"] for y in v}), sum(y["launch"] for y in v) / len(v), np.median(held) if held else 0,
                 sum(1 for h in held if h < 30) / len(v), sum(nets[5:]), sum(y["net"] for y in v if y["t"] < t_mid), sum(y["net"] for y in v if y["t"] >= t_mid),
                 sum(y["net2"] for y in v), sum(sorted((y["net2"] for y in v), reverse=True)[5:]), len(c), sum(1 for y in c if y["net"] > 0), np.median([y["sol"] for y in v])))
print("wallet   | buys coins creators | at launch | held med, under 30 s | OUR COPY (tentative; copies modelled) net SOL, a copy, won | w/o best 5 | day 1 / day 2 | its sale never followed: net, w/o best 5 | size med")
for (net, u, n, nc, ncr, la, hm, f30, wo5, h1, h2, n2, n2wo, nc_, won, sz) in sorted(rows, reverse=True):
    print(f"{u[:8]} | {n:4d} {nc:4d} {ncr:4d} | {100 * la:3.0f}% | {hm:5.0f} s {100 * f30:3.0f}% | ({nc_:3d}) {net:+6.2f} {100 * net / max(1, nc_) / 0.5:+6.1f}% {100 * won / max(1, nc_):3.0f}% |"
          f" {wo5:+6.2f} | {h1:+5.2f} / {h2:+5.2f} | {n2:+6.2f}, {n2wo:+6.2f} | {sz:4.2f}{'  <- wallet 4' if u == W4 else ''}")
json.dump({u: v for u, v in K.items()}, gzip.open(f"{O}/screen_kept{'_launch' if LAUNCH else ''}{os.environ.get('SUFFIX', '')}.json.gz", "wt"))
