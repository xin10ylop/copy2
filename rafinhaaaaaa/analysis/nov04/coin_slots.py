# Per trip: the fixed rule (its 5.0+ buys, 1 SOL, 300 s or behind its first sale) at each landing; reuses simslot's sim()
import os, sys, runpy, json
os.environ["FIXRULE"] = "buy>=5.00|None|None|300|1.0"
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "simslot.py")).read()
src = src.split("if os.environ.get(\"FIXRULE\"):")[0]          # everything before the fixed-rule printout
g = {"__name__": "x", "__file__": os.path.abspath("simslot.py")}
sys.argv = ["simslot.py", sys.argv[1]]
exec(compile(src, "simslot.py", "exec"), g)
for t in sorted(g["ok"], key=lambda t: t["t0"]):
    if g["its_sol"](t) < 5.0: continue
    r = [g["sim"](t, k, None, None, 300.0, 1.0) for k in ("s2k2", "s2s0", "s2s1", "s2s2", "s2s3")]
    print(t["mint"][:8], f"{g['its_sol'](t):5.2f}", "K2 / slot+0..3:", " ".join("   -  " if x is None else f"{x:+.3f}" for x in r))
