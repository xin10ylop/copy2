# The launch pickers on a week of graduations (w6_week.py: the coins graduated Nov 10-17, their first trades and create in
# SP/winners/week_meta.json and paths/): each wallet's first buys in the create slot or the 2 after, 0.25+ SOL, not the
# creator, on graduated coins; held (its first sale after, within the trades read). No control set here: the hit count is a
# screen, the rate comes from each wallet's own history (w4_history.py). Wallet 4 must show among the top.
#   python3 -I w13b_week.py SP > out/w13b_week.txt
import sys, os, json, gzip, collections, statistics as st
SP = sys.argv[1]; W = f"{SP}/winners"; W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
meta = json.load(open(f"{W}/week_meta.json")); sm = json.load(open(f"{W}/sample.json")); meta.update({m: None for m in sm["grad"] if m not in meta})
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/attention"); import creates
CR = creates.load(SP); WSOL = "So11111111111111111111111111111111111111112"
B = collections.defaultdict(list); n = 0
for m, mt in meta.items():
    if mt is None and m in CR: mt = dict(slot=CR[m][1]["slot"], t=CR[m][1]["t"], creator=CR[m][1]["creator"])
    f = f"{W}/paths/{m}.json.gz"
    if mt is None or not os.path.exists(f): continue
    tr = json.load(gzip.open(f)); n += 1; seen = set()
    if not tr: continue
    vq0 = tr[0]["vq"]; solq = 25e9 < tr[0]["vq"] * tr[0]["vt"] / 1.073e15 < 35e9   # a SOL curve; other quotes: sizes not compared
    for i, e in enumerate(tr):
        u = e["user"]
        if e["buy"] and u not in seen and u != mt["creator"] and e["slot"] - mt["slot"] <= 2 and e["slot"] != mt["slot"] - 0 or (e["buy"] and u not in seen and u != mt["creator"] and e["slot"] == mt["slot"] and i > 0):
            if e["slot"] - mt["slot"] <= 2 and (not solq or e["q"] / 1e9 >= 0.25):
                nxt = next((y for y in tr[i + 1:] if y["user"] == u and not y["buy"]), None)
                B[u].append(dict(m=m, cr=mt["creator"], held=(nxt["t"] - e["t"]) if nxt else None, t=e["t"]))
        seen.add(u)
rows = []
for u, v in B.items():
    if len({x["cr"] for x in v}) < 3: continue
    held = [x["held"] for x in v if x["held"] is not None]
    rows.append(dict(u=u, k=len(v), cr=len({x["cr"] for x in v}), days=len({x["t"] // 86400 for x in v}), held=st.median(held) if held else None,
                     f30=sum(1 for h in held if h < 30) / len(v)))
rows.sort(key=lambda r: -r["k"]); w4 = next((i for i, r in enumerate(rows) if r["u"] == W4), None)
print(f"{n} graduated coins read; {len(rows)} wallets with launch buys on 3+ creators' winners; WALLET 4 ranks {None if w4 is None else w4 + 1} by hits")
print("rank wallet   | launch hits, creators, days | held med, sold <30 s")
for i, r in enumerate(rows[:50]):
    print(f"{i + 1:3d} {r['u'][:8]} | {r['k']:4d} {r['cr']:4d} {r['days']:2d} | {'-' if r['held'] is None else f'{r['held']:5.0f} s'} {r['f30']:4.0%}{'  <- WALLET 4' if r['u'] == W4 else ''}")
json.dump(rows, open(f"{W}/w13b_rows.json", "w"))
