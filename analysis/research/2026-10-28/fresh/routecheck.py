# Fresh study: route_cls.py's class against the bot's own verdict (../verify/scan.out: examples/scan.rs over Oct 27 17:50
# to Oct 28 13:14 UTC) for its 1.45+ SOL first buys of coins priced in another token in that window.
#   python3 -I routecheck.py
import sys, os, json, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from route_cls import cls
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/fresh3"
W = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
here = os.path.dirname(os.path.abspath(__file__))
V = {}
for l in open(os.path.join(here, "..", "verify", "scan.out")):
    p = l.split()
    if len(p) > 2 and p[0].isdigit() and len(p[1]) == 8:
        V[p[1]] = "ROUTABLE" if ": ROUTABLE" in l else "unpriced" if "unpriced" in l else re.sub(r"\(.*", "", l.split(": ", 1)[1].strip())
T = json.load(open(f"{SP}/h9long/{W[:8]}_trips.json"))
F, U = 1793123400, 1793193240        # Oct 27 17:50, Oct 28 13:14 UTC
c = collections.Counter(); bad = []
for x in T:
    tr = x["tr"]
    if x["kind"] != "pump, other quote" or not tr or not tr[0]["buy"] or not F <= tr[0]["bt"] < U or (tr[0]["v"] or 0) < 1.45: continue
    k = cls(x); v = V.get(x["m"][:8], "not in scan.out")
    c[(k in "ABC", v)] += 1
    if (k in "ABC") != (v == "ROUTABLE"): bad.append((x["m"], k, v, round(tr[0]["v"], 3), len(tr)))
for k in sorted(c, key=str): print(f"   route_cls {'A/B/C' if k[0] else 'E    '}  bot: {k[1]:24s} {c[k]}")
for b in bad: print("   differs:", *b)
