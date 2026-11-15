# Top holders selling, with their real bags (build.py: each trader's balance before and after every trade since wallet
# 4's buy). A pump coin has 1,000,000,000 tokens; a bag is given as its share of them. Signals, each ADDED to the live
# setup (tp 4.0, 600 s, early 30-290 s under 1.5x, sell_pressure [5, 60, 30], stall 180 s), as ../signals/round3.py:
#   whale    a wallet holding s% of the supply or more sells (any part of it)
#   exit     a wallet holding s% or more sells its whole bag (90%+ of it)
#   exits    k such whole-bag exits (bags of 0.5%+) within W s
#   top      one of the K biggest bags known at that moment sells half of its bag or more (known = every wallet that
#            has traded since wallet 4's buy, at its balance after its last trade; bags of 0.2%+ only)
#   tops     k different wallets of the 10 biggest known bags sell half or more within 120 s
#   each from 30 s after its buy; whale / exit / top also only while the price is under 1.5x our buy
#   python3 -I holders.py CQ ALL BAGS > out/holders.txt
import sys, os, json, gzip, bisect, random, collections
import numpy as np
BAGS = sys.argv[3]
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "signals")); sys.argv = sys.argv[:3]
import round3 as R3
from round3 import L, ROWS, PREP, EX, S2
B = json.load(gzip.open(f"{BAGS}/bags.json.gz"))
unknown = total = 0
for (key, n), x in EX.items():
    k = len(x["user"]); b = B[key][len(B[key]) - k:] if k else []
    pre = np.array([max(a, 0) for a, _ in b], dtype=float) / 1e15; post = np.array([max(c, 0) for _, c in b], dtype=float) / 1e15
    sold = np.where(x["sell"], x["tok"], 0)
    pre = np.maximum(pre, sold)                               # a bag not found (a router's account): at least what it sold
    if n == 4: total += int(x["sell"].sum()); unknown += int((x["sell"] & (np.array([a for a, _ in b]) <= 0)).sum()) if k else 0
    x["pre"], x["full"] = pre, x["sell"] & (post <= 0.1 * pre)
    rank = np.full(k, 999); bal, srt = {}, []                # the seller's rank among the bags known just before its sale
    for i, u in enumerate(x["user"]):
        if not x["other"][i]: continue
        if x["sell"][i]: rank[i] = 1 + len(srt) - bisect.bisect_right(srt, pre[i])
        old = bal.get(u)
        if old is not None: srt.pop(bisect.bisect_left(srt, old))
        bal[u] = post[i]; bisect.insort(srt, post[i])
    x["rank"] = rank; x["half"] = x["sell"] & (sold >= 0.5 * pre)
r3_trigger = R3.trigger
def trigger(p, x, sig):
    kind = sig[0]
    if kind not in ("whale", "exit", "exits", "top", "tops"): return r3_trigger(p, x, sig)
    age, px = p["age"], p["px"] / x["pin"]; n = len(age)
    if n == 0: return None
    ok = age >= 30
    if kind in ("whale", "exit", "top") and sig[3]: ok = ok & (px < sig[3])
    if kind == "whale": return L.first(x["sell"] & (x["pre"] >= sig[1]) & ok)
    if kind == "exit": return L.first(x["full"] & (x["pre"] >= sig[1]) & ok)
    if kind == "top": return L.first(x["half"] & (x["rank"] <= sig[1]) & (x["pre"] >= 0.002) & ok)
    lo = np.searchsorted(age, age - sig[2], side="left")
    if kind == "exits":
        c = np.concatenate([[0], np.cumsum(x["full"] & (x["pre"] >= 0.005))]); return L.first(((c[1:] - c[lo]) >= sig[1]) & ok)
    f = x["half"] & (x["rank"] <= 10) & (x["pre"] >= 0.002)   # tops
    for i in np.nonzero(f & ok)[0]:
        if len({x["user"][q] for q in range(lo[i], i + 1) if f[q]}) >= sig[1]: return int(i)
    return None
R3.trigger = trigger
add, score, BASE = R3.add, R3.score, R3.BASE
R = {}
for cap in (None, 1.5):
    c = ", under 1.5x" if cap else ""
    for s in (0.01, 0.02, 0.03, 0.05): R[f"whale: a {s * 100:.0f}%+ holder sells{c}"] = add(("whale", s, 0, cap))
    for s in (0.005, 0.01, 0.02, 0.03): R[f"exit: a {s * 100:g}%+ holder sells its whole bag{c}"] = add(("exit", s, 0, cap))
    for K in (1, 3, 5, 10): R[f"top: one of the {K} biggest known bags sells half+{c}"] = add(("top", K, 0, cap))
for k in (2, 3, 5):
    for W in (60, 120): R[f"exits: {k} whole-bag exits (0.5%+ bags) in {W} s"] = add(("exits", k, W, None))
for k in (2, 3, 4): R[f"tops: {k} of the 10 biggest known bags sell half+ in 120 s"] = add(("tops", k, 120, None))
B0 = score(BASE); random.seed(7)
print(f"{len(ROWS)} buys; {total} sells by others after our buy (landing 4), the bag not found for {unknown}; {len(R)} additions to the live setup")
hdr = f"   {'rule':62s} | total  | gain   | A      B      C      | w/o best 5 | days<0 | worst | ahead in draws | exits by it"
def row(nm, s):
    g = [a - b for a, b in zip(s["days"], B0["days"])]; dr = [sum(random.choice(g) for _ in g) for _ in range(1000)]
    mine = sum(c for w, c in s["whys"].items() if w in ("whale", "exit", "exits", "top", "tops"))
    return f"   {nm:62s} | {s['tot']:+6.2f} | {s['tot'] - B0['tot']:+6.2f} | {s['b'][0]:+6.2f} {s['b'][1]:+6.2f} {s['b'][2]:+6.2f} | {s['wo5']:+6.2f}     | {s['neg']:2d}/{s['nd']} | {s['worst']:+5.2f} | {100 * sum(1 for y in dr if y > 0) / 1000:5.1f}%         | {mine:.0f}"
print("== the live setup\n" + hdr + "\n" + row("live", B0))
S = {nm: score(r) for nm, r in R.items()}
for f in ("whale", "exit", "top", "exits", "tops"):
    xs = [(nm, s) for nm, s in S.items() if nm.split(":")[0] == f]
    print(f"== {f}: {sum(1 for nm, s in xs if s['tot'] > B0['tot'])} of {len(xs)} ahead of the live setup, {sum(1 for nm, s in xs if all(s['b'][i] > B0['b'][i] for i in range(3)))} in all three blocks\n" + hdr)
    for nm, s in xs: print(row(nm, s))
print("== picked on two blocks, scored on the third (gain over the live setup in the held-out block)")
tot = 0
for held in range(3):
    other = [i for i in range(3) if i != held]
    rk = sorted(S.items(), key=lambda q: -sum(q[1]["b"][i] for i in other))
    g = rk[0][1]["b"][held] - B0["b"][held]; tot += g
    print(f"   held out {'ABC'[held]}: picked '{rk[0][0]}' ({sum(rk[0][1]['b'][i] - B0['b'][i] for i in other):+.2f} on the other two) -> {g:+.2f}; the 10 best picks on average {sum(s['b'][held] - B0['b'][held] for nm, s in rk[:10]) / 10:+.2f}")
print(f"   total out of sample: {tot:+.2f} SOL")
# what the bags look like: how big are the bags that sell, and how often is it the whole bag
pre = np.concatenate([x["pre"][x["sell"]] for (k, n), x in EX.items() if n == 4]); full = np.concatenate([x["full"][x["sell"]] for (k, n), x in EX.items() if n == 4])
print("== the sellers' bags (landing 4): share of sells by bag size, and how many of them sold the whole bag")
for lo_, hi_ in ((0, 0.002), (0.002, 0.005), (0.005, 0.01), (0.01, 0.02), (0.02, 0.05), (0.05, 1)):
    m = (pre >= lo_) & (pre < hi_); print(f"   bag {lo_ * 100:g}% to {hi_ * 100:g}% of supply: {100 * m.mean():5.1f}% of sells, {100 * full[m].mean() if m.any() else 0:5.1f}% of them the whole bag")
