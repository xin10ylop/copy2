# The SOL price of each quote token, the way h9long/ledger.py builds it (copy2 analysis/research/2026-10-27/h9long/):
# from wallet 4's own transactions (H9kuqGKN.jsonl, Oct 19 00:00 - Oct 27 00:40 UTC) that swap one token against SOL
# (native + wSOL, its fee and tip added back) for more than 0.01 SOL, or one token against USD (USDC / USDT / USD1) priced
# at the SOL/USD rate of its own SOL-USD swaps. Price = SOL per whole token (UI units).
#   python3 -I prices.py -> out/tokp.json {mint: {"dec": d, "ser": [[bt, sol_per_token], ...]}}
# price_at(mint, bt) = the nearest observation (ledger.py's near()); move(mint, t0, t1) = price_at(t1) / price_at(t0).
import os, sys, json, bisect, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib
WSOL = blib.WSOL
USD = {"EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
       "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB"}
PF = blib.OUT + "/tokp.json"
def near(ser, t):
    if not ser: return None
    ts = [x[0] for x in ser]; k = bisect.bisect_left(ts, t)
    c = [ser[j] for j in (k - 1, k) if 0 <= j < len(ser)]
    return min(c, key=lambda x: abs(x[0] - t))[1]
def build(path=blib.H9 + "/H9kuqGKN.jsonl"):
    rows = sorted((json.loads(l) for l in open(path)), key=lambda r: (r["s"], r["i"] or 0))
    dec = {}
    def legs(r):
        sol = r["d"] + r["tok"].get(WSOL, [0])[0]
        usd = sum(v[0] / 10 ** v[1] for m, v in r["tok"].items() if m in USD)
        tk = {}
        for m, v in r["tok"].items():
            if m != WSOL and m not in USD: tk[m] = v[0] / 10 ** v[1]; dec[m] = v[1]
            elif m in USD: dec[m] = v[1]
        return sol / 1e9, usd, tk
    usdp, usdq = [], []; tokp = collections.defaultdict(list)
    for r in rows:
        sol, usd, tk = legs(r)
        fee = (r["fee"] or 0) / 1e9 + (r["tip"] or 0) / 1e9 if r["signer"] else 0
        s = sol + fee
        if not tk and abs(usd) > 1 and s * usd < 0: usdp.append((r["bt"], -s / usd))
        if len(tk) == 1:
            (m, q), = tk.items()
            if q and abs(s) > 0.01 and s * q < 0 and abs(usd) < 0.01: tokp[m].append((r["bt"], -s / q))
            elif q and abs(usd) > 1 and usd * q < 0 and abs(s) < 0.02: usdq.append((r["bt"], m, -usd / q))
    usdp.sort()
    for t, m, pu in usdq:
        if near(usdp, t): tokp[m].append((t, pu * near(usdp, t)))
    for m in tokp: tokp[m].sort()
    out = {m: dict(dec=dec.get(m), ser=[list(x) for x in v]) for m, v in tokp.items()}
    for m in USD:                                   # USD itself: SOL per USD from its SOL-USD swaps
        if usdp: out[m] = dict(dec=dec.get(m, 6), ser=[list(x) for x in usdp])
    return out
_T = None
def load():
    global _T
    if _T is None: _T = blib.jl(PF)
    return _T
def price_at(m, t):
    T = load(); x = T.get(m)
    return near(x["ser"], t) if x else None
def lamports_per_raw(m, t):
    T = load(); x = T.get(m)
    if not x or x["dec"] is None: return None
    p = near(x["ser"], t)
    return p * 1e9 / 10 ** x["dec"] if p else None
def n_obs(m, t0, t1):
    T = load(); x = T.get(m)
    return sum(1 for a, _ in x["ser"] if t0 <= a < t1) if x else 0
if __name__ == "__main__":
    out = build(); blib.jdump(out, PF)
    print(f"{len(out)} tokens priced; top by observations:")
    for m, v in sorted(out.items(), key=lambda kv: -len(kv[1]["ser"]))[:25]:
        s = v["ser"]; print(f"  {m[:8]} dec {v['dec']} n {len(s):5d}  first {s[0][1]:.4g}  last {s[-1][1]:.4g}")
