# The ideas of this study re-scored with P3 (Oct 27 00:20 -> Oct 28 14:54 UTC) from the other session's re-run
# (SP/fresh3/h9long, ../fresh/README.md): sim.py with DATA=fresh3. Two sets, at most 4 open:
#   grid  grid.py's (1.5+ SOL, routes A B C)
#   bot   the bot's (../fresh grid.py "the bot's set": 1.45+, graduated coins in, its 3-hop coins out: AvcwGFaF,
#         2FSWwQwj in P3 and the 5 of P1 / P2 from routes.json)
#   python3 -I p3.py
import os, sys, datetime
os.environ["DATA"] = "fresh3"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim
THREE = ("AvcwGFaF", "2FSWwQwj", "6dp2JZAY", "CCci2Fr6", "CcLYZCSg", "EkvZsJuJ", "NotmcxBN")
SETS = {"grid": sim.trips(lo=1.5), "bot": sim.trips(lo=1.45, grad=True, nots=THREE)}
CL = {m: sim.cls(x) for S in SETS.values() for m, x, p in S}
def hour(x): return datetime.datetime.fromtimestamp(x["tr"][0]["bt"], datetime.timezone.utc).hour
V = [("as built", {}, None),
     ("stake 2.0 on WBTC routes, 1.0 on wSOL", {}, lambda m, x: {"stake": 2.0 if CL[m] in "BC" else 1.0}),
     ("stake 1.5 on WBTC routes, 1.0 on wSOL", {}, lambda m, x: {"stake": 1.5 if CL[m] in "BC" else 1.0}),
     ("stake 2.0 on every route", {"stake": 2.0}, None),
     ("WBTC routes only", {}, lambda m, x: {} if CL[m] in "BC" else {"skip": True}),
     ("landing in its own slot (land 0)", {"land": 0}, None),
     ("landing 3 slots after", {"land": 3}, None),
     ("entry limit 25% (the bot's)", {"pmax": 0.25}, None),
     ("stop 0.8 wSOL / 0.9 WBTC routes", {}, lambda m, x: {"sl": 0.9 if CL[m] in "BC" else 0.8}),
     ("tp 2.0, floor 1.2 after 1.5", {"floor": (1.5, 1.2)}, None),
     ("tp 2.0, floor 1.5 after 1.8", {"floor": (1.8, 1.5)}, None),
     ("half at 1.5, half at 2.0", {"ladder": [(0.5, 1.5), (0.5, 2.0)]}, None),
     ("without 18-24h UTC", {}, lambda m, x: {"skip": True} if hour(x) >= 18 else {}),
     ("1.5+ SOL only", {}, lambda m, x: {} if x["tr"][0]["v"] >= 1.5 else {"skip": True})]
for name, TR in SETS.items():
    print(f"{name} set: {len(TR)} buys")
    for label, kw, kw_of in V:
        sim.show(label, sim.score(TR, cap=4, kw_of=kw_of, **kw)[0], 40)
    TRx = sim.trips(lo=1.45, grad=True, nots=("AvcwGFaF", "2FSWwQwj")) if name == "bot" else None
    if TRx: sim.show("3-hop coins of P1 / P2 in (fresh's bot set)", sim.score(TRx, cap=4)[0], 40)
