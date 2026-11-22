# Our copy of wallet 4's buys of 1.3+ SOL paid in given quote tokens (mint prefixes), at 1 SOL, its live exit and tp 3x / 420 s /
# stall 240 (Nov 23).   HELIUS_URL=... RPC_URL=... LK=SP/lk COST=0.0064 python3 -I quote_replay.py SP WALLET he1iusmf,TTWofwAg
import sys, os, json, collections, numpy as np
SP, W, QPRE = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../2026-11-20/tape_screen")
sys.argv = [os.path.join(HERE, "w2_grid.py"), SP, W, "0", "0", "14"]; __file__ = sys.argv[0]
exec(open(sys.argv[0]).read().split("firsts.sort(key=lambda c: c[\"t\"]); h = len(firsts) // 2")[0])
q_of = {m: sorted(es, key=lambda e: (e["slot"], not e["buy"]))[0]["quote"] or "" for m, es in by.items()}
L = np.ravel_multi_index(LIVE, SH); T3 = np.ravel_multi_index((TP.index(3.0), HOLD.index(420), SPS.index(None), STALL.index(240), 0), SH)
for qp in QPRE:
    cs = sorted([c for c in firsts if q_of[c["m"]].startswith(qp) and c["sol"] >= 1.3], key=lambda c: c["t"])
    rows = fetch(cs)
    v = np.array([r["g"][L] if r["prem"] <= 1.5 else np.nan for r in rows]); v3 = np.array([r["g"][T3] if r["prem"] <= 1.5 else np.nan for r in rows])
    print(f"{qp}: {len(cs)} buys of 1.3+ SOL, {len(rows)} replayed, {int(np.isnan(v).sum())} refused over 1.5x; at 1 SOL a copy, wallet 4's live exit: "
          f"{np.nansum(v):+.2f} SOL ({100 * np.nanmean(v):+.1f}% a copy); tp 3x / 420 s / stall 240: {np.nansum(v3):+.2f}")
    print("   each: " + " ".join(f"{100 * x:+.0f}%" for x in v))
