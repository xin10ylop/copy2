# The owner (Nov 19): "of course there are wallets that every day have a big winner that covers all the losses". Two
# different things: the WALLET's own result and OUR COPY of it. On the same 4 days (m6_days.py's copies, saved in
# SP/market/m6_rows.json.gz), each wallet's OWN result on each coin it bought 0.5+ SOL first: SOL out of its sales minus
# SOL into its buys, plus the tokens it still held at the curve's last price (fees as charged; no price impact on the
# leftover). By day of its first buy. Wallets that THEMSELVES win every active day (3+) with a big winner (+100% on a
# coin) every day; their own result against our copy; then BLIND: picked on their own days 1-2, our copy on days 3-4.
#   LAUNCHES=<the 3 launch lists> python3 -I m7_own_vs_copy.py SP > ../out/m7_own_vs_copy.txt
import sys, os, json, gzip, collections, numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import m4_direct as M
R = json.load(gzip.open(f"{M.O}/m6_rows.json.gz")); PAIRS = collections.defaultdict(set)
for u, m, *_ in R: PAIRS[m].add(u)
def own(m):
    rate = M.rate_of(M.L[m]["quote"]) if m in M.L else None
    if rate is None: return {}
    tr = json.load(gzip.open(f"{M.PD}/{m}.json.gz")); want = PAIRS[m]; acc = collections.defaultdict(lambda: [0.0, 0.0, 0.0])
    for e in tr:
        u = e["user"]
        if u not in want: continue
        a = acc[u]
        if e["buy"]: a[0] += e["q"] * (1 + e["bps"] / 1e4) * rate / 1e9; a[2] += e["tok"]
        else: a[1] += e["q"] * (1 - e["bps"] / 1e4) * rate / 1e9; a[2] -= e["tok"]
    last = tr[-1]; px = last["vq"] / last["vt"] * rate / 1e9
    return {u: (a[1] + max(a[2], 0) * px - a[0], a[0]) for u, a in acc.items()}
if __name__ == "__main__":
    with Pool(8) as P: O = dict(zip(sorted(PAIRS), P.map(own, sorted(PAIRS), chunksize=20)))
    t0 = min(r[2] for r in R); DAY = 86400; W = collections.defaultdict(list)
    for u, m, t, sol, v, cre, off in R:
        o = O.get(m, {}).get(u)
        if o: W[u].append(dict(d=int((t - t0) // DAY), own=o[0], spent=o[1], copy=v, t=t))
    def judge(v):
        days = collections.defaultdict(lambda: [0.0, 0, 0.0])
        for x in v: d = days[x["d"]]; d[0] += x["own"]; d[1] += x["own"] >= x["spent"]; d[2] += x["copy"]
        return days
    hits = []
    for u, v in W.items():
        days = judge(v)
        if len(days) >= 3 and all(d[0] > 0 and d[1] >= 1 for d in days.values()): hits.append((u, v, days))
    allown = sum(x["own"] for v in W.values() for x in v); allcopy = sum(x["copy"] for v in W.values() for x in v)
    print(f"{len(W)} wallets, {sum(len(v) for v in W.values())} coins (their first buy 0.5+ SOL), 4 days. All together: their own result {allown:+.0f} SOL, our copy {allcopy:+.0f} SOL")
    print(f"\n== THEMSELVES up on every active day (3+ days), each day with a big winner (+100% on a coin): {len(hits)} wallets ==")
    print("   wallet        coins  days  their own SOL  (big winners)   OUR COPY SOL  a copy    by day: own / copy")
    for u, v, days in sorted(hits, key=lambda h: -sum(x["own"] for x in h[1])):
        oc = sum(x["copy"] for x in v)
        print(f"   {u[:12]}  {len(v):5d}  {len(days):4d}  {sum(x['own'] for x in v):+12.2f}  ({sum(1 for x in v if x['own'] >= x['spent']):3d})        {oc:+8.2f}  {100 * oc / len(v) / 0.5:+6.1f}%   "
              + "  ".join(f"{d[0]:+.1f}/{d[2]:+.1f}" for _, d in sorted(days.items())))
    h_own = sum(x["own"] for _, v, _ in hits for x in v); h_copy = sum(x["copy"] for _, v, _ in hits for x in v); h_n = sum(len(v) for _, v, _ in hits)
    print(f"   together: their own {h_own:+.2f} SOL; our copy {h_copy:+.2f} SOL on {h_n} copies ({100 * h_copy / max(1, h_n) / 0.5:+.1f}% a copy)")
    pick = []
    for u, v in W.items():
        a = [x for x in v if x["d"] < 2]; b = [x for x in v if x["d"] >= 2]; days = judge(a)
        if len(days) == 2 and all(d[0] > 0 and d[1] >= 1 for d in days.values()): pick.append((u, a, b))
    xs = [x["copy"] for _, _, b in pick for x in b]; ys = [x["own"] for _, _, b in pick for x in b]
    print(f"\n== BLIND: chosen on THEIR OWN days 1-2 (up both days, a big winner both days): {len(pick)} wallets ==")
    print(f"   days 3-4 (unseen): their own {sum(ys):+.2f} SOL; OUR COPY {sum(xs):+.2f} SOL on {len(xs)} copies ({100 * np.mean(xs) / 0.5 if xs else 0:+.1f}% a copy); "
          f"wallets whose copy was up on days 3-4: {sum(1 for *_, b in pick if b and sum(x['copy'] for x in b) > 0)} of {sum(1 for *_, b in pick if b)}; "
          f"themselves up on days 3-4: {sum(1 for *_, b in pick if b and sum(x['own'] for x in b) > 0)}")
