# TAB: how often each take profit fires, and what the copies that reach it make (Nov 18, "tp for tab is 6x?").
import sys, os, numpy as np
here = os.path.dirname(os.path.abspath(__file__)); sys.argv = sys.argv[:3] + ["x=0.5,1.5,6,600,5/60,180,never"]
exec(open(os.path.join(here, "e11_check.py")).read().split("base = None")[0])
Y = per_copy("0.5,1.5,none,600,5/60,180,never")
print("tp   | fires (copies, mean of 3 landings) | SOL all copies | SOL of the copies where it fires, with that tp / with no tp")
for t in ("2", "2.5", "3", "3.5", "4", "5", "6", "8"):
    X = per_copy(f"0.5,1.5,{t},600,5/60,180,never"); hit = np.abs(X - Y) > 1e-9; h = hit.mean(axis=1)
    print(f"{t:4s} | {h.sum():5.1f} | {X.mean(axis=1).sum():+6.2f} | {(X * hit).sum() / 3:+6.2f} / {(Y * hit).sum() / 3:+6.2f}")
