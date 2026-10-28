# Fresh study: its 1.45+ SOL first buys of coins priced in another token whose trip has no curve sale (the coin graduated
# before it sold: it sold on PumpSwap), by period. No backtest includes them (full_paths.py needs a curve sale).
#   python3 -I grad.py [MIN_SOL]
import sys, os, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from route_cls import cls
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad/fresh3"
W = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"; MIN = float(sys.argv[1]) if len(sys.argv) > 1 else 1.45
T = json.load(open(f"{SP}/h9long/{W[:8]}_trips.json"))
L = {p["m"]: p for p in json.load(open(f"{SP}/h9long/{W[:8]}_ledger.json"))["pos"]}
def per(t): return "P1" if datetime.datetime.fromtimestamp(t, datetime.timezone.utc).day <= 22 else "P2" if t < 1793060400 else "P3"
out = []
for x in T:
    tr = x["tr"]
    if x["kind"] != "pump, other quote" or not tr or not tr[0]["buy"] or (tr[0]["v"] or 0) < MIN or any(not t["buy"] for t in tr): continue
    b = tr[0]; p = L[x["m"]]
    sells = [t for t in p["tr"] if not t[2]]
    sec = sells[0][1] - b["bt"] if sells else None
    out.append((b["bt"], x["m"], b["v"], cls(x), x["net"], x["open"], sec, -sells[0][3] / b["v"] if sells else None))
for bt, m, v, c, net, op, sec, val in sorted(out):
    print(f"   {per(bt)} {datetime.datetime.fromtimestamp(bt, datetime.timezone.utc):%m-%d %H:%M:%S} UTC  {m}  its {v:.3f} SOL  route {c}  "
          f"its net {net:+.3f}  sold {'after ' + str(sec) + ' s' if sec is not None else 'not yet'} at {val and round(val, 2)}x its SOL  {'(still holds some)' if op else ''}")
json.dump([o[1] for o in out], open(f"{SP}/h9long/{W[:8]}_grad.json", "w"))
