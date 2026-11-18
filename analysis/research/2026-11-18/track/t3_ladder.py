# The ladder operation (t2: groups of wallets buying the same launches at fixed sizes 1.1 / 1.54 / 2.18 SOL, 94% of their
# coins graduated, a new group every day or two). Every coin on disk whose launch window (create slot to +2) has buys of at
# least two of the ladder sizes from different wallets: when, its creator, graduated or not, the ladder's slots against
# the create, and the price after the ladder (what a follower pays). The detection a bot could run at the create.
#   python3 -I t3_ladder.py SP > out/t3_ladder.txt   -> SP/track/ladder_coins.json
import sys, os, json, gzip, glob, collections, datetime as d
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/attention"); import creates
SP = sys.argv[1]; SIZES = (1.10, 1.54, 2.18); os.makedirs(f"{SP}/track", exist_ok=True)
CR = {m: v for m, (s, v) in creates.load(SP).items()}; meta = {m: v for m, v in json.load(open(f"{SP}/winners/week_meta_nov10_17.json")).items() if v}
info = {m: (v["slot"], v["creator"], v["t"]) for m, v in CR.items()}; info.update({m: (v["slot"], v["creator"], v["t"]) for m, v in meta.items()})
OUT = json.load(open(f"{SP}/attn/outcomes.json")); grad = set(meta) | set(json.load(open(f"{SP}/winners/sample.json"))["grad"]) | {m for m, v in OUT.items() if v and v[0]}
L = []
for f in glob.glob(f"{SP}/winners/paths/*.json.gz") + glob.glob(f"{SP}/market/paths/*.json.gz"):
    m = os.path.basename(f)[:-8]
    if m not in info: continue
    try: tr = json.load(gzip.open(f))
    except Exception: continue
    if not tr or not (25e9 < tr[0]["vq"] * tr[0]["vt"] / 1.073e15 < 35e9): continue
    s0, creator, t0 = info[m]; lad = []
    for i, e in enumerate(tr):
        if e["slot"] - s0 > 2: break
        if e["buy"] and any(abs(e["q"] / 1e9 - s) <= 0.005 for s in SIZES): lad.append((i, e))
    if len({e["user"] for _, e in lad}) < 2: continue
    last = max(i for i, _ in lad); px = lambda e: e["vq"] / e["vt"]
    p_lad = px(tr[last]); nxt = tr[last + 1] if last + 1 < len(tr) else None
    L.append(dict(m=m, t=t0, creator=creator, grad=m in grad, wallets=sorted({e["user"] for _, e in lad}), sizes=sorted(round(e["q"] / 1e9, 2) for _, e in lad),
                  slots=sorted({e["slot"] - s0 for _, e in lad}), first_px=px(tr[0]), lad_px=p_lad, next_px=px(nxt) if nxt else None, n_after=len(tr) - last - 1))
json.dump(L, open(f"{SP}/track/ladder_coins.json", "w"))
f = lambda t: d.datetime.fromtimestamp(t, d.UTC).strftime("%m-%d %H:%M")
print(f"ladder coins on disk: {len(L)}; graduated {sum(c['grad'] for c in L)}; {f(min(c['t'] for c in L))} to {f(max(c['t'] for c in L))}")
print("creators:", len({c['creator'] for c in L}), "distinct;", collections.Counter(c["creator"][:8] for c in L).most_common(5))
print("ladder wallets per coin:", collections.Counter(len(c["wallets"]) for c in L).most_common(6))
print("ladder slots after the create:", collections.Counter(tuple(c["slots"]) for c in L).most_common(5))
print("price at the end of the ladder / at the first trade: median", sorted(c["lad_px"] / c["first_px"] for c in L)[len(L) // 2])
print("per day:", sorted(collections.Counter(f(c["t"])[:5] for c in L).items()))
