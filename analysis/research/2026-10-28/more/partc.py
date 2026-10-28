# Part C again, cheaply: its 0.8-1.45 SOL buys (the band paths of full_paths_band.py are in the same _fpaths.json), a stake
# scaled to its buy (0.7x) or 1 SOL, by route class (BC = the WBTC routes: multihop from WBTC or a WBTC-quoted curve;
# A = from wSOL), alone and beside part A as built (at most 4 open), P1 / P2.   python3 -I partc.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim
A = sim.trips()
print("part A as built (1.5+, routes ABC):")
sim.show("   at most 4 open", sim.score(A, cap=4)[0])
for lo, hi in ((0.8, 1.45), (0.8, 1.0), (1.0, 1.25), (1.25, 1.45), (1.45, 1.5)):
    for routes in ("BC", "A", "ABC"):
        TR = sim.trips(lo=lo, hi=hi, routes=routes)
        print(f"its {lo}-{hi} SOL buys, routes {routes}: {len(TR)}")
        for name, kw in (("stake 0.7x its buy", lambda m, x: {"stake": 0.7 * x["tr"][0]["v"]}), ("stake 1 SOL", None)):
            sim.show(f"   {name}, no cap", sim.score(TR, cap=99, kw_of=kw)[0])
            if routes == "BC" and (lo, hi) == (0.8, 1.45):
                sim.show(f"   {name}, beside part A, 4 open", sim.score(A + TR, cap=4, kw_of=(lambda m, x, kw=kw, TRm={t[0] for t in TR}: (kw(m, x) if kw else {}) if m in TRm else {}))[0])
