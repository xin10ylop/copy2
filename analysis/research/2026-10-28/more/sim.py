# The copy model of ../../2026-10-27/h9long/grid.py (its one() and score(), the cautious price model q + LIFT, its sale
# ahead of ours within a slot, our trigger filled on the next trade, 0.0095 SOL a transaction, the 0.0155 SOL bias),
# importable, with what this study adds: the trips of any band and route class, a quote filter, a stake per trip, an
# extra cost factor per trip (a pool hop in front), a stop per route class, partial exits (a ladder of take profits),
# a take-profit floor after a peak, a landing in its own slot (land=0), and no entry limit. With the defaults it gives
# grid.py's numbers exactly (checked in check.py). DATA=fresh3 reads the other session's re-run to Oct 28 14:54
# (SP/fresh3/h9long, ../fresh/README.md) and splits a third period, P3 = Oct 27 00:20 -> Oct 28 14:54 UTC.
import sys, os, json, datetime, collections
HERE = os.path.dirname(os.path.abspath(__file__))
H9 = os.path.join(HERE, "..", "..", "2026-10-27", "h9long")
sys.path.insert(0, H9)
from route_cls import cls, by as ROWS_BY, rows as ROWS   # noqa: E402  (route_cls reads H9kuqGKN.jsonl)
SP = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"
W = "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg"
WSOL, WBTC = "So11111111111111111111111111111111111111112", "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh"
FEE, BIAS, ITS_TP = 0.0095, 0.0155, 2.5
COST = {"pump, other quote": 0.9487, "pump, SOL quote": 0.9713}
DATA = os.environ.get("DATA", "")
SPD = f"{SP}/{DATA}" if DATA else SP
P3_FROM = 1793060400                                     # Oct 27 00:20 UTC, the end of the 8-day data
P = json.load(open(f"{SPD}/h9long/{W[:8]}_fpaths.json"))
T = {x["m"]: x for x in json.load(open(f"{SPD}/h9long/{W[:8]}_trips.json"))}
Q = json.load(open(f"{SPD}/h9long/{W[:8]}_quote.json"))
R = json.load(open(f"{SP}/h9long/routable.json"))
PERIODS = ("P1", "P2", "P3") if DATA else ("P1", "P2")


def per(t):
    if datetime.datetime.fromtimestamp(t, datetime.timezone.utc).day <= 22: return "P1"
    return "P2" if t < P3_FROM else "P3"


def pay_token(x):
    """The token its buy started from besides the coin and wSOL (None: SOL), as route_cls reads it."""
    r = ROWS_BY.get((x["m"], x["tr"][0]["s"], 1))
    if not r: return "?"
    o = [k for k in r["tok"] if k not in (x["m"], WSOL)]
    return o[0] if o else None


def trips(lo=1.5, hi=9.0, routes="ABC", kind="other", grad=False, nots=()):
    """grid.py's TRIPS: single buy + single sell, its buy lo <= SOL < hi, a path, the route class in `routes`.
    grad (DATA=fresh3 only): also its buys whose coin graduated before it sold, as ../fresh/grid.py GRAD=1 adds them;
    nots: mint prefixes left out (../fresh/grid.py NOT)."""
    out = []
    for m, v in P.items():
        if not v or "path" not in v: continue
        x = T[m]
        if len(x["tr"]) != 2: continue
        its = x["tr"][0]["v"] or 0
        if lo <= its < hi and kind in x["kind"] and cls(x) in routes and not m.startswith(tuple(nots) or ("\0",)):
            out.append((m, x, v["path"]))
    if grad and DATA:
        G = json.load(open(f"{SPD}/h9long/{W[:8]}_gpaths.json"))
        L = {p["m"]: p for p in json.load(open(f"{SPD}/h9long/{W[:8]}_ledger.json"))["pos"]}
        for m, v in G.items():
            x = T[m]; b0 = x["tr"][0]; its = b0["v"] or 0
            if m.startswith(tuple(nots) or ("\0",)) or not (lo <= its < hi and kind in x["kind"] and cls(x) in routes): continue
            sl = next(t for t in L[m]["tr"] if not t[2]); rs = [r for r in v["path"] if (r[0], r[1]) > (b0["s"], b0["i"] or 0)]
            out.append((m, dict(x, tr=[b0, dict(s=sl[0], vt=rs[-1][5], tok=0, bt=sl[1])]), v["path"]))
    return out


KIND = {}


def one(x, path0, tp=2.0, sl=0.8, hold=1790, trail=None, land=1, pmax=None, stake=1.0, cost=1.0, ladder=None,
        floor=None, model="q", lift=True):
    """grid.py's one(): (buy time, close time, result SOL) or None when the entry is refused.
    New: cost multiplies the proceeds (a pool hop's fee and slippage); ladder = [(fraction, tp), ...] sells each part at
    its own take profit (the stop, the time and its own sell close what is left; fractions sum to 1; tp=None: no take
    profit for that part); floor = (arm, level): once the price reached `arm`, sell all if it falls back to `level`."""
    b, s = x["tr"]; its = b["v"]
    vbb, vab = b["vt"] + b["tok"], b["vt"]; Qi = 1 / vab - 1 / vbb
    path = [r for r in path0 if (r[0], r[1]) > (b["s"], b["i"] or 0)]
    last = b["s"] + land
    ahead = [r for r in path if r[0] <= last]; va = ahead[-1][5] if ahead else vab
    if pmax is not None and (vab / va) ** 2 > 1 + pmax:
        return None
    qin = Qi * stake / its; tok = va - 1 / (1 / va + qin)
    rest = [r for r in path if r[0] > last]
    real = (lambda vr: 1 / (1 / vr + qin)) if model == "q" else (lambda vr: vr - tok)
    ck = COST[x["kind"]] * cost
    if ladder is None:
        ladder = [(1.0, tp)]
    # what is left of our position: tokens out of the curve and our net quote in it (the q model generalised to part
    # sales: the curve's quote reserve is the recorded one plus our net quote; its token reserve follows from k = 1)
    st = dict(left=1.0, qnet=qin, got=0.0, sells=0)

    def sell_part(vr, frac):
        """sell `frac` of our first tokens at the recorded state vr; returns nothing, books the quote out"""
        if frac <= 0: return
        if model == "q":
            vx = 1 / (1 / vr + st["qnet"])
        else:
            vx = vr - tok * st["left"]
        if vx <= 0:
            st["left"] -= frac; st["sells"] += 1; return
        out = 1 / vx - 1 / (vx + tok * frac)
        st["got"] += out; st["qnet"] -= out; st["left"] -= frac; st["sells"] += 1

    def result():
        g = st["got"] / qin
        extra = max(0, st["sells"] - 1)          # every sell beyond the first: a transaction and half the bias more
        return stake * (g * ck - 1) - 2 * FEE - BIAS - extra * (FEE + BIAS / 2)

    s_slot, s_after, s_bt = s["s"], s["vt"], s.get("bt")
    if lift:
        for r in rest:
            if r[0] >= s["s"]: break
            if (vab / real(r[5])) ** 2 >= ITS_TP:
                s_slot, s_after, s_bt = r[0], r[5] + b["tok"], r[6]; break
            if r[6] and r[6] - b["bt"] >= 1800: break
    parts = [[f, lv] for f, lv in ladder]         # still to sell: [fraction, its take profit]
    peak = 0.0; tclose = None
    for k, r in enumerate(rest):
        if r[0] > s_slot: break
        px = (vab / r[5]) ** 2; peak = max(peak, px)
        fire_all = None
        if sl and px <= sl: fire_all = "sl"
        elif trail and peak >= trail[0] and px <= peak * (1 - trail[1]): fire_all = "trail"
        elif floor and peak >= floor[0] and px <= floor[1]: fire_all = "floor"
        elif r[6] and r[6] - b["bt"] >= hold: fire_all = "time"
        hit = [p for p in parts if p[1] and px >= p[1]]
        if not fire_all and not hit: continue
        if fire_all:
            frac = sum(p[0] for p in parts); kind = fire_all; parts_now = parts[:]
        else:
            frac = sum(p[0] for p in hit); kind = "tp"; parts_now = hit
        its_first = s_slot <= r[0] + 1
        KIND[x["m"]] = kind if not its_first else kind + ", its sell first"
        if kind == "time" and not its_first:
            nxt = [q for q in rest[k + 1:] if q[0] == r[0] + 1]
            sell_part(nxt[-1][5] if nxt else r[5], frac)
            return b["bt"], b["bt"] + hold, result()
        if its_first:                                # its sale lands first: everything left sells on its state
            sell_part(s_after, sum(p[0] for p in parts))
            return b["bt"], s_bt or r[6], result()
        nxt = [q for q in rest[k + 1:] if q[0] >= r[0] + 1]
        sell_part(nxt[0][5] if nxt else s_after, frac)
        for p in parts_now: parts.remove(p)
        if not parts:
            return b["bt"], r[6] or s_bt, result()
        tclose = r[6] or s_bt
    left = sum(p[0] for p in parts)
    if s_bt and s_bt - b["bt"] >= min(hold, 1790) and s_slot == s["s"]:
        KIND[x["m"]] = "time (its 30-minute sell)"
        sell_part(s["vt"] - s["tok"], left)
        return b["bt"], b["bt"] + min(hold, 1790), result()
    KIND[x["m"]] = "its early sell, we follow" if s_slot == s["s"] else "its 2.5x sell (lift), we follow"
    sell_part(s_after, left)
    return b["bt"], s_bt, result()


def score(TR, cap=3, kw_of=None, **kw):
    """grid.py's score(): copies in buy order, one skipped while `cap` are open. kw_of(m, x) -> per-trip overrides."""
    rows = []
    for m, x, path in TR:
        k2 = dict(kw)
        if kw_of: k2.update(kw_of(m, x) or {})
        if k2.pop("skip", False): continue
        r = one(x, path, **k2)
        if r: rows.append((r[0], r[1] or r[0] + 1800, r[2], m))
    openx, got = [], {p: [] for p in PERIODS}
    for bt, tx, res, m in sorted(rows):
        openx = [e for e in openx if e > bt]
        if len(openx) >= cap: continue
        openx.append(tx); got[per(bt)].append((res, m))
    out = {}
    for p, v in got.items():
        r = sorted((a for a, _ in v), reverse=True)
        out[p] = (len(r), sum(r), sum(r[2:]))
    return out, got


def show(name, sc, w=46):
    print(f"   {name:{w}s} " + "   ".join(f"{p} {sc[p][0]:3d} {sc[p][1]:+6.2f} ({sc[p][2]:+6.2f})" for p in PERIODS if p in sc), flush=True)
