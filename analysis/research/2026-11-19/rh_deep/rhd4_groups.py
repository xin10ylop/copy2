# Who the passers are (Nov 19): rhd1's passed identities, strongest first (null <= NULLMAX: a random wallet of the same size
# passes that rarely). (1) Groups: identities that buy the same coins (Jaccard of their copied coins >= 0.3, linked) are
# one signal, scored together (a coin counted once, at the group's first buy). (2) Callers: how many recipients a calling
# contract buys into, and the share of its buys that are first buys of a coin (a router used by the public has
# thousands of recipients; one operator's bot contract a few). (3) Own launches: the share of copied coins the identity
# (or its group) created.
#   python3 -I rhd4_groups.py DIR SCREEN_DIR > out/rhd4_groups.txt   (NULLMAX=0.05)
import sys, os, json, collections, numpy as np, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); import rhd_lib as R
D, SD = sys.argv[1], sys.argv[2]; NULLMAX = float(os.environ.get("NULLMAX", 0.05))
S = json.load(open(f"{SD}/screen.json")); Z = np.load(f"{SD}/screen.npz"); P1, P2 = S["P"]
IX = {k: i for i, k in enumerate(Z["keys"])}; X, T = Z["X"], Z["t"]
per = lambda t: 0 if t < P1 else (1 if t < P2 else 2)
res = S["res"]; good = {u: r for u, r in res.items() if r["passed"] and r["null"] <= NULLMAX}
print(f"passed {sum(r['passed'] for r in res.values())}; with null <= {NULLMAX}: {len(good)}")
coins = {u: {k.split(':')[0] for k in S["cand"][u]} for u in good}
DATA = R.Data(D)
creator = {}
for c in DATA.L:   # the curve's first buyer in its launch block is usually the creator; the deployer is not in the log we keep
    tr = DATA.TR.get(c)
    if tr: creator[c] = sorted(tr)[0][3]
# groups: link identities whose coin sets overlap
us = sorted(good, key=lambda u: -good[u]["p3"]); parent = {u: u for u in us}
def find(u):
    while parent[u] != u: parent[u] = parent[parent[u]]; u = parent[u]
    return u
inv = collections.defaultdict(set)
for u in us:
    for c in coins[u]: inv[c].add(u)
pairs = collections.Counter()
for c, s in inv.items():
    s = sorted(s)
    if len(s) > 60: continue
    for i in range(len(s)):
        for j in range(i + 1, len(s)): pairs[(s[i], s[j])] += 1
for (a, b), n in pairs.items():
    if n / len(coins[a] | coins[b]) >= 0.3: parent[find(a)] = find(b)
G = collections.defaultdict(list)
for u in us: G[find(u)].append(u)
def score(keys):
    x = np.array([X[IX[k]] for k in keys]); t = np.array([T[IX[k]] for k in keys]); p = np.array([per(v) for v in t]); return x, t, p
print(f"\n{len(G)} groups (identities linked when they share 30%+ of their copied coins)\n")
rows = []
for g, mem in G.items():
    # the group's copy: each coin once, at the first buy any member made
    first = {}
    for u in mem:
        for k in S["cand"][u]:
            c = k.split(":")[0]
            if c not in first or T[IX[k]] < T[IX[first[c]]]: first[c] = k
    e = good[mem[0]]["e"]; keys = list(first.values()); x, t, p = score(keys); x = x[:, e]
    own = np.mean([creator.get(k.split(":")[0]) in {m.split(":")[1] for m in mem} for k in keys])
    days = (DATA.t_end - t.min()) / 86400
    rows.append((x[p == 2].sum(), mem, e, x, p, own, len(keys) / max(days, 1)))
print(f"{'group (first member = strongest)':52s} {'members':>7s} {'coins P1/P2/P3':>15s} {'a day':>6s}  {'exit (first member)':44s} {'all':>8s} {'a copy':>7s} {'P3':>8s} {'P3 a copy':>9s} {'own coins':>9s}")
for p3, mem, e, x, p, own, rate in sorted(rows, key=lambda r: -r[0])[:60]:
    cnt = "/".join(str(int((p == i).sum())) for i in range(3))
    print(f"{mem[0]:52s} {len(mem):7d} {cnt:>15s} {rate:6.1f}  {R.EXITS[e][0]:44s} {x.sum():+8.4f} {100 * x.mean() / R.STAKE:+6.1f}% {p3:+8.4f} {100 * x[p == 2].mean() / R.STAKE if (p == 2).any() else 0:+8.1f}% {100 * own:8.0f}%")
    if len(mem) > 1: print(f"      members: {', '.join(m[:15] for m in mem[1:12])}{' ...' if len(mem) > 12 else ''}")
# the callers among the good: recipients and the share of all their buys
print("\nCALLERS (contracts that call the curve) among the good:")
for u in [u for u in us if u.startswith("call:")]:
    a = u.split(":")[1]; rec = collections.Counter(); nb = 0
    for c, tr in DATA.TR.items():
        for x_ in tr:
            if x_[2] and x_[4] == a: rec[x_[3]] += 1; nb += 1
    print(f"   {a}: {nb:,} buys into {len(rec):,} recipients; the top 5 recipients hold {100 * sum(v for _, v in rec.most_common(5)) / max(nb, 1):.0f}% of them: "
          + ", ".join(f"{r[:10]} {v}" for r, v in rec.most_common(5)))
