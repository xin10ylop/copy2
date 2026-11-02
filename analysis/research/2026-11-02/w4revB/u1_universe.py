# Step 1: the part-B universe. Every landed quote-control create of Oct 19 00:00 - Oct 27 00:00 UTC (the part-A agent's
# full read, ../w4rev/out/qc_creates_1792368000_1793059200.json, read-only), its quote classed as rugsnipe-long's
# route.rs would find it (../w4rev/routes.py: C = WBTC, A = canonical PumpSwap pool vs wSOL, B = vs WBTC only, E =
# neither; pools as of Nov 1, ../w4rev/out/pools_q.json plus our own reads for the missing quotes). Part B = class E.
# Labels: wallet 4's launch buys (its buy in the create slot or the next; ../w4rev/out/picks.json, built from
# h9long/H9kuqGKN_trips.json), "big" = 1.45+ SOL.
# USDC-quoted creates do not touch the quote-control PDA (11 of 15 in the part-A agent's 1,500-signature check), so
# USDC is under-counted here; u1b_usdc.py estimates it from a mint-authority sample.
#   python3 -I u1_universe.py -> out/universe.json [row], out/pools_q.json
import sys, os, time, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blib
QC = blib.A_OUT + f"/qc_creates_{blib.T_LO}_{blib.T_HI}.json"
PF = blib.OUT + "/pools_q.json"
POOLS = blib.jl(blib.A_OUT + "/pools_q.json")
if os.path.exists(PF): POOLS.update(blib.jl(PF))
def _fetch(q):
    return q, [bool((blib.rpc("getAccountInfo", [blib.canonical(q, a), {"encoding": "base64", "dataSlice": {"offset": 0, "length": 8}}]) or {}).get("value"))
               for a in (blib.WSOL, blib.WBTC)]
def ensure(qs):
    todo = sorted({q for q in qs if q and q not in POOLS and q not in blib.SOL_LIKE and q != blib.WBTC})
    if todo:
        with ThreadPoolExecutor(8) as ex:
            for q, v in ex.map(_fetch, todo): POOLS[q] = v
        blib.jdump(POOLS, PF)
def cls(q):
    if q in blib.SOL_LIKE: return "S"
    if q == blib.WBTC: return "C"
    w, b = POOLS[q]
    return "A" if w else "B" if b else "E"
SYM = {"pumpCmXq": "PUMP", "CARDSccU": "CARDS", "TTWofwAg": "TTWO", "EPjFWdd5": "USDC", "A7bdiYdS": "ZEC", "WXMRyRZh": "XMR",
       "SPCXxcqX": "SPCX", "DJTu7vi8": "DJTu", "7vfCXTUX": "WETH", "DoGEV7LA": "DOGE", "Pren1FvF": "Pren1F", "PreweJYE": "Prewe"}
def sym(q): return SYM.get((q or "")[:8], (q or "")[:8])
if __name__ == "__main__":
    U = blib.jl(QC)
    rows = [r for r in U.values() if r.get("mint") and blib.T_LO <= (r.get("cbt") or 0) < blib.T_HI]
    ensure([r["quote"] for r in rows])
    P = blib.jl(blib.A_OUT + "/picks.json")
    pk = {p["csig"]: (m, p) for m, p in P.items() if p.get("csig") and p.get("ds") is not None}
    c = collections.Counter(cls(r["quote"]) for r in rows)
    print(f"{len(U)} quote-control signatures read, {len(rows)} creates in Oct 19 00:00 - Oct 27 00:00 UTC; by quote class: {dict(c)}")
    out = []
    for r in rows:
        if cls(r["quote"]) != "E": continue
        x = {k: r[k] for k in ("mint", "csig", "cslot", "cbt", "cidx", "payer", "quote", "user", "creator", "name", "sym", "uri",
                               "vquote", "vtok", "depth", "mayhem", "cashback", "cfee", "dev", "fee", "progs", "nsig", "cu")}
        mp = pk.get(r["csig"])
        p = mp[1] if mp else None
        x.update(per=blib.per(r["cbt"]), w4ds=p["ds"] if p else None, w4v=p["v"] if p else 0.0, w4net=p["net"] if p else 0.0,
                 w4bslot=p["bslot"] if p else None, w4bidx=p.get("bidx") if p else None, w4vt=p.get("vt") if p else None)
        x["pick"] = int(p is not None and p["ds"] <= 1); x["big"] = int(x["pick"] and p["v"] >= 1.45)
        x["late"] = int(p is not None and p["ds"] > 1)
        out.append(x)
    blib.jdump(out, blib.OUT + "/universe.json")
    # its class-E launch picks not in the universe (quote-control missing: USDC)
    have = {x["csig"] for x in out}
    miss = [(m, p) for m, p in P.items() if p.get("quote") and p.get("ds") is not None and p["ds"] <= 1 and blib.T_LO <= p["cbt"] < blib.T_HI
            and p["quote"] not in blib.SOL_LIKE and p["csig"] not in have]
    ensure([p["quote"] for m, p in miss])
    mE = [(m, p) for m, p in miss if cls(p["quote"]) == "E"]
    print(f"part B (class E) creates: {len(out)}; wallet 4 launch picks among them {sum(x['pick'] for x in out)} (1.45+: {sum(x['big'] for x in out)}),"
          f" later buys {sum(x['late'] for x in out)}")
    print(f"its class-E launch picks of Oct 19-26 NOT in the quote-control universe: {len(mE)} "
          f"{collections.Counter(sym(p['quote']) for m, p in mE).most_common(6)}; 1.45+: {sum(1 for m, p in mE if p['v'] >= 1.45)}")
    # by quote token: creates, picks, share, its net, per period
    g = collections.defaultdict(list)
    for x in out: g[x["quote"]].append(x)
    print("\nby quote token (class E), Oct 19-22 = P1, Oct 23-26 = P2: creates / its launch picks (share) / 1.45+ picks / its net on the picks [1.45+]")
    print(f"{'quote':10s} {'mint':10s} | {'P1 creates':>10s} {'picks':>6s} {'share':>6s} {'big':>4s} {'net':>8s} {'[big]':>8s} | {'P2 creates':>10s} {'picks':>6s} {'share':>6s} {'big':>4s} {'net':>8s} {'[big]':>8s}")
    order = sorted(g, key=lambda q: -(sum(x["pick"] for x in g[q]) * 1000 + len(g[q])))
    tot = collections.defaultdict(float)
    for q in order:
        L = g[q]; line = f"{sym(q):10s} {q[:10]:10s}"
        for pp in ("P1", "P2"):
            S = [x for x in L if x["per"] == pp]; n = len(S); pi = sum(x["pick"] for x in S); bg = sum(x["big"] for x in S)
            net = sum(x["w4net"] for x in S if x["pick"]); nb = sum(x["w4net"] for x in S if x["big"])
            line += f" | {n:10d} {pi:6d} {pi / n if n else 0:6.1%} {bg:4d} {net:+8.2f} {nb:+8.2f}"
            tot[pp, "n"] += n; tot[pp, "p"] += pi; tot[pp, "b"] += bg; tot[pp, "net"] += net; tot[pp, "nb"] += nb
        if sum(x["pick"] for x in L) >= 3 or len(L) >= 1500: print(line)
    rest = [q for q in order if not (sum(x["pick"] for x in g[q]) >= 3 or len(g[q]) >= 1500)]
    print(f"... {len(rest)} more quotes ({sum(len(g[q]) for q in rest)} creates, {sum(x['pick'] for q in rest for x in g[q])} picks)")
    print("total      " + "".join(f"           | {int(tot[pp, 'n']):10d} {int(tot[pp, 'p']):6d} {tot[pp, 'p'] / tot[pp, 'n']:6.1%} {int(tot[pp, 'b']):4d} {tot[pp, 'net']:+8.2f} {tot[pp, 'nb']:+8.2f}" for pp in ("P1", "P2")))
    print(f"quotes with any create: {len(g)}; with a launch pick: {sum(1 for q in g if any(x['pick'] for x in g[q]))}")
    # per day by quote token: creates (picks)
    days = sorted({time.strftime("%m-%d", time.gmtime(x["cbt"])) for x in out})
    top = [q for q in order if sum(x["pick"] for x in g[q]) >= 20][:14]
    print("\nper day (UTC): creates / launch picks / 1.45+ picks, by quote token")
    print(f"{'quote':8s} " + " ".join(f"{d:>14s}" for d in days))
    for q in top + ["other"]:
        S = [x for x in out if (x["quote"] == q if q != "other" else x["quote"] not in top)]
        cells = []
        for d in days:
            D = [x for x in S if time.strftime("%m-%d", time.gmtime(x["cbt"])) == d]
            cells.append(f"{len(D):5d}/{sum(x['pick'] for x in D):4d}/{sum(x['big'] for x in D):3d}")
        print(f"{(sym(q) if q != 'other' else 'other'):8s} " + " ".join(f"{c:>14s}" for c in cells))
    D = collections.Counter(time.strftime("%m-%d", time.gmtime(x["cbt"])) for x in out)
    Dp = collections.Counter(time.strftime("%m-%d", time.gmtime(x["cbt"])) for x in out if x["pick"])
    Db = collections.Counter(time.strftime("%m-%d", time.gmtime(x["cbt"])) for x in out if x["big"])
    print(f"{'all':8s} " + " ".join(f"{f'{D[d]:5d}/{Dp[d]:4d}/{Db[d]:3d}':>14s}" for d in days))
    print("calls", blib.calls())
