# NOTE: sim_pool.py shows multi_hop_swap refuses every pool here (OnlyPumpPools: canonical pump pools only), so this
# is what part B would add IF those pools could be used: an upper bound, not a plan.
# Part B made routable: its big buys of class E whose pay token a PumpSwap pool reaches from wSOL, directly or through
# USDC (USDC / wSOL and PUMP / USDC are deep on PumpSwap; pools.py). Our route per buy (the cheapest that exists, at most
# HOPS hops): its direct curve buy behind a pool hop from wSOL (2 hops) or wSOL -> USDC -> token (3); its 2-hop route
# from the token behind the same (3 or 4). Each pool hop in front costs PumpSwap's 0.25% fee plus its price impact on
# 1 SOL (1 / (R + 1), R its SOL side now) each way, on top of grid.py's costs. The copy as grid.py prices it (sim.py),
# alone and beside part A (routes A, B, C), at most 4 open; FLOAT=USDC prices the USDC float instead of the wSOL->USDC hop;
# MINR (20) the smallest pool used, in SOL on its SOL side (thinner ones cost over 5% each way).
#   python3 -I partb.py [HOPS] [LO]
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim
HOPS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
LO = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
FLOAT = os.environ.get("FLOAT", "")
MINR = float(os.environ.get("MINR", "20"))       # a pool hop needs at least this much SOL on its SOL side (impact <= 5%)
SPX = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/more"
PL = json.load(open(f"{SPX}/pools.json"))["tokens"]; RT = json.load(open(f"{SPX}/routes.json"))
QS = {q["m"]: q for q in json.load(open(f"{SPX}/quotes.json"))}
USDC, FEE = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", 0.0025
NAMES = {"pumpCmXq": "PUMP", "EPjFWdd5": "USDC", "CARDSccU": "CARDS", "TTWofwAg": "TTWO"}
def hop_cost(sol_side):
    return (1 - FEE - 1 / (sol_side + 1)) ** 2 if sol_side else 0.0
def best(t, a):
    ps = ((PL.get(t) or {}).get("pools") or {}).get(a) or []
    return ps[0]["sol_side"] if ps and (ps[0]["sol_side"] or 0) >= MINR else None
def plan(m):
    """(hops, cost factor, how) of our cheapest route, or None"""
    q = QS.get(m); r = RT.get(q["sig"]) if q else None
    if not q or not q["pay"]: return None
    t = q["pay"]; its_hops = len(r["hops"]) if r and r.get("hops") else 1     # a direct buy: the curve hop
    opts = []
    if t == USDC:
        if FLOAT == "USDC": opts.append((its_hops, 1.0, "USDC float"))
        elif best(USDC, "wsol"): opts.append((its_hops + 1, hop_cost(best(USDC, "wsol")), "wSOL->USDC"))
    else:
        if best(t, "wsol"): opts.append((its_hops + 1, hop_cost(best(t, "wsol")), "wSOL pool"))
        if best(t, "usdc"):
            c = hop_cost(best(t, "usdc"))
            if FLOAT == "USDC": opts.append((its_hops + 1, c, "USDC float + pool"))
            elif best(USDC, "wsol"): opts.append((its_hops + 2, c * hop_cost(best(USDC, "wsol")), "wSOL->USDC->pool"))
    opts = [o for o in opts if o[0] <= HOPS]
    return max(opts, key=lambda o: o[1]) if opts else None
E = sim.trips(lo=LO, routes="E")
new, why = [], collections.Counter()
for m, x, path in E:
    p = plan(m)
    pay = NAMES.get((QS.get(m) or {}).get("pay", "")[:8] if (QS.get(m) or {}).get("pay") else "", "other")
    why[(pay, p[2] if p else "no route")] += 1
    if p: new.append((m, x, path, p))
print(f"its class-E buys {LO}+ SOL with a path: {len(E)}; our route at most {HOPS} hops{' (USDC float)' if FLOAT else ''}:")
for k, v in sorted(why.items(), key=lambda kv: -kv[1]): print(f"   {k[0]:6s} {k[1]:22s} {v:4d}")
COSTF = {m: p[1] for m, x, path, p in new}
print("   cost factor of the pool hops (round trip): " + ", ".join(f"{h}: {c:.4f}" for h, c in sorted({(p[2], round(p[1], 4)) for *_, p in new})))
NEW = [(m, x, path) for m, x, path, p in new]
A = sim.trips(lo=LO)
kw = lambda m, x: {"cost": COSTF.get(m, 1.0)}
for cap in (4, 99):
    sim.show(f"part A as built, at most {cap} open", sim.score(A, cap=cap)[0])
    sc, got = sim.score(NEW, cap=cap, kw_of=kw); sim.show(f"newly routable part B alone, at most {cap} open", sc)
    sim.show(f"   the same without the hop costs", sim.score(NEW, cap=cap)[0])
    sim.show(f"part A + the new part B, at most {cap} open", sim.score(A + NEW, cap=cap, kw_of=kw)[0])
sc, got = sim.score(NEW, cap=99, kw_of=kw)
for p in ("P1", "P2"):
    g = collections.defaultdict(list)
    for res, m in got[p]: g[NAMES.get(QS[m]["pay"][:8], QS[m]["pay"][:8])].append(res)
    print(f"   {p} by pay token (no cap): " + "  ".join(f"{k} {len(v)} {sum(v):+.2f}" for k, v in sorted(g.items(), key=lambda kv: -len(kv[1]))))
