# Is the TAB unit's exit the best? (Nov 18, the owner: "review that our exit rules are the most optimal"). hunt_lib's
# live model with every exit setting free: take profit {2, 3, 4, 6}x, stall {off, 60, 120, 180} s, sell pressure {off,
# 3/30, 5/60, 10/60} (from 30 s), time {300, 600} s, its sale never followed (the deployed rule: tp 4, stall 180, sp
# 5/60, 600 s). TAB16RxX's 140 copies (e3's: all its 0.5+ SOL first buys on the 4 days' float-quote coins, the mean of
# the three landings, 0.0345 SOL a round trip); days 1-2 / 3-4 at Nov 16 01:07 UTC. Picked on days 1-2, scored on 3-4;
# and ranked by the weaker half (a setting that holds on both).
#   python3 -I e4_tab_grid.py SP LAUNCHES,... > ../out/e4_tab_grid.txt
import sys, os, json, gzip, itertools, numpy as np
SP = sys.argv[1]; O = f"{SP}/market"; PD = f"{O}/paths_full"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); import hunt_lib as H
TAB = "TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3"; WSOL = "So11111111111111111111111111111111111111112"; COST = 0.0345 - 0.0026; MID = 1794791222
FLOATS = ("3NZ9JMVB", "pumpCmXq", "SPCXxcqX", "TTWofwAg", "DJTu7vi8", "98sMhvDw", "XsbEhLAt"); L = {}
for f_ in sys.argv[2].split(","): L.update({m: x for m, x in json.load(open(f_)).items() if x and x["quote"][:8] in FLOATS and os.path.exists(f"{PD}/{m}.json.gz")})
PR = json.load(open(f"{O}/prices.json")); su = PR[WSOL]["usdPrice"]; rate = lambda q: PR[q]["usdPrice"] / su * 1e9 / 10 ** PR[q]["decimals"] if q in PR else None
def model(p, tp, hold, sp, stall, stake=0.5):
    """hunt_lib.model with the sell pressure and the stall as settings (the same code otherwise), its sale off."""
    if p["refused"]: return -0.0004
    vt0, vq0, bps0 = p["ent"]; Q = stake * 1e9 * p["hopf"] / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    n = len(p["px"])
    def out(ex):
        if ex is None: vq, vt, b = vq0, vt0, bps0
        else: vq, vt, b = p["vq"][ex], p["vt"][ex], p["bps"][ex]
        vq_r = vq + net_in; vt_r = vt * vq / vq_r
        return (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - b / 1e4) * p["rate"] * p["hopf"] / 1e9 - stake - 0.0026
    if n == 0: return out(None)
    px, age = p["px"], p["age"]; c = []
    i = H.first(p["grad"]); c += [(i, 0)] if i is not None else []
    i = H.first(px >= tp); c += [(i, 1)] if i is not None else []
    if sp:
        nn, w, fr = sp; lo = np.searchsorted(age, age - w, side="left"); s = np.concatenate([[0], np.cumsum(p["osell"])]); b = np.concatenate([[0], np.cumsum(p["obuy"])])
        i = H.first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= nn) & (age >= fr)); c += [(i, 1)] if i is not None else []
    if stall:
        pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); lasthi = np.maximum.accumulate(np.where(newhi, age, -1e9))
        i = H.first((pk >= 1.0) & (age - lasthi >= stall)); c += [(i, 1)] if i is not None else []
    i = H.first(age >= hold); c += [(i, 0)] if i is not None else []
    if not c: return out(n - 1)
    i, d = min(c); return out(min(i + d, n - 1))
TPS = tuple(float(x) for x in os.environ["TPS"].split(",")) if os.environ.get("TPS") else (2, 3, 4, 6)   # TPS=...: a finer take-profit grid
G = list(itertools.product(TPS, (0, 60, 120, 180), (None, (3, 30, 30), (5, 60, 30), (10, 60, 30)), (300, 600))) if not os.environ.get("TPS") else [(t, 180, (5, 60, 30), 600) for t in TPS] + [(t, 60, (5, 60, 30), 600) for t in TPS]
DEP = (4, 180, (5, 60, 30), 600)
P = []
for m, x in L.items():
    r = rate(x["quote"]); tr = json.load(gzip.open(f"{PD}/{m}.json.gz")) if r else []
    i = next((j for j, e in enumerate(tr) if e["user"] == TAB), None)
    if i is None or not tr[i]["buy"] or tr[i]["q"] * (1 + tr[i]["bps"] / 1e4) * r / 1e9 < 0.5 or tr[-1]["t"] - tr[i]["t"] < 600: continue
    P.append((tr[i]["t"], [H.prep(tr, i, r, n) for n in (4, 8, "slot+1")]))
# check: the deployed setting reproduces e3 (hunt_lib.model, early=None)
chk = np.mean([np.mean([H.model(p, early=None)[0] for p in ps]) - COST for t, ps in P])
R = {}
for g in G:
    v = np.array([np.mean([model(p, g[0], g[3], g[2], g[1]) for p in ps]) - COST for t, ps in P]); R[g] = v
T = np.array([t for t, ps in P]); A = T < MID
def st(v):
    s = np.sort(v); k = max(1, round(0.02 * len(v))); return v.mean() / 0.5 * 100, s[:-k].sum()
name = lambda g: f"tp {g[0]}x, stall {g[1] or 'off'}, sp {'off' if not g[2] else f'{g[2][0]}/{g[2][1]}'}, {g[3]} s"
print(f"{len(P)} copies (days 1-2 {A.sum()}, days 3-4 {(~A).sum()}); check: the deployed setting through hunt_lib.model {100 * chk / 0.5:+.1f}% a copy, through this grid {100 * R[DEP].mean() / 0.5:+.1f}%")
rows = []
for g, v in R.items():
    a1, w1 = st(v[A]); a2, w2 = st(v[~A]); aa, wa = st(v)
    rows.append((g, a1, a2, aa, w1, w2, min(a1, a2)))
pos = sum(1 for r in rows if r[1] > 0 and r[2] > 0)
print(f"settings positive on both halves: {pos} of {len(rows)}")
def line(r, tag=""):
    return f"   {name(r[0]):38s} | days 1-2 {r[1]:+6.1f}% (w/o 2% {r[4]:+5.2f}) | days 3-4 {r[2]:+6.1f}% (w/o 2% {r[5]:+5.2f}) | all {r[3]:+6.1f}% {tag}"
dep = next(r for r in rows if r[0] == DEP)
print("\nTHE DEPLOYED SETTING:"); print(line(dep))
rk = sorted(rows, key=lambda r: -r[6]); print(f"   its rank by the weaker half: {1 + rk.index(dep)} of {len(rows)}; by all 4 days: {1 + sorted(rows, key=lambda r: -r[3]).index(dep)}")
print("\nTHE 12 BEST BY THE WEAKER HALF (a setting that holds on both):")
for r in rk[:12]: print(line(r, "<- deployed" if r[0] == DEP else ""))
b1 = max(rows, key=lambda r: r[1]); print("\nPICKED ON DAYS 1-2 ALONE:"); print(line(b1)); print(f"   its days 3-4 rank: {1 + sorted(rows, key=lambda r: -r[2]).index(b1)} of {len(rows)}")
if os.environ.get("TPS"):
    print("\nTAKE PROFIT, FINE (stall 180 / sell pressure 5-60 / 600 s as deployed; then the same with stall 60):")
    for st_ in (180, 60):
        for t in TPS: print(line(next(r for r in rows if r[0] == (t, st_, (5, 60, 30), 600)), "<- deployed" if (t, st_, (5, 60, 30), 600) == DEP else ""))
        print()
    sys.exit()
print("\nONE PART AT A TIME (the others as deployed):")
for lab, gs in (("take profit", [(t, 180, (5, 60, 30), 600) for t in (2, 3, 4, 6)]), ("stall", [(4, s, (5, 60, 30), 600) for s in (0, 60, 120, 180)]),
                ("sell pressure", [(4, 180, s, 600) for s in (None, (3, 30, 30), (5, 60, 30), (10, 60, 30))]), ("time", [(4, 180, (5, 60, 30), h) for h in (300, 600)])):
    print(f"  {lab}:")
    for g in gs: print(line(next(r for r in rows if r[0] == g), "<- deployed" if g == DEP else ""))
