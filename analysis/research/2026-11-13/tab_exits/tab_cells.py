# A few cells of tab_grid.py side by side, by landing: the live rule, the live rule with its early dumps followed,
# and the grid's pick (tp 4.0, 600 s, its sale followed in the first 60 s).   (same arguments as tab_grid.py)
import sys, os, io, contextlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tab_grid as G
CELLS = (("live: tp 3.0, 300 s, never follow", dict(tp=3.0, hold=300, fol=None, sl=None)),
         ("tp 3.0, 300 s, follow its sale at 0-60 s", dict(tp=3.0, hold=300, fol=(0, 60, 1e9), sl=None)),
         ("tp 3.0, 600 s, follow its sale at 0-60 s", dict(tp=3.0, hold=600, fol=(0, 60, 1e9), sl=None)),
         ("tp 4.0, 300 s, follow its sale at 0-60 s", dict(tp=4.0, hold=300, fol=(0, 60, 1e9), sl=None)),
         ("tp 4.0, 600 s, follow its sale at 0-60 s", dict(tp=4.0, hold=600, fol=(0, 60, 1e9), sl=None)),
         ("tp 4.0, 600 s, never follow", dict(tp=4.0, hold=600, fol=None, sl=None)))
print(f"{G.STAKE} SOL, 2 open; per landing 4 / 8 / one block late: raw (without the best 2), copies")
for name, kw in CELLS:
    print(name)
    for i, wk in enumerate(("week 1", "week 2")):
        x = [G.sim(G.WK[i], n, kw) for n in G.LAND]
        c = sum(a[2] for a in x) / 3; raw = sum(a[0] for a in x) / 3
        print(f"   {wk}: " + " | ".join(f"{a[0]:+.3f} ({a[1]:+.3f}) {a[2]:3d}" for a in x) + f"   mean raw {raw:+.3f}, corrected {raw + G.GAP[i] * G.STAKE * c:+.3f}")
