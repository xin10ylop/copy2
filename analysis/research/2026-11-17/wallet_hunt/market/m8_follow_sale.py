# m7's winners are profitable themselves every day, our copy under wallet 4's exits loses. A fair second exit for a
# wallet that trades fast: SELL WHEN IT SELLS (at the next trade after its first sale), else at 600 s / tp 4. Same
# landings (4 / 8 trades, the next slot; refused past 1.25x), 0.5 SOL, 0.0345 SOL a round trip. On m7's 16 wallets, and
# on m7's blind pick (39 wallets chosen on their own days 1-2, scored on days 3-4).
#   LAUNCHES=<the 3 launch lists> python3 -I m8_follow_sale.py SP > ../out/m8_follow_sale.txt
import sys, os, json, gzip, collections, numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import m4_direct as M, m7_own_vs_copy as M7
H = M.H
def first(c): i = int(np.argmax(c)) if len(c) else 0; return i if len(c) and c[i] else None
def val(p, rule, stake=0.5):
    if p["refused"]: return -0.0004
    vt0, vq0, b0 = p["ent"]; Q = stake * 1e9 / p["rate"]; net_in = Q * 1e4 / (1e4 + b0); tok = vt0 - vt0 * vq0 / (vq0 + net_in); n = len(p["px"])
    def out(ex):
        vq, vt, b = (vq0, vt0, b0) if ex is None else (p["vq"][ex], p["vt"][ex], p["bps"][ex]); vq_r = vq + net_in; vt_r = vt * vq / vq_r
        return (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - b / 1e4) * p["rate"] / 1e9 - stake - 0.0026
    if n == 0: return out(None)
    c = [n - 1]; i = first(p["grad"]); c += [i] if i is not None else []
    i = first(p["age"] >= 600); c += [i] if i is not None else []
    i = first(p["px"] >= 4.0); c += [min(i + 1, n - 1)] if i is not None else []
    if rule == "its sale": i = first(p["sell"]); c += [min(i + 1, n - 1)] if i is not None else []
    return out(min(c))
def job(arg):
    m, us = arg; rate = M.rate_of(M.L[m]["quote"]); tr = json.load(gzip.open(f"{M.PD}/{m}.json.gz")); res = []
    first_i = {}
    for i, e in enumerate(tr):
        if e["user"] in us and e["user"] not in first_i and e["buy"]: first_i[e["user"]] = i
    for u, i in first_i.items():
        ps = [H.prep(tr, i, rate, n) for n in (4, 8, "slot+1")]
        res.append((u, m, tr[i]["t"], np.mean([val(p, "its sale") for p in ps]) - M.COST))
    return res
if __name__ == "__main__":
    R = M7.R; t0 = min(r[2] for r in R); DAY = 86400
    names = ["8YcbyX92UHTU", "H9kuqGKNYgPF", "ARu4n5mFdZog", "AEdnzgqMSSR8", "TAB16RxXmazW", "HLU8QbLdvHDS", "BddzswyZNG5H", "5fMFE7rb8wSg",
             "AmNkdH7iX5ZF", "HryU8vPBVcmw", "BodzhZVG125i", "8FoG67wza3w4", "4pkm1cA7bXkL", "FZU56d9iPqoh", "9dVSVwrUJfnF", "CWJSBe7SemKo"]
    full = {u for u, *_ in R if any(u.startswith(n) for n in names)}
    with Pool(8) as P: O = dict(zip(sorted(M7.PAIRS), P.map(M7.own, sorted(M7.PAIRS), chunksize=20)))
    W = collections.defaultdict(list)
    for u, m, t, sol, v, cre, off in R:
        o = O.get(m, {}).get(u)
        if o: W[u].append(dict(d=int((t - t0) // DAY), own=o[0], spent=o[1]))
    blind = set()
    for u, v in W.items():
        days = collections.defaultdict(lambda: [0.0, 0])
        for x in v:
            if x["d"] < 2: days[x["d"]][0] += x["own"]; days[x["d"]][1] += x["own"] >= x["spent"]
        if len(days) == 2 and all(d[0] > 0 and d[1] >= 1 for d in days.values()): blind.add(u)
    want = full | blind; jobs = collections.defaultdict(set)
    for u, m, *_ in R:
        if u in want: jobs[m].add(u)
    with Pool(8) as P: X = [r for part in P.map(job, list(jobs.items()), chunksize=8) for r in part]
    by = collections.defaultdict(list)
    for u, m, t, v in X: by[u].append((t, v))
    print("== m7's 16 (themselves up every day): our copy, SELLING WHEN THEY SELL ==")
    print("   wallet        copies  net SOL  a copy  first 2 days / last 2 days")
    tot = []
    for n in names:
        u = next((x for x in full if x.startswith(n)), None)
        if not u: continue
        v = by[u]; a = sum(x[1] for x in v if x[0] < t0 + 2 * DAY); b = sum(x[1] for x in v if x[0] >= t0 + 2 * DAY); tot += [x[1] for x in v]
        print(f"   {n}  {len(v):6d}  {a + b:+7.2f}  {100 * (a + b) / len(v) / 0.5:+5.1f}%   {a:+.2f} / {b:+.2f}")
    print(f"   together: {sum(tot):+.2f} SOL on {len(tot)} copies ({100 * np.mean(tot) / 0.5:+.1f}% a copy)")
    xs = [x[1] for u in blind for x in by[u] if x[0] >= t0 + 2 * DAY]
    print(f"\n== BLIND ({len(blind)} wallets chosen on their own days 1-2), our copy selling when they sell, days 3-4: {sum(xs):+.2f} SOL on {len(xs)} copies ({100 * np.mean(xs) / 0.5 if xs else 0:+.1f}% a copy); "
          f"wallets up: {sum(1 for u in blind if sum(x[1] for x in by[u] if x[0] >= t0 + 2 * DAY) > 0)} of {sum(1 for u in blind if any(x[0] >= t0 + 2 * DAY for x in by[u]))}")
