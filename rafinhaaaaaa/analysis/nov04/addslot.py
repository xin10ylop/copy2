# Adds s2s{n} to every trip of an s3q2 file: our buy and our sales landing n slots after its trade, at the end of that
# slot (after every trade on the pool in its slot and the next n), the pessimistic end of "we land in slot +n". n = 0
# is the end of its own slot. The copier asks Jupiter for a quote and a swap over HTTP before it sends, so it lands
# later than the long copy (47% in its slot, 53% the next). Same pricing and costs as reprice.score; only the landing
# point changes from "K trades behind" to "n slots behind".
#   python3 -I addslot.py S3Q2_JSON [N_MAX] [ONLY_MIN_SOL]
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reprice as RP
from reprice import R, seq_behind, price, kind_of, known_state
from concurrent.futures import ThreadPoolExecutor
fn = sys.argv[1]; NMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 3
ONLY = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
R.AHEAD = NMAX + 1; KBIG = 60; SEQ = {}
def leg_slot(sig, owner, mint, want, x_sol_ratio, n):
    tx = R.tx_of(sig)
    if not tx: return None, "no tx"
    ps = R.pools(tx, mint)
    if not ps: return None, "no pool"
    own = ps[0]; pool, mine, q, dq, dc, side, Q, C = own
    X = dq * x_sol_ratio
    if sig not in SEQ: SEQ[sig] = seq_behind(tx, sig, mint, pool, q, R.AHEAD, KBIG)
    seq = SEQ[sig]
    if seq is None: return None, "not in its block"
    K = sum(1 for k, _, _ in seq if k <= n)
    how, base, k_land, Qs, f = price(own, seq, owner, want, K, X)
    why = f"{how}; {K} behind by slot +{n}"
    if how == "unpriced":
        at = seq[K - 1] if K else None
        st = known_state(kind_of(own), own, at[2] if at else own)
        if st: base, k_land, Qs = st[0] / st[1], (at[0] if at else 0), st[0]; why += "; fallback known reserves"
        elif at:
            # a local fit around our landing point (a curve with segments, Meteora DBC: one fit over the whole
            # sequence fails), from the same pool's trades just before and after it
            win = [p for _, _, p in seq[max(0, K - 6):K + 6]]
            f2 = R.fit_curve(win)
            if f2 and f2[2] < 0.05:
                Qa, Ca = at[2][6] + f2[0], at[2][7] + f2[1]
                base, k_land, Qs = Qa / Ca, at[0], Qa; why += f"; local fit err {f2[2]:.3f}"
    if base is None: return "unpriced", why
    imp1 = X / Qs if Qs else 0.0
    ours = base * (1 + imp1) if want == "buy" else base / (1 + imp1)
    return (mine, ours, k_land, base / mine, imp1, K), why
def score(w, t, n):
    usd0 = t.get("usd0") or t["usd_in"]; ratio = (R.SOLUSD / usd0) if usd0 > 0 else 1.0
    e, why0 = leg_slot(t["sig0"], w, t["mint"], "buy", ratio, n)
    if not e or e == "unpriced": return None
    r_in = e[1] / e[0]; legs, gross = [], 0.0
    sells = sorted(t["sells"], key=lambda s: -s["frac"])
    ks = [e[5]]
    for s in sells[:R.MAX_SELLS]:
        x, why = leg_slot(s["sig"], w, t["mint"], "sell", ratio, n)
        if x == "unpriced": return None
        r_out = x[1] / x[0] if x else 0.9
        legs.append((s["frac"], s["px"], x[3] if x else 0.9, x[4] if x else e[4])); ks.append(x[5] if x else None)
        gross += s["frac"] * (s["px"] * r_out) / (t["px0"] * r_in)
    for s in sells[R.MAX_SELLS:]: gross += s["frac"] * s["px"] * 0.97 / (t["px0"] * r_in)
    ntx = 1 + min(len(t["sells"]), 3)
    return dict(copy=gross - 1 - 0.0095 * ntx - 0.0125 * (1 + max(gross, 0)), entry_ratio=r_in, entry_slot=e[2],
                entry_base=e[3], entry_imp1=e[4], legs=legs, k_behind=ks)
d = json.load(open(fn)); w = d["wallet"]
chf = f"{RP.G1}/chain/{w}.json"; ch = json.load(open(chf)) if os.path.exists(chf) else {}
def its_sol(t):
    c = ch.get(t["sig0"]) or {}; s = -(c.get("sol") or 0)
    return s if s > 0.01 else t["usd_in"] / R.SOLUSD
def one(t):
    if ONLY and its_sol(t) < ONLY: return
    if all(t.get(f"s2s{n}") for n in range(NMAX + 1)) or (os.environ.get("KEEP") and all(f"s2s{n}" in t for n in range(NMAX + 1))): return
    for n in range(NMAX + 1):
        try: t[f"s2s{n}"] = score(w, t, n)
        except Exception as ex: t[f"s2s{n}"] = None
    for s in [t["sig0"]] + [x["sig"] for x in t["sells"]]: SEQ.pop(s, None); R.TXC.pop(s, None)
with ThreadPoolExecutor(3) as ex: list(ex.map(one, d["trips"]))
json.dump(d, open(fn, "w"))
for n in range(NMAX + 1):
    ok = [t for t in d["trips"] if t.get(f"s2s{n}")]
    print(w[:8], f"s2s{n}", len(ok), "priced, copy at 1 SOL %+.2f" % sum(t[f"s2s{n}"]["copy"] for t in ok), flush=True)
