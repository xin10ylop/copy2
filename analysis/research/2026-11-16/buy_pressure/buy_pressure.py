# Buy pressure (the owner, Nov 15 night: "as well as sell pressure, why not also test buy pressure? maybe it is also a
# smart way to know if tp should be lowered"). The reason it could work: on a bonding curve the price only rises while
# buys outnumber sells, so strong buying at a high price says the run is not over, and no buying says it is.
# Part 1, the idea itself, before any rule: when a copy's price first crosses a level (1.5x, 2x, 3x, 4x its price, in
# the first 600 s), split by the others' buys minus sells over the 60 s before; what comes next? If buy pressure at
# the crossing does not separate the coins that go on from those that fall back, no rule built on it can work.
# Part 2, the rules, each ADDED to the live setup (tp 4.0, 600 s, its sale 30-290 s under 1.5x, sell_pressure
# [5, 60, 30], stall 180 s), as ../final_exit/:
#   early   a lower take profit when buying has faded: out at A x (2 / 2.5 / 3 / 3.5) if buys minus sells over W s is M or less
#   late    tp 4.0 only once buying has faded: armed when the price has reached 4x (or 3x), out when buys minus sells
#           over W s falls under K; while buying stays strong the copy runs on (the other exits still apply)
#   python3 -I buy_pressure.py CQ ALL > out/buy_pressure.txt
import sys, os, random, collections
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "signals")); sys.argv = sys.argv[:3]
import round3 as R3
from round3 import L, ROWS, PREP, EX, score
def netbuy(p, x, W):
    age = p["age"]; lo = np.searchsorted(age, age - W, side="left")
    s = np.concatenate([[0], np.cumsum(x["sell"])]); b = np.concatenate([[0], np.cumsum(x["buy"])])
    return (b[1:] - b[lo]) - (s[1:] - s[lo])
r3_trigger = R3.trigger
def trigger(p, x, sig):
    kind = sig[0]
    if kind not in ("press", "stall2", "early", "late"): return r3_trigger(p, x, sig)
    age = p["age"]; n = len(age)
    if n == 0: return None
    if kind == "stall2":
        px = p["px"] / x["pin"]; pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]])
        last = np.maximum.accumulate(np.where(newhi, age, -1e9)); return L.first((pk >= sig[1]) & (age - last >= sig[2]))
    if kind == "press": return L.first((-netbuy(p, x, sig[2]) >= sig[1]) & (age >= sig[3]))
    nb = netbuy(p, x, sig[2])
    if kind == "early": return L.first((p["px"] >= sig[1]) & (nb <= sig[3]))                      # (A, W, M)
    return L.first((np.maximum.accumulate(p["px"]) >= sig[1]) & (nb < sig[3]))                    # late: (arm, W, K)
R3.trigger = trigger
P0, S0, E0 = ("press", 5, 60, 30), ("stall2", 1.0, 180), (30, 290, 1.5)
def rule(X=None, tp=4.0): return (tuple(s for s in (P0, S0, X) if s), tp, 600, E0)
LIVE = rule(); B0 = score(LIVE)
if __name__ == "__main__":
    # ---- part 1
    print(f"{len(ROWS)} buys. Part 1: at the first crossing of a level within 600 s of its buy (landing 4, every copy that is not refused),")
    print("by the others' buys minus sells in the 60 s before: what the price does next (to 600 s after its buy), in multiples of the level")
    for lvl, nxt in ((1.5, 2.0), (2.0, 3.0), (3.0, 4.0), (4.0, 6.0)):
        G = collections.defaultdict(list)
        for r in ROWS:
            p, x = PREP[r["key"], 4], EX[r["key"], 4]
            if p["refused"] or not len(p["px"]): continue
            ok = p["age"] <= 600; i = L.first((p["px"] >= lvl) & ok)
            if i is None: continue
            nb = netbuy(p, x, 60)[i]; rest = p["px"][i + 1:][ok[i + 1:]]
            if not len(rest): continue
            a60 = p["px"][i + 1:][p["age"][i + 1:] <= p["age"][i] + 60]
            G["0 or less" if nb <= 0 else "1 to 5" if nb <= 5 else "6 to 15" if nb <= 15 else "16 or more"].append((rest.max() / lvl, rest[-1] / lvl, rest.max() >= nxt, (a60[-1] / lvl) if len(a60) else 1.0))
        print(f"== crossing {lvl}x ({sum(len(v) for v in G.values())} copies); next level {nxt}x")
        for k in ("0 or less", "1 to 5", "6 to 15", "16 or more"):
            v = G.get(k, [])
            if v: print(f"   buys minus sells {k:10s}: {len(v):4d} copies | reaches {nxt}x: {100 * sum(1 for y in v if y[2]) / len(v):5.1f}% | highest after, median {np.median([y[0] for y in v]):.2f}x of the level | 60 s later, median {np.median([y[3] for y in v]):.2f}x | at 600 s, median {np.median([y[1] for y in v]):.2f}x, mean {np.mean([y[1] for y in v]):.2f}x")
    # ---- part 2
    random.seed(7)
    def line(nm, r):
        s = score(r); d = [a - b for a, b in zip(s["days"], B0["days"])]; dr = sorted(sum(random.choice(d) for _ in d) for _ in range(2000))
        star = "*" if all(s["b"][i] > B0["b"][i] for i in range(3)) else " "
        mine = sum(c for w, c in s["whys"].items() if w in ("early", "late"))
        return (f"   {nm:58s} | {s['tot']:+6.2f} | {s['tot'] - B0['tot']:+6.2f}{star} | {s['b'][0] - B0['b'][0]:+5.2f} {s['b'][1] - B0['b'][1]:+5.2f} {s['b'][2] - B0['b'][2]:+5.2f} | {s['wo5']:+6.2f} | {s['neg']}/{s['nd']} | {s['worst']:+5.2f} |"
                f" {sum(1 for y in dr if y > 0) / 20:5.1f}% [{dr[100]:+5.1f}, {dr[1900]:+5.1f}] | tp {s['whys'].get('tp', 0):.0f}, by it {mine:.0f}")
    hdr = f"   {'':58s} | total  | gain    | by block A / B / C | w/o b5 | neg  | worst | draws ahead [5%, 95%]  | exits"
    print(f"\nPart 2: each rule added to the live setup ({B0['tot']:+.2f}); * = ahead in all three blocks; the noise of a one-change gain is about +-3.4 SOL (../final_exit/)")
    print("== early: a lower take profit when buying has faded\n" + hdr)
    for A in (2.0, 2.5, 3.0, 3.5):
        for W, M in ((60, 0), (60, -3), (30, 0), (120, 0)): print(line(f"out at {A}x if buys minus sells in {W} s is {M} or less", rule(("early", A, W, M))))
    print("== late: the take profit only once buying has faded (no fixed tp)\n" + hdr)
    for arm in (4.0, 3.0):
        for W, K in ((60, 1), (60, 5), (60, 10), (30, 1), (30, 5), (120, 5)): print(line(f"armed at {arm}x, out when buys minus sells in {W} s is under {K}", rule(("late", arm, W, K), tp=None)))
    print("== for scale\n" + hdr)
    print(line("no tp at all (the signals and the timer only)", rule(tp=None))); print(line("tp 3.0", rule(tp=3.0))); print(line("tp 5.0", rule(tp=5.0)))
