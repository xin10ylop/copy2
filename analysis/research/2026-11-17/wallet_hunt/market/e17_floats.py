# Which float pays for wallet 4's copies, and what each makes (Nov 18, the owner: "which float never traded, so we
# decide which to eliminate"). e11's copies (Oct 21 - Nov 18), the running setting; the paying float = the coin's quote
# when it is one of the 7, else the route's input from the planner's scan.
import sys, os, collections, numpy as np, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); spec = sys.argv[3]; sys.argv = sys.argv[:3] + ["x=" + spec]
src = open(os.path.join(here, "e11_check.py")).read().split("base = None")[0]
src = src.replace('INP.setdefault(f"{d_}/{m.group(1)}_{m.group(2)}", "float" if m.group(4) in FLOATS or m.group(3)[:8] in FLOATS else "wsol")',
                  'INP.setdefault(f"{d_}/{m.group(1)}_{m.group(2)}", "float" if m.group(4) in FLOATS or m.group(3)[:8] in FLOATS else "wsol"); PAYER[f"{d_}/{m.group(1)}_{m.group(2)}"] = m.group(3)[:8] if m.group(3)[:8] in FLOATS else m.group(4)')
exec(src.replace("INP = {}", "INP = {}; PAYER = {}") if "INP = {}" in src else src)
NAME = {"3NZ9JMVB": "WBTC", "pumpCmXq": "PUMP", "SPCXxcqX": "SPCX", "TTWofwAg": "TTWO", "DJTu7vi8": "DJT", "98sMhvDw": "HYPE", "XsbEhLAt": "AAPLx", "So111111": "wSOL"}
v = per_copy(spec).mean(axis=1); b = v != 0
pay = np.array([r["q"] if r["q"] in FLOATS else ("float via route" if r["cls"] == "float" else "wSOL") for r in rows])
since = T >= 1794700800   # Nov 15 00:00 UTC: all 7 floats held (AAPLx from Nov 15 21:38)
print(f"\n{spec}: copies by what pays (the coin's quote when it is a float)")
print("payer            | all Oct 21-Nov 18: copies  SOL   a copy | since Nov 15: copies  SOL")
for p, n in collections.Counter(pay[b]).most_common():
    f = (pay == p) & b; g = f & since
    print(f"{NAME.get(p, p):16s} | {n:5d} {v[f].sum():+7.2f} {100 * v[f].mean() / 0.5:+6.1f}% | {g.sum():4d} {v[g].sum():+6.2f}")
for p in FLOATS:
    if not ((pay == p) & b).any(): print(f"{NAME[p]:16s} | never")
