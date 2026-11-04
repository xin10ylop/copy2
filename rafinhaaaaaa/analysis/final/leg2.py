# rescore2.leg with its reasons exposed, and an optional fallback for the legs it leaves unpriced.
# rescore2.leg prices our fill after the K-th coin trade behind its trade (same pool, its slot then the next 3), on a
# constant-product curve fitted to its trade plus up to K+10 trades behind it; when the fit fails (fewer than 2 trades,
# or worst error >= 3%) it takes the next other trade on our side; none in those 3 slots: "unpriced", and
# rescore2.score drops the whole trip if any leg (its buy or one of its 4 biggest sales) is unpriced.
# leg2(...) returns the same tuple as rescore2.leg plus a reason, and with FALLBACK:
#   - a pool whose reserves are known without a fit (a pump curve quoted in SOL: rescore2.pools adds the 30 SOL /
#     279.9M virtual reserves; a PumpSwap / other constant-product pool with no virtual reserves): we fill on the pool
#     state after the trades behind it that exist (none: right after its own trade), our impact on those reserves
#   - otherwise: the search goes on up to AHEAD2 slots (default 25, about 10 s) for the fit or a trade on our side
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g1lib import R
AHEAD2 = int(os.environ.get("AHEAD2", "25"))
PUMP = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"

def seq_behind(tx, sig, mint, pool, q, ahead, K, skip=()):
    slot, seq, found = tx["slot"], [], False
    for k in range(0, ahead + 1):
        for sg, sigs, p in R.trades_in(slot + k, mint):
            if sig in sigs: found = True; continue
            if k == 0 and not found: continue
            if sg & set(skip): continue
            if p[0] == pool and p[2] == q: seq.append((k, sg, p))
        if k == 0 and not found: return None
        if len(seq) >= K + 10: break
    return seq

def price(own, seq, owner, want, K, X):
    pool, mine, q, dq, dc, side, Q, C = own
    at = seq[min(K, len(seq)) - 1] if K and seq else None
    f = R.fit_curve([own] + [p for _, _, p in seq[:K + 10]])
    if f and f[2] < 0.03:
        A, B, _ = f
        Qs, Cs = (at[2][6], at[2][7]) if at else (Q, C)
        Qs, Cs = Qs + A, Cs + B
        return ("fit", Qs / Cs, at[0] if at else 0, Qs, f)
    hit = next(((k, p) for k, sg, p in seq[max(K - 1, 0):] if owner not in sg and p[5] == want
                and p[3] >= 0.02 * dq and 0.25 < p[1] / mine < 4), None)
    if hit: return ("next trade", hit[1][1], hit[0], None, f)
    return ("unpriced", None, None, None, f)

def leg2(sig, owner, mint, want, x_sol_ratio, K=4, X=None, fallback=False, known=None):
    """known: 'sol curve' / 'cpmm' (reserves known without a fit) or None. Returns (rescore2.leg tuple or 'unpriced' or
    None, reason, trades behind found)."""
    tx = R.tx_of(sig)
    if not tx: return None, "no tx", 0
    ps = R.pools(tx, mint)
    if not ps: return None, "no pool", 0
    own = ps[0]; pool, mine, q, dq, dc, side, Q, C = own
    if X is None: X = dq * x_sol_ratio
    seq = seq_behind(tx, sig, mint, pool, q, R.AHEAD, K)
    if seq is None: return None, "not in its block", 0
    how, base, k_land, Qs, f = price(own, seq, owner, want, K, X)
    reason = f"{how}; {len(seq)} trades behind in 3 slots" + ("" if f else "; no fit") + (f"; fit err {f[2]:.3f}" if f else "")
    if how == "unpriced" and fallback:
        if known in ("sol curve", "cpmm"):
            at = seq[min(K, len(seq)) - 1] if seq else None
            Qs, Cs = (at[2][6], at[2][7]) if at else (Q, C)
            base, k_land, how = Qs / Cs, (at[0] if at else 0), f"fallback known reserves ({known})"
        else:
            seq = seq_behind(tx, sig, mint, pool, q, AHEAD2, K)
            how, base, k_land, Qs, f = price(own, seq or [], owner, want, K, X)
            how = "fallback " + how + f" (to {AHEAD2} slots, {len(seq or [])} trades)"
        reason += " -> " + how
    if base is None: return "unpriced", reason, len(seq)
    imp1 = X / Qs if Qs else 0.0
    ours = base * (1 + imp1) if want == "buy" else base / (1 + imp1)
    return (mine, ours, k_land, base / mine, imp1), reason, len(seq)
