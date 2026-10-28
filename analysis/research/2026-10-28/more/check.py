# sim.py against grid.py: the same numbers with the defaults (grid.py cap / land / premium / ROUTES=BC / stops).
#   python3 -I check.py
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim
TR = sim.trips()
print(len(TR), "routable buys of 1.5-9.0 SOL (grid.py: 295)")
for cap in (3, 4):
    sim.show(f"as built, at most {cap} open", sim.score(TR, cap=cap)[0])
sim.show("landing 2 slots after its slot, 3 open", sim.score(TR, land=2)[0])
sim.show("entry at most 0.05 over its price, 3 open", sim.score(TR, pmax=0.05)[0])
sim.show("tp 2.0 sl 0.85, 3 open", sim.score(TR, sl=0.85)[0])
sim.show("ROUTES=BC, 3 open", sim.score(sim.trips(routes="BC"))[0])
sim.show("ladder [(1.0, 2.0)] = as built, 3 open", sim.score(TR, ladder=[(1.0, 2.0)])[0])
sim.show("ladder [(0.5, 2.0), (0.5, 2.0)] = as built + 1 sell", sim.score(TR, ladder=[(0.5, 2.0), (0.5, 2.0)])[0])
