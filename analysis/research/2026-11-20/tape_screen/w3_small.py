# CqCAzte8's buys the cq unit does not copy (Nov 23; the owner: "check we are benefiting from the max"): its first buys
# under 0.5 SOL paid in SOL or our floats, and its buys of 0.5+ SOL paid in given other tokens (QUOTES, mint prefixes),
# against its copied buys (0.5+ in SOL or our floats). Our copy at 1 SOL, the live exits (token coins tp 3x / 420 s /
# stall 240, SOL coins tp 2x / 120 s), refused over 1.5x, by group, in the 2 halves of its history.
#   HELIUS_URL=... RPC_URL=... LK=SP/lk COST=0.0064 QUOTES=4CxjZyMN,98kfF7rm python3 -I w3_small.py SP WALLET
import sys, os, numpy as np
SP, W = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [sys.argv[0], SP, W, "0", "0", "14"]
src = open(os.path.join(HERE, "w2_grid.py")).read().split("firsts.sort(key=lambda c: c[\"t\"]); h = len(firsts) // 2")[0]
exec(src.replace(">= 0.5 and sigs", ">= 0.0 and sigs"))
OURS = ("3NZ9JMVB", "pumpCmXq", "SPCXxcqX", "TTWofwAg", "he1iusmf"); QUOTES = [q for q in os.environ.get("QUOTES", "").split(",") if q]
q_of = {m: (sorted(es, key=lambda e: (e["slot"], not e["buy"]))[0]["quote"] or "") for m, es in by.items()}
def group(c):
    q = q_of[c["m"]]; ours = (not c["tok"]) or q[:8] in OURS
    if ours and c["sol"] >= 0.5: return "copied now (0.5+, SOL or our floats)"
    if ours and c["sol"] >= 0.3: return "0.3-0.5 SOL, SOL or our floats"
    if ours: return "under 0.3 SOL, SOL or our floats"
    if c["sol"] >= 0.5 and q[:8] in QUOTES: return f"0.5+ paid in {q[:8]}"
    return None
def one(c, tr):
    k = next((i for i, e in enumerate(tr) if e["user"] == W and e["buy"] and e["slot"] == c["slot"]), None)
    if k is None: return None
    p = H.prep(tr, k, c["rate"], "slot+1", pmax=1e9)
    if not len(p["px"]): return None
    vt0, vq0, b0 = p["ent"]; prem = (tr[k]["vt"] / vt0) ** 2
    if prem > 1.5: return -0.0004
    Q = STAKE * 1e9 / c["rate"]; net_in = Q * 1e4 / (1e4 + b0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq_r = p["vq"] + net_in; vt_r = p["vt"] * p["vq"] / vq_r
    val = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - p["bps"] / 1e4) * c["rate"] / 1e9 - STAKE - COST
    px, age, n = p["px"], p["age"], len(p["px"]); BIG = 10 ** 9
    trig = lambda i: BIG if i is None else min(i + 1, n - 1); at = lambda i: BIG if i is None else i
    tp, hold, stall = (3.0, 420, 240) if c["tok"] else (2.0, 120, 0)
    pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
    return float(val[min(trig(first(px >= tp)), at(first(age >= hold)), at(first(p["grad"])), n - 1,
                         trig(first((pk >= prem) & (age - lasthi >= stall))) if stall else BIG)])
firsts.sort(key=lambda c: c["t"]); mid = firsts[len(firsts) // 2]["t"]
G = {}
for c in firsts:
    g = group(c)
    if g: G.setdefault(g, []).append(c)
print(f"{W[:8]}: {len(firsts)} first buys; our copy at 1 SOL, the live exits; halves split at {dt.datetime.fromtimestamp(mid, dt.UTC):%m-%d %H:%M} UTC")
def wo2(v):
    k = max(1, round(0.02 * len(v))); return v.sum() - np.sort(v)[-k:].sum()
for g, cs in G.items():
    vals, ts = [], []
    for i in range(0, len(cs), 30):
        b = cs[i:i + 30]
        with cf.ThreadPoolExecutor(3) as ex: paths = list(ex.map(lambda c: M.path(c["m"], c["slot"], next((s for t, s in sigs if t >= c["t"] + 640), sigs[-1][1]), threads=8), b))
        for c, tr in zip(b, paths):
            v = one(c, tr)
            if v is not None: vals.append(v); ts.append(c["t"])
    v = np.array(vals); ts = np.array(ts); a, b_ = v[ts < mid], v[ts >= mid]
    print(f"  {g:40s} {len(v):4d} copies  {100 * v.mean():+6.1f}% a copy ({v.sum():+6.2f} SOL; w/o best 2% {wo2(v):+6.2f})"
          f"   older half {100 * a.mean() if len(a) else float('nan'):+6.1f}% ({len(a)}), newer {100 * b_.mean() if len(b_) else float('nan'):+6.1f}% ({len(b_)})")
