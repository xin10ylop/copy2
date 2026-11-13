# TAB16RxX's exits, on exactly the buys the bot takes: the bot's own detection and route planner (examples/scan.rs,
# W=TAB16RxX, min_sol 1.0, 3-hop routes in) over its landed transactions Oct 29 12:02 - Nov 12 06:49 UTC, each coin's
# path (31 minutes, block order; cmodel.path), then a grid: take profit x timer x how its own sale is treated (never
# followed, always, or only when it comes a..b seconds after its buy and under a price) x a stop. STAKE SOL (0.1 as
# live), 2 open, the buy limit 1.25, one more pool hop each way charged on 3-hop routes. Picked on week 1 (to Nov 5
# 06:49; mean of landings 4 / 8 / one block late, without the best 2), scored on week 2. Corrected = raw + gap x
# stake x copies, the gap measured on TAB16RxX itself by the lookalike study (+10.5 points week 1, +8.5 week 2).
#   RPC_URL=... LK=<cache dir> [STAKE=0.1] python3 -I tab_grid.py TXDIR SIGS.json SCAN_OUT
import sys, os, json, re, glob, itertools
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import cmodel as M
W = "TAB16RxXmazWzCTpJbnKiREWUybdEoskuyidaV291u3"
PA, PB, PC = 1793275320, 1793861340, 1794466140; GAP = (0.105, 0.085); STAKE = float(os.environ.get("STAKE", "0.1"))
TXDIR, SIGS, SCAN = sys.argv[1:4]
def load():
    sigs = sorted(json.load(open(SIGS)), key=lambda s: s[2])
    byslot = {}
    for f in glob.glob(f"{TXDIR}/*.json"): byslot.setdefault(int(os.path.basename(f).split("_")[0]), []).append(f)
    rows, why = [], {}
    for l in open(SCAN):
        m = re.match(r"(\d+) (\S{8}) ([\d.]+) SOL from (\S+) quote (\S+) jupiter (\S+): (ROUTABLE|no route)(.*)", l)
        if not m:
            if "unpriced" in l: why["unpriced"] = why.get("unpriced", 0) + 1
            continue
        v = "ROUTABLE" if m.group(7) == "ROUTABLE" else re.sub(r"\(.*", "", m.group(8).strip(": "))
        why[v] = why.get(v, 0) + 1
        if v != "ROUTABLE": continue
        slot, m8 = int(m.group(1)), m.group(2); mint = t0 = None
        for f in byslot.get(slot, []):
            t = json.load(open(f))
            mint = next((b["mint"] for b in t["meta"].get("postTokenBalances") or [] if b.get("owner") == W and b["mint"].startswith(m8)), None)
            if mint: t0 = t["blockTime"]; break
        if mint and PA <= t0 < PC:
            rows.append(dict(m=mint, slot=slot, t=t0, sol=float(m.group(3)), frm=m.group(4), hops=m.group(8).count("venue:")))
    seen, uniq = set(), []
    for r in sorted(rows, key=lambda r: r["t"]):               # the bot skips its second buy of a coin
        if r["m"] not in seen: seen.add(r["m"]); uniq.append(r)
    anchor = lambda t: next((s[0] for s in sigs if s[2] >= t + 1880), sigs[-1][0])
    def getp(r):
        try: r["tr"] = M.path(r["m"], r["slot"], anchor(r["t"]), threads=6)
        except Exception as e: r["tr"] = None; print("path failed", r["m"][:8], str(e)[:60], flush=True)
        return r
    with ThreadPoolExecutor(4) as ex: uniq = list(ex.map(getp, uniq))
    return [r for r in uniq if r["tr"] and M.its_buy(W, r, r["tr"]) is not None], why
ROWS, WHY = load()
WK = [[r for r in ROWS if r["t"] < PB], [r for r in ROWS if r["t"] >= PB]]
def model(r, n, tp, hold, fol, sl, pmax=1.25):
    tr = r["tr"]; k = M.its_buy(W, r, tr); its = tr[k]; vta = its["vt"]; t0 = its["t"]
    rate = r["sol"] * 1e9 / (its["q"] * (1 + its["bps"] / 1e4))
    j = k + len([e for e in tr[k + 1:] if e["slot"] <= its["slot"] + 1]) if n == "slot+1" else min(k + n, len(tr) - 1)
    ent = tr[j]; px_in = (vta / ent["vt"]) ** 2
    if px_in > pmax: return (-0.0004, "refused", 0)
    hops = 0.997 ** max(0, r["hops"] - 2)
    Q = STAKE * 1e9 * (1 - 0.003) * hops / rate; net_in = Q * 1e4 / (1e4 + ent["bps"])
    tok = ent["vt"] - ent["vt"] * ent["vq"] / (ent["vq"] + net_in)
    ex, why = None, "time"
    for i in range(j + 1, len(tr)):
        e = tr[i]; px = (vta / e["vt"]) ** 2; age = e["t"] - t0
        if e.get("real") == 0: why, ex = "graduated", i; break
        if fol and e["user"] == W and not e["buy"] and fol[0] <= age < fol[1] and px < fol[2]: why, ex = "its_sell", min(i + 1, len(tr) - 1); break
        if tp and px >= tp: why, ex = "tp", min(i + 1, len(tr) - 1); break
        if sl and px <= sl: why, ex = "stop", min(i + 1, len(tr) - 1); break
        if age >= hold: why, ex = "time", i; break
    if ex is None: ex = len(tr) - 1
    x = tr[ex]; vq_r = x["vq"] + net_in; vt_r = x["vt"] * x["vq"] / vq_r
    out = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - x["bps"] / 1e4)
    return (out * rate * (1 - 0.003) * hops / 1e9 - STAKE - 0.0026, why, x["t"] - t0)
def sim(rs, n, kw):
    out, open_ = [], []
    for r in rs:
        open_ = [x for x in open_ if x > r["t"]]
        if len(open_) >= 2: continue
        o = model(r, n, **kw)
        if o[1] != "refused": open_.append(r["t"] + o[2])
        out.append(o)
    v = sorted((o[0] for o in out), reverse=True)
    return sum(v), sum(v[2:]), sum(1 for o in out if o[1] != "refused")
LAND = (4, 8, "slot+1")
FOL = {"never (live)": None, "always": (0, 1e9, 1e9), "always <1.5x": (0, 1e9, 1.5), "0-60 s": (0, 60, 1e9), "0-120 s": (0, 120, 1e9),
       "0-60 s <1.5x": (0, 60, 1.5), "0-240 s <1.5x": (0, 240, 1.5)}
GRID = [dict(tp=tp, hold=h, fol=FOL[f], sl=sl) for tp, h, f, sl in
        itertools.product((1.5, 2.0, 2.5, 3.0, 4.0, None), (60, 120, 180, 210, 300, 600, 1790), FOL, (None, 0.5))]
def ev(kw):
    w = [[sim(Wk, n, kw) for n in LAND] for Wk in WK]
    return kw, tuple((sum(a[0] for a in x) / 3, sum(a[1] for a in x) / 3, sum(a[2] for a in x) / 3) for x in w)
if __name__ == "__main__":
    print(f"scan verdicts of its 1.0+ SOL buys (all dates): {WHY}")
    print(f"copyable first buys with its buy on the path: {len(ROWS)} (week 1 {len(WK[0])}, week 2 {len(WK[1])}); 3-hop {sum(r['hops'] >= 3 for r in ROWS)}, from WBTC {sum(r['frm'] == '3NZ9JMVB' for r in ROWS)}")
    hs = sorted(next((e["t"] - r["tr"][M.its_buy(W, r, r["tr"])]["t"] for e in r["tr"][M.its_buy(W, r, r["tr"]) + 1:] if e["user"] == W and not e["buy"]), 9999) for r in WK[1])
    print(f"its first sale after its buy, week 2: p25 / median / p75 {hs[len(hs)//4]} / {hs[len(hs)//2]} / {hs[3*len(hs)//4]} s; under 60 s on {sum(h < 60 for h in hs)} of {len(hs)}")
    with Pool(4) as p: R = p.map(ev, GRID)
    fn = lambda kw: next(k for k, v in FOL.items() if v == kw["fol"])
    lab = lambda kw: f"tp {str(kw['tp']):4s} {kw['hold']:>4}s follow {fn(kw):14s} stop {str(kw['sl']):4s}"
    corr = lambda r, i: r[1][i][0] + GAP[i] * STAKE * r[1][i][2]
    row = lambda r: print(f"   {lab(r[0])} | {r[1][0][0]:+6.3f} ({r[1][0][1]:+6.3f}) {corr(r,0):+6.3f} | {r[1][1][0]:+6.3f} ({r[1][1][1]:+6.3f}) {corr(r,1):+6.3f} | {corr(r,0)+corr(r,1):+6.3f}")
    print(f"\n{len(R)} rule sets; {STAKE} SOL, 2 open; week 1 raw (w/o best 2) corrected | week 2 raw (w/o best 2) corrected | both corrected")
    live = next(r for r in R if r[0] == dict(tp=3.0, hold=300, fol=None, sl=None))
    print("== live"); row(live)
    R.sort(key=lambda r: -r[1][0][1])
    print("== the 10 best on week 1 (without its best 2), with their week 2")
    for r in R[:10]: row(r)
    both = [r for r in R if r[1][0][1] > live[1][0][1] and r[1][1][1] > live[1][1][1]]
    print(f"== beat live in BOTH weeks without the best 2: {len(both)} of {len(R)}")
    for r in sorted(both, key=lambda r: -(r[1][0][1] + r[1][1][1]))[:10]: row(r)
    print("== each choice on its own: mean over every rule set with it, week 1 / week 2 (raw, without the best 2)")
    for key, vals, f in (("tp", (1.5, 2.0, 2.5, 3.0, 4.0, None), str), ("hold", (60, 120, 180, 210, 300, 600, 1790), str),
                         ("fol", list(FOL.values()), lambda v: next(k for k, x in FOL.items() if x == v)), ("sl", (None, 0.5), str)):
        print(f"   {key:5s}: " + "   ".join(f"{f(v)} {sum(r[1][0][1] for r in R if r[0][key] == v)/sum(1 for r in R if r[0][key] == v):+.3f} / {sum(r[1][1][1] for r in R if r[0][key] == v)/sum(1 for r in R if r[0][key] == v):+.3f}" for v in vals))
