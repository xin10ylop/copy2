# Our copy of one wallet on wallet 4's yardstick (since_stop/vs_him_week.py, exit_search.py), the model of cmodel.py
# (= since_stop/model.py). Copied: its first buys of pump coins priced in another token, FLOOR+ SOL (SOL value from the
# score pipeline's ledger), routable (route_q.py class A, B or C), one buy per coin (MULTI=1: a coin it bought once and
# sold in parts counts too), Oct 29 12:02 -> Nov 12 06:49 UTC; P1 = the pick week to Nov 5 06:49, P2 = the test week.
#  - its own real result on those coins (ledger.py: SOL in and out, quote tokens at its own rate), % of its SOL spent;
#  - the raw model on the wallet itself: its price (landing 0), selling right behind its sale, no tp, no timer, no limit;
#    gap = real % - that model % (the model's caution for this wallet; 9.1 points for wallet 4 Nov 5-12);
#  - our copy: 1 SOL, 2 open, landing 4 / 8 trades after its buy / one block late; exits HOLD (tp 2.5, 30 min, as live),
#    FOLLOW (sell behind its sale, 30 min cap), FOLLOW+TP (sell behind it, or tp 2.5 first); net, (without the best 2),
#    copies, refused at the 1.25 limit; "corr" = net + gap x copies;
#  - a small exit grid (tp x stop x timer x its sale), picked on P1 by the mean over the three landings without the best
#    2, scored on P2.
#   SP=<score data> python3 -I copyscore.py WALLET [FLOOR=1.45]        (W4 data: SRC=w4 SPD=<since_stop> ... H9kuqGKN...)
import sys, os, json, gzip, itertools, statistics, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import cmodel as M
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/score"); from periods import PA, PB, PC
W = sys.argv[1]; FLOOR = float(sys.argv[2]) if len(sys.argv) > 2 else 1.45; MULTI = os.environ.get("MULTI") == "1"
ROUTES = os.environ.get("ROUTES", "ABC")    # E = the copier's coins (no canonical pool: Jupiter), scored one and two blocks late
SRC = os.environ.get("SRC", "score")
W4 = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
SPD = os.environ.get("SPD", "/tmp/claude-0/-home-user-copy2/2a3626e5-937e-5580-9928-ee4cf7459077/scratchpad/since_stop")
w4rows = json.load(open(f"{SPD}/routable.json")); W4COINS = {r["mint8"] for r in w4rows}
trips = []                     # dict(m, slot, t, sol, real, spent, closed, path)
if SRC == "w4":                # wallet 4 from since_stop: its routable 1.45+ buys and their cached paths
    P = json.load(gzip.open(f"{SPD}/paths.json.gz"))
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import w4real
    REAL = w4real.per_coin(SPD)
    for r in w4rows:
        k = f"{r['slot']}_{r['mint8']}"
        if not r["ok"] or k not in P or not (PA <= r["t"] < PC): continue
        m, tr = P[k]; h = REAL.get(m[:8])
        trips.append(dict(m=m, slot=r["slot"], t=r["t"], sol=r["sol"], real=h["net"] if h else None, spent=h["spent"] if h else None,
                          closed=bool(h and not h["bad"]), tr=tr))
else:
    SP = os.environ["SP"]; H = f"{SP}/h9long/{W[:8]}"
    os.environ["W"] = W; from route_q import cls
    T = json.load(open(f"{H}_trips.json")); sigs = sorted(json.load(open(f"{H}_sigs.json")), key=lambda x: x[2])
    for x in T:
        b = x["tr"][0]
        if x["kind"] != "pump, other quote" or not b["buy"] or (b["v"] or 0) < FLOOR or not (PA <= b["bt"] < PC): continue
        nb = sum(1 for y in x["tr"] if y["buy"]); ns = sum(1 for y in x["tr"] if not y["buy"])
        if nb != 1 or (ns > 1 and not MULTI): continue
        if cls(x) not in ROUTES: continue
        anchor = next((s for s, sl, bt, f in sigs if bt >= b["bt"] + 1880), None)
        trips.append(dict(m=x["m"], slot=b["s"], t=b["bt"], sol=b["v"], real=x["net"], spent=b["v"], closed=not x["open"], anchor=anchor))
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(4) as ex:
        for d, tr in zip(trips, ex.map(lambda d: M.path(d["m"], d["slot"], d["anchor"], threads=24), trips)): d["tr"] = tr
trips.sort(key=lambda d: d["t"])
trips = [d for d in trips if M.its_buy(W, d, d["tr"]) is not None]
per = lambda d: "P1" if d["t"] < PB else "P2"
HALF = {"P1": [d for d in trips if per(d) == "P1"], "P2": [d for d in trips if per(d) == "P2"]}
print(f"{W}: {len(trips)} copyable buys ({FLOOR}+ SOL, other quote, route class {ROUTES}, one buy{', sold in parts too' if MULTI else ''}) with its buy on the path; "
      f"P1 {len(HALF['P1'])} ({len(HALF['P1'])/((PB-PA)/86400):.1f} a day), P2 {len(HALF['P2'])} ({len(HALF['P2'])/((PC-PB)/86400):.1f} a day)")
print(f"   size: median {statistics.median(d['sol'] for d in trips):.2f} SOL" if trips else "   no trips")
ov = sum(1 for d in trips if d["m"][:8] in W4COINS)
print(f"   overlap: {ov} of {len(trips)} are coins wallet 4 bought for 1.45+ SOL (since_stop scan.out, Oct 28 - Nov 12)")
n01 = [sum(1 for e in d["tr"][M.its_buy(W, d, d["tr"]) + 1:] if e["slot"] <= d["slot"] + 1) for d in trips]
if n01: print(f"   frenzy: curve trades after its buy in its slot and the next: median {statistics.median(n01)} (p25 {sorted(n01)[len(n01)//4]}, p75 {sorted(n01)[3*len(n01)//4]})")
# its own sale: hold and multiple (first sale on the path)
hs = []
for d in trips:
    k = M.its_buy(W, d, d["tr"]); s = next((e for e in d["tr"][k + 1:] if e["user"] == W and not e["buy"]), None)
    hs.append(None if s is None else s["t"] - d["tr"][k]["t"])
got = sorted(h for h in hs if h is not None)
if got:
    q = lambda p: got[min(len(got) - 1, int(p * len(got)))]
    print(f"   its first sale after its buy: p25 / median / p75 {q(.25)} / {q(.5)} / {q(.75)} s; none within 31 min on {sum(1 for h in hs if h is None)}; "
          f"under 20 s {sum(1 for h in got if h < 20)}, 20-120 s {sum(1 for h in got if 20 <= h < 120)}, 120 s+ {sum(1 for h in got if h >= 120)}")
def sim(rs, n, cap=2, **kw):
    out, open_ = [], []
    for d in rs:
        open_ = [x for x in open_ if x > d["t"]]
        if len(open_) >= cap: continue
        o = M.model(W, d, d["tr"], 1.0, n, **kw)
        if "net" not in o: continue
        if o["exit"] != "refused": open_.append(d["t"] + o.get("held", 0))
        out.append((d, o))
    return out
def sc(res):
    v = sorted((o["net"] for _, o in res if o["exit"] != "refused"), reverse=True)
    allv = [o["net"] for _, o in res]
    return len(v), sum(allv), sum(allv) - sum(v[:2]), sum(1 for _, o in res if o["exit"] == "refused")
# its real result and the gap
print("\n== its own result on these coins (closed coins), and the raw model on it (landing 0, behind its sale)")
GAP = {}
for p in ("P1", "P2", "both"):
    rs = trips if p == "both" else HALF[p]
    c = [d for d in rs if d["closed"] and d["real"] is not None and d["spent"]]
    if not c: print(f"   {p}: none"); continue
    real = 100 * sum(d["real"] for d in c) / sum(d["spent"] for d in c)
    v = sorted((d["real"] for d in c), reverse=True)
    mo = [M.model(W, d, d["tr"], 1.0, 0, tp=None, sl=None, hold=10**9, follow=True, pmax=99) for d in c]
    mp = 100 * sum(o["net"] for o in mo if "net" in o) / max(1, sum(1 for o in mo if "net" in o))
    GAP[p] = real - mp
    print(f"   {p}: {len(c)} coins, spent {sum(d['spent'] for d in c):.2f} SOL, real {sum(v):+.2f} SOL ({real:+.1f}%), without its best 2 {sum(v[2:]):+.2f}; "
          f"won {sum(1 for x in v if x > 0)}; model on it {mp:+.1f}% a trade -> gap {real - mp:+.1f} points")
POL = (("HOLD (tp 2.5, 30 min; live)", dict(tp=2.5, sl=None, hold=1790, follow=False)),
       ("FOLLOW (behind its sale, 30 min cap)", dict(tp=None, sl=None, hold=1790, follow=True)),
       ("FOLLOW+TP (behind it, or tp 2.5 first)", dict(tp=2.5, sl=None, hold=1790, follow=True)))
LAND = ((4, "4 after"), (8, "8 after"), ("slot+1", "block late")) if ROUTES != "E" else (("slot+1", "block late"), ("slot+2", "2 blocks late"))
print("\n== our copy, 1 SOL, 2 open, limit 1.25: net SOL (without the best 2), copies, refused; corr = net + gap x copies")
print(f"   {'exit':40s} {'landing':10s} | {'P1 net (w/o 2)':>16s} {'n':>4s} {'ref':>3s} {'corr':>7s} | {'P2 net (w/o 2)':>16s} {'n':>4s} {'ref':>3s} {'corr':>7s}")
SUM = {}
for name, kw in POL:
    for n, ln in LAND:
        cells = []
        for p in ("P1", "P2"):
            k, s, s2, ref = sc(sim(HALF[p], n, **kw)); g = GAP.get(p, GAP.get("both", 0))
            cells.append(f"{s:+7.2f} ({s2:+6.2f}) {k:4d} {ref:3d} {s + g / 100 * k:+7.2f}"); SUM[(name, ln, p)] = (k, s, s2, ref, s + g / 100 * k)
        print(f"   {name:40s} {ln:10s} | " + " | ".join(cells))
# exit grid picked on P1
FOL = {"hold": False, "follow": True, "follow<1.5": 1.5}
grid = [dict(tp=tp, sl=sl, hold=h, follow=FOL[f]) for tp, sl, h, f in itertools.product((1.5, 2.0, 2.5, 3.0, None), (None, 0.5, 0.7), (300, 600, 1790), FOL)]
def ev(kw):
    a = [sc(sim(HALF["P1"], n, **kw)) for n, _ in LAND]; b = [sc(sim(HALF["P2"], n, **kw)) for n, _ in LAND]
    return kw, sum(x[2] for x in a) / len(a), sum(x[1] for x in a) / len(a), sum(x[2] for x in b) / len(b), sum(x[1] for x in b) / len(b), b
res = [ev(kw) for kw in grid]; res.sort(key=lambda r: -r[1])
nm = lambda kw: f"{next(k for k, v in FOL.items() if v == kw['follow']):10s} tp {str(kw['tp']):4s} stop {str(kw['sl']):4s} {kw['hold']:4d}s"
print(f"\n== exit grid ({len(grid)} rule sets), picked on P1 (mean over the landings, without the best 2), scored on P2")
for r in res[:5]:
    print(f"   {nm(r[0]):36s} P1 {r[2]:+6.2f} ({r[1]:+6.2f}) | P2 {r[4]:+6.2f} ({r[3]:+6.2f}) | P2 by landing: "
          + " / ".join(f"{x[1]:+.2f} ({x[2]:+.2f})" for x in r[5]))
best = res[0]
json.dump(dict(W=W, floor=FLOOR, n=len(trips), P1=len(HALF["P1"]), P2=len(HALF["P2"]), gap=GAP, overlap=ov,
               table={"|".join(map(str, k)): v for k, v in SUM.items()}, best=dict(rule=nm(best[0]), p1=best[1:3], p2=best[3:5])),
          open(f"{M.lib.OUT}/copyscore_{W[:8]}_{FLOOR}{'_multi' if MULTI else ''}_{ROUTES}.json", "w"))
