# The ladder operation as ONE candidate (the owner, Nov 18: "trade the group as one candidate"): the copies of every ladder
# wallet studied (wallet_study.py, any refusal limit given by the suffix), one per coin (all ladder wallets buy in the
# create slot, so our copy, one slot later, is the same trade whichever wallet signals it), only buys after the screen
# (Nov 17 01:07 UTC). Every exit, picked on the first half by time and scored on the second; the fair measures (the best 2%
# out, a bootstrap) on the second half. At 0.0345 SOL a round trip.
#   python3 -I t4_pool.py SP W8:SUFFIX ... > out/t4_pool.txt
import sys, json, os, numpy as np
SP = sys.argv[1]; S0 = int(os.environ.get("S0", 1794877620)); coins = {}   # S0: the cutoff (Nov 17 13:49 UTC = 1794923340, the end of the week screen that picked groups C-F)
for arg in sys.argv[2:]:
    w, suf = arg.split(":"); f = f"{SP}/winners/study_{w}{suf}.json"
    if not os.path.exists(f): print(f"   (no study for {w}{suf})"); continue
    for r in json.load(open(f)):
        if not r["refused"] and r["t"] >= S0 and r["m"] not in coins: r["w"] = w; coins[r["m"]] = r
R = sorted(coins.values(), key=lambda r: r["t"]); h = len(R) // 2; A, B = R[:h], R[h:]
def S(v):
    v = np.array(v); s = np.sort(v); k = max(1, round(0.02 * len(v))) if len(v) else 0
    return f"{len(v):3d} {v.sum():+6.2f} ({100 * v.mean() / 0.5 if len(v) else 0:+6.1f}%) w/o best 2% {s[:-k].sum() if len(v) > 1 else 0:+6.2f}"
print(f"the ladder pooled: {len(R)} coins after the screen (1st half {len(A)}, 2nd half {len(B)}), 0.0345 SOL a round trip")
for e in R[0]["ex"]: print(f"   {e:13s}: 1st {S([r['ex'][e] - 0.0319 for r in A])} | 2nd {S([r['ex'][e] - 0.0319 for r in B])}")
best = max(R[0]["ex"], key=lambda e: sum(r["ex"][e] for r in A)); v = np.array([r["ex"][best] - 0.0319 for r in B])
bs = np.random.default_rng(7).choice(v, size=(10000, len(v))).mean(axis=1) if len(v) else np.array([0])
print(f"PICKED on the 1st half: {best} -> 2nd half {S(list(v))}; P(mean > 0) {np.mean(bs > 0):.1%}; 5th pct {100 * np.percentile(bs, 5) / 0.5:+.1f}% a copy")

import collections, datetime as dt
print("\nby wallet (group) and day, the picked exit:")
G = collections.defaultdict(list)
for r in R: G[(r["w"], dt.datetime.fromtimestamp(r["t"], dt.UTC).strftime("%m-%d"))].append(r["ex"][best] - 0.0319)
for k in sorted(G): print(f"   {k[0]} {k[1]}: {S(G[k])}")
