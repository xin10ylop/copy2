# The Jupiter leg's cost per active quote (state now, Nov 1): for STAKE in (0.1, 1) SOL, Jupiter's quote of SOL -> Q
# (ExactIn) and of the Q received -> SOL; the round trip's loss (1 - SOL back / SOL in) = both swap fees + both price
# impacts. The buy leg alone against the mid price (Jupiter price v3, USD per token, SOL's USD price): 1 - Q out x mid
# / SOL in; the sell leg = round trip less the buy leg. Venues of each route, and Jupiter's liquidity figure.
# Public API (lite-api.jup.ag), paced at 1.2 s; no key.   python3 -I j1_jup.py [sample] -> out/jup.json {quote: {...}}
# ("sample": also every other quote with a coin in out/sample.json)
import sys, os, json, time, urllib.request, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib
from u1_universe import sym
J = "https://lite-api.jup.ag"
def get(u):
    for i in range(5):
        try:
            time.sleep(1.2)
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "w4revB"}), timeout=30) as r: return json.load(r)
        except Exception as e:
            err = str(e)[:120]; time.sleep(3 * (i + 1))
    return {"error": err}
if __name__ == "__main__":
    T = blib.jl(blib.OUT + "/table.json")
    pk = collections.Counter(t["quote"] for t in T if t["pick"])
    QS = [q for q, n in pk.most_common() if n >= 5]
    if len(sys.argv) > 1 and sys.argv[1] == "sample":          # every quote with a coin in the backtest sample
        SQ = collections.Counter(v["quote"] for v in blib.jl(blib.OUT + "/sample.json").values())
        QS = QS + [q for q, _ in SQ.most_common() if q not in QS]
    op = blib.OUT + "/jup.json"; out = blib.jl(op) if os.path.exists(op) else {}
    ids = [blib.WSOL] + QS
    pr = {}
    for i in range(0, len(ids), 40):
        pr.update(get(f"{J}/price/v3?ids={','.join(ids[i:i + 40])}") or {})
    sol_usd = (pr.get(blib.WSOL) or {}).get("usdPrice")
    for q in QS:
        if q in out and "rt" in out[q]: continue
        p = pr.get(q) or {}
        dec = p.get("decimals")
        row = dict(sym=sym(q), usd=p.get("usdPrice"), liq=p.get("liquidity"), dec=dec, sol_usd=sol_usd, rt={})
        mid = p["usdPrice"] / sol_usd if p.get("usdPrice") and sol_usd else None      # SOL per whole token
        for st in (0.1, 1.0):
            lam = int(st * 1e9)
            a = get(f"{J}/swap/v1/quote?inputMint={blib.WSOL}&outputMint={q}&amount={lam}&slippageBps=300")
            if "outAmount" not in a: row["rt"][str(st)] = dict(err=str(a.get("error") or a)[:160]); continue
            qo = int(a["outAmount"])
            b = get(f"{J}/swap/v1/quote?inputMint={q}&outputMint={blib.WSOL}&amount={qo}&slippageBps=300")
            if "outAmount" not in b: row["rt"][str(st)] = dict(err=str(b.get("error") or b)[:160], q_out=qo); continue
            back = int(b["outAmount"]) / 1e9
            buy = (1 - qo / 10 ** dec * mid / st) if (mid and dec is not None) else None
            rt = 1 - back / st
            row["rt"][str(st)] = dict(q_out=qo, sol_back=back, rt=rt, buy=buy, sell=(rt - buy) if buy is not None else None,
                                      imp_buy=float(a.get("priceImpactPct") or 0), imp_sell=float(b.get("priceImpactPct") or 0),
                                      venues_buy=[r["swapInfo"].get("label") for r in a.get("routePlan", [])],
                                      venues_sell=[r["swapInfo"].get("label") for r in b.get("routePlan", [])])
        out[q] = row; blib.jdump(out, op)
        r1 = row["rt"].get("1.0", {}); r0 = row["rt"].get("0.1", {})
        print(f"{row['sym']:10s} liq ${row['liq'] or 0:>14,.0f}  0.1 SOL rt {r0.get('rt', float('nan')):7.2%}  1 SOL rt {r1.get('rt', float('nan')):7.2%}"
              f" (buy {r1.get('buy') if r1.get('buy') is None else f'{r1.get(chr(98)+chr(117)+chr(121)):.2%}'})  {'/'.join(r1.get('venues_buy') or [])[:40]} {r1.get('err', '')}", flush=True)
