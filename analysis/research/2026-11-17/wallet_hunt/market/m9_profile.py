# The owner (Nov 19): "not copying, but on the wallets we identify": learn WHAT the daily winners do, to trade the rule
# ourselves at the moment they act. Their every round trip on the 4 days (m7's wallets that are up every day and do not
# buy at the launch): at their buy, the coin's age, the curve's progress (SOL-equivalent in the curve), the price
# against the coin's high so far (a dip?), the last 30 s of flow; then how long they hold, how they leave (all at once?),
# and what each trade made them. Medians, and winners against losers.
#   LAUNCHES=<the 3 launch lists> python3 -I m9_profile.py SP > ../out/m9_profile.txt
import sys, os, json, gzip, collections, numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import m4_direct as M, m7_own_vs_copy as M7
WHO = ["ARu4n5mFdZog", "AEdnzgqMSSR8", "HLU8QbLdvHDS", "HryU8vPBVcmw", "FZU56d9iPqoh", "9dVSVwrUJfnF"]
FULL = {u for u, *_ in M7.R if any(u.startswith(w) for w in WHO)}; COINS = collections.defaultdict(set)
for u, m, *_ in M7.R:
    if u in FULL: COINS[m].add(u)
def trips(m):
    rate = M.rate_of(M.L[m]["quote"]); tr = json.load(gzip.open(f"{M.PD}/{m}.json.gz")); out = []
    t_launch = tr[0]["t"]; px = [(e["vq"] / e["vt"]) for e in tr]; hi = np.maximum.accumulate(px)
    for u in COINS[m]:
        idx = [i for i, e in enumerate(tr) if e["user"] == u]
        b = next((i for i in idx if tr[i]["buy"]), None)
        if b is None: continue
        spent = sum(tr[i]["q"] * (1 + tr[i]["bps"] / 1e4) for i in idx if tr[i]["buy"]) * rate / 1e9
        got = sum(tr[i]["q"] * (1 - tr[i]["bps"] / 1e4) for i in idx if not tr[i]["buy"]) * rate / 1e9
        tok = sum(tr[i]["tok"] * (1 if tr[i]["buy"] else -1) for i in idx); got += max(tok, 0) * px[-1] * rate / 1e9
        sells = [i for i in idx if not tr[i]["buy"] and i > b]; buys = [i for i in idx if tr[i]["buy"]]
        w30 = [e for e in tr[:b] if tr[b]["t"] - e["t"] <= 30]
        out.append(dict(u=u[:12], m=m, pnl=got - spent, spent=spent, ret=(got - spent) / spent if spent else 0,
            age=tr[b]["t"] - t_launch, prog=(tr[b - 1]["vq"] if b else tr[b]["vq"]) * rate / 1e9, dip=(px[b - 1] / hi[b - 1] if b else 1.0),
            n_before=b, buys30=sum(1 for e in w30 if e["buy"]), sells30=sum(1 for e in w30 if not e["buy"]),
            hold=(tr[sells[0]]["t"] - tr[b]["t"]) if sells else None, nsell=len(sells), nbuy=len(buys),
            rise_at_first_sale=(px[sells[0]] / px[b]) if sells else None))
    return out
if __name__ == "__main__":
    with Pool(8) as P: T = [x for part in P.map(trips, sorted(COINS), chunksize=8) for x in part]
    med = lambda v: float(np.median([x for x in v if x is not None])) if any(x is not None for x in v) else float("nan")
    q = lambda v, p: float(np.percentile([x for x in v if x is not None], p)) if any(x is not None for x in v) else float("nan")
    print(f"{len(T)} round trips of {len(FULL)} wallets on the 4 days\n")
    print("wallet        trips  net SOL  won%  size   age at buy (med, 10-90%)    curve SOL at buy   price/high   trades before   buys/sells 30s   hold s (med)  sales  rise at 1st sale")
    for w in WHO:
        v = [x for x in T if x["u"] == w]
        if not v: continue
        g = lambda k: [x[k] for x in v]
        print(f"{w}  {len(v):5d}  {sum(g('pnl')):+7.1f}  {100 * np.mean([x['pnl'] > 0 for x in v]):3.0f}%  {med(g('spent')):5.2f}   {med(g('age')):7.0f} ({q(g('age'), 10):.0f}-{q(g('age'), 90):.0f})"
              f"     {med(g('prog')):8.2f}           {med(g('dip')):5.2f}       {med(g('n_before')):6.0f}        {med(g('buys30')):4.0f}/{med(g('sells30')):<4.0f}      {med(g('hold')):7.0f}     {med(g('nsell')):3.0f}     {med(g('rise_at_first_sale')):5.2f}")
    print("\nwinners against losers (all six together):")
    for lab, f in (("won", lambda x: x["pnl"] > 0), ("lost", lambda x: x["pnl"] <= 0)):
        v = [x for x in T if f(x)]; g = lambda k: [x[k] for x in v]
        print(f"   {lab:5s} {len(v):5d} trips  net {sum(g('pnl')):+8.1f}  age {med(g('age')):6.0f} s  curve {med(g('prog')):6.2f}  price/high {med(g('dip')):.2f}  trades before {med(g('n_before')):5.0f}  "
              f"buys/sells 30s {med(g('buys30')):.0f}/{med(g('sells30')):.0f}  hold {med(g('hold')):5.0f} s  rise at 1st sale {med(g('rise_at_first_sale')):.2f}")
    json.dump(T, gzip.open(f"{M.O}/m9_trips.json.gz", "wt"))
