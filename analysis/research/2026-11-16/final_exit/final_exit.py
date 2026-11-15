# The last exit study before the freeze (the owner, Nov 15 night: "recompute deeply the exit strategy, when we sell
# after him and the holding and everything after adding the new filters ... a smart combination that is not overfitted
# and most importantly smart and logic. After the study now we stop making changes").
# Method, so that the result is a reason and not a search: each part of the exit is a mechanism with a few coarse
# values; each is changed ALONE against the live setup; only a part that is ahead in all three blocks by more than
# the noise goes into a combination; the combination is then checked walk-forward (picked on A -> scored on B; picked
# on A+B -> scored on C), as we would really have lived it.
# The live setup: tp 4.0, timer 600 s, its sale followed 30-290 s under 1.5x, sell_pressure [5, 60, 30], stall 180 s.
#   H  its sale: followed in which window, under which price (it gave up on the coin: follow; it took profit: don't)
#   A  after its sale that we did not follow (it is out, we are alone): a floor under the price it sold at, a
#      shorter stall, a lower pressure count, or simply out T seconds later
#   T  the timer   TP the take profit   S the stall   P the pressure rule
#   python3 -I final_exit.py CQ ALL > out/final_exit.txt
import sys, os, random, collections
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "signals")); sys.argv = sys.argv[:3]
import round3 as R3
from round3 import L, ROWS, PREP, EX, score, blk
r3_trigger = R3.trigger
def trigger(p, x, sig):
    kind = sig[0]
    if kind not in ("press", "stall2", "floor", "stallafter", "pressafter", "hisgone"): return r3_trigger(p, x, sig)
    age = p["age"]; n = len(age)
    if n == 0: return None
    px = p["px"] / x["pin"]
    if kind == "stall2":
        pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]])
        last = np.maximum.accumulate(np.where(newhi, age, -1e9)); return L.first((pk >= sig[1]) & (age - last >= sig[2]))
    if kind == "press":
        lo = np.searchsorted(age, age - sig[2], side="left")
        s = np.concatenate([[0], np.cumsum(x["sell"])]); b = np.concatenate([[0], np.cumsum(x["buy"])])
        return L.first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= sig[1]) & (age >= sig[3]))
    j = L.first(p["sell"])                                    # wallet 4's first sale after our buy
    if j is None: return None
    after = np.arange(n) > j
    if kind == "floor": return L.first(after & (px <= sig[1] * px[j]))
    if kind == "hisgone": return L.first(after & (age >= age[j] + sig[1]))
    if kind == "stallafter":
        pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]])
        last = np.maximum(np.maximum.accumulate(np.where(newhi, age, -1e9)), age[j]); return L.first(after & (age - last >= sig[1]))
    lo = np.searchsorted(age, age - sig[2], side="left")      # pressafter
    s = np.concatenate([[0], np.cumsum(x["sell"])]); b = np.concatenate([[0], np.cumsum(x["buy"])])
    return L.first(after & ((s[1:] - s[lo]) - (b[1:] - b[lo]) >= sig[1]) & (age >= 30))
R3.trigger = trigger
P0, S0, E0 = ("press", 5, 60, 30), ("stall2", 1.0, 180), (30, 290, 1.5)
def rule(P=P0, S=S0, A=None, tp=4.0, hold=600, E=E0): return (tuple(s for s in (P, S, A) if s), tp, hold, E)
LIVE = rule(); B0 = score(LIVE); cache = {LIVE: B0}
def g(r):
    if r not in cache: cache[r] = score(r)
    return cache[r]
random.seed(7)
def stats(r):
    s = g(r); d = [a - b for a, b in zip(s["days"], B0["days"])]; dr = sorted(sum(random.choice(d) for _ in d) for _ in range(2000))
    return s, sum(1 for y in dr if y > 0) / 20, dr[100], dr[1900], sum(1 for a in d if a > 0.005), sum(1 for a in d if a < -0.005)
def line(nm, r):
    s, share, lo, hi, up, dn = stats(r); kinds = " ".join(f"{w} {c:.0f}" for w, c in s["whys"].most_common() if w != "refused")
    star = "*" if all(s["b"][i] > B0["b"][i] for i in range(3)) else " "
    return (f"   {nm:44s} | {s['tot']:+6.2f} | {s['tot'] - B0['tot']:+6.2f}{star} | {s['b'][0] - B0['b'][0]:+5.2f} {s['b'][1] - B0['b'][1]:+5.2f} {s['b'][2] - B0['b'][2]:+5.2f} | {s['wo5']:+6.2f} | {s['neg']}/{s['nd']} | {s['worst']:+5.2f} |"
            f" {share:5.1f}% [{lo:+5.1f}, {hi:+5.1f}] | {up:2d}/{dn:2d} | {kinds}")
hdr = f"   {'':44s} | total  | gain    | by block A / B / C | w/o b5 | neg  | worst | draws ahead [5%, 95%]  | days +/- | exits (a landing)"
print(f"{len(ROWS)} buys, 0.5 SOL, 2 open. gain = against the live setup; * = ahead in all three blocks; [5%, 95%] = the gain when the 24 days are drawn again")
print(hdr); print(line("LIVE: tp 4, 600 s, his sale 30-290 s <1.5x, press, stall", LIVE))
# what the live setup does on the copies where it sold and we did not follow
foll = collections.Counter(); nets = collections.defaultdict(list)
for r in ROWS:
    p, x = PREP[r["key"], 4], EX[r["key"], 4]
    if p["refused"]: continue
    j = L.first(p["sell"]); net, why, held = R3.model(p, x, 0.5, LIVE[0], 4.0, 600, E0)
    if j is None or p["age"][j] > held: k = "it had not sold when we closed"
    elif why == "its_sell": k = "it sold under 1.5x at 30-290 s: followed"
    elif p["age"][j] < 30: k = "it sold in the first 30 s: not followed"
    elif p["age"][j] >= 290: k = "it sold after 290 s: not followed"
    else: k = "it sold at 1.5x or more: not followed"
    foll[k] += 1; nets[k].append(net)
print("== the live setup by what wallet 4 did (every copy, landing 4, no slot limit)")
for k, c in foll.most_common(): print(f"   {k:44s}: {c:4d} copies, net {sum(nets[k]):+7.2f} SOL, {100 * sum(nets[k]) / c / 0.5:+6.1f}% a copy, {100 * sum(1 for v in nets[k] if v > 0) / c:4.1f}% won")
SETS = collections.OrderedDict()
SETS["H  its sale followed"] = [("never", rule(E=None)), ("0-290 s under 1.5x", rule(E=(0, 290, 1.5))), ("10-290 s under 1.5x", rule(E=(10, 290, 1.5))), ("30-180 s under 1.5x", rule(E=(30, 180, 1.5))),
    ("30-600 s under 1.5x", rule(E=(30, 600, 1.5))), ("0-600 s under 1.5x", rule(E=(0, 600, 1.5))), ("30-290 s under 1.25x", rule(E=(30, 290, 1.25))), ("30-290 s under 1.0x", rule(E=(30, 290, 1.0))),
    ("30-290 s under 2.0x", rule(E=(30, 290, 2.0))), ("0-600 s under 1.0x", rule(E=(0, 600, 1.0)))]
SETS["A  after its sale that we did not follow"] = [(f"out if under {k}x the price it sold at", rule(A=("floor", k))) for k in (0.9, 0.8, 0.7, 0.6, 0.5)] + \
    [(f"out after {T} s more without a new high", rule(A=("stallafter", T))) for T in (30, 60, 90, 120)] + \
    [(f"out on {n} more sells than buys in {w} s", rule(A=("pressafter", n, w))) for n, w in ((2, 60), (3, 60), (3, 30))] + \
    [(f"out {T} s after its sale", rule(A=("hisgone", T))) for T in (30, 60, 120, 240)]
SETS["T  the timer"] = [(f"{h} s", rule(hold=h)) for h in (300, 450, 750, 900, 1200, 1790)]
SETS["TP the take profit"] = [(f"tp {t}" if t else "no tp", rule(tp=t)) for t in (2.5, 3.0, 3.5, 4.5, 5.0, 6.0, 8.0, None)]
SETS["S  the stall"] = [("off", rule(S=None))] + [(f"{T} s", rule(S=("stall2", 1.0, T))) for T in (120, 150, 210, 240, 300)]
SETS["P  the pressure rule"] = [("off", rule(P=None)), ("5 in 60 s from 20 s", rule(P=("press", 5, 60, 20))), ("4 in 90 s", rule(P=("press", 4, 90, 30))), ("5 in 90 s", rule(P=("press", 5, 90, 30))), ("6 in 120 s", rule(P=("press", 6, 120, 30)))]
SETS["   neither signal (tp 4 alone) / old live"] = [("no press, no stall, tp 4", rule(P=None, S=None)), ("no press, no stall, tp 3 (before Nov 15)", rule(P=None, S=None, tp=3.0))]
for title, rs in SETS.items():
    print(f"== {title}: one change against the live setup\n" + hdr)
    for nm, r in rs: print(line(nm, r))
# the noise: how far apart are two setups that differ by nothing real? the spread of the gain when the days are redrawn
w = [stats(r) for t, rs in SETS.items() for nm, r in rs]
print(f"== the noise: half the width of the [5%, 95%] band of a one-change gain, median over the {len(w)} changes: {sorted((x[3] - x[2]) / 2 for x in w)[len(w) // 2]:.2f} SOL")
# combinations only of the changes that are ahead in all three blocks
ok = [(t.split()[0], nm, r) for t, rs in SETS.items() if not t.startswith("   ") for nm, r in rs if all(g(r)["b"][i] > B0["b"][i] for i in range(3))]
print(f"== ahead in all three blocks alone: {len(ok)}")
for fam, nm, r in ok: print(f"   {fam} {nm}: {g(r)['tot'] - B0['tot']:+.2f}")
def merge(a, b):                                             # two rules that each differ from LIVE in one part
    ka = dict(P=P0, S=S0, A=None, tp=4.0, hold=600, E=E0)
    for r in (a, b):
        sig, tp, hold, E = r
        P = next((s for s in sig if s[0] == "press"), None); S = next((s for s in sig if s[0] == "stall2"), None); A = next((s for s in sig if s[0] not in ("press", "stall2")), None)
        for k, v, d in (("P", P, P0), ("S", S, S0), ("A", A, None), ("tp", tp, 4.0), ("hold", hold, 600), ("E", E, E0)):
            if v != d: ka[k] = v
    return rule(**ka)
best = {}
for fam, nm, r in ok:
    if fam not in best or g(r)["tot"] > g(best[fam][1])["tot"]: best[fam] = (nm, r)
print("== the best of each part that passed, together (pairs, then all)\n" + hdr)
fams = list(best)
for i in range(len(fams)):
    for k in range(i + 1, len(fams)):
        print(line(f"{fams[i]} {best[fams[i]][0][:16]} + {fams[k]} {best[fams[k]][0][:16]}", merge(best[fams[i]][1], best[fams[k]][1])))
if len(fams) > 2:
    allr = LIVE
    for f in fams: allr = merge(allr, best[f][1])
    print(line("all of them", allr))
# walk-forward over everything scored: what we would really have got
ALLR = [r for r in cache if r != LIVE]
print(f"== walk-forward over the {len(ALLR)} setups scored (gain over the live setup)")
pickA = max(ALLR, key=lambda r: cache[r]["b"][0]); pickAB = max(ALLR, key=lambda r: cache[r]["b"][0] + cache[r]["b"][1])
print(f"   best on A ({cache[pickA]['b'][0] - B0['b'][0]:+.2f}) -> on B {cache[pickA]['b'][1] - B0['b'][1]:+.2f}, on C {cache[pickA]['b'][2] - B0['b'][2]:+.2f}")
print(f"   best on A+B ({cache[pickAB]['b'][0] + cache[pickAB]['b'][1] - B0['b'][0] - B0['b'][1]:+.2f}) -> on C {cache[pickAB]['b'][2] - B0['b'][2]:+.2f}")
top = sorted(ALLR, key=lambda r: -(cache[r]["b"][0] + cache[r]["b"][1]))[:10]
print(f"   the 10 best on A+B -> on C on average {sum(cache[r]['b'][2] - B0['b'][2] for r in top) / 10:+.2f}; ahead on C: {sum(1 for r in top if cache[r]['b'][2] > B0['b'][2])} of 10")
