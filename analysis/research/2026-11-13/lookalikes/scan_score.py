# The copy of a wallet on exactly the buys the long copy would take: examples/scan.rs's verdicts (W=<wallet>, the bot's
# own detection and route planner) instead of route_q.py's class. Kept: ROUTABLE, the wallet's first buy of the coin.
# WBTC-input routes (the plan's route input is 3NZ9JMVB: they need our WBTC float) are scored with the rest and also apart.
# Model: cmodel.py (= since_stop/model.py), 1 SOL, 2 open, landing 4 / 8 / one block late; exits tp 3.0 + 300 s,
# tp 2.5 + 1790 s, and follow its sale (30 min cap); raw, without each week's best 2, and corrected = raw + GAP x copies
# (the wallet's model gap per week, copyscore.py). Paths: the cached ones, the rest fetched (cmodel.path).
#   SP=<score data> python3 -I scan_score.py WALLET SCAN.txt JSONDIR GAP1 GAP2
import sys, os, re, json, collections, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import cmodel as M
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/score"); from periods import PA, PB, PC
W, SCAN, JD = sys.argv[1], sys.argv[2], sys.argv[3]; GAP = {"P1": float(sys.argv[4]), "P2": float(sys.argv[5])}
WBTC = "3NZ9JMVB"
bt = {}; mints = {}
for f in os.listdir(JD):
    t = json.load(open(f"{JD}/{f}")); bt[t["slot"]] = t["blockTime"]
    for b in (t["meta"].get("postTokenBalances") or []):
        if b.get("owner") == W: mints[(t["slot"], b["mint"][:8])] = b["mint"]
rows, seen = [], set()
for l in open(SCAN):
    m = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL from (\S+) quote (\S+) jupiter (\S+): (ROUTABLE|no route)(.*)", l)
    u = re.match(r"(\d+) (\S{8}) unpriced: paid in (\S+)", l)
    if m:
        s = int(m.group(1)); r = dict(slot=s, t=bt.get(s), mint8=m.group(2), sol=float(m.group(3)), frm=m.group(4), quote=m.group(5),
                                     verdict="ROUTABLE" if m.group(7) == "ROUTABLE" else "no route", why=m.group(8).strip()[:60])
        ri = re.search(r"route: Route \{ input: (\w{8})", l)          # what our bot pays with: wSOL, or the WBTC float
        r["frm"] = ri.group(1) if ri else r["frm"]
    elif u:
        s = int(u.group(1)); r = dict(slot=s, t=bt.get(s), mint8=u.group(2), sol=None, frm=u.group(3), quote="?", verdict="unpriced", why="")
    else: continue
    r["first"] = r["mint8"] not in seen; seen.add(r["mint8"]); rows.append(r)
per = lambda t: "P1" if t < PB else "P2" if t < PC else "P3"
day = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d")
print(f"{W[:8]}: scan.rs verdicts on its buys (1.0+ SOL priced, and every unpriced one), first buy of a coin only")
c = collections.Counter((per(r["t"]), r["verdict"] + (" (WBTC input)" if r["verdict"] == "ROUTABLE" and r["frm"] == WBTC else "")) for r in rows if r["first"])
for p in ("P1", "P2", "P3"):
    print(f"   {p}: " + "  ".join(f"{k[1]} {v}" for k, v in sorted(c.items()) if k[0] == p))
dc = collections.Counter((day(r["t"]), r["verdict"]) for r in rows if r["first"])
print("   by day (UTC): " + "  ".join(f"{d}: R {dc[(d, 'ROUTABLE')]} / no {dc[(d, 'no route')]} / unpriced {dc[(d, 'unpriced')]}" for d in sorted({k[0] for k in dc})))
print("   quotes of the no-route buys: ", collections.Counter(r["quote"] for r in rows if r["first"] and r["verdict"] == "no route").most_common(8))
take = [r for r in rows if r["first"] and r["verdict"] == "ROUTABLE" and PA <= r["t"] < PC]
sigs = sorted(json.load(open(f"{os.environ['SP']}/h9long/{W[:8]}_sigs.json")), key=lambda x: x[2])
from concurrent.futures import ThreadPoolExecutor
def load(r):
    m = mints.get((r["slot"], r["mint8"]))
    if not m: return None
    anchor = next((s for s, sl, b, f in sigs if b >= r["t"] + 1880), None)
    return M.path(m, r["slot"], anchor, threads=24)
with ThreadPoolExecutor(4) as ex:
    for r, tr in zip(take, ex.map(load, take)): r["tr"] = tr
take = [r for r in take if r.get("tr") and M.its_buy(W, r, r["tr"]) is not None]
print(f"\n{len(take)} ROUTABLE first buys with its buy on the path (of which WBTC input {sum(1 for r in take if r['frm'] == WBTC)}); "
      f"week 1 {sum(1 for r in take if per(r['t']) == 'P1')}, week 2 {sum(1 for r in take if per(r['t']) == 'P2')}")
def sim(rs, n, **kw):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x > r["t"]]
        if len(open_) >= 2: continue
        o = M.model(W, r, r["tr"], 1.0, n, **kw)
        if "net" not in o: continue
        if o["exit"] != "refused": open_.append(r["t"] + o.get("held", 0))
        out.append(o)
    v = sorted((o["net"] for o in out if o["exit"] != "refused"), reverse=True); a = sum(o["net"] for o in out)
    return len(v), a, a - sum(v[:2]), sum(1 for o in out if o["exit"] == "refused")
EX = (("tp 3.0 + 300 s", dict(tp=3.0, sl=None, hold=300)), ("tp 2.5 + 1790 s", dict(tp=2.5, sl=None, hold=1790)),
      ("follow its sale", dict(tp=None, sl=None, hold=1790, follow=True)))
for sel, lab in ((lambda r: True, "all ROUTABLE"), (lambda r: r["frm"] != WBTC, "ROUTABLE without WBTC input")):
    print(f"\n== {lab}: 1 SOL, 2 open; net raw (w/o best 2) [corrected], copies, refused")
    print(f"   {'exit':18s} {'landing':10s} | {'week 1':>36s} | {'week 2':>36s}")
    for en, kw in EX:
        for n, ln in ((4, "4 after"), (8, "8 after"), ("slot+1", "block late")):
            cells = []
            for p in ("P1", "P2"):
                k, s, s2, ref = sim([r for r in take if per(r["t"]) == p and sel(r)], n, **kw)
                cells.append(f"{s:+6.2f} ({s2:+6.2f}) [{s + GAP[p] / 100 * k:+6.2f}] {k:3d} {ref:2d}")
            print(f"   {en:18s} {ln:10s} | " + " | ".join(cells))
