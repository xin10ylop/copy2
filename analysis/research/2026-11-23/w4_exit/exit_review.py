# Wallet 4's exit review (Nov 23; the owner: "do the exit review now", the frozen exit's review was due Nov 29).
# Its first buys of 1.3+ SOL paid in our floats (what rugsnipe-long copies), its history from Helius (own_only.py's
# cache), each copy at 1 SOL landing at the end of the slot after its buy, refused over 1.5x (max_premium 0.5), COST a
# round trip; the live exit against fixed alternatives (no picking), in 4 time blocks, % a copy, and without the best 2%.
#   RPC_URL=... HELIUS_URL=... LK=SP/lk COST=0.0064 python3 -I exit_review.py SP
import sys, os, collections, numpy as np
SP = sys.argv[1]; W = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
G2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../2026-11-20/tape_screen/w2_grid.py")
sys.argv = [G2, SP, W, "0", "0", "14"]; __file__ = G2
exec(open(G2).read().split("firsts.sort(key=lambda c: c[\"t\"]); h = len(firsts) // 2")[0])
OURS = ("3NZ9JMVB", "pumpCmXq", "SPCXxcqX", "TTWofwAg", "he1iusmf", "98kfF7rm")
q_of = {m: (sorted(es, key=lambda e: (e["slot"], not e["buy"]))[0]["quote"] or "") for m, es in by.items()}
cs = sorted([c for c in firsts if c["tok"] and c["sol"] >= 1.3 and q_of[c["m"]][:8] in OURS], key=lambda c: c["t"])
EXITS = {"LIVE: tp 4, 600 s, sp 5/60, stall 180, its sale 30-290 s": (4.0, 600, (5, 60), 180, 2),
         "live without sell pressure": (4.0, 600, None, 180, 2), "live without its sale": (4.0, 600, (5, 60), 180, 0),
         "live, sp 8/60": (4.0, 600, (8, 60), 180, 2), "live, sp 10/60": (4.0, 600, (10, 60), 180, 2),
         "tp 3x / 420 s / stall 240 (the other units')": (3.0, 420, None, 240, 0),
         "tp 3x / 420 s / stall 240 + its sale 30-290": (3.0, 420, None, 240, 2),
         "held 300 s": (None, 300, None, 0, 0), "tp 2x / 120 s": (2.0, 120, None, 0, 0), "its sale (to 600 s)": (None, 600, None, 0, 1),
         "tp 4 / 600 s / stall 180, no sale, no sp": (4.0, 600, None, 180, 0)}
IDX = [np.ravel_multi_index((TP.index(tp), HOLD.index(h_), SPS.index(sp), STALL.index(st), it), SH) for tp, h_, sp, st, it in EXITS.values()]
rows = []
for i in range(0, len(cs), 30):
    for r_ in fetch(cs[i:i + 30]): r_["g"] = r_["g"][IDX]; rows.append(r_)
rows.sort(key=lambda r_: r_["t"])
V = np.stack([np.where(r_["prem"] > 1.5, -0.0004, r_["g"]) for r_ in rows]); bl = np.array_split(np.arange(len(rows)), 4)
t = [r_["t"] for r_ in rows]
print(f"wallet 4: {len(rows)} copies of its {len(cs)} first buys of 1.3+ SOL paid in our floats "
      f"({dt.datetime.fromtimestamp(t[0], dt.UTC):%m-%d %H:%M} to {dt.datetime.fromtimestamp(t[-1], dt.UTC):%m-%d %H:%M} UTC), "
      f"{sum(r_['prem'] > 1.5 for r_ in rows)} refused over 1.5x; % a copy at 1 SOL, COST {COST}")
print("blocks: " + " | ".join(f"{dt.datetime.fromtimestamp(t[b[0]], dt.UTC):%m-%d %H:%M}-{dt.datetime.fromtimestamp(t[b[-1]], dt.UTC):%m-%d %H:%M}" for b in bl))
def wo2(v): k = max(1, round(0.02 * len(v))); return v.sum() - np.sort(v)[-k:].sum()
for j, n in enumerate(EXITS):
    v = V[:, j]; per = [V[b, j].mean() for b in bl]
    print(f"  {n:52s} " + " / ".join(f"{100 * p:+6.1f}" for p in per) + f" = {100 * v.mean():+6.1f}% ({len(v)})  {v.sum():+7.2f} SOL  w/o 2% {wo2(v):+7.2f}  +blocks {sum(p > 0 for p in per)}/4")
