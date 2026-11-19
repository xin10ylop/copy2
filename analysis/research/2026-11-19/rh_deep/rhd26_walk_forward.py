# Walk-forward: is the METHOD profitable on data it never saw? (Nov 19 audit; the owner: "have you run everything on
# unseen data to check for overfitting?"). The wallets were chosen on all the data (rhd1's P3 scored the exit, but the
# finalists were then picked by P3 too), so the backtest of the chosen wallets is in-sample. Here, for each week W, the
# screen is redone with ONLY the data before W: every identity with 10+ first buys before W, its exit picked among rhd1's
# seven on that data (sum without the best 2%), kept if positive without the best 2% and in both halves of its past;
# the top N by that past result are then copied in W, unseen, with the exit chosen before W. rhd1's screen.npz values
# (exact model, landing 2/3/5 blocks, our 0.02 ETH); data to Nov 19 00:31 UTC.
#   python3 -I rhd26_walk_forward.py DIR SCREEN_NPZ > out/rhd26_walk_forward.txt
import sys, os, collections, datetime as dt, numpy as np
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
D, NPZ = sys.argv[1], sys.argv[2]; DATA = R.Data(D); z = np.load(NPZ)
VAL = {k: (t, x) for k, t, x in zip(z["keys"], z["t"], z["X"])}
firsts = collections.defaultdict(list)
for c in DATA.L:
    if c not in DATA.TR: continue
    tr = DATA.path(c); sr, sc = set(), set()
    for j, e in enumerate(tr):
        if not e["buy"] or e["q"] / 1e9 < 0.01 or e["t"] > DATA.t_end - 600: continue
        k = f"{c}:{j}"
        if e["user"] not in sr: sr.add(e["user"]); (k in VAL) and firsts["rec:" + e["user"]].append(k)
        if e["caller"] != e["user"] and e["caller"] not in sc: sc.add(e["caller"]); (k in VAL) and firsts["call:" + e["caller"]].append(k)
ID = {u: (np.array([VAL[k][0] for k in v]), np.array([VAL[k][1] for k in v])) for u, v in firsts.items() if len(v) >= 10}
ALLT = z["t"]; ALLX = z["X"]
def w2(x):
    k = max(1, round(0.02 * len(x))); return np.sort(x)[:-k].sum() if len(x) > k else 0.0
day = 86400; t0 = dt.datetime(2026, 10, 22, tzinfo=dt.UTC).timestamp(); tend = float(ALLT.max())
weeks = []; s = t0
while s < tend: weeks.append((s, min(s + 7 * day, tend + 1))); s += 7 * day
NS = [3, 5, 10, 20, 50]
print(f"identities with 10+ first buys: {len(ID)}; weeks from {dt.datetime.fromtimestamp(t0, dt.UTC):%m-%d}; our 0.02 ETH a copy")
tot = {n: [0, 0.0] for n in NS}; tot["all passers"] = [0, 0.0]; tot["market"] = [0, 0.0]
for a, b in weeks:
    pas = []
    for u, (T, X) in ID.items():
        old = T < a
        if old.sum() < 10: continue
        e = int(np.argmax([w2(X[old, i]) for i in range(X.shape[1])])); x = X[old, e]; To = T[old]; mid = np.median(To)
        if w2(x) <= 0 or x[To < mid].sum() <= 0 or x[To >= mid].sum() <= 0: continue
        new = (T >= a) & (T < b)
        pas.append((w2(x), u, e, X[new, e]))
    pas.sort(key=lambda r: -r[0])
    for who in ("rec:0x9a3955a1", "rec:0x5bc235ac", "rec:0xc54d3914", "rec:0xe3fdae6c", "call:0xd6d35b56"):
        hit = [(i, r) for i, r in enumerate(pas) if r[1].startswith(who)]
        print(f"      {who:16s} " + (f"passed before the week, rank {hit[0][0] + 1}; unseen: {len(hit[0][1][3])} copies {hit[0][1][3].sum():+.3f} ETH" if hit else "NOT passed before the week (would not be chosen)"))
    m = (ALLT >= a) & (ALLT < b); mk = ALLX[m, 3]   # a random market buy under "held 600 s"
    line = f"week {dt.datetime.fromtimestamp(a, dt.UTC):%m-%d} to {dt.datetime.fromtimestamp(b, dt.UTC):%m-%d}: {len(pas)} passed before it;"
    for n in NS + ["all passers"]:
        sel = pas if n == "all passers" else pas[:n]; x = np.concatenate([r[3] for r in sel]) if sel else np.array([])
        tot[n][0] += len(x); tot[n][1] += x.sum()
        line += f"  top {n}: {len(x)} copies {x.sum():+.3f} ETH ({100 * x.mean() / R.STAKE if len(x) else 0:+.1f}%)" if n != "all passers" else f"  all: {len(x)} {x.sum():+.3f} ({100 * x.mean() / R.STAKE if len(x) else 0:+.1f}%)"
    tot["market"][0] += len(mk); tot["market"][1] += mk.sum()
    print(line)
    print(f"      the top 5 chosen before it: " + ", ".join(f"{r[1][:14]} ({len(r[3])} copies {r[3].sum():+.3f})" for r in pas[:5]))
print("\nALL WEEKS, UNSEEN: " + "; ".join(f"{k}: {v[0]} copies {v[1]:+.3f} ETH ({100 * v[1] / max(1, v[0]) / R.STAKE:+.1f}% a copy)" for k, v in tot.items()))
