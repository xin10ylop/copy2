# One operator, many wallets? 8QzUkGJi and AsDCYFPT both buy a fixed 1.1 SOL and share no coin (117 and 257 coins);
# 4sgdNABj buys a fixed 1.54, B4BMZH3T 2.18. Every launch-window buy (create slot to +2) on the SOL-priced coins with
# trades on disk (the week's graduations, the 48 h sample and market coins): the wallets whose buys sit at one of these
# sizes (within 0.005 SOL), how many coins each, when, how much they overlap, and their graduation share.
#   python3 -I t2_sizes.py SP > out/t2_sizes.txt
import sys, os, json, gzip, glob, collections, datetime as d
sys.path.insert(0, "/home/user/copy2/analysis/research/2026-11-17/attention"); import creates
SP = sys.argv[1]; SIZES = (1.10, 1.54, 2.18, 2.21)
CR = {m: v for m, (s, v) in creates.load(SP).items()}; meta = {m: v for m, v in json.load(open(f"{SP}/winners/week_meta_nov10_17.json")).items() if v}
slot0 = {m: v["slot"] for m, v in CR.items()}; slot0.update({m: v["slot"] for m, v in meta.items()})
grad = set(meta) | set(json.load(open(f"{SP}/winners/sample.json"))["grad"])
B = collections.defaultdict(list)
for f in glob.glob(f"{SP}/winners/paths/*.json.gz") + glob.glob(f"{SP}/market/paths/*.json.gz"):
    m = os.path.basename(f)[:-8]
    if m not in slot0: continue
    try: tr = json.load(gzip.open(f))
    except Exception: continue
    if not tr or not (25e9 < tr[0]["vq"] * tr[0]["vt"] / 1.073e15 < 35e9): continue   # SOL curves only (sizes in SOL)
    for e in tr:
        if e["slot"] - slot0[m] > 2: break
        if e["buy"]:
            sol = e["q"] * (1 + e["bps"] / 1e4) / 1e9
            for s in SIZES:
                if abs(e["q"] / 1e9 - s) <= 0.005 or abs(sol - s) <= 0.005: B[(s, e["user"])].append((e["t"], m))
f = lambda t: d.datetime.fromtimestamp(t, d.UTC).strftime("%m-%d %H:%M")
for s in SIZES:
    W = {u: v for (ss, u), v in B.items() if ss == s and len(v) >= 3}
    print(f"\n== size {s} SOL: {len(W)} wallets with 3+ launch buys of it")
    for u, v in sorted(W.items(), key=lambda x: -len(x[1]))[:15]:
        ms = {m for _, m in v}; print(f"   {u[:8]} | {len(v):4d} buys, {len(ms):4d} coins, graduated {len(ms & grad):3d} | {f(min(t for t, _ in v))} to {f(max(t for t, _ in v))}")
    us = list(W); 
    for i in range(min(8, len(us))):
        for j in range(i + 1, min(8, len(us))):
            a = {m for _, m in W[us[i]]}; b = {m for _, m in W[us[j]]}
            if a & b: print(f"      overlap {us[i][:8]} x {us[j][:8]}: {len(a & b)} coins")
