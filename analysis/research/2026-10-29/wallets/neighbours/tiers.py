# The listed wallets' early buys split by buy size and by period (P1 Oct 19-22, P2 Oct 23 -> Oct 27 00:20, P3 after):
# coins, its first-sale win share, median hold, and the gross return estimate of rank.py (no fees).
#   python3 -I tiers.py [PREFIX ...]   ->  out/tiers.txt
import sys, os, json, statistics, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nlib as L
R = json.load(open(L.OUT + "/rank.json"))
want = sys.argv[1:] or ["6anjqMeW", "AMDEmVoc", "DsGJkPzF", "C5EMTGGE", "53DnQU1d"]
def x_of(r): return r["mult"] if r["sold"] else r.get("mark")
def per(t): return "P1" if t < 1792713600 else "P2" if t < 1793060400 else "P3"   # Oct 23 00:00 and Oct 27 00:20 UTC
def show(name, rs):
    v = [(r["size"], x_of(r)) for r in rs if x_of(r)]
    sold = [r for r in rs if r["sold"]]; hs = [r["hold_s"] for r in sold if r.get("hold_s") is not None]
    ret = sum(a * (x - 1) for a, x in v) / sum(a for a, _ in v) if v else float("nan")
    won = sum(1 for r in sold if r["mult"] > 1)
    print(f"    {name:14s} coins {len(rs):4d}  sold {len(sold):4d}  won {won:4d} ({won / max(len(sold), 1):4.0%})  "
          f"median hold {statistics.median(hs) if hs else float('nan'):6.0f} s  gross return {ret:+.3f}")
for u in R["recs"]:
    if not u.startswith(tuple(want)): continue
    rs = R["recs"][u]; print(u)
    for lo, hi in ((0, .45), (.45, .8), (.8, 1.5), (1.5, 99)):
        g = [r for r in rs if lo <= r["size"] < hi]
        if g: show(f"{lo}-{hi} SOL", g)
    for p in ("P1", "P2", "P3"):
        g = [r for r in rs if per(r["bt"]) == p]
        if g: show(p, g)
    for o, n in ((True, "other quote"), (False, "SOL quote")):
        g = [r for r in rs if r["other"] == o]
        if g: show(n, g)
    sold = [r for r in rs if r["sold"]]; h = [r["hold_s"] for r in sold if r.get("hold_s") is not None]
    import collections
    print(f"    hold to its first sale, s: most common {collections.Counter(h).most_common(8)}; "
          + ", ".join(f"{lo}-{hi} s {sum(1 for x in h if lo <= x < hi)}" for lo, hi in ((0, 6), (6, 60), (60, 300), (300, 900), (900, 1800), (1800, 10**6))))
    print(f"    first sale sold everything (>= 99% of its early tokens) on {sum(1 for r in sold if r['sold_part'] >= 0.99)} of {len(sold)}; "
          f"no sale seen by wallet 4's sale {len(rs) - len(sold)} (path complete on {sum(1 for r in rs if not r['sold'] and not r['sampled'])})")
