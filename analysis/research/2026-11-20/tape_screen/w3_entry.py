# Where does a wallet's edge go? (Nov 23; the owner on 965Nk2u3 and HCq8h5ad, up every day themselves while our copies
# lose: "check if there's a totally different way to profit, a smart way"). For each first buy of 0.5+ SOL (the coins'
# trades cached by w3_robust.py), our copy at 1 SOL entered (a) right behind its buy (the next trade, its own slot: the
# best a copier could ever do) and (b) as the bot lands (the end of the slot after its buy); the price we pay over its
# own (premium); who bought the same coin in its slot just before it (a leader it follows?); and how far into the curve
# its buy is (SOL in the curve: 30 = the launch).
#   RPC_URL=... LK=SP/lk COST=0.0064 python3 -I w3_entry.py SP WALLET [MAXN=400]
import sys, os, random, collections, numpy as np
SP, W = sys.argv[1], sys.argv[2]; MAXN = int(sys.argv[3]) if len(sys.argv) > 3 else 400
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [sys.argv[0], SP, W, "0", "0", "14"]
src = open(os.path.join(HERE, "w2_grid.py")).read().split("firsts.sort(key=lambda c: c[\"t\"]); h = len(firsts) // 2")[0]
exec(src.replace('H.prep(tr, k, c["rate"], "slot+1", pmax=1e9)', 'H.prep(tr, k, c["rate"], ENTRY[0], pmax=1e9)'))
ENTRY = ["slot+1"]
EX = {"tp 3x / 420 s / stall 240": (3.0, 420, None, 240, 0), "held 300 s": (None, 300, None, 0, 0), "tp 2x / 120 s": (2.0, 120, None, 0, 0),
      "its sale (to 600 s)": (None, 600, None, 0, 1), "tp 1.5x / 60 s": (1.5, 60, None, 0, 0)}
IDX = [np.ravel_multi_index((TP.index(tp), HOLD.index(h_), SPS.index(sp), STALL.index(st), it), SH) for tp, h_, sp, st, it in EX.values()]
firsts.sort(key=lambda c: c["t"])
if len(firsts) > MAXN: random.seed(7); firsts = sorted(random.sample(firsts, MAXN), key=lambda c: c["t"])
anchor = lambda c: next((s for t, s in sigs if t >= c["t"] + 640), sigs[-1][1])
res = {"behind": [], "lands": []}; prem = []; lead = collections.Counter(); nslot = []; curve = []
for i in range(0, len(firsts), 30):
    cs = firsts[i:i + 30]
    with cf.ThreadPoolExecutor(3) as ex: paths = list(ex.map(lambda c: M.path(c["m"], c["slot"], anchor(c), threads=8), cs))
    for c, tr in zip(cs, paths):
        for name, e in (("behind", 1), ("lands", "slot+1")):
            ENTRY[0] = e; g = grid(c, tr)
            if g: res[name].append(g["g"][IDX])
            if g and name == "lands": prem.append(g["prem"])
        k = next((j for j, e in enumerate(tr) if e["user"] == W and e["buy"] and e["slot"] == c["slot"]), None)
        if k is None: continue
        before = [e["user"] for e in tr[:k] if e["slot"] == c["slot"] and e["buy"] and e["user"] != W]
        nslot.append(len(before)); lead.update(set(before))
        if not c["tok"]: curve.append(tr[k]["vq"] / 1e9)
print(f"{W[:8]}: {len(res['lands'])} copies of its first buys of 0.5+ SOL; % a copy at 1 SOL (COST {COST})")
print(f"  {'exit':28s} {'right behind it (its slot)':>28s} {'as the bot lands (slot+1)':>28s}")
for j, n in enumerate(EX):
    a = np.array([r[j] for r in res["behind"]]); b = np.array([r[j] for r in res["lands"]])
    print(f"  {n:28s} {100 * a.mean():+26.1f}% {100 * b.mean():+26.1f}%")
p = np.array(prem)
print(f"  the price we pay over its own, as the bot lands: median {np.median(p):.2f}x, 75% {np.percentile(p, 75):.2f}x, over 1.2x on {np.mean(p > 1.2):.0%}")
print(f"  other buyers in its slot before it: median {np.median(nslot):.0f}; none on {np.mean(np.array(nslot) == 0):.0%}")
print(f"  wallets most often in its slot before it (of {len(nslot)} coins): " + ", ".join(f"{u[:8]} {n}" for u, n in lead.most_common(5)))
if curve: print(f"  SOL in the curve at its buy (SOL coins, 30 = launch): median {np.median(curve):.1f}, 10-90%: {np.percentile(curve, 10):.1f}-{np.percentile(curve, 90):.1f}")
