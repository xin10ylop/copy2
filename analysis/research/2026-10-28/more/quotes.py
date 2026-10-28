# Part B by the token its buy was paid in: its big buys (>= LO SOL, single buy + sell trips, coins priced in another
# token) that route_cls.py puts in class E (no route through pump's own programs from wSOL or WBTC). How it paid: a
# Jupiter leg from SOL in the same transaction ("jup": the bot values it, then finds no route: journal "no anchor
# reaches") or from a token it already held ("held": the bot has no price: journal "paid in an unpriced token");
# direct curve buy or multi_hop_swap (hops from qual_routes.json). Its net per coin (ledger), P1 / P2.
#   python3 -I quotes.py [LO]   ->  SPX/quotes.json
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim
LO = float(sys.argv[1]) if len(sys.argv) > 1 else 1.45
SPX = "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/more"
JUP, PAMM = "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4", "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
QR = {q["sig"]: q for q in json.load(open(f"{sim.SP}/h9long/qual_routes.json"))}
out = []
for m, x in sim.T.items():
    if x["kind"] != "pump, other quote" or not x["tr"] or len(x["tr"]) != 2 or not x["tr"][0]["buy"]: continue
    b = x["tr"][0]
    if (b["v"] or 0) < LO: continue
    c = sim.cls(x)
    r = sim.ROWS_BY.get((m, b["s"], 1))
    if not r: continue
    pay = sim.pay_token(x)
    jup = JUP in r["progs"] and (r["d"] + r["tok"].get(sim.WSOL, [0])[0]) < -50_000_000
    mh = PAMM in r["progs"]
    q = QR.get(r["sig"]) or {}
    hops = (q.get("mh") or {}).get("n") if q.get("mh") else (None if not mh else "?")
    out.append(dict(m=m, sig=r["sig"], per=sim.per(b["bt"]), bt=b["bt"], v=b["v"], net=x["net"], cls=c, pay=pay,
                    how="jup" if jup else ("SOL" if pay is None else "held"), mh=mh, hops=hops,
                    path=bool(sim.P.get(m) and "path" in sim.P[m])))
os.makedirs(SPX, exist_ok=True)
json.dump(out, open(f"{SPX}/quotes.json", "w"))
print(f"its single-trip buys >= {LO} SOL of other-quote coins: {len(out)}; by route class:",
      dict(collections.Counter(o["cls"] for o in out)))
E = [o for o in out if o["cls"] == "E"]
print(f"class E (part B): {len(E)} buys, its net {sum(o['net'] or 0 for o in E):+.2f}; how it paid:",
      dict(collections.Counter((o["how"], "multihop" if o["mh"] else "direct") for o in E)))
g = collections.defaultdict(list)
for o in E: g[o["pay"]].append(o)
NAMES = {"pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn": "PUMP", "CARDSccUMFKoPRZxt5vt3ksUbxEFEcnZ3H2pd3dKxYjp": "CARDS",
         "TTWofwAgjnfpJaSswrYCMfxAkBoabdmJhHfHMWUiRBH": "TTWO", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC"}
print(f"\n{'pay token':46s} {'buys':>4s} {'jup':>4s} {'held':>4s} {'mh':>3s}  {'P1 n':>4s} {'its net':>8s}  {'P2 n':>4s} {'its net':>8s}  paths")
for k, v in sorted(g.items(), key=lambda kv: -len(kv[1])):
    a = [o for o in v if o["per"] == "P1"]; b = [o for o in v if o["per"] == "P2"]
    print(f"  {(k or 'SOL'):44s} {len(v):4d} {sum(o['how'] == 'jup' for o in v):4d} {sum(o['how'] == 'held' for o in v):4d} "
          f"{sum(o['mh'] for o in v):3d}  {len(a):4d} {sum(o['net'] or 0 for o in a):+8.2f}  {len(b):4d} {sum(o['net'] or 0 for o in b):+8.2f}  "
          f"{sum(o['path'] for o in v):3d}  {NAMES.get(k, '')}")
