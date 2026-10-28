# The long copy's settings tested together under the strict fills of band.py (its sale placed ahead of ours within a
# slot, our trigger filled on the next trade, the cautious price model q + LIFT by default): exits (take profit, stop,
# trailing stop, hold), the entry premium limit, a later landing, and the result by quote token. Every grid is picked
# on Oct 19-22 (P1, without its best 2 copies) and scored on Oct 23-27 (P2); at most 3 open.
#   W=WALLET CAP=4 python3 -I grid.py exits|stops|tp|cap|mix|days|premium|land|quote [MODEL LIFT] [LO HI]   (ROUTES=BC: only the WBTC routes, A: only SOL)
import sys, json, datetime, collections, itertools, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from route_q import cls   # score: the route class from the curve's quote token (route_q.py), not wallet 4's own route
SP0 = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"      # helpers: month/tri.py, rivalpnl
SP = __import__("os").environ.get("SP", "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/score")  # score: SP from the environment
W = os.environ.get("W", "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg")   # score: the wallet from the environment
WHAT = sys.argv[1]
MODEL = sys.argv[2] if len(sys.argv) > 2 else "q"
LIFT = (sys.argv[3] if len(sys.argv) > 3 else "1") == "1"
LO, HI = (float(sys.argv[4]), float(sys.argv[5])) if len(sys.argv) > 5 else (1.5, 9.0)
FEE, BIAS, ITS_TP = 0.0095, 0.0155, 2.5
ITS_TP = float(os.environ.get("ITS_TP", ITS_TP))   # score: the wallet's own take profit for the lift (wallet 4: 2.5)
FEE, BIAS = float(os.environ.get("FEE", FEE)), float(os.environ.get("BIAS", BIAS))   # fresh study: paper's costs to compare
COST = {"pump, other quote": float(os.environ.get("COSTO", 0.9487)), "pump, SOL quote": 0.9713}
CAP = int(os.environ.get("CAP", "3"))   # fresh study: the cap of "as built" and every grid (the bot runs 4)
P = json.load(open(f"{SP}/h9long/{W[:8]}_fpaths.json"))
T = {x["m"]: x for x in json.load(open(f"{SP}/h9long/{W[:8]}_trips.json"))}
Q = json.load(open(f"{SP}/h9long/{W[:8]}_quote.json"))
TRIPS = []
for m, v in P.items():
    if not v or "path" not in v: continue
    x = T[m]
    if len(x["tr"]) != 2:
        # score: MULTI=1 copies a coin it bought once and sold in parts as one trip from its buy to its LAST sale (its earlier
        # partial sales are trades on the recorded path)
        if os.environ.get("MULTI") == "1" and x["tr"][0]["buy"] and not x["tr"][-1]["buy"] and sum(t["buy"] for t in x["tr"]) == 1:
            x = dict(x, tr=[x["tr"][0], x["tr"][-1]])
        else: continue
    its = x["tr"][0]["v"] or 0
    if LO <= its < HI and "other" in x["kind"] and cls(x) in os.environ.get("ROUTES", "ABC"):
        TRIPS.append((m, x, v["path"]))
# fresh study: NOT = mint prefixes to leave out (comma list: coins the bot itself refused, e.g. AvcwGFaF, 2FSWwQwj: 3 hops);
# GRAD=1 adds its buys whose coin graduated before it sold (grad.py, grad_paths.py: _gpaths.json), its sell = its real
# sale after graduation (slot and time from the ledger, state = the last curve trade)
NOT = tuple(p for p in os.environ.get("NOT", "").split(",") if p)
TRIPS = [t for t in TRIPS if not t[0].startswith(NOT or ("\0",))]
if os.environ.get("GRAD") == "1":
    _G = json.load(open(f"{SP}/h9long/{W[:8]}_gpaths.json"))
    _L = {p["m"]: p for p in json.load(open(f"{SP}/h9long/{W[:8]}_ledger.json"))["pos"]}
    for m, v in _G.items():
        x = T[m]; b0 = x["tr"][0]; its = b0["v"] or 0
        if m.startswith(NOT or ("\0",)) or not (LO <= its < HI and "other" in x["kind"] and cls(x) in os.environ.get("ROUTES", "ABC")): continue
        sl = next(t for t in _L[m]["tr"] if not t[2]); rs = [r for r in v["path"] if (r[0], r[1]) > (b0["s"], b0["i"] or 0)]
        TRIPS.append((m, dict(x, tr=[b0, dict(s=sl[0], vt=rs[-1][5], tok=0, bt=sl[1])]), v["path"]))
def per(t): return "P1" if datetime.datetime.fromtimestamp(t, datetime.timezone.utc).day <= 22 else "P2" if t < 1793060400 else "P3"

KIND = {}
FILL = {}
ENTRY = {}


def one(x, path0, tp=2.0, sl=0.8, hold=1790, trail=None, land=1, pmax=None, stake=float(os.environ.get("STAKE", 1.0))):   # score: STAKE
    """(buy time, close time, result SOL) or None when the entry is refused; KIND[mint] = the exit that closed it."""
    b, s = x["tr"]; its = b["v"]
    vbb, vab = b["vt"] + b["tok"], b["vt"]; Qi = 1 / vab - 1 / vbb
    path = [r for r in path0 if (r[0], r[1]) > (b["s"], b["i"] or 0)]
    last = b["s"] + land
    ahead = [r for r in path if r[0] <= last]; va = ahead[-1][5] if ahead else vab
    ENTRY[x["m"]] = (vab / va) ** 2               # fresh study: our entry against its price
    if pmax is not None and (vab / va) ** 2 > 1 + pmax:
        return None
    qin = Qi * stake / its; tok = va - 1 / (1 / va + qin)
    rest = [r for r in path if r[0] > last]
    real = (lambda vr: 1 / (1 / vr + qin)) if MODEL == "q" else (lambda vr: vr - tok)
    def sell(vr):
        FILL[x["m"]] = (vab / vr) ** 2           # fresh study: the recorded price multiple our sale fills at
        vx = real(vr)
        if vx <= 0: return -stake
        g = (1 / vx - 1 / (vx + tok)) / qin
        return stake * (g * COST[x["kind"]] - 1) - 2 * FEE - BIAS
    s_slot, s_after, s_bt = s["s"], s["vt"], s.get("bt")
    if LIFT:
        for r in rest:
            if r[0] >= s["s"]: break
            if (vab / real(r[5])) ** 2 >= ITS_TP:
                s_slot, s_after, s_bt = r[0], r[5] + b["tok"], r[6]; break
            if r[6] and r[6] - b["bt"] >= 1800: break
    peak = 0.0
    for k, r in enumerate(rest):
        if r[0] > s_slot: break
        px = (vab / r[5]) ** 2; peak = max(peak, px)
        if tp and px >= tp: kind = "tp"
        elif sl and px <= sl: kind = "sl"
        elif trail and peak >= trail[0] and px <= peak * (1 - trail[1]): kind = "trail"
        elif r[6] and r[6] - b["bt"] >= hold: kind = "time"
        else: continue
        KIND[x["m"]] = kind if not s_slot <= r[0] + 1 else kind + ", its sell first"
        if kind == "time" and not s_slot <= r[0] + 1:
            nxt = [q for q in rest[k + 1:] if q[0] == r[0] + 1]
            return b["bt"], b["bt"] + hold, sell(nxt[-1][5] if nxt else r[5])
        if s_slot <= r[0] + 1:
            return b["bt"], s_bt or r[6], sell(s_after)
        nxt = [q for q in rest[k + 1:] if q[0] >= r[0] + 1]
        return b["bt"], r[6] or s_bt, sell(nxt[0][5] if nxt else s_after)
    if s_bt and s_bt - b["bt"] >= min(hold, 1790) and s_slot == s["s"]:
        KIND[x["m"]] = "time (its 30-minute sell)"
        return b["bt"], b["bt"] + min(hold, 1790), sell(s["vt"] - s["tok"])
    # no rule of ours fired before its own sell: the path ends there, so we sell right after it (the engine must follow)
    KIND[x["m"]] = "its early sell, we follow" if s_slot == s["s"] else "its 2.5x sell (lift), we follow"
    return b["bt"], s_bt, sell(s_after)

def score(cap=CAP, **kw):
    rows = []
    for m, x, path in TRIPS:
        r = one(x, path, **kw)
        if r: rows.append((r[0], r[1] or r[0] + 1800, r[2], m))
    openx, got = [], {"P1": [], "P2": [], "P3": []}
    for bt, tx, res, m in sorted(rows):
        openx = [e for e in openx if e > bt]
        if len(openx) >= cap: continue
        openx.append(tx); got[per(bt)].append((res, m))
    out = {}
    for p, v in got.items():
        r = sorted((a for a, _ in v), reverse=True)
        out[p] = (len(r), sum(r), sum(r[2:]))
    return out, got

def show(name, sc):
    a, b, c = sc["P1"], sc["P2"], sc["P3"]
    print(f"   {name:44s} P1 {a[0]:3d} {a[1]:+6.2f} ({a[2]:+6.2f})   P2 {b[0]:3d} {b[1]:+6.2f} ({b[2]:+6.2f})   P3 {c[0]:3d} {c[1]:+6.2f} ({c[2]:+6.2f})")

print(f"{len(TRIPS)} routable buys of {LO}-{HI} SOL, model {MODEL}, its exits see our tokens {LIFT}, at most {CAP} open")
show("as built: tp 2.0 sl 0.8 1790 s", score()[0])
if WHAT == "exits":
    res = []
    for tp, sl, hold in itertools.product((1.5, 1.75, 2.0, 2.25, None), (0.6, 0.7, 0.75, 0.8, 0.85, 0.9, None),
                                          (600, 1200, 1790)):
        res.append((f"tp {tp} sl {sl} {hold} s", score(tp=tp, sl=sl, hold=hold)[0]))
    for a, f, sl in itertools.product((1.3, 1.5, 1.75, 2.0), (0.15, 0.25, 0.35), (0.8, None)):
        res.append((f"trail from {a}x -{f:.0%}, sl {sl}, 1790 s", score(tp=None, sl=sl, trail=(a, f))[0]))
    print("   best 15 on P1 (without its best 2):")
    for name, sc in sorted(res, key=lambda r: -r[1]["P1"][2])[:15]:
        show(name, sc)
    rank = sorted(res, key=lambda r: -r[1]["P1"][2])
    i = next(k for k, (n, _) in enumerate(rank) if n == "tp 2.0 sl 0.8 1790 s")
    print(f"   the built rule ranks {i + 1} of {len(rank)} on P1; on P2 it ranks "
          f"{1 + sorted(res, key=lambda r: -r[1]['P2'][2]).index(rank[i])}")
elif WHAT == "stops":
    for sl in (0.75, 0.8, 0.85, 0.9):
        show(f"tp 2.0 sl {sl} 1790 s", score(sl=sl)[0])
elif WHAT == "tp":
    # take profit from 1.1x up, at the built stop and hold, and with a tighter stop; won = closed above zero
    for sl in (0.8, 0.9):
        for tp in (1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.75, 2.0, 2.25, 2.5, 3.0, None):
            sc, got = score(tp=tp, sl=sl)
            won = "  ".join(f"{p} won {sum(r > 0 for r, _ in got[p])}/{len(got[p])}" for p in ("P1", "P2", "P3"))
            show(f"tp {tp} sl {sl} 1790 s", sc)
            print(f"   {'':44s} {won}")
elif WHAT == "mix":
    # what closed each copy as built, and what it made: the rows "we follow" are copies the backtest sells right after
    # the wallet's own sell (no price path after it)
    _, got = score()
    for p in ("P1", "P2", "P3"):
        g = collections.defaultdict(list)
        for res, m in got[p]: g[KIND.get(m, "?")].append(res)
        print(f"   {p}:")
        for k, v in sorted(g.items(), key=lambda kv: -len(kv[1])):
            print(f"     {k:34s} {len(v):4d} copies  {sum(v):+7.2f} SOL  mean {sum(v) / len(v):+.3f}")
elif WHAT == "cap":
    # positions open at once (each takes 1 SOL): the bankroll the cap needs against what it adds
    for cap in (1, 2, 3, 4, 5, 7, 10, 99):
        show(f"at most {cap} open", score(cap=cap)[0])
elif WHAT == "days":
    _, got = score()
    for p in ("P1", "P2", "P3"):
        g = collections.defaultdict(list)
        for res, m in got[p]:
            g[datetime.datetime.fromtimestamp(T[m]["tr"][0]["bt"], datetime.timezone.utc).strftime("%m-%d")].append(res)
        print(f"   {p}: " + "  ".join(f"{d} {len(v)} {sum(v):+.2f}" for d, v in sorted(g.items())))
elif WHAT == "premium":
    for pm in (None, 0.5, 0.25, 0.15, 0.10, 0.07, 0.05, 0.03):
        show(f"entry at most {pm} over its price", score(pmax=pm)[0])
elif WHAT == "land":
    for land in (1, 2, 3, 5, 10):
        show(f"landing {land} slot(s) after its slot", score(land=land)[0])
elif WHAT == "quote":
    _, got = score()
    for p in ("P1", "P2", "P3"):
        g = collections.defaultdict(list)
        for res, m in got[p]: g[Q.get(m, "?")].append(res)
        print(f"   {p}: " + "  ".join(f"{q} {len(v)} {sum(v):+.2f}" for q, v in sorted(g.items(), key=lambda kv: -len(kv[1]))[:8]))
elif WHAT == "paper":
    # fresh study: the paper run (paper.tsv, the owner's paste of history.py paper, Oct 28) against the backtest on the same
    # coins: one() as built (tp 2.0, sl 0.8, 1790 s, landing at its slot + 1), no cap, no route or size filter; also with
    # the bot's 25% price limit (pmax 0.25). Its own trip: SOL, route class, seconds to its sell, the multiple at its sell.
    import datetime as _dt
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "paper.tsv")) if l.strip() and not l.startswith("#")]
    sp = sb = sb25 = 0.0; nb = 0
    print(f"   {'#':>2s} {'bought UTC':11s} {'coin':8s} {'paper exit':10s} {'paper':>8s} | {'model':>8s} {'pmax.25':>8s}  {'model exit':34s} | its: SOL rt   sec  mult")
    for no, bought, its_sol, route, state, ex, peak, held, net, m in rows:
        utc = (_dt.datetime.strptime(bought, "%Y-%m-%d %H:%M:%S") - _dt.timedelta(hours=2)).strftime("%d %H:%M:%S")
        x, v = T.get(m), P.get(m)
        TD = {mm: (xx, pp) for mm, xx, pp in TRIPS}
        if m in TD and len(T[m]["tr"]) == 1:          # GRAD=1: a coin that graduated before its sale, its pseudo trip
            x, v = TD[m][0], dict(path=TD[m][1])
        pnet = float(net) if state == "closed" else None
        if not x or len(x["tr"]) != 2 or not v or "path" not in v:
            why = "not in its trips" if not x else f"{len(x['tr'])} curve trades, no path" if len(x["tr"]) != 2 else "no path fetched"
            print(f"   {no:>2s} {utc:11s} {m[:8]} {ex:10s} {net:>8s} | {why}"); continue
        b, s = x["tr"]
        r = one(x, v["path"]); k = KIND.get(m, "?"); fx = FILL.get(m, 0); en = ENTRY.get(m, 0); r25 = one(x, v["path"], pmax=0.25)
        mult = (b["vt"] / (s["vt"] - s["tok"])) ** 2 if s["vt"] - s["tok"] > 0 else 0   # graduated: the last curve state
        res, res25 = r[2] if r else None, (r25[2] if r25 else 0.0)
        print(f"   {no:>2s} {utc:11s} {m[:8]} {ex:10s} {net:>8s} | {res:+8.4f} {res25:+8.4f}  {k:34s} | {b['v']:.3f} {cls(x)} {s['bt'] - b['bt']:5d} {mult:5.2f}x | we buy at {en:.3f}x, sell at {fx:.2f}x")
        if pnet is not None:
            sp += pnet; sb += res; nb += 1
        sb25 += res25
    print(f"   closed in paper and modelled: {nb}, paper {sp:+.4f}, model {sb:+.4f}; model with the price limit over every row {sb25:+.4f}")
elif WHAT == "grad":
    # fresh study: its 1.45+ buys whose coin graduated before it sold (grad.py, grad_paths.py -> _gpaths.json), which no
    # other mode sees. one() as built, no cap, on the curve path up to the migration; its sell = its real sale (on
    # PumpSwap after graduation: slot and time from the ledger, state = the last curve trade). Run with LIFT 1 and 0: it did
    # not sell on the curve at 2.5x, so the lift's premise fails here.
    G = json.load(open(f"{SP}/h9long/{W[:8]}_gpaths.json"))
    L = {p["m"]: p for p in json.load(open(f"{SP}/h9long/{W[:8]}_ledger.json"))["pos"]}
    tot = collections.defaultdict(list)
    for m, v in G.items():
        x = T[m]; b = x["tr"][0]; path = v["path"]
        sl = next(t for t in L[m]["tr"] if not t[2])
        rs = [r for r in path if (r[0], r[1]) > (b["s"], b["i"] or 0)]
        s = dict(s=sl[0], vt=rs[-1][5], tok=0, bt=sl[1])
        r = one(dict(x, tr=[b, s]), path); k = KIND.get(m, "?")
        top = (b["vt"] / min(q[5] for q in rs)) ** 2
        fire = next((i for i, q in enumerate(rs) if q[0] > b["s"] + 1 and (b["vt"] / q[5]) ** 2 >= 2.0), None)
        c = cls(x); tot[(per(b["bt"]), c in "ABC")].append(r[2])
        print(f"   {per(b['bt'])} {m[:8]} route {c} its {b['v']:.3f}  model {r[2]:+.4f}  {k:32s} curve top {top:5.2f}x  "
              f"2.0x on trade {fire} of {len(rs)} after its buy  its net {x['net']:+.3f}")
    for k in sorted(tot): print(f"   {k[0]} {'routable (A B C)' if k[1] else 'class E'}: {len(tot[k])} copies {sum(tot[k]):+.4f}")
elif WHAT == "list":
    # fresh study: every copy the capped score kept in P3, in buy order (time UTC, coin, route class, result, what closed it)
    _, got = score()
    for res, m in sorted(got["P3"], key=lambda z: T[z[1]]["tr"][0]["bt"]):
        b = T[m]["tr"][0]
        print(f"   {datetime.datetime.fromtimestamp(b['bt'], datetime.timezone.utc):%m-%d %H:%M:%S}  {m[:8]}  {cls(T[m])}  its {b['v']:.3f}  {res:+.4f}  {KIND.get(m, '?')}")
elif WHAT == "itsown":
    # fresh study: the wallet's own result (ledger.py) on the coins the capped copy kept, against the copy's, per period
    _, got = score()
    for p in ("P1", "P2", "P3"):
        print(f"   {p}: {len(got[p])} copies, ours {sum(r for r, _ in got[p]):+.2f}, its own on the same coins {sum(T[m]['net'] for _, m in got[p]):+.2f}")
