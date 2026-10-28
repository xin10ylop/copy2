# grid.py's model with our own hold shorter than the wallet's timer (for 3dwZP6T8: 60-260 s against its 272 s), TP 2.0
# and 1.5, SL 0.8, the other settings as grid.py (W, CAP, MULTI from the environment).
#   W=WALLET CAP=4 MULTI=1 python3 -I hold.py [LO=1.45] [HOLDS=60,120,180,240,260,1790]
import sys, os, runpy
LO = sys.argv[1] if len(sys.argv) > 1 else "1.45"
HOLDS = [int(h) for h in (sys.argv[2] if len(sys.argv) > 2 else "60,120,180,240,260,1790").split(",")]
sys.argv = ["grid.py", "none", "q", "1", LO, "9"]
g = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "grid.py"))
for tp in (2.0, 1.5):
    for hold in HOLDS:
        g["show"](f"tp {tp} sl 0.8 hold {hold} s", g["score"](tp=tp, sl=0.8, hold=hold)[0])
