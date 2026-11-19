# Traders with several wallets (Nov 19; the owner: "maybe traders that use several wallets ... include on-chain
# tracking", "do it with what we have now"). From the 4 days' copies (m6_rows: every wallet's first buy of 0.5+ SOL on
# 7,263 coins, our copy valued with wallet 4's live model), wallets are linked when they buy the SAME coins within 1
# slot of each other, after the launch slot+1 (launch snipers all buy at once and are not one trader), on 4+ coins that
# make up half or more of the smaller wallet's coins. Linked wallets = one trader (connected groups, at most 60 wallets).
# Each trader is copied once a coin (its first wallet's buy), and judged like a wallet: by day, and BLIND (chosen on
# days 1-2: up, w/o the best 2% up, 6+ copies; scored on days 3-4).
#   LAUNCHES=<the 3 launch lists> python3 -I m12_clusters.py SP > ../out/m12_clusters.txt
import sys, os, json, gzip, collections, itertools, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import m4_direct as M
R = json.load(gzip.open(f"{M.O}/m6_rows.json.gz")); t0 = min(r[2] for r in R); DAY = 86400; mid = t0 + 2 * DAY
by_coin = collections.defaultdict(list); coins_of = collections.defaultdict(set)
for u, m, t, sol, v, cre, off in R:
    coins_of[u].add(m)
    if off >= 2 and m in M.L: by_coin[m].append((M.L[m]["slot"] + off, u))
pair = collections.Counter()
for m, xs in by_coin.items():
    xs.sort()
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            if xs[j][0] - xs[i][0] > 1: break
            a, b = sorted((xs[i][1], xs[j][1]))
            if a != b: pair[(a, b)] += 1
links = [(a, b, n) for (a, b), n in pair.items() if n >= 4 and n >= 0.5 * min(len(coins_of[a]), len(coins_of[b]))]
parent = {}
def find(x):
    while parent.get(x, x) != x: parent[x] = parent.get(parent[x], parent[x]); x = parent[x]
    return x
for a, b, n in links: ra, rb = find(a), find(b); parent[ra] = rb if ra != rb else rb
groups = collections.defaultdict(set)
for a, b, n in links: groups[find(a)] |= {a, b}
groups = {k: g for k, g in groups.items() if 2 <= len(g) <= 60}
print(f"{len(R)} first buys of {len(coins_of)} wallets; {len(links)} links; {len(groups)} traders of 2-60 wallets "
      f"(sizes: {collections.Counter(min(len(g), 10) for g in groups.values()).most_common()})")
rows = collections.defaultdict(list)
for u, m, t, sol, v, cre, off in R: rows[u].append((t, m, v, cre))
def trader_copies(g):
    first = {}
    for u in g:
        for t, m, v, cre in rows[u]:
            if m not in first or t < first[m][0]: first[m] = (t, m, v, cre)
    return sorted(first.values())
def judge(cp):
    a = np.array([c[2] for c in cp]); k = max(1, round(0.02 * len(a))); d = collections.defaultdict(float)
    for c in cp: d[int((c[0] - t0) // DAY)] += c[2]
    return dict(n=len(a), net=a.sum(), wo=np.sort(a)[:-k].sum(), up=sum(1 for x in d.values() if x > 0), act=len(d), days=d,
                h1=sum(c[2] for c in cp if c[0] < mid), h2=sum(c[2] for c in cp if c[0] >= mid), cre=len({c[3] for c in cp}))
T = [(g, judge(trader_copies(g))) for g in groups.values()]
good = [x for x in T if x[1]["n"] >= 8 and x[1]["net"] > 0 and x[1]["wo"] > 0 and x[1]["h1"] > 0 and x[1]["h2"] > 0]
print(f"\n== traders (2+ linked wallets) whose copy is up on days 1-2 AND days 3-4 AND without the best 2%, 8+ copies: {len(good)} of {len(T)} ==")
print("   wallets  first wallet   copies  net SOL  a copy  w/o 2%   days 1-2 / 3-4   days up  creators   by day")
for g, s in sorted(good, key=lambda x: -x[1]["wo"])[:30]:
    print(f"   {len(g):5d}    {sorted(g)[0][:12]}  {s['n']:5d}  {s['net']:+7.2f}  {100 * s['net'] / s['n'] / 0.5:+5.1f}%  {s['wo']:+6.2f}   {s['h1']:+6.2f} / {s['h2']:+6.2f}    {s['up']}/{s['act']}    {s['cre']:5d}   "
          + " ".join(f"{s['days'][k]:+.2f}" if k in s['days'] else "  -  " for k in range(4)))
pick = []
for g, _ in T:
    cp = trader_copies(g); a = [c for c in cp if c[0] < mid]; b = [c for c in cp if c[0] >= mid]
    if len(a) < 6: continue
    s = judge(a)
    if s["net"] > 0 and s["wo"] > 0: pick.append((g, s, b))
xs = [c[2] for _, _, b in pick for c in b]
print(f"\n== BLIND: traders chosen on days 1-2 (up, up w/o the best 2%, 6+ copies): {len(pick)}; on days 3-4: {len(xs)} copies, {sum(xs):+.2f} SOL "
      f"({100 * np.mean(xs) / 0.5 if xs else 0:+.1f}% a copy); traders up: {sum(1 for *_, b in pick if b and sum(c[2] for c in b) > 0)} of {sum(1 for *_, b in pick if b)}")
for g, s, b in sorted(pick, key=lambda x: -x[1]["wo"])[:20]:
    print(f"   {len(g):3d} wallets {sorted(g)[0][:12]}: days 1-2 {s['n']:3d} copies {s['net']:+6.2f} (w/o 2% {s['wo']:+.2f})  ->  days 3-4 {len(b):3d} copies {sum(c[2] for c in b):+6.2f}")
json.dump([sorted(g) for g in groups.values()], open(f"{M.O}/m12_groups.json", "w"))
