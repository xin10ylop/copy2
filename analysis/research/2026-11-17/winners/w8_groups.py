# Groups on the chain (the owner, Nov 17: "find good groups ... not thousands of people"): a call group leaves a
# footprint, the same wallets buying the same coins within seconds of each other, coin after coin. From every path
# fetched (steps 2 and 6: the graduated coins of 7 days and the 48 h control sample), each wallet's first buy on a coin
# (0.1+ SOL, SOL curves only, not the creator, 2+ slots after the create: the launch-slot bundles are not a group).
# Pairs of wallets (each 5+ coins) buying the same coin within LAG slots of each other; a pair is tied when it does on 5+
# coins and on 30%+ of the coins of the less active one. Groups = connected tied wallets. For each group: its size, its
# coins, the wallet first in the group on most of them (the leader: the one to copy, earlier than any message), and on the
# 48 h sample (where the losers are sampled too) how often the coins the group bought graduated against the base rate.
#   python3 -I w8_groups.py SP [LAG=10] > out/w8_groups.txt
import sys, os, json, gzip, collections, itertools, statistics as st
SP = sys.argv[1]; LAG = int(sys.argv[2]) if len(sys.argv) > 2 else 10; W = f"{SP}/winners"
WSOL = "So11111111111111111111111111111111111111112"; SOLQ = {WSOL, "11111111111111111111111111111111", None, "?"}
meta = {}
for v in json.load(open(f"{SP}/market/creates.json")).values():
    if v and v.get("mint"): meta[v["mint"]] = dict(slot=v["slot"], creator=v.get("creator"), sol=v.get("quote") in SOLQ)
for m, v in json.load(open(f"{W}/week_meta.json")).items():
    if v and m not in meta: meta[m] = dict(slot=v["slot"], creator=v["creator"], sol=None)
sm = json.load(open(f"{W}/sample.json")); G48 = set(sm["grad"]); C48 = set(sm["ctrl"]); WCTRL = sm["n_rest"] / len(sm["ctrl"])
grad = G48 | {m for m, _ in json.load(open(f"{W}/week_migrations.json"))}
coins = {}
for f in os.listdir(f"{W}/paths"):
    m = f[:-8]
    if m not in meta: continue
    tr = json.load(gzip.open(f"{W}/paths/{f}"))
    if not tr: continue
    mt = meta[m]; sol = mt["sol"] if mt["sol"] is not None else 25e9 < tr[0]["vq"] * tr[0]["vt"] / 1.073e15 < 35e9
    if not sol: continue
    seen = set(); fb = []
    for e in tr:
        u = e["user"]
        if e["buy"] and u not in seen and u != mt["creator"] and e["slot"] - mt["slot"] >= 2 and e["q"] * (1 + e["bps"] / 1e4) >= 1e8:
            fb.append((e["slot"], u))
        seen.add(u)
    coins[m] = fb
act = collections.Counter(u for fb in coins.values() for _, u in fb)
keep = {u for u, c in act.items() if c >= 5}
pair = collections.Counter(); first = collections.Counter()
for m, fb in coins.items():
    fb = [(s, u) for s, u in fb if u in keep]
    for i, (s1, a) in enumerate(fb):
        for s2, b in fb[i + 1:]:
            if s2 - s1 > LAG: break
            if a == b: continue
            k = (a, b) if a < b else (b, a); pair[k] += 1
            if s1 < s2: first[(a, b)] += 1
tied = {k: c for k, c in pair.items() if c >= 5 and c >= 0.3 * min(act[k[0]], act[k[1]])}
adj = collections.defaultdict(set)
for a, b in tied: adj[a].add(b); adj[b].add(a)
groups, done = [], set()
for u in adj:
    if u in done: continue
    comp, stack = set(), [u]
    while stack:
        x = stack.pop()
        if x in comp: continue
        comp.add(x); stack += list(adj[x] - comp)
    done |= comp; groups.append(comp)
print(f"{len(coins)} SOL coins read; {len(keep)} wallets with 5+ first buys; {len(tied)} tied pairs (5+ coins within {LAG} slots); {len(groups)} groups")
print("size | coins with 3+ members | leader (first on most) and its share | 48 h sample: group coins, graduated, est. rate | members' median buys")
rows = []
for g in groups:
    gc = [m for m, fb in coins.items() if len({u for _, u in fb} & g) >= min(3, len(g))]
    if len(gc) < 5: continue
    lead = collections.Counter(next(u for _, u in coins[m] if u in g) for m in gc)
    l, ln = lead.most_common(1)[0]
    g48 = [m for m in gc if m in G48]; c48 = [m for m in gc if m in C48]
    est = len(g48) / (len(g48) + WCTRL * len(c48)) if (g48 or c48) else None
    rows.append((len(gc), len(g), l, ln / len(gc), len(g48) + len(c48), len(g48), est, st.median(act[u] for u in g)))
for n, sz, l, sh, n48, g48, est, med in sorted(rows, key=lambda r: -r[0])[:40]:
    print(f"{sz:4d} | {n:5d} | {l[:8]} {sh:4.0%} | {n48:4d}, {g48:3d}, {('%.1f%%' % (100 * est)) if est is not None else '-':>6s} | {med:.0f}")
json.dump([dict(n=r[0], size=r[1], leader=r[2], share=r[3], est=r[6]) for r in rows], open(f"{W}/w8_groups.json", "w"))
