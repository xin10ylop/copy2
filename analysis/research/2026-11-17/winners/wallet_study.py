# One wallet studied on its own (the owner, Nov 17: "the logic study of each wallet, same way we did for wallet 4 ... you
# cannot set our bot's filters directly on it"). Up to N of its buys since Nov 3 (w4_history.py's RES file: copyable
# buys, 0.2+ SOL, any curve stage), a random sample (seed 7), each copied one slot after it (hunt_lib.prep, refused past
# 1.25x of its price) on the coin's curve trades (w5_copy's cpaths cache, HOLD s after its buy). Per copy: what it was (its
# size, the quote, the curve sold, the hour, how long the wallet held before its first sale) and what each exit of a wide
# menu makes, a menu that is not our bot's (sim(): no hidden exit): follow its sale (any time); take profit
# 1.3/1.5/2/3/5x (of its price); sell at 1/2/5/10/30 min; trailing stops; sell pressure at three settings. Rows -> SP/winners/study_<w8>.json for the analysis.
#   RPC_URL=... python3 -I wallet_study.py SP WALLET8 [N=300] [HOLD=1800]
import sys, os, json, time, random, numpy as np
SP, W8 = sys.argv[1], sys.argv[2]; N = int(sys.argv[3]) if len(sys.argv) > 3 else 300; os.environ["HOLD"] = sys.argv[4] if len(sys.argv) > 4 else "1800"
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "w5_copy.py")).read().split("EX = [")[0]   # its cpath(), rate_of(), H, M
sys.argv = ["x", SP, W8]; ns = {"__file__": os.path.join(here, "w5_copy.py")}; exec(compile(src, "w5_copy.py", "exec"), ns)
cpath, rate_of, H = ns["cpath"], ns["rate_of"], ns["H"]
res = json.load(open(os.environ.get("RES", f"{SP}/winners/w4_res.json"))); full = next(k for k in res if k.startswith(W8))
h = json.load(open(f"{SP}/winners/hist/{full}.json"))
own = {}
for e in sorted(h["trades"], key=lambda e: e["t"]): own.setdefault(e["m"], []).append(e)
items = [x for v in res[full].values() for x in v]; random.Random(7).shuffle(items)
OFF = int(os.environ.get("OFFSET", 0)); items = items[OFF:OFF + N]   # OFFSET=300: the next 300 of the same shuffle, disjoint (the holdout)
def sim(p, tp=None, hold=1800, its=False, sp=None, trail=None):
    """One exit, nothing hidden (hunt_lib.model always adds our bot's sell pressure and stall). Candidates: the curve
    completing (sold there), its own first sale after our buy (its), the take profit (px over ITS price), nn net sales by
    others within w s from 30 s (sp), a trailing stop (after a x, d off the peak), the time limit. A trigger sells at the
    next trade, time and graduation at that trade (hunt_lib's convention)."""
    if p["refused"]: return -0.0004
    vt0, vq0, bps0 = p["ent"]; Q = 0.5 * 1e9 / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    def out(i):
        if i is None: vq, vt, b = vq0, vt0, bps0
        else: vq, vt, b = p["vq"][i], p["vt"][i], p["bps"][i]
        vq_r = vq + net_in; vt_r = vt * vq / vq_r
        return (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - b / 1e4) * p["rate"] / 1e9 - 0.5 - 0.0026
    px, age = p["px"], p["age"]; n = len(px)
    if n == 0: return out(None)
    c = []
    for mask, d in ((p["grad"], 0), (age >= hold, 0)):
        i = H.first(mask); c += [(i, d)] if i is not None else []
    if its: i = H.first(p["sell"]); c += [(i, 1)] if i is not None else []
    if tp: i = H.first(px >= tp); c += [(i, 1)] if i is not None else []
    if sp:
        nn, w = sp; lo = np.searchsorted(age, age - w, side="left"); s_ = np.concatenate([[0], np.cumsum(p["osell"])]); b_ = np.concatenate([[0], np.cumsum(p["obuy"])])
        i = H.first(((s_[1:] - s_[lo]) - (b_[1:] - b_[lo]) >= nn) & (age >= 30)); c += [(i, 1)] if i is not None else []
    if trail:
        a, dd = trail; pk = np.maximum.accumulate(px); i = H.first((pk >= a) & (px <= (1 - dd) * pk)); c += [(i, 1)] if i is not None else []
    if not c: return out(n - 1)
    i, d = min(c); return out(min(i + d, n - 1))
def menu(p):
    o = {"its-sale": sim(p, its=True)}
    for tp in (1.3, 1.5, 2, 3, 5): o[f"tp{tp}"] = sim(p, tp=tp)
    for m in (1, 2, 5, 10, 30): o[f"t{m}m"] = sim(p, hold=m * 60)
    o["its-sale+tp2"] = sim(p, its=True, tp=2); o["trail1.3/25%"] = sim(p, trail=(1.3, 0.25)); o["trail1.5/35%"] = sim(p, trail=(1.5, 0.35))
    for nn, w in ((3, 30), (5, 60), (10, 60)): o[f"sp{nn}/{w}s"] = sim(p, sp=(nn, w))
    return o
rows = []; t0 = time.time()
for i, x in enumerate(items):
    mine = own.get(x["m"], []); b = next((e for e in mine if e["buy"]), None)
    if not b: continue
    rate = rate_of(b["quote"])
    if rate is None: continue
    if os.environ.get("NOFETCH") and not os.path.exists(f"{ns['CP']}/{b['slot']}_{x['m']}.json.gz"): continue   # a report on what is cached
    tr = cpath(x["m"], b["slot"], b["t"])
    k = next((j for j, y in enumerate(tr) if y["user"] == full and y["buy"] and y["slot"] == b["slot"]), None)
    if k is None or k >= len(tr) - 1: continue
    p = H.prep(tr, k, rate, "slot+1"); s1 = next((e["t"] for e in mine if not e["buy"] and e["t"] >= b["t"]), None)
    o = menu(p)
    rows.append(dict(m=x["m"], t=b["t"], sol=x["sol"], prog=x["p"], quote=b["quote"] or "SOL", hour=(b["t"] // 3600) % 24,
                     held=(s1 - b["t"]) if s1 else None, refused=p["refused"], ex=o))
    if (i + 1) % 25 == 0: print(f"{W8}: {i + 1}/{len(items)} buys, {time.time() - t0:.0f} s", flush=True)
json.dump(rows, open(f"{SP}/winners/study_{W8}{os.environ.get('SUFFIX', '')}.json", "w"))
print(f"{W8}: {len(rows)} copies saved")
