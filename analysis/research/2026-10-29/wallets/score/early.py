# Fresh study: how wallet 4 closed its 1.45+ SOL buys of coins priced in another token (its one-buy one-sell curve trips,
# exitrule.py's _exits.json), by period: at its take profit (marginal multiple >= 2.4x), its stop (<= 0.75x), its
# 30-minute timer (held >= 1790 s), or EARLY (none of the three). The early sells: seconds held, the multiple at the sale,
# its SOL value multiple, the share of its tokens sold, the quote token, the route class (route_cls.py).
# Also every coin it first bought for 1.45+ SOL (any number of trades): its first sale, and whether it sold everything.
#   W=WALLET python3 -I early.py [MIN_SOL]
import sys, os, json, datetime, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from route_q import cls   # score: the route class from the curve's quote token (route_q.py), not wallet 4's own route
SP0 = "/tmp/claude-0/-home-user-rugsnipe/972c43cf-f494-5af4-b87a-fe32117a83be/scratchpad"      # helpers: month/tri.py, rivalpnl
SP = __import__("os").environ.get("SP", "/tmp/claude-0/-home-user-copy2/5735f118-428c-51f1-989c-5d5d23b0b4ec/scratchpad/score")  # score: SP from the environment
W = os.environ.get("W", "H9kuqGKNYgPFYCA17uUTkaqXGum7MK8y1GwbS7cxsjDg")   # score: the wallet from the environment
MIN = float(sys.argv[1]) if len(sys.argv) > 1 else 1.45
R = json.load(open(f"{SP}/h9long/{W[:8]}_exits.json"))
T = {x["m"]: x for x in json.load(open(f"{SP}/h9long/{W[:8]}_trips.json"))}
Q = json.load(open(f"{SP}/h9long/{W[:8]}_quote.json"))
def per(t): return "P1" if datetime.datetime.fromtimestamp(t, datetime.timezone.utc).day <= 22 else "P2" if t < 1793060400 else "P3"
def how(r):
    if r["sec"] < 1790 and r["marg"] >= 2.4: return "tp"
    if r["sec"] < 1790 and r["marg"] <= 0.75: return "stop"
    if r["sec"] >= 1790: return "time"
    return "early"
def q(xs, ps=(10, 25, 50, 75, 90)):
    xs = sorted(xs); return [round(xs[min(len(xs) - 1, int(p / 100 * len(xs)))], 2) for p in ps] if xs else []
rows = [dict(r, per=per(r["bt"]), how=how(r), cls=cls(T[r["m"]]), quote=Q.get(r["m"], "via SOL only"),
             frac=T[r["m"]]["tr"][1]["tok"] / T[r["m"]]["tr"][0]["tok"] if T[r["m"]]["tr"][0]["tok"] else None)
        for r in R if r["kind"] == "pump, other quote" and (r["buy_sol"] or 0) >= MIN]
for name, sel in (("all", lambda r: True), ("routable (route class A, B, C)", lambda r: r["cls"] in "ABC")):
    print(f"\n== its one-buy one-sell trips, {MIN}+ SOL, other quote, {name}: how it sold   [n: tp / stop / time / early (share)]")
    for p in ("P1", "P2", "P3"):
        xs = [r for r in rows if r["per"] == p and sel(r)]; c = collections.Counter(r["how"] for r in xs); n = len(xs) or 1
        print(f"   {p} {len(xs):4d}:  tp {c['tp']:3d} ({100 * c['tp'] / n:4.1f}%)  stop {c['stop']:3d} ({100 * c['stop'] / n:4.1f}%)  "
              f"time {c['time']:3d} ({100 * c['time'] / n:4.1f}%)  early {c['early']:3d} ({100 * c['early'] / n:4.1f}%)   its net {sum(r['net'] for r in xs):+7.2f}"
              f"  (early sells {sum(r['net'] for r in xs if r['how'] == 'early'):+6.2f})")
print(f"\n== the early sells ({MIN}+ SOL, other quote, all routes): p10 p25 p50 p75 p90")
for p in ("P1", "P2", "P3"):
    xs = [r for r in rows if r["per"] == p and r["how"] == "early"]
    print(f"   {p} {len(xs)}: seconds held {q([r['sec'] for r in xs])}  multiple at its sale {q([r['marg'] for r in xs])}"
          f"  SOL value multiple {q([r['val'] for r in xs if r['val']])}  share of its tokens sold {q([r['frac'] for r in xs if r['frac']])}")
    hb = collections.Counter(("<10 s", "10-60 s", "1-5 min", "5-15 min", "15-30 min")[(r["sec"] >= 10) + (r["sec"] >= 60) + (r["sec"] >= 300) + (r["sec"] >= 900)] for r in xs)
    mb = collections.Counter(("0.75-1.0x", "1.0-1.5x", "1.5-2.0x", "2.0-2.4x")[(r["marg"] >= 1.0) + (r["marg"] >= 1.5) + (r["marg"] >= 2.0)] for r in xs)
    print(f"      held: " + "  ".join(f"{k} {hb[k]}" for k in ("<10 s", "10-60 s", "1-5 min", "5-15 min", "15-30 min")))
    print(f"      multiple: " + "  ".join(f"{k} {mb[k]}" for k in ("0.75-1.0x", "1.0-1.5x", "1.5-2.0x", "2.0-2.4x")) + f"   won {sum(r['net'] > 0 for r in xs)}")
    print(f"      quote: " + "  ".join(f"{k} {v}" for k, v in collections.Counter(r["quote"] for r in xs).most_common(8))
          + "   route class: " + "  ".join(f"{k} {v}" for k, v in sorted(collections.Counter(r["cls"] for r in xs).items())))
    for k in ("time", "tp"):
        ys = [r for r in rows if r["per"] == p and r["how"] == k]
        print(f"      for scale, {k}: {len(ys)} quote " + "  ".join(f"{a} {b}" for a, b in collections.Counter(r["quote"] for r in ys).most_common(4)))
# every coin it first bought for MIN+ SOL on the curve, other quote: its first sale and whether it sold everything
print(f"\n== every coin first bought for {MIN}+ SOL (other quote), any number of trades: its first curve sale")
for p in ("P1", "P2", "P3"):
    c = collections.Counter(); early_first = 0; n = 0
    for x in T.values():
        tr = x["tr"]
        if x["kind"] != "pump, other quote" or not tr or not tr[0]["buy"] or (tr[0]["v"] or 0) < MIN or per(tr[0]["bt"]) != p: continue
        n += 1; sells = [t for t in tr if not t["buy"]]; buys = [t for t in tr if t["buy"]]
        c["trades: 1 buy 1 sell" if len(tr) == 2 and len(sells) == 1 else "1 buy, no curve sale" if not sells else f"{len(buys)} buys {len(sells)} sells"] += 1
        if x["open"]: c["still holds some"] += 1
        if sells:
            s = sells[0]; b = tr[0]; sec = s["bt"] - b["bt"]; frac = s["tok"] / sum(t["tok"] for t in buys if t["s"] <= s["s"])
            m = (b["vt"] / (s["vt"] - s["tok"])) ** 2 if s["vt"] - s["tok"] > 0 else 0
            if sec < 1790 and 0.75 < m < 2.4: early_first += 1; c[f"early first sale, sold {'all' if frac > 0.99 else 'part'}"] += 1
    print(f"   {p} {n} coins: " + "  ".join(f"{k} {v}" for k, v in sorted(c.items())) + f"   early first sale {early_first} ({100 * early_first / max(n, 1):.1f}%)")
json.dump([r for r in rows], open(f"{SP}/h9long/{W[:8]}_early.json", "w"))
