# A take profit and timer that follow how the coin behaves (the owner, Nov 16, after #66 went to 4x in 15 s: "set a
# max timer for that x seconds ... then start adjusting tp depending on how the coin behaves, and test this behaviour
# with several logical metrics"). The first 30 s split winners from losers (../winners/); here they decide the exit.
#   class   at T s (30 / 60) after its buy, a copy is "strong" by one metric: its price over P times ours (1.2 / 1.5),
#           N more buys than sells by others since its buy (10 / 20), or K trades by others (50 / 100); else "weak".
#           Before T the live take profit (4.0); after it, strong: tp 6 / 10 / none and a timer of 600 / 1200 s;
#           weak: tp 3 / 4 and 600 s.
#   fast    a copy whose price reaches 4x within F s (15 / 30 / 60) is not sold there: its tp goes to 6 / 10 / none and
#           its timer to 600 / 1200 s.
# Everything else as live (its sale 30-290 s under 1.5x, sell_pressure [5, 60, 30], stall 180 s, graduation). Judged
# as before: the three blocks, the days drawn again, walk-forward over the whole family (best on A -> B and C; best on
# A+B -> C), and then on wallet 4's newest days (Nov 15 13:04 - Nov 16 14:25, ../new_days/), which no study has used.
#   python3 -I dynamic_tp.py CQ ALL NEW > out/dynamic_tp.txt
import sys, os, random, itertools, collections, datetime
import numpy as np
NEWD = sys.argv[3]
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "buy_pressure")); sys.argv = sys.argv[:3]
import buy_pressure as BP
from buy_pressure import L, ROWS, PREP, EX
from round3 import blk, day, CAPS
CAPS = dict(CAPS, XsbEhLAt=1)
OURS = {L.W4, "Eao8T2Pk2aDzPWUFCA8si7oWd5ndFKfnX3HjYMpERst6"}
# ---- wallet 4's newest days (as ../new_days/new_days.py)
T_END = datetime.datetime(2026, 11, 15, 13, 4, tzinfo=datetime.timezone.utc).timestamp()
rows, P, info = L.load(NEWD, T_END); NROWS, NPREP, NEX = [], {}, {}
for r in rows:
    if r["anchor"] not in CAPS or r["sol"] < 1.3: continue
    ps = [L.prep(r, P, n) for n in L.LAND]
    if any(p is None for p in ps): continue
    tr = P[r["key"]][1]; k = next(i for i, e in enumerate(tr) if e["user"] == L.W4 and e["buy"] and e["slot"] == r["slot"])
    for n, p in zip(L.LAND, ps):
        NPREP[r["key"], n] = p; rest = tr[len(tr) - len(p["px"]):]; j = len(tr) - len(p["px"]) - 1
        other = np.array([e["user"] not in OURS for e in rest], dtype=bool); sell = np.array([not e["buy"] for e in rest], dtype=bool) & other
        NEX[r["key"], n] = dict(sell=sell, buy=other & ~sell, pin=(tr[k]["vt"] / tr[j]["vt"]) ** 2)
    NROWS.append(r)
def sigs(p, x):
    """first index of the pressure rule and of the stall, or None."""
    age = p["age"]; px = p["px"] / x["pin"]
    lo = np.searchsorted(age, age - 60, side="left"); s = np.concatenate([[0], np.cumsum(x["sell"])]); b = np.concatenate([[0], np.cumsum(x["buy"])])
    pr = L.first(((s[1:] - s[lo]) - (b[1:] - b[lo]) >= 5) & (age >= 30))
    pk = np.maximum.accumulate(px); newhi = np.concatenate([[True], pk[1:] > pk[:-1]]); last = np.maximum.accumulate(np.where(newhi, age, -1e9))
    st = L.first((pk >= 1.0) & (age - last >= 180))
    return pr, st
def model(p, x, stake, rule):
    """(net, why, held). rule: None (live), ("class", T, metric, level, (tp, hold) strong, tp weak), ("fast", F, tp, hold)."""
    if p["refused"]: return (-0.0004, "refused", 0)
    n = len(p["px"]); age, px = p["age"], p["px"]
    if n == 0: return L.model(p, stake, 4.0, 600, (30, 290, 1.5), None)
    tp_arr = np.full(n, 4.0); hold = 600
    if rule and rule[0] == "class":
        _, T, met, lvl, (tps, hs), tpw = rule
        i = L.first(age >= T)
        if i is not None:
            m = age < T
            if met == "price": v = (px[m][-1] / x["pin"]) if m.any() else 1.0
            elif met == "netbuy": v = int(x["buy"][m].sum() - x["sell"][m].sum())
            else: v = int((x["buy"] | x["sell"])[m].sum())
            strong = v >= lvl
            tp_arr[i:] = (tps if tps else 1e9) if strong else tpw
            if strong: hold = hs
    elif rule and rule[0] == "fast":
        _, F, tpf, hf = rule
        j = L.first((px >= 4.0) & (age <= F))
        if j is not None: tp_arr[:] = tpf if tpf else 1e9; hold = hf
    c = []
    i = L.first(p["grad"]);                                                 c += [(i, 0, "graduated", 0)] if i is not None else []
    i = L.first(p["sell"] & (age >= 30) & (age < 290) & (px < 1.5));       c += [(i, 1, "its_sell", 1)] if i is not None else []
    i = L.first(px >= tp_arr);                                              c += [(i, 2, "tp", 1)] if i is not None else []
    pr, st = sigs(p, x)
    if pr is not None: c += [(pr, 3, "press", 1)]
    if st is not None: c += [(st, 3, "stall", 1)]
    i = L.first(age >= hold);                                               c += [(i, 4, "time", 0)] if i is not None else []
    i, _, why, d = min(c) if c else (n - 1, 0, "time", 0); ex = min(i + d, n - 1)
    vt0, vq0, bps0 = p["ent"]; Q = stake * 1e9 * p["hopf"] / p["rate"]; net_in = Q * 1e4 / (1e4 + bps0); tok = vt0 - vt0 * vq0 / (vq0 + net_in)
    vq_r = p["vq"][ex] + net_in; vt_r = p["vt"][ex] * p["vq"][ex] / vq_r; out = (vq_r - vt_r * vq_r / (vt_r + tok)) * (1 - p["bps"][ex] / 1e4)
    return (out * p["rate"] * p["hopf"] / 1e9 - stake - 0.0026, why, int(age[ex]))
def score(rule, rows=ROWS, prep=PREP, ex=EX):
    tot, b, days, wo = 0, [0, 0, 0], collections.defaultdict(float), []
    for n in L.LAND:
        open_, res = [], []
        for r in rows:
            open_ = [y for y in open_ if y[0] > r["t"]]
            if len(open_) >= 2 or sum(1 for y in open_ if y[1] == r["anchor"]) >= CAPS[r["anchor"]]: continue
            net, why, held = model(prep[r["key"], n], ex[r["key"], n], 0.5, rule)
            if why != "refused": open_.append((r["t"] + held, r["anchor"]))
            res.append((r, net))
        v = sorted((q[1] for q in res), reverse=True); tot += sum(v) / 3; wo.append(sum(v[5:]))
        for r, net in res: b[blk(r)] += net / 3; days[day(r["t"])] += net / 3
    ks = sorted(days)[1:-1] if len(days) > 2 else sorted(days)
    return dict(tot=tot, b=b, wo5=sum(wo) / 3, days=[days[k] for k in ks], neg=sum(1 for k in ks if days[k] < 0), worst=min(days[k] for k in ks))
# a check that the model here is the live one
import round3 as R3
print(f"check: the live setup here {score(None)['tot']:+.2f}, in ../final_exit/ +75.29")
if __name__ == "__main__":
    RULES = collections.OrderedDict()
    for T, (met, lvls), strong, tpw in itertools.product((30, 60), (("price", (1.2, 1.5)), ("netbuy", (10, 20)), ("trades", (50, 100))),
                                                         ((6, 600), (10, 600), (None, 600), (6, 1200), (10, 1200), (None, 1200)), (3.0, 4.0)):
        for lvl in lvls:
            nm = f"at {T} s, {met} >= {lvl:g}: strong tp {strong[0] or 'none'} / {strong[1]} s, weak tp {tpw:g}"
            RULES[nm] = ("class", T, met, lvl, strong, tpw)
    for F, tpf, hf in itertools.product((15, 30, 60), (6, 10, None), (600, 1200)):
        RULES[f"fast: 4x within {F} s -> tp {tpf or 'none'} / {hf} s"] = ("fast", F, tpf, hf)
    B0 = score(None); S = {nm: score(r) for nm, r in RULES.items()}; random.seed(7)
    def line(nm, s, ref=B0):
        d = [a - c for a, c in zip(s["days"], ref["days"])]; dr = sorted(sum(random.choice(d) for _ in d) for _ in range(1000))
        star = "*" if all(s["b"][i] > ref["b"][i] for i in range(3)) else " "
        return f"   {nm:70s} | {s['tot']:+6.2f} | {s['tot'] - ref['tot']:+6.2f}{star} | {s['b'][0] - ref['b'][0]:+5.2f} {s['b'][1] - ref['b'][1]:+5.2f} {s['b'][2] - ref['b'][2]:+5.2f} | {s['wo5']:+6.2f} | {s['neg']} | {s['worst']:+5.2f} | {sum(1 for y in dr if y > 0) / 10:5.1f}%"
    hdr = f"   {'':70s} | total  | gain    | by block A / B / C | w/o b5 | neg | worst | ahead in draws"
    print(f"{len(ROWS)} buys, 0.5 SOL, the bot's run; the live setup {B0['tot']:+.2f} (w/o best 5 {B0['wo5']:+.2f}, losing days {B0['neg']}, worst {B0['worst']:+.2f}); {len(RULES)} rules; * = ahead in all three blocks; noise of one change about +-3.4")
    print("== the 20 best by total\n" + hdr)
    for nm, s in sorted(S.items(), key=lambda q: -q[1]["tot"])[:20]: print(line(nm, s))
    print("== ahead in all three blocks\n" + hdr)
    for nm, s in sorted(S.items(), key=lambda q: -q[1]["tot"]):
        if all(s["b"][i] > B0["b"][i] for i in range(3)): print(line(nm, s))
    print("== the fast-runner rules\n" + hdr)
    for nm, s in S.items():
        if nm.startswith("fast"): print(line(nm, s))
    print("== by family (settings ahead of live / all; the best)")
    for fam in ("price", "netbuy", "trades", "fast"):
        xs = [(nm, s) for nm, s in S.items() if (f", {fam} >=" in nm) or (fam == "fast" and nm.startswith("fast"))]
        b = max(xs, key=lambda q: q[1]["tot"])
        print(f"   {fam:7s}: {sum(1 for nm, s in xs if s['tot'] > B0['tot'])}/{len(xs)} ahead, {sum(1 for nm, s in xs if all(s['b'][i] > B0['b'][i] for i in range(3)))} in all blocks; best '{b[0]}' {b[1]['tot'] - B0['tot']:+.2f}")
    print("== walk-forward over all the rules (gain over the live setup in the blocks not picked on)")
    pa = max(S, key=lambda k: S[k]["b"][0]); pab = max(S, key=lambda k: S[k]["b"][0] + S[k]["b"][1])
    print(f"   best on A '{pa}' ({S[pa]['b'][0] - B0['b'][0]:+.2f}) -> on B {S[pa]['b'][1] - B0['b'][1]:+.2f}, on C {S[pa]['b'][2] - B0['b'][2]:+.2f}")
    print(f"   best on A+B '{pab}' ({S[pab]['b'][0] + S[pab]['b'][1] - B0['b'][0] - B0['b'][1]:+.2f}) -> on C {S[pab]['b'][2] - B0['b'][2]:+.2f}")
    top = sorted(S, key=lambda k: -(S[k]["b"][0] + S[k]["b"][1]))[:10]
    print(f"   the 10 best on A+B -> on C on average {sum(S[k]['b'][2] - B0['b'][2] for k in top) / 10:+.2f}; ahead on C: {sum(1 for k in top if S[k]['b'][2] > B0['b'][2])} of 10")
    N0 = score(None, NROWS, NPREP, NEX)
    print(f"== wallet 4's newest days ({len(NROWS)} buys, Nov 15 13:04 - Nov 16 14:25; the live setup {N0['tot']:+.2f} SOL): the best on A+B and the 10 best on all three blocks")
    print(f"   best on A+B '{pab}': {score(RULES[pab], NROWS, NPREP, NEX)['tot'] - N0['tot']:+.2f}")
    top3 = sorted(S, key=lambda k: -S[k]["tot"])[:10]
    for k in top3: print(f"   '{k}': {score(RULES[k], NROWS, NPREP, NEX)['tot'] - N0['tot']:+.2f}")
