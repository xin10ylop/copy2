# The final review of wallet 4's exits with everything the bot does on Nov 13 together: 0.5 SOL, 2 open, 3-hop coins
# included (one more pool hop each way), the buy limit 1.25. Grid: take profit x timer x the early-sale rule (its sale
# followed at a..b seconds under a price) x a stop. Picked on week 1 (to Nov 5 06:49 UTC; mean of landings 4 / 8 / one
# block late, without the best 2), scored on week 2 (to Nov 12 06:49). Raw model.
#   python3 -I exit_final.py SPD
import sys, os, io, contextlib, json, gzip, itertools
from multiprocessing import Pool
SPD = sys.argv[1]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", SPD]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import exit_search as E
M = E.M; G = E.G
P3 = json.load(gzip.open(f"{SPD}/paths_3hop.json.gz")); G.P.update(P3); H3 = set(P3)
STAKE = 0.5
def model(r, n, tp, hold, early, sl, pmax=1.25):
    key = f"{r['slot']}_{r['mint8']}"; m, tr = G.P[key]
    k = next((i for i, e in enumerate(tr) if e["user"] == M.W4 and e["buy"] and e["slot"] == r["slot"]), None)
    if k is None: return None
    its = tr[k]; vta = its["vt"]; t0 = its["t"]; rate = r["sol"] * 1e9 / (its["q"] * (1 + its["bps"] / 1e4))
    j = k + len([e for e in tr[k + 1:] if e["slot"] <= its["slot"] + 1]) if n == "slot+1" else min(k + n, len(tr) - 1)
    ent = tr[j]; px_in = (vta / ent["vt"]) ** 2
    if px_in > pmax: return (-0.0004, "refused", 0)
    hops = 0.997 if key in H3 else 1.0
    Q = STAKE * 1e9 * (1 - 0.003) * hops / rate; net_in = Q * 1e4 / (1e4 + ent["bps"])
    tok = ent["vt"] - ent["vt"] * ent["vq"] / (ent["vq"] + net_in)
    ex, why = None, "time"
    for i in range(j + 1, len(tr)):
        e = tr[i]; px = (vta / e["vt"]) ** 2; age = e["t"] - t0
        if e.get("real") == 0: why, ex = "graduated", i; break
        if early and e["user"] == M.W4 and not e["buy"] and early[0] <= age < early[1] and px < early[2]: why, ex = "its_sell", min(i + 1, len(tr) - 1); break
        if tp and px >= tp: why, ex = "tp", min(i + 1, len(tr) - 1); break
        if sl and px <= sl: why, ex = "stop", min(i + 1, len(tr) - 1); break
        if age >= hold: why, ex = "time", i; break
    if ex is None: ex = len(tr) - 1
    x = tr[ex]; vq_r = x["vq"] + net_in; vt_r = x["vt"] * x["vq"] / vq_r
    out = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - x["bps"] / 1e4)
    return (out * rate * (1 - 0.003) * hops / 1e9 - STAKE - 0.0026, why, x["t"] - t0)
rows3 = [r for r in json.load(open(f"{SPD}/toolong.json")) if f"{r['slot']}_{r['mint8']}" in P3]
END = max(r["t"] for r in G.trips); MID = END - 7 * 86400
allr = sorted(G.trips + rows3, key=lambda r: r["t"])
WK = [[r for r in allr if r["t"] < MID], [r for r in allr if MID <= r["t"] <= END]]
def sim(rs, n, kw):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x > r["t"]]
        if len(open_) >= 2: continue
        o = model(r, n, **kw)
        if o is None: continue
        if o[1] != "refused": open_.append(r["t"] + o[2])
        out.append(o[0])
    v = sorted(out, reverse=True); return sum(v), sum(v[2:])
EARLY = {"never": None, "30-180<1.5 (live)": (30, 180, 1.5), "0-180<1.5": (0, 180, 1.5), "30-240<1.5": (30, 240, 1.5), "30-180 any": (30, 180, 1e9), "0-300<1.0": (0, 300, 1.0)}
GRID = [dict(tp=tp, hold=h, early=EARLY[e], sl=sl) for tp, h, e, sl in itertools.product((2.0, 2.2, 2.4, 2.6, 3.0), (300, 600, 1200, 1790), EARLY, (None, 0.5))]
def ev(kw):
    w = [[sim(W, n, kw) for n in E.LAND] for W in WK]
    return kw, tuple((sum(a for a, _ in x) / 3, sum(b for _, b in x) / 3) for x in w)
if __name__ == "__main__":
    with Pool(4) as p: R = p.map(ev, GRID)
    en = lambda kw: next(k for k, v in EARLY.items() if v == kw["early"])
    lab = lambda kw: f"tp {kw['tp']:<3} {kw['hold']:>4}s early {en(kw):18s} stop {str(kw['sl']):4s}"
    row = lambda r: print(f"   {lab(r[0])} | {r[1][0][0]:+6.2f} ({r[1][0][1]:+6.2f}) | {r[1][1][0]:+6.2f} ({r[1][1][1]:+6.2f}) | {r[1][0][0]+r[1][1][0]:+6.2f} ({r[1][0][1]+r[1][1][1]:+6.2f})")
    live = next(r for r in R if r[0] == dict(tp=2.4, hold=1790, early=(30, 180, 1.5), sl=None))
    print(f"{len(R)} rule sets; 0.5 SOL, 2 open, 3-hop coins in; raw; week 1 (w/o best 2) | week 2 (w/o best 2) | both")
    print("== live"); row(live)
    R.sort(key=lambda r: -r[1][0][1])
    print("== the 10 best on week 1 (without its best 2), with their week 2")
    for r in R[:10]: row(r)
    both = [r for r in R if r[1][0][1] > live[1][0][1] and r[1][1][1] > live[1][1][1]]
    print(f"== beat live in BOTH weeks without the best 2: {len(both)} of {len(R)}")
    for r in sorted(both, key=lambda r: -(r[1][0][1] + r[1][1][1]))[:8]: row(r)
    print("== each choice on its own: mean over every rule set with it, week 1 / week 2 (without the best 2)")
    for key, vals, f in (("tp", (2.0, 2.2, 2.4, 2.6, 3.0), str), ("hold", (300, 600, 1200, 1790), str), ("early", list(EARLY.values()), lambda v: next(k for k, x in EARLY.items() if x == v)), ("sl", (None, 0.5), str)):
        print(f"   {key:5s}: " + "   ".join(f"{f(v)} {sum(r[1][0][1] for r in R if r[0][key] == v)/sum(1 for r in R if r[0][key] == v):+.2f} / {sum(r[1][1][1] for r in R if r[0][key] == v)/sum(1 for r in R if r[0][key] == v):+.2f}" for v in vals))
