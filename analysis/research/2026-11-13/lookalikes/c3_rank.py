# Search 2, step 3: who buys coins priced in another token at launch (create + 0..WIN s, the coin's creator and the
# create transaction's own buys excluded), for MIN+ SOL. SOL value of a buy = quote amount x (30 SOL / the coin's
# initial virtual quote reserves) x a factor per quote token: the median of SOL paid / that value over the buys paid in
# SOL in their own transaction (the buyer pays the fee, its quote token not drawn down, one trade by it in the
# transaction), as the Oct 29 scan (../../2026-10-29/wallets/creates/README.md §4); quotes with under 3 such buys take
# the median over all. Wallet 4 is listed as the calibration row.
# A wallet is "bundled" on a coin when it buys in the create slot within 5 transactions of the create. Kept: wallets
# with MIN+ SOL launch buys on NMIN+ coins of 5+ creators.
#   python3 -I c3_rank.py [MIN=1.0] [WIN=2] [NMIN=20]  ->  LK/c3_rank.json
import sys, os, json, statistics, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib
MIN = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0; WIN = float(sys.argv[2]) if len(sys.argv) > 2 else 2; NMIN = int(sys.argv[3]) if len(sys.argv) > 3 else 20
L = json.load(open(lib.OUT + "/c2_launch.json")); W4 = lib.W4
ok = {m: v for m, v in L.items() if "err" not in v and v.get("vquote")}
cidx = {}
# the create's own block index, for the bundle mark
C = json.load(open(lib.OUT + "/c1_creates.json"))
ratio = collections.defaultdict(list)
for m, v in ok.items():
    p0 = 30e9 / v["vquote"]
    cnt = collections.Counter((e["sig"], e["user"]) for e in v["trades"])
    for e in v["trades"]:
        if e["buy"] and e["payer"] and e["solchg"] is not None and e["solchg"] < 0 and (e["qdrawn"] or 0) <= 0 and cnt[(e["sig"], e["user"])] == 1 and e["q"]:
            ratio[v["quote"]].append(-e["solchg"] / (e["q"] * p0))
allr = statistics.median([x for v in ratio.values() for x in v]) if ratio else 1.0
F = {q: (statistics.median(v) if len(v) >= 3 else allr) for q, v in ratio.items()}
print(f"{len(ok)} coins priced in another token with launch trades read; price factor: {sum(1 for v in ratio.values() if len(v) >= 3)} quotes with 3+ SOL-paid buys, "
      f"overall median {allr:.3f} ({sum(len(v) for v in ratio.values())} buys)")
buys = collections.defaultdict(list)
for m, v in ok.items():
    p0 = 30e9 / v["vquote"]; f = F.get(v["quote"], allr); first = set()
    tx0 = min((e["idx"] for e in v["trades"] if e["sig"] == v["csig"] and e["idx"] is not None), default=None)
    for e in v["trades"]:
        if not e["buy"] or e["user"] in (v["creator"], v["user"]) or e["sig"] == v["csig"] or e["user"] in first: continue
        if e["t"] - v["bt"] > WIN: continue
        first.add(e["user"])
        sol = e["q"] * p0 * f / 1e9                     # lamports -> SOL
        bundled = e["ds"] == 0 and tx0 is not None and e["idx"] is not None and e["idx"] - tx0 <= 5
        buys[e["user"]].append(dict(m=m, sol=sol, ds=e["ds"], dt=e["t"] - v["bt"], creator=v["creator"], quote=v["quote"], bundled=bundled, sig=e["sig"]))
rows = []
for w, b in buys.items():
    big = [x for x in b if x["sol"] >= MIN]
    if not big: continue
    cr = collections.Counter(x["creator"] for x in big)
    rows.append(dict(w=w, n=len(big), creators=len(cr), top_creator=cr.most_common(1)[0][1], bundled=sum(x["bundled"] for x in big),
                     sol=statistics.median(x["sol"] for x in big), ds=statistics.median(x["ds"] for x in big),
                     quotes=collections.Counter(x["quote"][:8] for x in big).most_common(3), coins=[x["m"] for x in big]))
rows.sort(key=lambda r: -r["n"])
indep = [r for r in rows if r["creators"] >= 5 and r["bundled"] < r["n"] / 2]
print(f"{len(buys)} wallets bought at create+0..{WIN} s; {len(rows)} for {MIN}+ SOL; {sum(1 for r in rows if r['creators'] < 5)} on under 5 creators "
      f"(launch bundles and their own coins), {len(indep)} independent (5+ creators, under half bundled); kept with {NMIN}+ coins: "
      f"{sum(1 for r in indep if r['n'] >= NMIN)}")
w4 = next((r for r in rows if r["w"] == W4), None)
if w4: print(f"calibration: wallet 4 {w4['n']} coins, median {w4['sol']:.2f} SOL (its known buys: 1.45+ SOL, median 1.60)")
print(f"{'wallet':45s} {'coins':>5s} {'creators':>8s} {'bundled':>7s} {'SOL med':>7s} {'slot med':>8s}  quotes")
for r in indep:
    if r["n"] < max(5, NMIN // 4): continue
    print(f"{r['w']:45s} {r['n']:5d} {r['creators']:8d} {r['bundled']:7d} {r['sol']:7.2f} {r['ds']:8.1f}  {r['quotes']}")
json.dump(dict(factor=F, rows=rows), open(lib.OUT + f"/c3_rank_{MIN}.json", "w"))
