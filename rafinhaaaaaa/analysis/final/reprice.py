# Re-price a wallet's trips at our live speed (rescore2's model, K=4) and price the legs rescore2 leaves unpriced.
# rescore2.leg needs at least one other trade on the same pool within 3 slots behind its trade (for the curve fit or
# the next trade on our side); with none it returns "unpriced" and the whole trip is dropped. But with nobody behind
# it, our copy (landing in its slot or the next block's top) fills right after its own trade. So here, when a leg is
# unpriced and the pool's reserves are known without a fit, we fill on the pool after the trades behind it that exist
# (none: right after its own), our impact on those reserves:
#   pump curve quoted in SOL: virtual SOL = lamports + 30 (as rescore2), virtual coin = the curve's coin account + 73M
#     (1,073M virtual at the start against 1,000M in the account; rescore2.pools adds 279.9M, which its curve fit then
#     corrects, so rescore2's priced legs are not affected)
#   pump curve quoted in a token: virtual coin = account + 73M, virtual quote = account + A, A solved from its own trade
#   anything else (PumpSwap, Raydium, CLMM, DLMM ...): the search goes on to 25 slots (about 10 s) for a fit or a
#     trade on our side (PumpSwap's real reserves were tried and failed the check below: 0.60-0.88 against the fit's 1.03-1.12)
# Entry and sales at K = 4 trades behind (the live median), and at K = 1 and K = 7 (the live range) as a check:
# s2 (K=4, rescore2's exactly when it priced the trip), s2k1, s2k7.
# Priced legs keep rescore2's result exactly (same code path, K=4). For a validation sample of fitted buy legs the
# known-reserves price is computed too (kr_check), to test the reserves above against the fit.
#   python3 -I reprice.py IN_JSON OUT_JSON [VALIDATE_N]
import sys, os, json, time, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g1lib import *
from leg2 import seq_behind, price
from concurrent.futures import ThreadPoolExecutor
IN, OUTF = (sys.argv[1], sys.argv[2]) if __name__ == "__main__" else (None, None); VAL = int(sys.argv[3]) if len(sys.argv) > 3 and __name__ == "__main__" else 12
K = 4; PUMP = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
CPMM = {"pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA", "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8", "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C"}
OWN, lk = {}, threading.Lock()
def owner_of(acct):
    if acct not in OWN:
        a = R.rpc("getAccountInfo", [acct, {"encoding": "base64", "dataSlice": {"offset": 0, "length": 0}}])
        OWN[acct] = ((a or {}).get("value") or {}).get("owner")
    return OWN[acct]

def kind_of(own):
    pool, q = own[0], own[2]
    o = owner_of(pool)
    if o == PUMP: return "sol curve" if q == WSOL and own[6] > 29.99 else "token curve"
    if o in CPMM: return "cpmm"
    return "other:" + (o or "?")[:8]

def known_state(kind, own, state):
    """(Q, C) virtual of the pool at `state` (a pools() tuple after some trade), or None."""
    pool, mine, q, dq, dc, side, Q, C = own
    Qs, Cs = state[6], state[7]
    if kind == "sol curve": return Qs, Cs - R.VTOK + 73e6
    if kind == "token curve":
        Cav = C + 73e6; Cbv = Cav + dc if side == "buy" else Cav - dc
        Qa = Q; Qb = Q - dq if side == "buy" else Q + dq
        if abs(Cav - Cbv) <= 0: return None
        A = (Qb * Cbv - Qa * Cav) / (Cav - Cbv)
        if A <= 0: return None
        return Qs + A, Cs + 73e6
    return None

def leg3(sig, owner, mint, want, x_sol_ratio, validate=False, K=4):
    tx = R.tx_of(sig)
    if not tx: return None, "no tx"
    ps = R.pools(tx, mint)
    if not ps: return None, "no pool"
    own = ps[0]; pool, mine, q, dq, dc, side, Q, C = own
    X = dq * x_sol_ratio
    seq = SEQ.get((sig, K))
    if seq is None:
        seq = seq_behind(tx, sig, mint, pool, q, R.AHEAD, K); SEQ[(sig, K)] = seq
    if seq is None: return None, "not in its block"
    how, base, k_land, Qs, f = price(own, seq, owner, want, K, X)
    why = f"{how}; {len(seq)} behind"
    kr = None
    if how == "unpriced" or (validate and how == "fit"):
        kind = kind_of(own)
        at = seq[min(K, len(seq)) - 1] if seq else None
        st = known_state(kind, own, at[2] if at else own)
        if st:
            kr = (st[0] / st[1], at[0] if at else 0, st[0], kind)
        if how == "unpriced":
            if kr: base, k_land, Qs = kr[0], kr[1], kr[2]; why += f"; fallback {kind}"
            else:
                seq2 = seq_behind(tx, sig, mint, pool, q, 25, K) or []
                how2, base, k_land, Qs, f = price(own, seq2, owner, want, K, X)
                why += f"; fallback {kind} 25 slots: {how2}, {len(seq2)} behind"
    if base is None: return "unpriced", why
    imp1 = X / Qs if Qs else 0.0
    ours = base * (1 + imp1) if want == "buy" else base / (1 + imp1)
    res = (mine, ours, k_land, base / mine, imp1)
    if kr and how == "fit": why += f"; kr_check base {kr[0] / mine:.4f} vs fit {base / mine:.4f} ({kr[3]})"
    return res, why

SEQ = {}
def score(w, t, validate, K=4):
    usd0 = t.get("usd0") or t["usd_in"]; ratio = (R.SOLUSD / usd0) if usd0 > 0 else 1.0
    e, why0 = leg3(t["sig0"], w, t["mint"], "buy", ratio, validate, K)
    if not e or e == "unpriced": return None, [why0]
    r_in = e[1] / e[0]; legs, whys, gross = [], [why0], 0.0
    sells = sorted(t["sells"], key=lambda s: -s["frac"])
    for s in sells[:R.MAX_SELLS]:
        x, why = leg3(s["sig"], w, t["mint"], "sell", ratio, False, K); whys.append(why)
        if x == "unpriced": return None, whys
        r_out = x[1] / x[0] if x else 0.9
        legs.append((s["frac"], s["px"], x[3] if x else 0.9, x[4] if x else e[4]))
        gross += s["frac"] * (s["px"] * r_out) / (t["px0"] * r_in)
    for s in sells[R.MAX_SELLS:]: gross += s["frac"] * s["px"] * 0.97 / (t["px0"] * r_in)
    ntx = 1 + min(len(t["sells"]), 3)
    return dict(copy=gross - 1 - 0.0095 * ntx - 0.0125 * (1 + max(gross, 0)), entry_ratio=r_in, entry_slot=e[2],
                entry_base=e[3], entry_imp1=e[4], legs=legs,
                its_pct=(t["usd_out"] - t["usd_in"]) / t["usd_in"] if t["usd_in"] else 0.0), whys

if __name__ == "__main__":
    d = jl(IN); w = d["wallet"]
    prev = jl(OUTF) if os.path.exists(OUTF) else None
    done = {t["sig0"]: t for t in (prev or {}).get("trips", []) if "s2_how" in t}
    nval = [0]
    def one(t):
        if t["sig0"] in done: return done[t["sig0"]]
        t = dict(t)
        has = "s2" in t and t.get("s2") is not None and "entry_base" in (t.get("s2") or {})
        with lk:
            v = has and nval[0] < VAL
            if v: nval[0] += 1
        try:
            r, whys = (None, []) if (has and not v) else score(w, t, v)
            t["s2k1"] = score(w, t, False, 1)[0]; t["s2k7"] = score(w, t, False, 7)[0]
        except Exception as ex: r, whys = None, ["error " + str(ex)[:120]]
        for k in [k for k in SEQ if k[0] == t["sig0"] or k[0] in {x["sig"] for x in t["sells"]}]: SEQ.pop(k, None)
        if has and not v: t["s2_how"] = "rescore2"; return t
        if has: t["s2_how"] = "rescore2"; t["val"] = dict(mine=r, whys=whys)
        else: t["s2"] = r; t["s2_how"] = "fallback" if r else "unpriced"; t["whys"] = whys
        R.TXC.pop(t["sig0"], None)
        return t
    with ThreadPoolExecutor(3) as ex: trips = list(ex.map(one, d["trips"]))
    d = dict(d); d["trips"] = trips
    json.dump(d, open(OUTF, "w"))
    c = {}
    for t in trips: c[t["s2_how"]] = c.get(t["s2_how"], 0) + 1
    ok = [t for t in trips if t.get("s2")]
    print(time.strftime("%H:%M:%S"), w[:8], c, "copy at 1 SOL %+.2f on %d priced (rescore2's own %+.2f on %d)" % (
        sum(t["s2"]["copy"] for t in ok), len(ok), sum(t["s2"]["copy"] for t in ok if t["s2_how"] == "rescore2"),
        sum(1 for t in ok if t["s2_how"] == "rescore2")), flush=True)
