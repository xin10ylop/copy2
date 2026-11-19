# rhd4's groups as a file for rhd2_engineer.py (grp:NAME, NAME = the first member's address, 10 characters).
#   python3 -I rhd5_dump_groups.py SCREEN_DIR > SCREEN_DIR/groups.json    (NULLMAX=0.05; the same linking as rhd4)
import sys, os, json, collections
SD = sys.argv[1]; NULLMAX = float(os.environ.get("NULLMAX", 0.05)); S = json.load(open(f"{SD}/screen.json"))
good = {u: r for u, r in S["res"].items() if r["passed"] and r["null"] <= NULLMAX}; coins = {u: {k.split(":")[0] for k in S["cand"][u]} for u in good}
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
print(json.dumps({sorted(m, key=lambda u: -good[u]["p3"])[0].split(":")[1][:10]: sorted(m, key=lambda u: -good[u]["p3"]) for m in G.values() if len(m) > 1 and all(x.startswith("rec:") for x in m)}, indent=0))
