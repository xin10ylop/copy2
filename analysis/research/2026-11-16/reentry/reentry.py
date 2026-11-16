# Not missing the run after a signal exit (the owner, Nov 16, after #64 J8Lutktx: sold on sell_pressure at 1.06x at
# 131 s, 0.71x at 240 s, 4x at 526 s): "isn't there something we can adjust to not miss the 4x with sell pressure?"
# Two ideas with a reason, each against the live setup (tp 4.0, 600 s, its sale 30-290 s under 1.5x, sell_pressure
# [5, 60, 30], stall 180 s), on the 1,238 buys, the bot's run (2 open, caps; a copy holds its slot to its last sale):
#   back in  after an exit on a signal or its early sale, buy again (once, the same stake) on the trade after a sign
#            that the coin has turned, before 480 s: a new high above the high while we held / the price back over
#            1.5x or 2x its price / 10+ more buys than sells in 30 s with the price over our sale. The second leg: tp
#            4.0 and the 600 s timer, with or without the pressure rule; its own round trip charged.
#   runner   on an exit by a signal or its early sale, keep a share of the position (10 / 20 / 30%) to the take
#            profit or the timer; the extra sale charged 0.0013 SOL.
#   python3 -I reentry.py CQ ALL > out/reentry.txt
import sys, os, random
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "buy_pressure")); sys.argv = sys.argv[:3]
import buy_pressure as BP
from buy_pressure import L, ROWS, PREP, EX, R3, rule
from round3 import blk, day, CAPS
STAKE = 0.5; SIGS, TP, HOLD, E = rule()
SIG_EXITS = ("press", "stall2", "its_sell")
def cut(p, x, e):
    """the copy as if bought on trade e of the path (its arrays after it)."""
    p2 = dict(p); p2["ent"] = (p["vt"][e], p["vq"][e], p["bps"][e]); p2["refused"] = False; p2["last"] = int(p["age"][e])
    for k in ("px", "age", "sell", "grad", "vt", "vq", "bps"): p2[k] = p[k][e + 1:]
    x2 = dict(x); x2["sell"] = x["sell"][e + 1:]; x2["buy"] = x["buy"][e + 1:]
    return p2, x2
def netbuy(p, x, W):
    age = p["age"]; lo = np.searchsorted(age, age - W, side="left")
    s = np.concatenate([[0], np.cumsum(x["sell"])]); b = np.concatenate([[0], np.cumsum(x["buy"])])
    return (b[1:] - b[lo]) - (s[1:] - s[lo])
def copy(p, x, how):
    net, why, held = R3.model(p, x, STAKE, SIGS, TP, HOLD, E)
    if how is None or why not in SIG_EXITS or not len(p["px"]): return net, held
    ex = int(np.searchsorted(p["age"], held)); ex = min(ex, len(p["px"]) - 1)
    if how[0] == "runner":
        f = how[1]; keep = L.model(p, STAKE * f, TP, HOLD, None, None)
        return net * (1 - f) + (keep[0] + 0.0026) - 0.0013 + 0.0026 * f, max(held, keep[2])
    kind, lvl, sigs2 = how[1], how[2], how[3]
    px, age = p["px"], p["age"]; after = (np.arange(len(px)) > ex) & (age < 480)
    if not after.any(): return net, held
    if kind == "newhigh": f = after & (px > np.maximum.accumulate(px)[ex] * lvl)
    elif kind == "level": f = after & (px >= lvl)
    else: f = after & (netbuy(p, x, 30) >= lvl) & (px > px[ex])
    i = L.first(f)
    if i is None or i + 1 >= len(px) - 1: return net, held
    p2, x2 = cut(p, x, i + 1)
    n2, w2, h2 = R3.model(p2, x2, STAKE, sigs2, TP, HOLD, None) if sigs2 else L.model(p2, STAKE, TP, HOLD, None, None)
    return net + n2, max(held, h2)
def score(how):
    tot, b, days, wo = 0, [0, 0, 0], {}, []
    for n in L.LAND:
        open_, res = [], []
        for r in ROWS:
            open_ = [y for y in open_ if y[0] > r["t"]]
            if len(open_) >= 2 or sum(1 for y in open_ if y[1] == r["anchor"]) >= CAPS[r["anchor"]]: continue
            p, x = PREP[r["key"], n], EX[r["key"], n]
            if p["refused"]: res.append((r, -0.0004)); continue
            net, held = copy(p, x, how); open_.append((r["t"] + held, r["anchor"])); res.append((r, net))
        v = sorted((q[1] for q in res), reverse=True); tot += sum(v) / 3; wo.append(sum(v[5:]))
        for r, net in res: b[blk(r)] += net / 3; days[day(r["t"])] = days.get(day(r["t"]), 0) + net / 3
    ks = sorted(days)[1:-1]
    return dict(tot=tot, b=b, wo5=sum(wo) / 3, days=[days[k] for k in ks], neg=sum(1 for k in ks if days[k] < 0), worst=min(days[k] for k in ks))
B0 = score(None); random.seed(7)
def line(nm, how):
    s = score(how); d = [a - c for a, c in zip(s["days"], B0["days"])]; dr = sorted(sum(random.choice(d) for _ in d) for _ in range(2000))
    star = "*" if all(s["b"][i] > B0["b"][i] for i in range(3)) else " "
    return f"   {nm:66s} | {s['tot']:+6.2f} | {s['tot'] - B0['tot']:+6.2f}{star} | {s['b'][0] - B0['b'][0]:+5.2f} {s['b'][1] - B0['b'][1]:+5.2f} {s['b'][2] - B0['b'][2]:+5.2f} | {s['wo5']:+6.2f} | {s['neg']} | {s['worst']:+5.2f} | {sum(1 for y in dr if y > 0) / 20:5.1f}% [{dr[100]:+5.1f}, {dr[1900]:+5.1f}]"
if __name__ == "__main__":
    print(f"{len(ROWS)} buys, 0.5 SOL, the bot's run; the live setup {B0['tot']:+.2f} (w/o best 5 {B0['wo5']:+.2f}, losing days {B0['neg']}, worst {B0['worst']:+.2f}); * = ahead in all three blocks; noise of one change about +-3.4")
    print(f"   {'':66s} | total  | gain    | by block A / B / C | w/o b5 | neg | worst | draws ahead [5%, 95%]")
    PR = (("press", 5, 60, 30),)
    print("== back in after a signal exit (or its early sale), once, before 480 s")
    for nm, k, lvl in (("a new high 10% over the high while we held", "newhigh", 1.1), ("a new high 30% over it", "newhigh", 1.3), ("the price back over 1.5x its price", "level", 1.5),
                       ("the price back over 2x its price", "level", 2.0), ("10+ more buys than sells in 30 s, over our sale price", "buys", 10), ("20+ more buys than sells in 30 s, over our sale price", "buys", 20)):
        print(line(f"{nm}; then tp 4 / timer", ("back", k, lvl, None)))
        print(line(f"{nm}; then tp 4 / timer / pressure", ("back", k, lvl, PR)))
    print("== a runner: keep a share to the take profit or the timer")
    for f in (0.1, 0.2, 0.3, 0.5): print(line(f"keep {int(f * 100)}%", ("runner", f)))
