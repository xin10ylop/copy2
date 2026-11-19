# The deep redo of the Robinhood search (Nov 19; the owner: "re do the whole process to check that any wallets have been
# missed, more deeply"). What the first pass (rh5_direct.py) did not do, done here:
#   - the exact curve, and no coin left out for going quiet (rhd_lib.py)
#   - 10+ copyable first buys (was 20+), buys of 0.01+ ETH (was 0.05+), the data refreshed to Nov 19 and back to its start
#   - two identities: the RECIPIENT of the buy (as before) and the CALLER (the contract or wallet that called the curve:
#     one operator's bot contract buying into many wallets shows up only here)
#   - three periods by time instead of two halves; the exit picked on the older two, scored on the newest
#   - a NULL: pseudo-wallets made of random copyable buys of the market (same count in each period), put through the
#     same test, so the number of passes chance alone gives is known
# Seven exits fixed before looking (rhd_lib.EXITS). Out: OUT/screen.npz (per buy: identity, time, its ETH, the 7 values).
#   python3 -I rhd1_screen.py DIR OUT > out/rhd1_screen.txt     (MINC=10 MINQ=0.01 NULL=20000)
import sys, os, collections, numpy as np, datetime as dt, random
from multiprocessing import Pool
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
D, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
MINC = int(os.environ.get("MINC", 10)); MINQ = float(os.environ.get("MINQ", 0.01)); NNULL = int(os.environ.get("NULL", 20000))
DATA = R.Data(D); ETHC = [c for c in DATA.L if c in DATA.TR]
print(f"data {dt.datetime.fromtimestamp(DATA.t_start, dt.UTC):%m-%d %H:%M} to {dt.datetime.fromtimestamp(DATA.t_end, dt.UTC):%m-%d %H:%M} UTC; "
      f"{len(DATA.L)} ETH-quoted launches ({len(ETHC)} traded), {sum(DATA.OTHER.values())} launches in other quote tokens (not copyable by the bot)")
# every first buy (per identity and curve) of MINQ+ ETH, at least 600 s before the data ends
firsts = collections.defaultdict(list); allbuys = []
for c in ETHC:
    tr = DATA.path(c); sr, sc = set(), set()
    for j, e in enumerate(tr):
        if not e["buy"] or e["q"] / 1e9 < MINQ or e["t"] > DATA.t_end - 600: continue
        if e["user"] not in sr: sr.add(e["user"]); firsts["rec:" + e["user"]].append((c, j)); allbuys.append((c, j))
        if e["caller"] != e["user"] and e["caller"] not in sc: sc.add(e["caller"]); firsts["call:" + e["caller"]].append((c, j))
cand = {u: v for u, v in firsts.items() if len(v) >= MINC}
ncall = sum(1 for u in cand if u.startswith("call:"))
print(f"{len(allbuys):,} first buys of {MINQ}+ ETH; identities with {MINC}+: {len(cand)} ({len(cand) - ncall} recipients, {ncall} callers)")
rng = random.Random(7); null_pool = rng.sample(allbuys, min(NNULL, len(allbuys)))
todo = sorted({x for v in cand.values() for x in v} | set(null_pool))
print(f"buys to value: {len(todo):,}", flush=True)
_cache = {}
def value(cj):
    c, j = cj
    if c not in _cache: _cache.clear(); _cache[c] = DATA.path(c)
    tr = _cache[c]; prems, vals = R.copy_one(tr, j)
    return cj, tr[j]["t"], tr[j]["q"] / 1e9, tr[j]["vq"] / 1e9 - R.V0 - (tr[j]["vq"] / 1e9 - (tr[j - 1]["vq"] / 1e9 if j else R.V0)), R.fixed_vals(prems, vals)
todo.sort()
with Pool(4) as pool: V = {r[0]: r[1:] for r in pool.imap(value, todo, chunksize=64)}
P1, P2 = DATA.t_start + (DATA.t_end - DATA.t_start) / 3, DATA.t_start + 2 * (DATA.t_end - DATA.t_start) / 3
per = lambda t: 0 if t < P1 else (1 if t < P2 else 2)
print(f"periods: P1 to {dt.datetime.fromtimestamp(P1, dt.UTC):%m-%d %H:%M}, P2 to {dt.datetime.fromtimestamp(P2, dt.UTC):%m-%d %H:%M}, P3 to the end (UTC); our {R.STAKE} ETH a copy, landings +{R.LANDB} blocks")
def w2(x):
    k = max(1, round(0.02 * len(x))); return np.sort(x)[:-k].sum() if len(x) > k else 0.0
def test(X, Pp):
    """X: copies x exits (ETH), Pp: their periods. Pick the exit on P1+P2 (sum without the best 2%), score it on P3."""
    old, new = Pp < 2, Pp == 2
    if old.sum() < 8 or new.sum() < 4: return None
    e = int(np.argmax([w2(X[old, i]) for i in range(X.shape[1])]))
    x = X[:, e]; ok_old = w2(x[old]) > 0 and all(x[Pp == p].sum() > 0 for p in (0, 1) if (Pp == p).sum() >= 4)
    return dict(e=e, n=len(x), n3=int(new.sum()), old=x[old].sum(), old2=w2(x[old]), p3=x[new].sum(), pct=100 * x.mean() / R.STAKE, pct3=100 * x[new].mean() / R.STAKE,
                tot=x.sum(), passed=bool(ok_old and x[new].sum() > 0))
res = {}
for u, v in cand.items():
    X = np.array([V[cj][3] for cj in v]); T = np.array([V[cj][0] for cj in v]); Pp = np.array([per(t) for t in T])
    r = test(X, Pp)
    if r: r["counts"] = [int((Pp == p).sum()) for p in range(3)]; res[u] = r
passed = {u: r for u, r in res.items() if r["passed"]}
# the null: pseudo-wallets with the same number of copies in each period, drawn from the random market buys
NP = collections.defaultdict(list)
for cj in null_pool: NP[per(V[cj][0])].append(cj)
nrng = np.random.default_rng(11); exp_pass = 0.0; NREP = 100
for u, r in res.items():
    hits = 0
    for _ in range(NREP):
        pick = [NP[p][i] for p in range(3) for i in nrng.integers(0, len(NP[p]), r["counts"][p])]
        X = np.array([V[cj][3] for cj in pick]); Pp = np.array([per(V[cj][0]) for cj in pick]); rr = test(X, Pp)
        hits += bool(rr and rr["passed"])
    r["null"] = hits / NREP; exp_pass += hits / NREP
mk = np.array([V[cj][3] for cj in null_pool]); mt = np.array([per(V[cj][0]) for cj in null_pool])
print("\nTHE MARKET (a random copyable buy), ETH a copy by exit, P1 / P2 / P3:")
for i, (lab, _, _) in enumerate(R.EXITS): print(f"   {lab:44s} " + " / ".join(f"{100 * mk[mt == p, i].mean() / R.STAKE:+5.1f}%" for p in range(3)))
print(f"\nidentities tested (8+ copies in P1+P2, 4+ in P3): {len(res)}; PASSED: {len(passed)}; chance alone would pass about {exp_pass:.0f}")
print("\nPASSED, by P3's result (exit picked on P1+P2; null = how often a random wallet of the same size passes):")
print(f"   {'identity':52s} {'copies P1/P2/P3':>16s}  {'exit':44s} {'P1+P2 w/o 2%':>12s} {'P3':>9s} {'a copy':>7s} {'P3 a copy':>9s} {'null':>5s}")
for u, r in sorted(passed.items(), key=lambda x: -x[1]["p3"]):
    print(f"   {u:52s} {'/'.join(map(str, r['counts'])):>16s}  {R.EXITS[r['e']][0]:44s} {r['old2']:+12.4f} {r['p3']:+9.4f} {r['pct']:+6.1f}% {r['pct3']:+8.1f}% {r['null']:5.2f}")
np.savez_compressed(f"{OUT}/screen.npz", keys=np.array([f"{c}:{j}" for c, j in V]), t=np.array([V[k][0] for k in V]), q=np.array([V[k][1] for k in V]),
                    prog=np.array([V[k][2] for k in V]), X=np.array([V[k][3] for k in V]))
import json; json.dump({"cand": {u: [f"{c}:{j}" for c, j in v] for u, v in cand.items()}, "res": res, "P": [P1, P2]}, open(f"{OUT}/screen.json", "w"))
