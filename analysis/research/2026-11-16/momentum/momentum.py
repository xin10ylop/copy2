# Buying that was fast and slows down, selling that rises (the owner, Nov 15 night: "why not check when buy pressure
# is fast, then slows down, and maybe also then if sell pressure is rising"). Rounds 1-3 and ../buy_pressure/ looked at
# the LEVEL of buys and sells over a window; this is their CHANGE: the last W seconds against the W seconds before.
#   fade    buying was fast (B0 or more buys by others in the earlier window) and has slowed to F times that or less
#   turn    a fade, and sells now outnumber buys in the last window
#   surge   selling has risen: S or more sells in the last window, and K times the earlier window's or more
# Part 1, before any rule: at the first time each pattern shows (30 s or more after its buy, while the live setup still
# holds the copy), what does the price do next? Against the same for the live sell_pressure signal. A pattern that is
# not followed by a lower price cannot make a sell rule.
# Part 2: each pattern as an exit ADDED to the live setup (tp 4.0, 600 s, its sale 30-290 s under 1.5x, sell_pressure
# [5, 60, 30], stall 180 s), at any price or only at 1.5x or more.
#   python3 -I momentum.py CQ ALL > out/momentum.txt
import sys, os, random, collections
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "buy_pressure")); sys.argv = sys.argv[:3]
import buy_pressure as BP
from buy_pressure import L, ROWS, PREP, EX, score, rule, B0, R3
def counts(p, x, W):
    age = p["age"]; a = np.searchsorted(age, age - W, side="left"); b = np.searchsorted(age, age - 2 * W, side="left")
    cb = np.concatenate([[0], np.cumsum(x["buy"])]); cs = np.concatenate([[0], np.cumsum(x["sell"])])
    return cb[1:] - cb[a], cb[a] - cb[b], cs[1:] - cs[a], cs[a] - cs[b]      # buys now, buys before, sells now, sells before
def cond(p, x, sig):
    kind, W = sig[0], sig[1]; b1, b0, s1, s0 = counts(p, x, W); ok = p["age"] >= max(30, 2 * W)
    if kind == "fade": f = (b0 >= sig[2]) & (b1 <= sig[3] * b0)
    elif kind == "turn": f = (b0 >= sig[2]) & (b1 <= sig[3] * b0) & (s1 > b1)
    else: f = (s1 >= sig[2]) & (s1 >= sig[3] * np.maximum(s0, 1))
    if sig[4]: f = f & (p["px"] >= sig[4])
    return f & ok
bp_trigger = R3.trigger
def trigger(p, x, sig):
    if sig[0] not in ("fade", "turn", "surge"): return bp_trigger(p, x, sig)
    return L.first(cond(p, x, sig)) if len(p["age"]) else None
R3.trigger = trigger
LIVE = rule()
# ---- part 1
def after(sig, live_sig=None):
    out = []
    for r in ROWS:
        p, x = PREP[r["key"], 4], EX[r["key"], 4]
        if p["refused"] or not len(p["px"]): continue
        net, why, held = R3.model(p, x, 0.5, LIVE[0], 4.0, 600, LIVE[3])
        i = bp_trigger(p, x, live_sig) if live_sig else L.first(cond(p, x, sig))
        if i is None or p["age"][i] >= held: continue          # the live setup had closed the copy already
        m = (np.arange(len(p["px"])) > i) & (p["age"] <= 600); fut = p["px"][m]
        if not len(fut): continue
        a = p["age"][m] - p["age"][i]; at = lambda T: (fut[a <= T][-1] if (a <= T).any() else p["px"][i]) / p["px"][i]
        out.append((at(60), at(180), fut[-1] / p["px"][i], fut.max() / p["px"][i], p["px"][i]))
    return out
def show(nm, v):
    if len(v) < 5: return f"   {nm:62s}: {len(v):4d} copies"
    q = lambda k: np.median([y[k] for y in v])
    return (f"   {nm:62s}: {len(v):4d} copies | price then, median: 60 s later {q(0):.2f}x, 180 s {q(1):.2f}x, at 600 s {q(2):.2f}x (mean {np.mean([y[2] for y in v]):.2f}x) |"
            f" lower at 600 s: {100 * sum(1 for y in v if y[2] < 1) / len(v):4.1f}% | a new high 20%+ above after it: {100 * sum(1 for y in v if y[3] >= 1.2) / len(v):4.1f}%")
print(f"{len(ROWS)} buys. Part 1 (landing 4): the first time a pattern shows while the live setup still holds the copy; the price after it, in multiples of the price then")
print(show("REFERENCE: the live rule, 5 more sells than buys in 60 s", after(None, ("press", 5, 60, 30))))
P1 = [("fade: 10+ buys in the earlier 30 s, now half or less", ("fade", 30, 10, 0.5, None)), ("fade: 10+ buys in the earlier 30 s, now a quarter or less", ("fade", 30, 10, 0.25, None)),
      ("fade: 20+ buys in the earlier 30 s, now half or less", ("fade", 30, 20, 0.5, None)), ("fade: 20+ buys in the earlier 60 s, now half or less", ("fade", 60, 20, 0.5, None)),
      ("fade at 1.5x or more: 10+ buys in 30 s, now half or less", ("fade", 30, 10, 0.5, 1.5)), ("fade at 2x or more: 10+ buys in 30 s, now half or less", ("fade", 30, 10, 0.5, 2.0)),
      ("turn: that fade (10+, half) and sells now above buys", ("turn", 30, 10, 0.5, None)), ("turn: fade (20+, half, 60 s) and sells now above buys", ("turn", 60, 20, 0.5, None)),
      ("turn at 1.5x or more: fade (10+, half) and sells above buys", ("turn", 30, 10, 0.5, 1.5)),
      ("surge: 8+ sells in 30 s, twice the earlier 30 s", ("surge", 30, 8, 2.0, None)), ("surge: 15+ sells in 30 s, twice the earlier 30 s", ("surge", 30, 15, 2.0, None)),
      ("surge: 15+ sells in 60 s, twice the earlier 60 s", ("surge", 60, 15, 2.0, None)), ("surge at 1.5x or more: 8+ sells in 30 s, twice the earlier", ("surge", 30, 8, 2.0, 1.5))]
for nm, sig in P1: print(show(nm, after(sig)))
# ---- part 2
random.seed(7)
def line(nm, r):
    s = score(r); d = [a - b for a, b in zip(s["days"], B0["days"])]; dr = sorted(sum(random.choice(d) for _ in d) for _ in range(2000))
    star = "*" if all(s["b"][i] > B0["b"][i] for i in range(3)) else " "
    mine = sum(c for w, c in s["whys"].items() if w in ("fade", "turn", "surge"))
    return (f"   {nm:62s} | {s['tot']:+6.2f} | {s['tot'] - B0['tot']:+6.2f}{star} | {s['b'][0] - B0['b'][0]:+5.2f} {s['b'][1] - B0['b'][1]:+5.2f} {s['b'][2] - B0['b'][2]:+5.2f} | {s['wo5']:+6.2f} | {s['neg']}/{s['nd']} | {s['worst']:+5.2f} |"
            f" {sum(1 for y in dr if y > 0) / 20:5.1f}% [{dr[100]:+5.1f}, {dr[1900]:+5.1f}] | tp {s['whys'].get('tp', 0):.0f}, by it {mine:.0f}")
hdr = f"   {'':62s} | total  | gain    | by block A / B / C | w/o b5 | neg  | worst | draws ahead [5%, 95%]  | exits"
print(f"\nPart 2: each pattern as an exit added to the live setup ({B0['tot']:+.2f}); * = ahead in all three blocks; the noise of one change is about +-3.4 SOL")
for kind, title in (("fade", "buying was fast and has slowed"), ("turn", "buying slowed and sells are now above buys"), ("surge", "selling has risen")):
    print(f"== {kind}: {title}\n" + hdr)
    for cap in (None, 1.5):
        c = f", only at {cap}x or more" if cap else ""
        if kind == "surge":
            for W, S, K in ((30, 8, 2.0), (30, 15, 2.0), (30, 8, 3.0), (60, 15, 2.0), (60, 25, 2.0), (60, 15, 3.0)): print(line(f"{S}+ sells in {W} s, {K:g} times the earlier {W} s{c}", rule((kind, W, S, K, cap))))
        else:
            for W, Bm, F in ((30, 10, 0.5), (30, 10, 0.25), (30, 20, 0.5), (60, 20, 0.5), (60, 20, 0.25), (60, 40, 0.5)): print(line(f"{Bm}+ buys in the earlier {W} s, now {F:g} of it or less{c}", rule((kind, W, Bm, F, cap))))
