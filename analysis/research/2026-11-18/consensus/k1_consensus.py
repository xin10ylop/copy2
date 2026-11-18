# Consensus of pickers (the owner, Nov 18: "when something fails find another solution, on and on"). Single good pickers
# (8Fux3NDf, Dj216RQs ...) pick graduating coins about 2x better than chance but a copy of one loses. Is a coin several of
# them buy far stronger? Every wallet with a fetched history (SP/winners/hist: the winners-first candidates, the launch
# pickers, the VIP-map crew; wallet 4 and the ladder left out), their first buys on the launches of Nov 15 01:07 - Nov 17
# 01:07 UTC, whose outcome is known for every launch (SP/attn/outcomes.json: no sampling bias). By the number of distinct
# pickers buying within 300 s of the first: coins, graduated share; and the delay to the 2nd/3rd picker.
#   python3 -I k1_consensus.py SP > out/k1_consensus.txt
import sys, os, json, glob, collections
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/attention"); import creates
SP = sys.argv[1]; OUT = json.load(open(f"{SP}/attn/outcomes.json")); CR = {m: v for m, (s, v) in creates.load(SP).items()}
SKIP = {"H9kuqGKN", "4sgdNABj", "AsDCYFPT", "8QzUkGJi", "B4BMZH3T", "HbovEh3L", "64Dn57gX", "H2nsBdjF", "EhS8bGVC", "Gf9gk8sZ", "DHLAr4dH", "91Wu2yN6", "G8hmNBej", "7zvP2xFF"}
buys = collections.defaultdict(list); W = 0
for f in glob.glob(f"{SP}/winners/hist/*.json"):
    w = os.path.basename(f)[:8]
    if w in SKIP: continue
    try: T = json.load(open(f))["trades"]
    except Exception: continue
    W += 1; first = {}
    for e in sorted(T, key=lambda e: e["t"]):
        if e["buy"]: first.setdefault(e["m"], e["t"])
    for m, t in first.items():
        if m in CR and OUT.get(m): buys[m].append((t, w))
rows = []
for m, v in buys.items():
    v.sort(); t0 = v[0][0]; ws = []
    for t, w in v:
        if t - t0 <= 300 and w not in ws: ws.append(w)
    rows.append(dict(m=m, n=len(ws), grad=OUT[m][0], age=t0 - CR[m]["t"], d2=(v[1][0] - t0) if len(v) > 1 else None))
base = sum(v[0] for v in OUT.values() if v) / sum(1 for v in OUT.values() if v)
print(f"{W} pickers with a history; {len(rows)} of the 48 h's launches bought by 1+ of them; base graduation rate {base:.2%}")
for n in sorted({r["n"] for r in rows}):
    X = [r for r in rows if r["n"] == n]; d2 = sorted(r["d2"] for r in X if r["d2"] is not None)
    print(f"   {n} picker(s) within 300 s: {len(X):5d} coins, graduated {sum(r['grad'] for r in X):4d} ({sum(r['grad'] for r in X) / len(X):6.1%}, x{sum(r['grad'] for r in X) / len(X) / base:4.1f}) | 2nd picker {d2[len(d2) // 2] if d2 else '-'} s after the first")
json.dump(rows, open(f"{SP}/consensus_rows.json", "w"))
